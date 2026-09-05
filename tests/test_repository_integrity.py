"""Repository-only integrity checks that do not interpret ALPS meaning."""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path, PureWindowsPath
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
DISTRIBUTED_SKILLS = ("design-process-description",)
PLUGIN_MANIFESTS = (
    ROOT / "plugin.json",
    ROOT / ".claude-plugin/plugin.json",
    ROOT / ".cursor-plugin/plugin.json",
    ROOT / ".codex-plugin/plugin.json",
)
CLAUDE_PLUGIN_SCHEMA = (
    "https://json.schemastore.org/claude-code-plugin-manifest.json"
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
    ROOT / "CONTRIBUTING.md",
    ROOT / "docs/locales/ja/CONTRIBUTING.md",
    ROOT / "docs/versioning.md",
    ROOT / "docs/locales/ja/versioning.md",
    ROOT / "docs/unreleased-redesign.md",
    ROOT / "docs/locales/ja/unreleased-redesign.md",
    ROOT / ".github/workflows/validate.yml",
    ROOT / "skills/design-process-description/references/SKILL-template.md",
    ROOT / "skills/design-process-description/references/examples.md",
    ROOT / "skills/design-process-description/references/locales/ja/SKILL-template.md",
    ROOT / "skills/design-process-description/references/locales/ja/examples.md",
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


def active_markdown_files(root: Path) -> list[Path]:
    """Current guidance and sources only; never inspect release/change history."""
    files = [root / name for name in ("README.md", "AGENTS.md", "CONTRIBUTING.md")]
    files += [root / ".github/pull_request_template.md"]
    files += list((root / "docs").glob("*.md"))
    for directory in ("spec", "skills", "docs/locales/ja"):
        files += list((root / directory).rglob("*.md"))
    files += [root / ".agents/skills" / name / "SKILL.md" for name in REPOSITORY_SKILLS]
    return sorted(set(files))


def local_links(path: Path) -> list[str]:
    """Extract this repository's inline link targets for path checks only.

    Markdown syntax and anchors are independently checked by markdown-link-check.
    This is not an interpreter for Process Descriptions.
    """
    text = path.read_text(encoding="utf-8")
    targets = re.findall(r"\[[^\]\n]*\]\(([^\s)]+)\)", text)
    targets += re.findall(r'(?:href|src)="([^"\n]+)"', text)
    result = []
    for target in targets:
        parsed = urlsplit(target)
        if not parsed.scheme and not parsed.netloc and parsed.path:
            result.append(unquote(parsed.path))
    return result


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
        claude_manifest = load_json(ROOT / ".claude-plugin/plugin.json")
        self.assertEqual(
            claude_manifest.get("$schema"), CLAUDE_PLUGIN_SCHEMA
        )

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
        self.assertFalse(
            Path(value).is_absolute(), f"{label} must be relative"
        )
        windows_path = PureWindowsPath(value)
        self.assertFalse(
            windows_path.is_absolute() or bool(windows_path.drive),
            f"{label} must not use an absolute Windows path",
        )
        self.assertFalse(
            windows_path_escapes_root(windows_path),
            f"{label} must not escape the Plugin root on Windows",
        )

        resolved_root = owner_root.resolve()
        resolved_target = (owner_root / value).resolve()
        try:
            resolved_target.relative_to(resolved_root)
        except ValueError:
            self.fail(f"{label} escapes {owner_root}")

        if target_type == "directory":
            self.assertTrue(
                resolved_target.is_dir(), f"{label} must name a directory"
            )
        elif target_type == "file":
            self.assertTrue(
                resolved_target.is_file(), f"{label} must name a regular file"
            )
        else:
            self.fail(f"unsupported target type for {label}: {target_type}")
        return resolved_target

    def test_host_adapter_local_paths_exist_within_plugin_root(self) -> None:
        path_fields = (
            (
                ROOT / ".cursor-plugin/plugin.json",
                ("logo",),
                "file",
                None,
            ),
            (
                ROOT / ".cursor-plugin/plugin.json",
                ("skills",),
                "directory",
                SKILLS_ROOT,
            ),
            (
                ROOT / ".codex-plugin/plugin.json",
                ("skills",),
                "directory",
                SKILLS_ROOT,
            ),
            (
                ROOT / ".codex-plugin/plugin.json",
                ("interface", "composerIcon"),
                "file",
                None,
            ),
            (
                ROOT / ".codex-plugin/plugin.json",
                ("interface", "logo"),
                "file",
                None,
            ),
            (
                ROOT / ".codex-plugin/plugin.json",
                ("interface", "logoDark"),
                "file",
                None,
            ),
        )
        for manifest_path, field_path, target_type, expected_target in path_fields:
            label = (
                f"{manifest_path.relative_to(ROOT)}:"
                f"{'.'.join(field_path)}"
            )
            with self.subTest(path=label):
                manifest = load_json(manifest_path)
                resolved_target = self.assert_local_target(
                    owner_root=ROOT,
                    value=nested_value(manifest, field_path),
                    target_type=target_type,
                    label=label,
                )
                if expected_target is not None:
                    self.assertEqual(resolved_target, expected_target.resolve())

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

    def test_distributed_skill_roots_and_locale_assets_exist(self) -> None:
        self.assertFalse(SKILLS_ROOT.is_symlink())
        actual_roots = tuple(
            sorted(path.name for path in SKILLS_ROOT.iterdir() if path.is_dir())
        )
        self.assertEqual(actual_roots, DISTRIBUTED_SKILLS)

        expected_manifest = "locale: ja\nsource_locale: en\nstatus: reviewed\n"
        for skill_name in DISTRIBUTED_SKILLS:
            with self.subTest(skill=skill_name):
                skill_root = SKILLS_ROOT / skill_name
                self.assertFalse(skill_root.is_symlink())
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
        self.assertEqual(
            {path.name for path in development_root.iterdir()},
            set(DISTRIBUTED_SKILLS + REPOSITORY_SKILLS),
        )
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

    def test_required_specification_references_survive_plugin_packaging(self) -> None:
        # Copy the actual distributable sources, without repository development
        # Skills or parent checkout files. Relative references must still work.
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "alps"
            package.mkdir()
            for name in ("skills", "spec", "assets"):
                shutil.copytree(ROOT / name, package / name, symlinks=True)
            for manifest in PLUGIN_MANIFESTS:
                target = package / manifest.relative_to(ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(manifest, target)
            self.assertFalse((package / ".agents").exists())
            for name in DISTRIBUTED_SKILLS:
                skill = package / "skills" / name / "SKILL.md"
                targets = {(skill.parent / link).resolve() for link in local_links(skill)}
                for required in ("process-framework.md", "ALPS-SPEC.md"):
                    self.assertIn(package / "spec" / required, targets)
            for path in [*package.glob("skills/**/*.md"), *package.glob("spec/**/*.md")]:
                for link in local_links(path):
                    with self.subTest(source=path.relative_to(package), link=link):
                        self.assert_local_target(
                            owner_root=package,
                            value=str(path.parent.relative_to(package) / link),
                            target_type="file",
                            label=f"{path.relative_to(package)}:{link}",
                        )

    def test_active_relative_links_resolve_inside_repository(self) -> None:
        for source in active_markdown_files(ROOT):
            for link in local_links(source):
                with self.subTest(source=source.relative_to(ROOT), link=link):
                    self.assert_local_target(
                        owner_root=ROOT,
                        value=str(source.parent.relative_to(ROOT) / link),
                        target_type="file",
                        label=f"{source.relative_to(ROOT)}:{link}",
                    )

    def test_distributed_files_stay_inside_plugin_root(self) -> None:
        paths = list(PLUGIN_MANIFESTS)
        for directory in ("skills", "spec", "assets"):
            paths += list((ROOT / directory).rglob("*"))
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.resolve().is_relative_to(ROOT.resolve()))
                self.assertTrue(path.exists())
                self.assertFalse(path.resolve().is_relative_to(ROOT / ".agents"))

    def test_path_guard_rejects_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            package = base / "package"
            package.mkdir()
            outside = base / "outside.md"
            outside.write_text("outside\n", encoding="utf-8")
            (package / "escaped.md").symlink_to(outside)
            with self.assertRaises(AssertionError):
                self.assert_local_target(
                    owner_root=package,
                    value="escaped.md",
                    target_type="file",
                    label="escaping symlink",
                )

    def test_retired_contracts_are_absent_from_active_content(self) -> None:
        # These are retirement sentinels, not semantic correctness criteria.
        # Migration notes deliberately name removed surfaces. They and historical
        # releases are not sources of current requirements.
        retired = (
            "alps-reference-model", "define-alps", "apply-alps", "manage-alps",
            "process_instance_record", "process-instance-record/1",
            "record-templates.md", "management-records.md", "skill-package-format.md",
            "skill:", "Logical Package Scope", "Package Binding", "alps.kind",
            "ALPS-conformant.", "ALPS準拠。",
            "Outcome Conformance", "Task Conformance", "Tailored Conformance",
            "Description Conformance", "Reference Process Conformance",
            "Execution Conformance", "ALPS Reference Model",
            "成果適合", "タスク適合", "参照プロセス適合", "記述適合", "実行適合",
        )
        current = [p for p in active_markdown_files(ROOT) if p.name != "unreleased-redesign.md"]
        current += list(PLUGIN_MANIFESTS)
        current += list((ROOT / "skills").rglob("*.yaml"))
        current += list((ROOT / "assets").glob("*.svg"))
        current += [ROOT / ".github/workflows/validate.yml", ROOT / "localization.yaml"]
        for path in current:
            content = path.read_text(encoding="utf-8")
            for marker in retired:
                with self.subTest(path=path.relative_to(ROOT), retired=marker):
                    self.assertNotIn(marker, content)

    def test_no_retired_implementation_or_aliases_remain(self) -> None:
        retired_names = {
            "process_instance_record.py", "test_process_instance_record.py",
            "process-instance-record.md", "record-templates.md",
            "management-records.md", "skill-package-format.md",
        }
        for directory in ("skills", "tests", "spec", ".agents/skills"):
            for path in (ROOT / directory).rglob("*"):
                with self.subTest(path=path.relative_to(ROOT)):
                    self.assertNotIn(path.name, retired_names)
        self.assertFalse(any((SKILLS_ROOT / DISTRIBUTED_SKILLS[0]).rglob("*.py")))

    def test_svg_resources_and_local_image_targets_exist(self) -> None:
        for svg in [*ROOT.glob("assets/*.svg"), *SKILLS_ROOT.glob("*/assets/*.svg")]:
            document = ET.parse(svg)
            for element in document.iter():
                for key, value in element.attrib.items():
                    if key in ("href", "{http://www.w3.org/1999/xlink}href"):
                        if value.startswith("#"):
                            continue
                        self.assert_local_target(
                            owner_root=ROOT,
                            value=str(svg.parent.relative_to(ROOT) / value),
                            target_type="file",
                            label=f"{svg.relative_to(ROOT)}:{value}",
                        )

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
                    self.assert_local_target(
                        owner_root=SKILLS_ROOT / skill_name,
                        value=icon,
                        target_type="file",
                        label=f"{metadata_path.relative_to(ROOT)}:{icon}",
                    )


if __name__ == "__main__":
    unittest.main()
