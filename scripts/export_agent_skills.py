#!/usr/bin/env python3
"""Export self-contained ALPS Agent Skills for clients that upload Skills individually."""

from __future__ import annotations

import argparse
import os
import re
import shutil
from pathlib import Path

SKILL_NAMES = ("define-alps", "apply-alps", "manage-alps")
TARGETS = ("chatgpt",)
REPOSITORY_SPEC_LINK = re.compile(r"(?P<path>(?:\.\./)+\.alps/spec/(?P<suffix>[^)\s>'\"]+))")


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def rewrite_repository_spec_links(skill_root: Path) -> None:
    bundled_spec_root = skill_root / "references" / "alps" / "spec"

    for path in skill_root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")

        def replacement(match: re.Match[str]) -> str:
            destination = bundled_spec_root / match.group("suffix")
            return os.path.relpath(destination, path.parent).replace(os.sep, "/")

        rewritten = REPOSITORY_SPEC_LINK.sub(replacement, text)
        if rewritten != text:
            path.write_text(rewritten, encoding="utf-8")


def verify_export(skill_root: Path) -> None:
    skill_file = skill_root / "SKILL.md"
    if not skill_file.is_file():
        raise RuntimeError(f"missing authoritative Skill Description: {skill_file}")

    bundled_spec = skill_root / "references" / "alps" / "spec"
    if not bundled_spec.is_dir():
        raise RuntimeError(f"missing bundled ALPS specification: {bundled_spec}")

    unresolved = []
    for path in skill_root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        if REPOSITORY_SPEC_LINK.search(text):
            unresolved.append(path.relative_to(skill_root).as_posix())

    if unresolved:
        joined = ", ".join(unresolved)
        raise RuntimeError(f"repository-escaping ALPS spec links remain in: {joined}")


def export_skill(root: Path, skill_name: str, output_root: Path) -> Path:
    source = root / "skills" / skill_name
    if not source.is_dir():
        raise RuntimeError(f"unknown Skill package: {source}")

    destination = output_root / skill_name
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)

    shared_spec = root / ".alps" / "spec"
    bundled_spec = destination / "references" / "alps" / "spec"
    bundled_spec.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(shared_spec, bundled_spec)

    rewrite_repository_spec_links(destination)
    verify_export(destination)
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export self-contained ALPS Agent Skills for an upload-oriented client."
    )
    parser.add_argument("--target", choices=TARGETS, default="chatgpt")
    parser.add_argument(
        "--skill",
        action="append",
        choices=SKILL_NAMES,
        dest="skills",
        help="Export only this Skill. Repeat to export multiple Skills.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory. Defaults to dist/<target> under the repository root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repository_root()
    output_root = (args.output or root / "dist" / args.target).resolve()
    selected = tuple(args.skills or SKILL_NAMES)
    output_root.mkdir(parents=True, exist_ok=True)

    for skill_name in selected:
        exported = export_skill(root, skill_name, output_root)
        print(exported)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
