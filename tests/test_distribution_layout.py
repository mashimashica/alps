"""Keep distributed Skills self-contained and the repository layout stable."""

import os
import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
SKIPPED_DIRECTORIES = {".git", ".claude", "node_modules"}
DISTRIBUTED_SKILLS = ("design-process-description", "design-agent-work-system")
DEVELOPMENT_SKILLS = ("review-alps", "sync-locales")
EXAMPLE_SKILLS = ("examples/assess-service-change",)
# A converted third-party Plugin tree kept as reference material. Its Skill
# entry points sit only where that Plugin places them.
EXAMPLE_PLUGIN_TREES = {
    "examples/pstack": ("skills", "automations/benny/skills"),
}

LINK_PATTERNS = (
    re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)"),
    re.compile(r"^\s*\[[^\]]+\]:\s*<?(\S+?)>?(?:\s|$)", re.MULTILINE),
    re.compile(r"\b(?:src|href)\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE),
)
FENCE = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.DOTALL | re.MULTILINE)
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def walk_files(name: str):
    """Yield repository files with the given name without following symlinks."""
    for directory, subdirectories, files in os.walk(ROOT, followlinks=False):
        subdirectories[:] = [
            entry for entry in subdirectories if entry not in SKIPPED_DIRECTORIES
        ]
        for file_name in files:
            if file_name == name:
                yield Path(directory, file_name)


def relative_links(text: str):
    """Yield local inline, reference-style, and HTML link targets without anchors."""
    text = FENCE.sub("", text)
    for pattern in LINK_PATTERNS:
        for match in pattern.finditer(text):
            target = match.group(1).strip().strip("<>")
            if SCHEME.match(target) or target.startswith("#"):
                continue
            path = target.split("#", 1)[0]
            if path:
                yield path


class DistributionLayoutTests(unittest.TestCase):
    def test_skill_entry_points(self) -> None:
        found = {path.relative_to(ROOT).as_posix() for path in walk_files("SKILL.md")}
        expected = {f"skills/{name}/SKILL.md" for name in DISTRIBUTED_SKILLS}
        expected |= {f".agents/skills/{name}/SKILL.md" for name in DEVELOPMENT_SKILLS}
        expected |= {f"{path}/SKILL.md" for path in EXAMPLE_SKILLS}
        for tree, skill_roots in EXAMPLE_PLUGIN_TREES.items():
            in_tree = {path for path in found if path.startswith(f"{tree}/")}
            found -= in_tree
            with self.subTest(example_plugin_tree=tree):
                self.assertTrue(in_tree, "example Plugin tree has no Skill")
            for path in sorted(in_tree):
                skill_directory = Path(path).parent
                with self.subTest(example_plugin_tree=tree, skill=path):
                    self.assertIn(
                        skill_directory.parent.as_posix(),
                        {f"{tree}/{root}" for root in skill_roots},
                        "Skill entry point outside the tree's Skill roots",
                    )
        self.assertEqual(found, expected)
        distributed = {entry.name for entry in (ROOT / "skills").iterdir() if entry.is_dir()}
        self.assertEqual(distributed, set(DISTRIBUTED_SKILLS))

    def test_distributed_skill_links_stay_within_skill(self) -> None:
        for name in DISTRIBUTED_SKILLS:
            skill_directory = ROOT / "skills" / name
            for document in sorted(skill_directory.rglob("*.md")):
                relative_document = document.relative_to(skill_directory).as_posix()
                text = document.read_text(encoding="utf-8")
                for target in relative_links(text):
                    resolved = Path(os.path.normpath(document.parent / unquote(target)))
                    with self.subTest(skill=name, file=relative_document, link=target):
                        self.assertTrue(resolved.exists(), "link target does not exist")
                        self.assertTrue(
                            resolved == skill_directory or skill_directory in resolved.parents,
                            "link leaves the Skill directory",
                        )

    def test_repository_skill_discovery_view(self) -> None:
        skills_view = ROOT / ".agents" / "skills"
        for name in DISTRIBUTED_SKILLS:
            with self.subTest(skill=name):
                path = skills_view / name
                self.assertTrue(path.is_symlink())
                self.assertEqual(os.readlink(path), f"../../skills/{name}")
                self.assertEqual(path.resolve(), (ROOT / "skills" / name).resolve())
        for name in DEVELOPMENT_SKILLS:
            with self.subTest(skill=name):
                path = skills_view / name
                self.assertFalse(path.is_symlink())
                self.assertTrue(path.is_dir())


if __name__ == "__main__":
    unittest.main()
