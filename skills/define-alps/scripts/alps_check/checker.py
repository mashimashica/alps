"""Orchestration and compatibility helpers for the ALPS profile checker."""

from __future__ import annotations

import os
import re
from pathlib import Path

from .frontmatter_profile import parse_frontmatter
from .input_profile import read_input
from .locale_compare import compare_locale_ir
from .markdown_profile import parse_markdown
from .model import (
    CheckResult,
    Diagnostic,
    DocumentIR,
    ParseResult,
    PROFILE_VERSION,
    Severity,
    deterministic_diagnostics,
)
from .reference_profile import (
    PackageRootConfig,
    package_roots,
)
from .validators import validate_ir


_PACKAGE_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*(?:/[a-z0-9]+(?:-[a-z0-9]+)*)*\Z")


def _path(value: os.PathLike[str] | str) -> Path:
    return Path(os.fspath(value))


def _label(value: os.PathLike[str] | str) -> str:
    raw = os.fspath(value)
    return raw if isinstance(raw, str) else os.fsdecode(raw)


def locale_for(path: os.PathLike[str] | str) -> str:
    """Return the profile locale encoded by the canonical Japanese path."""
    parts = _path(path).parts
    for index in range(len(parts) - 2):
        if parts[index:index + 3] == ("references", "locales", "ja"):
            return "ja"
    return "en"


def japanese_counterpart(path: os.PathLike[str] | str) -> Path:
    """Return the canonical Japanese counterpart path for an asset."""
    value = _path(path)
    if locale_for(value) == "ja" and value.parent.name == "ja":
        return value
    return value.parent / "references" / "locales" / "ja" / value.name


def english_counterpart(path: os.PathLike[str] | str) -> Path:
    """Return the canonical English counterpart path for a Japanese asset."""
    value = _path(path)
    parts = value.parts
    if (
        locale_for(value) == "ja"
        and len(parts) >= 4
        and parts[-4:-1] == ("references", "locales", "ja")
    ):
        return value.parent.parent.parent.parent / value.name
    return value


def _internal(path: str, code: str, message: str) -> Diagnostic:
    return Diagnostic("internal", code, Severity.ERROR, path, None, message)


def _has_errors(diagnostics: tuple[Diagnostic, ...] | list[Diagnostic]) -> bool:
    return any(item.severity is Severity.ERROR for item in diagnostics)


def _ordered(diagnostics: list[Diagnostic]) -> tuple[Diagnostic, ...]:
    return deterministic_diagnostics(diagnostics)


def parse_asset(path: os.PathLike[str] | str, locale: str | None = None) -> ParseResult:
    """Read, parse, and extract one asset exactly once."""
    label = _label(path)
    selected_locale = locale if locale is not None else locale_for(path)
    try:
        input_result = read_input(path, label)
        frontmatter_result = parse_frontmatter(input_result)
        diagnostics = list(frontmatter_result.diagnostics)
        ir: DocumentIR | None = None
        if input_result.text is not None and frontmatter_result.frontmatter is not None:
            ir, markdown_diagnostics = parse_markdown(
                label,
                selected_locale,
                frontmatter_result.frontmatter,
                input_result.lines,
                frontmatter_result.body_start,
            )
            diagnostics.extend(markdown_diagnostics)
        return ParseResult(
            frontmatter_result.frontmatter,
            frontmatter_result.body_start,
            ir,
            _ordered(diagnostics),
        )
    except (OSError, TypeError, ValueError) as error:
        return ParseResult(None, 0, None, (_internal(label, "parse-input", str(error)),))
    except Exception as error:  # Keep parser failures inside the checker boundary.
        return ParseResult(None, 0, None, (_internal(label, "parse-failed", str(error)),))


def _root_config(roots: object) -> PackageRootConfig:
    if isinstance(roots, PackageRootConfig):
        return roots
    return package_roots(roots)  # type: ignore[arg-type]


def _parse_key(path: os.PathLike[str] | str, locale: str | None) -> tuple[str, str]:
    absolute = os.path.normcase(os.path.abspath(os.fspath(path)))
    return absolute, locale if locale is not None else locale_for(path)


def _check_document(
    path: os.PathLike[str] | str,
    roots: object,
    package_id: str | None,
    parse_cache: dict[tuple[str, str], ParseResult],
) -> CheckResult:
    label = _label(path)
    try:
        config = _root_config(roots)
    except Exception as error:
        diagnostic = _internal("<package-config>", "root-configuration", str(error))
        return CheckResult((diagnostic,), None, None, 2)

    key = _parse_key(path, None)
    parsed = parse_cache.get(key)
    if parsed is None:
        parsed = parse_asset(path)
        parse_cache[key] = parsed

    diagnostics = list(config.diagnostics) + list(parsed.diagnostics)
    if package_id is not None and package_id != "" and _PACKAGE_ID.fullmatch(package_id) is None:
        diagnostics.append(
            Diagnostic(
                "host-input",
                "invalid-current-package-id",
                Severity.ERROR,
                "<package-config>",
                None,
                f"invalid current package ID: {package_id!r}",
            )
        )

    if parsed.ir is not None and not _has_errors(parsed.diagnostics) and not _has_errors(config.diagnostics):
        def load_ir(target: Path, target_locale: str | None) -> ParseResult:
            target_key = _parse_key(target, target_locale)
            loaded = parse_cache.get(target_key)
            if loaded is None:
                loaded = parse_asset(target, target_locale)
                parse_cache[target_key] = loaded
            return loaded

        try:
            diagnostics.extend(
                validate_ir(
                    parsed.ir,
                    config.roots,
                    current_package_id=package_id,
                    load_ir=load_ir,
                )
            )
        except Exception as error:
            diagnostics.append(_internal(label, "validation-failed", str(error)))

    ordered = _ordered(diagnostics)
    status = _exit_status(ordered)
    return CheckResult(ordered, parsed.ir, parsed.frontmatter, status)


def _exit_status(diagnostics: tuple[Diagnostic, ...]) -> int:
    if any(
        item.severity is Severity.ERROR
        and item.class_name in {"host-input", "internal"}
        for item in diagnostics
    ):
        return 2
    return 1 if any(item.severity is Severity.ERROR for item in diagnostics) else 0


def check_document(
    path: os.PathLike[str] | str,
    roots: object,
    package_id: str | None = None,
    *,
    parse_cache: dict[tuple[str, str], ParseResult] | None = None,
) -> CheckResult:
    """Check one parsed document and its IR-resolved dependencies."""
    return _check_document(path, roots, package_id, parse_cache if parse_cache is not None else {})


def _strings(diagnostics: tuple[Diagnostic, ...]) -> tuple[list[str], list[str]]:
    errors = [item.render() for item in diagnostics if item.severity is Severity.ERROR]
    warnings = [item.render() for item in diagnostics if item.severity is Severity.WARNING]
    return errors, warnings


def check_asset(
    path: os.PathLike[str] | str,
    roots: object,
    package_id: str | None = None,
) -> tuple[list[str], list[str]]:
    """Compatibility wrapper returning rendered error and warning strings."""
    return _strings(check_document(path, roots, package_id).diagnostics)


def check_pair(
    english: os.PathLike[str] | str,
    japanese: os.PathLike[str] | str,
    allowed_terms: object = None,
    package_identity: str | None = None,
) -> tuple[list[str], list[str]]:
    """Compatibility wrapper for comparison of two independently valid IRs."""
    del allowed_terms
    left = parse_asset(english, "en")
    right = parse_asset(japanese, "ja")
    diagnostics = list(left.diagnostics) + list(right.diagnostics)
    if (
        left.ir is not None
        and right.ir is not None
        and not _has_errors(left.diagnostics)
        and not _has_errors(right.diagnostics)
    ):
        try:
            diagnostics.extend(compare_locale_ir(left.ir, right.ir, package_identity=package_identity))
        except Exception as error:
            diagnostics.append(_internal(_label(japanese), "locale-comparison-failed", str(error)))
    return _strings(_ordered(diagnostics))


__all__ = [
    "PROFILE_VERSION",
    "locale_for",
    "japanese_counterpart",
    "english_counterpart",
    "parse_asset",
    "check_document",
    "check_asset",
    "check_pair",
]
