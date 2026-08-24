from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


CHECKER_PATH = Path(__file__).parents[1] / "skills/define-alps/scripts/check_alps_asset.py"
SPEC = importlib.util.spec_from_file_location("check_alps_asset", CHECKER_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def process_skill(root: Path, name: str, title: str) -> None:
    write(
        root / "skills" / name / "SKILL.md",
        f"---\nname: {name}\ndescription: {title} process.\n---\n\n# {title}\n",
    )


def process_model(root: Path, relationships: str) -> Path:
    path = root / "skills" / "fixture-model" / "SKILL.md"
    write(
        path,
        """---
name: fixture-model
description: A fixture Process Model.
metadata:
  alps.kind: process-model
---

# Fixture Model

## Purpose

The fixture organizes two Processes.

## Processes

- One
- Two

## Relationships

"""
        + relationships
        + "\n",
    )
    return path


def check_model(relationships: str) -> list[str]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        process_skill(root, "one", "One")
        process_skill(root, "two", "Two")
        path = process_model(root, relationships)
        errors, _ = CHECKER.check_asset(path, {"": root}, None)
        return errors


class CheckerRegressionTests(unittest.TestCase):
    def test_process_model_rejects_undeclared_named_table_endpoint(self) -> None:
        relationships = """| Provider | Information | Recipient | Relationship |
| --- | --- | --- | --- |
| One | information | Missing | relates the Processes. |"""
        errors = check_model(relationships)
        self.assertTrue(
            any(
                "relationship row 1 recipient Process 'Missing' is not declared"
                in error
                for error in errors
            ),
            errors,
        )

    def test_process_model_accepts_declared_named_table_endpoints(self) -> None:
        relationships = """| Provider | Information | Recipient | Relationship |
| --- | --- | --- | --- |
| One | information | Two | relates the Processes. |"""
        self.assertEqual(check_model(relationships), [])

    def test_process_model_rejects_undeclared_named_list_endpoint(self) -> None:
        errors = check_model("- One -> Missing")
        self.assertTrue(
            any(
                "relationship item 1 recipient Process 'Missing' is not declared"
                in error
                for error in errors
            ),
            errors,
        )

    def test_process_model_accepts_declared_named_list_endpoints(self) -> None:
        self.assertEqual(check_model("- One -> Two"), [])

    def test_process_model_trims_named_recipient_description(self) -> None:
        self.assertEqual(check_model("- One -> Two: carries information"), [])

    def test_process_model_accepts_canonical_provider_in_arrow_list(self) -> None:
        self.assertEqual(check_model("- skill:#one -> Two"), [])

    def test_process_model_accepts_canonical_recipient_in_arrow_list(self) -> None:
        self.assertEqual(check_model("- One -> skill:#two"), [])

    def test_inline_code_cannot_hide_following_canonical_reference(self) -> None:
        inline_comment = chr(96) + chr(60) + "!--" + chr(96)
        self.assertEqual(
            CHECKER.references(inline_comment + " skill:#missing"),
            ["skill:#missing"],
        )
        errors = check_model("- " + inline_comment + " skill:#missing")
        self.assertTrue(
            any("unresolved Skill reference skill:#missing" in error for error in errors),
            errors,
        )

    def test_inline_code_keeps_valid_canonical_reference_operative(self) -> None:
        self.assertEqual(CHECKER.references(chr(96) + "skill:#one" + chr(96)), ["skill:#one"])
        inline_comment = chr(96) + chr(60) + "!--" + chr(96)
        self.assertEqual(check_model("- " + inline_comment + " skill:#one"), [])


if __name__ == "__main__":
    unittest.main()
