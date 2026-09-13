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

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.DOTALL | re.MULTILINE)
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")

# Links that leave their Skill directory, as (Skill, file within the Skill,
# link target). PR5 removes these links from design-agent-work-system and
# deletes this allowlist. design-process-description has no allowed entries.
ALLOWED_EXTERNAL_LINKS = {
    ("design-agent-work-system", "SKILL.md", "../design-process-description/SKILL.md"),
    ("design-agent-work-system", "SKILL.md", "../design-process-description/references/process-framework.md"),
    ("design-agent-work-system", "SKILL.md", "../design-process-description/references/SKILL-template.md"),
    ("design-agent-work-system", "SKILL.md", "../../examples/README.md"),
    ("design-agent-work-system", "references/examples.md", "../../design-process-description/references/SKILL-template.md"),
    ("design-agent-work-system", "references/examples.md", "../../../examples/README.md"),
    ("design-agent-work-system", "references/examples.md", "../../../examples/assess-service-change/SKILL.md"),
    ("design-agent-work-system", "references/examples.md", "../../../examples/assess-service-change/references/pilot-context.md"),
    ("design-agent-work-system", "references/locales/ja/SKILL.ja.md", "../../../../design-process-description/references/locales/ja/SKILL.ja.md"),
    ("design-agent-work-system", "references/locales/ja/SKILL.ja.md", "../../../../design-process-description/references/locales/ja/process-framework.md"),
    ("design-agent-work-system", "references/locales/ja/SKILL.ja.md", "../../../../design-process-description/references/locales/ja/SKILL-template.md"),
    ("design-agent-work-system", "references/locales/ja/SKILL.ja.md", "../../../../../examples/locales/ja/README.md"),
    ("design-agent-work-system", "references/locales/ja/examples.md", "../../../../design-process-description/references/locales/ja/SKILL-template.md"),
    ("design-agent-work-system", "references/locales/ja/examples.md", "../../../../../examples/locales/ja/README.md"),
    ("design-agent-work-system", "references/locales/ja/examples.md", "../../../../../examples/assess-service-change/references/locales/ja/SKILL.ja.md"),
    ("design-agent-work-system", "references/locales/ja/examples.md", "../../../../../examples/assess-service-change/references/locales/ja/pilot-context.md"),
}


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
    """Yield local Markdown link targets without anchors."""
    for match in LINK.finditer(FENCE.sub("", text)):
        target = match.group(1)
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
        self.assertEqual(found, expected)
        distributed = {entry.name for entry in (ROOT / "skills").iterdir() if entry.is_dir()}
        self.assertEqual(distributed, set(DISTRIBUTED_SKILLS))

    def test_distributed_skill_links_stay_within_skill(self) -> None:
        seen_allowed = set()
        for name in DISTRIBUTED_SKILLS:
            skill_directory = ROOT / "skills" / name
            for document in sorted(skill_directory.rglob("*.md")):
                relative_document = document.relative_to(skill_directory).as_posix()
                text = document.read_text(encoding="utf-8")
                for target in relative_links(text):
                    resolved = Path(os.path.normpath(document.parent / unquote(target)))
                    with self.subTest(skill=name, file=relative_document, link=target):
                        self.assertTrue(resolved.exists(), "link target does not exist")
                        inside = resolved == skill_directory or skill_directory in resolved.parents
                        key = (name, relative_document, target)
                        if not inside:
                            self.assertIn(
                                key,
                                ALLOWED_EXTERNAL_LINKS,
                                "link leaves the Skill directory",
                            )
                            seen_allowed.add(key)
        self.assertEqual(
            ALLOWED_EXTERNAL_LINKS - seen_allowed,
            set(),
            "remove allowlist entries whose links no longer exist",
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
