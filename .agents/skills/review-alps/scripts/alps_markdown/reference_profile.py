"""Canonical, filesystem-only resolution for ALPS Skill references."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, MutableSequence
from dataclasses import dataclass, field
import ntpath
import os
from pathlib import Path
import re
from typing import TypeAlias

try:  # Package import is used by the checker; the fallback aids direct use.
    from .model import Diagnostic, Reference, Severity, deterministic_diagnostics
except ImportError:  # pragma: no cover - only for direct script-style imports.
    from model import Diagnostic, Reference, Severity, deterministic_diagnostics


PathLike: TypeAlias = str | os.PathLike[str]
_PACKAGE_ID = r"[a-z0-9]+(?:-[a-z0-9]+)*(?:/[a-z0-9]+(?:-[a-z0-9]+)*)*"
_SKILL_NAME = r"[a-z0-9]+(?:-[a-z0-9]+)*"
_PACKAGE_RE = re.compile(rf"\A{_PACKAGE_ID}\Z")
_VERSION_RE = re.compile(r"\A[0-9A-Za-z]+(?:[._+-][0-9A-Za-z]+)*\Z")
_REFERENCE_RE = re.compile(
    rf"\Askill:(?:(?P<package>{_PACKAGE_ID}))?#(?P<skill>{_SKILL_NAME})\Z"
)


@dataclass(frozen=True)
class PackageRootConfig:
    """Validated versioned package bindings and host diagnostics."""

    roots: Mapping[str, Path]
    diagnostics: tuple[Diagnostic, ...] = ()
    versions: Mapping[str, str] = field(default_factory=dict)

    def __getitem__(self, package_id: str) -> Path:
        return self.roots[package_id]

    def __iter__(self):
        return iter(self.roots)

    def __len__(self) -> int:
        return len(self.roots)


@dataclass(frozen=True)
class LogicalPackageIdentity:
    """A package ID paired with the exact version selected by a binding."""

    package_id: str
    exact_version: str

    def __str__(self) -> str:
        return f"{self.package_id}@{self.exact_version}"


@dataclass(frozen=True)
class LogicalSkillIdentity:
    """The complete logical identity required by ALPS."""

    package_id: str
    exact_version: str
    skill_name: str

    def __str__(self) -> str:
        return f"{self.package_id}@{self.exact_version}#{self.skill_name}"


@dataclass(frozen=True)
class ResolvedReference:
    """A canonical identity and its checked, package-contained target path."""

    reference: Reference
    package_id: str | None
    exact_version: str | None
    skill_name: str
    package_root: Path
    target: Path

    @property
    def identity(self) -> LogicalSkillIdentity | None:
        if self.package_id is None or self.exact_version is None:
            return None
        return LogicalSkillIdentity(self.package_id, self.exact_version, self.skill_name)

    @property
    def root(self) -> Path:
        return self.package_root

    @property
    def path(self) -> Path:
        return self.target


@dataclass(frozen=True)
class ReferenceResolution:
    """Result wrapper used so resolution errors remain deterministic and typed."""

    resolved: ResolvedReference | None
    diagnostics: tuple[Diagnostic, ...] = ()

    def __iter__(self):
        yield self.resolved
        yield self.diagnostics


ResolutionResult = ReferenceResolution

__all__ = [
    "PackageRootConfig",
    "LogicalPackageIdentity",
    "LogicalSkillIdentity",
    "ResolvedReference",
    "ReferenceResolution",
    "ResolutionResult",
    "package_roots",
    "containing_package_identity",
    "resolve_reference",
    "localized_target",
]


def _diagnostic(
    class_name: str,
    code: str,
    path: str | Path,
    message: str,
    reference: Reference | None = None,
) -> Diagnostic:
    return Diagnostic(
        class_name=class_name,
        code=code,
        severity=Severity.ERROR,
        path=str(path),
        line=reference.line if reference is not None else None,
        message=message,
        reference=reference,
    )


def _sorted(items: Iterable[Diagnostic]) -> tuple[Diagnostic, ...]:
    return deterministic_diagnostics(tuple(items))


def _absolute_path(value: PathLike, cwd: Path) -> Path:
    raw = os.fspath(value)
    if isinstance(raw, bytes):
        raise ValueError("package roots must be text paths")
    if not raw or "\x00" in raw:
        raise ValueError("package root is empty or contains NUL")
    return Path(os.path.abspath(os.path.join(os.fspath(cwd), raw)))


def _valid_package_id(value: object) -> bool:
    return isinstance(value, str) and _PACKAGE_RE.fullmatch(value) is not None


def _valid_version(value: object) -> bool:
    return isinstance(value, str) and _VERSION_RE.fullmatch(value) is not None


def _binding_key(value: object) -> tuple[str | None, str | None]:
    if value == "":
        return "", None
    if not isinstance(value, str):
        return None, None
    package, separator, version = value.rpartition("@")
    if not separator:
        return value, None
    return package, version


def package_roots(
    packages: Iterable[str] | Mapping[str, PathLike] | str | None = None,
    root: PathLike | None = None,
    package_id: str | None = None,
    package_version: str | None = None,
    *,
    cwd: PathLike | None = None,
) -> PackageRootConfig:
    """Parse exact ``PACKAGE@VERSION=PATH`` bindings and root compatibility.

    Relative paths are resolved against ``cwd`` (or the current directory),
    and no default package is invented.  Invalid entries are retained as
    diagnostics rather than being guessed or looked up elsewhere.
    """
    base = Path(os.path.abspath(os.fspath(cwd or os.getcwd())))
    diagnostics: list[Diagnostic] = []
    entries: list[tuple[object, object, str]] = []
    allow_default_root = False

    if isinstance(packages, PackageRootConfig):
        entries.extend(
            (
                f"{key}@{packages.versions[key]}" if key and key in packages.versions else key,
                value,
                f"{key}={value}",
            )
            for key, value in packages.roots.items()
        )
        diagnostics.extend(packages.diagnostics)
        allow_default_root = True
    elif isinstance(packages, Mapping):
        entries.extend((key, value, f"{key}={value}") for key, value in packages.items())
        allow_default_root = True
    elif packages is None:
        pass
    elif isinstance(packages, str):
        packages = (packages,)
        for spec in packages:
            package, separator, path = spec.partition("=")
            if not separator or not package or not path:
                diagnostics.append(
                    _diagnostic("host-input", "invalid-package-root-spec", "<package-config>",
                                "package binding must be exactly PACKAGE@VERSION=PATH")
                )
            else:
                entries.append((package, path, spec))
    else:
        for spec in packages:
            if not isinstance(spec, str):
                diagnostics.append(
                    _diagnostic("host-input", "invalid-package-root-spec", "<package-config>",
                                "package binding must be a PACKAGE@VERSION=PATH string")
                )
                continue
            package, separator, path = spec.partition("=")
            if not separator or not package or not path:
                diagnostics.append(
                    _diagnostic("host-input", "invalid-package-root-spec", "<package-config>",
                                "package binding must be exactly PACKAGE@VERSION=PATH")
                )
            else:
                entries.append((package, path, spec))

    if root is None and (package_id is not None or package_version is not None):
        diagnostics.append(
            _diagnostic("host-input", "incomplete-root-compatibility", "<package-config>",
                        "--root, --package-id, and --package-version must be supplied together")
        )
    elif root is not None:
        if package_id is None and package_version is None:
            allow_default_root = True
            entries.append(("", root, f"={root}"))
        elif package_id is None or package_version is None:
            diagnostics.append(
                _diagnostic("host-input", "incomplete-root-compatibility", "<package-config>",
                            "--root, --package-id, and --package-version must be supplied together")
            )
        else:
            entries.append((f"{package_id}@{package_version}", root,
                            f"{package_id}@{package_version}={root}"))

    roots: dict[str, Path] = {}
    versions: dict[str, str] = {}
    for binding, raw_path, display in entries:
        package, version = _binding_key(binding)
        if package == "" and allow_default_root:
            pass
        elif not _valid_package_id(package):
            diagnostics.append(
                _diagnostic("host-input", "invalid-package-id", "<package-config>",
                            f"invalid package ID in {display!r}")
            )
            continue
        if package != "" and not _valid_version(version):
            diagnostics.append(
                _diagnostic("host-input", "missing-or-invalid-package-version",
                            "<package-config>",
                            f"package binding {display!r} must include an exact version")
            )
            continue
        if package in roots:
            diagnostics.append(
                _diagnostic("host-input", "duplicate-package-id", "<package-config>",
                            f"package ID {package!r} is configured more than once")
            )
            continue
        try:
            absolute = _absolute_path(raw_path, base)  # type: ignore[arg-type]
        except (TypeError, ValueError, OSError) as error:
            diagnostics.append(
                _diagnostic("host-input", "invalid-package-root", str(raw_path), str(error))
            )
            continue
        roots[package] = absolute
        if package and version is not None:
            versions[package] = version
        try:
            is_directory = absolute.is_dir()
        except OSError:
            is_directory = False
        if not is_directory:
            diagnostics.append(
                _diagnostic("host-input", "package-root-not-directory", absolute,
                            f"configured package root is not a directory: {absolute}")
            )

    if not roots and not diagnostics:
        diagnostics.append(
            _diagnostic("host-input", "no-package-roots", "<package-config>",
                        "at least one package root must be configured")
        )
    return PackageRootConfig(
        dict(sorted(roots.items())),
        _sorted(diagnostics),
        dict(sorted(versions.items())),
    )


def _coerce_config(
    configured: PackageRootConfig | Mapping[str, PathLike] | Iterable[str] | str | None,
) -> PackageRootConfig:
    if isinstance(configured, PackageRootConfig):
        return configured
    return package_roots(configured)


def _contained(candidate: Path, root: Path) -> bool:
    try:
        lexical_candidate = os.path.abspath(os.fspath(candidate))
        lexical_root = os.path.abspath(os.fspath(root))
        if os.path.commonpath((lexical_candidate, lexical_root)) != lexical_root:
            return False
        real_candidate = os.path.realpath(lexical_candidate)
        real_root = os.path.realpath(lexical_root)
        return os.path.commonpath((real_candidate, real_root)) == real_root
    except (OSError, ValueError):
        return False


def _reference_parts(
    value: Reference | str,
) -> tuple[Reference | None, str | None, str | None, Diagnostic | None]:
    original = value if isinstance(value, Reference) else None
    token = value.token if original is not None else value
    if not isinstance(token, str):
        return None, None, None, _diagnostic(
            "semantic", "invalid-reference", "<reference>",
            "reference must be a canonical skill token", original
        )
    logical_token = _logical_reference_token(token)
    match = _REFERENCE_RE.fullmatch(logical_token or "")
    if match is None:
        return None, None, None, _diagnostic(
            "semantic", "invalid-reference", "<reference>",
            "reference must be exactly skill:#<skill-name> or "
            "skill:<package-id>#<skill-name>", original
        )
    package = match.group("package")
    skill = match.group("skill")
    reference = Reference(
        token=logical_token,
        skill_name=skill,
        package_id=package,
        line=original.line if original is not None else None,
        span=original.span if original is not None else None,
    )
    if original is not None and (
        original.skill_name != skill or original.package_id != package
    ):
        return None, None, None, _diagnostic(
            "semantic", "inconsistent-reference", "<reference>",
            "reference fields do not match the canonical token", original
        )
    return reference, package, skill, None


def _logical_reference_token(token: str) -> str | None:
    """Accept a logical token or exactly one surrounding backtick pair."""
    if "`" in token:
        if (
            len(token) < 3
            or token[0] != "`"
            or token[-1] != "`"
            or token.count("`") != 2
        ):
            return None
        token = token[1:-1]
    if "\\" in token or ntpath.isabs(token) or ntpath.splitdrive(token)[0]:
        return None
    return token


def _identity_for_path(
    path: PathLike,
    roots: Mapping[str, Path],
    diagnostics: list[Diagnostic],
) -> str | None:
    try:
        candidate = Path(os.path.abspath(os.fspath(path)))
    except (TypeError, ValueError, OSError) as error:
        diagnostics.append(_diagnostic("semantic", "invalid-containing-path", str(path), str(error)))
        return None
    matches = [
        (package, package_root)
        for package, package_root in roots.items()
        if _contained(candidate, package_root)
    ]
    if not matches:
        diagnostics.append(
            _diagnostic("semantic", "containing-package-not-found", candidate,
                        "current asset is not contained by a configured package root")
        )
        return None
    deepest = max(len(os.path.realpath(os.fspath(root))) for _, root in matches)
    matches = [item for item in matches if len(os.path.realpath(os.fspath(item[1]))) == deepest]
    if len(matches) > 1:
        names = ", ".join(sorted(package for package, _ in matches))
        diagnostics.append(
            _diagnostic("semantic", "ambiguous-containing-package", candidate,
                        f"current asset is contained by multiple package roots: {names}")
        )
        return None
    return matches[0][0]


def containing_package_identity(
    path: PathLike,
    configured: PackageRootConfig | Mapping[str, PathLike] | Iterable[str] | str | None,
    *,
    diagnostics: MutableSequence[Diagnostic] | None = None,
) -> LogicalPackageIdentity | None:
    """Return the exact versioned package scope containing ``path``.

    Both lexical and real-path containment are required.  A default root (the
    empty mapping key) is usable for local resolution but has no identity, so
    this function returns ``None`` for that root.  An optional mutable
    diagnostics sequence receives deterministic diagnostics.
    """
    config = _coerce_config(configured)
    collected = list(config.diagnostics)
    identity = _identity_for_path(path, config.roots, collected)
    ordered = _sorted(collected)
    if diagnostics is not None:
        diagnostics[:] = ordered
    if identity in (None, ""):
        return None
    version = config.versions.get(identity)
    return LogicalPackageIdentity(identity, version) if version is not None else None


def resolve_reference(
    reference: Reference | str,
    configured: PackageRootConfig | Mapping[str, PathLike] | Iterable[str] | str | None,
    containing_path: PathLike | None = None,
    *,
    current_package_id: str | None = None,
    current_path: PathLike | None = None,
) -> ReferenceResolution:
    """Resolve one canonical reference without reading its target content."""
    if containing_path is None:
        containing_path = current_path
    config = _coerce_config(configured)
    roots = config.roots
    diagnostics = list(config.diagnostics)
    parsed, qualified_package, skill, parse_error = _reference_parts(reference)
    if parse_error is not None:
        diagnostics.append(parse_error)
        return ReferenceResolution(None, _sorted(diagnostics))
    assert parsed is not None and skill is not None

    selected_root = qualified_package
    resolved_package_id: str | None = qualified_package
    if qualified_package is None:
        if current_package_id is not None:
            if current_package_id == "" and "" in roots:
                selected_root = ""
                resolved_package_id = None
            elif not _valid_package_id(current_package_id):
                diagnostics.append(
                    _diagnostic("host-input", "invalid-current-package-id", "<reference>",
                                f"invalid current package ID: {current_package_id!r}", parsed)
                )
            else:
                resolved_package_id = current_package_id
                selected_root = current_package_id if current_package_id in roots else ""
                if selected_root not in roots:
                    selected_root = current_package_id
            if containing_path is not None and (
                current_package_id == "" or _valid_package_id(current_package_id)
            ):
                discovered = _identity_for_path(containing_path, roots, diagnostics)
                if discovered is not None and discovered != "" and discovered != current_package_id:
                    diagnostics.append(
                        _diagnostic("host-input", "conflicting-current-package", str(containing_path),
                                    f"current package ID {current_package_id!r} does not contain the asset",
                                    parsed)
                    )
        elif containing_path is not None:
            selected_root = _identity_for_path(containing_path, roots, diagnostics)
            resolved_package_id = None if selected_root == "" else selected_root
        elif "" in roots:
            selected_root = ""
            resolved_package_id = None
        else:
            diagnostics.append(
                _diagnostic("host-input", "missing-containing-package", "<reference>",
                            "a local reference requires a containing path or current package ID", parsed)
            )

    if selected_root is None or selected_root not in roots:
        if selected_root is not None and selected_root not in roots:
            diagnostics.append(
                _diagnostic("semantic", "unknown-package", "<reference>",
                            f"package ID {selected_root!r} is not configured", parsed)
            )
        return ReferenceResolution(None, _sorted(diagnostics))

    package_root = roots[selected_root]
    exact_version = config.versions.get(selected_root) if selected_root else None
    if selected_root and exact_version is None:
        diagnostics.append(
            _diagnostic("host-input", "missing-package-version", "<reference>",
                        f"no exact version is bound for package ID {selected_root!r}", parsed)
        )
        return ReferenceResolution(None, _sorted(diagnostics))
    if not selected_root:
        diagnostics.append(
            _diagnostic("host-input", "missing-logical-package-scope", "<reference>",
                        "reference resolution requires a versioned package binding", parsed)
        )
        return ReferenceResolution(None, _sorted(diagnostics))
    target = package_root / "skills" / skill / "SKILL.md"
    if not _contained(target, package_root):
        diagnostics.append(
            _diagnostic("semantic", "target-escapes-package-root", target,
                        "canonical target is not contained by its package root", parsed)
        )
        return ReferenceResolution(None, _sorted(diagnostics))
    try:
        exists = os.path.lexists(os.fspath(target))
        regular = target.is_file()
    except OSError:
        exists = False
        regular = False
    if not exists:
        diagnostics.append(
            _diagnostic("semantic", "target-not-found", target,
                        f"canonical target does not exist: {target}", parsed)
        )
    elif not regular:
        diagnostics.append(
            _diagnostic("semantic", "target-not-regular-file", target,
                        f"canonical target is not a regular file: {target}", parsed)
        )
    if any(item.severity is Severity.ERROR for item in diagnostics):
        return ReferenceResolution(None, _sorted(diagnostics))
    return ReferenceResolution(
        ResolvedReference(
            parsed,
            resolved_package_id,
            exact_version,
            skill,
            package_root,
            target,
        ),
        _sorted(diagnostics),
    )


def localized_target(
    resolved: ResolvedReference | ReferenceResolution | None,
    locale: str | None = None,
    *,
    requested_locale: str | None = None,
    diagnostics: MutableSequence[Diagnostic] | None = None,
) -> Path | None:
    """Select the optional Japanese counterpart while preserving identity."""
    if requested_locale is not None:
        locale = requested_locale
    item = resolved.resolved if isinstance(resolved, ReferenceResolution) else resolved
    if item is None or not (
        isinstance(locale, str) and (locale == "ja" or locale.startswith("ja-"))
    ):
        return item.target if item is not None else None

    candidate = item.target.parent / "references" / "locales" / "ja" / "SKILL.md"
    local_diagnostics: list[Diagnostic] = []
    if not _contained(candidate, item.package_root):
        local_diagnostics.append(
            _diagnostic("semantic", "localized-target-escapes-package-root", candidate,
                        "localized target is not contained by its package root", item.reference)
        )
    else:
        try:
            exists = os.path.lexists(os.fspath(candidate))
            regular = candidate.is_file()
        except OSError:
            exists = False
            regular = False
        if exists and regular:
            if diagnostics is not None:
                diagnostics[:] = _sorted((*diagnostics, *local_diagnostics))
            return candidate
        if exists and not regular:
            local_diagnostics.append(
                _diagnostic("semantic", "localized-target-not-regular-file", candidate,
                            f"localized target is not a regular file: {candidate}", item.reference)
            )
    if diagnostics is not None:
        diagnostics[:] = _sorted((*diagnostics, *local_diagnostics))
    return item.target
