"""Repository-only integrity checks that do not interpret ALPS meaning."""

from __future__ import annotations

import json
import os
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
DISTRIBUTED_SKILLS = (
    "alps-reference-model",
    "apply-alps",
    "define-alps",
    "manage-alps",
)
PLUGIN_MANIFESTS = (
    ROOT / "plugin.json",
    ROOT / ".claude-plugin/plugin.json",
    ROOT / ".cursor-plugin/plugin.json",
    ROOT / ".codex-plugin/plugin.json",
)
REPOSITORY_SKILLS = ("review-alps", "sync-locales")
REQUIRED_PATHS = (
    ROOT / "AGENTS.md",
    ROOT / "docs/locales/ja/AGENTS.md",
    ROOT / "README.md",
    ROOT / "docs/locales/ja/README.md",
    ROOT / "localization.yaml",
    ROOT / "spec/process-framework.md",
    ROOT / "spec/locales/ja/process-framework.md",
    ROOT / "spec/ALPS-SPEC.md",
    ROOT / "spec/locales/ja/ALPS-SPEC.md",
    ROOT / "skills/apply-alps/scripts/process_instance_record.py",
    ROOT / "skills/apply-alps/references/process-instance-record.md",
    ROOT / "skills/apply-alps/references/locales/ja/process-instance-record.md",
)
ICON_PATTERN = re.compile(
    r'^\s*icon_(?:small|large):\s*["\']?([^"\'\s]+)["\']?\s*$',
    re.MULTILINE,
)


def load_json(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return value


class RepositoryIntegrityTests(unittest.TestCase):
    def test_manifest_names_and_versions_match_release_files(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertTrue(version)

        for manifest_path in PLUGIN_MANIFESTS:
            with self.subTest(manifest=manifest_path.relative_to(ROOT)):
                manifest = load_json(manifest_path)
                self.assertEqual(manifest.get("name"), "alps")
                self.assertEqual(manifest.get("version"), version)

        root_manifest = load_json(ROOT / "plugin.json")
        self.assertEqual(
            root_manifest.get("$schema"),
            "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        )

    def test_distributed_skill_roots_and_locale_assets_exist(self) -> None:
        actual_roots = tuple(
            sorted(path.name for path in SKILLS_ROOT.iterdir() if path.is_dir())
        )
        self.assertEqual(actual_roots, DISTRIBUTED_SKILLS)

        expected_manifest = "locale: ja\nsource_locale: en\nstatus: reviewed\n"
        for skill_name in DISTRIBUTED_SKILLS:
            with self.subTest(skill=skill_name):
                skill_root = SKILLS_ROOT / skill_name
                self.assertTrue((skill_root / "SKILL.md").is_file())
                locale_root = skill_root / "references/locales/ja"
                self.assertTrue((locale_root / "SKILL.md").is_file())
                manifest_path = locale_root / "manifest.yaml"
                self.assertTrue(manifest_path.is_file())
                self.assertEqual(
                    manifest_path.read_text(encoding="utf-8"), expected_manifest
                )

    def test_repository_skill_links_and_distribution_boundary(self) -> None:
        development_root = ROOT / ".agents/skills"
        for skill_name in DISTRIBUTED_SKILLS:
            with self.subTest(skill=skill_name):
                link = development_root / skill_name
                self.assertTrue(link.is_symlink())
                self.assertEqual(
                    os.readlink(link), f"../../skills/{skill_name}"
                )
                self.assertEqual(link.resolve(), (SKILLS_ROOT / skill_name).resolve())

        for skill_name in REPOSITORY_SKILLS:
            with self.subTest(repository_skill=skill_name):
                path = development_root / skill_name
                self.assertTrue(path.is_dir())
                self.assertFalse(path.is_symlink())
                self.assertTrue((path / "SKILL.md").is_file())

        serialized_manifests = "\n".join(
            json.dumps(load_json(path), sort_keys=True) for path in PLUGIN_MANIFESTS
        )
        for skill_name in REPOSITORY_SKILLS:
            self.assertNotIn(skill_name, serialized_manifests)
        self.assertNotIn(".agents/skills", serialized_manifests)

    def test_reference_model_known_same_scope_targets_exist(self) -> None:
        model = (SKILLS_ROOT / "alps-reference-model/SKILL.md").read_text(
            encoding="utf-8"
        )
        for skill_name in ("define-alps", "apply-alps", "manage-alps"):
            with self.subTest(skill=skill_name):
                self.assertIn(f"skill:#{skill_name}", model)
                self.assertTrue((SKILLS_ROOT / skill_name / "SKILL.md").is_file())

    def test_required_repository_targets_exist(self) -> None:
        for path in REQUIRED_PATHS:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_openai_interface_icons_exist(self) -> None:
        for skill_name in DISTRIBUTED_SKILLS:
            metadata_path = SKILLS_ROOT / skill_name / "agents/openai.yaml"
            metadata = metadata_path.read_text(encoding="utf-8")
            icons = ICON_PATTERN.findall(metadata)
            with self.subTest(skill=skill_name):
                self.assertEqual(len(icons), 2)
                for icon in icons:
                    self.assertTrue((SKILLS_ROOT / skill_name / icon).is_file())


if __name__ == "__main__":
    unittest.main()
