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
from typing import Iterable
from urllib.parse import unquote, urlsplit


SUPPORTED_KINDS = {
    "process",
    "process-model",
    "process-reference-model",
    "process-view",
}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILL_REF = re.compile(r"skill:(?P<package>[^#\s]*)#(?P<skill>[a-z0-9][a-z0-9-]*)")
SKILL_TOKEN = re.compile(r'''skill:[^\s`<>()\[\]{}"',;!?]*''')
MARKDOWN_INLINE_LINK = re.compile(
    r"!?\[[^\]\n]*\]\((?P<target><[^>\n]+>|[^)\n]+)\)"
)
MARKDOWN_REFERENCE_LINK = re.compile(
    r"(?m)^\s{0,3}\[[^\]\n]+\]:\s*(?P<target><[^>\n]+>|\S+)"
)
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


def locale_for(path: Path) -> str:
    parts = path.as_posix().split("/")
    for index in range(len(parts) - 2):
        if parts[index : index + 3] == ["references", "locales", "ja"]:
            return "ja"
    return "en"


def frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    if not text.startswith("---\n"):
        return {}, ["YAML frontmatter must start on the first line"]
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, ["YAML frontmatter is not closed"]

    values: dict[str, str] = {}
    errors: list[str] = []
    in_metadata = False
    for number, raw in enumerate(text[4:end].splitlines(), start=2):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw == "metadata:":
            in_metadata = True
            continue
        if raw and not raw.startswith((" ", "\t")):
            in_metadata = False
        scalar = re.match(r"^([A-Za-z0-9_.-]+):\s*(.*?)\s*$", raw)
        nested = re.match(r"^\s+([A-Za-z0-9_.-]+):\s*(.*?)\s*$", raw)
        match = nested if in_metadata else scalar
        if not match:
            # Block scalars and unrelated nested binding metadata are outside
            # the fields inspected here.
            if raw.lstrip().startswith(("- ", "|", ">")) or raw.startswith((" ", "\t")):
                continue
            errors.append(f"frontmatter line {number} is not a key/value")
            continue
        key, value = match.groups()
        if in_metadata:
            key = f"metadata.{key}"
        values[key] = value.strip().strip('"').strip("'")
    if "metadata.alps.kind" in values:
        values["alps.kind"] = values["metadata.alps.kind"]
    return values, errors


def heading1(text: str) -> str | None:
    match = re.search(r"(?m)^# ([^\n]+?)\s*$", text)
    return match.group(1).strip() if match else None


def section(text: str, heading: str, level: int = 2) -> str | None:
    marker = "#" * level + " " + heading
    pattern = re.compile(rf"(?ms)^{re.escape(marker)}\s*$\n(.*?)(?=^#{{1,{level}}}\s|\Z)")
    match = pattern.search(text)
    return match.group(1).strip() if match else None


def normalized_lines(value: str) -> list[str]:
    return [re.sub(r"\s+", " ", line.strip()) for line in value.splitlines() if line.strip()]


def prose_paragraphs(value: str) -> list[str]:
    return [re.sub(r"\s+", " ", block.strip()) for block in re.split(r"\n\s*\n", value) if block.strip()]


def table(text: str) -> tuple[list[str], list[list[str]]]:
    lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|") and line.strip().endswith("|")]
    for index in range(1, len(lines)):
        separators = [cell.strip() for cell in lines[index].strip("|").split("|")]
        if separators and all(re.fullmatch(r":?-{3,}:?", cell) for cell in separators):
            header = [cell.strip() for cell in lines[index - 1].strip("|").split("|")]
            rows = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines[index + 1 :]]
            return header, rows
    return [], []


def outcome_items(value: str | None) -> list[str]:
    """Return semantic Outcome units without prescribing Markdown markers."""

    if not value or not value.strip():
        return []
    lines = normalized_lines(value)
    marked = [line for line in lines if re.match(r"^(?:[-*+]\s+|\d+[.)]\s+|[a-z][.)]\s+)", line, re.I)]
    if marked:
        values: list[str] = []
        for line in marked:
            line = re.sub(r"^(?:[-*+]\s+|\d+[.)]\s+)", "", line)
            line = re.sub(r"^[a-z][.)]\s+", "", line, flags=re.I)
            values.append(re.sub(r"\s+", " ", line).strip())
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
    meta, _ = frontmatter(path.read_text(encoding="utf-8"))
    return meta.get("alps.kind", "process")


def reference_tokens(text: str) -> list[str]:
    return [match.group(0).rstrip(".:") for match in SKILL_TOKEN.finditer(text)]


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


def markdown_link_targets(text: str) -> list[str]:
    """Return inline and reference-definition Markdown link destinations."""

    targets = [match.group("target") for match in MARKDOWN_INLINE_LINK.finditer(text)]
    targets.extend(match.group("target") for match in MARKDOWN_REFERENCE_LINK.finditer(text))
    return targets


def containing_package_root(path: Path, roots: dict[str, Path]) -> Path | None:
    """Return the most specific declared package root containing path."""

    resolved_path = path.resolve()
    candidates = {
        root.resolve()
        for root in roots.values()
        if resolved_path.is_relative_to(root.resolve())
    }
    return max(candidates, key=lambda root: len(root.parts)) if candidates else None


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
        if not target or target.startswith(("#", "/", "//")):
            continue
        parsed = urlsplit(target)
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


def resolve_skill(reference: str, roots: dict[str, Path], locale: str = "en") -> ResolvedSkill:
    match = SKILL_REF.fullmatch(reference)
    if not match:
        raise ValueError(f"invalid canonical Skill reference: {reference}")
    package = match.group("package")
    if package not in roots:
        raise ValueError(f"unresolved package identity {package!r} in {reference}")
    root = roots[package]
    path = root / "skills" / match.group("skill") / "SKILL.md"
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
    matches = list(re.finditer(r"(?m)^### ([^\n]+?)\s*$", activity_text))
    activities: list[str] = []
    tasks: list[tuple[str, ...]] = []
    for index, match in enumerate(matches):
        activities.append(match.group(1).strip())
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(activity_text)
        block = activity_text[start:end]
        task_values = tuple(
            item.group(1).strip()
            for item in re.finditer(r"(?m)^\s*(?:\d+[.)]|[-*+])\s+(.+?)\s*$", block)
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


def check_process_model(path: Path, text: str, locale: str, roots: dict[str, Path]) -> list[str]:
    errors = required_sections(path, text, "Process Model", locale, ("purpose", "processes", "relationships"))
    for reference in references(section(text, HEADINGS[locale]["processes"]) or ""):
        try:
            target = resolve_skill(reference, roots, locale)
        except ValueError as exc:
            errors.append(f"{path}: {exc}")
            continue
        if representation_kind(target.path) != "process":
            errors.append(f"{path}: {reference} does not resolve to a Process representation")
    return errors


def process_blocks(value: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"(?ms)^### ([^\n]+?)\s*$\n(.*?)(?=^### |\Z)", value))
    return [(match.group(1).strip(), match.group(2)) for match in matches]


def check_reference_model(path: Path, text: str, locale: str, roots: dict[str, Path]) -> list[str]:
    errors = required_sections(
        path, text, "Process Reference Model", locale, ("purpose", "processes", "relationships")
    )
    processes = section(text, HEADINGS[locale]["processes"]) or ""
    blocks = process_blocks(processes)
    if not blocks:
        return errors + [f"{path}: no Process entries found"]

    for model_name, body in blocks:
        purpose = section(body, HEADINGS[locale]["purpose"], 4)
        outcomes = section(body, HEADINGS[locale]["outcomes"], 4)
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
            target = resolve_skill(refs[0], roots, locale)
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


def source_identity(value: str) -> str:
    value = re.sub(r"`?skill:[^\s`]+`?", "", value)
    value = re.sub(r"[（(][^()（）]*[）)]", "", value)
    return re.sub(r"\s+", " ", value).strip(" |-:")


def source_process_keys(value: str) -> set[str]:
    """Return one identity key per declared Source Process.

    A displayed Process name and the canonical reference in the same table row
    identify one source, not two independent sources.
    """

    _, rows = table(value)
    keys: set[str] = set()
    if rows:
        for row in rows:
            row_text = " ".join(row)
            refs = references(row_text)
            if refs:
                keys.add(f"ref:{refs[0]}")
            elif row and source_identity(row[0]):
                keys.add(f"name:{source_identity(row[0])}")
        return keys
    ordered: list[str] = []
    pending_name_index: int | None = None
    for entry in source_entries(value):
        refs = references(entry)
        if refs:
            key = f"ref:{refs[0]}"
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
            ordered.append(f"name:{source_identity(entry)}")
            pending_name_index = len(ordered) - 1
    return set(ordered)


def check_view(path: Path, text: str, locale: str, roots: dict[str, Path]) -> tuple[list[str], list[str]]:
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
    source_values = source_entries(source_text)
    if len(source_process_keys(source_text)) < 2:
        errors.append(f"{path}: Process View requires at least two distinct Source Processes")
    for reference in references(source_text):
        try:
            target = resolve_skill(reference, roots, locale)
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
        known = {source_identity(value) for value in source_values}
        for row_number, row in enumerate(rows, start=1):
            if len(row) < 2 or not row[0] or not row[1]:
                errors.append(f"{path}: provenance row {row_number} must identify Source Process and source element")
                continue
            row_source = source_identity(row[0])
            if known and row_source not in known:
                errors.append(f"{path}: provenance row {row_number} names an undeclared Source Process: {row[0]}")
    elif re.search(r"(?im)\b(?:Activity|Task)\b|活動|タスク", included):
        warnings.append(f"{path}: source-element provenance could not be established mechanically")
    return errors, warnings


def check_asset(path: Path, roots: dict[str, Path]) -> tuple[list[str], list[str]]:
    text = path.read_text(encoding="utf-8")
    locale = locale_for(path)
    errors = check_frontmatter(path, text)
    errors.extend(reference_syntax_errors(path, text))
    package_root = containing_package_root(path, roots)
    if package_root is None:
        errors.append(f"{path}: representation is outside the declared package roots")
    else:
        errors.extend(local_link_errors(path, text, package_root))
    warnings: list[str] = []
    if not heading1(text):
        errors.append(f"{path}: representation requires Name as a level-one heading")
    meta, _ = frontmatter(text)
    kind = meta.get("alps.kind", "process")
    if kind not in SUPPORTED_KINDS:
        return errors, warnings
    if kind == "process":
        more_errors, more_warnings = semantic_process_findings(path, text, locale)
        return errors + more_errors, warnings + more_warnings
    if kind == "process-model":
        return errors + check_process_model(path, text, locale, roots), warnings
    if kind == "process-reference-model":
        return errors + check_reference_model(path, text, locale, roots), warnings
    more_errors, more_warnings = check_view(path, text, locale, roots)
    return errors + more_errors, warnings + more_warnings


def japanese_prose_lines(text: str) -> Iterable[tuple[int, str]]:
    in_frontmatter = False
    description_indent: int | None = None
    in_fence = False
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
                    yield number, original
                    continue
                description_indent = None
            description = re.match(r"^(\s*)description:\s*(.*)$", original)
            if description:
                indent_text, value = description.groups()
                if re.fullmatch(r"[>|](?:[+-]?[1-9]?|[1-9][+-]?)", value.strip()):
                    description_indent = len(indent_text)
                else:
                    yield number, value
            continue
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not stripped or stripped.startswith("<!--"):
            continue
        yield number, original


def raw_english_words(line: str, allowed_terms: set[str]) -> list[str]:
    for term in sorted(allowed_terms, key=len, reverse=True):
        line = line.replace(term, "")
    line = re.sub(r"`[^`]*`", "", line)
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


def japanese_naturalness_errors(path: Path, text: str, allowed_terms: set[str]) -> list[str]:
    errors: list[str] = []
    for number, line in japanese_prose_lines(text):
        for word in raw_english_words(line, allowed_terms):
            errors.append(f"{path}:{number}: untranslated English in Japanese prose: {word}")
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
        en_processes = table(section(en_text, HEADINGS["en"]["processes"]) or "")[1]
        ja_processes = table(section(ja_text, HEADINGS["ja"]["processes"]) or "")[1]
        en_relationships = table(section(en_text, HEADINGS["en"]["relationships"]) or "")[1]
        ja_relationships = table(section(ja_text, HEADINGS["ja"]["relationships"]) or "")[1]
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
        return errors, warnings
    if en_kind == "process-reference-model":
        en_processes = process_blocks(section(en_text, HEADINGS["en"]["processes"]) or "")
        ja_processes = process_blocks(section(ja_text, HEADINGS["ja"]["processes"]) or "")
        en_relationships = table(section(en_text, HEADINGS["en"]["relationships"]) or "")[1]
        ja_relationships = table(section(ja_text, HEADINGS["ja"]["relationships"]) or "")[1]
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
        return errors, warnings
    if en_kind == "process-view":
        en_outcomes = outcome_items(section(en_text, HEADINGS["en"]["outcomes"]))
        ja_outcomes = outcome_items(section(ja_text, HEADINGS["ja"]["outcomes"]))
        en_sources = source_entries(section(en_text, HEADINGS["en"]["sources"]) or "")
        ja_sources = source_entries(section(ja_text, HEADINGS["ja"]["sources"]) or "")
        en_included = table(section(en_text, HEADINGS["en"]["included"]) or "")[1]
        ja_included = table(section(ja_text, HEADINGS["ja"]["included"]) or "")[1]
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
            if en_force and ja_force and en_force != ja_force:
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
            asset_errors, asset_warnings = check_asset(path, roots)
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
            asset_errors, asset_warnings = check_asset(localized_path, roots)
            errors.extend(asset_errors)
            warnings.extend(asset_warnings)
            checked_assets.add(localized_path)
        checked_pairs.add(pair)
        pair_errors, pair_warnings = check_pair(*pair, allowed_terms, args.package_id)
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
