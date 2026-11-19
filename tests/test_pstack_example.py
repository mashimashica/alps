"""Check the form of the converted pstack example tree.

These checks cover file form only: Skill frontmatter, the Markdown presentation
of Process Descriptions, and link containment. They do not establish that a
description is a valid account of its work or that it preserves its source.
"""

import os
import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
TREE = ROOT / "examples" / "pstack"
SKILL_ROOTS = ("skills", "automations/benny/skills")
PLAYBOOKS = "skills/poteto-mode/playbooks"
# The reviewing agent's definition describes work with results of its own. The
# bootstrapping agent's definition configures a delegate and stays as upstream wrote it.
AGENT_PROCESS_DESCRIPTIONS = ("agents/comment-sicko.md",)
# A reference that prescribes work with a result of its own.
REFERENCE_PROCESS_DESCRIPTIONS = (
    "automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md",
)
# Tools in the tree install their dependencies beside themselves on first use.
SKIPPED_DIRECTORIES = {"node_modules"}

SPEC_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
# The source Plugin's Hosts act on these fields; the conversion keeps them.
HOST_SKILL_FIELDS = {"disable-model-invocation", "icon", "color", "paths"}
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
FENCE = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.DOTALL | re.MULTILINE)
LINK_PATTERNS = (
    re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)"),
    re.compile(r"^\s*\[[^\]]+\]:\s*<?(\S+?)>?(?:\s|$)", re.MULTILINE),
    re.compile(r"\b(?:src|href)\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE),
)
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def frontmatter_fields(text: str) -> dict:
    """Return top-level frontmatter keys with their first-line scalar values."""
    match = FRONTMATTER.match(text)
    if not match:
        return {}
    fields = {}
    for line in match.group(1).splitlines():
        entry = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if entry:
            fields[entry.group(1)] = entry.group(2).strip().strip("\"'")
    return fields


def body_of(text: str) -> str:
    """Return the Markdown body without frontmatter or fenced code."""
    match = FRONTMATTER.match(text)
    body = text[match.end():] if match else text
    return FENCE.sub("", body)


def section(body: str, heading: str) -> str | None:
    """Return the text of a level-two section, or None when it is absent."""
    match = re.search(
        rf"^## {re.escape(heading)}[ \t]*\n(.*?)(?=^## |\Z)",
        body,
        re.DOTALL | re.MULTILINE,
    )
    return match.group(1) if match else None


def skill_files():
    for root in SKILL_ROOTS:
        yield from sorted((TREE / root).glob("*/SKILL.md"))


def process_descriptions():
    """Yield every file whose body the conversion presents as a Process Description."""
    yield from skill_files()
    yield from sorted((TREE / PLAYBOOKS).glob("*.md"))
    yield from (TREE / path for path in AGENT_PROCESS_DESCRIPTIONS)
    yield from (TREE / path for path in REFERENCE_PROCESS_DESCRIPTIONS)


class PstackExampleFormTests(unittest.TestCase):
    def test_skill_frontmatter(self) -> None:
        skills = list(skill_files())
        self.assertTrue(skills)
        for path in skills:
            relative = path.relative_to(TREE).as_posix()
            fields = frontmatter_fields(path.read_text(encoding="utf-8"))
            with self.subTest(skill=relative):
                self.assertEqual(fields.get("name"), path.parent.name)
                self.assertRegex(fields.get("name", ""), NAME)
                self.assertIn("description", fields)
                self.assertEqual(
                    set(fields) - SPEC_FIELDS - HOST_SKILL_FIELDS,
                    set(),
                    "frontmatter field outside the Agent Skills format and "
                    "the retained Host fields",
                )

    def test_process_description_presentation(self) -> None:
        documents = list(process_descriptions())
        self.assertTrue(documents)
        for path in documents:
            relative = path.relative_to(TREE).as_posix()
            body = body_of(path.read_text(encoding="utf-8"))
            with self.subTest(document=relative):
                titles = re.findall(r"^# \S.*$", body, re.MULTILINE)
                self.assertEqual(len(titles), 1, "expected one title for Name")
                purpose = section(body, "Purpose")
                self.assertTrue(purpose and purpose.strip(), "missing Purpose")
                outcomes = section(body, "Outcomes")
                self.assertIsNotNone(outcomes, "missing Outcomes")
                self.assertTrue(
                    re.search(r"^- \S", outcomes or "", re.MULTILINE),
                    "Outcomes needs one or more list items",
                )
                empty = [
                    heading
                    for heading, following in re.findall(
                        r"^(#{2,6} [^\n]+)\n(?:[ \t]*\n)*(?=(#{1,6}) |\Z)",
                        body,
                        re.MULTILINE,
                    )
                    if not following
                    or len(following) <= len(heading) - len(heading.lstrip("#"))
                ]
                self.assertEqual(empty, [], "section without content")

    def test_links_resolve_within_tree(self) -> None:
        for document in sorted(TREE.rglob("*.md")):
            if SKIPPED_DIRECTORIES.intersection(document.relative_to(TREE).parts):
                continue
            relative = document.relative_to(TREE).as_posix()
            text = FENCE.sub("", document.read_text(encoding="utf-8"))
            for pattern in LINK_PATTERNS:
                for match in pattern.finditer(text):
                    target = match.group(1).strip().strip("<>")
                    if SCHEME.match(target) or target.startswith("#"):
                        continue
                    path = target.split("#", 1)[0]
                    if not path:
                        continue
                    resolved = Path(os.path.normpath(document.parent / unquote(path)))
                    with self.subTest(file=relative, link=target):
                        self.assertTrue(resolved.exists(), "link target does not exist")
                        self.assertTrue(
                            resolved == TREE or TREE in resolved.parents,
                            "link leaves the example tree",
                        )


if __name__ == "__main__":
    unittest.main()
