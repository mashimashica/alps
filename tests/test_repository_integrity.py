"""Repository-only integrity checks that do not interpret Process meaning."""

from __future__ import annotations

import json
import os
import re
import unittest
from pathlib import Path, PureWindowsPath


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
DISTRIBUTED_SKILLS = ("reusable-work-design",)
REPOSITORY_SKILLS = ("review-alps", "sync-locales")
PLUGIN_MANIFESTS = (
    ROOT / "plugin.json",
    ROOT / ".claude-plugin/plugin.json",
    ROOT / ".cursor-plugin/plugin.json",
    ROOT / ".codex-plugin/plugin.json",
)
CLAUDE_PLUGIN_SCHEMA = (
    "https://json.schemastore.org/claude-code-plugin-manifest.json"
)
REQUIRED_PATHS = (
    ROOT / "AGENTS.md",
    ROOT / "docs/locales/ja/AGENTS.md",
    ROOT / "README.md",
    ROOT / "docs/locales/ja/README.md",
    ROOT / "docs/versioning.md",
    ROOT / "docs/locales/ja/versioning.md",
    ROOT / "localization.yaml",
    ROOT / "spec/process-framework.md",
    ROOT / "spec/locales/ja/process-framework.md",
    ROOT / "spec/ALPS-SPEC.md",
    ROOT / "spec/locales/ja/ALPS-SPEC.md",
    ROOT / "skills/reusable-work-design/SKILL.md",
    ROOT / "skills/reusable-work-design/references/locales/ja/SKILL.md",
    ROOT / "skills/reusable-work-design/references/locales/ja/manifest.yaml",
    ROOT / "skills/reusable-work-design/agents/openai.yaml",
    ROOT / "skills/reusable-work-design/assets/alps.svg",
)
DELETED_PATHS = (
    ROOT / "skills/alps-reference-model",
    ROOT / "skills/define-alps",
    ROOT / "skills/apply-alps",
    ROOT / "skills/manage-alps",
    ROOT / ".agents/skills/alps-reference-model",
    ROOT / ".agents/skills/define-alps",
    ROOT / ".agents/skills/apply-alps",
    ROOT / ".agents/skills/manage-alps",
    ROOT / "assets/alps-reference-model.svg",
    ROOT / "assets/alps-reference-model-ja.svg",
    ROOT / "skills/apply-alps/scripts/process_instance_record.py",
    ROOT / "skills/apply-alps/references/process-instance-record.md",
    ROOT / "skills/apply-alps/references/locales/ja/process-instance-record.md",
    ROOT / "tests/test_process_instance_record.py",
)
ACTIVE_OLD_REFERENCES = (
    "alps-reference-model",
    "define-alps",
    "apply-alps",
    "manage-alps",
    "skill:#",
    "skill:alps#",
    "metadata.alps.kind",
    "process-reference-model",
    "process-instance-record",
    "process_instance_record",
    "ALPS-conformant.",
    "ALPS準拠。",
    "Logical Package Scope",
    "Package Binding",
    "Reference Process Conformance",
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


def nested_value(
    mapping: dict[str, object], field_path: tuple[str, ...]
) -> object:
    value: object = mapping
    for field in field_path:
        if not isinstance(value, dict) or field not in value:
            raise AssertionError(f"missing manifest field {'.'.join(field_path)}")
        value = value[field]
    return value


def windows_path_escapes_root(path: PureWindowsPath) -> bool:
    depth = 0
    for part in path.parts:
        if part in ("", "."):
            continue
        if part == "..":
            if depth == 0:
                return True
            depth -= 1
        else:
            depth += 1
    return False


def active_text_paths() -> list[Path]:
    paths: list[Path] = []
    suffixes = {".json", ".md", ".svg", ".yaml", ".yml"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in suffixes:
            continue
        relative = path.relative_to(ROOT)
        if relative.parts[0] in {".git", "tests"}:
            continue
        if relative == Path("CHANGELOG.md"):
            continue
        if relative.parts[:2] == ("docs", "releases"):
            continue
        paths.append(path)
    return paths


class RepositoryIntegrityTests(unittest.TestCase):
    def assert_local_target(
        self,
        *,
        owner_root: Path,
        value: object,
        target_type: str,
        label: str,
    ) -> Path:
        self.assertIsInstance(value, str, f"{label} must be a string")
        assert isinstance(value, str)
        self.assertTrue(value, f"{label} must not be empty")
        self.assertFalse(Path(value).is_absolute(), f"{label} must be relative")
        windows_path = PureWindowsPath(value)
        self.assertFalse(
            windows_path.is_absolute() or bool(windows_path.drive),
            f"{label} must not use an absolute Windows path",
        )
        self.assertFalse(
            windows_path_escapes_root(windows_path),
            f"{label} must not escape the owner root on Windows",
        )

        resolved_root = owner_root.resolve()
        resolved_target = (owner_root / value).resolve()
        try:
            resolved_target.relative_to(resolved_root)
        except ValueError:
            self.fail(f"{label} escapes {owner_root.relative_to(ROOT)}")

        if target_type == "directory":
            self.assertTrue(resolved_target.is_dir(), f"{label} must name a directory")
        elif target_type == "file":
            self.assertTrue(resolved_target.is_file(), f"{label} must name a file")
        else:
            self.fail(f"unsupported target type for {label}: {target_type}")
        return resolved_target

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
        claude_manifest = load_json(ROOT / ".claude-plugin/plugin.json")
        self.assertEqual(claude_manifest.get("$schema"), CLAUDE_PLUGIN_SCHEMA)

    def test_distributed_skill_root_and_locale_assets_exist(self) -> None:
        actual_roots = tuple(
            sorted(path.name for path in SKILLS_ROOT.iterdir() if path.is_dir())
        )
        self.assertEqual(actual_roots, DISTRIBUTED_SKILLS)

        skill_root = SKILLS_ROOT / "reusable-work-design"
        self.assertTrue((skill_root / "SKILL.md").is_file())
        locale_root = skill_root / "references/locales/ja"
        self.assertTrue((locale_root / "SKILL.md").is_file())
        manifest_path = locale_root / "manifest.yaml"
        self.assertEqual(
            manifest_path.read_text(encoding="utf-8"),
            "locale: ja\nsource_locale: en\nstatus: reviewed\n",
        )

    def test_repository_skill_links_and_distribution_boundary(self) -> None:
        development_root = ROOT / ".agents/skills"
        link = development_root / "reusable-work-design"
        self.assertTrue(link.is_symlink())
        self.assertEqual(os.readlink(link), "../../skills/reusable-work-design")
        self.assertEqual(link.resolve(), (SKILLS_ROOT / "reusable-work-design").resolve())

        for skill_name in REPOSITORY_SKILLS:
            with self.subTest(repository_skill=skill_name):
                path = development_root / skill_name
                self.assertTrue(path.is_dir())
                self.assertFalse(path.is_symlink())
                self.assertTrue((path / "SKILL.md").is_file())

        serialized = "\n".join(
            json.dumps(load_json(path), sort_keys=True) for path in PLUGIN_MANIFESTS
        )
        for skill_name in REPOSITORY_SKILLS:
            self.assertNotIn(skill_name, serialized)
        self.assertNotIn(".agents/skills", serialized)

    def test_required_paths_exist_and_removed_paths_do_not(self) -> None:
        for path in REQUIRED_PATHS:
            with self.subTest(required=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

        for path in DELETED_PATHS:
            with self.subTest(deleted=path.relative_to(ROOT)):
                self.assertFalse(os.path.lexists(path))

    def test_host_adapter_local_paths_exist_within_owner_root(self) -> None:
        path_fields = (
            (ROOT / ".cursor-plugin/plugin.json", ("logo",), "file", None),
            (ROOT / ".cursor-plugin/plugin.json", ("skills",), "directory", SKILLS_ROOT),
            (ROOT / ".codex-plugin/plugin.json", ("skills",), "directory", SKILLS_ROOT),
            (ROOT / ".codex-plugin/plugin.json", ("interface", "composerIcon"), "file", None),
            (ROOT / ".codex-plugin/plugin.json", ("interface", "logo"), "file", None),
            (ROOT / ".codex-plugin/plugin.json", ("interface", "logoDark"), "file", None),
        )
        for manifest_path, field_path, target_type, expected_target in path_fields:
            label = f"{manifest_path.relative_to(ROOT)}:{'.'.join(field_path)}"
            with self.subTest(path=label):
                manifest = load_json(manifest_path)
                resolved = self.assert_local_target(
                    owner_root=ROOT,
                    value=nested_value(manifest, field_path),
                    target_type=target_type,
                    label=label,
                )
                if expected_target is not None:
                    self.assertEqual(resolved, expected_target.resolve())

    def test_local_path_guard_rejects_invalid_targets(self) -> None:
        invalid_targets = (
            ("/tmp", "directory"),
            ("../outside.svg", "file"),
            (r"..\outside.svg", "file"),
            ("./assets/missing.svg", "file"),
            ("./assets/icon.svg", "directory"),
            ("./skills", "file"),
        )
        for value, target_type in invalid_targets:
            with self.subTest(value=value, target_type=target_type):
                with self.assertRaises(AssertionError):
                    self.assert_local_target(
                        owner_root=ROOT,
                        value=value,
                        target_type=target_type,
                        label="negative path test",
                    )

    def test_openai_metadata_points_within_the_skill_package(self) -> None:
        skill_root = SKILLS_ROOT / "reusable-work-design"
        metadata_path = skill_root / "agents/openai.yaml"
        metadata = metadata_path.read_text(encoding="utf-8")
        self.assertIn('display_name: "Reusable Work Design Process"', metadata)
        self.assertIn("$reusable-work-design", metadata)
        icons = ICON_PATTERN.findall(metadata)
        self.assertEqual(len(icons), 2)
        for icon in icons:
            self.assert_local_target(
                owner_root=skill_root,
                value=icon,
                target_type="file",
                label=f"{metadata_path.relative_to(ROOT)}:{icon}",
            )

    def test_active_surface_has_no_removed_identifiers_or_requirements(self) -> None:
        for path in active_text_paths():
            text = path.read_text(encoding="utf-8")
            for old_reference in ACTIVE_OLD_REFERENCES:
                with self.subTest(path=path.relative_to(ROOT), value=old_reference):
                    self.assertNotIn(old_reference, text)


if __name__ == "__main__":
    unittest.main()
