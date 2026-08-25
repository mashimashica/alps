"""Typed data model for the bounded ALPS checker profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Sequence


PROFILE_VERSION = "alps-repository-checker/v1"

MAX_INPUT_BYTES = 1 * 1024 * 1024
MAX_INPUT_LINES = 20_000
MAX_LINE_BYTES = 8 * 1024
MAX_FRONTMATTER_BYTES = 256 * 1024
MAX_RECORDS_PER_SECTION = 512
MAX_ACTIVE_CONTAINER_STATES = 1
SUPPORTED_KINDS = (
    "process",
    "process-model",
    "process-reference-model",
    "process-view",
)


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    line: int | None = None
    column: int | None = None


@dataclass(frozen=True)
class Reference:
    token: str
    skill_name: str
    package_id: str | None = None
    line: int | None = None
    span: Span | None = None


@dataclass(frozen=True)
class Diagnostic:
    class_name: str
    code: str
    severity: Severity
    path: str
    line: int | None
    message: str
    span: Span | None = None
    reference: Reference | None = None

    def render(self) -> str:
        location = self.path
        if self.line is not None:
            location += f":{self.line}"
        return f"{location}: {self.severity.value} {self.class_name}/{self.code}: {self.message}"


@dataclass(frozen=True)
class Frontmatter:
    name: str
    description: str
    kind: str
    metadata: Mapping[str, str] = field(default_factory=dict)
    name_line: int | None = None
    name_span: Span | None = None
    description_line: int | None = None
    description_span: Span | None = None
    kind_line: int | None = None
    kind_span: Span | None = None
    metadata_line: int | None = None
    metadata_span: Span | None = None


@dataclass(frozen=True)
class SectionIR:
    title: str
    level: int
    line: int
    span: Span | None = None
    prose: str | None = None
    key: str | None = None

    @property
    def role(self) -> str | None:
        """Return the stable semantic key for callers that use role terminology."""
        return self.key


@dataclass(frozen=True)
class OutcomeIR:
    text: str
    line: int
    identity: str | None = None
    references: tuple[Reference, ...] = ()
    span: Span | None = None


@dataclass(frozen=True)
class TaskIR:
    text: str
    line: int
    normative_class: str | None = None
    name: str | None = None
    references: tuple[Reference, ...] = ()
    span: Span | None = None


@dataclass(frozen=True)
class ActivityIR:
    name: str
    line: int
    purpose: str | None = None
    tasks: tuple[TaskIR, ...] = ()
    span: Span | None = None


@dataclass(frozen=True)
class ProcessEntryIR:
    name: str
    line: int
    purpose: str | None = None
    outcomes: tuple[OutcomeIR, ...] = ()
    reference: Reference | None = None
    span: Span | None = None


@dataclass(frozen=True)
class RelationshipIR:
    provider_process: str
    information: str
    recipient_process: str
    relationship: str
    line: int
    span: Span | None = None


@dataclass(frozen=True)
class SourceProcessIR:
    name: str
    line: int
    reference: Reference | None = None
    span: Span | None = None


@dataclass(frozen=True)
class IncludedActivityTaskIR:
    source_display: str
    source_reference: Reference | None
    kind: str
    label: str
    line: int
    span: Span | None = None


@dataclass(frozen=True)
class ApplicationIR:
    text: str
    line: int
    references: tuple[Reference, ...] = ()
    span: Span | None = None


@dataclass(frozen=True)
class DocumentIR:
    path: str
    locale: str | None
    frontmatter: Frontmatter | None
    sections: tuple[SectionIR, ...] = ()
    kind: str = "process"
    purpose: str | None = None
    outcomes: tuple[OutcomeIR, ...] = ()
    activities: tuple[ActivityIR, ...] = ()
    processes: tuple[ProcessEntryIR, ...] = ()
    relationships: tuple[RelationshipIR, ...] = ()
    source_processes: tuple[SourceProcessIR, ...] = ()
    included_activities_tasks: tuple[IncludedActivityTaskIR, ...] = ()
    application: tuple[ApplicationIR, ...] = ()
    references: tuple[Reference, ...] = ()
    title: str | None = None

    @property
    def h1_title(self) -> str | None:
        """Return the exact display title parsed from the document H1."""
        return self.title


@dataclass(frozen=True)
class InputResult:
    path: str
    text: str | None
    lines: tuple[str, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()


@dataclass(frozen=True)
class FrontmatterParseResult:
    frontmatter: Frontmatter | None
    body_start: int
    diagnostics: tuple[Diagnostic, ...] = ()


@dataclass(frozen=True)
class ParseResult:
    frontmatter: Frontmatter | None
    body_start: int
    ir: DocumentIR | None
    diagnostics: tuple[Diagnostic, ...] = ()


@dataclass(frozen=True)
class CheckResult:
    diagnostics: tuple[Diagnostic, ...] = ()
    ir: DocumentIR | None = None
    frontmatter: Frontmatter | None = None
    exit_status: int | None = None


def deterministic_diagnostics(
    diagnostics: Sequence[Diagnostic],
) -> tuple[Diagnostic, ...]:
    """Sort diagnostics deterministically, with missing lines last."""
    return tuple(
        sorted(
            diagnostics,
            key=lambda item: (
                item.path,
                item.line is None,
                item.line if item.line is not None else 0,
                item.span.start if item.span is not None else -1,
                item.class_name,
                item.code,
                item.message,
            ),
        )
    )
