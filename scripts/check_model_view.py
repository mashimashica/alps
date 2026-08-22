#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

BINDING = "alps-markdown-agent-plugins/1.0"
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
RANGE_TOKEN_RE = re.compile(r"^(?:>=|<=|==|=|>|<)\d+\.\d+\.\d+$")
STATUS = {"draft", "active", "deprecated", "retired"}
MODEL_KINDS = {"process-model", "process-reference-model"}
TREATMENTS = {"selected", "adapted", "new"}
MODEL_SECTIONS = ["Purpose", "Scope", "Included Processes", "Relationships", "Selection and Application", "Compatibility", "Management"]
VIEW_SECTIONS = ["Purpose", "Outcomes", "Stakeholders and Concerns", "Source Models", "Included Activities and Tasks", "Handoffs", "Application Guidance", "Compatibility and Conformance"]

class CheckError(Exception):
    pass

def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise CheckError("missing opening YAML frontmatter delimiter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise CheckError("missing closing YAML frontmatter delimiter")
    front: dict[str, str] = {}
    for number, raw in enumerate(text[4:end].splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise CheckError(f"frontmatter line {number} is not key: value")
        key, value = line.split(":", 1)
        key = key.strip(); value = value.strip().strip('"').strip("'")
        if not key or not value:
            raise CheckError(f"frontmatter line {number} has an empty key or value")
        if key in front:
            raise CheckError(f"duplicate frontmatter key: {key}")
        front[key] = value
    return front, text[end + 5:]

def sections(body: str) -> set[str]:
    return {m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", body, flags=re.MULTILINE)}

def section_body(body: str, heading: str) -> str:
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$\n(.*?)(?=^##\s+|\Z)", body, flags=re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else ""

def parse_table(text: str) -> tuple[list[str], list[list[str]]]:
    lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        raise CheckError("required Markdown table is missing")
    headers = [c.strip() for c in lines[0].strip("|").split("|")]
    separator = [c.strip() for c in lines[1].strip("|").split("|")]
    if len(headers) != len(separator) or not all(set(c) <= {"-", ":"} for c in separator):
        raise CheckError("Markdown table separator is invalid")
    rows = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != len(headers):
            raise CheckError("Markdown table row has a different number of cells")
        rows.append(cells)
    return headers, rows

def expected_path(path: Path, kind: str, asset_id: str, default: str | None) -> None:
    posix = path.as_posix()
    if kind in MODEL_KINDS:
        if posix.endswith("/.alps/MODEL.md") or posix == ".alps/MODEL.md":
            if default != "true":
                raise CheckError("the default .alps/MODEL.md must declare default: true")
        elif not re.search(rf"/?\.alps/models/{re.escape(asset_id)}/MODEL\.md$", posix):
            raise CheckError("named MODEL.md path does not match its id")
    elif not re.search(rf"/?\.alps/views/{re.escape(asset_id)}/VIEW\.md$", posix):
        raise CheckError("VIEW.md path does not match its id")

def check(path: Path) -> list[str]:
    try:
        front, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        required = {"kind", "id", "name", "version", "status", "binding", "alps-requires", "authoritative-language"}
        missing = sorted(required - front.keys())
        if missing: raise CheckError("missing frontmatter keys: " + ", ".join(missing))
        kind = front["kind"]
        if kind not in MODEL_KINDS | {"process-view"}: raise CheckError(f"unsupported kind: {kind}")
        if not ID_RE.fullmatch(front["id"]): raise CheckError("id must be lowercase kebab-case")
        if not SEMVER_RE.fullmatch(front["version"]): raise CheckError("version must be a semantic version")
        if front["status"] not in STATUS: raise CheckError("invalid status")
        if front["binding"] != BINDING: raise CheckError(f"binding must be {BINDING}")
        tokens = front["alps-requires"].split()
        if not tokens or not all(RANGE_TOKEN_RE.fullmatch(t) for t in tokens): raise CheckError("invalid alps-requires")
        expected_path(path, kind, front["id"], front.get("default"))
        heading = re.search(r"^#\s+(.+?)\s*$", body, flags=re.MULTILINE)
        if not heading or heading.group(1).strip() != front["name"]: raise CheckError("level-one heading must equal frontmatter name")
        needed = MODEL_SECTIONS if kind in MODEL_KINDS else VIEW_SECTIONS
        absent = [name for name in needed if name not in sections(body)]
        if absent: raise CheckError("missing sections: " + ", ".join(absent))
        if kind in MODEL_KINDS:
            headers, rows = parse_table(section_body(body, "Included Processes"))
            expected = ["Process ID", "Process Name", "Skill ID", "Skill Source", "Version or Resolution", "Status", "Role"]
            if headers != expected: raise CheckError(f"Included Processes headers must be {expected}")
            seen = set()
            for row in rows:
                process_id, _, skill_id, source, _, status, _ = row
                if not ID_RE.fullmatch(process_id): raise CheckError(f"invalid Process ID: {process_id}")
                if process_id in seen: raise CheckError(f"duplicate Process ID: {process_id}")
                seen.add(process_id)
                if not ID_RE.fullmatch(skill_id): raise CheckError(f"invalid Skill ID: {skill_id}")
                if not source.startswith(("local:", "plugin:", "uri:")): raise CheckError(f"invalid Skill Source: {source}")
                if status not in {"adopted", "candidate", "deprecated", "retired"}: raise CheckError(f"invalid status: {status}")
            rel, _ = parse_table(section_body(body, "Relationships"))
            expected_rel = ["Provider Process", "Output", "Recipient Process", "Input", "Conditions"]
            if rel != expected_rel: raise CheckError(f"Relationships headers must be {expected_rel}")
        else:
            if not front.get("source-models"): raise CheckError("a Process View must declare source-models")
            headers, rows = parse_table(section_body(body, "Included Activities and Tasks"))
            expected = ["View Element ID", "Origin", "Source Process", "Source Element", "Treatment", "Guidance"]
            if headers != expected: raise CheckError(f"Included Activities and Tasks headers must be {expected}")
            for row in rows:
                element_id, _, source_process, source_element, treatment, _ = row
                if not ID_RE.fullmatch(element_id): raise CheckError(f"invalid View Element ID: {element_id}")
                if treatment not in TREATMENTS: raise CheckError(f"invalid treatment: {treatment}")
                if treatment in {"selected", "adapted"} and (not source_process or source_process == "—" or not source_element):
                    raise CheckError(f"{treatment} element {element_id} must identify its source")
            rel, _ = parse_table(section_body(body, "Handoffs"))
            expected_rel = ["Provider Process", "Output", "Recipient Process", "Input", "Conditions"]
            if rel != expected_rel: raise CheckError(f"Handoffs headers must be {expected_rel}")
        return []
    except (OSError, UnicodeError, CheckError) as exc:
        return [str(exc)]

def discover(root: Path) -> list[Path]:
    paths = []
    if (root / ".alps/MODEL.md").is_file(): paths.append(root / ".alps/MODEL.md")
    paths.extend(sorted((root / ".alps/models").glob("*/MODEL.md")))
    paths.extend(sorted((root / ".alps/views").glob("*/VIEW.md")))
    return paths

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("paths", nargs="*", type=Path); parser.add_argument("--root", type=Path, default=Path(".")); args = parser.parse_args()
    paths = args.paths or discover(args.root)
    if not paths: print("No MODEL.md or VIEW.md assets found.", file=sys.stderr); return 1
    failed = False
    for path in paths:
        errors = check(path)
        if errors:
            failed = True
            for error in errors: print(f"{path}: {error}", file=sys.stderr)
        else: print(f"{path}: OK")
    return 1 if failed else 0

if __name__ == "__main__": raise SystemExit(main())
