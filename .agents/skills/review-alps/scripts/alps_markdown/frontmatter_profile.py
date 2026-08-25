"""Exact section-4 frontmatter parser for the ALPS checker profile."""

from __future__ import annotations

import re

from .model import (
    MAX_FRONTMATTER_BYTES,
    SUPPORTED_KINDS,
    Diagnostic,
    Frontmatter,
    FrontmatterParseResult,
    InputResult,
    Severity,
    Span,
    deterministic_diagnostics,
)


NAME_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
TOP_LEVEL_KEYS = ("name", "description", "metadata")
CHILD_PREFIX = "  alps.kind:"


def _diagnostic(
    path: str,
    class_name: str,
    code: str,
    message: str,
    line: int | None = None,
) -> Diagnostic:
    return Diagnostic(class_name, code, Severity.ERROR, path, line, message)


def _line_end(text: str, start: int) -> tuple[int, bool]:
    end = text.find("\n", start)
    return (len(text), False) if end < 0 else (end, True)


def _scalar_issue(value: str) -> str | None:
    if not value:
        return "empty scalar value"
    if value != value.strip():
        return "scalar has leading or trailing whitespace"
    if "#" in value:
        return "inline comments are not profile syntax"
    if any(char in value for char in "{}[]"):
        return "flow mappings and sequences are not profile syntax"
    if value.startswith(("|", ">")):
        return "block scalars are not profile syntax"
    if value.startswith(("'", '"')):
        return "quoted scalars are not profile syntax"
    if value.startswith(("*", "&", "!")) or re.search(r"(^|\s)[*&!]", value):
        return "aliases, anchors, and tags are not profile syntax"
    if value == "<<" or value.startswith("<< "):
        return "merge keys are not profile syntax"
    if value == "-" or value.startswith("- "):
        return "sequences are not profile syntax"
    if ": " in value:
        return "additional mapping separators are not profile syntax"
    return None


def _unknown_line_message(line: str) -> str:
    if line.startswith("<<:"):
        return "merge keys are not profile syntax"
    if line.startswith(("-", "'", '"')):
        return "sequences and quoted keys are not profile syntax"
    match = re.match(r"([^:]+):", line)
    if match:
        return f"unknown frontmatter key {match.group(1)!r}"
    return "frontmatter line is outside the profile"


def _result(
    frontmatter: Frontmatter | None,
    body_start: int,
    diagnostics: list[Diagnostic],
) -> FrontmatterParseResult:
    return FrontmatterParseResult(
        frontmatter,
        body_start,
        deterministic_diagnostics(diagnostics),
    )


def parse_frontmatter(
    source: str | InputResult,
    path: str = "<input>",
) -> FrontmatterParseResult:
    """Parse normalized input and return a zero-based body line index."""
    inherited: list[Diagnostic] = []
    if isinstance(source, InputResult):
        path = source.path
        inherited.extend(source.diagnostics)
        text = source.text
        if text is None or any(item.severity == Severity.ERROR for item in inherited):
            return _result(None, 0, inherited)
    elif isinstance(source, str):
        text = source
    else:
        raise TypeError("frontmatter parser requires normalized text or InputResult")

    diagnostics = inherited
    opening_end, opening_newline = _line_end(text, 0)
    if opening_end > MAX_FRONTMATTER_BYTES:
        diagnostics.append(
            _diagnostic(
                path,
                "profile-structure",
                "frontmatter-too-large",
                f"frontmatter exceeds {MAX_FRONTMATTER_BYTES} bytes",
                1,
            )
        )
        return _result(None, 0, diagnostics)
    opening = text[:opening_end]
    if opening != "---":
        diagnostics.append(
            _diagnostic(
                path,
                "profile-structure",
                "frontmatter-opening",
                "frontmatter must begin with exactly --- on line 1",
                1,
            )
        )
        return _result(None, 0, diagnostics)

    size = len(opening.encode("utf-8")) + int(opening_newline)
    cursor = opening_end + 1 if opening_newline else len(text)
    line_number = 2
    closed = False
    body_start = 0
    top_seen: list[str] = []
    values: dict[str, tuple[str, int, Span]] = {}
    metadata_seen = False
    metadata_child_seen = False
    metadata_line: int | None = None
    metadata_span: Span | None = None

    while cursor < len(text):
        end, has_newline = _line_end(text, cursor)
        if end - cursor > MAX_FRONTMATTER_BYTES:
            diagnostics.append(
                _diagnostic(
                    path,
                    "profile-structure",
                    "frontmatter-too-large",
                    f"frontmatter exceeds {MAX_FRONTMATTER_BYTES} bytes",
                    line_number,
                )
            )
            return _result(None, 0, diagnostics)
        line = text[cursor:end]
        size += len(line.encode("utf-8")) + int(has_newline)
        if size > MAX_FRONTMATTER_BYTES:
            diagnostics.append(
                _diagnostic(
                    path,
                    "profile-structure",
                    "frontmatter-too-large",
                    f"frontmatter exceeds {MAX_FRONTMATTER_BYTES} bytes",
                    line_number,
                )
            )
            return _result(None, 0, diagnostics)
        if line == "---":
            closed = True
            body_start = line_number
            break
        if "\t" in line:
            diagnostics.append(
                _diagnostic(
                    path,
                    "unsupported-profile-syntax",
                    "tab-indentation",
                    "tabs are not profile indentation syntax",
                    line_number,
                )
            )
        elif line.startswith("  "):
            if not metadata_seen:
                diagnostics.append(
                    _diagnostic(
                        path,
                        "unsupported-profile-syntax",
                        "orphan-child",
                        "indented content is only allowed under metadata",
                        line_number,
                    )
                )
            elif line.startswith(CHILD_PREFIX):
                suffix = line[len(CHILD_PREFIX) :]
                if not suffix.startswith(" "):
                    diagnostics.append(
                        _diagnostic(
                            path,
                            "profile-structure",
                            "field-separator",
                            "alps.kind requires one colon followed by one space",
                            line_number,
                        )
                    )
                elif metadata_child_seen:
                    diagnostics.append(
                        _diagnostic(
                            path,
                            "unsupported-profile-syntax",
                            "duplicate-key",
                            "metadata.alps.kind is duplicated",
                            line_number,
                        )
                    )
                else:
                    metadata_child_seen = True
                    value = suffix[1:]
                    issue = _scalar_issue(value)
                    if issue:
                        diagnostics.append(
                            _diagnostic(
                                path,
                                "unsupported-profile-syntax",
                                "unsupported-scalar",
                                issue,
                                line_number,
                            )
                        )
                    else:
                        start = cursor + len(CHILD_PREFIX) + 1
                        values["kind"] = (
                            value,
                            line_number,
                            Span(
                                start,
                                start + len(value),
                                line_number,
                                len(CHILD_PREFIX) + 1,
                            ),
                        )
            else:
                diagnostics.append(
                    _diagnostic(
                        path,
                        "unsupported-profile-syntax",
                        "unknown-metadata-child",
                        "unknown metadata child or indentation",
                        line_number,
                    )
                )
        elif line.startswith(" "):
            diagnostics.append(
                _diagnostic(
                    path,
                    "unsupported-profile-syntax",
                    "continuation-line",
                    "continuation lines are not profile syntax",
                    line_number,
                )
            )
        else:
            key = next((item for item in TOP_LEVEL_KEYS if line.startswith(item + ":")), None)
            if key is None:
                diagnostics.append(
                    _diagnostic(
                        path,
                        "unsupported-profile-syntax",
                        "unknown-key",
                        _unknown_line_message(line),
                        line_number,
                    )
                )
            else:
                suffix = line[len(key) + 1 :]
                already_seen = key in top_seen
                if already_seen:
                    diagnostics.append(
                        _diagnostic(
                            path,
                            "unsupported-profile-syntax",
                            "duplicate-key",
                            f"frontmatter key {key} is duplicated",
                            line_number,
                        )
                    )
                elif top_seen and TOP_LEVEL_KEYS.index(key) < max(
                    TOP_LEVEL_KEYS.index(item) for item in top_seen
                ):
                    diagnostics.append(
                        _diagnostic(
                            path,
                            "profile-structure",
                            "field-order",
                            "frontmatter keys must be ordered name, description, metadata",
                            line_number,
                        )
                    )
                    top_seen.append(key)
                else:
                    top_seen.append(key)
                if key == "metadata" and suffix == "":
                    metadata_seen = True
                    if metadata_line is None:
                        metadata_line = line_number
                        metadata_span = Span(
                            cursor,
                            cursor + len(key),
                            line_number,
                            0,
                        )
                elif suffix == "":
                    diagnostics.append(
                        _diagnostic(
                            path,
                            "unsupported-profile-syntax",
                            "empty-value",
                            f"frontmatter key {key} has an empty value",
                            line_number,
                        )
                    )
                elif not suffix.startswith(" "):
                    diagnostics.append(
                        _diagnostic(
                            path,
                            "profile-structure",
                            "field-separator",
                            f"{key} requires one colon followed by one space",
                            line_number,
                        )
                    )
                elif key == "metadata":
                    diagnostics.append(
                        _diagnostic(
                            path,
                            "unsupported-profile-syntax",
                            "metadata-form",
                            "metadata must be an exact non-empty mapping",
                            line_number,
                        )
                    )
                else:
                    value = suffix[1:]
                    issue = _scalar_issue(value)
                    if issue:
                        diagnostics.append(
                            _diagnostic(
                                path,
                                "unsupported-profile-syntax",
                                "unsupported-scalar",
                                issue,
                                line_number,
                            )
                        )
                    elif key not in values:
                        start = cursor + len(key) + 2
                        values[key] = (
                            value,
                            line_number,
                            Span(
                                start,
                                start + len(value),
                                line_number,
                                len(key) + 2,
                            ),
                        )
        if not has_newline:
            break
        cursor = end + 1
        line_number += 1

    if not closed:
        diagnostics.append(
            _diagnostic(
                path,
                "profile-structure",
                "frontmatter-closing",
                "frontmatter must close with a line containing exactly ---",
                line_number,
            )
        )
        return _result(None, 0, diagnostics)
    if metadata_seen and not metadata_child_seen:
        diagnostics.append(
            _diagnostic(
                path,
                "unsupported-profile-syntax",
                "empty-metadata",
                "metadata must contain exactly the alps.kind child",
                metadata_line,
            )
        )
    for required in ("name", "description"):
        if required not in values:
            diagnostics.append(
                _diagnostic(
                    path,
                    "profile-structure",
                    "missing-field",
                    f"frontmatter is missing {required}",
                )
            )

    name_record = values.get("name")
    description_record = values.get("description")
    kind_record = values.get("kind")
    if name_record:
        name, name_line, name_span = name_record
        if len(name) > 63:
            diagnostics.append(
                _diagnostic(path, "profile-structure", "name-length", "name exceeds 63 characters", name_line)
            )
        if not NAME_PATTERN.fullmatch(name):
            diagnostics.append(
                _diagnostic(path, "profile-structure", "name-format", "name is not lowercase-hyphen form", name_line)
            )
    if description_record:
        description, description_line, description_span = description_record
    else:
        description = ""
        description_line = None
        description_span = None
    kind = kind_record[0] if kind_record else "process"
    if kind not in SUPPORTED_KINDS:
        diagnostics.append(
            _diagnostic(path, "profile-structure", "kind-value", "metadata.alps.kind is unsupported", kind_record[1] if kind_record else None)
        )
    if kind == "process" and description and not (
        description.endswith("ALPS-conformant.") or description.endswith("ALPS準拠。")
    ):
        diagnostics.append(
            _diagnostic(path, "profile-structure", "description-suffix", "Process description must end in ALPS-conformant. or ALPS準拠。", description_line)
        )
    if not name_record or not description_record:
        return _result(None, body_start, diagnostics)
    frontmatter = Frontmatter(
        name=name_record[0],
        description=description_record[0],
        kind=kind,
        metadata={"alps.kind": kind_record[0]} if kind_record else {},
        name_line=name_record[1],
        name_span=name_record[2],
        description_line=description_record[1],
        description_span=description_record[2],
        kind_line=kind_record[1] if kind_record else None,
        kind_span=kind_record[2] if kind_record else None,
        metadata_line=metadata_line,
        metadata_span=metadata_span,
    )
    return _result(frontmatter, body_start, diagnostics)
