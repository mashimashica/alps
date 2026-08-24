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


def process_model(
    root: Path,
    relationships: str,
    processes: str = "- One\n- Two",
) -> Path:
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

"""
        + processes
        + """

## Relationships

"""
        + relationships
        + "\n",
    )
    return path


def check_model(
    relationships: str,
    processes: str = "- One\n- Two",
) -> list[str]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        process_skill(root, "one", "One")
        process_skill(root, "two", "Two")
        path = process_model(root, relationships, processes)
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


def check_anchored_view_fixture(complete: bool) -> tuple[str, list[str]]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        process_skill(root, "one", "One")
        process_skill(root, "two", "Two")
        if complete:
            path = process_view(
                root,
                "- One (`skill:#one`)\n- Two (`skill:#two`)",
                """| Source Process | Source element |
| --- | --- |
| One (`skill:#one`) | Activity |
| Two (`skill:#two`) | Task |""",
            )
            write(
                path,
                path.read_text(encoding="utf-8").replace(
                    "metadata:\n",
                    "metadata: &representation\n",
                ),
            )
        else:
            path = root / "skills" / "fixture-view" / "SKILL.md"
            write(
                path,
                """---
name: fixture-view
description: A fixture Process View.
metadata: &representation
  alps.kind: process-view
---

# Fixture View

## Purpose

The fixture organizes source Processes.

## Outcomes

- The source Processes are represented.
""",
            )
        errors, _ = CHECKER.check_asset(path, {"": root}, None)
        return CHECKER.representation_kind(path), errors


def write_process_model_pair(
    root: Path,
    japanese_relationships: str,
    english_relationships: str = "- One -> Two",
) -> tuple[Path, Path]:
    english = root / "model" / "SKILL.md"
    japanese = english.parent / "references" / "locales" / "ja" / "SKILL.md"
    write(
        english,
        """---
name: fixture-process-model
description: Fixture Process Model.
metadata:
  alps.kind: process-model
---

# Fixture Process Model

## Purpose

The fixture organizes two Processes.

## Processes

- One
- Two

## Relationships

"""
        + english_relationships
        + """

## Application

The fixture is applicable.
""",
    )
    write(
        japanese,
        """---
name: fixture-process-model
description: フィクスチャのプロセスモデル。
metadata:
  alps.kind: process-model
---

# フィクスチャプロセスモデル

## 目的

二つのプロセスを整理する。

## プロセス

- 一
- 二

## 関係

"""
        + japanese_relationships
        + """

## 適用

フィクスチャを適用できる。
""",
    )
    return english, japanese


def write_reference_model_pair(
    root: Path,
    japanese_relationships: str,
) -> tuple[Path, Path]:
    english = root / "fixture" / "SKILL.md"
    japanese = english.parent / "references" / "locales" / "ja" / "SKILL.md"
    skill_ref = chr(96) + "skill:#" + "{}" + chr(96)
    write(
        english,
        """---
name: fixture-reference-model
description: Fixture Process Reference Model.
metadata:
  alps.kind: process-reference-model
---

# Fixture Reference Model

## Purpose

The fixture defines two Processes.

## Processes

### Define ALPS

Skill: """
        + skill_ref.format("define-alps")
        + """

#### Purpose

Define purpose.

#### Outcomes

- Define is achieved.

### Apply ALPS

Skill: """
        + skill_ref.format("apply-alps")
        + """

#### Purpose

Apply purpose.

#### Outcomes

- Apply is achieved.

## Relationships

| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| Define ALPS | information | Apply ALPS | relates the Processes. |

## Application

The fixture is applicable.
""",
    )
    write(
        japanese,
        """---
name: fixture-reference-model
description: フィクスチャのプロセス参照モデル。
metadata:
  alps.kind: process-reference-model
---

# フィクスチャ参照モデル

## 目的

二つのプロセスを定める。

## プロセス

### ALPS定義

スキル: """
        + skill_ref.format("define-alps")
        + """

#### 目的

定義目的。

#### 成果

- 定義が達成されている。

### ALPS適用

スキル: """
        + skill_ref.format("apply-alps")
        + """

#### 目的

適用目的。

#### 成果

- 適用が達成されている。

## 関係

"""
        + japanese_relationships
        + """

## 適用

フィクスチャを適用できる。
""",
    )
    return english, japanese


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

    def test_table_accepts_outer_and_unpiped_gfm_rows(self) -> None:
        outer = """| Provider | Information | Recipient | Relationship |
| :--- | :---: | ---: | --- |
| One | information | Two | relates the Processes. |"""
        unpiped = """Provider | Information | Recipient | Relationship
:--- | :---: | ---: | ---
One | information | Two | relates the Processes."""
        leading_only = """| Provider | Information | Recipient | Relationship
| :--- | :---: | ---: | ---
| One | information | Two | relates the Processes. |"""
        trailing_only = """Provider | Information | Recipient | Relationship |
:--- | :---: | ---: | ---: |
One | information | Two | relates the Processes. |"""
        self.assertEqual(CHECKER.table(outer), CHECKER.table(unpiped))
        self.assertEqual(CHECKER.table(outer), CHECKER.table(leading_only))
        self.assertEqual(CHECKER.table(outer), CHECKER.table(trailing_only))
        self.assertEqual(check_model(outer), [])
        self.assertEqual(check_model(unpiped), [])
        self.assertEqual(check_model(leading_only), [])
        self.assertEqual(check_model(trailing_only), [])

    def test_table_ignores_unrelated_pipe_prose_around_contiguous_block(self) -> None:
        text = """Unrelated | prose
Provider | Information | Recipient | Relationship
--- | --- | --- | ---
One | information | Two | relates the Processes.
Unrelated | prose"""
        header, rows = CHECKER.table(text)
        self.assertEqual(
            header,
            ["Provider", "Information", "Recipient", "Relationship"],
        )
        self.assertEqual(
            rows,
            [["One", "information", "Two", "relates the Processes."]],
        )

    def test_table_stops_before_blank_and_second_table(self) -> None:
        text = """Provider | Information | Recipient | Relationship
--- | --- | --- | ---
One | information | Two | relates the Processes.

Second Provider | Information | Second Recipient | Relationship
--- | --- | --- | ---
Three | information | Four | relates the Processes."""
        header, rows = CHECKER.table(text)
        self.assertEqual(
            header,
            ["Provider", "Information", "Recipient", "Relationship"],
        )
        self.assertEqual(
            rows,
            [["One", "information", "Two", "relates the Processes."]],
        )

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


    def test_process_model_accepts_list_process_descriptions(self) -> None:
        processes = "- One: the first Process\n- Two: the second Process"
        self.assertEqual(check_model("- One -> Two", processes), [])

    def test_process_model_preserves_meaningful_parenthetical_names(self) -> None:
        processes = (
            "- One (intake): the first Process\n"
            "- Two (review): the second Process"
        )
        self.assertEqual(
            check_model("- One (intake) -> Two (review): carries information", processes),
            [],
        )
        self.assertEqual(
            check_model(
                "- One (intake) -> Two (review) - carries information",
                processes,
            ),
            [],
        )
        full_width_processes = (
            "- One （intake）: the first Process\n"
            "- Two （review）: the second Process"
        )
        self.assertEqual(
            check_model(
                "- One （intake） -> Two （review）: carries information",
                full_width_processes,
            ),
            [],
        )
        self.assertEqual(CHECKER.process_display_name("skill:#one"), "")
        self.assertEqual(
            CHECKER.process_display_name("One (intake): the first Process"),
            "One (intake)",
        )
        self.assertEqual(
            CHECKER.process_display_name("One （intake）: the first Process"),
            "One （intake）",
        )
        self.assertEqual(
            CHECKER.process_display_name("One (v2: beta): the first Process"),
            "One (v2: beta)",
        )
        self.assertEqual(
            CHECKER.process_display_name("One (intake) - the first Process"),
            "One (intake)",
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

    def test_process_model_rejects_endpointless_relationship_list_item(self) -> None:
        errors = check_model("- Nothing structured here")
        self.assertTrue(
            any(
                "relationship item 1 must identify provider and recipient Processes"
                in error
                for error in errors
            ),
            errors,
        )

    def test_process_reference_model_rejects_endpointless_relationship_list_item(self) -> None:
        errors = check_reference_model_fixture("- Nothing structured here")
        self.assertTrue(
            any(
                "relationship item 1 must identify provider and recipient Processes"
                in error
                for error in errors
            ),
            errors,
        )

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

    def test_anchored_metadata_kind_is_preserved_for_valid_view(self) -> None:
        kind, errors = check_anchored_view_fixture(True)
        self.assertEqual(kind, "process-view")
        self.assertEqual(errors, [])

    def test_anchored_process_view_requires_view_sections(self) -> None:
        kind, errors = check_anchored_view_fixture(False)
        self.assertEqual(kind, "process-view")
        self.assertTrue(
            any("Process View requires Source Processes" in error for error in errors),
            errors,
        )
        self.assertFalse(
            any("Process representation requires" in error for error in errors),
            errors,
        )


    def test_process_model_pair_accepts_translated_named_endpoints(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_process_model_pair(
                Path(directory),
                "- 一 -> 二",
            )
            errors, _ = CHECKER.check_pair(
                english,
                japanese,
                set(CHECKER.DEFAULT_JA_TERMS),
                "fixture",
            )
            self.assertEqual(errors, [], errors)

    def test_process_model_pair_accepts_outer_and_unpiped_relationship_tables(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_process_model_pair(
                Path(directory),
                "提供側プロセス | 情報 | 受領側プロセス | 関係\n--- | --- | --- | ---\n一 | 情報 | 二 | プロセス間の関係。",
                "| Provider Process | Information | Recipient Process | Relationship |\n| --- | --- | --- | --- |\n| One | information | Two | relates the Processes. |",
            )
            errors, _ = CHECKER.check_pair(
                english,
                japanese,
                set(CHECKER.DEFAULT_JA_TERMS),
                "fixture",
            )
            self.assertEqual(errors, [], errors)

    def test_process_model_pair_rejects_reversed_unpiped_relationship_table(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_process_model_pair(
                Path(directory),
                "提供側プロセス | 情報 | 受領側プロセス | 関係\n--- | --- | --- | ---\n二 | 情報 | 一 | プロセス間の関係。",
                "| Provider Process | Information | Recipient Process | Relationship |\n| --- | --- | --- | --- |\n| One | information | Two | relates the Processes. |",
            )
            errors, _ = CHECKER.check_pair(
                english,
                japanese,
                set(CHECKER.DEFAULT_JA_TERMS),
                "fixture",
            )
            self.assertTrue(
                any(
                    "relationship provider/recipient endpoint identity or order differs"
                    in error
                    for error in errors
                ),
                errors,
            )

    def test_process_model_pair_rejects_reversed_translated_endpoints(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_process_model_pair(
                Path(directory),
                "- 二 -> 一",
            )
            errors, _ = CHECKER.check_pair(
                english,
                japanese,
                set(CHECKER.DEFAULT_JA_TERMS),
                "fixture",
            )
            self.assertTrue(
                any(
                    "relationship provider/recipient endpoint identity or order differs"
                    in error
                    for error in errors
                ),
                errors,
            )

    def test_reference_model_pair_accepts_translated_named_endpoints(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_reference_model_pair(
                Path(directory),
                """| 提供側プロセス | 情報 | 受領側プロセス | 関係 |
| --- | --- | --- | --- |
| ALPS定義 | 情報 | ALPS適用 | プロセス間の関係。 |""",
            )
            errors, _ = CHECKER.check_pair(english, japanese, set(CHECKER.DEFAULT_JA_TERMS), "fixture")
            self.assertEqual(errors, [], errors)

    def test_reference_model_pair_rejects_reversed_named_endpoints(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_reference_model_pair(
                Path(directory),
                """| 提供側プロセス | 情報 | 受領側プロセス | 関係 |
| --- | --- | --- | --- |
| ALPS適用 | 情報 | ALPS定義 | プロセス間の関係。 |""",
            )
            errors, _ = CHECKER.check_pair(english, japanese, set(CHECKER.DEFAULT_JA_TERMS), "fixture")
            self.assertTrue(
                any(
                    "relationship provider/recipient endpoint identity or order differs"
                    in error
                    for error in errors
                ),
                errors,
            )

    def test_shipped_reference_model_pair_passes_named_endpoint_comparison(self) -> None:
        root = Path(__file__).parents[1]
        english = root / "skills" / "alps-reference-model" / "SKILL.md"
        japanese = (
            english.parent / "references" / "locales" / "ja" / "SKILL.md"
        )
        errors, _ = CHECKER.check_pair(english, japanese, set(CHECKER.DEFAULT_JA_TERMS), "mashimashica/alps")
        self.assertEqual(errors, [], errors)


if __name__ == "__main__":
    unittest.main()
