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


def reference_process_skill(root: Path, name: str, title: str) -> None:
    write(
        root / "skills" / name / "SKILL.md",
        f"""---
name: {name}
description: {title} process.
---

# {title}

## Purpose

{title} purpose.

## Outcomes

- {title} is achieved.
""",
    )


def process_reference_model(root: Path, relationships: str) -> Path:
    path = root / "skills" / "fixture-reference-model" / "SKILL.md"
    write(
        path,
        """---
name: fixture-reference-model
description: A fixture Process Reference Model.
metadata:
  alps.kind: process-reference-model
---

# Fixture Reference Model

## Purpose

The fixture defines two reference Processes.

## Processes

### One

#### Purpose

One purpose.

#### Outcomes

- One is achieved.

`skill:#one`

### Two

#### Purpose

Two purpose.

#### Outcomes

- Two is achieved.

`skill:#two`

## Relationships

"""
        + relationships
        + "\n",
    )
    return path


def check_reference_model_fixture(relationships: str) -> list[str]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        reference_process_skill(root, "one", "One")
        reference_process_skill(root, "two", "Two")
        path = process_reference_model(root, relationships)
        errors, _ = CHECKER.check_asset(path, {"": root}, None)
        return errors


def process_view(root: Path, sources: str, included: str) -> Path:
    path = root / "skills" / "fixture-view" / "SKILL.md"
    write(
        path,
        """---
name: fixture-view
description: A fixture Process View.
metadata:
  alps.kind: process-view
---

# Fixture View

## Purpose

The fixture organizes source Processes.

## Outcomes

- The source Processes are represented.

## Source Processes

"""
        + sources
        + """

## Included Activities and Tasks

"""
        + included
        + """

## Application

The fixture provides application guidance.
""",
    )
    return path


def check_view_fixture(sources: str, included: str) -> list[str]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        process_skill(root, "one", "One")
        process_skill(root, "two", "Two")
        path = process_view(root, sources, included)
        errors, _ = CHECKER.check_asset(path, {"": root}, None)
        return errors


class CheckerRegressionTests(unittest.TestCase):
    def test_table_tokenizer_honors_escape_parity_and_exact_code_run(self) -> None:
        self.assertEqual(
            CHECKER.table_row_cells(r"| left | A \| B | right |"),
            ["left", r"A \| B", "right"],
        )
        self.assertEqual(
            CHECKER.table_row_cells(r"| left | A \\| B | right |"),
            ["left", "A " + chr(92) + chr(92), "B", "right"],
        )
        self.assertEqual(
            CHECKER.table_row_cells(r"| left | ``A | B`` | right |"),
            ["left", "``A | B``", "right"],
        )
        self.assertEqual(
            CHECKER.table_row_cells(r"| left | ```A | B`` | right |"),
            ["left", "```A | B`` | right |"],
        )

    def test_process_model_accepts_escaped_and_inline_code_pipes(self) -> None:
        escaped = r"""| Provider | Information | Recipient | Relationship |
| --- | --- | --- | --- |
| One | A \| B | Two | relates the Processes. |"""
        inline = """| Provider | Information | Recipient | Relationship |
| --- | --- | --- | --- |
| One | `A | B` | Two | relates the Processes. |"""
        self.assertEqual(check_model(escaped), [])
        self.assertEqual(check_model(inline), [])

    def test_process_model_checks_canonical_endpoint_display_name(self) -> None:
        invalid = """| Provider | Information | Recipient | Relationship |
| --- | --- | --- | --- |
| Missing (`skill:#one`) | information | Two | relates the Processes. |"""
        errors = check_model(invalid)
        self.assertTrue(any("differs from referenced Process 'One'" in error for error in errors), errors)
        valid = """| Provider | Information | Recipient | Relationship |
| --- | --- | --- | --- |
| One (`skill:#one`) | information | skill:#two | relates the Processes. |"""
        self.assertEqual(check_model(valid), [])

    def test_process_model_rejects_multiple_canonical_endpoint_references(self) -> None:
        relationships = """| Provider | Information | Recipient | Relationship |
| --- | --- | --- | --- |
| One (`skill:#one` `skill:#two`) | information | Two | relates the Processes. |"""
        errors = check_model(relationships)
        self.assertTrue(any("at most one canonical Skill reference" in error for error in errors), errors)

    def test_process_reference_model_checks_canonical_endpoint_display_name(self) -> None:
        invalid = """| Provider | Information | Recipient | Relationship |
| --- | --- | --- | --- |
| Missing (`skill:#one`) | information | Two | relates the Processes. |"""
        errors = check_reference_model_fixture(invalid)
        self.assertTrue(any("differs from referenced Process 'One'" in error for error in errors), errors)
        valid = """| Provider | Information | Recipient | Relationship |
| --- | --- | --- | --- |
| One (`skill:#one`) | information | skill:#two | relates the Processes. |"""
        self.assertEqual(check_reference_model_fixture(valid), [])

    def test_process_view_checks_source_list_display_name(self) -> None:
        invalid_sources = "- Missing (`skill:#one`)\n- Two (`skill:#two`)"
        included = """| Source Process | Source element |
| --- | --- |
| Missing (`skill:#one`) | Activity |
| Two (`skill:#two`) | Task |"""
        errors = check_view_fixture(invalid_sources, included)
        self.assertTrue(any("source entry 1" in error and "differs from referenced Process 'One'" in error for error in errors), errors)
        valid_sources = "- One\n- skill:#one\n- skill:#two"
        valid_included = """| Source Process | Source element |
| --- | --- |
| One (`skill:#one`) | Activity |
| skill:#two | Task |"""
        self.assertEqual(check_view_fixture(valid_sources, valid_included), [])

    def test_process_view_checks_source_table_display_name_and_canonical_only(self) -> None:
        invalid_sources = """| Source Process | Reference |
| --- | --- |
| Missing | skill:#one |
| Two | skill:#two |"""
        included = """| Source Process | Source element |
| --- | --- |
| Missing (`skill:#one`) | Activity |
| Two (`skill:#two`) | Task |"""
        errors = check_view_fixture(invalid_sources, included)
        self.assertTrue(any("source row 1" in error and "differs from referenced Process 'One'" in error for error in errors), errors)
        valid_sources = """| Source Process | Reference |
| --- | --- |
| One | skill:#one |
| skill:#two | canonical-only |"""
        valid_included = """| Source Process | Source element |
| --- | --- |
| One | Activity |
| skill:#two | Task |"""
        self.assertEqual(check_view_fixture(valid_sources, valid_included), [])

    def test_process_view_rejects_multiple_source_references(self) -> None:
        sources = """| Source Process | Reference |
| --- | --- |
| One | skill:#one skill:#two |
| Two | skill:#two |"""
        included = """| Source Process | Source element |
| --- | --- |
| One | Activity |
| Two | Task |"""
        errors = check_view_fixture(sources, included)
        self.assertTrue(any("source row 1" in error and "at most one canonical Skill reference" in error for error in errors), errors)

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
