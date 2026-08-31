"""Repository integrity checks for the minimal ALPS distribution."""

from __future__ import annotations

import json
import os
import re
import unittest
from pathlib import Path, PureWindowsPath


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
SKILL_NAME = "design-process-description"
SKILL_ROOT = SKILLS_ROOT / SKILL_NAME
REFERENCES = (
    "purpose-and-outcomes.md",
    "boundary-and-detail.md",
    "inputs-outputs-and-conditions.md",
)
PLUGIN_MANIFESTS = (
    ROOT / "plugin.json",
    ROOT / ".claude-plugin/plugin.json",
    ROOT / ".cursor-plugin/plugin.json",
    ROOT / ".codex-plugin/plugin.json",
)
CLAUDE_PLUGIN_SCHEMA = (
    "https://json.schemastore.org/claude-code-plugin-manifest.json"
)
ICON_PATTERN = re.compile(
    r'^\s*icon_(?:small|large):\s*["\']?([^"\'\s]+)["\']?\s*$',
    re.MULTILINE,
)
LEGACY_SKILL_IDS = (
    "alps-reference" + "-model",
    "define-" + "alps",
    "apply-" + "alps",
    "manage-" + "alps",
    "review-" + "alps",
    "sync-" + "locales",
)
FORBIDDEN_ACTIVE_TEXT = LEGACY_SKILL_IDS + (
    "metadata." + "alps.kind",
    "ALPS-" + "conformant.",
    "ALPS" + "準拠。",
    "skill:" + "#",
    "Logical Package " + "Scope",
    "Package " + "Binding",
    "Process Instance " + "Record",
    "Process Reference " + "Model representation",
    "Process View " + "representation",
    "ALPS Reference " + "Model",
    "Description " + "Conformance",
    "Reference Process " + "Conformance",
    "Execution " + "Conformance",
    "formal " + "Tailoring",
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
            f"{label} must not escape the Plugin root on Windows",
        )

        resolved_root = owner_root.resolve()
        resolved_target = (owner_root / value).resolve()
        try:
            resolved_target.relative_to(resolved_root)
        except ValueError:
            self.fail(f"{label} escapes {owner_root.relative_to(ROOT)}")

        if target_type == "directory":
            self.assertTrue(resolved_target.is_dir(), f"{label} must be a directory")
        elif target_type == "file":
            self.assertTrue(resolved_target.is_file(), f"{label} must be a file")
        else:
            self.fail(f"unsupported target type: {target_type}")
        return resolved_target

    def test_single_distributed_skill_and_minimal_tree(self) -> None:
        actual = tuple(
            sorted(path.name for path in SKILLS_ROOT.iterdir() if path.is_dir())
        )
        self.assertEqual(actual, (SKILL_NAME,))
        self.assertEqual(
            {path.name for path in SKILL_ROOT.iterdir()},
            {"SKILL.md", "agents", "assets", "references"},
        )
        self.assertEqual(
            {path.name for path in (SKILL_ROOT / "agents").iterdir()},
            {"openai.yaml"},
        )
        self.assertEqual(
            {path.name for path in (SKILL_ROOT / "assets").iterdir()},
            {"alps.svg"},
        )
        self.assertEqual(
            {path.name for path in (SKILL_ROOT / "references").iterdir()},
            {*REFERENCES, "locales"},
        )

    def test_root_skill_frontmatter_purpose_and_outcomes(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", skill, re.DOTALL)
        self.assertIsNotNone(frontmatter_match)
        assert frontmatter_match is not None
        frontmatter_lines = frontmatter_match.group(1).splitlines()
        keys = [line.split(":", 1)[0] for line in frontmatter_lines]
        self.assertEqual(keys, ["name", "description"])
        name_line = next(
            line for line in frontmatter_lines if line.startswith("name:")
        )
        self.assertEqual(name_line.split(":", 1)[1].strip(), SKILL_NAME)
        self.assertIn("## Purpose", skill)
        self.assertIn("## Outcomes", skill)

    def test_three_references_are_linked_with_specific_conditions(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        conditions = {
            "purpose-and-outcomes.md": (
                "Purpose combines multiple independent intents",
                "success cannot be assessed",
            ),
            "boundary-and-detail.md": (
                "Skill is too case-specific",
                "raises a split-or-merge decision",
            ),
            "inputs-outputs-and-conditions.md": (
                "agent or tool is labeled as an Input",
                "meaning is lost at a Handoff",
            ),
        }
        for reference in REFERENCES:
            with self.subTest(reference=reference):
                self.assertTrue((SKILL_ROOT / "references" / reference).is_file())
                self.assertIn(f"(references/{reference})", skill)
                for phrase in conditions[reference]:
                    self.assertIn(phrase, skill)

    def test_japanese_counterparts_are_complete(self) -> None:
        locale_root = SKILL_ROOT / "references/locales/ja"
        self.assertEqual(
            {path.name for path in locale_root.iterdir()},
            {"SKILL.md", "manifest.yaml", *REFERENCES},
        )
        self.assertEqual(
            (locale_root / "manifest.yaml").read_text(encoding="utf-8"),
            "locale: ja\nsource_locale: en\nstatus: reviewed\n",
        )

    def test_repository_skill_symlink(self) -> None:
        links_root = ROOT / ".agents/skills"
        self.assertEqual({path.name for path in links_root.iterdir()}, {SKILL_NAME})
        link = links_root / SKILL_NAME
        self.assertTrue(link.is_symlink())
        self.assertEqual(os.readlink(link), f"../../skills/{SKILL_NAME}")
        self.assertEqual(link.resolve(), SKILL_ROOT.resolve())

    def test_manifest_names_versions_and_paths(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(version, "0.6.0")
        for manifest_path in PLUGIN_MANIFESTS:
            with self.subTest(manifest=manifest_path.relative_to(ROOT)):
                manifest = load_json(manifest_path)
                self.assertEqual(manifest.get("name"), "alps")
                self.assertEqual(manifest.get("version"), version)

        self.assertEqual(
            load_json(ROOT / "plugin.json").get("$schema"),
            "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        )
        self.assertEqual(
            load_json(ROOT / ".claude-plugin/plugin.json").get("$schema"),
            CLAUDE_PLUGIN_SCHEMA,
        )
        for manifest_path in (
            ROOT / ".cursor-plugin/plugin.json",
            ROOT / ".codex-plugin/plugin.json",
        ):
            manifest = load_json(manifest_path)
            resolved = self.assert_local_target(
                owner_root=ROOT,
                value=manifest["skills"],
                target_type="directory",
                label=f"{manifest_path.relative_to(ROOT)}:skills",
            )
            self.assertEqual(resolved, SKILLS_ROOT.resolve())

        codex = load_json(ROOT / ".codex-plugin/plugin.json")
        self.assertEqual(
            nested_value(codex, ("interface", "capabilities")),
            [
                "Design a Process Description from recurring work",
                "Simplify an existing Process Skill",
                "Revise a Process Description from evidence of use",
            ],
        )
        prompts = nested_value(codex, ("interface", "defaultPrompt"))
        self.assertIsInstance(prompts, list)
        self.assertEqual(len(prompts), 3)

    def test_host_adapter_icon_paths(self) -> None:
        path_fields = (
            (ROOT / ".cursor-plugin/plugin.json", ("logo",)),
            (ROOT / ".codex-plugin/plugin.json", ("interface", "composerIcon")),
            (ROOT / ".codex-plugin/plugin.json", ("interface", "logo")),
            (ROOT / ".codex-plugin/plugin.json", ("interface", "logoDark")),
        )
        for manifest_path, field_path in path_fields:
            with self.subTest(path=manifest_path, field=field_path):
                manifest = load_json(manifest_path)
                self.assert_local_target(
                    owner_root=ROOT,
                    value=nested_value(manifest, field_path),
                    target_type="file",
                    label=f"{manifest_path.relative_to(ROOT)}:{'.'.join(field_path)}",
                )

    def test_openai_interface_icons_exist(self) -> None:
        metadata_path = SKILL_ROOT / "agents/openai.yaml"
        metadata = metadata_path.read_text(encoding="utf-8")
        icons = ICON_PATTERN.findall(metadata)
        self.assertEqual(len(icons), 2)
        for icon in icons:
            self.assert_local_target(
                owner_root=SKILL_ROOT,
                value=icon,
                target_type="file",
                label=f"{metadata_path.relative_to(ROOT)}:{icon}",
            )

    def test_removed_paths_are_absent(self) -> None:
        removed = [
            ROOT / "spec",
            ROOT / ("tests/test_" + "process_instance_record.py"),
            ROOT / "assets" / ("alps-reference" + "-model.svg"),
            ROOT / "assets" / ("alps-reference" + "-model-ja.svg"),
        ]
        removed.extend(SKILLS_ROOT / name for name in LEGACY_SKILL_IDS[:4])
        removed.extend(ROOT / ".agents/skills" / name for name in LEGACY_SKILL_IDS)
        for path in removed:
            with self.subTest(path=path):
                self.assertFalse(path.exists() or path.is_symlink())

    def test_obsolete_terms_are_absent_from_active_product_files(self) -> None:
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts:
                continue
            relative = path.relative_to(ROOT)
            if relative == Path("CHANGELOG.md") or relative.parts[:2] == (
                "docs",
                "releases",
            ):
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for term in FORBIDDEN_ACTIVE_TEXT:
                with self.subTest(path=relative, term=term):
                    self.assertNotIn(term, content)


if __name__ == "__main__":
    unittest.main()
