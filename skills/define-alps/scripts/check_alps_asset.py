#!/usr/bin/env python3
"""Preflight Markdown Agent Skill representations of ALPS assets.

This checker validates mechanically observable structure and selected semantic
invariants.  It supports Process, Process Model, Process Reference Model, and
Process View representations, including paired English/Japanese assets.  A
successful run is not by itself an ALPS conformance determination.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable
from urllib.parse import unquote, urlsplit


SUPPORTED_KINDS = {
    "process",
    "process-model",
    "process-reference-model",
    "process-view",
}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILL_REF = re.compile(r"skill:(?P<package>[^#\s]*)#(?P<skill>[a-z0-9][a-z0-9-]*)")
SKILL_TOKEN = re.compile(r'''skill:[^\s`<>()\[\]{}"',;!?。、，；：！？）」』】〉》]*''')
RECORD_CENTRIC = {
    "en": re.compile(r"\b(?:is|are|was|were)\s+(?:only\s+)?(?:recorded|documented)\b", re.I),
    "ja": re.compile(r"(?:が|は)(?:記録|文書化)されている"),
}
INPUT_CONTROL = {
    "en": re.compile(r"\bapplicable Controls?\b", re.I),
    "ja": re.compile(r"適用(?:される)?(?:統制事項|Control)"),
}
HEADINGS = {
    "en": {
        "purpose": "Purpose",
        "outcomes": "Outcomes",
        "activities": "Activities & Tasks",
        "inputs": "Inputs",
        "processes": "Processes",
        "relationships": "Relationships",
        "sources": "Source Processes",
        "included": "Included Activities and Tasks",
        "application": "Application",
    },
    "ja": {
        "purpose": "目的",
        "outcomes": "成果",
        "activities": "活動とタスク",
        "inputs": "入力",
        "processes": "プロセス",
        "relationships": "関係",
        "sources": "出典プロセス",
        "included": "含まれる活動およびタスク",
        "application": "適用",
    },
}
NORMATIVE_PATTERNS = {
    "en": (
        ("must_not", re.compile(r"\bmust not\b", re.I)),
        ("must", re.compile(r"\bmust\b", re.I)),
        ("should_not", re.compile(r"\bshould not\b", re.I)),
        ("should", re.compile(r"\bshould\b", re.I)),
        ("may", re.compile(r"\bmay\b", re.I)),
        ("typically", re.compile(r"\btypically\b", re.I)),
    ),
    "ja": (
        ("must_not", re.compile(r"てはならない|ではならない|禁止される")),
        ("should_not", re.compile(r"(?:の|こと)が望ましくない|避けるのが望ましい")),
        ("must", re.compile(r"必要がある|なければならない")),
        ("should", re.compile(r"(?:の|こと)が望ましい")),
        ("may", re.compile(r"(?:て|で)(?:も)?よい")),
        ("typically", re.compile(r"通常|典型的")),
    ),
}
RAW_ENGLISH = re.compile(r"(?<![A-Za-z])[A-Za-z][A-Za-z-]{1,}(?![A-Za-z])")
DEFAULT_JA_TERMS = {
    "ALPS",
    "AI",
    "AI-DDLC",
    "Define ALPS",
    "Apply ALPS",
    "Manage ALPS",
}
DISCOVERY_SUFFIX = {
    "en": "ALPS-conformant.",
    "ja": "ALPS準拠。",
}


@dataclass(frozen=True)
class ResolvedSkill:
    reference: str
    root: Path
    path: Path


@dataclass(frozen=True)
class ProcessStructure:
    outcomes: tuple[str, ...]
    activities: tuple[str, ...]
    tasks: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class YAMLScalarNode:
    value: str
    line: int


@dataclass(frozen=True)
class YAMLAliasNode:
    name: str
    line: int


@dataclass(frozen=True)
class YAMLMappingNode:
    items: dict[str, "YAMLNode"]
    line: int


@dataclass(frozen=True)
class YAMLNullNode:
    line: int


YAMLNode = YAMLScalarNode | YAMLAliasNode | YAMLMappingNode | YAMLNullNode
YAMLResolved = str | dict[str, "YAMLResolved"] | None
YAML_MAX_DEPTH = 32
YAML_MAX_NODES = 512


def locale_for(path: Path) -> str:
    parts = path.as_posix().split("/")
    for index in range(len(parts) - 2):
        if parts[index : index + 3] == ["references", "locales", "ja"]:
            return "ja"
    return "en"


YAML_DOUBLE_ESCAPES = {
    "0": "\0",
    "a": "\a",
    "b": "\b",
    "t": "\t",
    "n": "\n",
    "v": "\v",
    "f": "\f",
    "r": "\r",
    "e": "\x1b",
    " ": " ",
    '"': '"',
    "/": "/",
    "\\": "\\",
    "N": "\x85",
    "_": "\xa0",
    "L": "\u2028",
    "P": "\u2029",
}


def yaml_decode_quoted_scalar(
    value: str,
) -> tuple[str, int | None, str | None]:
    """Decode one bounded YAML quoted scalar and return its closing index."""
    if not value.startswith(("'", '"')):
        return value, None, None
    quote = value[0]
    decoded: list[str] = []
    cursor = 1
    while cursor < len(value):
        character = value[cursor]
        if character == quote:
            if quote == "'" and cursor + 1 < len(value) and value[cursor + 1] == quote:
                decoded.append("'")
                cursor += 2
                continue
            return "".join(decoded), cursor, None
        if quote == '"' and character == "\\":
            if cursor + 1 >= len(value):
                return "", None, "unbalanced quoted scalar"
            escaped = value[cursor + 1]
            if escaped in "\r\n":
                cursor += 2
                if escaped == "\r" and cursor < len(value) and value[cursor] == "\n":
                    cursor += 1
                while cursor < len(value) and value[cursor] in " \t":
                    cursor += 1
                continue
            if escaped in YAML_DOUBLE_ESCAPES:
                decoded.append(YAML_DOUBLE_ESCAPES[escaped])
                cursor += 2
                continue
            if escaped in "xuU":
                width = {"x": 2, "u": 4, "U": 8}[escaped]
                digits = value[cursor + 2 : cursor + 2 + width]
                if len(digits) != width or not re.fullmatch(r"[0-9A-Fa-f]+", digits):
                    return "", None, "invalid YAML double-quoted escape"
                codepoint = int(digits, 16)
                if codepoint > 0x10FFFF or 0xD800 <= codepoint <= 0xDFFF:
                    return "", None, "invalid YAML double-quoted codepoint"
                decoded.append(chr(codepoint))
                cursor += 2 + width
                continue
            return "", None, "invalid YAML double-quoted escape"
        if character in "\r\n":
            line_breaks = 0
            while cursor < len(value) and value[cursor] in "\r\n":
                line_breaks += 1
                if value[cursor] == "\r" and cursor + 1 < len(value) and value[cursor + 1] == "\n":
                    cursor += 2
                else:
                    cursor += 1
                while cursor < len(value) and value[cursor] in " \t":
                    cursor += 1
            decoded.append(" " if line_breaks == 1 else "\n" * (line_breaks - 1))
            continue
        decoded.append(character)
        cursor += 1
    return "", None, "unbalanced quoted scalar"


def quoted_scalar_end(value: str) -> int | None:
    if not value.startswith(("'", '"')):
        return None
    quote = value[0]
    cursor = 1
    while cursor < len(value):
        if quote == '"' and value[cursor] == "\\":
            if cursor + 1 < len(value) and value[cursor + 1] in "\r\n":
                cursor += 2
                if value[cursor - 1] == "\r" and cursor < len(value) and value[cursor] == "\n":
                    cursor += 1
                while cursor < len(value) and value[cursor] in " \t":
                    cursor += 1
            else:
                cursor += 2
            continue
        if value[cursor] == quote:
            if quote == "'" and cursor + 1 < len(value) and value[cursor + 1] == quote:
                cursor += 2
                continue
            return cursor
        cursor += 1
    return -1


def backtick_run_length(value: str, start: int) -> int:
    """Return the length of the backtick run beginning at ``start``."""
    length = 1
    while start + length < len(value) and value[start + length] == "`":
        length += 1
    return length


def inline_code_end(text: str, start: int, delimiter_length: int) -> int | None:
    """Find a closing inline-code run whose length exactly matches the opener."""
    cursor = start + delimiter_length
    while cursor < len(text):
        if text[cursor] != "`":
            cursor += 1
            continue
        run = backtick_run_length(text, cursor)
        if run == delimiter_length:
            return cursor
        cursor += run
    return None


def yaml_node_properties(value: str) -> tuple[tuple[str, ...], str]:
    """Return YAML tags/anchors and the value that follows them."""
    value = value.lstrip()
    properties: list[str] = []
    while value:
        if value.startswith("&"):
            match = re.match(r"&[^\s#]+", value)
        elif value.startswith("!<"):
            close = value.find(">", 2)
            match = None if close < 0 else re.match(r"!<[^>]*>", value)
        elif value.startswith("!"):
            match = re.match(r"![^\s#]+", value)
        else:
            break
        if match is None:
            break
        properties.append(match.group(0))
        value = value[match.end() :].lstrip()
    return tuple(properties), value


def strip_yaml_node_properties(value: str) -> str:
    """Remove YAML anchors and tags that precede a scalar value."""
    _, value = yaml_node_properties(value)
    return value


def yaml_quoted_end(value: str, start: int) -> int | None:
    """Return the end after a quoted scalar, honoring YAML quote escapes."""
    end = quoted_scalar_end(value[start:])
    return None if end is None or end < 0 else start + end + 1


def yaml_without_flow_comments(value: str, stop_at_comment: bool = False) -> str:
    """Remove flow comments while preserving quoted content and line state."""
    visible: list[str] = []
    cursor = 0
    while cursor < len(value):
        if value[cursor] in ("'", '"'):
            end = yaml_quoted_end(value, cursor)
            visible.append(value[cursor:] if end is None else value[cursor:end])
            cursor = len(value) if end is None else end
            continue
        if value[cursor] == "#" and (cursor == 0 or value[cursor - 1].isspace()):
            if stop_at_comment:
                break
            while cursor < len(value) and value[cursor] not in "\r\n":
                cursor += 1
            while cursor < len(value) and value[cursor] in "\r\n":
                cursor += 1
            visible.append(" ")
            continue
        visible.append(value[cursor])
        cursor += 1
    return "".join(visible)


def yaml_without_comment(value: str) -> str:
    """Remove an unquoted YAML comment without changing quoted content."""
    return yaml_without_flow_comments(value, stop_at_comment=True).strip()


def yaml_alias_name(value: str) -> str | None:
    """Return a complete YAML alias name, excluding comments."""
    _, value = yaml_node_properties(value.strip())
    value = yaml_without_comment(value)
    match = re.fullmatch(r"\*([^\s#]+)", value)
    return None if match is None else match.group(1)


@dataclass
class YAMLParseState:
    anchors: dict[str, YAMLNode]
    errors: list[tuple[int, str]]
    node_count: int = 0

    def add_error(self, line: int, message: str) -> None:
        item = (line, message)
        if item not in self.errors:
            self.errors.append(item)

    def count_node(self, line: int) -> bool:
        self.node_count += 1
        if self.node_count > YAML_MAX_NODES:
            self.add_error(line, "YAML frontmatter node limit exceeded")
            return False
        return True


def yaml_register_anchors(
    properties: Iterable[str], node: YAMLNode, line: int, state: YAMLParseState
) -> None:
    for property_name in properties:
        if not property_name.startswith("&"):
            continue
        name = property_name[1:]
        if name in state.anchors:
            state.add_error(line, f"duplicate YAML anchor &{name}")
        elif len(state.anchors) >= YAML_MAX_NODES:
            state.add_error(line, "YAML frontmatter anchor limit exceeded")
        else:
            state.anchors[name] = node


def yaml_flow_close(value: str) -> int | None:
    value = yaml_without_flow_comments(value)
    if not value.startswith("{"):
        return None
    depth = 0
    cursor = 0
    while cursor < len(value):
        if value[cursor] in ("'", '"'):
            end = yaml_quoted_end(value, cursor)
            if end is None:
                return None
            cursor = end
            continue
        character = value[cursor]
        if character in "[{":
            depth += 1
        elif character in "]}":
            depth -= 1
            if depth == 0 and character == "}":
                return cursor
            if depth < 0:
                return None
        cursor += 1
    return None


def yaml_flow_parts(value: str) -> list[str] | None:
    value = yaml_without_flow_comments(value)
    close = yaml_flow_close(value)
    if close is None or value[close + 1 :].strip():
        return None
    body = value[1:close]
    parts: list[str] = []
    start = 0
    depth = 0
    cursor = 0
    while cursor < len(body):
        if body[cursor] in ("'", '"'):
            end = yaml_quoted_end(body, cursor)
            if end is None:
                return None
            cursor = end
            continue
        index = cursor
        character = body[cursor]
        if character in "[{":
            depth += 1
        elif character in "]}":
            depth -= 1
        elif character == "," and depth == 0:
            parts.append(body[start:index])
            start = index + 1
        cursor += 1
    parts.append(body[start:])
    return parts


def yaml_collect_flow(lines: list[str], index: int, value: str) -> tuple[str, int]:
    """Collect a possibly multiline flow mapping before parsing its entries."""
    properties, remainder = yaml_node_properties(value.strip())
    if not remainder.startswith("{"):
        return value, index + 1
    parts = [remainder]
    cursor = index + 1
    while yaml_flow_close("\n".join(parts)) is None and cursor < len(lines):
        parts.append(lines[cursor].strip())
        cursor += 1
    return yaml_without_flow_comments("\n".join((*properties, *parts))), cursor


def yaml_collect_quoted(lines: list[str], index: int, value: str) -> tuple[str, int]:
    """Collect a possibly multiline quoted scalar before parsing its value."""
    properties, remainder = yaml_node_properties(value.strip())
    if not remainder.startswith(("'", '"')):
        return value, index + 1
    parts = [remainder]
    cursor = index + 1
    while yaml_quoted_end("\n".join(parts), 0) is None and cursor < len(lines):
        parts.append(lines[cursor].strip())
        cursor += 1
    prefix = " ".join(properties)
    return (f"{prefix} " if prefix else "") + yaml_join_quoted_parts(parts), cursor


def yaml_join_quoted_parts(parts: list[str]) -> str:
    """Fold collected quoted lines while retaining escaped line breaks."""
    if not parts:
        return ""
    result = parts[0]
    for part in parts[1:]:
        trailing = len(result) - len(result.rstrip("\\"))
        result += ("\n" if trailing % 2 else " ") + part
    return result


def yaml_flow_separator(value: str) -> int:
    value = yaml_without_flow_comments(value)
    depth = 0
    cursor = 0
    while cursor < len(value):
        if value[cursor] in ("'", '"'):
            end = yaml_quoted_end(value, cursor)
            if end is None:
                return -1
            cursor = end
            continue
        index = cursor
        character = value[cursor]
        if character in "[{":
            depth += 1
        elif character in "]}":
            depth -= 1
        elif character == ":" and depth == 0:
            return index
        cursor += 1
    return -1


def yaml_scalar_value(
    value: str,
    line: int | None = None,
    state: YAMLParseState | None = None,
) -> str:
    value = yaml_without_comment(value.strip())
    if value.startswith(("'", '"')):
        scalar, _, error = yaml_decode_quoted_scalar(value)
        if error is not None:
            if state is not None and line is not None:
                state.add_error(line, error)
            return ""
        return scalar
    return value


def yaml_mapping_line(
    value: str,
    line: int | None = None,
    state: YAMLParseState | None = None,
) -> tuple[int, str, str] | None:
    """Parse a block mapping line with a scalar or quoted scalar key."""
    indentation = len(value) - len(value.lstrip(" "))
    _, content = yaml_node_properties(value[indentation:])
    if content.startswith(("'", '"')):
        end = quoted_scalar_end(content)
        if end in {None, -1}:
            return None
        separator = re.match(
            r"^[ \t]*:[ \t]*(.*)$", content[end + 1 :], re.S
        )
        if not separator:
            return None
        key = yaml_scalar_value(content[: end + 1], line, state)
        return None if not key else (indentation, key, separator.group(1))
    match = re.fullmatch(
        r"([A-Za-z0-9_.-]+|<<):(?:[ \t]*(.*))?", content, re.S
    )
    if not match:
        return None
    return indentation, match.group(1), match.group(2) or ""


def yaml_inline_node(
    value: str,
    line: int,
    depth: int,
    state: YAMLParseState,
) -> YAMLNode:
    if depth > YAML_MAX_DEPTH:
        state.add_error(line, "YAML frontmatter nesting limit exceeded")
        return YAMLNullNode(line)
    properties, remainder = yaml_node_properties(value)
    remainder = yaml_without_comment(remainder)
    alias = yaml_alias_name(remainder)
    if alias is not None:
        node: YAMLNode = YAMLAliasNode(alias, line)
    elif remainder.startswith("{"):
        node = yaml_flow_mapping(remainder, line, depth + 1, state)
    elif remainder.startswith("["):
        # Sequences are outside the inspected frontmatter subset. Keep their
        # source text so an alias to one is rejected as a non-mapping value.
        node = YAMLScalarNode(remainder, line)
    elif not remainder:
        node = YAMLNullNode(line)
    else:
        node = YAMLScalarNode(yaml_scalar_value(remainder, line, state), line)
    if state.count_node(line):
        yaml_register_anchors(properties, node, line, state)
    return node


def yaml_flow_mapping(
    value: str,
    line: int,
    depth: int,
    state: YAMLParseState,
) -> YAMLMappingNode:
    items: dict[str, YAMLNode] = {}
    parts = yaml_flow_parts(value)
    if parts is None:
        message = (
            "unclosed YAML flow mapping"
            if yaml_flow_close(value) is None
            else "invalid YAML flow mapping"
        )
        state.add_error(line, message)
        return YAMLMappingNode(items, line)
    for part in parts:
        if not part.strip():
            continue
        separator = yaml_flow_separator(part)
        if separator < 0:
            state.add_error(line, "invalid YAML flow mapping entry")
            continue
        key = yaml_scalar_value(part[:separator].strip(), line, state)
        if not key:
            state.add_error(line, "invalid YAML flow mapping key")
            continue
        items[key] = yaml_inline_node(part[separator + 1 :], line, depth, state)
    return YAMLMappingNode(items, line)


def yaml_block_scalar(
    lines: list[str], index: int, base_indent: int, line: int, state: YAMLParseState
) -> tuple[YAMLScalarNode, int]:
    parts: list[str] = []
    cursor = index + 1
    while cursor < len(lines):
        raw = lines[cursor]
        if raw.strip():
            indent = len(raw) - len(raw.lstrip(" "))
            if indent <= base_indent:
                break
            parts.append(raw.strip())
        else:
            parts.append("")
        cursor += 1
    if not state.count_node(line):
        return YAMLScalarNode("", line), cursor
    return YAMLScalarNode(" ".join(part for part in parts if part), line), cursor


def yaml_mapping(
    lines: list[str],
    index: int,
    indent: int,
    depth: int,
    state: YAMLParseState,
) -> tuple[YAMLMappingNode, int]:
    items: dict[str, YAMLNode] = {}
    if depth > YAML_MAX_DEPTH:
        state.add_error(index + 2, "YAML frontmatter nesting limit exceeded")
        return YAMLMappingNode(items, index + 2), index
    if not state.count_node(index + 2):
        return YAMLMappingNode(items, index + 2), index
    cursor = index
    while cursor < len(lines):
        raw = lines[cursor]
        if not raw.strip() or raw.lstrip().startswith("#"):
            cursor += 1
            continue
        current_indent = len(raw) - len(raw.lstrip(" "))
        if current_indent < indent:
            break
        if current_indent > indent:
            break
        mapping = yaml_mapping_line(raw, cursor + 2, state)
        if mapping is None:
            if raw.lstrip().startswith(("'", '"', "?", "[", "{")):
                state.add_error(cursor + 2, "invalid YAML mapping key")
            cursor += 1
            continue
        _, key, raw_value = mapping
        line = cursor + 2
        properties, remainder = yaml_node_properties(raw_value.strip())
        remainder = yaml_without_comment(remainder)
        if re.fullmatch(r"[>|](?:[+-]?[1-9]?|[1-9][+-]?)?", remainder):
            node, cursor = yaml_block_scalar(lines, cursor, indent, line, state)
            yaml_register_anchors(properties, node, line, state)
        elif not remainder:
            child = cursor + 1
            while child < len(lines) and (
                not lines[child].strip() or lines[child].lstrip().startswith("#")
            ):
                child += 1
            if child < len(lines):
                child_indent = len(lines[child]) - len(lines[child].lstrip(" "))
            else:
                child_indent = indent
            if child < len(lines) and child_indent > indent:
                node, cursor = yaml_mapping(lines, child, child_indent, depth + 1, state)
            else:
                node = YAMLNullNode(line)
                state.count_node(line)
                cursor += 1
            yaml_register_anchors(properties, node, line, state)
        else:
            if remainder.startswith(("'", '"')):
                scalar_value, next_cursor = yaml_collect_quoted(lines, cursor, raw_value)
            else:
                scalar_value, next_cursor = yaml_collect_flow(lines, cursor, raw_value)
            node = yaml_inline_node(scalar_value, line, depth, state)
            cursor = next_cursor
        items[key] = node
    return YAMLMappingNode(items, index + 2), cursor


def resolve_yaml_node(
    node: YAMLNode,
    anchors: dict[str, YAMLNode],
    stack: tuple[str, ...],
    depth: int,
    errors: list[tuple[int, str]],
) -> YAMLResolved:
    if depth > YAML_MAX_DEPTH:
        item = (getattr(node, "line", 0), "YAML alias resolution depth exceeded")
        if item not in errors:
            errors.append(item)
        return None
    if isinstance(node, YAMLScalarNode):
        return node.value
    if isinstance(node, YAMLNullNode):
        return None
    if isinstance(node, YAMLAliasNode):
        if node.name not in anchors:
            item = (node.line, f"unresolved YAML alias *{node.name}")
            if item not in errors:
                errors.append(item)
            return None
        if node.name in stack:
            item = (node.line, f"cyclic YAML alias *{node.name}")
            if item not in errors:
                errors.append(item)
            return None
        return resolve_yaml_node(
            anchors[node.name], anchors, (*stack, node.name), depth + 1, errors
        )
    merged: dict[str, YAMLResolved] = {}
    for key, child in node.items.items():
        if key != "<<":
            continue
        merged_value = resolve_yaml_node(
            child, anchors, stack, depth + 1, errors
        )
        if not isinstance(merged_value, dict):
            item = (
                getattr(child, "line", getattr(node, "line", 0)),
                "YAML merge key must resolve to a mapping",
            )
            if item not in errors:
                errors.append(item)
            continue
        for merged_key, merged_child in merged_value.items():
            merged.setdefault(merged_key, merged_child)
    result = dict(merged)
    for key, child in node.items.items():
        if key == "<<":
            continue
        result[key] = resolve_yaml_node(child, anchors, stack, depth + 1, errors)
    return result


def yaml_frontmatter_nodes(
    lines: list[str],
) -> tuple[
    dict[str, YAMLResolved],
    dict[str, YAMLResolved],
    list[tuple[int, str]],
]:
    state = YAMLParseState({}, [])
    root, _ = yaml_mapping(lines, 0, 0, 0, state)
    errors = list(state.errors)
    resolved_root = resolve_yaml_node(root, state.anchors, (), 0, errors)
    resolved_anchors: dict[str, YAMLResolved] = {}
    for name, node in state.anchors.items():
        resolved_anchors[name] = resolve_yaml_node(node, state.anchors, (name,), 0, errors)
    return (
        resolved_root if isinstance(resolved_root, dict) else {},
        resolved_anchors,
        errors,
    )


def yaml_flatten_mapping(value: YAMLResolved, prefix: str = "") -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, str] = {}
    for key, child in value.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(child, str):
            result[full_key] = child
        elif isinstance(child, dict):
            result.update(yaml_flatten_mapping(child, full_key))
    return result


def frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    if not text.startswith("---\n"):
        return {}, ["YAML frontmatter must start on the first line"]
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, ["YAML frontmatter is not closed"]

    lines = text[4:end].splitlines()
    resolved_yaml, resolved_yaml_anchors, yaml_errors = yaml_frontmatter_nodes(lines)
    errors = [f"frontmatter line {line} {message}" for line, message in yaml_errors]
    block_values: dict[int, str] = {}
    for index, raw in enumerate(lines):
        mapping = yaml_mapping_line(raw)
        if not mapping:
            continue
        base_indent, key, raw_value = mapping
        _, style = yaml_node_properties(raw_value.strip())
        style = yaml_without_comment(style)
        if not re.fullmatch(r"[>|](?:[+-]?[1-9]?|[1-9][+-]?)?", style):
            continue
        content: list[str] = []
        for continuation in lines[index + 1 :]:
            if not continuation.strip():
                content.append("")
                continue
            indent = len(continuation) - len(continuation.lstrip(" "))
            if indent <= base_indent:
                break
            content.append(continuation.strip())
        value = " ".join(part for part in content if part)
        block_values[index] = " " * base_indent + key + ": " + value

    quoted_values: dict[int, str] = {}
    quoted_continuations: set[int] = set()
    for index, raw in enumerate(lines):
        mapping = yaml_mapping_line(raw)
        if not mapping:
            continue
        indentation, key, raw_value = mapping
        raw_value = raw_value.strip()
        scalar_value = strip_yaml_node_properties(raw_value)
        if not scalar_value.startswith(("'", '"')) or quoted_scalar_end(scalar_value) != -1:
            continue
        property_prefix = raw_value[: len(raw_value) - len(scalar_value)]
        pieces = [scalar_value]
        last = index
        for continuation_index in range(index + 1, len(lines)):
            pieces.append(lines[continuation_index].strip())
            last = continuation_index
            combined = "\n".join(pieces)
            if quoted_scalar_end(combined) not in {None, -1}:
                break
        quoted_values[index] = (
            " " * indentation + key + ": " + property_prefix + yaml_join_quoted_parts(pieces)
        )
        quoted_continuations.update(range(index + 1, last + 1))

    plain_values: dict[int, str] = {}
    plain_scalar_values: dict[int, str] = {}
    plain_continuations: set[int] = set()
    for index, raw in enumerate(lines):
        mapping = yaml_mapping_line(raw)
        if (
            not mapping
            or mapping[0] != 0
            or mapping[1] != "description"
        ):
            continue
        raw_value = mapping[2].strip()
        _, scalar = yaml_node_properties(raw_value)
        scalar = yaml_without_comment(scalar)
        if (
            not scalar
            or scalar.startswith(("'", '"', "{", "[", "|", ">"))
            or yaml_alias_name(scalar) is not None
        ):
            continue
        base_indent = len(raw) - len(raw.lstrip(" "))
        parts = [scalar]
        consumed: list[int] = []
        pending_blank = False
        for continuation_index in range(index + 1, len(lines)):
            continuation = lines[continuation_index]
            if not continuation.strip():
                pending_blank = True
                continue
            if continuation.lstrip().startswith("#"):
                continue
            continuation_indent = len(continuation) - len(continuation.lstrip(" "))
            if continuation_indent <= base_indent:
                break
            if re.match(r"^\s*[A-Za-z0-9_.-]+:\s*", continuation):
                break
            continuation_value = yaml_without_comment(continuation.strip())
            if not continuation_value:
                continue
            parts.append(("\n" if pending_blank else " ") + continuation_value)
            pending_blank = False
            consumed.append(continuation_index)
        if consumed:
            plain_values[index] = mapping[1] + ": " + scalar
            plain_scalar_values[index] = "".join(parts)
            plain_continuations.update(consumed)

    values: dict[str, str] = {}
    flow_continuations: set[int] = set()
    in_metadata = False
    metadata_child_indent: int | None = None
    for index, original in enumerate(lines):
        if (
            index in quoted_continuations
            or index in plain_continuations
            or index in flow_continuations
        ):
            continue
        number = index + 2
        raw = quoted_values.get(
            index,
            block_values.get(index, plain_values.get(index, original)),
        )
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if re.match(r"^ *\t", raw):
            errors.append(f"frontmatter line {number} uses a tab for indentation")
            continue
        mapping_line = yaml_mapping_line(raw)
        if index not in block_values:
            if mapping_line:
                _, _, raw_value = mapping_line
                _, remainder = yaml_node_properties(raw_value.strip())
                if remainder.startswith("{"):
                    _, last = yaml_collect_flow(lines, index, raw_value)
                    flow_continuations.update(range(index + 1, last))
        metadata_alias = (
            yaml_alias_name(mapping_line[2])
            if mapping_line and mapping_line[1] == "metadata"
            else None
        )
        if metadata_alias is not None:
            resolved = resolved_yaml_anchors.get(metadata_alias)
            alias_error = any(
                line == number and "YAML alias" in message
                for line, message in yaml_errors
            )
            alias_resolution_error = any("YAML alias" in message for _, message in yaml_errors)
            if not alias_error and isinstance(resolved, dict):
                for key, value in yaml_flatten_mapping(resolved).items():
                    values[f"metadata.{key}"] = value
            elif not alias_error and not (resolved is None and alias_resolution_error):
                errors.append(
                    f"frontmatter line {number} YAML alias *{metadata_alias} "
                    "must resolve to a mapping for metadata"
                )
            in_metadata = False
            metadata_child_indent = None
            continue
        # YAML mapping nodes may carry anchors or tags before nested entries.
        metadata_value = (
            yaml_without_comment(strip_yaml_node_properties(mapping_line[2]))
            if mapping_line and mapping_line[1] == "metadata"
            else None
        )
        if metadata_value == "":
            in_metadata = True
            metadata_child_indent = None
            continue
        flow_value = (
            strip_yaml_node_properties(mapping_line[2])
            if mapping_line and mapping_line[1] == "metadata"
            else ""
        )
        if mapping_line and mapping_line[1] == "metadata" and flow_value.startswith("{"):
            resolved_metadata = resolved_yaml.get("metadata")
            flow_error = any(
                line == number and message.startswith("invalid YAML flow mapping")
                for line, message in yaml_errors
            )
            if flow_error or not isinstance(resolved_metadata, dict):
                errors.append(f"frontmatter line {number} has an invalid metadata flow mapping")
            else:
                items = yaml_flatten_mapping(resolved_metadata)
                if "alps.kind" in items:
                    values["metadata.alps.kind"] = items["alps.kind"]
            in_metadata = False
            metadata_child_indent = None
            continue
        if raw and not raw.startswith((" ", "\t")):
            in_metadata = False
            metadata_child_indent = None
        if in_metadata and mapping_line:
            indent, key, value = mapping_line
            if metadata_child_indent is None:
                metadata_child_indent = indent
            match = mapping_line if indent == metadata_child_indent else None
        else:
            match = mapping_line if mapping_line and mapping_line[0] == 0 else None
        if not match:
            # Block scalars and unrelated nested binding metadata are outside
            # the fields inspected here.
            if raw.lstrip().startswith(("- ", "|", ">")) or raw.startswith((" ", "\t")):
                continue
            errors.append(f"frontmatter line {number} is not a key/value")
            continue
        _, key, value = match
        if key == "<<":
            continue
        if not in_metadata and key in {"alps.kind", "metadata.alps.kind"}:
            errors.append(
                f"frontmatter line {number} must declare alps.kind under metadata"
            )
            continue
        if in_metadata:
            key = f"metadata.{key}"
        value = value.strip()
        if index in plain_scalar_values:
            values[key] = plain_scalar_values[index]
            continue
        alias = yaml_alias_name(value)
        if alias is not None and isinstance(resolved_yaml_anchors.get(alias), str):
            value = resolved_yaml_anchors[alias]
        if index not in block_values:
            value = strip_yaml_node_properties(value)
            if value.startswith(("'", '"')):
                cursor = quoted_scalar_end(value)
                if cursor in {None, -1}:
                    errors.append(f"frontmatter line {number} has an unbalanced quoted scalar")
                    continue
                remainder = value[cursor + 1 :].strip()
                if remainder and not remainder.startswith("#"):
                    errors.append(f"frontmatter line {number} has content after a quoted scalar")
                    continue
                value = yaml_scalar_value(value[: cursor + 1], number)
            else:
                value = re.split(r"\s+#", value, maxsplit=1)[0].rstrip()
        values[key] = value
    resolved_metadata = resolved_yaml.get("metadata")
    if isinstance(resolved_metadata, dict):
        for key, value in yaml_flatten_mapping(resolved_metadata).items():
            values.setdefault(f"metadata.{key}", value)
    if "metadata.alps.kind" in values:
        values["alps.kind"] = values["metadata.alps.kind"]
    return values, errors


def heading1(text: str) -> str | None:
    text = without_html_comments(without_fenced_code(text))
    match = re.search(r"(?m)^# ([^\n]+?)\s*$", text)
    return match.group(1).strip() if match else None


def section(
    text: str,
    heading: str,
    level: int = 2,
    stop_at_any_heading: bool = False,
) -> str | None:
    text = without_html_comments(without_fenced_code(text))
    marker = "#" * level + " " + heading
    boundary = r"^#{1,6}\s" if stop_at_any_heading else rf"^#{{1,{level}}}\s"
    pattern = re.compile(rf"(?ms)^{re.escape(marker)}\s*$\n(.*?)(?={boundary}|\Z)")
    match = pattern.search(text)
    return match.group(1).strip() if match else None


def normalized_lines(value: str) -> list[str]:
    return [re.sub(r"\s+", " ", line.strip()) for line in value.splitlines() if line.strip()]


def prose_paragraphs(value: str) -> list[str]:
    return [re.sub(r"\s+", " ", block.strip()) for block in re.split(r"\n\s*\n", value) if block.strip()]


def table_row_cells(line: str) -> list[str]:
    """Split a Markdown table row without changing cell text.

    A pipe is a delimiter only when it is outside an inline code span and is
    preceded by an even number of backslashes.  Inline code closes only on a
    backtick run whose length exactly matches the opening run.  The optional
    leading and trailing table delimiters are removed after tokenization so an
    escaped edge pipe remains part of its cell.
    """

    line = line.strip()
    cells: list[str] = []
    start = 0
    code_run: int | None = None
    index = 0
    separators: list[int] = []
    while index < len(line):
        if line[index] == "`":
            run = backtick_run_length(line, index)
            if code_run is None:
                code_run = run
            elif run == code_run:
                code_run = None
            index += run
            continue
        if line[index] == "|" and code_run is None:
            backslashes = 0
            cursor = index - 1
            while cursor >= 0 and line[cursor] == "\\":
                backslashes += 1
                cursor -= 1
            if backslashes % 2 == 0:
                separators.append(index)
                cells.append(line[start:index].strip())
                start = index + 1
        index += 1
    cells.append(line[start:].strip())
    if separators and separators[0] == 0:
        cells = cells[1:]
    if separators and separators[-1] == len(line) - 1:
        cells = cells[:-1]
    return cells


def markdown_tables(text: str) -> list[tuple[list[str], list[list[str]]]]:
    """Return every Markdown table block in document order."""
    lines = text.splitlines()
    tables: list[tuple[list[str], list[list[str]]]] = []
    index = 1
    while index < len(lines):
        if not lines[index].strip() or "|" not in lines[index]:
            index += 1
            continue
        separators = table_row_cells(lines[index])
        if not separators or not all(
            re.fullmatch(r":?-{3,}:?", cell) for cell in separators
        ):
            index += 1
            continue
        if not lines[index - 1].strip() or "|" not in lines[index - 1]:
            index += 1
            continue
        header = table_row_cells(lines[index - 1])
        column_count = len(separators)
        if len(header) != column_count:
            index += 1
            continue
        rows: list[list[str]] = []
        cursor = index + 1
        while cursor < len(lines):
            line = lines[cursor]
            if not line.strip() or "|" not in line:
                break
            row = table_row_cells(line)
            if len(row) != column_count:
                break
            rows.append(row)
            cursor += 1
        tables.append((header, rows))
        index = max(cursor, index + 1)
    return tables


def table(text: str) -> tuple[list[str], list[list[str]]]:
    tables = markdown_tables(text)
    if tables:
        return tables[0]
    return [], []


def relationship_table_endpoint_indices(header: list[str]) -> tuple[int, int] | None:
    """Return provider/recipient columns for a supported relationship table."""
    if len(header) >= 3:
        return 0, 2
    if len(header) != 2:
        return None
    normalized = [
        re.sub(r"\s+", " ", without_inline_code(cell)).strip().casefold()
        for cell in header
    ]
    provider = normalized[0] in {
        "provider",
        "provider process",
        "提供側プロセス",
        "提供プロセス",
    }
    recipient = normalized[1] in {
        "recipient",
        "recipient process",
        "受領側プロセス",
        "受領プロセス",
    }
    return (0, 1) if provider and recipient else None


def relationship_table_errors(path: Path, value: str) -> list[str]:
    """Reject a two-column table unless its columns identify both endpoints."""
    errors: list[str] = []
    for header, rows in markdown_tables(value):
        if rows and len(header) == 2 and relationship_table_endpoint_indices(header) is None:
            errors.append(
                f"{path}: two-column relationship table must identify Provider and Recipient Processes"
            )
    return errors


def outcome_items(value: str | None) -> list[str]:
    """Return semantic Outcome units without prescribing Markdown markers."""

    if not value or not value.strip():
        return []
    marked = [
        re.sub(r"\s+", " ", item.group("item")).strip()
        for item in re.finditer(
            r"(?ms)^(?P<indent>[ \t]{0,3})(?:[-*+]|\d+[.)]|[a-z][.)])\s+"
            r"(?P<item>.*?)(?=^(?P=indent)(?:[-*+]|\d+[.)]|[a-z][.)])\s+|"
            r"^[ \t]*$\n(?=\S)|\Z)",
            value,
            re.I,
        )
    ]
    if marked:
        values: list[str] = []
        for item in marked:
            item = re.sub(r"^[a-z][.)]\s+", "", item, flags=re.I)
            values.append(item)
        return values
    _, rows = table(value)
    if rows:
        values = []
        for row in rows:
            cells = [re.sub(r"\s+", " ", cell).strip() for cell in row]
            if len(cells) > 1 and re.fullmatch(r"(?:[a-z]|\d+)[.)]?", cells[0], re.I):
                cells = cells[1:]
            values.append(" | ".join(cell for cell in cells if cell))
        return [item for item in values if item]
    return prose_paragraphs(value)


def representation_kind(path: Path) -> str:
    meta, frontmatter_errors = frontmatter(path.read_text(encoding="utf-8"))
    if frontmatter_errors and "alps.kind" not in meta:
        return ""
    return meta.get("alps.kind", "process")


def markdown_container_content(line: str) -> str:
    """Return line content after Markdown blockquote container prefixes."""

    content = line.rstrip("\r\n")
    newline = line[len(content) :]
    cursor = 0
    while True:
        marker = re.match(r" {0,3}>[ \t]?", content[cursor:])
        if marker is None:
            break
        cursor += marker.end()
    return content[cursor:] + newline


def without_fenced_code(text: str) -> str:
    """Replace fenced code with newlines so examples are not operative syntax."""

    visible: list[str] = []
    fence: tuple[str, int] | None = None
    for line in text.splitlines(keepends=True):
        content = markdown_container_content(line)
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", content)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = (token[0], len(token))
            elif (
                token[0] == fence[0]
                and len(token) >= fence[1]
                and not content[marker.end() :].strip()
            ):
                fence = None
            visible.append("\n" if line.endswith("\n") else "")
            continue
        visible.append(line if fence is None else ("\n" if line.endswith("\n") else ""))
    return "".join(visible)


def without_html_comments(text: str) -> str:
    visible: list[str] = []
    index = 0
    while index < len(text):
        if text[index] == "`":
            run = backtick_run_length(text, index)
            end = inline_code_end(text, index, run)
            if end is None:
                visible.append(text[index:])
                break
            visible.append(text[index : end + run])
            index = end + run
            continue
        if text.startswith("<!--", index):
            end = text.find("-->", index + 4)
            stop = len(text) if end < 0 else end + 3
            visible.append("\n" * text[index:stop].count("\n"))
            index = stop
            continue
        visible.append(text[index])
        index += 1
    return "".join(visible)


def without_inline_code(text: str) -> str:
    result: list[str] = []
    index = 0
    while index < len(text):
        if text[index] != "`":
            result.append(text[index])
            index += 1
            continue
        run = backtick_run_length(text, index)
        end = inline_code_end(text, index, run)
        if end is None:
            result.append(text[index:])
            break
        result.append(" " * (end + run - index))
        index = end + run
    return "".join(result)


def mask_inline_code_for_reference_scan(text: str) -> str:
    """Mask non-reference inline code before HTML comments are removed."""

    result: list[str] = []
    index = 0
    while index < len(text):
        if text[index] != "`":
            result.append(text[index])
            index += 1
            continue
        run = backtick_run_length(text, index)
        end = inline_code_end(text, index, run)
        if end is None:
            token = text[index:]
            result.append("".join("\n" if char == "\n" else " " for char in token))
            break
        token = text[index : end + run]
        content = text[index + run : end].strip()
        if SKILL_REF.fullmatch(content):
            result.append(content)
        else:
            result.append("".join("\n" if char == "\n" else " " for char in token))
        index = end + run
    return "".join(result)


def without_indented_code(text: str) -> str:
    """Mask Markdown indented code while retaining ordinary list continuations."""

    visible: list[str] = []
    in_code = False
    previous_paragraph = False
    list_content_indent: int | None = None
    for line in text.splitlines(keepends=True):
        content_line = markdown_container_content(line)
        content = content_line.rstrip("\r\n")
        newline = line[len(line.rstrip("\r\n")) :]
        if not content.strip():
            visible.append(newline)
            previous_paragraph = False
            continue
        expanded = content.expandtabs(4)
        indent = len(expanded) - len(expanded.lstrip(" "))
        list_item = re.match(r"^( {0,3})(?:[-*+]|\d+[.)])\s+", expanded)
        if list_item:
            marker = re.match(r"^ {0,3}(?:[-*+]|\d+[.)])\s+", expanded)
            assert marker is not None
            list_content_indent = marker.end()
            in_code = False
            visible.append(line)
            previous_paragraph = True
            continue
        if list_content_indent is not None and indent < list_content_indent:
            list_content_indent = None
        code_indent = (list_content_indent + 4) if list_content_indent is not None else 4
        if indent >= code_indent and (in_code or not previous_paragraph):
            visible.append(newline)
            in_code = True
            previous_paragraph = False
            continue
        in_code = False
        visible.append(line)
        stripped = expanded.lstrip()
        previous_paragraph = not re.match(
            r"(?:#{1,6}\s|>|```|~~~|(?:[-*_]\s*){3,}$)", stripped
        )
    return "".join(visible)


def reference_scan_text(text: str) -> str:
    """Keep prose and exact inline canonical references, excluding code examples."""

    value = without_fenced_code(text)
    value = without_indented_code(value)
    value = mask_inline_code_for_reference_scan(value)
    value = without_html_comments(value)
    for start, end in reversed(markdown_link_target_spans(value)):
        value = value[:start] + " " * (end - start) + value[end:]
    value = re.sub(r"\b(?:https?|ftp)://[^\s<]+", "", value)
    return value


def reference_tokens(text: str) -> list[str]:
    return [
        match.group(0).rstrip(".:")
        for match in SKILL_TOKEN.finditer(reference_scan_text(text))
    ]


def references(text: str) -> list[str]:
    return [token for token in reference_tokens(text) if SKILL_REF.fullmatch(token)]


def normalized_references(text: str, current_package_id: str | None) -> tuple[tuple[str, str], ...]:
    result: list[tuple[str, str]] = []
    for reference in references(text):
        match = SKILL_REF.fullmatch(reference)
        assert match is not None
        package = match.group("package") or current_package_id or ""
        result.append((package, match.group("skill")))
    return tuple(result)


def reference_syntax_errors(path: Path, text: str) -> list[str]:
    return [
        f"{path}: invalid canonical Skill reference: {token}"
        for token in reference_tokens(text)
        if not SKILL_REF.fullmatch(token)
    ]


def markdown_link_scan_text(text: str) -> str:
    """Prepare Markdown text before locating link destinations."""

    return without_html_comments(
        without_inline_code(without_indented_code(without_fenced_code(text)))
    )


def markdown_link_target_spans(value: str) -> list[tuple[int, int]]:
    """Return source spans for inline and reference-definition destinations."""

    spans: list[tuple[int, int]] = []
    index = 0
    while index < len(value):
        if value[index] == "`":
            run = backtick_run_length(value, index)
            end = inline_code_end(value, index, run)
            index = len(value) if end is None else end + run
            continue
        label_start = index + 1 if value.startswith("![", index) else index
        if label_start >= len(value) or value[label_start] != "[":
            index += 1
            continue
        depth = 1
        cursor = label_start + 1
        while cursor < len(value) and depth:
            if value[cursor] == "\\":
                cursor += 2
                continue
            if value[cursor] == "[":
                depth += 1
            elif value[cursor] == "]":
                depth -= 1
            cursor += 1
        if depth or cursor >= len(value) or value[cursor] != "(":
            index = max(index + 1, cursor)
            continue
        cursor += 1
        while cursor < len(value) and value[cursor] in " \t\n":
            cursor += 1
        if cursor < len(value) and value[cursor] == "<":
            start = cursor
            cursor += 1
            while cursor < len(value):
                if value[cursor] == "\\":
                    cursor += 2
                    continue
                if value[cursor] == ">":
                    spans.append((start, cursor + 1))
                    cursor += 1
                    break
                cursor += 1
        else:
            start = cursor
            parentheses = 0
            while cursor < len(value):
                character = value[cursor]
                if character == "\\":
                    cursor += 2
                    continue
                if character == "(":
                    parentheses += 1
                elif character == ")":
                    if parentheses == 0:
                        spans.append((start, cursor))
                        cursor += 1
                        break
                    parentheses -= 1
                elif character in " \t\n" and parentheses == 0:
                    spans.append((start, cursor))
                    break
                cursor += 1
        index = max(index + 1, cursor)

    lines = value.splitlines(keepends=True)
    line_starts: list[int] = []
    offset = 0
    for raw_line in lines:
        line_starts.append(offset)
        offset += len(raw_line)
    for line_index, raw_line in enumerate(lines):
        line = raw_line.rstrip("\r\n")
        line_start = line_starts[line_index]
        label = re.match(r"^ {0,3}\[", line)
        if not label:
            continue
        cursor = label.end()
        while cursor < len(line):
            if line[cursor] == "\\":
                cursor += 2
                continue
            if line[cursor] == "]":
                break
            cursor += 1
        if cursor >= len(line) or not line.startswith("]:", cursor):
            continue
        cursor += 2
        while cursor < len(line) and line[cursor] in " \t":
            cursor += 1
        if cursor >= len(line):
            if line_index + 1 >= len(lines) or not re.match(r"^[ \t]+\S", lines[line_index + 1]):
                continue
            line_start = line_starts[line_index + 1]
            line = lines[line_index + 1].rstrip("\r\n")
            cursor = len(line) - len(line.lstrip(" \t"))
        if line[cursor] == "<":
            end = cursor + 1
            while end < len(line):
                if line[end] == "\\":
                    end += 2
                    continue
                if line[end] == ">":
                    spans.append((line_start + cursor, line_start + end + 1))
                    break
                end += 1
        else:
            end = cursor
            while end < len(line) and not line[end].isspace():
                if line[end] == "\\" and end + 1 < len(line):
                    end += 2
                else:
                    end += 1
            spans.append((line_start + cursor, line_start + end))
    return spans


def markdown_link_targets(text: str) -> list[str]:
    """Return inline and reference-definition Markdown link destinations."""

    value = markdown_link_scan_text(text)
    return [value[start:end] for start, end in markdown_link_target_spans(value)]


def containing_package_root(path: Path, roots: dict[str, Path]) -> Path | None:
    """Return the most specific declared package root containing path."""

    resolved_path = path.resolve()
    candidates = {
        root.resolve()
        for root in roots.values()
        if resolved_path.is_relative_to(root.resolve())
    }
    return max(candidates, key=lambda root: len(root.parts)) if candidates else None


def containing_package_identity(
    path: Path, roots: dict[str, Path], configured_identity: str | None
) -> str | None:
    """Return the identity of the most specific package containing path."""

    package_root = containing_package_root(path, roots)
    if package_root is None:
        return configured_identity
    if (
        configured_identity
        and configured_identity in roots
        and roots[configured_identity].resolve() == package_root
    ):
        return configured_identity
    aliases = sorted(
        identity
        for identity, root in roots.items()
        if identity and root.resolve() == package_root
    )
    return aliases[0] if len(aliases) == 1 else configured_identity


def local_link_errors(path: Path, text: str, package_root: Path) -> list[str]:
    """Report local Markdown links that escape the package or do not resolve."""

    errors: list[str] = []
    seen: set[str] = set()
    for raw_target in markdown_link_targets(text):
        target = raw_target.strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1].strip()
        else:
            target = target.split(maxsplit=1)[0]
        if not target or target.startswith(("#", "//")):
            continue
        if target.startswith("/"):
            errors.append(f"{path}: root-relative Markdown reference is not allowed: {target}")
            continue
        if re.match(r"^[A-Za-z]:[\\/]", target):
            errors.append(f"{path}: absolute Markdown reference is not allowed: {target}")
            continue
        parsed = urlsplit(target)
        if parsed.scheme == "file":
            errors.append(f"{path}: file-scheme Markdown reference is not allowed: {target}")
            continue
        if parsed.scheme:
            continue
        local_target = unquote(parsed.path)
        if not local_target or local_target in seen:
            continue
        seen.add(local_target)
        destination = (path.parent / local_target).resolve()
        if not destination.is_relative_to(package_root.resolve()):
            errors.append(f"{path}: local Markdown reference escapes package root: {target}")
        elif not destination.exists():
            errors.append(f"{path}: unresolved local Markdown reference: {target}")
    return errors


def package_roots(values: list[str], current_root: Path, package_id: str | None) -> dict[str, Path]:
    roots: dict[str, Path] = {"": current_root}
    if package_id:
        roots[package_id] = current_root
    for value in values:
        if "=" not in value:
            raise ValueError(f"invalid --package-root {value!r}; expected PACKAGE=PATH")
        package, raw_path = value.split("=", 1)
        if not package:
            raise ValueError("--package-root requires a non-empty package identity")
        roots[package] = Path(raw_path).resolve()
    return roots


def resolve_skill(
    reference: str,
    roots: dict[str, Path],
    locale: str = "en",
    current_package_id: str | None = None,
) -> ResolvedSkill:
    match = SKILL_REF.fullmatch(reference)
    if not match:
        raise ValueError(f"invalid canonical Skill reference: {reference}")
    package = match.group("package") or current_package_id or ""
    if package not in roots:
        raise ValueError(f"unresolved package identity {package!r} in {reference}")
    root = roots[package].resolve()
    path = (root / "skills" / match.group("skill") / "SKILL.md").resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Skill reference escapes package root: {reference}")
    if not path.is_file():
        raise ValueError(f"unresolved Skill reference {reference}: {path} not found")
    if locale == "ja":
        localized = japanese_counterpart(path)
        if localized.is_file():
            path = localized
    return ResolvedSkill(reference, root, path)


def required_sections(path: Path, text: str, kind: str, locale: str, keys: Iterable[str]) -> list[str]:
    errors: list[str] = []
    for key in keys:
        heading = HEADINGS[locale][key]
        value = section(text, heading)
        if value is None:
            errors.append(f"{path}: {kind} requires {heading}")
        elif not value.strip():
            errors.append(f"{path}: {kind} requires non-empty {heading}")
    return errors


def process_core(path: Path) -> tuple[str, str, list[str]]:
    text = path.read_text(encoding="utf-8")
    locale = locale_for(path)
    name = heading1(text)
    purpose = section(text, HEADINGS[locale]["purpose"])
    outcomes = section(text, HEADINGS[locale]["outcomes"])
    if name is None or purpose is None or outcomes is None:
        raise ValueError(f"{path}: Process representation requires Name, Purpose, and Outcomes")
    purpose_value = " ".join(line for line in normalized_lines(purpose) if not line.startswith(">"))
    outcome_values = outcome_items(outcomes)
    if not purpose_value:
        raise ValueError(f"{path}: Process representation requires non-empty Purpose")
    if not outcome_values:
        raise ValueError(f"{path}: Process representation requires at least one Outcome")
    return name, purpose_value, outcome_values


def classify_normative(task: str, locale: str) -> str | None:
    task = without_inline_code(without_html_comments(task))
    matches: list[tuple[int, int, str]] = []
    for priority, (name, pattern) in enumerate(NORMATIVE_PATTERNS[locale]):
        matches.extend((match.start(), -priority, name) for match in pattern.finditer(task))
    if not matches:
        return None
    # A Task can contain conditions or explanatory clauses that use another
    # normative word.  The final explicit marker normally governs the action
    # asserted by the Task; priority disambiguates overlapping negative forms.
    return max(matches)[2]


def parse_process_structure(text: str, locale: str) -> ProcessStructure:
    outcomes = tuple(outcome_items(section(text, HEADINGS[locale]["outcomes"])))
    activity_text = section(text, HEADINGS[locale]["activities"]) or ""
    heading_matches = list(re.finditer(r"(?m)^(#{3,6}) ([^\n]+?)\s*$", activity_text))
    activity_level = min(
        (len(match.group(1)) for match in heading_matches),
        default=None,
    )
    matches = [
        match
        for match in heading_matches
        if len(match.group(1)) == activity_level
    ]
    activities: list[str] = []
    tasks: list[tuple[str, ...]] = []
    for index, match in enumerate(matches):
        activities.append(match.group(2).strip())
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(activity_text)
        block = activity_text[start:end]
        task_block = block
        if activity_level is not None and activity_level < 6:
            child_heading = re.search(
                rf"(?m)^#{{{activity_level + 1},6}} [^\n]+?\s*$",
                block,
            )
            if child_heading is not None:
                task_block = block[: child_heading.start()]
        task_values = tuple(
            re.sub(r"\s+", " ", item.group("item")).strip()
            for item in re.finditer(
                r"(?ms)^(?P<indent>[ \t]{0,3})(?:\d+[.)]|[-*+])\s+"
                r"(?P<item>.*?)(?=^(?P=indent)(?:\d+[.)]|[-*+])\s+|"
                r"^[ \t]*$\n(?=\S)|\Z)",
                task_block,
            )
        )
        tasks.append(task_values)
    return ProcessStructure(outcomes, tuple(activities), tuple(tasks))


def check_frontmatter(path: Path, text: str) -> list[str]:
    meta, errors = frontmatter(text)
    errors = [f"{path}: {error}" for error in errors]
    missing = {"name", "description"} - set(meta)
    if missing:
        errors.append(f"{path}: missing frontmatter keys: {', '.join(sorted(missing))}")
    name = meta.get("name", "")
    if "name" in meta and not name:
        errors.append(f"{path}: name must be non-empty")
    elif name and (len(name) > 63 or not NAME_RE.fullmatch(name)):
        errors.append(f"{path}: name must be <=63 characters in lowercase hyphen-case")
    kind = meta.get("alps.kind", "process")
    if kind not in SUPPORTED_KINDS:
        errors.append(f"{path}: unsupported metadata.alps.kind: {kind}")
    description = meta.get("description", "").strip()
    if "description" in meta and not description:
        errors.append(f"{path}: description must be non-empty")
    elif kind == "process" and description:
        suffix = DISCOVERY_SUFFIX[locale_for(path)]
        if not description.endswith(suffix):
            errors.append(f"{path}: Process description must end with {suffix!r}")
    return errors


def semantic_process_findings(path: Path, text: str, locale: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        process_core(path)
    except ValueError as exc:
        errors.append(str(exc))
        return errors, warnings

    structure = parse_process_structure(text, locale)
    for activity_index, tasks in enumerate(structure.tasks, start=1):
        for task_index, task in enumerate(tasks, start=1):
            if classify_normative(task, locale) is None:
                errors.append(
                    f"{path}: Activity {activity_index} Task {task_index} has no recognizable normative attribute"
                )
    for outcome in structure.outcomes:
        if RECORD_CENTRIC[locale].search(outcome):
            warnings.append(f"{path}: record-centric Outcome review candidate: {outcome}")
    inputs = section(text, HEADINGS[locale]["inputs"]) or ""
    if INPUT_CONTROL[locale].search(inputs):
        errors.append(f"{path}: applicable Control is classified as an Input")
    return errors, warnings


def check_process_model(
    path: Path,
    text: str,
    locale: str,
    roots: dict[str, Path],
    current_package_id: str | None,
) -> list[str]:
    errors = required_sections(path, text, "Process Model", locale, ("purpose", "processes", "relationships"))
    processes = section(text, HEADINGS[locale]["processes"]) or ""
    relationships = section(text, HEADINGS[locale]["relationships"]) or ""
    relationship_tables = markdown_tables(relationships)
    relationship_rows = [
        row for _, rows in relationship_tables for row in rows
    ]
    process_entries = process_model_entries(processes)
    relationship_items = re.findall(r"(?m)^\s{0,3}(?:[-*+]|\d+[.)])\s+\S", relationships)
    if not process_entries and not references(processes):
        errors.append(f"{path}: Process Model requires identifiable Process entries")
    if not relationship_rows and not relationship_items:
        errors.append(f"{path}: Process Model requires identifiable relationship entries")
    errors.extend(relationship_table_errors(path, relationships))
    errors.extend(relationship_list_endpoint_errors(path, relationships))

    process_references = references(processes)
    declared_references = set(normalized_references(processes, current_package_id))
    declared_names = {
        process_display_name(entry) for entry in process_model_entries(processes)
    } - {""}
    for reference in process_references:
        try:
            target = resolve_skill(reference, roots, locale, current_package_id)
        except ValueError as exc:
            errors.append(f"{path}: {exc}")
            continue
        if representation_kind(target.path) != "process":
            errors.append(f"{path}: {reference} does not resolve to a Process representation")
    for reference in references(relationships):
        try:
            target = resolve_skill(reference, roots, locale, current_package_id)
        except ValueError as exc:
            errors.append(f"{path}: {exc}")
            continue
        if representation_kind(target.path) != "process":
            errors.append(f"{path}: {reference} does not resolve to a Process representation")
            continue
        target_name = heading1(target.path.read_text(encoding="utf-8"))
        if (
            normalized_references(reference, current_package_id)[0] not in declared_references
            and process_display_name(target_name or "") not in declared_names
        ):
            errors.append(f"{path}: relationship endpoint {reference} is not declared in Processes")
    errors.extend(
        named_relationship_endpoint_errors(
            path,
            relationships,
            declared_names,
            declared_references,
            roots,
            locale,
            current_package_id,
        )
    )
    return errors


def process_model_entries(value: str, *, include_headings: bool = True) -> list[str]:
    table_rows = [row for _, rows in markdown_tables(value) for row in rows]
    if table_rows:
        return [row[0] for row in table_rows if row and row[0]]
    entries = [
        match.group(1).strip()
        for match in re.finditer(
            r"(?m)^\s{0,3}(?:[-*+]|\d+[.)])\s+(\S.*)$", value
        )
    ]
    if entries:
        return entries
    if not include_headings:
        return []
    visible = without_html_comments(without_indented_code(without_fenced_code(value)))
    headings = list(
        re.finditer(r"(?m)^ {0,3}(#{3,6})\s+([^\n]+?)\s*$", visible)
    )
    entry_level = min((len(match.group(1)) for match in headings), default=None)
    return [
        match.group(2).strip()
        for match in headings
        if len(match.group(1)) == entry_level
    ]


def relationship_endpoint_cells(value: str) -> list[tuple[str, int, str, str]]:
    """Return provider and recipient cells from recognized relationship structures."""

    table_endpoints: list[tuple[str, int, str, str]] = []
    for header, rows in markdown_tables(value):
        endpoint_indices = relationship_table_endpoint_indices(header)
        if not rows or endpoint_indices is None:
            continue
        provider_index, recipient_index = endpoint_indices
        table_endpoints.extend(
            (
                ("row", row_number, role, row[index])
                for row_number, row in enumerate(rows, start=1)
                for role, index in (("provider", provider_index), ("recipient", recipient_index))
                if len(row) > index
            )
        )
    if table_endpoints:
        return table_endpoints

    endpoints: list[tuple[str, int, str, str]] = []
    for item_number, item in enumerate(
        process_model_entries(value, include_headings=False), start=1
    ):
        cells = table_row_cells(item)
        if len(cells) >= 3:
            endpoints.extend(
                (
                    ("item", item_number, "provider", cells[0]),
                    ("item", item_number, "recipient", cells[2]),
                )
            )
            continue
        arrow = re.search(r"\s+(?:->|=>|→|⟶|⟹)\s+", item)
        if not arrow:
            continue
        provider = item[: arrow.start()].strip()
        recipient = item[arrow.end() :].strip()
        if not references(recipient):
            recipient = process_display_name(recipient)
        if provider and recipient:
            endpoints.extend(
                (
                    ("item", item_number, "provider", provider),
                    ("item", item_number, "recipient", recipient),
                )
            )
    return endpoints


def relationship_list_endpoint_errors(path: Path, value: str) -> list[str]:
    """Reject list relationship items that do not identify both endpoints."""
    if any(rows for _, rows in markdown_tables(value)):
        return []
    items = process_model_entries(value, include_headings=False)
    if not items:
        return []
    endpoint_items = {
        (entry_kind, entry_number)
        for entry_kind, entry_number, _, _ in relationship_endpoint_cells(value)
    }
    errors: list[str] = []
    for item_number, item in enumerate(items, start=1):
        if ("item", item_number) in endpoint_items:
            continue
        errors.append(
            f"{path}: relationship item {item_number} must identify "
            "provider and recipient Processes"
        )
    return errors


def named_relationship_endpoint_errors(
    path: Path,
    relationships: str,
    declared_names: set[str],
    declared_references: set[tuple[str, str]],
    roots: dict[str, Path],
    locale: str,
    current_package_id: str | None,
) -> list[str]:
    errors: list[str] = []
    for entry_kind, entry_number, role, cell in relationship_endpoint_cells(relationships):
        cell_references = references(cell)
        if len(cell_references) > 1:
            errors.append(
                f"{path}: relationship {entry_kind} {entry_number} {role} Process "
                "must identify at most one canonical Skill reference"
            )
            continue
        if cell_references:
            reference = cell_references[0]
            try:
                target = resolve_skill(reference, roots, locale, current_package_id)
            except ValueError as exc:
                errors.append(f"{path}: relationship {entry_kind} {entry_number} {role}: {exc}")
                continue
            if representation_kind(target.path) != "process":
                errors.append(
                    f"{path}: relationship {entry_kind} {entry_number} {role} "
                    f"reference {reference} does not resolve to a Process representation"
                )
                continue
            target_name = process_display_name(
                heading1(target.path.read_text(encoding="utf-8")) or ""
            )
            displayed_name = process_display_name(cell)
            if displayed_name and displayed_name != target_name:
                errors.append(
                    f"{path}: relationship {entry_kind} {entry_number} {role} "
                    f"Process name {displayed_name!r} differs from referenced Process {target_name!r}"
                )
            reference_key = normalized_references(reference, current_package_id)[0]
            if reference_key not in declared_references and target_name not in declared_names:
                errors.append(
                    f"{path}: relationship {entry_kind} {entry_number} {role} "
                    f"endpoint {reference} is not declared in Processes"
                )
            continue
        endpoint = process_display_name(cell)
        if endpoint in declared_names:
            continue
        errors.append(
            f"{path}: relationship {entry_kind} {entry_number} {role} Process "
            f"{cell!r} is not declared in Processes"
        )
    return errors


def process_block_details(value: str) -> list[tuple[str, str, int]]:
    visible = without_html_comments(without_fenced_code(value))
    child_headings = {
        HEADINGS[locale][key]
        for locale in HEADINGS
        for key in ("purpose", "outcomes")
    }
    candidates = [
        match
        for match in re.finditer(r"(?m)^(#{3,5}) ([^\n]+?)\s*$", visible)
        if match.group(2).strip() not in child_headings
    ]
    entry_level = min((len(match.group(1)) for match in candidates), default=None)
    headings = [
        match for match in candidates if len(match.group(1)) == entry_level
    ]
    return [
        (
            match.group(2).strip(),
            visible[
                match.end() : headings[index + 1].start()
                if index + 1 < len(headings)
                else None
            ],
            len(match.group(1)),
        )
        for index, match in enumerate(headings)
    ]


def process_blocks(value: str) -> list[tuple[str, str]]:
    return [(name, body) for name, body, _ in process_block_details(value)]


def check_reference_model(
    path: Path,
    text: str,
    locale: str,
    roots: dict[str, Path],
    current_package_id: str | None,
) -> list[str]:
    errors = required_sections(
        path, text, "Process Reference Model", locale, ("purpose", "processes", "relationships")
    )
    processes = section(text, HEADINGS[locale]["processes"]) or ""
    relationships = section(text, HEADINGS[locale]["relationships"]) or ""
    blocks = process_block_details(processes)
    if not blocks:
        return errors + [f"{path}: no Process entries found"]
    relationship_tables = markdown_tables(relationships)
    relationship_rows = [
        row for _, rows in relationship_tables for row in rows
    ]
    relationship_items = re.findall(
        r"(?m)^\s{0,3}(?:[-*+]|\d+[.)])\s+\S", relationships
    )
    if not relationship_rows and not relationship_items:
        errors.append(
            f"{path}: Process Reference Model requires identifiable relationship entries"
        )
    errors.extend(relationship_table_errors(path, relationships))
    errors.extend(relationship_list_endpoint_errors(path, relationships))

    declared_references = set(normalized_references(processes, current_package_id))
    declared_names = {model_name for model_name, _, _ in blocks}
    for model_name, body, level in blocks:
        child_level = level + 1
        purpose = section(
            body,
            HEADINGS[locale]["purpose"],
            child_level,
            stop_at_any_heading=True,
        )
        outcomes = section(
            body,
            HEADINGS[locale]["outcomes"],
            child_level,
            stop_at_any_heading=True,
        )
        if purpose is None or not purpose.strip() or not outcome_items(outcomes):
            errors.append(f"{path}: {model_name}: non-empty Purpose and Outcomes are required")
            continue
        refs = references(body)
        if len(refs) > 1:
            errors.append(f"{path}: {model_name}: at most one authoritative Process Skill reference is allowed")
            continue
        if not refs:
            continue
        try:
            target = resolve_skill(refs[0], roots, locale, current_package_id)
        except ValueError as exc:
            errors.append(f"{path}: {model_name}: {exc}")
            continue
        if representation_kind(target.path) != "process":
            errors.append(f"{path}: {model_name}: {refs[0]} does not represent a Process")
            continue
        try:
            source_name, source_purpose, source_outcomes = process_core(target.path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        model_purpose = " ".join(normalized_lines(purpose))
        model_outcomes = outcome_items(outcomes)
        if model_name != source_name:
            errors.append(f"{path}: Process Name {model_name!r} differs from {target.path}: {source_name!r}")
        if model_purpose != source_purpose:
            errors.append(f"{path}: {model_name}: Purpose differs from {target.path}")
        if model_outcomes != source_outcomes:
            errors.append(f"{path}: {model_name}: Outcomes differ from {target.path}")

    for reference in references(relationships):
        try:
            target = resolve_skill(reference, roots, locale, current_package_id)
        except ValueError as exc:
            errors.append(f"{path}: {exc}")
            continue
        if representation_kind(target.path) != "process":
            errors.append(f"{path}: {reference} does not resolve to a Process representation")
            continue
        target_name = heading1(target.path.read_text(encoding="utf-8"))
        reference_key = normalized_references(reference, current_package_id)[0]
        if reference_key not in declared_references and target_name not in declared_names:
            errors.append(f"{path}: relationship endpoint {reference} is not declared in Processes")
    for relationship_header, relationship_table_rows in relationship_tables:
        if len(relationship_header) < 3:
            continue
        for row_number, row in enumerate(relationship_table_rows, start=1):
            if len(row) < 3:
                errors.append(
                    f"{path}: relationship row {row_number} must identify provider and recipient Processes"
                )
    errors.extend(
        named_relationship_endpoint_errors(
            path,
            relationships,
            declared_names,
            declared_references,
            roots,
            locale,
            current_package_id,
        )
    )
    return errors


def source_entries(value: str) -> list[str]:
    _, rows = table(value)
    if rows:
        return [row[0] for row in rows if row and row[0]]
    structured = [
        re.sub(r"^(?:[-*+]\s+|\d+[.)]\s+|#{3,}\s+)", "", line)
        for line in normalized_lines(value)
        if re.match(r"^(?:[-*+]\s+|\d+[.)]\s+|#{3,}\s+)", line)
    ]
    return structured or normalized_lines(value)


def source_identity(value: str, *, preserve_parentheses: bool = False) -> str:
    value = re.sub(
        r"`?skill:[^\s`<>()\[\]{}\"',;!?。、，；：！？）」』】〉》]+`?",
        "",
        value,
    )
    value = re.sub(r"[（(]\s*[）)]", "", value)
    strip_characters = " |-" if preserve_parentheses else " |-:()（）"
    return re.sub(r"\s+", " ", value).strip(strip_characters)


def process_display_name(value: str) -> str:
    """Return a displayed Process name without an optional entry description."""
    identity = source_identity(value, preserve_parentheses=True)
    if not identity:
        return ""
    parenthesis_depth = 0
    for index, character in enumerate(identity):
        if character in "（(":
            parenthesis_depth += 1
        elif character in "）)":
            parenthesis_depth = max(0, parenthesis_depth - 1)
        elif parenthesis_depth == 0 and character in ":：":
            return identity[:index].strip()
        elif (
            parenthesis_depth == 0
            and character in "–—-"
            and index > 0
            and index + 1 < len(identity)
            and identity[index - 1].isspace()
            and identity[index + 1].isspace()
        ):
            return identity[:index].strip()
    return identity


def declared_process_identities(
    entries: Iterable[tuple[str, Iterable[str]]],
    current_package_id: str | None,
    name_normalizer: Callable[[str], str],
) -> dict[str, str | None]:
    """Map displayed Process names to stable identities when available."""
    identities: dict[str, str | None] = {}
    for raw_name, raw_references in entries:
        process_references = list(raw_references)
        name = name_normalizer(raw_name)
        if not name:
            continue
        if len(process_references) == 1:
            identity = normalized_reference_key(process_references[0], current_package_id)
        else:
            identity = f"name:{name}"
        if name not in identities or identities[name] is None:
            identities[name] = identity
        elif identities[name] != identity or identity is None:
            identities[name] = None
    return identities


def process_model_identities(
    value: str,
    current_package_id: str | None,
) -> dict[str, str | None]:
    table_rows = [row for _, rows in markdown_tables(value) for row in rows]
    if table_rows:
        entries = (
            (row[0], references(" ".join(row)))
            for row in table_rows
            if row and row[0]
        )
    else:
        entries = (
            (entry, references(entry))
            for entry in process_model_entries(value)
        )
    return declared_process_identities(
        entries,
        current_package_id,
        process_display_name,
    )


def process_reference_model_identities(
    value: str,
    current_package_id: str | None,
) -> dict[str, str | None]:
    return declared_process_identities(
        (
            (displayed_name, references(body))
            for displayed_name, body in process_blocks(value)
        ),
        current_package_id,
        source_identity,
    )


def normalized_relationship_endpoint_pairs(
    value: str,
    process_identities: dict[str, str | None],
    current_package_id: str | None,
) -> tuple[tuple[str | None, str | None], ...]:
    """Normalize parsed provider/recipient endpoints to declared Process identities."""
    grouped: dict[tuple[str, int], dict[str, str | None]] = {}
    order: list[tuple[str, int]] = []
    for entry_kind, entry_number, role, cell in relationship_endpoint_cells(value):
        entry_key = (entry_kind, entry_number)
        if entry_key not in grouped:
            grouped[entry_key] = {}
            order.append(entry_key)
        cell_references = references(cell)
        if len(cell_references) == 1:
            identity: str | None = normalized_reference_key(
                cell_references[0], current_package_id
            )
        elif cell_references:
            identity = None
        else:
            identity = process_identities.get(process_display_name(cell))
        grouped[entry_key][role] = identity
    return tuple(
        (
            grouped[entry_key].get("provider"),
            grouped[entry_key].get("recipient"),
        )
        for entry_key in order
    )


def relationship_endpoint_pair_status(
    english_relationships: str,
    japanese_relationships: str,
    english_process_identities: dict[str, str | None],
    japanese_process_identities: dict[str, str | None],
    current_package_id: str | None,
) -> tuple[bool, bool]:
    """Return (stable mismatch, unverified) for paired relationship endpoints."""
    english_pairs = normalized_relationship_endpoint_pairs(
        english_relationships,
        english_process_identities,
        current_package_id,
    )
    japanese_pairs = normalized_relationship_endpoint_pairs(
        japanese_relationships,
        japanese_process_identities,
        current_package_id,
    )
    if not english_pairs or len(english_pairs) != len(japanese_pairs):
        return False, False
    mismatch = False
    unverified = False
    for english_pair, japanese_pair in zip(english_pairs, japanese_pairs):
        for english_identity, japanese_identity in zip(english_pair, japanese_pair):
            if english_identity is None or japanese_identity is None:
                unverified = True
            elif english_identity.startswith("ref:") and japanese_identity.startswith("ref:"):
                if english_identity != japanese_identity:
                    mismatch = True
            elif english_identity.startswith("name:") and japanese_identity.startswith("name:"):
                if english_identity != japanese_identity:
                    unverified = True
            else:
                unverified = True
    return mismatch, unverified


def relationship_endpoint_pairs_differ(
    english_relationships: str,
    japanese_relationships: str,
    english_process_identities: dict[str, str | None],
    japanese_process_identities: dict[str, str | None],
    current_package_id: str | None,
) -> bool:
    """Return whether stable endpoint identities differ across locales."""
    mismatch, _ = relationship_endpoint_pair_status(
        english_relationships,
        japanese_relationships,
        english_process_identities,
        japanese_process_identities,
        current_package_id,
    )
    return mismatch


def unverified_relationship_warning(english: Path, japanese: Path) -> str:
    return (
        f"{english} / {japanese}: Process relationship endpoint identity is unverified "
        "because one or more translated endpoints lack a stable canonical reference "
        "or matching displayed name"
    )


def source_cell_reference_errors(
    path: Path,
    context: str,
    value: str,
    roots: dict[str, Path],
    locale: str,
    current_package_id: str | None,
    displayed_value: str | None = None,
) -> list[str]:
    errors: list[str] = []
    cell_references = references(value)
    if len(cell_references) > 1:
        errors.append(
            f"{path}: {context} must identify at most one canonical Skill reference"
        )
        return errors
    if not cell_references:
        return errors
    reference = cell_references[0]
    try:
        target = resolve_skill(reference, roots, locale, current_package_id)
    except ValueError as exc:
        errors.append(f"{path}: {context}: {exc}")
        return errors
    if representation_kind(target.path) != "process":
        errors.append(
            f"{path}: {context} reference {reference} does not resolve to a Process representation"
        )
        return errors
    target_name = source_identity(
        heading1(target.path.read_text(encoding="utf-8")) or ""
    )
    displayed_name = source_identity(
        value if displayed_value is None else displayed_value
    )
    if displayed_name and displayed_name != target_name:
        errors.append(
            f"{path}: {context} Process name {displayed_name!r} differs from "
            f"referenced Process {target_name!r}"
        )
    return errors


def source_reference_errors(
    path: Path,
    value: str,
    roots: dict[str, Path],
    locale: str,
    current_package_id: str | None,
) -> list[str]:
    """Validate displayed Source Process names before canonical binding."""

    _, rows = table(value)
    if rows:
        candidates = [
            ("source row", row_number, " ".join(row), row[0] if row else "")
            for row_number, row in enumerate(rows, start=1)
        ]
    else:
        candidates = [
            ("source entry", entry_number, entry, None)
            for entry_number, entry in enumerate(source_entries(value), start=1)
        ]
    errors: list[str] = []
    for entry_kind, entry_number, entry, displayed_value in candidates:
        errors.extend(
            source_cell_reference_errors(
                path,
                f"{entry_kind} {entry_number}",
                entry,
                roots,
                locale,
                current_package_id,
                displayed_value,
            )
        )
    return errors


def normalized_reference_key(
    reference: str,
    current_package_id: str | None,
    roots: dict[str, Path] | None = None,
) -> str:
    package, skill = normalized_references(reference, current_package_id)[0]
    if not package and roots is not None and "" in roots:
        current_root = roots[""].resolve()
        aliases = sorted(
            identity
            for identity, root in roots.items()
            if identity and root.resolve() == current_root
        )
        if len(aliases) == 1:
            package = aliases[0]
    return f"ref:{package}#{skill}"


def source_canonical_names(
    value: str,
    current_package_id: str | None,
    roots: dict[str, Path] | None,
    locale: str,
) -> dict[str, str]:
    canonical_names: dict[str, str] = {}

    def bind(name: str, key: str) -> None:
        existing = canonical_names.get(name)
        canonical_names[name] = key if existing is None or existing == key else ""

    for entry in source_entries(value):
        refs = references(entry)
        if len(refs) != 1:
            continue
        reference = refs[0]
        key = normalized_reference_key(reference, current_package_id, roots)
        displayed_name = source_identity(entry)
        if displayed_name:
            if roots is not None:
                try:
                    target = resolve_skill(reference, roots, locale, current_package_id)
                except ValueError:
                    continue
                target_name = source_identity(
                    heading1(target.path.read_text(encoding="utf-8")) or ""
                )
                if target_name and displayed_name != target_name:
                    continue
            bind(displayed_name, key)
    _, rows = table(value)
    for row in rows:
        refs = references(" ".join(row))
        if len(refs) == 1 and row and source_identity(row[0]):
            displayed_name = source_identity(row[0])
            if roots is not None:
                try:
                    target = resolve_skill(refs[0], roots, locale, current_package_id)
                except ValueError:
                    continue
                target_name = source_identity(
                    heading1(target.path.read_text(encoding="utf-8")) or ""
                )
                if target_name and displayed_name != target_name:
                    continue
            bind(
                displayed_name,
                normalized_reference_key(refs[0], current_package_id, roots),
            )
    if roots is not None:
        for reference in references(value):
            try:
                target = resolve_skill(reference, roots, locale, current_package_id)
            except ValueError:
                continue
            target_name = heading1(target.path.read_text(encoding="utf-8"))
            if target_name:
                bind(
                    source_identity(target_name),
                    normalized_reference_key(reference, current_package_id, roots),
                )
    return canonical_names


def source_identity_key(
    value: str,
    current_package_id: str | None,
    roots: dict[str, Path] | None,
    canonical_names: dict[str, str],
) -> str:
    refs = references(value)
    if refs:
        return normalized_reference_key(refs[0], current_package_id, roots)
    identity = source_identity(value)
    if not identity:
        return ""
    return canonical_names.get(identity, f"name:{identity}")


def source_process_keys(
    value: str,
    current_package_id: str | None,
    roots: dict[str, Path] | None = None,
    locale: str = "en",
) -> set[str]:
    """Return one identity key per declared Source Process.

    A displayed Process name and the canonical reference in the same table row
    identify one source, not two independent sources.
    """

    _, rows = table(value)
    canonical_names = source_canonical_names(value, current_package_id, roots, locale)

    keys: set[str] = set()
    if rows:
        for row in rows:
            row_text = " ".join(row)
            refs = references(row_text)
            if refs:
                keys.add(normalized_reference_key(refs[0], current_package_id, roots))
            elif row and source_identity(row[0]):
                identity = source_identity(row[0])
                keys.add(canonical_names.get(identity, f"name:{identity}"))
        return keys
    ordered: list[str] = []
    pending_name_index: int | None = None
    for entry in source_entries(value):
        refs = references(entry)
        if refs:
            key = normalized_reference_key(refs[0], current_package_id, roots)
            # Plain Markdown can place a displayed Process name on one line
            # and its canonical reference on the next.  Replace that pending
            # displayed-name key instead of counting the same source twice.
            if not source_identity(entry) and pending_name_index is not None:
                ordered[pending_name_index] = key
                pending_name_index = None
            else:
                ordered.append(key)
                pending_name_index = None
        elif source_identity(entry):
            identity = source_identity(entry)
            ordered.append(canonical_names.get(identity, f"name:{identity}"))
            pending_name_index = len(ordered) - 1
    return set(ordered)


def included_kind_pattern(locale: str) -> re.Pattern[str]:
    if locale == "en":
        return re.compile(r"\b(?:Activity|Task)\b", re.I)
    return re.compile(r"活動|タスク")


def included_visible_text(value: str) -> str:
    """Mask code while retaining nested list markers under a visible list."""
    cleaned = without_html_comments(without_fenced_code(value))
    visible: list[str] = []
    list_indent: int | None = None
    for line in cleaned.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        newline = line[len(content) :]
        if not content.strip():
            visible.append(line)
            list_indent = None
            continue
        expanded = content.expandtabs(4)
        indent = len(expanded) - len(expanded.lstrip(" "))
        marker = re.match(r"^ *(?:[-*+]|\d+[.)])\s+", expanded)
        if marker:
            if indent <= 3 or (list_indent is not None and indent <= 32):
                visible.append(expanded[indent:] + newline if indent > 3 else line)
                list_indent = indent
            else:
                visible.append(newline)
            continue
        if list_indent is not None and indent <= list_indent:
            list_indent = None
        if indent >= 4:
            visible.append(newline)
            continue
        visible.append(line)
    return "".join(visible)


def included_semantic_items(
    value: str,
    locale: str,
) -> list[tuple[str, str]]:
    """Extract structured Activity/Task items without comparing names."""
    visible = included_visible_text(value)
    pattern = included_kind_pattern(locale)
    lines = visible.splitlines()
    headings: list[tuple[int, int, str | None]] = []
    for line_number, line in enumerate(lines):
        heading = re.match(r"^ {0,3}(#{3,6})\s+(.+?)\s*$", line)
        if heading is None:
            continue
        candidate = heading.group(2)
        kind_match = pattern.search(without_inline_code(candidate))
        kind = None
        if kind_match is not None:
            kind = "activity" if kind_match.group(0).casefold() in {"activity", "活動"} else "task"
        headings.append((line_number, len(heading.group(1)), kind))
    # An unqualified heading at the shallowest heading level is the structural
    # Activity boundary.  Explicit Task headings must not move that boundary,
    # and a heading's own kind remains authoritative when it is emitted.
    activity_level = min(
        (level for _, level, kind in headings if kind != "task"),
        default=None,
    )
    heading_structure = activity_level is not None
    events: list[tuple[int, str, str]] = []
    heading_stack: list[tuple[int, str | None]] = []
    for line_number, line in enumerate(lines):
        heading = re.match(r"^ {0,3}(#{3,6})\s+(.+?)\s*$", line)
        if heading is not None:
            level = len(heading.group(1))
            candidate = heading.group(2)
            kind_match = pattern.search(without_inline_code(candidate))
            heading_kind = None
            if kind_match is not None:
                heading_kind = (
                    "activity"
                    if kind_match.group(0).casefold() in {"activity", "活動"}
                    else "task"
                )
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, heading_kind))
            if not heading_structure:
                if heading_kind is None:
                    continue
                kind = heading_kind
            elif level == activity_level:
                kind = heading_kind or "activity"
            elif level == activity_level + 1 and heading_kind == "task":
                kind = "task"
            else:
                continue
        else:
            item = re.match(r"^ {0,3}(?:[-*+]|\d+[.)])\s+(.+?)\s*$", line)
            if item is None:
                continue
            direct_activity_item = False
            if heading_structure and heading_stack:
                context_level, _ = heading_stack[-1]
                direct_activity_item = context_level == activity_level
                if not direct_activity_item:
                    continue
            candidate = item.group(1)
            kind_match = pattern.search(without_inline_code(candidate))
            if direct_activity_item:
                # A list directly under an Activity heading is its task list;
                # deeper heading bodies are intentionally non-semantic.
                kind = "task"
            else:
                if kind_match is None:
                    continue
                kind = "activity" if kind_match.group(0).casefold() in {"activity", "活動"} else "task"
        events.append((line_number, kind, candidate))
    return [(kind, candidate) for _, kind, candidate in events]


def included_semantic_elements(
    value: str,
    locale: str,
    current_package_id: str | None,
) -> list[tuple[str, str | None]]:
    """Extract structured Activity/Task elements without comparing names."""
    events = included_semantic_items(value, locale)
    result: list[tuple[str, str | None]] = []
    for kind, candidate in events:
        refs = references(candidate)
        identity = (
            normalized_reference_key(refs[0], current_package_id)
            if len(refs) == 1
            else None
        )
        result.append((kind, identity))
    return result


def included_reference_errors(
    path: Path,
    items: Iterable[tuple[str, str]],
    source_text: str,
    roots: dict[str, Path],
    locale: str,
    current_package_id: str | None,
) -> list[str]:
    """Validate canonical source identities in non-table Included items."""
    declared_keys = source_process_keys(source_text, current_package_id, roots, locale)
    errors: list[str] = []
    for item_number, (_, candidate) in enumerate(items, start=1):
        item_references = references(candidate)
        if len(item_references) > 1:
            errors.append(
                f"{path}: included item {item_number} must identify at most one canonical Skill reference"
            )
            continue
        if not item_references:
            continue
        reference = item_references[0]
        try:
            target = resolve_skill(reference, roots, locale, current_package_id)
        except ValueError as exc:
            errors.append(f"{path}: included item {item_number}: {exc}")
            continue
        if representation_kind(target.path) != "process":
            errors.append(
                f"{path}: included item {item_number} reference {reference} "
                "does not resolve to a Process representation"
            )
            continue
        target_name = source_identity(
            heading1(target.path.read_text(encoding="utf-8")) or ""
        )
        reference_key = normalized_reference_key(
            reference, current_package_id, roots
        )
        target_name_key = f"name:{target_name}" if target_name else ""
        if reference_key not in declared_keys and target_name_key not in declared_keys:
            errors.append(
                f"{path}: included item {item_number} reference {reference} "
                "names an undeclared Source Process"
            )
    return errors


def check_view(
    path: Path,
    text: str,
    locale: str,
    roots: dict[str, Path],
    current_package_id: str | None,
) -> tuple[list[str], list[str]]:
    errors = required_sections(
        path,
        text,
        "Process View",
        locale,
        ("purpose", "outcomes", "sources", "included", "application"),
    )
    warnings: list[str] = []
    if not outcome_items(section(text, HEADINGS[locale]["outcomes"])):
        errors.append(f"{path}: Process View requires at least one Outcome")

    source_text = section(text, HEADINGS[locale]["sources"]) or ""
    errors.extend(
        source_reference_errors(
            path, source_text, roots, locale, current_package_id
        )
    )
    source_values = source_entries(source_text)
    if len(source_process_keys(source_text, current_package_id, roots, locale)) < 2:
        errors.append(f"{path}: Process View requires at least two distinct Source Processes")
    for reference in references(source_text):
        try:
            target = resolve_skill(reference, roots, locale, current_package_id)
        except ValueError as exc:
            errors.append(f"{path}: {exc}")
            continue
        if representation_kind(target.path) != "process":
            errors.append(f"{path}: source reference {reference} does not resolve to a Process representation")

    included = section(text, HEADINGS[locale]["included"]) or ""
    header, rows = table(included)
    expected = (
        ("Source Process", "Source element")
        if locale == "en"
        else ("出典プロセス", "出典要素")
    )
    if rows:
        if len(header) < 2 or tuple(header[:2]) != expected:
            errors.append(f"{path}: Process View provenance table must begin with {expected[0]} and {expected[1]}")
        canonical_names = source_canonical_names(
            source_text, current_package_id, roots, locale
        )
        declared_keys = source_process_keys(
            source_text, current_package_id, roots, locale
        )
        for row_number, row in enumerate(rows, start=1):
            if len(row) < 2 or not row[0] or not row[1]:
                errors.append(f"{path}: provenance row {row_number} must identify Source Process and source element")
                continue
            row_refs = references(row[0])
            if len(row_refs) > 1:
                errors.append(
                    f"{path}: provenance row {row_number} must identify exactly one Source Process"
                )
                continue
            errors.extend(
                source_cell_reference_errors(
                    path,
                    f"provenance row {row_number}",
                    row[0],
                    roots,
                    locale,
                    current_package_id,
                )
            )
            row_source = source_identity_key(
                row[0], current_package_id, roots, canonical_names
            )
            if not row_source:
                errors.append(
                    f"{path}: provenance row {row_number} has no usable Source Process identity"
                )
                continue
            if row_refs:
                try:
                    target = resolve_skill(row_refs[0], roots, locale, current_package_id)
                except ValueError as exc:
                    errors.append(f"{path}: provenance row {row_number}: {exc}")
                    continue
                if representation_kind(target.path) != "process":
                    errors.append(
                        f"{path}: provenance row {row_number} source reference "
                        f"{row_refs[0]} does not resolve to a Process representation"
                    )
                    continue
            if row_source not in declared_keys:
                errors.append(f"{path}: provenance row {row_number} names an undeclared Source Process: {row[0]}")
    elif included.strip():
        structured_items = included_semantic_items(included, locale)
        if structured_items:
            errors.extend(
                included_reference_errors(
                    path,
                    structured_items,
                    source_text,
                    roots,
                    locale,
                    current_package_id,
                )
            )
            warnings.append(
                f"{path}: source-element provenance could not be established mechanically"
            )
        else:
            errors.append(
                f"{path}: Process View Included Activities and Tasks must identify at least one Activity or Task"
            )
    return errors, warnings


def check_asset(
    path: Path,
    roots: dict[str, Path],
    current_package_id: str | None,
) -> tuple[list[str], list[str]]:
    text = path.read_text(encoding="utf-8")
    locale = locale_for(path)
    errors = check_frontmatter(path, text)
    errors.extend(reference_syntax_errors(path, text))
    package_root = containing_package_root(path, roots)
    package_identity = containing_package_identity(path, roots, current_package_id)
    if package_root is None:
        errors.append(f"{path}: representation is outside the declared package roots")
    else:
        errors.extend(local_link_errors(path, text, package_root))
    warnings: list[str] = []
    if not heading1(text):
        errors.append(f"{path}: representation requires Name as a level-one heading")
    meta, frontmatter_errors = frontmatter(text)
    if frontmatter_errors and "alps.kind" not in meta:
        return errors, warnings
    kind = meta.get("alps.kind", "process")
    if kind not in SUPPORTED_KINDS:
        return errors, warnings
    if kind == "process":
        more_errors, more_warnings = semantic_process_findings(path, text, locale)
        return errors + more_errors, warnings + more_warnings
    if kind == "process-model":
        return errors + check_process_model(path, text, locale, roots, package_identity), warnings
    if kind == "process-reference-model":
        return errors + check_reference_model(path, text, locale, roots, package_identity), warnings
    more_errors, more_warnings = check_view(path, text, locale, roots, package_identity)
    return errors + more_errors, warnings + more_warnings


def japanese_prose_lines(
    text: str,
    *,
    include_description: bool = True,
) -> Iterable[tuple[int, str]]:
    text = without_html_comments(without_fenced_code(text))
    in_frontmatter = False
    description_indent: int | None = None
    for number, original in enumerate(text.splitlines(), start=1):
        stripped = original.strip()
        if number == 1 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if stripped == "---":
                in_frontmatter = False
                description_indent = None
                continue
            if description_indent is not None:
                indent = len(original) - len(original.lstrip())
                if not stripped:
                    continue
                if indent > description_indent:
                    if include_description:
                        yield number, original
                    continue
                description_indent = None
            description = re.match(r"^(\s*)description:\s*(.*)$", original)
            if description:
                indent_text, value = description.groups()
                if re.fullmatch(r"[>|](?:[+-]?[1-9]?|[1-9][+-]?)", value.strip()):
                    description_indent = len(indent_text)
                elif include_description:
                    yield number, value
            continue
        if not stripped or stripped.startswith("<!--"):
            continue
        yield number, original


def raw_english_words(line: str, allowed_terms: set[str]) -> list[str]:
    for term in sorted(allowed_terms, key=len, reverse=True):
        line = line.replace(term, "")
    line = without_inline_code(line)
    line = re.sub(r"https?://\S+", "", line)
    line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)
    line = re.sub(r"<[^>]+>", "", line)
    line = re.sub(r"(?<!\w)(?:\.{0,2}/)?(?:[\w.-]+/)+[\w.-]+", "", line)
    line = re.sub(r"(?<!\w)[\w.-]+\.[A-Za-z0-9]{1,8}(?!\w)", "", line)
    words: list[str] = []
    for match in RAW_ENGLISH.finditer(line):
        word = match.group(0)
        if word.lower() in {"md", "markdown", "yaml", "yml", "json", "py", "svg"}:
            continue
        if word.isupper() or re.fullmatch(r"[A-Z0-9]+(?:-[A-Z0-9]+)+", word):
            continue
        if "-" in word and word == word.lower():
            continue
        words.append(word)
    return words


def frontmatter_field_line(text: str, field: str) -> int:
    """Return the source line for a decoded top-level frontmatter field."""
    if not text.startswith("---\n"):
        return 1
    end = text.find("\n---\n", 4)
    if end < 0:
        return 1
    for index, raw in enumerate(text[4:end].splitlines(), start=2):
        mapping = yaml_mapping_line(raw)
        if mapping is not None and mapping[0] == 0 and mapping[1] == field:
            return index
    return 1


def japanese_naturalness_errors(path: Path, text: str, allowed_terms: set[str]) -> list[str]:
    errors: list[str] = []
    decoded_frontmatter, _ = frontmatter(text)
    description = decoded_frontmatter.get("description")
    seen: set[tuple[int, str]] = set()

    def add_error(number: int, word: str) -> None:
        item = (number, word)
        if item in seen:
            return
        seen.add(item)
        errors.append(f"{path}:{number}: untranslated English in Japanese prose: {word}")

    for number, line in japanese_prose_lines(
        text,
        include_description=description is None,
    ):
        for word in raw_english_words(line, allowed_terms):
            add_error(number, word)
    if description is not None:
        number = frontmatter_field_line(text, "description")
        for word in raw_english_words(description, allowed_terms):
            add_error(number, word)
    return errors


def japanese_counterpart(english: Path) -> Path:
    return english.parent / "references" / "locales" / "ja" / "SKILL.md"


def english_counterpart(japanese: Path) -> Path | None:
    parts = japanese.parts
    try:
        index = next(
            index
            for index in range(len(parts) - 2)
            if parts[index : index + 3] == ("references", "locales", "ja")
        )
    except StopIteration:
        return None
    return Path(*parts[:index]) / "SKILL.md"


def check_pair(
    english: Path,
    japanese: Path,
    allowed_terms: set[str],
    current_package_id: str | None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    en_text = english.read_text(encoding="utf-8")
    ja_text = japanese.read_text(encoding="utf-8")
    en_meta, _ = frontmatter(en_text)
    ja_meta, _ = frontmatter(ja_text)
    if en_meta.get("name") != ja_meta.get("name"):
        errors.append(f"{english} / {japanese}: frontmatter name differs")
    en_kind = en_meta.get("alps.kind", "process")
    ja_kind = ja_meta.get("alps.kind", "process")
    if en_kind != ja_kind:
        errors.append(f"{english} / {japanese}: representation kind differs ({en_kind} != {ja_kind})")

    errors.extend(japanese_naturalness_errors(japanese, ja_text, allowed_terms))
    if en_kind == "process-model":
        en_process_text = section(en_text, HEADINGS["en"]["processes"]) or ""
        ja_process_text = section(ja_text, HEADINGS["ja"]["processes"]) or ""
        en_relationship_text = section(en_text, HEADINGS["en"]["relationships"]) or ""
        ja_relationship_text = section(ja_text, HEADINGS["ja"]["relationships"]) or ""
        en_processes = process_model_entries(en_process_text)
        ja_processes = process_model_entries(ja_process_text)
        en_relationships = process_model_entries(
            en_relationship_text, include_headings=False
        )
        ja_relationships = process_model_entries(
            ja_relationship_text, include_headings=False
        )
        if len(en_processes) != len(ja_processes):
            errors.append(
                f"{english} / {japanese}: Process count differs ({len(en_processes)} != {len(ja_processes)})"
            )
        if len(en_relationships) != len(ja_relationships):
            errors.append(
                f"{english} / {japanese}: Relationship count differs "
                f"({len(en_relationships)} != {len(ja_relationships)})"
            )
        en_refs = normalized_references(en_process_text, current_package_id)
        ja_refs = normalized_references(ja_process_text, current_package_id)
        if en_refs != ja_refs:
            errors.append(f"{english} / {japanese}: Process reference identity or order differs")
        en_relationship_refs = normalized_references(
            en_relationship_text, current_package_id
        )
        ja_relationship_refs = normalized_references(
            ja_relationship_text, current_package_id
        )
        if en_relationship_refs != ja_relationship_refs:
            errors.append(
                f"{english} / {japanese}: Relationship reference identity or order differs"
            )
        en_process_identities = process_model_identities(
            en_process_text,
            current_package_id,
        )
        ja_process_identities = process_model_identities(
            ja_process_text,
            current_package_id,
        )
        endpoint_mismatch, endpoint_unverified = relationship_endpoint_pair_status(
            en_relationship_text,
            ja_relationship_text,
            en_process_identities,
            ja_process_identities,
            current_package_id,
        )
        if endpoint_mismatch:
            errors.append(
                f"{english} / {japanese}: relationship provider/recipient "
                "endpoint identity or order differs"
            )
        if endpoint_unverified:
            warnings.append(unverified_relationship_warning(english, japanese))
        return errors, warnings
    if en_kind == "process-reference-model":
        en_processes = process_blocks(section(en_text, HEADINGS["en"]["processes"]) or "")
        ja_processes = process_blocks(section(ja_text, HEADINGS["ja"]["processes"]) or "")
        en_relationships = process_model_entries(
            section(en_text, HEADINGS["en"]["relationships"]) or "",
            include_headings=False,
        )
        ja_relationships = process_model_entries(
            section(ja_text, HEADINGS["ja"]["relationships"]) or "",
            include_headings=False,
        )
        if len(en_processes) != len(ja_processes):
            errors.append(
                f"{english} / {japanese}: Process count differs ({len(en_processes)} != {len(ja_processes)})"
            )
        if len(en_relationships) != len(ja_relationships):
            errors.append(
                f"{english} / {japanese}: Relationship count differs "
                f"({len(en_relationships)} != {len(ja_relationships)})"
            )
        en_refs = normalized_references(
            section(en_text, HEADINGS["en"]["processes"]) or "", current_package_id
        )
        ja_refs = normalized_references(
            section(ja_text, HEADINGS["ja"]["processes"]) or "", current_package_id
        )
        if en_refs != ja_refs:
            errors.append(f"{english} / {japanese}: Process reference identity or order differs")
        en_relationship_refs = normalized_references(
            section(en_text, HEADINGS["en"]["relationships"]) or "", current_package_id
        )
        ja_relationship_refs = normalized_references(
            section(ja_text, HEADINGS["ja"]["relationships"]) or "", current_package_id
        )
        if en_relationship_refs != ja_relationship_refs:
            errors.append(
                f"{english} / {japanese}: Relationship reference identity or order differs"
            )
        en_relationship_text = section(en_text, HEADINGS["en"]["relationships"]) or ""
        ja_relationship_text = section(ja_text, HEADINGS["ja"]["relationships"]) or ""
        en_process_identities = process_reference_model_identities(
            section(en_text, HEADINGS["en"]["processes"]) or "",
            current_package_id,
        )
        ja_process_identities = process_reference_model_identities(
            section(ja_text, HEADINGS["ja"]["processes"]) or "",
            current_package_id,
        )
        endpoint_mismatch, endpoint_unverified = relationship_endpoint_pair_status(
            en_relationship_text,
            ja_relationship_text,
            en_process_identities,
            ja_process_identities,
            current_package_id,
        )
        if endpoint_mismatch:
            errors.append(
                f"{english} / {japanese}: relationship provider/recipient "
                "endpoint identity or order differs"
            )
        if endpoint_unverified:
            warnings.append(unverified_relationship_warning(english, japanese))
        return errors, warnings
    if en_kind == "process-view":
        en_outcomes = outcome_items(section(en_text, HEADINGS["en"]["outcomes"]))
        ja_outcomes = outcome_items(section(ja_text, HEADINGS["ja"]["outcomes"]))
        en_source_text = section(en_text, HEADINGS["en"]["sources"]) or ""
        ja_source_text = section(ja_text, HEADINGS["ja"]["sources"]) or ""
        en_included_text = section(en_text, HEADINGS["en"]["included"]) or ""
        ja_included_text = section(ja_text, HEADINGS["ja"]["included"]) or ""
        en_sources = source_entries(en_source_text)
        ja_sources = source_entries(ja_source_text)
        en_included = table(en_included_text)[1]
        ja_included = table(ja_included_text)[1]
        if len(en_outcomes) != len(ja_outcomes):
            errors.append(
                f"{english} / {japanese}: Outcome count differs ({len(en_outcomes)} != {len(ja_outcomes)})"
            )
        if len(en_sources) != len(ja_sources):
            errors.append(
                f"{english} / {japanese}: Source Process count differs "
                f"({len(en_sources)} != {len(ja_sources)})"
            )
        if len(en_included) != len(ja_included):
            errors.append(
                f"{english} / {japanese}: included source-element count differs "
                f"({len(en_included)} != {len(ja_included)})"
            )
        en_refs = normalized_references(
            section(en_text, HEADINGS["en"]["sources"]) or "", current_package_id
        )
        ja_refs = normalized_references(
            section(ja_text, HEADINGS["ja"]["sources"]) or "", current_package_id
        )
        if en_refs != ja_refs:
            errors.append(f"{english} / {japanese}: Source Process reference identity or order differs")
        en_names = source_canonical_names(
            en_source_text, current_package_id, None, "en"
        )
        ja_names = source_canonical_names(
            ja_source_text, current_package_id, None, "ja"
        )

        def provenance_identity(
            rows: list[list[str]], canonical_names: dict[str, str]
        ) -> tuple[str, ...]:
            result: list[str] = []
            for row in rows:
                if len(row) < 2:
                    continue
                result.append(
                    source_identity_key(
                        row[0], current_package_id, None, canonical_names
                    )
                )
            return tuple(result)

        if provenance_identity(en_included, en_names) != provenance_identity(
            ja_included, ja_names
        ):
            errors.append(
                f"{english} / {japanese}: included source provenance or order differs"
            )
        if not en_included and not ja_included:
            en_elements = included_semantic_elements(
                en_included_text, "en", current_package_id
            )
            ja_elements = included_semantic_elements(
                ja_included_text, "ja", current_package_id
            )
            if en_elements and ja_elements:
                if len(en_elements) != len(ja_elements):
                    errors.append(
                        f"{english} / {japanese}: included Activity/Task count differs "
                        f"({len(en_elements)} != {len(ja_elements)})"
                    )
                elif tuple(kind for kind, _ in en_elements) != tuple(
                    kind for kind, _ in ja_elements
                ):
                    errors.append(
                        f"{english} / {japanese}: included Activity/Task kind/order differs"
                    )
                if len(en_elements) == len(ja_elements):
                    en_identities = tuple(identity for _, identity in en_elements)
                    ja_identities = tuple(identity for _, identity in ja_elements)
                    if all(identity is not None for identity in en_identities + ja_identities):
                        if en_identities != ja_identities:
                            errors.append(
                                f"{english} / {japanese}: included source identity or order differs"
                            )
                    elif any(identity is not None for identity in en_identities + ja_identities):
                        warnings.append(
                            f"{english} / {japanese}: included Activity/Task source identity is unverified"
                        )
            elif en_elements or ja_elements:
                warnings.append(
                    f"{english} / {japanese}: included Activity/Task structure is unverified "
                    "because one locale has no comparable structured elements"
                )
        return errors, warnings
    if en_kind != "process":
        return errors, warnings

    en = parse_process_structure(en_text, "en")
    ja = parse_process_structure(ja_text, "ja")
    if len(en.outcomes) != len(ja.outcomes):
        errors.append(
            f"{english} / {japanese}: Outcome count differs ({len(en.outcomes)} != {len(ja.outcomes)})"
        )
    if len(en.activities) != len(ja.activities):
        errors.append(
            f"{english} / {japanese}: Activity count differs ({len(en.activities)} != {len(ja.activities)})"
        )
    en_task_counts = tuple(map(len, en.tasks))
    ja_task_counts = tuple(map(len, ja.tasks))
    if en_task_counts != ja_task_counts:
        errors.append(
            f"{english} / {japanese}: Task counts by Activity differ ({en_task_counts} != {ja_task_counts})"
        )
    for activity_index in range(min(len(en.tasks), len(ja.tasks))):
        for task_index in range(min(len(en.tasks[activity_index]), len(ja.tasks[activity_index]))):
            en_force = classify_normative(en.tasks[activity_index][task_index], "en")
            ja_force = classify_normative(ja.tasks[activity_index][task_index], "ja")
            if en_force != ja_force:
                errors.append(
                    f"{english} / {japanese}: normative force differs at Activity {activity_index + 1} "
                    f"Task {task_index + 1} ({en_force} != {ja_force})"
                )
    return errors, warnings


def unique_paths(paths: Iterable[Path]) -> list[Path]:
    result: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            result.append(resolved)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--package-id")
    parser.add_argument("--package-root", action="append", default=[], metavar="PACKAGE=PATH")
    parser.add_argument("--require-japanese", action="store_true")
    parser.add_argument("--no-locale-pairs", action="store_true")
    parser.add_argument("--ja-allow-term", action="append", default=[])
    args = parser.parse_args()

    root = args.root.resolve()
    try:
        roots = package_roots(args.package_root, root, args.package_id)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2

    raw_paths = args.paths or sorted(root.glob("skills/*/SKILL.md"))
    paths = unique_paths(path if path.is_absolute() else root / path for path in raw_paths)
    errors: list[str] = []
    warnings: list[str] = []
    checked_pairs: set[tuple[Path, Path]] = set()
    checked_assets: set[Path] = set()
    allowed_terms = DEFAULT_JA_TERMS | set(args.ja_allow_term)

    for path in paths:
        if not path.is_file():
            errors.append(f"{path}: file not found")
            continue
        if path not in checked_assets:
            asset_errors, asset_warnings = check_asset(path, roots, args.package_id)
            errors.extend(asset_errors)
            warnings.extend(asset_warnings)
            checked_assets.add(path)
        if args.no_locale_pairs:
            continue
        if locale_for(path) == "ja":
            english = english_counterpart(path)
            japanese = path
        else:
            english = path
            japanese = japanese_counterpart(path)
        if english is None:
            continue
        if args.require_japanese and not japanese.is_file():
            errors.append(f"{english}: missing Japanese counterpart {japanese}")
            continue
        if not japanese.is_file() or not english.is_file():
            continue
        pair = (english.resolve(), japanese.resolve())
        if pair in checked_pairs:
            continue
        for localized_path in pair:
            if localized_path in checked_assets:
                continue
            asset_errors, asset_warnings = check_asset(localized_path, roots, args.package_id)
            errors.extend(asset_errors)
            warnings.extend(asset_warnings)
            checked_assets.add(localized_path)
        checked_pairs.add(pair)
        pair_identity = containing_package_identity(english, roots, args.package_id)
        pair_errors, pair_warnings = check_pair(*pair, allowed_terms, pair_identity)
        errors.extend(pair_errors)
        warnings.extend(pair_warnings)

    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    if errors:
        print("ALPS Markdown representation validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"ALPS Markdown representation validation: OK ({len(paths)} assets, {len(checked_pairs)} pairs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
