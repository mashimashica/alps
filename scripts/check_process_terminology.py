#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TEXT_SUFFIXES = {".md", ".py", ".json", ".yml", ".yaml", ".txt"}
PATTERNS = [
    re.compile(r"\bskill[ -]?(?:model|view|instance|instantiation)s?\b", re.IGNORECASE),
    re.compile("alps-" + "skill-" + r"(?:model|view)", re.IGNORECASE),
    re.compile("Skill" + "の" + "Instance"),
    re.compile("Skill" + "インスタンス"),
    re.compile("スキル" + "モデル"),
    re.compile("スキル" + "ビュー"),
    re.compile("ALPS Reference " + "Process Model"),
    re.compile(r"\bSkills?\s+(?:is|are|was|were|be|being)\s+instantiated\b", re.IGNORECASE),
    re.compile(r"\binstantiat(?:e|ed|ing|ion)\s+(?:a\s+|an\s+|the\s+)?Skills?\b", re.IGNORECASE),
    re.compile("Skill" + "を" + "インスタンス化"),
    re.compile("Skill" + "を" + "Instantiation"),
]


def scan(root: Path) -> list[str]:
    findings: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeError:
            continue
        for number, line in enumerate(lines, 1):
            if any(pattern.search(line) for pattern in PATTERNS):
                findings.append(f"{path}:{number}:{line.strip()}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    findings = scan(args.root)
    if findings:
        print("Inconsistent process terminology found:", file=sys.stderr)
        for finding in findings:
            print(finding, file=sys.stderr)
        return 1
    print("Process terminology: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
