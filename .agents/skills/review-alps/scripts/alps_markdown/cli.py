"""Command-line entry point for the ALPS Markdown profile checker."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

try:
    from .checker import (
        english_counterpart,
        japanese_counterpart,
        locale_for,
        check_document,
    )
    from .locale_compare import compare_locale_ir
    from .model import (
        CheckResult,
        Diagnostic,
        PROFILE_VERSION,
        Severity,
        deterministic_diagnostics,
    )
    from .reference_profile import (
        PackageRootConfig,
        containing_package_identity,
        package_roots,
    )
except ImportError:  # pragma: no cover - supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from alps_markdown.checker import (  # type: ignore
        english_counterpart,
        japanese_counterpart,
        locale_for,
        check_document,
    )
    from alps_markdown.locale_compare import compare_locale_ir  # type: ignore
    from alps_markdown.model import (  # type: ignore
        CheckResult,
        Diagnostic,
        PROFILE_VERSION,
        Severity,
        deterministic_diagnostics,
    )
    from alps_markdown.reference_profile import (  # type: ignore
        PackageRootConfig,
        containing_package_identity,
        package_roots,
    )


_PACKAGE_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*(?:/[a-z0-9]+(?:-[a-z0-9]+)*)*\Z")


def _host(code: str, message: str) -> Diagnostic:
    return Diagnostic("host-input", code, Severity.ERROR, "<package-config>", None, message)


def _merge(
    roots: dict[str, Path], diagnostics: list[Diagnostic], addition: PackageRootConfig
) -> None:
    diagnostics.extend(addition.diagnostics)
    for package, root in addition.roots.items():
        if package in roots:
            diagnostics.append(
                _host("duplicate-package-id", f"package ID {package!r} is configured more than once")
            )
        else:
            roots[package] = root


def _configure(args: argparse.Namespace) -> PackageRootConfig:
    cwd = Path.cwd()
    roots: dict[str, Path] = {}
    diagnostics: list[Diagnostic] = []
    if args.package_roots:
        _merge(roots, diagnostics, package_roots(args.package_roots, cwd=cwd))

    if args.root is not None:
        key = args.package_id or ""
        _merge(roots, diagnostics, package_roots({key: args.root}, cwd=cwd))
    elif args.package_id is None:
        _merge(roots, diagnostics, package_roots({"": cwd}, cwd=cwd))
    elif _PACKAGE_ID.fullmatch(args.package_id) is None:
        diagnostics.append(_host("invalid-package-id", f"invalid package ID: {args.package_id!r}"))
    elif args.package_id not in roots:
        diagnostics.append(
            _host("missing-package-root", f"no configured root exists for package ID {args.package_id!r}")
        )
    return PackageRootConfig(dict(sorted(roots.items())), deterministic_diagnostics(diagnostics))


def _path_key(path: Path) -> str:
    return os.path.normcase(os.path.abspath(os.fspath(path)))


def _is_file(path: Path) -> bool:
    try:
        return path.is_file()
    except OSError:
        return False


def _dedupe(paths: list[Path]) -> list[Path]:
    result: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = _path_key(path)
        if key not in seen:
            seen.add(key)
            result.append(path)
    return result


def _default_paths(root: Path) -> list[Path]:
    return sorted(root.glob("skills/*/SKILL.md"), key=lambda item: os.fspath(item))


def _resolve_asset_paths(paths: list[Path], discovery_root: Path) -> list[Path]:
    """Resolve positional relative paths against the configured discovery root."""
    return [path if path.is_absolute() else discovery_root / path for path in paths]


def _valid(result: CheckResult) -> bool:
    return result.ir is not None and not any(
        item.severity is Severity.ERROR for item in result.diagnostics
    )


def _pair_package_identity(
    english: Path,
    japanese: Path,
    config: PackageRootConfig,
    configured: str | None,
) -> str | None:
    """Provide locale comparison with the package context already configured."""
    if configured:
        return configured
    left = containing_package_identity(english, config.roots)
    right = containing_package_identity(japanese, config.roots)
    return left if left is not None and left == right else None


def _status(diagnostics: tuple[Diagnostic, ...]) -> int:
    if any(
        item.severity is Severity.ERROR
        and item.class_name in {"host-input", "internal"}
        for item in diagnostics
    ):
        return 2
    return 1 if any(item.severity is Severity.ERROR for item in diagnostics) else 0


def _run(argv: list[str] | None) -> int:
    parser = argparse.ArgumentParser(prog="alps-markdown")
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--package-id")
    parser.add_argument("--package-root", dest="package_roots", action="append", metavar="PACKAGE=PATH")
    parser.add_argument("--require-japanese", action="store_true")
    parser.add_argument("--no-locale-pairs", action="store_true")
    parser.add_argument("--version", action="version", version=PROFILE_VERSION)
    args = parser.parse_args(argv)

    config = _configure(args)
    if config.diagnostics:
        diagnostics = deterministic_diagnostics(config.diagnostics)
        for item in diagnostics:
            print(item.render(), file=sys.stderr)
        return _status(diagnostics)

    if args.root is not None:
        discovery_root = config.roots[args.package_id or ""]
    elif args.package_id and args.package_id in config.roots:
        discovery_root = config.roots[args.package_id]
    else:
        discovery_root = Path.cwd()
    initial = (
        _resolve_asset_paths(list(args.paths), discovery_root)
        if args.paths
        else _default_paths(discovery_root)
    )
    if not initial:
        diagnostics = (
            _host("no-assets", "no assets matched root/skills/*/SKILL.md"),
        )
        print(diagnostics[0].render(), file=sys.stderr)
        return 2

    assets = _dedupe(initial)
    if not args.no_locale_pairs:
        for path in tuple(assets):
            if locale_for(path) == "en":
                counterpart = japanese_counterpart(path)
                if _is_file(counterpart):
                    assets = _dedupe(assets + [counterpart])
            else:
                counterpart = english_counterpart(path)
                if _is_file(counterpart):
                    assets = _dedupe(assets + [counterpart])

    diagnostics: list[Diagnostic] = []
    if args.require_japanese:
        for path in assets:
            if locale_for(path) == "en" and not _is_file(japanese_counterpart(path)):
                diagnostics.append(
                    Diagnostic(
                        "locale-mismatch",
                        "missing-japanese-counterpart",
                        Severity.ERROR,
                        os.fspath(path),
                        None,
                        "required Japanese counterpart is missing",
                    )
                )

    parse_cache = {}
    results: dict[str, CheckResult] = {}
    for path in assets:
        result = check_document(
            path,
            config.roots,
            args.package_id,
            parse_cache=parse_cache,
        )
        results[_path_key(path)] = result
        diagnostics.extend(result.diagnostics)

    if not args.no_locale_pairs:
        compared: set[tuple[str, str]] = set()
        for path in assets:
            if locale_for(path) != "en":
                continue
            counterpart = japanese_counterpart(path)
            if not _is_file(counterpart):
                continue
            pair = (_path_key(path), _path_key(counterpart))
            if pair in compared:
                continue
            compared.add(pair)
            left = results.get(pair[0])
            right = results.get(pair[1])
            if left is not None and right is not None and _valid(left) and _valid(right):
                diagnostics.extend(
                    compare_locale_ir(
                        left.ir,
                        right.ir,
                        package_identity=_pair_package_identity(path, counterpart, config, args.package_id),
                    )
                )  # type: ignore[arg-type]

    ordered = deterministic_diagnostics(diagnostics)
    for item in ordered:
        if item.severity is Severity.WARNING or item.severity is Severity.ERROR:
            print(item.render(), file=sys.stderr)
    status = _status(ordered)
    if status == 0:
        print(f"PROFILE_VERSION={PROFILE_VERSION}")
        print("Valid under ALPS Markdown Profile v1 only; this is not an ALPS Conformance claim.")
    return status


def main(argv: list[str] | None = None) -> int:
    """Run the CLI with a safe internal-error boundary."""
    try:
        return _run(argv)
    except SystemExit:
        raise
    except Exception as error:
        diagnostic = Diagnostic(
            "internal", "cli-failed", Severity.ERROR, "<cli>", None, str(error)
        )
        print(diagnostic.render(), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
