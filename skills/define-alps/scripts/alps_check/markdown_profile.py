"""Bounded Markdown profile structure extraction."""

from __future__ import annotations

from dataclasses import dataclass, replace
import re
from typing import Sequence

from .model import (
    MAX_ACTIVE_CONTAINER_STATES,
    MAX_INPUT_LINES,
    MAX_RECORDS_PER_SECTION,
    ActivityIR,
    ApplicationIR,
    Diagnostic,
    DocumentIR,
    Frontmatter,
    IncludedActivityTaskIR,
    OutcomeIR,
    ProcessEntryIR,
    Reference,
    RelationshipIR,
    SectionIR,
    Severity,
    SourceProcessIR,
    Span,
    TaskIR,
    deterministic_diagnostics,
)


_SECTION_NAMES = {
    "en": {
        "purpose": "Purpose",
        "outcomes": "Outcomes",
        "activities": "Activities & Tasks",
        "inputs": "Inputs",
        "outputs": "Outputs",
        "entry": "Entry Criteria",
        "exit": "Exit Criteria",
        "controls": "Controls",
        "constraints": "Constraints",
        "enablers": "Enablers",
        "conformance": "Conformance",
        "interfaces": "Interfaces & Traceability",
        "shared": "Shared Normative References",
        "bundled": "Bundled Resources",
        "approach": "Common Approach",
        "processes": "Processes",
        "relationships": "Relationships",
        "source": "Source Processes",
        "included": "Included Activities and Tasks",
        "application": "Application",
        "verification": "Verification",
    },
    "ja": {
        "purpose": "目的",
        "outcomes": "成果",
        "activities": "活動とタスク",
        "inputs": "入力",
        "outputs": "出力",
        "entry": "開始基準",
        "exit": "完了基準",
        "controls": "統制事項",
        "constraints": "制約",
        "enablers": "実行支援要素",
        "conformance": "適合",
        "interfaces": "インターフェースと追跡可能性",
        "shared": "共通規範参照",
        "bundled": "同梱資源",
        "approach": "一般的な進め方",
        "processes": "プロセス",
        "relationships": "関係",
        "source": "出典プロセス",
        "included": "含まれる活動およびタスク",
        "application": "適用",
        "verification": "検証",
    },
}

_SECTION_ORDER = {
    "process": (
        "purpose", "outcomes", "activities", "inputs", "outputs", "entry",
        "exit", "controls", "constraints", "enablers", "conformance",
        "interfaces", "shared", "bundled", "approach",
    ),
    "process-model": (
        "purpose", "processes", "relationships", "application", "verification",
        "conformance", "bundled",
    ),
    "process-reference-model": (
        "purpose", "processes", "relationships", "application", "verification",
        "conformance", "bundled",
    ),
    "process-view": (
        "purpose", "outcomes", "source", "included", "application",
        "conformance", "bundled",
    ),
}

_REQUIRED_SECTIONS = {
    "process": frozenset(("purpose", "outcomes", "activities")),
    "process-model": frozenset(("purpose", "processes", "relationships")),
    "process-reference-model": frozenset(("purpose", "processes", "relationships")),
    "process-view": frozenset(("purpose", "outcomes", "source", "included", "application")),
}

_TABLE_HEADERS = {
    "processes": {
        "en": ("Process", "Skill"),
        "ja": ("プロセス", "スキル"),
    },
    "relationships": {
        "en": ("Provider Process", "Information", "Recipient Process", "Relationship"),
        "ja": ("提供側プロセス", "情報", "受領側プロセス", "関係"),
    },
    "source-processes": {
        "en": ("Source Process", "Reference"),
        "ja": ("出典プロセス", "参照"),
    },
    "included": {
        "en": ("Source Process", "Source element"),
        "ja": ("出典プロセス", "出典要素"),
    },
}

_SKILL_NAME = r"[a-z0-9]+(?:-[a-z0-9]+)*"
_PACKAGE_ID = rf"[a-z0-9]+(?:-[a-z0-9]+)*(?:/[a-z0-9]+(?:-[a-z0-9]+)*)*"
_REFERENCE_RE = re.compile(
    rf"skill:(?:#(?P<bare_name>{_SKILL_NAME})|(?P<package>{_PACKAGE_ID})#(?P<name>{_SKILL_NAME}))\Z"
)
_REFERENCE_SPAN_RE = re.compile(r"(?<!`)(`[^`\n]+`)(?!`)")
_SETEXT_RE = re.compile(r"^(?:=+|-+)\s*$")
_FENCE_RE = re.compile(r"^(?P<run>`{3,}|~{3,})(?P<info>.*)$")
_HTML_TAG_RE = re.compile(r"</?[A-Za-z][^>]*>|<![A-Za-z][^>]*>")
_HTML_OPEN_RE = re.compile(r"<(?P<close>/)?(?P<name>[A-Za-z][A-Za-z0-9:-]*)\b[^>]*>")
_BLOCK_TAGS = frozenset(
    ("article", "blockquote", "details", "div", "li", "ol", "p", "pre", "script", "section", "style", "table", "ul")
)
_ORDERED_ITEM_RE = re.compile(r"^([1-9][0-9]*)\. (\S(?:.*\S)?)\s*$")
_UNORDERED_ITEM_RE = re.compile(r"^- (\S(?:.*\S)?)\s*$")
_LIST_LIKE_RE = re.compile(r"^(?:[-+*]|[0-9]+[.)])(?:\s|$)")
_QUALITY_RE = re.compile(
    r"\b(?:is|are|was|were)\s+(?:only\s+)?(?:recorded|documented)\b", re.IGNORECASE
)
_QUALITY_JA_RE = re.compile(r"(?:が|は)(?:記録|文書化)されている")
_CONTROL_RE = re.compile(r"\bapplicable Controls?\b", re.IGNORECASE)
_CONTROL_JA_RE = re.compile(r"適用(?:される)?(?:統制事項|Control)")
_EN_MARKER_RE = re.compile(
    r"(?<![A-Za-z0-9_-])(?:must not|should not|typically|must|should|may)(?![A-Za-z0-9_-])",
    re.IGNORECASE,
)
_EN_MARKER_CLASSES = {
    "must not": "must-not",
    "must": "must",
    "should not": "should-not",
    "should": "should",
    "may": "may",
    "typically": "typically",
}
_JA_MARKERS = (
    ("must-not", "てはならない"), ("must-not", "ではならない"), ("must-not", "禁止される"),
    ("must", "必要がある"), ("must", "なければならない"),
    ("should-not", "のが望ましくない"), ("should-not", "ことが望ましくない"), ("should-not", "避けるのが望ましい"),
    ("should", "のが望ましい"), ("should", "ことが望ましい"),
    ("may", "てよい"), ("may", "でもよい"), ("may", "てもよい"), ("may", "でよい"),
    ("typically", "通常"), ("typically", "典型的"),
)
_JA_MARKER_RE = re.compile("|".join(re.escape(text) for _, text in sorted(_JA_MARKERS, key=lambda item: -len(item[1]))))
_SKILL_LINE_PREFIX = {"en": "Skill: ", "ja": "スキル: "}
_SKILL_PREFIX_RE = re.compile(r"^(?:Skill|スキル)(?::|：)")


def _span(line: int, start: int = 0, end: int | None = None) -> Span:
    return Span(start=start, end=end if end is not None else start, line=line, column=start)


def _diagnostic(
    path: str,
    code: str,
    message: str,
    line: int | None = None,
    *,
    class_name: str = "unsupported-profile-syntax",
    severity: Severity = Severity.ERROR,
    span: Span | None = None,
) -> Diagnostic:
    return Diagnostic(class_name, code, severity, path, line, message, span)


def parse_reference_token(
    token: str,
    line: int | None = None,
    column: int | None = None,
) -> Reference | None:
    """Parse exactly one canonical single-backtick Skill reference."""
    if len(token) < 4 or not token.startswith("`") or not token.endswith("`"):
        return None
    if "`" in token[1:-1]:
        return None
    match = _REFERENCE_RE.fullmatch(token[1:-1])
    if match is None:
        return None
    start = column or 0
    skill_name = match.group("bare_name") or match.group("name")
    return Reference(
        token=token,
        skill_name=skill_name,
        package_id=match.group("package"),
        line=line,
        span=_span(line, start, start + len(token)) if line is not None else None,
    )


def _locale_key(locale: str) -> str:
    return "ja" if locale.lower().split("-", 1)[0] == "ja" else "en"


def _closing_marker(text: str) -> bool:
    return bool(re.search(r"(?:^|[ \t])#+[ \t]*$", text))


def _heading(line: str) -> tuple[int, str] | None:
    match = re.match(r"^(#{1,6})( )(.+)$", line)
    if match is None:
        return None
    text = match.group(3)
    if not text.strip() or _closing_marker(text):
        return None
    return len(match.group(1)), text


@dataclass(frozen=True)
class _VisibleLine:
    number: int
    text: str | None
    level: int | None = None
    heading: str | None = None
    opaque_kind: str | None = None


@dataclass(frozen=True)
class _TableRow:
    line: int
    cells: tuple[str, ...]
    span: Span


@dataclass(frozen=True)
class _Table:
    line: int
    header: tuple[str, ...]
    rows: tuple[_TableRow, ...]


def _is_indented_container(line: str) -> bool:
    if not line or line[0] not in " \t":
        return False
    stripped = line.lstrip(" \t")
    if stripped.startswith(("#", ">", "|")):
        return True
    if re.match(r"^(?:[-+*]|\d+[.)])\s", stripped):
        return True
    if re.match(r"^(?:`{3,}|~{3,})", stripped):
        return True
    return line.startswith("\t") or len(line) - len(stripped) >= 4


def _fence_closes(line: str, char: str, length: int) -> bool:
    if not line.startswith(char * length):
        return False
    end = 0
    while end < len(line) and line[end] == char:
        end += 1
    return all(item == " " for item in line[end:])


_NESTED_CONTAINER_RE = re.compile(
    r"^(?:[-+*]|\d+[.)])\s+(?:`{3,}|~{3,}|>)"
)


def _scan(
    path: str,
    lines: Sequence[str],
    body_start: int,
) -> tuple[tuple[_VisibleLine, ...] | None, tuple[Diagnostic, ...]]:
    """Classify body lines once; opaque container bodies are never retained."""
    diagnostics: list[Diagnostic] = []
    try:
        line_count = len(lines)
    except TypeError:
        return None, (
            _diagnostic(path, "line-boundary", "input lines have no bounded length", class_name="host-input"),
        )
    if body_start < 0 or body_start > line_count:
        return None, (
            _diagnostic(path, "body-boundary", "frontmatter body boundary is outside the input", class_name="host-input"),
        )

    visible: list[_VisibleLine] = []
    fence: tuple[str, int, int] | None = None
    comment_line: int | None = None
    html_tag: tuple[str, int] | None = None
    state_count = 0

    def hidden(number: int, opaque_kind: str = "opaque") -> None:
        visible.append(_VisibleLine(number, None, opaque_kind=opaque_kind))

    def push_state() -> bool:
        nonlocal state_count
        if state_count >= MAX_ACTIVE_CONTAINER_STATES:
            diagnostics.append(
                _diagnostic(
                    path,
                    "state-limit",
                    f"more than {MAX_ACTIVE_CONTAINER_STATES} container state is active",
                    class_name="profile-structure",
                )
            )
            return False
        state_count += 1
        return True

    def pop_state() -> None:
        nonlocal state_count
        state_count = max(0, state_count - 1)

    for index, raw_line in enumerate(lines):
        number = index + 1
        if not isinstance(raw_line, str):
            diagnostics.append(
                _diagnostic(path, "line-type", "input line is not text", number, class_name="host-input")
            )
            return None, deterministic_diagnostics(diagnostics)
        if index < body_start:
            continue
        line = raw_line

        if fence is not None:
            char, length, _opened = fence
            if _fence_closes(line, char, length):
                fence = None
                pop_state()
            hidden(number)
            continue

        if comment_line is not None:
            if "<!--" in line:
                diagnostics.append(
                    _diagnostic(path, "nested-comment", "nested HTML comments are unsupported", number)
                )
            if "-->" in line:
                comment_line = None
                pop_state()
            hidden(number, "comment")
            continue

        if html_tag is not None:
            tags = list(_HTML_OPEN_RE.finditer(line))
            closed = any(
                match.group("close") and match.group("name").lower() == html_tag[0]
                for match in tags
            )
            if len(tags) > 1 or any(not match.group("close") for match in tags):
                diagnostics.append(
                    _diagnostic(path, "nested-html", "nested raw HTML blocks are unsupported", number)
                )
            if closed:
                html_tag = None
                pop_state()
            hidden(number)
            continue

        if line.startswith(">") or (line[:1] in " \t" and line.lstrip(" \t").startswith(">")):
            if line.startswith(">>") or line.startswith("> >"):
                diagnostics.append(
                    _diagnostic(path, "nested-blockquote", "nested blockquotes are unsupported", number)
                )
            elif line[:1] in " \t":
                diagnostics.append(
                    _diagnostic(path, "indented-container", "indented blockquotes are unsupported", number)
                )
            hidden(number)
            continue

        if _NESTED_CONTAINER_RE.match(line):
            diagnostics.append(
                _diagnostic(path, "nested-container", "fences and blockquotes cannot be nested in list containers", number)
            )
            hidden(number)
            continue

        if _is_indented_container(line):
            diagnostics.append(
                _diagnostic(path, "indented-container", "indented headings, lists, tables, and code are unsupported", number)
            )
            hidden(number)
            continue

        fence_match = _FENCE_RE.match(line)
        if fence_match is not None:
            run = fence_match.group("run")
            if push_state():
                fence = (run[0], len(run), number)
            hidden(number)
            continue

        if "<!--" in line:
            if "-->" not in line[line.find("<!--") + 4:]:
                if push_state():
                    comment_line = number
            else:
                trailing = line[line.find("<!--") + 4:]
                if "<!--" in trailing[:trailing.find("-->")]:
                    diagnostics.append(
                        _diagnostic(path, "nested-comment", "nested HTML comments are unsupported", number)
                    )
            hidden(number, "comment")
            continue
        if "-->" in line:
            diagnostics.append(
                _diagnostic(path, "comment-close", "HTML comment close has no matching opener", number)
            )
            hidden(number)
            continue

        html_tags = list(_HTML_TAG_RE.finditer(line))
        if html_tags or re.search(r"<[A-Za-z][^>]*$", line):
            diagnostics.append(
                _diagnostic(path, "raw-html", "raw HTML tags and blocks are unsupported", number)
            )
            opens = list(_HTML_OPEN_RE.finditer(line))
            if opens and not any(match.group("close") for match in opens):
                name = opens[0].group("name").lower()
                if name in _BLOCK_TAGS and not line.rstrip().endswith("/>") and push_state():
                    html_tag = (name, number)
            if len(opens) > 1:
                diagnostics.append(
                    _diagnostic(path, "nested-html", "nested raw HTML blocks are unsupported", number)
                )
            hidden(number)
            continue

        if _SETEXT_RE.fullmatch(line):
            diagnostics.append(
                _diagnostic(path, "setext-heading", "Setext headings and horizontal-rule syntax are unsupported", number)
            )
            hidden(number)
            continue

        if line.startswith("#"):
            heading_match = re.match(r"^(#+)([ \t]?)(.*)$", line)
            if heading_match is None:
                hidden(number)
                continue
            hashes, separator, text = heading_match.groups()
            if len(hashes) > 6:
                diagnostics.append(
                    _diagnostic(path, "heading-level", "heading levels above H6 are unsupported", number)
                )
                hidden(number)
                continue
            if separator == "\t":
                code = "literal-tab-h1" if len(hashes) == 1 else "tab-heading"
                diagnostics.append(_diagnostic(path, code, "heading separators must be one ASCII space", number))
                hidden(number)
                continue
            if separator != " " or not text.strip():
                diagnostics.append(
                    _diagnostic(path, "malformed-heading", "headings require an unindented text form", number)
                )
                hidden(number)
                continue
            if _closing_marker(text):
                diagnostics.append(
                    _diagnostic(path, "closing-heading", "closing ATX heading markers are unsupported", number)
                )
                hidden(number)
                continue
            record = _VisibleLine(number, line, len(hashes), text)
            visible.append(record)
            continue

        record = _VisibleLine(number, line)
        visible.append(record)

    if fence is not None:
        diagnostics.append(
            _diagnostic(path, "unclosed-fence", "fenced block is not closed", fence[2])
        )
    if comment_line is not None:
        diagnostics.append(
            _diagnostic(path, "unclosed-comment", "HTML comment is not closed", comment_line)
        )
    if html_tag is not None:
        diagnostics.append(
            _diagnostic(path, "unclosed-html", "raw HTML block is not closed", html_tag[1])
        )
    return tuple(visible), deterministic_diagnostics(diagnostics)


def _make_section_ir(
    title: str,
    key: str,
    item: _VisibleLine,
    prose: str | None = None,
) -> SectionIR:
    return SectionIR(
        title=title,
        level=2,
        line=item.number,
        span=_span(item.number, 0, len(item.text or "")),
        prose=prose,
        key=key,
    )


def _make_document_ir(
    path: str,
    locale: str,
    frontmatter: Frontmatter,
    sections: tuple[SectionIR, ...],
    title: str | None,
    **values: object,
) -> DocumentIR:
    return DocumentIR(
        path=path,
        locale=locale,
        frontmatter=frontmatter,
        sections=sections,
        kind=frontmatter.kind,
        title=title,
        **values,
    )


def _section_structure(
    path: str,
    locale: str,
    kind: str,
    lines: Sequence[_VisibleLine],
) -> tuple[tuple[SectionIR, ...], tuple[Diagnostic, ...], str | None]:
    diagnostics: list[Diagnostic] = []
    locale_key = _locale_key(locale)
    headings = _SECTION_NAMES[locale_key]
    reverse_headings = {value: key for key, value in headings.items()}
    order = _SECTION_ORDER.get(kind)

    h1_lines = [item for item in lines if item.level == 1]
    h1_title = h1_lines[0].heading.strip() if h1_lines and h1_lines[0].heading else None
    if not h1_lines:
        diagnostics.append(
            _diagnostic(
                path, "missing-h1", "exactly one unindented '# ' H1 is required",
                class_name="profile-structure",
            )
        )
    elif len(h1_lines) > 1:
        diagnostics.append(
            _diagnostic(
                path, "duplicate-h1", "exactly one unindented H1 is allowed", h1_lines[1].number,
                class_name="profile-structure", span=_span(h1_lines[1].number, 0, len(h1_lines[1].text or "")),
            )
        )

    if order is None:
        diagnostics.append(
            _diagnostic(
                path, "unsupported-kind", f"unsupported frontmatter kind: {kind}",
                class_name="profile-structure",
            )
        )
        return (), deterministic_diagnostics(diagnostics), h1_title

    allowed = frozenset(order)
    sections: list[SectionIR] = []
    seen: dict[str, _VisibleLine] = {}
    last_index = -1
    order_index = {key: index for index, key in enumerate(order)}
    for item in lines:
        if item.level != 2:
            continue
        if h1_lines and item.number < h1_lines[0].number:
            diagnostics.append(
                _diagnostic(
                    path, "h1-order", "the H1 must precede every semantic H2", item.number,
                    class_name="profile-structure",
                )
            )
            continue
        if not h1_lines:
            continue
        key = reverse_headings.get(item.heading or "")
        if key is None:
            diagnostics.append(
                _diagnostic(
                    path, "unrecognized-h2", "H2 text is not an exact localized profile section", item.number,
                    span=_span(item.number, 0, len(item.text or "")),
                )
            )
            continue
        if key not in allowed:
            diagnostics.append(
                _diagnostic(
                    path, "section-not-allowed", f"section is not allowed for kind {kind}: {item.heading}",
                    item.number, class_name="profile-structure",
                )
            )
            continue
        if key in seen:
            diagnostics.append(
                _diagnostic(
                    path, "duplicate-section", f"section occurs more than once: {item.heading}", item.number,
                    class_name="profile-structure", span=_span(item.number, 0, len(item.text or "")),
                )
            )
            continue
        index = order_index[key]
        if index < last_index:
            diagnostics.append(
                _diagnostic(
                    path, "section-order", f"section is out of order: {item.heading}", item.number,
                    class_name="profile-structure",
                )
            )
        last_index = max(last_index, index)
        seen[key] = item
        sections.append(
            _make_section_ir(item.heading or "", key, item)
        )

    for key in order:
        if key in _REQUIRED_SECTIONS[kind] and key not in seen:
            diagnostics.append(
                _diagnostic(
                    path, "missing-section", f"required section is missing: {headings[key]}",
                    class_name="profile-structure",
                )
            )
    return tuple(sections), deterministic_diagnostics(diagnostics), h1_title


def _section_blocks(
    locale: str,
    kind: str,
    lines: Sequence[_VisibleLine],
    h1_title: str | None,
) -> dict[str, tuple[_VisibleLine, ...]]:
    """Return bounded visible blocks delimited by the next visible H2."""
    names = _SECTION_NAMES[_locale_key(locale)]
    reverse = {value: key for key, value in names.items()}
    allowed = frozenset(_SECTION_ORDER.get(kind, ()))
    h1_line = next((item.number for item in lines if item.level == 1), None)
    blocks: dict[str, tuple[_VisibleLine, ...]] = {}
    for index, item in enumerate(lines):
        if item.level != 2 or item.number < (h1_line or 0):
            continue
        key = reverse.get(item.heading or "")
        if key is None or key not in allowed or key in blocks:
            continue
        end = len(lines)
        for following in range(index + 1, len(lines)):
            if lines[following].level == 2:
                end = following
                break
        blocks[key] = tuple(lines[index + 1:end])
    return blocks


def _required_prose(
    path: str,
    block: Sequence[_VisibleLine],
    label: str,
) -> tuple[str | None, int | None, tuple[Diagnostic, ...]]:
    """Extract visible prose and diagnose headings in a required prose block."""
    parts: list[str] = []
    first_line: int | None = None
    diagnostics: list[Diagnostic] = []
    for item in block:
        if item.text is None:
            continue
        if item.level is not None:
            if item.level < 3 or item.level > 6:
                continue
            diagnostics.append(
                _diagnostic(
                    path,
                    "required-prose-heading",
                    f"H{item.level} headings are unsupported inside required {label} prose",
                    item.number,
                )
            )
            continue
        text = item.text.strip()
        if not text:
            continue
        if first_line is None:
            first_line = item.number
        parts.append(text)
    return " ".join(parts) or None, first_line, deterministic_diagnostics(diagnostics)


def _in_link_destination(text: str, start: int, end: int) -> bool:
    prefix = text[:start].rstrip()
    suffix = text[end:].lstrip()
    return prefix.endswith("](") and suffix.startswith(")")


def _visible_references(text: str, line: int) -> tuple[Reference, ...]:
    references: list[Reference] = []
    for match in _REFERENCE_SPAN_RE.finditer(text):
        if _in_link_destination(text, match.start(), match.end()):
            continue
        reference = parse_reference_token(match.group(1), line, match.start())
        if reference is not None:
            references.append(reference)
    return tuple(references)


def _dedupe_references(references: Sequence[Reference]) -> tuple[Reference, ...]:
    deduplicated: list[Reference] = []
    seen_spans: set[tuple[int | None, int, int]] = set()
    for reference in references:
        if reference.span is None:
            deduplicated.append(reference)
            continue
        key = (reference.span.line or reference.line, reference.span.start, reference.span.end)
        if key in seen_spans:
            continue
        seen_spans.add(key)
        deduplicated.append(reference)
    return tuple(deduplicated)


def _unique_document_references(
    references: Sequence[Reference],
) -> tuple[Reference, ...]:
    """Bound document-level references by distinct lexical tokens.

    Record IR keeps ordered repeated references for locale comparison.  The
    document aggregate is a separate allocation boundary: short and qualified
    spellings remain distinct here and are normalized later by resolution.
    Retain only one overflow item so callers can emit the deterministic limit
    diagnostic without allocating an unbounded aggregate.
    """
    unique: list[Reference] = []
    seen_tokens: set[str] = set()
    for reference in references:
        if reference.token in seen_tokens:
            continue
        seen_tokens.add(reference.token)
        unique.append(reference)
        if len(unique) > MAX_RECORDS_PER_SECTION:
            break
    return tuple(unique)


def _block_visible_references(block: Sequence[_VisibleLine]) -> tuple[Reference, ...]:
    references: list[Reference] = []
    for item in block:
        if item.text is not None and item.level is None:
            references.extend(_visible_references(item.text, item.number))
    return _dedupe_references(references)


def _non_machine_references(
    blocks: dict[str, tuple[_VisibleLine, ...]],
    machine_keys: frozenset[str],
) -> tuple[Reference, ...]:
    references: list[Reference] = []
    for key, block in blocks.items():
        if key not in machine_keys:
            references.extend(_block_visible_references(block))
    return _dedupe_references(references)


def _normative_class(text: str) -> str | None:
    candidates: list[tuple[int, int, str]] = []
    for match in _EN_MARKER_RE.finditer(text):
        candidates.append(
            (match.start(), match.end(), _EN_MARKER_CLASSES[match.group(0).lower()])
        )
    japanese_classes = {marker: class_name for class_name, marker in _JA_MARKERS}
    for match in _JA_MARKER_RE.finditer(text):
        candidates.append((match.start(), match.end(), japanese_classes[match.group(0)]))
    candidates.sort(key=lambda item: (item[0], -(item[1] - item[0])))
    last: str | None = None
    cursor = -1
    for start, end, class_name in candidates:
        if start < cursor:
            continue
        last = class_name
        cursor = end
    return last


def _table_like(text: str) -> bool:
    stripped = text.strip()
    return stripped.startswith("|") or stripped.endswith("|")


def _nested_continuation(text: str) -> bool:
    return (
        text.startswith("   ")
        and not text.startswith("    ")
        and _LIST_LIKE_RE.match(text[3:]) is not None
    )


def _endpoint_has_reference_form(text: str) -> bool:
    return "`" in text or re.search(r"skill:", text, re.IGNORECASE) is not None


def _table_cells(text: str, width: int) -> tuple[str, ...] | None:
    if not text.startswith("|") or not text.endswith("|"):
        return None
    pieces = text.split("|")
    if len(pieces) != width + 2:
        return None
    cells: list[str] = []
    for piece in pieces[1:-1]:
        if piece == " ":
            cells.append("")
            continue
        if len(piece) < 3 or not piece.startswith(" ") or not piece.endswith(" "):
            return None
        content = piece[1:-1]
        if not content or content[0].isspace() or content[-1].isspace():
            return None
        cells.append(content)
    return tuple(cells)


def _parse_table(
    path: str,
    locale: str,
    block: Sequence[_VisibleLine],
    schema: str,
) -> tuple[_Table | None, tuple[Diagnostic, ...]]:
    diagnostics: list[Diagnostic] = []
    expected = _TABLE_HEADERS[schema][_locale_key(locale)]
    width = len(expected)
    table_line: int | None = None
    header: tuple[str, ...] | None = None
    rows: list[_TableRow] = []
    table_seen = False
    closed = False
    separator_ok = False
    over_limit = False

    def tableish(text: str) -> bool:
        return "|" in text

    for item in block:
        if item.text is None:
            if table_seen:
                closed = True
            continue
        text = item.text
        if not text.strip():
            if table_seen:
                closed = True
            continue
        if item.level is not None:
            diagnostics.append(
                _diagnostic(path, "table-heading", "headings are unsupported inside a machine-bearing table section", item.number)
            )
            if table_seen:
                closed = True
            continue
        if not tableish(text):
            if _LIST_LIKE_RE.match(text):
                diagnostics.append(
                    _diagnostic(path, "table-mixed-content", "machine-bearing table sections cannot use a mixed list representation", item.number)
                )
            if table_seen:
                closed = True
            continue
        if closed:
            diagnostics.append(
                _diagnostic(path, "table-second", "machine-bearing section contains a second or mixed table", item.number)
            )
            continue
        if not table_seen:
            table_seen = True
            table_line = item.number
            cells = _table_cells(text, width)
            if cells is None:
                diagnostics.append(
                    _diagnostic(path, "table-width", "table header must have exact outer pipes and width", item.number)
                )
                header = ()
            else:
                header = cells
                if cells != expected:
                    diagnostics.append(
                        _diagnostic(path, "table-header", "table header is not the exact localized schema header", item.number)
                    )
            continue
        cells = _table_cells(text, width)
        if not separator_ok:
            if cells is None:
                diagnostics.append(
                    _diagnostic(path, "table-separator", "table separator must have exact width and outer pipes", item.number)
                )
            elif any(cell != "---" for cell in cells):
                diagnostics.append(
                    _diagnostic(path, "table-separator", "table separator cells must be exactly '---'", item.number)
                )
            else:
                separator_ok = True
            continue
        if cells is None:
            diagnostics.append(
                _diagnostic(path, "table-width", "table data rows must have exact width and no cell pipes", item.number)
            )
            continue
        if len(rows) >= MAX_RECORDS_PER_SECTION:
            if not over_limit:
                diagnostics.append(_record_limit_diagnostic(path, item.number, "table"))
                over_limit = True
            continue
        rows.append(_TableRow(item.number, cells, _span(item.number, 0, len(text))))

    if not table_seen:
        diagnostics.append(
            _diagnostic(path, "table-missing", "machine-bearing section requires exactly one table", class_name="profile-structure")
        )
        return None, deterministic_diagnostics(diagnostics)
    return _Table(table_line or 0, header or (), tuple(rows)), deterministic_diagnostics(diagnostics)


def _designated_reference(
    path: str,
    cell: str,
    line: int,
    *,
    required: bool = True,
) -> tuple[Reference | None, tuple[Diagnostic, ...]]:
    value = cell.strip()
    if not value and not required:
        return None, ()
    reference = parse_reference_token(value, line, 0)
    if reference is None:
        return None, (
            _diagnostic(
                path, "malformed-reference", "designated reference field must contain one exact single-backtick Skill reference", line
            ),
        )
    return reference, ()


def _parse_relationships(
    path: str,
    locale: str,
    block: Sequence[_VisibleLine],
) -> tuple[tuple[RelationshipIR, ...], tuple[Diagnostic, ...]]:
    table, table_diagnostics = _parse_table(path, locale, block, "relationships")
    diagnostics = list(table_diagnostics)
    relationships: list[RelationshipIR] = []
    if table is None:
        return (), deterministic_diagnostics(diagnostics)
    for row in table.rows:
        if len(row.cells) != 4:
            continue
        if any(not cell for cell in row.cells):
            diagnostics.append(
                _diagnostic(path, "relationship-empty", "relationship table cells must be non-empty", row.line, class_name="semantic")
            )
        for endpoint in (row.cells[0], row.cells[2]):
            if _endpoint_has_reference_form(endpoint):
                diagnostics.append(
                    _diagnostic(
                        path,
                        "relationship-endpoint-reference",
                        "relationship endpoint cells cannot contain code spans or Skill reference forms",
                        row.line,
                    )
                )
        relationships.append(
            RelationshipIR(
                provider_process=row.cells[0],
                information=row.cells[1],
                recipient_process=row.cells[2],
                relationship=row.cells[3],
                line=row.line,
                span=row.span,
            )
        )
    if not relationships:
        diagnostics.append(
            _diagnostic(path, "relationship-empty", "Relationships requires at least one data row", class_name="profile-structure")
        )
    return tuple(relationships), deterministic_diagnostics(diagnostics)


def _extract_process_model(
    path: str,
    locale: str,
    blocks: dict[str, tuple[_VisibleLine, ...]],
    sections: tuple[SectionIR, ...],
) -> tuple[
    str | None,
    tuple[ProcessEntryIR, ...],
    tuple[RelationshipIR, ...],
    tuple[Reference, ...],
    tuple[SectionIR, ...],
    tuple[Diagnostic, ...],
]:
    diagnostics: list[Diagnostic] = []
    purpose: str | None = None
    if "purpose" in blocks:
        purpose, purpose_line, purpose_diagnostics = _required_prose(
            path, blocks["purpose"], "Purpose"
        )
        diagnostics.extend(purpose_diagnostics)
        if purpose is None:
            diagnostics.append(
                _diagnostic(path, "purpose-empty", "Purpose must contain non-empty normalized prose", purpose_line, class_name="profile-structure")
            )

    processes: list[ProcessEntryIR] = []
    references: list[Reference] = []
    names: set[str] = set()
    identities: set[str] = set()
    if "processes" in blocks:
        table, table_diagnostics = _parse_table(path, locale, blocks["processes"], "processes")
        diagnostics.extend(table_diagnostics)
        if table is not None:
            for row in table.rows:
                if len(row.cells) != 2:
                    continue
                name = row.cells[0].strip()
                if not name:
                    diagnostics.append(
                        _diagnostic(path, "process-name-empty", "Process display names must be non-empty", row.line, class_name="semantic")
                    )
                reference, reference_diagnostics = _designated_reference(
                    path, row.cells[1], row.line, required=False
                )
                diagnostics.extend(reference_diagnostics)
                identity = reference.token if reference is not None else name
                if name in names or identity in identities:
                    diagnostics.append(
                        _diagnostic(path, "process-duplicate", "Process display names and identities must be unique", row.line, class_name="semantic")
                    )
                names.add(name)
                identities.add(identity)
                if reference is not None:
                    references.append(reference)
                processes.append(
                    ProcessEntryIR(name=name, line=row.line, reference=reference, span=row.span)
                )
        if not processes:
            diagnostics.append(
                _diagnostic(path, "process-empty", "Processes requires at least one table row", class_name="profile-structure")
            )

    relationships: tuple[RelationshipIR, ...] = ()
    if "relationships" in blocks:
        relationships, relationship_diagnostics = _parse_relationships(
            path, locale, blocks["relationships"]
        )
        diagnostics.extend(relationship_diagnostics)
        for relationship in relationships:
            provider_invalid = (
                not _endpoint_has_reference_form(relationship.provider_process)
                and relationship.provider_process not in names
            )
            recipient_invalid = (
                not _endpoint_has_reference_form(relationship.recipient_process)
                and relationship.recipient_process not in names
            )
            if provider_invalid or recipient_invalid:
                diagnostics.append(
                    _diagnostic(path, "relationship-endpoint", "relationship endpoints must be declared Process display names", relationship.line, class_name="semantic")
                )

    references.extend(
        _non_machine_references(blocks, frozenset(("processes", "relationships")))
    )
    references = list(_unique_document_references(references))
    if len(references) > MAX_RECORDS_PER_SECTION:
        references = references[:MAX_RECORDS_PER_SECTION]
        diagnostics.append(
            _diagnostic(path, "reference-limit", f"Process Model references exceed {MAX_RECORDS_PER_SECTION} records", class_name="profile-structure")
        )

    purpose_title = _SECTION_NAMES[_locale_key(locale)]["purpose"]
    annotated_sections = tuple(
        replace(section, prose=purpose) if section.title == purpose_title else section
        for section in sections
    )
    return (
        purpose,
        tuple(processes),
        relationships,
        tuple(references),
        annotated_sections,
        deterministic_diagnostics(diagnostics),
    )


def _parse_reference_entry(
    path: str,
    locale: str,
    name: str,
    line: int,
    body: Sequence[_VisibleLine],
) -> tuple[ProcessEntryIR, tuple[Reference, ...], tuple[Diagnostic, ...]]:
    diagnostics: list[Diagnostic] = []
    references: list[Reference] = []
    skill: Reference | None = None
    h4 = [(index, item) for index, item in enumerate(body) if item.level == 4]
    purpose_key = _SECTION_NAMES[_locale_key(locale)]["purpose"]
    outcomes_key = _SECTION_NAMES[_locale_key(locale)]["outcomes"]

    for item in body:
        if item.level in (5, 6):
            diagnostics.append(
                _diagnostic(path, "reference-entry-heading", "H5-H6 are unsupported in a Reference Model entry", item.number)
            )

    preamble_end = h4[0][0] if h4 else len(body)
    expected_prefix = _SKILL_LINE_PREFIX[_locale_key(locale)]
    saw_visible = False
    for item in body[:preamble_end]:
        if item.text is None:
            if item.opaque_kind != "comment":
                diagnostics.append(
                    _diagnostic(
                        path,
                        "reference-entry-preamble",
                        "only blank lines, HTML comments, and one optional localized Skill line are permitted before the first H4",
                        item.number,
                    )
                )
            continue
        if not item.text.strip():
            continue
        if item.text.startswith(expected_prefix):
            if saw_visible or skill is not None:
                diagnostics.append(
                    _diagnostic(path, "skill-position", "Skill must be the optional first visible line before the first H4", item.number)
                )
                saw_visible = True
                continue
            skill, reference_diagnostics = _designated_reference(
                path, item.text[len(expected_prefix):], item.number
            )
            diagnostics.extend(reference_diagnostics)
            if skill is not None:
                references.append(skill)
            saw_visible = True
            continue
        if _SKILL_PREFIX_RE.match(item.text.strip()):
            diagnostics.append(
                _diagnostic(path, "skill-locale", "Skill line prefix must exactly match the document locale", item.number)
            )
        else:
            diagnostics.append(
                _diagnostic(
                    path,
                    "reference-entry-preamble",
                    "arbitrary prose is unsupported before the first Reference Model entry H4",
                    item.number,
                )
            )
        saw_visible = True

    for item in body[preamble_end:]:
        if item.text is not None and _SKILL_PREFIX_RE.match(item.text.strip()):
            diagnostics.append(
                _diagnostic(path, "skill-position", "Skill line is permitted only before the first H4", item.number)
            )

    purpose: str | None = None
    outcomes: tuple[OutcomeIR, ...] = ()
    if not h4:
        diagnostics.append(
            _diagnostic(path, "reference-entry-headings", "Reference Model entries require H4 Purpose followed by H4 Outcomes", line, class_name="profile-structure")
        )
    else:
        if h4[0][1].heading != purpose_key:
            diagnostics.append(
                _diagnostic(path, "reference-entry-purpose", "the first entry H4 must be the exact localized Purpose heading", h4[0][1].number, class_name="profile-structure")
            )
        if len(h4) < 2:
            diagnostics.append(
                _diagnostic(path, "reference-entry-outcomes", "Reference Model entries require H4 Outcomes after Purpose", h4[0][1].number, class_name="profile-structure")
            )
        elif h4[1][1].heading != outcomes_key:
            diagnostics.append(
                _diagnostic(path, "reference-entry-outcomes", "the second entry H4 must be the exact localized Outcomes heading", h4[1][1].number, class_name="profile-structure")
            )
        if len(h4) > 2:
            for _, item in h4[2:]:
                diagnostics.append(
                    _diagnostic(path, "reference-entry-heading", "only Purpose and Outcomes H4 headings are permitted", item.number)
                )
        if len(h4) >= 2:
            purpose_block = body[h4[0][0] + 1:h4[1][0]]
            purpose, purpose_line, purpose_diagnostics = _required_prose(
                path, purpose_block, "Reference Model Process Purpose"
            )
            diagnostics.extend(purpose_diagnostics)
            references.extend(_block_visible_references(purpose_block))
            if purpose is None:
                diagnostics.append(
                    _diagnostic(path, "purpose-empty", "Reference Model Process Purpose must be non-empty", purpose_line, class_name="profile-structure")
                )
            end = h4[2][0] if len(h4) > 2 else len(body)
            outcomes, outcome_diagnostics = _parse_outcomes(path, body[h4[1][0] + 1:end])
            diagnostics.extend(outcome_diagnostics)

    references.extend(reference for outcome in outcomes for reference in outcome.references)
    entry = ProcessEntryIR(
        name=name,
        line=line,
        purpose=purpose,
        outcomes=outcomes,
        reference=skill,
        span=_span(line, 0, len(name) + 4),
    )
    return entry, _dedupe_references(references), deterministic_diagnostics(diagnostics)


def _extract_reference_model(
    path: str,
    locale: str,
    blocks: dict[str, tuple[_VisibleLine, ...]],
    sections: tuple[SectionIR, ...],
) -> tuple[
    str | None,
    tuple[ProcessEntryIR, ...],
    tuple[RelationshipIR, ...],
    tuple[Reference, ...],
    tuple[SectionIR, ...],
    tuple[Diagnostic, ...],
]:
    diagnostics: list[Diagnostic] = []
    purpose: str | None = None
    if "purpose" in blocks:
        purpose, purpose_line, purpose_diagnostics = _required_prose(
            path, blocks["purpose"], "Purpose"
        )
        diagnostics.extend(purpose_diagnostics)
        if purpose is None:
            diagnostics.append(
                _diagnostic(path, "purpose-empty", "Purpose must contain non-empty normalized prose", purpose_line, class_name="profile-structure")
            )

    entries: list[ProcessEntryIR] = []
    references: list[Reference] = []
    names: set[str] = set()
    identities: set[str] = set()
    entries_over_limit = False
    process_block = blocks.get("processes", ())
    h3_indices = [index for index, item in enumerate(process_block) if item.level == 3 and item.text is not None]
    for item in process_block:
        if item.level in (4, 5, 6) and not h3_indices:
            diagnostics.append(
                _diagnostic(path, "reference-entry-heading", "Reference Model H4-H6 headings require a preceding Process H3", item.number)
            )
    for position, start in enumerate(h3_indices):
        end = h3_indices[position + 1] if position + 1 < len(h3_indices) else len(process_block)
        item = process_block[start]
        name = (item.heading or "").strip()
        entry, entry_references, entry_diagnostics = _parse_reference_entry(
            path, locale, name, item.number, process_block[start + 1:end]
        )
        diagnostics.extend(entry_diagnostics)
        identity = entry.reference.token if entry.reference is not None else name
        if name in names or identity in identities:
            diagnostics.append(
                _diagnostic(path, "process-duplicate", "Reference Model Process names and identities must be unique", item.number, class_name="semantic")
            )
        names.add(name)
        identities.add(identity)
        references.extend(entry_references)
        if len(entries) < MAX_RECORDS_PER_SECTION:
            entries.append(entry)
        elif not entries_over_limit:
            diagnostics.append(_record_limit_diagnostic(path, item.number, "Processes"))
            entries_over_limit = True
    if not entries:
        diagnostics.append(
            _diagnostic(path, "process-empty", "Reference Model Processes requires at least one H3 entry", class_name="profile-structure")
        )

    relationships: tuple[RelationshipIR, ...] = ()
    if "relationships" in blocks:
        relationships, relationship_diagnostics = _parse_relationships(path, locale, blocks["relationships"])
        diagnostics.extend(relationship_diagnostics)
        for relationship in relationships:
            provider_invalid = (
                not _endpoint_has_reference_form(relationship.provider_process)
                and relationship.provider_process not in names
            )
            recipient_invalid = (
                not _endpoint_has_reference_form(relationship.recipient_process)
                and relationship.recipient_process not in names
            )
            if provider_invalid or recipient_invalid:
                diagnostics.append(
                    _diagnostic(path, "relationship-endpoint", "relationship endpoints must be declared Process display names", relationship.line, class_name="semantic")
                )

    references.extend(
        _non_machine_references(blocks, frozenset(("processes", "relationships")))
    )
    references = list(_unique_document_references(references))
    if len(references) > MAX_RECORDS_PER_SECTION:
        references = references[:MAX_RECORDS_PER_SECTION]
        diagnostics.append(
            _diagnostic(path, "reference-limit", f"Reference Model references exceed {MAX_RECORDS_PER_SECTION} records", class_name="profile-structure")
        )

    purpose_title = _SECTION_NAMES[_locale_key(locale)]["purpose"]
    annotated_sections = tuple(
        replace(section, prose=purpose) if section.title == purpose_title else section
        for section in sections
    )
    return (
        purpose,
        tuple(entries[:MAX_RECORDS_PER_SECTION]),
        relationships,
        tuple(references),
        annotated_sections,
        deterministic_diagnostics(diagnostics),
    )


def _parse_application(
    path: str,
    block: Sequence[_VisibleLine],
) -> tuple[tuple[ApplicationIR, ...], tuple[Diagnostic, ...]]:
    text, first_line, prose_diagnostics = _required_prose(path, block, "Application")
    if text is None:
        diagnostic = _diagnostic(
            path,
            "application-empty",
            "Application must contain visible non-empty opaque text",
            class_name="profile-structure",
        )
        return (), deterministic_diagnostics((*prose_diagnostics, diagnostic))
    references: list[Reference] = []
    for item in block:
        if item.text is not None and item.level is None and item.text.strip():
            references.extend(_visible_references(item.text, item.number))
    application = ApplicationIR(
        text=text,
        line=first_line or 0,
        references=_dedupe_references(references),
        span=_span(first_line or 0, 0, len(text)),
    )
    return (application,), prose_diagnostics


def _extract_process_view(
    path: str,
    locale: str,
    blocks: dict[str, tuple[_VisibleLine, ...]],
    sections: tuple[SectionIR, ...],
) -> tuple[
    str | None,
    tuple[OutcomeIR, ...],
    tuple[ApplicationIR, ...],
    tuple[SourceProcessIR, ...],
    tuple[IncludedActivityTaskIR, ...],
    tuple[Reference, ...],
    tuple[SectionIR, ...],
    tuple[Diagnostic, ...],
]:
    diagnostics: list[Diagnostic] = []
    purpose: str | None = None
    if "purpose" in blocks:
        purpose, purpose_line, purpose_diagnostics = _required_prose(
            path, blocks["purpose"], "Purpose"
        )
        diagnostics.extend(purpose_diagnostics)
        if purpose is None:
            diagnostics.append(
                _diagnostic(path, "purpose-empty", "Purpose must contain non-empty normalized prose", purpose_line, class_name="profile-structure")
            )

    outcomes: tuple[OutcomeIR, ...] = ()
    if "outcomes" in blocks:
        outcomes, outcome_diagnostics = _parse_outcomes(path, blocks["outcomes"])
        diagnostics.extend(outcome_diagnostics)

    applications: tuple[ApplicationIR, ...] = ()
    if "application" in blocks:
        applications, application_diagnostics = _parse_application(path, blocks["application"])
        diagnostics.extend(application_diagnostics)

    sources: list[SourceProcessIR] = []
    source_by_name: dict[str, SourceProcessIR] = {}
    source_by_reference: dict[str, SourceProcessIR] = {}
    references: list[Reference] = []
    if "source" in blocks:
        table, table_diagnostics = _parse_table(path, locale, blocks["source"], "source-processes")
        diagnostics.extend(table_diagnostics)
        if table is not None:
            for row in table.rows:
                if len(row.cells) != 2:
                    continue
                name = row.cells[0].strip()
                if not name:
                    diagnostics.append(
                        _diagnostic(path, "source-name-empty", "Source Process display names must be non-empty", row.line, class_name="semantic")
                    )
                reference, reference_diagnostics = _designated_reference(path, row.cells[1], row.line)
                diagnostics.extend(reference_diagnostics)
                source = SourceProcessIR(name=name, line=row.line, reference=reference, span=row.span)
                if name in source_by_name or (reference is not None and reference.token in source_by_reference):
                    diagnostics.append(
                        _diagnostic(path, "source-duplicate", "Source Process display names and references must be unique", row.line, class_name="semantic")
                    )
                source_by_name[name] = source
                if reference is not None:
                    source_by_reference[reference.token] = source
                    references.append(reference)
                if len(sources) < MAX_RECORDS_PER_SECTION:
                    sources.append(source)
        if len(source_by_name) < 2:
            diagnostics.append(
                _diagnostic(path, "source-count", "Process View requires at least two distinct Source Processes", table.line if table else None, class_name="semantic")
            )

    included: list[IncludedActivityTaskIR] = []
    included_keys: set[tuple[str, str, str]] = set()
    prefixes = (
        (("Activity: ", "activity"), ("Task: ", "task"))
        if _locale_key(locale) == "en"
        else (("活動: ", "activity"), ("タスク: ", "task"))
    )
    if "included" in blocks:
        table, table_diagnostics = _parse_table(path, locale, blocks["included"], "included")
        diagnostics.extend(table_diagnostics)
        if table is not None:
            for row in table.rows:
                if len(row.cells) != 2:
                    continue
                source_display = ""
                source_reference: Reference | None = None
                source_match = re.fullmatch(r"(.+) \((`[^`\n]+`)\)", row.cells[0])
                if source_match is None:
                    diagnostics.append(
                        _diagnostic(path, "included-source", "Included source must be '<display> (`skill...`)' with exact spacing", row.line)
                    )
                else:
                    source_display = source_match.group(1)
                    source_reference, reference_diagnostics = _designated_reference(path, source_match.group(2), row.line)
                    diagnostics.extend(reference_diagnostics)
                    declared = source_by_name.get(source_display)
                    if declared is None or source_reference is None or declared.reference is None:
                        diagnostics.append(
                            _diagnostic(path, "included-source", "Included source display and reference must match a declared Source Process", row.line, class_name="semantic")
                        )
                kind: str | None = None
                label = ""
                for prefix, prefix_kind in prefixes:
                    if row.cells[1].startswith(prefix):
                        label = row.cells[1][len(prefix):].strip()
                        kind = prefix_kind
                        break
                if kind is None or not label:
                    diagnostics.append(
                        _diagnostic(path, "included-prefix", "Included element requires an exact localized Activity: or Task: prefix and non-empty label", row.line)
                    )
                if source_reference is not None:
                    references.append(source_reference)
                if source_reference is None or kind is None or not label:
                    continue
                identity = (source_reference.token, kind, label)
                if identity in included_keys:
                    diagnostics.append(
                        _diagnostic(path, "included-duplicate", "Included Activity/Task identity is duplicated", row.line, class_name="semantic")
                    )
                included_keys.add(identity)
                if len(included) < MAX_RECORDS_PER_SECTION:
                    included.append(
                        IncludedActivityTaskIR(
                            source_display=source_display,
                            source_reference=source_reference,
                            kind=kind,
                            label=label,
                            line=row.line,
                            span=row.span,
                        )
                    )
        if not included:
            diagnostics.append(
                _diagnostic(path, "included-empty", "Included Activities and Tasks requires at least one data row", class_name="profile-structure")
            )

    for application in applications:
        references.extend(application.references)
    for outcome in outcomes:
        references.extend(outcome.references)
    references.extend(
        _non_machine_references(blocks, frozenset(("outcomes", "source", "included")))
    )
    references = list(_unique_document_references(references))
    if len(references) > MAX_RECORDS_PER_SECTION:
        references = references[:MAX_RECORDS_PER_SECTION]
        diagnostics.append(
            _diagnostic(path, "reference-limit", f"Process View references exceed {MAX_RECORDS_PER_SECTION} records", class_name="profile-structure")
        )

    purpose_title = _SECTION_NAMES[_locale_key(locale)]["purpose"]
    annotated_sections = tuple(
        replace(section, prose=purpose) if section.title == purpose_title else section
        for section in sections
    )
    return (
        purpose,
        outcomes,
        applications,
        tuple(sources),
        tuple(included),
        tuple(references),
        annotated_sections,
        deterministic_diagnostics(diagnostics),
    )


def _record_limit_diagnostic(path: str, line: int, kind: str) -> Diagnostic:
    return _diagnostic(
        path, "record-limit", f"{kind} section exceeds {MAX_RECORDS_PER_SECTION} records", line,
        class_name="profile-structure",
    )


def _finish_outcome(
    path: str,
    parts: list[str],
    line: int,
    outcomes: list[OutcomeIR],
    diagnostics: list[Diagnostic],
    over_limit: list[bool],
) -> None:
    if not parts:
        return
    text = " ".join(parts).strip()
    if not text:
        return
    references = _visible_references(text, line)
    if len(outcomes) >= MAX_RECORDS_PER_SECTION:
        if not over_limit[0]:
            diagnostics.append(_record_limit_diagnostic(path, line, "Outcomes"))
            over_limit[0] = True
        return
    outcomes.append(
        OutcomeIR(
            text=text,
            line=line,
            identity=references[0].token if references else None,
            references=references,
            span=_span(line, 0, len(text)),
        )
    )
    if _QUALITY_RE.search(text) or _QUALITY_JA_RE.search(text):
        diagnostics.append(
            _diagnostic(
                path, "outcome-recorded-language", "outcome wording is a bounded quality-review candidate",
                line, class_name="quality-review", severity=Severity.WARNING,
            )
        )


def _parse_outcomes(
    path: str,
    block: Sequence[_VisibleLine],
) -> tuple[tuple[OutcomeIR, ...], tuple[Diagnostic, ...]]:
    outcomes: list[OutcomeIR] = []
    diagnostics: list[Diagnostic] = []
    parts: list[str] = []
    item_line = 0
    active = False
    seen_list = False
    closed_list = False
    over_limit = [False]

    def finish() -> None:
        nonlocal parts, active
        if active:
            _finish_outcome(path, parts, item_line, outcomes, diagnostics, over_limit)
        parts = []
        active = False

    for item in block:
        if item.text is None:
            finish()
            if seen_list:
                closed_list = True
            continue
        text = item.text
        if item.level is not None:
            finish()
            diagnostics.append(
                _diagnostic(
                    path, "outcome-heading", "headings are unsupported inside Outcomes", item.number
                )
            )
            if seen_list:
                closed_list = True
            continue
        if not text.strip():
            finish()
            if seen_list:
                closed_list = True
            continue
        if _nested_continuation(text):
            finish()
            diagnostics.append(
                _diagnostic(path, "nested-list", "three-space continuations cannot contain nested list markers", item.number)
            )
            closed_list = True
            continue
        if text.startswith("   ") and not text.startswith("    "):
            if active and text[3:].strip():
                parts.append(text[3:].strip())
                continue
            finish()
            diagnostics.append(
                _diagnostic(path, "outcome-continuation", "continuations require one active item and three spaces", item.number)
            )
            closed_list = True
            continue
        match = _UNORDERED_ITEM_RE.fullmatch(text)
        if match is not None:
            if active:
                finish()
            if closed_list:
                diagnostics.append(
                    _diagnostic(path, "outcome-second-list", "Outcomes must contain one contiguous hyphen list", item.number)
                )
                continue
            seen_list = True
            active = True
            item_line = item.number
            parts = [match.group(1).strip()]
            continue
        if _LIST_LIKE_RE.match(text) or _table_like(text):
            finish()
            diagnostics.append(
                _diagnostic(path, "outcome-list-syntax", "Outcomes accept only one unindented '- ' list", item.number)
            )
            if seen_list:
                closed_list = True
            continue
        if active:
            finish()
            if seen_list:
                closed_list = True
                diagnostics.append(
                    _diagnostic(path, "outcome-trailing-prose", "prose cannot interrupt the Outcomes list", item.number)
                )
        elif seen_list:
            diagnostics.append(
                _diagnostic(path, "outcome-trailing-prose", "prose cannot follow the Outcomes list", item.number)
            )

    finish()
    if not seen_list:
        diagnostics.append(
            _diagnostic(path, "outcome-list-missing", "Outcomes requires one unindented '- ' list", class_name="profile-structure")
        )
    elif not outcomes:
        diagnostics.append(
            _diagnostic(path, "outcome-empty", "Outcomes list must contain a non-empty item", class_name="profile-structure")
        )
    return tuple(outcomes), deterministic_diagnostics(diagnostics)


def _parse_tasks(
    path: str,
    block: Sequence[_VisibleLine],
) -> tuple[tuple[TaskIR, ...], tuple[Diagnostic, ...]]:
    tasks: list[TaskIR] = []
    diagnostics: list[Diagnostic] = []
    parts: list[str] = []
    item_line = 0
    active = False
    seen_list = False
    closed_list = False
    expected = 1
    over_limit = [False]

    def finish() -> None:
        nonlocal parts, active
        if not active:
            return
        text = " ".join(parts).strip()
        references = _visible_references(text, item_line)
        normative = _normative_class(text)
        if normative is None:
            diagnostics.append(
                _diagnostic(
                    path, "normative-marker-missing", "each Task requires a recognized normative marker",
                    item_line, class_name="semantic",
                )
            )
        if text and len(tasks) < MAX_RECORDS_PER_SECTION:
            tasks.append(
                TaskIR(
                    text=text,
                    line=item_line,
                    normative_class=normative,
                    references=references,
                    span=_span(item_line, 0, len(text)),
                )
            )
        elif text and not over_limit[0]:
            diagnostics.append(_record_limit_diagnostic(path, item_line, "Tasks"))
            over_limit[0] = True
        parts = []
        active = False

    for item in block:
        if item.text is None:
            finish()
            if seen_list:
                closed_list = True
            continue
        text = item.text
        if item.level is not None:
            finish()
            diagnostics.append(
                _diagnostic(path, "activity-heading", "H4-H6 and child headings are unsupported inside Activities", item.number)
            )
            if seen_list:
                closed_list = True
            continue
        if not text.strip():
            finish()
            if seen_list:
                closed_list = True
            continue
        if _nested_continuation(text):
            finish()
            diagnostics.append(
                _diagnostic(path, "nested-list", "three-space continuations cannot contain nested list markers", item.number)
            )
            closed_list = True
            continue
        if text.startswith("   ") and not text.startswith("    "):
            if active and text[3:].strip():
                parts.append(text[3:].strip())
                continue
            finish()
            diagnostics.append(
                _diagnostic(path, "task-continuation", "continuations require one active item and three spaces", item.number)
            )
            closed_list = True
            continue
        match = _ORDERED_ITEM_RE.fullmatch(text)
        if match is not None:
            if active:
                finish()
            marker = match.group(1)
            if closed_list:
                diagnostics.append(
                    _diagnostic(path, "task-second-list", "each Activity must contain one contiguous ordered task list", item.number)
                )
                continue
            expected_marker = str(expected)
            if not seen_list and marker != "1":
                diagnostics.append(
                    _diagnostic(path, "task-list-start", "the Task list must start at 1", item.number, class_name="profile-structure")
                )
            elif seen_list and marker != expected_marker:
                diagnostics.append(
                    _diagnostic(path, "task-list-order", "Task list numbers must increment by one", item.number, class_name="profile-structure")
                )
            seen_list = True
            expected = min(expected + 1, MAX_INPUT_LINES + 1)
            active = True
            item_line = item.number
            parts = [match.group(2).strip()]
            continue
        if _LIST_LIKE_RE.match(text) or _table_like(text):
            finish()
            diagnostics.append(
                _diagnostic(path, "task-list-syntax", "Activities accept only one unindented decimal task list", item.number)
            )
            if seen_list:
                closed_list = True
            continue
        if active:
            finish()
            if seen_list:
                closed_list = True
                diagnostics.append(
                    _diagnostic(path, "task-trailing-prose", "prose cannot interrupt the Task list", item.number)
                )
        elif seen_list:
            diagnostics.append(
                _diagnostic(path, "task-trailing-prose", "prose cannot follow the Task list", item.number)
            )

    finish()
    if not seen_list:
        diagnostics.append(
            _diagnostic(path, "task-list-missing", "each Activity requires one ordered Task list", class_name="profile-structure")
        )
    elif not tasks:
        diagnostics.append(
            _diagnostic(path, "task-empty", "Task list must contain a non-empty item", class_name="profile-structure")
        )
    return tuple(tasks), deterministic_diagnostics(diagnostics)


def _parse_activities(
    path: str,
    block: Sequence[_VisibleLine],
) -> tuple[tuple[ActivityIR, ...], tuple[Diagnostic, ...]]:
    activities: list[ActivityIR] = []
    diagnostics: list[Diagnostic] = []
    current_name: str | None = None
    current_line = 0
    current_block: list[_VisibleLine] = []
    over_limit = False

    def finish() -> None:
        nonlocal current_name, current_block, over_limit
        if current_name is None:
            current_block = []
            return
        tasks, task_diagnostics = _parse_tasks(path, current_block)
        diagnostics.extend(task_diagnostics)
        if len(activities) >= MAX_RECORDS_PER_SECTION:
            if not over_limit:
                diagnostics.append(_record_limit_diagnostic(path, current_line, "Activities"))
                over_limit = True
        else:
            activities.append(
                ActivityIR(
                    name=current_name,
                    line=current_line,
                    tasks=tasks,
                    span=_span(current_line, 0, len(current_name) + 4),
                )
            )
        current_name = None
        current_block = []

    for item in block:
        if item.level == 3 and item.text is not None:
            finish()
            name = (item.heading or "").strip()
            if not name:
                diagnostics.append(
                    _diagnostic(path, "activity-name", "Activity H3 labels must be non-empty", item.number)
                )
                continue
            current_name = name
            current_line = item.number
            current_block = []
            continue
        if current_name is None:
            if item.level is not None:
                diagnostics.append(
                    _diagnostic(path, "activity-heading", "only H3 headings may start Activities", item.number)
                )
            continue
        current_block.append(item)
    finish()
    if not activities:
        diagnostics.append(
            _diagnostic(path, "activity-missing", "Activities requires at least one H3 Activity", class_name="profile-structure")
        )
    return tuple(activities), deterministic_diagnostics(diagnostics)


def _extract_process(
    path: str,
    locale: str,
    blocks: dict[str, tuple[_VisibleLine, ...]],
    sections: tuple[SectionIR, ...],
) -> tuple[
    str | None,
    tuple[OutcomeIR, ...],
    tuple[ActivityIR, ...],
    tuple[Reference, ...],
    tuple[SectionIR, ...],
    tuple[Diagnostic, ...],
]:
    diagnostics: list[Diagnostic] = []
    purpose: str | None = None
    if "purpose" in blocks:
        purpose, purpose_line, purpose_diagnostics = _required_prose(
            path, blocks["purpose"], "Purpose"
        )
        diagnostics.extend(purpose_diagnostics)
        if purpose is None:
            diagnostics.append(
                _diagnostic(
                    path, "purpose-empty", "Purpose must contain non-empty normalized prose",
                    purpose_line, class_name="profile-structure",
                )
            )

    outcomes: tuple[OutcomeIR, ...] = ()
    if "outcomes" in blocks:
        outcomes, outcome_diagnostics = _parse_outcomes(path, blocks["outcomes"])
        diagnostics.extend(outcome_diagnostics)

    activities: tuple[ActivityIR, ...] = ()
    if "activities" in blocks:
        activities, activity_diagnostics = _parse_activities(path, blocks["activities"])
        diagnostics.extend(activity_diagnostics)

    if "inputs" in blocks:
        for item in blocks["inputs"]:
            if item.text is None or item.level is not None:
                continue
            if _CONTROL_RE.search(item.text) or _CONTROL_JA_RE.search(item.text):
                diagnostics.append(
                    _diagnostic(
                        path, "input-classified-control", "Inputs text classifies an applicable Control as an Input",
                        item.number, class_name="semantic",
                    )
                )

    references: list[Reference] = []
    for outcome in outcomes:
        references.extend(outcome.references)
    for activity in activities:
        for task in activity.tasks:
            references.extend(task.references)
    references.extend(
        _non_machine_references(blocks, frozenset(("outcomes", "activities")))
    )
    references = list(_unique_document_references(references))
    if len(references) > MAX_RECORDS_PER_SECTION:
        references = references[:MAX_RECORDS_PER_SECTION]
        diagnostics.append(
            _diagnostic(
                path, "reference-limit", f"Process references exceed {MAX_RECORDS_PER_SECTION} records",
                class_name="profile-structure",
            )
        )

    purpose_title = _SECTION_NAMES[_locale_key(locale)]["purpose"]
    annotated_sections = tuple(
        replace(section, prose=purpose) if section.title == purpose_title else section
        for section in sections
    )
    return (
        purpose,
        outcomes,
        activities,
        tuple(references),
        annotated_sections,
        deterministic_diagnostics(diagnostics),
    )


def parse_markdown(
    path: str,
    locale: str,
    frontmatter: Frontmatter,
    lines: Sequence[str],
    body_start: int,
) -> tuple[DocumentIR | None, tuple[Diagnostic, ...]]:
    """Extract one bounded document and its section structure."""
    if not isinstance(frontmatter, Frontmatter):
        diagnostic = _diagnostic(
            path, "frontmatter-boundary", "frontmatter is required before Markdown parsing",
            class_name="host-input",
        )
        return None, (diagnostic,)
    scanned, scan_diagnostics = _scan(path, lines, body_start)
    if scanned is None:
        return None, scan_diagnostics
    sections, structure_diagnostics, h1_title = _section_structure(
        path, locale, frontmatter.kind, scanned
    )
    purpose: str | None = None
    outcomes: tuple[OutcomeIR, ...] = ()
    activities: tuple[ActivityIR, ...] = ()
    processes: tuple[ProcessEntryIR, ...] = ()
    relationships: tuple[RelationshipIR, ...] = ()
    source_processes: tuple[SourceProcessIR, ...] = ()
    included_activities_tasks: tuple[IncludedActivityTaskIR, ...] = ()
    application: tuple[ApplicationIR, ...] = ()
    references: tuple[Reference, ...] = ()
    extraction_diagnostics: tuple[Diagnostic, ...] = ()
    if frontmatter.kind in _SECTION_ORDER:
        blocks = _section_blocks(locale, frontmatter.kind, scanned, h1_title)
        if frontmatter.kind == "process":
            (
                purpose,
                outcomes,
                activities,
                references,
                sections,
                extraction_diagnostics,
            ) = _extract_process(path, locale, blocks, sections)
        elif frontmatter.kind == "process-model":
            (
                purpose,
                processes,
                relationships,
                references,
                sections,
                extraction_diagnostics,
            ) = _extract_process_model(path, locale, blocks, sections)
        elif frontmatter.kind == "process-reference-model":
            (
                purpose,
                processes,
                relationships,
                references,
                sections,
                extraction_diagnostics,
            ) = _extract_reference_model(path, locale, blocks, sections)
        elif frontmatter.kind == "process-view":
            (
                purpose,
                outcomes,
                application,
                source_processes,
                included_activities_tasks,
                references,
                sections,
                extraction_diagnostics,
            ) = _extract_process_view(path, locale, blocks, sections)
    document = _make_document_ir(
        path,
        locale,
        frontmatter,
        sections,
        h1_title,
        purpose=purpose,
        outcomes=outcomes,
        activities=activities,
        processes=processes,
        relationships=relationships,
        source_processes=source_processes,
        included_activities_tasks=included_activities_tasks,
        application=application,
        references=references,
    )
    return document, deterministic_diagnostics(
        scan_diagnostics + structure_diagnostics + extraction_diagnostics
    )
