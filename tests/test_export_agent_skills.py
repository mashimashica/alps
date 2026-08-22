from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "export_agent_skills.py"
SPEC = importlib.util.spec_from_file_location("export_agent_skills", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
export_agent_skills = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_agent_skills)


class ExportAgentSkillsTest(unittest.TestCase):
    def test_exports_self_contained_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_root = Path(temporary_directory)
            exported = export_agent_skills.export_skill(
                ROOT, "apply-alps", output_root
            )

            self.assertTrue((exported / "SKILL.md").is_file())
            self.assertTrue(
                (exported / "references" / "alps" / "spec" / "ALPS-SPEC.md").is_file()
            )
            self.assertTrue(
                (
                    exported
                    / "references"
                    / "alps"
                    / "spec"
                    / "process-framework.md"
                ).is_file()
            )

            for markdown_file in exported.rglob("*.md"):
                contents = markdown_file.read_text(encoding="utf-8")
                self.assertIsNone(
                    export_agent_skills.REPOSITORY_SPEC_LINK.search(contents),
                    markdown_file.relative_to(exported).as_posix(),
                )

    def test_source_skill_is_not_modified(self) -> None:
        source = ROOT / "skills" / "define-alps" / "SKILL.md"
        before = source.read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory() as temporary_directory:
            export_agent_skills.export_skill(
                ROOT, "define-alps", Path(temporary_directory)
            )

        self.assertEqual(before, source.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
