"""Public API for the ALPS Markdown profile checker."""

from .model import (
    ActivityIR,
    ApplicationIR,
    CheckResult,
    Diagnostic,
    DocumentIR,
    Frontmatter,
    FrontmatterParseResult,
    IncludedActivityTaskIR,
    InputResult,
    OutcomeIR,
    ParseResult,
    ProcessEntryIR,
    Reference,
    RelationshipIR,
    SectionIR,
    Severity,
    SourceProcessIR,
    Span,
    TaskIR,
    PROFILE_VERSION,
)
from .checker import (
    check_asset,
    check_document,
    check_pair,
    english_counterpart,
    japanese_counterpart,
    locale_for,
    parse_asset,
)
from .validators import validate_ir
from .reference_profile import (
    LogicalPackageIdentity,
    LogicalSkillIdentity,
    PackageRootConfig,
    ReferenceResolution,
    ResolvedReference,
    package_roots,
    resolve_reference,
)


def main(argv=None):
    """Run the command-line entry point without eagerly importing it."""
    from .cli import main as _main

    return _main(argv)


__all__ = [
    "PROFILE_VERSION",
    "Severity",
    "Span",
    "Reference",
    "Diagnostic",
    "Frontmatter",
    "SectionIR",
    "OutcomeIR",
    "TaskIR",
    "ActivityIR",
    "ProcessEntryIR",
    "RelationshipIR",
    "SourceProcessIR",
    "IncludedActivityTaskIR",
    "ApplicationIR",
    "DocumentIR",
    "InputResult",
    "FrontmatterParseResult",
    "ParseResult",
    "CheckResult",
    "PackageRootConfig",
    "LogicalPackageIdentity",
    "LogicalSkillIdentity",
    "ResolvedReference",
    "ReferenceResolution",
    "package_roots",
    "resolve_reference",
    "locale_for",
    "japanese_counterpart",
    "english_counterpart",
    "parse_asset",
    "validate_ir",
    "check_document",
    "check_asset",
    "check_pair",
    "main",
]
