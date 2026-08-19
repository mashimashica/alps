#!/usr/bin/env python3
"""Mechanically preflight this Package's representative Markdown binding.

The YAML frontmatter, canonical headings, and name-format rules checked here are
binding-specific. The discovery-description suffix is an ALPS requirement. The
normative vocabulary is defined by the Process Framework and inherited by ALPS.
This checker reports structural signals; it does not establish ALPS conformance
or prove that a process outcome is achievable.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LOCALES = {
    "en": {
        "conformance_suffix": "ALPS-conformant.",
        "normative_markers": (
            "must ",
            "must not",
            "should ",
            "should not",
            "may ",
            "typically",
        ),
        "note": "Binding-specific mechanical preflight only; not an ALPS conformance determination.",
    },
    "ja": {
        "conformance_suffix": "ALPS準拠。",
        "normative_markers": (
            "必要がある",
            "てはならない",
            "のが望ましい",
            "てよい",
            "通常、",
        ),
        "note": "Binding固有の機械的事前検査に限られ、ALPS Conformanceの判定ではありません。",
    },
}


def frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    if not text.startswith("---\n"):
        return {}, ["YAML frontmatter must start on the first line"]
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, ["YAML frontmatter is not closed"]
    data: dict[str, str] = {}
    for number, line in enumerate(text[4:end].splitlines(), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            errors.append(f"frontmatter line {number} is not a scalar key/value")
            continue
        key, value = match.groups()
        data[key] = value.strip().strip('"').strip("'")
    return data, errors


def section(text: str, names: tuple[str, ...]) -> str | None:
    for name in names:
        match = re.search(
            rf"(?ms)^##\s+{re.escape(name)}\s*$\n(.*?)(?=^##\s+|\Z)", text
        )
        if match:
            return match.group(1)
    return None


def inspect(path: Path, locale: str = "en") -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    settings = LOCALES[locale]
    text = path.read_text(encoding="utf-8")
    meta, meta_errors = frontmatter(text)
    errors.extend(meta_errors)

    missing = {"name", "description"} - set(meta)
    if missing:
        errors.append("missing frontmatter keys: " + ", ".join(sorted(missing)))
    extras = set(meta) - {"name", "description"}
    if extras:
        warnings.append("non-standard frontmatter keys: " + ", ".join(sorted(extras)))

    name = meta.get("name", "")
    if name and (len(name) > 63 or not NAME_RE.fullmatch(name)):
        errors.append("name must be <=63 characters in lowercase hyphen-case")
    description = meta.get("description", "").strip()
    if not description:
        errors.append("description must state what the Skill does and when to use it")
    elif not description.endswith(settings["conformance_suffix"]):
        errors.append(
            f"description must end with {settings['conformance_suffix']!r}"
        )

    purpose = section(text, ("Purpose",))
    outcomes = section(text, ("Outcomes", "Outcome"))
    if purpose is None or not purpose.strip():
        errors.append("Purpose section is missing or empty")
    if outcomes is None or not outcomes.strip():
        errors.append("Outcomes section is missing or empty")

    activity_heading = re.search(
        r"(?m)^##\s+Activities(?:\s+(?:and|&)\s+Tasks)?\s*$",
        text,
    )
    if not activity_heading:
        warnings.append("Activity and Task section was not detected")
    else:
        activity_text = text[activity_heading.end() :]
        next_h2 = re.search(r"(?m)^##\s+", activity_text)
        if next_h2:
            activity_text = activity_text[: next_h2.start()]
        task_lines = [
            line.strip()
            for line in activity_text.splitlines()
            if re.match(r"^\s*(?:[-*]|\d+[.)])\s+", line)
        ]
        if not task_lines:
            warnings.append("no Task list items were detected")
        for line in task_lines:
            if not any(
                marker.lower() in line.lower()
                for marker in settings["normative_markers"]
            ):
                warnings.append(f"Task has no recognizable normative marker: {line[:100]}")

    local_links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    unresolved: list[str] = []
    for target in local_links:
        if "://" in target or target.startswith("#"):
            continue
        local_target = target.split("#", 1)[0]
        if local_target and not (path.parent / local_target).resolve().exists():
            unresolved.append(target)
    if unresolved:
        errors.append("unresolved local references: " + ", ".join(unresolved))

    return {
        "path": str(path),
        "status": "fail" if errors else "pass",
        "errors": errors,
        "warnings": warnings,
        "note": settings["note"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill_md", type=Path)
    parser.add_argument("--locale", choices=tuple(LOCALES), default="en")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    if not args.skill_md.is_file():
        parser.error(f"not a file: {args.skill_md}")
    result = inspect(args.skill_md.resolve(), args.locale)
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = (
            "合格" if result["status"] == "pass" else "不合格"
        ) if args.locale == "ja" else result["status"].upper()
        error_label = "エラー" if args.locale == "ja" else "ERROR"
        warning_label = "警告" if args.locale == "ja" else "WARNING"
        print(f"{status}: {result['path']}")
        for error in result["errors"]:
            print(f"{error_label}: {error}")
        for warning in result["warnings"]:
            print(f"{warning_label}: {warning}")
        print(result["note"])
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
