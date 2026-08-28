"""Orchestration and compatibility helpers for the ALPS Markdown profile checker."""

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
    Reference,
    Severity,
    deterministic_diagnostics,
)
from .reference_profile import (
    LogicalPackageIdentity,
    LogicalSkillIdentity,
    PackageRootConfig,
    ReferenceResolution,
    localized_target,
    package_roots,
    resolve_reference,
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
    return (
        "ja"
        if len(parts) >= 4
        and parts[-4:-1] == ("references", "locales", "ja")
        else "en"
    )


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


def _contained_source(path: os.PathLike[str] | str, root: Path) -> bool:
    """Require both lexical and real-path containment for a declared source."""
    try:
        lexical_path = os.path.abspath(os.fspath(path))
        lexical_root = os.path.abspath(os.fspath(root))
        if os.path.commonpath((lexical_path, lexical_root)) != lexical_root:
            return False
        real_path = os.path.realpath(lexical_path)
        real_root = os.path.realpath(lexical_root)
        return os.path.commonpath((real_path, real_root)) == real_root
    except (OSError, TypeError, ValueError):
        return False


def _operative_references(document: DocumentIR) -> tuple[Reference, ...]:
    """Collect every operative reference from all bounded IR projections."""
    result: list[Reference] = []
    seen: set[tuple[str, int | None, int | None, int | None]] = set()

    def add(reference: Reference | None) -> None:
        if not isinstance(reference, Reference):
            return
        key = (
            reference.token,
            reference.line,
            reference.span.start if reference.span is not None else None,
            reference.span.end if reference.span is not None else None,
        )
        if key not in seen:
            seen.add(key)
            result.append(reference)

    for reference in document.references:
        add(reference)
    for outcome in document.outcomes:
        for reference in outcome.references:
            add(reference)
    for activity in document.activities:
        for task in activity.tasks:
            for reference in task.references:
                add(reference)
    for process in document.processes:
        add(process.reference)
        for outcome in process.outcomes:
            for reference in outcome.references:
                add(reference)
    for source in document.source_processes:
        add(source.reference)
    for inclusion in document.included_activities_tasks:
        add(inclusion.source_reference)
    for application in document.application:
        for reference in application.references:
            add(reference)
    return tuple(result)


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
    require_locale_counterpart: bool,
    verify_selected_root_counterpart: bool = True,
) -> CheckResult:
    label = _label(path)
    try:
        config = _root_config(roots)
    except Exception as error:
        diagnostic = _internal("<package-config>", "root-configuration", str(error))
        return CheckResult((diagnostic,), None, None, 2)

    diagnostics = list(config.diagnostics)
    if package_id is not None and package_id != "":
        if _PACKAGE_ID.fullmatch(package_id) is None:
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
        elif package_id not in config.roots:
            diagnostics.append(
                Diagnostic(
                    "host-input",
                    "missing-current-package-binding",
                    Severity.ERROR,
                    "<package-config>",
                    None,
                    f"no Package Binding exists for current package ID {package_id!r}",
                )
            )
        elif not _contained_source(path, config.roots[package_id]):
            diagnostics.append(
                Diagnostic(
                    "host-input",
                    "source-outside-package-root",
                    Severity.ERROR,
                    label,
                    None,
                    "the source asset is not contained by the declared package root",
                )
            )

    if _has_errors(diagnostics):
        ordered = _ordered(diagnostics)
        return CheckResult(ordered, None, None, _exit_status(ordered))

    key = _parse_key(path, None)
    parsed = parse_cache.get(key)
    if parsed is None:
        parsed = parse_asset(path)
        parse_cache[key] = parsed

    diagnostics.extend(parsed.diagnostics)

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
                    config,
                    current_package_id=package_id,
                    require_locale_counterpart=False,
                    load_ir=load_ir,
                )
            )
        except Exception as error:
            diagnostics.append(_internal(label, "validation-failed", str(error)))

    if (
        require_locale_counterpart
        and verify_selected_root_counterpart
        and locale_for(path) == "en"
        and parsed.ir is not None
        and not _has_errors(diagnostics)
    ):
        japanese_path = japanese_counterpart(path)
        try:
            counterpart_exists = os.path.lexists(os.fspath(japanese_path))
            counterpart_is_file = japanese_path.is_file()
        except OSError:
            counterpart_exists = False
            counterpart_is_file = False
        if not counterpart_exists:
            diagnostics.append(
                Diagnostic(
                    "locale-mismatch",
                    "missing-japanese-counterpart",
                    Severity.ERROR,
                    label,
                    None,
                    f"required Japanese counterpart does not exist: {japanese_path}",
                )
            )
        elif not counterpart_is_file:
            diagnostics.append(
                Diagnostic(
                    "host-input",
                    "japanese-counterpart-not-regular-file",
                    Severity.ERROR,
                    os.fspath(japanese_path),
                    None,
                    "required Japanese counterpart is not a regular file",
                )
            )
        else:
            japanese_result = _check_document(
                japanese_path,
                config,
                package_id,
                parse_cache,
                False,
                False,
            )
            diagnostics.extend(japanese_result.diagnostics)
            if (
                japanese_result.ir is not None
                and not _has_errors(japanese_result.diagnostics)
            ):
                bound_identity = None
                if package_id and package_id in config.versions:
                    bound_identity = LogicalPackageIdentity(
                        package_id,
                        config.versions[package_id],
                    )
                diagnostics.extend(
                    compare_locale_ir(
                        parsed.ir,
                        japanese_result.ir,
                        package_identity=(bound_identity, config.versions),
                    )
                )

    if (
        require_locale_counterpart
        and parsed.ir is not None
        and not _has_errors(diagnostics)
    ):
        try:
            diagnostics.extend(
                _locale_dependency_closure(
                    parsed.ir,
                    config,
                    package_id,
                    parse_cache,
                )
            )
        except Exception as error:
            diagnostics.append(_internal(label, "locale-dependency-validation-failed", str(error)))

    ordered = _ordered(diagnostics)
    status = _exit_status(ordered)
    return CheckResult(ordered, parsed.ir, parsed.frontmatter, status)


def _locale_dependency_closure(
    document: DocumentIR,
    config: PackageRootConfig,
    current_package_id: str | None,
    parse_cache: dict[tuple[str, str], ParseResult],
) -> tuple[Diagnostic, ...]:
    """Validate the transitive English/Japanese dependency closure once.

    The walk is deliberately iterative.  A valid dependency graph is bounded
    by the host's finite package contents, but its depth is not a profile error
    and therefore must not be bounded accidentally by Python's call stack.
    """
    diagnostics: list[Diagnostic] = []
    visited: set[LogicalSkillIdentity] = set()
    pending: list[ReferenceResolution] = []

    def enqueue_document(source: DocumentIR, containing_package_id: str | None) -> None:
        for reference in _operative_references(source):
            resolution = resolve_reference(
                reference,
                config,
                containing_path=source.path,
                current_package_id=containing_package_id,
            )
            if resolution.resolved is None:
                diagnostics.extend(resolution.diagnostics)
                continue
            pending.append(resolution)

    enqueue_document(document, current_package_id)
    while pending:
        resolution = pending.pop()
        resolved = resolution.resolved
        if resolved is None or resolved.identity is None:
            continue
        identity = resolved.identity
        if identity in visited:
            continue
        visited.add(identity)

        localized_diagnostics: list[Diagnostic] = []
        japanese_path = localized_target(
            resolution,
            "ja",
            require_counterpart=True,
            diagnostics=localized_diagnostics,
        )
        diagnostics.extend(localized_diagnostics)
        if japanese_path is None:
            continue

        english_result = _check_document(
            resolved.target,
            config,
            identity.package_id,
            parse_cache,
            False,
        )
        japanese_result = _check_document(
            japanese_path,
            config,
            identity.package_id,
            parse_cache,
            False,
        )
        diagnostics.extend(english_result.diagnostics)
        diagnostics.extend(japanese_result.diagnostics)

        if (
            english_result.ir is not None
            and japanese_result.ir is not None
            and not _has_errors(english_result.diagnostics)
            and not _has_errors(japanese_result.diagnostics)
        ):
            diagnostics.extend(
                compare_locale_ir(
                    english_result.ir,
                    japanese_result.ir,
                    package_identity=(
                        LogicalPackageIdentity(
                            identity.package_id,
                            identity.exact_version,
                        ),
                        config.versions,
                    ),
                )
            )
            enqueue_document(english_result.ir, identity.package_id)
            enqueue_document(japanese_result.ir, identity.package_id)

    return deterministic_diagnostics(diagnostics)


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
    require_locale_counterpart: bool = False,
) -> CheckResult:
    """Check one parsed document and its IR-resolved dependencies."""
    return _check_document(
        path,
        roots,
        package_id,
        parse_cache if parse_cache is not None else {},
        require_locale_counterpart,
    )


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
    package_identity: str | LogicalPackageIdentity | None = None,
    package_versions: dict[str, str] | None = None,
    *,
    roots: object = None,
    package_id: str | None = None,
    require_locale_counterpart: bool = False,
) -> tuple[list[str], list[str]]:
    """Compare two locale assets after resolving references through a binding.

    ``package_identity`` and ``package_versions`` remain accepted for source
    compatibility, but they do not prove that a referenced target exists.  A
    caller comparing documents that contain Skill references must therefore
    supply ``roots``.  The binding, rather than the lexical context alone,
    supplies every exact version used for locale identity comparison.
    """
    del allowed_terms
    parse_cache: dict[tuple[str, str], ParseResult] = {}
    config: PackageRootConfig | None = None
    current_package_id = package_id
    declared_package_id: str | None = None
    declared_version: str | None = None
    if isinstance(package_identity, LogicalPackageIdentity):
        declared_package_id = package_identity.package_id
        current_package_id = current_package_id or package_identity.package_id
        declared_version = package_identity.exact_version
    elif isinstance(package_identity, str):
        if "@" in package_identity:
            identity_package, declared_version = package_identity.rsplit("@", 1)
            declared_package_id = identity_package
            current_package_id = current_package_id or identity_package
        elif package_identity:
            declared_package_id = package_identity
            current_package_id = current_package_id or package_identity

    diagnostics: list[Diagnostic] = []
    if (
        package_id is not None
        and declared_package_id is not None
        and package_id != declared_package_id
    ):
        diagnostics.append(
            Diagnostic(
                "host-input",
                "conflicting-package-identity",
                Severity.ERROR,
                "<package-config>",
                None,
                "package_identity and package_id declare different containing package scopes",
            )
        )
    if roots is None:
        left = parse_asset(english, "en")
        right = parse_asset(japanese, "ja")
        diagnostics.extend(left.diagnostics)
        diagnostics.extend(right.diagnostics)
    else:
        try:
            config = _root_config(roots)
        except Exception as error:
            diagnostics.append(_internal("<package-config>", "root-configuration", str(error)))
            left = parse_asset(english, "en")
            right = parse_asset(japanese, "ja")
        else:
            # A pair API carries explicit locale roles even when fixture paths
            # do not use the canonical ``references/locales/ja`` layout.
            parse_cache[_parse_key(english, None)] = parse_asset(english, "en")
            parse_cache[_parse_key(japanese, None)] = parse_asset(japanese, "ja")
            left_checked = _check_document(
                english,
                config,
                current_package_id,
                parse_cache,
                require_locale_counterpart,
                False,
            )
            right_checked = _check_document(
                japanese,
                config,
                current_package_id,
                parse_cache,
                require_locale_counterpart,
                False,
            )
            diagnostics.extend(left_checked.diagnostics)
            diagnostics.extend(right_checked.diagnostics)
            left = ParseResult(left_checked.frontmatter, 0, left_checked.ir, ())
            right = ParseResult(right_checked.frontmatter, 0, right_checked.ir, ())

            if current_package_id and current_package_id in config.versions:
                bound_version = config.versions[current_package_id]
                if declared_version is not None and declared_version != bound_version:
                    diagnostics.append(
                        Diagnostic(
                            "host-input",
                            "conflicting-package-version",
                            Severity.ERROR,
                            "<package-config>",
                            None,
                            "locale package identity version conflicts with the Package Binding",
                        )
                    )
            if package_versions is not None:
                for bound_package, asserted_version in package_versions.items():
                    actual_version = config.versions.get(bound_package)
                    if actual_version is not None and asserted_version != actual_version:
                        diagnostics.append(
                            Diagnostic(
                                "host-input",
                                "conflicting-package-version",
                                Severity.ERROR,
                                "<package-config>",
                                None,
                                f"locale version for {bound_package!r} conflicts with the Package Binding",
                            )
                        )

    if (
        left.ir is not None
        and right.ir is not None
        and not _has_errors(diagnostics)
    ):
        try:
            if config is None:
                # Lexical package data does not establish a resolved identity.
                locale_context = None
            else:
                bound_identity = None
                if current_package_id and current_package_id in config.versions:
                    bound_identity = LogicalPackageIdentity(
                        current_package_id,
                        config.versions[current_package_id],
                    )
                locale_context = (bound_identity, config.versions)
            diagnostics.extend(
                compare_locale_ir(
                    left.ir,
                    right.ir,
                    package_identity=locale_context,
                )
            )
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
