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


def process_reference_model_with_heading_level(
    root: Path,
    entry_level: int,
    child_level: int | None = None,
    malformed: bool = False,
    boundary_fixture: bool = False,
    custom_heading_level: int | None = None,
) -> Path:
    path = root / "skills" / "fixture-reference-model" / "SKILL.md"
    entry = "#" * entry_level
    child = "#" * (child_level or entry_level + 1)
    purpose_heading = "#" * (entry_level if malformed else child_level or entry_level + 1)
    custom = (
        f"{'#' * custom_heading_level} Notes\n\nEvidence for One.\n\n"
        + chr(96) + "skill:#one" + chr(96) + "\n\n"
        if custom_heading_level is not None
        else ""
    )
    first_reference = (
        ""
        if custom_heading_level is not None
        else chr(96) + "skill:#one" + chr(96) + "\n\n"
    )
    tail = "\n### Fake from a later section\n\nIgnored.\n" if boundary_fixture else ""
    write(
        path,
        f"""---
name: fixture-reference-model
description: A fixture Process Reference Model.
metadata:
  alps.kind: process-reference-model
---

# Fixture Reference Model

## Purpose

The fixture defines two reference Processes.

## Processes

{entry} One

{purpose_heading} Purpose

One purpose.

{custom}
{child} Outcomes

- One is achieved.

{first_reference}

{entry} Two

{child} Purpose

Two purpose.

{child} Outcomes

- Two is achieved.

`skill:#two`

## Relationships

| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| One | information | Two | relates the Processes. |
{tail}""",
    )
    return path


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


def write_process_view_pair(
    root: Path,
    english_included: str,
    japanese_included: str,
) -> tuple[Path, Path]:
    english = root / "view" / "SKILL.md"
    japanese = english.parent / "references" / "locales" / "ja" / "SKILL.md"
    write(
        english,
        """---
name: fixture-view
description: Fixture Process View.
metadata:
  alps.kind: process-view
---

# Fixture View

## Purpose

The fixture organizes source Processes.

## Outcomes

- The source Processes are represented.

## Source Processes

- One
- Two

## Included Activities and Tasks

"""
        + english_included
        + """

## Application

The fixture provides application guidance.
""",
    )
    write(
        japanese,
        """---
name: fixture-view
description: フィクスチャのプロセスビュー。
metadata:
  alps.kind: process-view
---

# フィクスチャビュー

## 目的

出典プロセスを整理する。

## 成果

- 出典プロセスを表現する。

## 出典プロセス

- 一
- 二

## 含まれる活動およびタスク

"""
        + japanese_included
        + """

## 適用

フィクスチャを適用できる。
""",
    )
    return english, japanese


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


def write_table_process_model_pair(
    root: Path,
    japanese_relationships: str,
    english_relationships: str = "- One -> Two",
) -> tuple[Path, Path]:
    english, japanese = write_process_model_pair(
        root, japanese_relationships, english_relationships
    )
    write(
        english,
        english.read_text(encoding="utf-8").replace(
            "## Processes\n\n- One\n- Two",
            "## Processes\n\n"
            "| Process | Skill |\n"
            "| --- | --- |\n"
            "| One | `skill:#one` |\n"
            "| Two | `skill:#two` |",
        ),
    )
    write(
        japanese,
        japanese.read_text(encoding="utf-8").replace(
            "## プロセス\n\n- 一\n- 二",
            "## プロセス\n\n"
            "| プロセス | スキル |\n"
            "| --- | --- |\n"
            "| 一 | `skill:#one` |\n"
            "| 二 | `skill:#two` |",
        ),
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

    def test_process_reference_model_accepts_entry_heading_levels_three_to_five(self) -> None:
        for entry_level in (3, 4, 5):
            with self.subTest(entry_level=entry_level), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                reference_process_skill(root, "one", "One")
                reference_process_skill(root, "two", "Two")
                path = process_reference_model_with_heading_level(root, entry_level)
                errors, _ = CHECKER.check_asset(path, {"": root}, None)
                self.assertEqual(errors, [], (entry_level, errors))

    def test_process_reference_model_keeps_deeper_custom_headings_in_entry_body(self) -> None:
        for entry_level in (3, 4):
            with self.subTest(entry_level=entry_level), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                reference_process_skill(root, "one", "One")
                reference_process_skill(root, "two", "Two")
                path = process_reference_model_with_heading_level(
                    root,
                    entry_level,
                    custom_heading_level=5,
                )
                errors, _ = CHECKER.check_asset(path, {"": root}, None)
                self.assertEqual(errors, [], (entry_level, errors))

    def test_process_reference_model_rejects_malformed_child_level_and_ignores_fake_headings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reference_process_skill(root, "one", "One")
            reference_process_skill(root, "two", "Two")
            malformed = process_reference_model_with_heading_level(root, 4, malformed=True)
            errors, _ = CHECKER.check_asset(malformed, {"": root}, None)
            self.assertTrue(
                any("One: non-empty Purpose and Outcomes are required" in error for error in errors),
                errors,
            )

            valid = process_reference_model_with_heading_level(
                root,
                5,
                boundary_fixture=True,
            )
            fence = chr(96) * 3
            content = valid.read_text(encoding="utf-8").replace(
                chr(96) + "skill:#one" + chr(96) + "\n\n",
                (
                    chr(96) + "skill:#one" + chr(96) + "\n\n"
                    "The prose mentions ### Fake but is not a heading.\n\n"
                    "<!--\n### Comment fake\n-->\n\n"
                    + fence + "markdown\n### Code fake\n" + fence + "\n\n"
                ),
            )
            write(valid, content)
            errors, _ = CHECKER.check_asset(valid, {"": root}, None)
            self.assertEqual(errors, [], errors)

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

    def test_process_view_pair_compares_structured_non_table_included_elements(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            english, japanese = write_process_view_pair(
                Path(directory),
                "- Activity: Work\n- Task: Review",
                "- 活動: 作業\n- タスク: 確認",
            )
            self.assertEqual(
                CHECKER.check_asset(english, {"": root}, "fixture")[0],
                [],
            )
            self.assertEqual(
                CHECKER.check_asset(japanese, {"": root}, "fixture")[0],
                [],
            )
            errors, warnings = CHECKER.check_pair(
                english,
                japanese,
                set(CHECKER.DEFAULT_JA_TERMS),
                "fixture",
            )
            self.assertEqual(errors, [], errors)
            self.assertEqual(warnings, [], warnings)

        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_process_view_pair(
                Path(directory),
                "### Activity: Work\n#### Task: Review",
                "### 活動: 作業\n#### タスク: 確認",
            )
            errors, warnings = CHECKER.check_pair(
                english,
                japanese,
                set(CHECKER.DEFAULT_JA_TERMS),
                "fixture",
            )
            self.assertEqual(errors, [], errors)
            self.assertEqual(warnings, [], warnings)

        for english_included, japanese_included, expected in (
            (
                "- Activity: Work\n- Task: Review",
                "- 活動: 作業",
                "included Activity/Task count differs",
            ),
            (
                "- Activity: Work\n    - Task: Review",
                "- 活動: 作業",
                "included Activity/Task count differs",
            ),
            (
                "- Activity: Work\n- Task: Review",
                "- タスク: 確認\n- 活動: 作業",
                "included Activity/Task kind/order differs",
            ),
        ):
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as directory:
                english, japanese = write_process_view_pair(
                    Path(directory), english_included, japanese_included
                )
                errors, _ = CHECKER.check_pair(
                    english,
                    japanese,
                    set(CHECKER.DEFAULT_JA_TERMS),
                    "fixture",
                )
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_outcome_items_merge_mixed_forms_in_order_and_mask_code(self) -> None:
        table = """| Outcome | Reference |
| --- | --- |
| First | `skill:#one` |
| Second | `skill:#two` |"""
        mixed = (
            table
            + "\n\n- Third (`skill:#three`)\n\n"
            + "<!-- - Hidden -->\n\n"
            + "```markdown\n"
            + table
            + "\n- Missing (`skill:#does-not-exist`)\n```")
        self.assertEqual(
            CHECKER.outcome_items(mixed),
            [
                "First | `skill:#one`",
                "Second | `skill:#two`",
                "Third (`skill:#three`)",
            ],
        )
        self.assertEqual(
            CHECKER.outcome_items(table),
            ["First | `skill:#one`", "Second | `skill:#two`"],
        )
        self.assertEqual(CHECKER.outcome_items("- First\n- Second"), ["First", "Second"])
        self.assertEqual(
            CHECKER.outcome_items("First outcome.\n\nSecond outcome."),
            ["First outcome.", "Second outcome."],
        )
        self.assertEqual(
            CHECKER.outcome_items(table + "\n\nCategory label prose."),
            ["First | `skill:#one`", "Second | `skill:#two`"],
        )

    def test_process_view_pair_compares_mixed_outcome_entries(self) -> None:
        english_outcomes = """| Outcome | Reference |
| --- | --- |
| First | `skill:#one` |

- Second (`skill:#two`)"""
        japanese_outcomes = """| 成果 | 参照 |
| --- | --- |
| 一つ目 | `skill:#one` |

- 二つ目 (`skill:#two`)"""

        def install_outcomes(
            english: Path, japanese: Path, en_value: str, ja_value: str
        ) -> None:
            for path, heading, next_heading, value in (
                (english, "## Outcomes\n\n", "\n\n## Source Processes", en_value),
                (japanese, "## 成果\n\n", "\n\n## 出典プロセス", ja_value),
            ):
                text = path.read_text(encoding="utf-8")
                prefix, remainder = text.split(heading, 1)
                _, suffix = remainder.split(next_heading, 1)
                write(path, prefix + heading + value + next_heading + suffix)

        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_process_view_pair(
                Path(directory), "- Activity: Work", "- 活動: 作業"
            )
            install_outcomes(english, japanese, english_outcomes, japanese_outcomes)
            errors, _ = CHECKER.check_pair(
                english, japanese, set(CHECKER.DEFAULT_JA_TERMS), "fixture"
            )
            self.assertEqual(errors, [], errors)

            install_outcomes(
                english,
                japanese,
                english_outcomes,
                "- 二つ目\n\n" + japanese_outcomes.split("\n\n", 1)[0],
            )
            errors, _ = CHECKER.check_pair(
                english, japanese, set(CHECKER.DEFAULT_JA_TERMS), "fixture"
            )
            self.assertTrue(any("Outcome kind/order differs" in error for error in errors), errors)

            install_outcomes(english, japanese, english_outcomes, japanese_outcomes.split("\n\n", 1)[0])
            errors, _ = CHECKER.check_pair(
                english, japanese, set(CHECKER.DEFAULT_JA_TERMS), "fixture"
            )
            self.assertTrue(any("Outcome count differs" in error for error in errors), errors)

            install_outcomes(
                english,
                japanese,
                english_outcomes,
                japanese_outcomes.replace(
                    "- 二つ目 (`skill:#two`)", "- 一つ目 (`skill:#one`)"
                ),
            )
            errors, _ = CHECKER.check_pair(
                english, japanese, set(CHECKER.DEFAULT_JA_TERMS), "fixture"
            )
            self.assertTrue(
                any("Outcome reference identity or order differs" in error for error in errors),
                errors,
            )

    def test_process_view_pair_counts_keyword_free_tasks_under_activity_headings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_process_view_pair(
                Path(directory),
                "### Activity: Work\n- Review inputs",
                "### 活動: 作業\n- 入力を確認",
            )
            errors, warnings = CHECKER.check_pair(
                english,
                japanese,
                set(CHECKER.DEFAULT_JA_TERMS),
                "fixture",
            )
            self.assertEqual(errors, [], errors)
            self.assertEqual(warnings, [], warnings)

        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_process_view_pair(
                Path(directory),
                "### Work\n- Review inputs\n- Confirm output",
                "### 作業\n- 出力を確認",
            )
            errors, _ = CHECKER.check_pair(
                english,
                japanese,
                set(CHECKER.DEFAULT_JA_TERMS),
                "fixture",
            )
            self.assertTrue(
                any("included Activity/Task count differs" in error for error in errors),
                errors,
            )

    def test_process_view_accepts_valid_non_table_canonical_inclusions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            process_skill(root, "one", "One")
            process_skill(root, "two", "Two")
            path = process_view(
                root,
                "- One (`skill:fixture#one`)\n- Two (`skill:#two`)",
                "- Task One (`skill:#one`)\n- Task Two (`skill:fixture#two`)",
            )
            errors, _ = CHECKER.check_asset(
                path,
                {"": root, "fixture": root},
                "fixture",
            )
            self.assertEqual(errors, [], errors)

    def test_process_view_rejects_non_table_inclusion_missing_canonical_reference(self) -> None:
        errors = check_view_fixture(
            "- One\n- Two",
            "- Task Missing (`skill:#does-not-exist`)",
        )
        self.assertTrue(
            any("unresolved Skill reference skill:#does-not-exist" in error for error in errors),
            errors,
        )

    def test_process_view_rejects_non_table_inclusion_undeclared_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            process_skill(root, "one", "One")
            process_skill(root, "two", "Two")
            process_skill(root, "three", "Three")
            path = process_view(
                root,
                "- One\n- Two",
                "- Activity: Work (`skill:#three`)",
            )
            errors, _ = CHECKER.check_asset(path, {"": root}, None)
        self.assertTrue(
            any("undeclared Source Process" in error for error in errors),
            errors,
        )

    def test_process_view_validates_all_source_process_tables(self) -> None:
        valid_sources = """| Source Process | Reference |
| --- | --- |
| One | skill:#one |

### Other Sources

| Source Process | Reference |
| --- | --- |
| Two | skill:#two |"""
        included = """| Source Process | Source element |
| --- | --- |
| One | Activity |
| Two | Task |"""
        self.assertEqual(check_view_fixture(valid_sources, included), [])

    def test_process_view_rejects_wrong_source_in_later_source_table(self) -> None:
        sources = """| Source Process | Reference |
| --- | --- |
| One | skill:#one |
| Two | skill:#two |

### Other Sources

| Source Process | Reference |
| --- | --- |
| Totally Wrong | skill:#one |"""
        included = """| Source Process | Source element |
| --- | --- |
| One | Activity |
| Two | Task |"""
        errors = check_view_fixture(sources, included)
        self.assertTrue(
            any("differs from referenced Process 'One'" in error for error in errors),
            errors,
        )

    def test_process_view_combines_source_tables_and_outside_entries(self) -> None:
        valid_sources = """| Source Process | Reference |
| --- | --- |
| One | `skill:#one` |

- Two (`skill:#two`)

```markdown
| Source Process | Reference |
| --- | --- |
| Missing | `skill:#does-not-exist` |
- Missing (`skill:#does-not-exist`)
```"""
        self.assertEqual(
            CHECKER.source_entries(valid_sources),
            ["One", "Two (`skill:#two`)",],
        )
        included = """| Source Process | Source element |
| --- | --- |
| One | Activity |"""
        self.assertEqual(check_view_fixture(valid_sources, included), [])

        wrong_sources = valid_sources.split("\n\n```", 1)[0].replace(
            "- Two (`skill:#two`)",
            "- Totally Wrong (`skill:#one`)",
        )
        wrong_errors = check_view_fixture(wrong_sources, included)
        self.assertTrue(
            any("differs from referenced Process 'One'" in error for error in wrong_errors),
            wrong_errors,
        )

        missing_sources = valid_sources.split("\n\n```", 1)[0].replace(
            "- Two (`skill:#two`)",
            "- Missing (`skill:#does-not-exist`)",
        )
        missing_errors = check_view_fixture(missing_sources, included)
        self.assertTrue(
            any("unresolved Skill reference skill:#does-not-exist" in error for error in missing_errors),
            missing_errors,
        )

    def test_process_view_pair_combines_mixed_source_table_and_outside_order(self) -> None:
        table_en = """| Source Process | Reference |
| --- | --- |
| One | `skill:#one` |"""
        table_ja = """| 出典プロセス | 参照 |
| --- | --- |
| 一 | `skill:#one` |"""

        def check_pair_case(english_sources: str, japanese_sources: str) -> list[str]:
            with tempfile.TemporaryDirectory() as directory:
                english, japanese = write_process_view_pair(
                    Path(directory), "- Activity: Work", "- 活動: 作業"
                )
                write(
                    english,
                    english.read_text(encoding="utf-8").replace(
                        "- One\n- Two", english_sources
                    ),
                )
                write(
                    japanese,
                    japanese.read_text(encoding="utf-8").replace(
                        "- 一\n- 二", japanese_sources
                    ),
                )
                errors, _ = CHECKER.check_pair(
                    english,
                    japanese,
                    set(CHECKER.DEFAULT_JA_TERMS),
                    "fixture",
                )
                return errors

        mixed_en = table_en + "\n\n- Two (`skill:#two`)"
        mixed_ja = table_ja + "\n\n- 二 (`skill:#two`)"
        cases = (
            ("valid mixed source form", mixed_en, mixed_ja, None),
            ("outside omission", mixed_en, table_ja, "Source Process count differs"),
            (
                "outside order",
                mixed_en,
                "- 二 (`skill:#two`)\n\n" + table_ja,
                "Source Process reference identity or order differs",
            ),
            (
                "outside identity",
                mixed_en,
                table_ja + "\n\n- 一 (`skill:#one`)",
                "Source Process reference identity or order differs",
            ),
        )
        for name, english_sources, japanese_sources, expected in cases:
            with self.subTest(name=name):
                errors = check_pair_case(english_sources, japanese_sources)
                if expected is None:
                    self.assertEqual(errors, [], errors)
                else:
                    self.assertTrue(any(expected in error for error in errors), errors)

    def test_process_view_pair_compares_all_source_process_tables(self) -> None:
        def source_table(
            header: str, rows: str, reference_header: str = "Reference"
        ) -> str:
            return f"""| {header} | {reference_header} |
| --- | --- |
{rows}"""

        first_en = source_table("Source Process", "| One | `skill:#one` |")
        second_en = source_table("Source Process", "| Two | `skill:#two` |")
        first_ja = source_table("出典プロセス", "| 一 | `skill:#one` |", "参照")
        second_ja = source_table("出典プロセス", "| 二 | `skill:#two` |", "参照")

        def check_pair_case(english_sources: str, japanese_sources: str) -> list[str]:
            with tempfile.TemporaryDirectory() as directory:
                english, japanese = write_process_view_pair(
                    Path(directory), "- Activity: Work", "- 活動: 作業"
                )
                write(
                    english,
                    english.read_text(encoding="utf-8").replace(
                        "- One\n- Two", english_sources
                    ),
                )
                write(
                    japanese,
                    japanese.read_text(encoding="utf-8").replace(
                        "- 一\n- 二", japanese_sources
                    ),
                )
                errors, _ = CHECKER.check_pair(
                    english,
                    japanese,
                    set(CHECKER.DEFAULT_JA_TERMS),
                    "fixture",
                )
                return errors

        cases = (
            (
                "multiple valid tables",
                first_en + "\n\n" + second_en,
                first_ja + "\n\n" + second_ja,
                None,
            ),
            (
                "later-table omission",
                first_en + "\n\n" + second_en,
                first_ja,
                "Source Process count differs",
            ),
            (
                "later-table order",
                first_en + "\n\n" + second_en,
                second_ja + "\n\n" + first_ja,
                "Source Process reference identity or order differs",
            ),
            (
                "later-table identity",
                first_en + "\n\n" + second_en,
                first_ja
                + "\n\n"
                + source_table("出典プロセス", "| 一 | `skill:#one` |", "参照"),
                "Source Process reference identity or order differs",
            ),
        )
        for name, english_sources, japanese_sources, expected in cases:
            with self.subTest(name=name):
                errors = check_pair_case(english_sources, japanese_sources)
                if expected is None:
                    self.assertEqual(errors, [], errors)
                else:
                    self.assertTrue(any(expected in error for error in errors), errors)

    def test_process_view_validates_non_table_items_after_provenance_table(self) -> None:
        valid = """| Source Process | Source element |
| --- | --- |
| One | Activity |

### Activity: Work
- Task Two (`skill:#two`)"""
        self.assertEqual(check_view_fixture("- One\n- Two", valid), [])

        missing = valid.replace(
            "Task Two (`skill:#two`)",
            "Task Missing (`skill:#does-not-exist`)",
        )
        errors = check_view_fixture("- One\n- Two", missing)
        self.assertTrue(
            any("unresolved Skill reference skill:#does-not-exist" in error for error in errors),
            errors,
        )

    def test_process_view_pair_compares_mixed_provenance_and_non_table_items(self) -> None:
        table_en = """| Source Process | Source element |
| --- | --- |
| One (`skill:#one`) | Activity |"""
        table_ja = """| 出典プロセス | 出典要素 |
| --- | --- |
| 一 (`skill:#one`) | 活動 |"""
        outside_en = "### Activity: Work\n- Task Two (`skill:#two`)"
        outside_ja = "### 活動: 作業\n- タスク 二 (`skill:#two`)"

        def check_pair_case(english_included: str, japanese_included: str) -> list[str]:
            with tempfile.TemporaryDirectory() as directory:
                english, japanese = write_process_view_pair(
                    Path(directory), english_included, japanese_included
                )
                english_text = english.read_text(encoding="utf-8").replace(
                    "- One\n- Two",
                    "- One (`skill:#one`)\n- Two (`skill:#two`)",
                )
                japanese_text = japanese.read_text(encoding="utf-8").replace(
                    "- 一\n- 二",
                    "- 一 (`skill:#one`)\n- 二 (`skill:#two`)",
                )
                write(english, english_text)
                write(japanese, japanese_text)
                errors, _ = CHECKER.check_pair(
                    english,
                    japanese,
                    set(CHECKER.DEFAULT_JA_TERMS),
                    "fixture",
                )
                return errors

        cases = (
            (
                "valid mixed forms",
                table_en + "\n\n" + outside_en,
                table_ja + "\n\n" + outside_ja,
                None,
            ),
            (
                "outside omission",
                table_en + "\n\n" + outside_en,
                table_ja,
                "included Activity/Task count differs",
            ),
            (
                "outside order",
                table_en + "\n\n" + outside_en,
                outside_ja + "\n\n" + table_ja,
                "included source identity or order differs",
            ),
            (
                "outside identity",
                table_en + "\n\n" + outside_en,
                table_ja + "\n\n" + outside_ja.replace("skill:#two", "skill:#one"),
                "included source identity or order differs",
            ),
        )
        for name, english_included, japanese_included, expected in cases:
            with self.subTest(name=name):
                errors = check_pair_case(english_included, japanese_included)
                if expected is None:
                    self.assertEqual(errors, [], errors)
                else:
                    self.assertTrue(any(expected in error for error in errors), errors)

    def test_process_view_validates_every_provenance_table_and_ignores_fenced_tables(self) -> None:
        included = """| Source Process | Source element |
| --- | --- |
| One | Activity |

### Categorized Tasks

```markdown
| Source Process | Source element |
| --- | --- |
| Missing | Task |
```

| Source Process | Source element |
| --- | --- |
| Two | Task |"""
        self.assertEqual(check_view_fixture("- One\n- Two", included), [])

    def test_process_view_rejects_undeclared_source_in_later_provenance_table(self) -> None:
        included = """| Source Process | Source element |
| --- | --- |
| One | Activity |

### Categorized Tasks

| Source Process | Source element |
| --- | --- |
| Missing | Task |"""
        errors = check_view_fixture("- One\n- Two", included)
        self.assertTrue(any("undeclared Source Process" in error for error in errors), errors)

    def test_process_view_pair_compares_every_provenance_table(self) -> None:
        first_en = """| Source Process | Source element |
| --- | --- |
| One (`skill:#one`) | Activity |"""
        first_ja = """| 出典プロセス | 出典要素 |
| --- | --- |
| 一 (`skill:#one`) | 活動 |"""
        second_en_one = """| Source Process | Source element |
| --- | --- |
| Two (`skill:#two`) | Task |"""
        second_ja_one = """| 出典プロセス | 出典要素 |
| --- | --- |
| 二 (`skill:#two`) | タスク |"""

        def check_pair_case(english_included: str, japanese_included: str) -> list[str]:
            with tempfile.TemporaryDirectory() as directory:
                english, japanese = write_process_view_pair(
                    Path(directory), english_included, japanese_included
                )
                english_text = english.read_text(encoding="utf-8").replace(
                    "- One\n- Two",
                    "- One (`skill:#one`)\n- Two (`skill:#two`)",
                )
                japanese_text = japanese.read_text(encoding="utf-8").replace(
                    "- 一\n- 二",
                    "- 一 (`skill:#one`)\n- 二 (`skill:#two`)",
                )
                write(english, english_text)
                write(japanese, japanese_text)
                errors, _ = CHECKER.check_pair(
                    english,
                    japanese,
                    set(CHECKER.DEFAULT_JA_TERMS),
                    "fixture",
                )
                return errors

        cases = (
            (
                "second-table omission",
                first_en + "\n\n" + second_en_one,
                first_ja,
                "included provenance table count differs",
            ),
            (
                "second-table count",
                first_en + "\n\n" + second_en_one + "\n| One (`skill:#one`) | Task |",
                first_ja + "\n\n" + second_ja_one,
                "included source-element count differs",
            ),
            (
                "second-table order",
                first_en
                + "\n\n"
                + """| Source Process | Source element |
| --- | --- |
| One (`skill:#one`) | Task |
| Two (`skill:#two`) | Task |""",
                first_ja
                + "\n\n"
                + """| 出典プロセス | 出典要素 |
| --- | --- |
| 二 (`skill:#two`) | タスク |
| 一 (`skill:#one`) | タスク |""",
                "included source provenance or order differs",
            ),
            (
                "second-table identity",
                first_en + "\n\n" + second_en_one,
                first_ja
                + "\n\n"
                + """| 出典プロセス | 出典要素 |
| --- | --- |
| 一 (`skill:#one`) | タスク |""",
                "included source provenance or order differs",
            ),
        )
        for name, english_included, japanese_included, expected in cases:
            with self.subTest(name=name):
                errors = check_pair_case(english_included, japanese_included)
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_process_view_pair_compares_stable_included_source_identity(self) -> None:
        reference_one = chr(96) + "skill:#one" + chr(96)
        reference_two = chr(96) + "skill:#two" + chr(96)
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_process_view_pair(
                Path(directory),
                "- Activity: Work (" + reference_one + ")\n"
                "- Task: Review (" + reference_two + ")",
                "- 活動: 作業 (" + reference_two + ")\n"
                "- タスク: 確認 (" + reference_one + ")",
            )
            errors, _ = CHECKER.check_pair(
                english,
                japanese,
                set(CHECKER.DEFAULT_JA_TERMS),
                "fixture",
            )
            self.assertTrue(
                any("included source identity or order differs" in error for error in errors),
                errors,
            )

    def test_process_view_non_table_extractor_ignores_code_and_comments(self) -> None:
        fence = chr(96) * 3
        included = (
            fence
            + "markdown\n### Activity: Hidden\n"
            + fence
            + "\n<!--\n- Task: Hidden\n-->\n"
            "- Activity: Work\n"
            "    - Task: Hidden continuation code\n"
        )
        self.assertEqual(
            CHECKER.included_semantic_elements(included, "en", "fixture"),
            [("activity", None), ("task", None)],
        )
        self.assertEqual(
            CHECKER.included_semantic_elements(
                "- 活動: 作業\n    - タスク: 確認\n", "ja", "fixture"
            ),
            [("activity", None), ("task", None)],
        )
        self.assertEqual(
            CHECKER.included_semantic_elements(
                "Paragraph\n\n    - Activity: Hidden\n    - Task: Hidden\n",
                "en",
                "fixture",
            ),
            [],
        )
        self.assertEqual(
            CHECKER.included_semantic_elements(
                "    Activity: Hidden\n        Task: Hidden\n",
                "en",
                "fixture",
            ),
            [],
        )
        self.assertEqual(
            check_view_fixture("- One\n- Two", included),
            [],
        )
        self.assertEqual(
            check_view_fixture(
                "- One\n- Two",
                "### Activity: Work\n#### Task: Review",
            ),
            [],
        )

    def test_process_view_heading_extractor_uses_shallowest_activity_level(self) -> None:
        included = """### Work
- Activity: Work step
#### Notes
- Task: explanatory Task text is not a semantic item
#### Activity: Nested example
- Task: nested explanatory item is not a semantic item
### Review
- Task: Review step
"""
        self.assertEqual(
            CHECKER.included_semantic_elements(included, "en", "fixture"),
            [
                ("activity", None),
                ("task", None),
                ("activity", None),
                ("task", None),
            ],
        )
        self.assertEqual(
            CHECKER.included_semantic_elements(
                "#### Work\n- 活動: 作業\n##### Notes\n- タスク: 説明\n#### Review\n- タスク: 確認\n",
                "ja",
                "fixture",
            ),
            [
                ("activity", None),
                ("task", None),
                ("activity", None),
                ("task", None),
            ],
        )

    def test_process_view_heading_extractor_ignores_shallower_task_heading(self) -> None:
        included = """### Task: explanatory section
#### Activity: Work
##### Task: Review
"""
        self.assertEqual(
            CHECKER.included_semantic_elements(included, "en", "fixture"),
            [("activity", None), ("task", None)],
        )

    def test_process_view_heading_extractor_preserves_task_kind_at_activity_level(self) -> None:
        included = """### Activity: Work
### Task: explanatory task
"""
        self.assertEqual(
            CHECKER.included_semantic_elements(included, "en", "fixture"),
            [("activity", None), ("task", None)],
        )

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

    def test_process_model_accepts_heading_form_process_entries(self) -> None:
        processes = """### One

#### Notes

This explanatory heading is not a Process entry.

```markdown
### Fake from code
```

    ### Fake from indented code

### Two

#### Details

This deeper heading is not a Process entry.
"""
        self.assertEqual(CHECKER.process_model_entries(processes), ["One", "Two"])
        self.assertEqual(check_model("- One -> Two", processes), [])

    def test_process_model_merges_mixed_process_entries_and_masks_code(self) -> None:
        processes = """| Process | Skill |
| --- | --- |
| One | `skill:#one` |

- Two

### Three

#### Notes

This is explanatory text.

```markdown
| Process | Skill |
| --- | --- |
| Missing | `skill:#does-not-exist` |
- Missing
```
"""
        self.assertEqual(
            CHECKER.process_model_entries(processes),
            ["One", "Two", "Three"],
        )
        self.assertEqual(
            CHECKER.process_model_identities(processes, "fixture"),
            {
                "One": "ref:fixture#one",
                "Two": "name:Two",
                "Three": "name:Three",
            },
        )
        self.assertEqual(check_model("- One -> Two", processes), [])

        missing = processes.replace(
            "- Two\n\n### Three", "- Missing (`skill:#does-not-exist`)\n\n### Three"
        )
        errors = check_model("- One -> Two", missing)
        self.assertTrue(
            any("unresolved Skill reference skill:#does-not-exist" in error for error in errors),
            errors,
        )

    def test_process_model_pair_compares_mixed_process_entries(self) -> None:
        english_processes = """| Process | Description |
| --- | --- |
| One | first Process |

- Two
"""
        japanese_processes = """| プロセス | 説明 |
| --- | --- |
| 一 | 最初のプロセス |

- 二
"""
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_process_model_pair(
                Path(directory), "- 一 -> 二", "- One -> Two"
            )
            write(
                english,
                english.read_text(encoding="utf-8").replace(
                    "- One\n- Two", english_processes.strip()
                ),
            )
            write(
                japanese,
                japanese.read_text(encoding="utf-8").replace(
                    "- 一\n- 二", japanese_processes.strip()
                ),
            )
            errors, _ = CHECKER.check_pair(
                english, japanese, set(CHECKER.DEFAULT_JA_TERMS), "fixture"
            )
            self.assertEqual(errors, [], errors)

            write(
                japanese,
                japanese.read_text(encoding="utf-8").replace("\n\n- 二", ""),
            )
            errors, _ = CHECKER.check_pair(
                english, japanese, set(CHECKER.DEFAULT_JA_TERMS), "fixture"
            )
            self.assertTrue(
                any("Process count differs" in error for error in errors),
                errors,
            )

        canonical_en = """| Process | Skill |
| --- | --- |
| One | `skill:#one` |

- Two (`skill:#two`)
"""
        canonical_ja = """| プロセス | スキル |
| --- | --- |
| 一 | `skill:#one` |

- 二 (`skill:#two`)
"""
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_process_model_pair(
                Path(directory), "- 一 -> 二", "- One -> Two"
            )
            write(
                english,
                english.read_text(encoding="utf-8").replace(
                    "- One\n- Two", canonical_en.strip()
                ),
            )
            write(
                japanese,
                japanese.read_text(encoding="utf-8").replace(
                    "- 一\n- 二",
                    canonical_ja.replace(
                        "- 二 (`skill:#two`)",
                        "- 一 (`skill:#one`) -> 二 (`skill:#two`)",
                    ).strip(),
                ),
            )
            errors, _ = CHECKER.check_pair(
                english, japanese, set(CHECKER.DEFAULT_JA_TERMS), "fixture"
            )
            self.assertTrue(
                any("Process reference identity or order differs" in error for error in errors),
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

    def test_process_models_reject_single_canonical_relationship_list_items(self) -> None:
        for checker in (check_model, check_reference_model_fixture):
            with self.subTest(checker=checker.__name__):
                errors = checker("- skill:#one")
                self.assertTrue(
                    any(
                        "relationship item 1 must identify provider and recipient Processes"
                        in error
                        for error in errors
                    ),
                    errors,
                )

    def test_process_models_accept_canonical_provider_and_recipient_relationships(self) -> None:
        self.assertEqual(check_model("- skill:#one -> skill:#two"), [])
        self.assertEqual(check_reference_model_fixture("- skill:#one -> skill:#two"), [])

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
        self.assertEqual(
            CHECKER.references(inline_comment + " skill:#one"),
            ["skill:#one"],
        )

    def test_reference_scan_ignores_top_level_and_list_indented_code(self) -> None:
        value = """Relationships:

    skill:#missing

- One -> Two skill:#one
  Continuation keeps skill:#two operative.

      skill:#missing
"""
        self.assertEqual(
            CHECKER.references(value),
            ["skill:#one", "skill:#two"],
        )

    def test_reference_scan_ignores_blockquoted_fences_and_indented_code(self) -> None:
        backticks = chr(96) * 3
        tildes = chr(126) * 3
        quoted_code = (
            "> " + backticks + "text\n"
            "> skill:#missing\n"
            "> " + backticks + "\n"
            "> > " + tildes + "text\n"
            "> > skill:#missing\n"
            "> > " + tildes + "\n"
            ">     skill:#missing\n"
            "> >     skill:#missing\n"
        )
        self.assertEqual(CHECKER.references(quoted_code), [])
        self.assertEqual(
            CHECKER.references("> See skill:#one here.\n"),
            ["skill:#one"],
        )
        self.assertEqual(
            CHECKER.references(
                "> - One -> Two skill:#one\n"
                ">   Continuation keeps skill:#two operative.\n"
            ),
            ["skill:#one", "skill:#two"],
        )

    def test_reference_scan_masks_fences_nested_in_list_containers(self) -> None:
        tildes = chr(126) * 3
        value = (
            "- outer item\n"
            "    " + tildes + "\n"
            "    skill:#missing\n"
            "    " + (chr(126) * 4) + "\n"
            "- visible skill:#one\n"
            "  - nested item\n"
            "      " + tildes + "\n"
            "      skill:#missing-nested\n"
            "      " + (chr(126) * 5) + "\n"
            "> - quoted item\n"
            ">     " + tildes + "\n"
            ">     skill:#missing-quoted\n"
            ">     " + (chr(126) * 4) + "\n"
            "> - visible skill:#two\n"
        )
        self.assertEqual(
            CHECKER.references(value),
            ["skill:#one", "skill:#two"],
        )

        ordinary_code = (
            "    " + tildes + "\n"
            "    skill:#ordinary-code\n"
            "    " + tildes + "\n"
            "\nParagraph skill:#three\n"
        )
        self.assertIn("skill:#ordinary-code", CHECKER.without_fenced_code(ordinary_code))
        self.assertEqual(CHECKER.references(ordinary_code), ["skill:#three"])

    def test_reference_scan_masks_only_markdown_link_destination_spans(self) -> None:
        inline = "[one](skill:#missing) [two](skill:#missing)\nskill:#missing"
        self.assertEqual(
            CHECKER.markdown_link_targets(inline),
            ["skill:#missing", "skill:#missing"],
        )
        self.assertEqual(CHECKER.references(inline), ["skill:#missing"])

        definitions = "[one]: skill:#missing\n[two]: skill:#missing\n\nskill:#missing"
        self.assertEqual(
            CHECKER.markdown_link_targets(definitions),
            ["skill:#missing", "skill:#missing"],
        )
        self.assertEqual(CHECKER.references(definitions), ["skill:#missing"])

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

    def test_frontmatter_aliases_select_view_kind_and_validate_view_sections(self) -> None:
        forms = (
            "view-kind: &view-kind {alps.kind: process-view}\n"
            "metadata: *view-kind\n",
            "view-kind: &view-kind {alps.kind: process-view}\n"
            "metadata: !!map *view-kind\n",
            "representations:\n"
            "  view-kind: &view-kind\n"
            "    alps.kind: process-view\n"
            "metadata: *view-kind\n",
        )
        for form in forms:
            with self.subTest(form=form):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    path = root / "skills" / "fixture" / "SKILL.md"
                    write(
                        path,
                        "---\n"
                        "name: fixture\n"
                        "description: Fixture process. ALPS-conformant.\n"
                        + form
                        + "---\n\n"
                        "# Fixture\n\n"
                        "## Purpose\n\n"
                        "The fixture has a purpose.\n\n"
                        "## Outcomes\n\n"
                        "- The fixture is complete.\n",
                    )
                    values, frontmatter_errors = CHECKER.frontmatter(
                        path.read_text(encoding="utf-8")
                    )
                    self.assertEqual(frontmatter_errors, [], frontmatter_errors)
                    self.assertEqual(values["alps.kind"], "process-view")
                    self.assertEqual(CHECKER.representation_kind(path), "process-view")
                    errors, _ = CHECKER.check_asset(path, {"": root}, None)
                    self.assertTrue(
                        any("Process View requires Source Processes" in error for error in errors),
                        errors,
                    )
                    self.assertFalse(
                        any("Process representation requires" in error for error in errors),
                        errors,
                    )

    def test_frontmatter_merges_nested_metadata_aliases_before_kind_dispatch(self) -> None:
        forms = (
            "view: &view {kind: process-view}\n"
            "metadata:\n"
            "  alps: *view\n",
            "view: !!map &view {kind: !!str process-view}\n"
            "metadata:\n"
            "  alps: !!map *view\n",
            "kind: &kind process-view\n"
            "metadata: {alps: {kind: *kind}}\n",
        )
        for form in forms:
            with self.subTest(form=form):
                text = (
                    "---\n"
                    "name: fixture\n"
                    "description: Fixture process. ALPS-conformant.\n"
                    + form
                    + "---\n"
                )
                values, frontmatter_errors = CHECKER.frontmatter(text)
                self.assertEqual(frontmatter_errors, [], frontmatter_errors)
                self.assertEqual(values["alps.kind"], "process-view")
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    path = root / "skills" / "fixture" / "SKILL.md"
                    write(
                        path,
                        text
                        + "\n# Fixture\n\n## Purpose\n\nPurpose.\n\n"
                        "## Outcomes\n\n- Outcome.\n",
                    )
                    self.assertEqual(CHECKER.representation_kind(path), "process-view")
                    errors, _ = CHECKER.check_asset(path, {"": root}, None)
                    self.assertTrue(
                        any("Process View requires Source Processes" in error for error in errors),
                        errors,
                    )
                    self.assertFalse(
                        any("Process representation requires" in error for error in errors),
                        errors,
                    )

    def test_frontmatter_resolves_mapping_merge_before_kind_dispatch(self) -> None:
        text = """---
name: fixture
description: Fixture process. ALPS-conformant.
defaults: &defaults {alps: {kind: process-view}}
metadata:
  <<: *defaults
---
"""
        values, errors = CHECKER.frontmatter(text)
        self.assertEqual(errors, [], errors)
        self.assertEqual(values.get("alps.kind"), "process-view")

        override = text.replace(
            "metadata:\n  <<: *defaults",
            "metadata:\n  <<: *defaults\n  alps:\n    kind: process-model",
        )
        override_values, override_errors = CHECKER.frontmatter(override)
        self.assertEqual(override_errors, [], override_errors)
        self.assertEqual(override_values.get("alps.kind"), "process-model")

    def test_frontmatter_rejects_invalid_and_cyclic_mapping_merges(self) -> None:
        invalid = """---
name: fixture
description: Fixture process. ALPS-conformant.
kind: &kind process-view
metadata:
  <<: *kind
---
"""
        _, invalid_errors = CHECKER.frontmatter(invalid)
        self.assertTrue(
            any("YAML merge key" in error for error in invalid_errors),
            invalid_errors,
        )

        cyclic = """---
name: fixture
description: Fixture process. ALPS-conformant.
defaults: &defaults {<<: *defaults}
metadata:
  <<: *defaults
---
"""
        _, cyclic_errors = CHECKER.frontmatter(cyclic)
        self.assertTrue(
            any("cyclic YAML alias" in error for error in cyclic_errors),
            cyclic_errors,
        )

    def test_frontmatter_resolves_sequence_mapping_merges_with_precedence(self) -> None:
        text = """---
name: fixture
description: Fixture process. ALPS-conformant.
defaults: &defaults {alps: {kind: process-view}}
overrides: &overrides {alps: {kind: process-model}}
metadata:
  <<: [*defaults, *overrides]
---
"""
        values, errors = CHECKER.frontmatter(text)
        self.assertEqual(errors, [], errors)
        self.assertEqual(values.get("alps.kind"), "process-view")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "skills" / "fixture" / "SKILL.md"
            write(path, text + "\n# Fixture\n")
            self.assertEqual(CHECKER.representation_kind(path), "process-view")
            asset_errors, _ = CHECKER.check_asset(path, {"": root}, None)
            self.assertTrue(
                any("Process View requires" in error for error in asset_errors),
                asset_errors,
            )

        explicit = text.replace(
            "  <<: [*defaults, *overrides]",
            "  <<: [*defaults, *overrides]\n  alps:\n    kind: process-reference-model",
        )
        explicit_values, explicit_errors = CHECKER.frontmatter(explicit)
        self.assertEqual(explicit_errors, [], explicit_errors)
        self.assertEqual(explicit_values.get("alps.kind"), "process-reference-model")

        multiline = text.replace(
            "  <<: [*defaults, *overrides]",
            "  <<: [\n    *defaults, # first mapping\n    *overrides\n  ]",
        )
        multiline_values, multiline_errors = CHECKER.frontmatter(multiline)
        self.assertEqual(multiline_errors, [], multiline_errors)
        self.assertEqual(multiline_values.get("alps.kind"), "process-view")

        invalid = text.replace(
            "  <<: [*defaults, *overrides]",
            "  <<: [*defaults, scalar-member]",
        )
        _, invalid_errors = CHECKER.frontmatter(invalid)
        self.assertTrue(
            any("YAML merge key must resolve to a mapping" in error for error in invalid_errors),
            invalid_errors,
        )

        unresolved = text.replace(
            "  <<: [*defaults, *overrides]",
            "  <<: [*defaults, *missing]",
        )
        _, unresolved_errors = CHECKER.frontmatter(unresolved)
        self.assertTrue(
            any("unresolved YAML alias *missing" in error for error in unresolved_errors),
            unresolved_errors,
        )

        cyclic = """---
name: fixture
description: Fixture process. ALPS-conformant.
defaults: &defaults {<<: [*defaults]}
metadata:
  <<: *defaults
---
"""
        _, cyclic_errors = CHECKER.frontmatter(cyclic)
        self.assertTrue(
            any("cyclic YAML alias" in error for error in cyclic_errors),
            cyclic_errors,
        )

        block_sequence = """---
name: fixture
description: Fixture process. ALPS-conformant.
defaults: &defaults {alps: {kind: process-view}}
metadata:
  <<:
    - *defaults
---
"""
        _, block_errors = CHECKER.frontmatter(block_sequence)
        self.assertTrue(
            any("unsupported YAML block sequence" in error for error in block_errors),
            block_errors,
        )

    def test_frontmatter_accumulates_multiline_flow_metadata_before_kind_dispatch(self) -> None:
        forms = (
            "metadata: {\n"
            "  alps: {kind: process-view}\n"
            "}\n",
            "kind: &kind process-view\n"
            "metadata: !!map &metadata {\n"
            "  # metadata comment\n"
            "  alps: !!map {kind: !!str *kind} # item comment\n"
            "} # representation comment\n",
            "metadata: {\n"
            "  note: 'it''s } # text',\n"
            "  alps: {kind: process-view}\n"
            "} # representation comment\n",
        )
        for form in forms:
            with self.subTest(form=form):
                text = (
                    "---\n"
                    "name: fixture\n"
                    "description: Fixture process. ALPS-conformant.\n"
                    + form
                    + "---\n"
                )
                values, frontmatter_errors = CHECKER.frontmatter(text)
                self.assertEqual(frontmatter_errors, [], frontmatter_errors)
                self.assertEqual(values["alps.kind"], "process-view")
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    path = root / "skills" / "fixture" / "SKILL.md"
                    write(
                        path,
                        text
                        + "\n# Fixture\n\n## Purpose\n\nPurpose.\n\n"
                        "## Outcomes\n\n- Outcome.\n",
                    )
                    self.assertEqual(CHECKER.representation_kind(path), "process-view")
                    errors, _ = CHECKER.check_asset(path, {"": root}, None)
                    self.assertTrue(
                        any("Process View requires Source Processes" in error for error in errors),
                        errors,
                    )
                    self.assertFalse(
                        any("Process representation requires" in error for error in errors),
                        errors,
                    )

    def test_frontmatter_flow_quote_scanner_preserves_multiline_hash_and_brace(self) -> None:
        text = (
            "---\n"
            "name: fixture\n"
            "description: Fixture process. ALPS-conformant.\n"
            "metadata: {\n"
            "  note: \"line one\n"
            "\n"
            "    # } remains quoted\",\n"
            "  alps: {kind: process-view}\n"
            "} # representation comment\n"
            "---\n"
        )
        values, errors = CHECKER.frontmatter(text)
        self.assertEqual(errors, [], errors)
        self.assertEqual(values["metadata.note"], "line one\n# } remains quoted")
        self.assertEqual(values["alps.kind"], "process-view")

    def test_frontmatter_flow_double_quoted_line_breaks_fold_and_preserve_blanks(self) -> None:
        text = (
            "---\n"
            "name: fixture\n"
            "description: Fixture process. ALPS-conformant.\n"
            "metadata: {\n"
            '  "alps.kind": process-view,\n'
            '  note: "line one\n'
            '    line two",\n'
            '  "display\n'
            '    name": "value",\n'
            '  blank: "first\n'
            "\n"
            '    third"\n'
            "}\n"
            "---\n"
        )
        values, errors = CHECKER.frontmatter(text)
        self.assertEqual(errors, [], errors)
        self.assertEqual(values["alps.kind"], "process-view")
        self.assertEqual(values["metadata.note"], "line one line two")
        self.assertEqual(values["metadata.display name"], "value")
        self.assertEqual(values["metadata.blank"], "first\nthird")
        decoded, _, error = CHECKER.yaml_decode_quoted_scalar('"one\r\ntwo"')
        self.assertIsNone(error)
        self.assertEqual(decoded, "one two")

    def test_frontmatter_reports_invalid_and_unclosed_flow_mappings(self) -> None:
        invalid = (
            "---\n"
            "name: fixture\n"
            "description: Fixture process. ALPS-conformant.\n"
            "metadata: {alps process-view}\n"
            "---\n"
        )
        _, errors = CHECKER.frontmatter(invalid)
        self.assertTrue(any("invalid metadata flow mapping" in error for error in errors), errors)
        unclosed = (
            "---\n"
            "name: fixture\n"
            "description: Fixture process. ALPS-conformant.\n"
            "metadata: {\n"
            "  alps: {kind: process-view}\n"
            "---\n"
        )
        _, errors = CHECKER.frontmatter(unclosed)
        self.assertTrue(any("unclosed YAML flow mapping" in error for error in errors), errors)

    def test_frontmatter_aliases_report_unresolved_cyclic_and_wrong_nodes(self) -> None:
        cases = (
            (
                "metadata: *missing\n",
                "unresolved YAML alias *missing",
            ),
            (
                "kind: &kind process\nmetadata: *kind\n",
                "must resolve to a mapping for metadata",
            ),
            (
                "first: &first *second\n"
                "second: &second *first\n"
                "metadata: *first\n",
                "cyclic YAML alias",
            ),
        )
        for form, expected in cases:
            with self.subTest(form=form):
                text = (
                    "---\n"
                    "name: fixture\n"
                    "description: Fixture process. ALPS-conformant.\n"
                    + form
                    + "---\n"
                )
                values, errors = CHECKER.frontmatter(text)
                self.assertNotIn("alps.kind", values)
                self.assertTrue(any(expected in error for error in errors), errors)
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    path = root / "skills" / "fixture" / "SKILL.md"
                    write(
                        path,
                        text
                        + "\n# Fixture\n\n## Purpose\n\nPurpose.\n\n"
                        "## Outcomes\n\n- Outcome.\n",
                    )
                    self.assertEqual(CHECKER.representation_kind(path), "")
                    asset_errors, _ = CHECKER.check_asset(path, {"": root}, None)
                    self.assertFalse(
                        any("Process representation requires" in error for error in asset_errors),
                        asset_errors,
                    )

    def test_frontmatter_scalar_aliases_resolve_and_mapping_aliases_remain_non_scalar(self) -> None:
        text = "---\n"
        text += "name: &skill-name fixture\n"
        text += "description: Fixture process. ALPS-conformant.\n"
        text += "metadata: &representation {alps.kind: process}\n"
        text += "alias: *skill-name\n"
        text += "mapping-alias: *representation\n"
        text += "---\n"
        values, errors = CHECKER.frontmatter(text)
        self.assertEqual(errors, [], errors)
        self.assertEqual(values["alias"], "fixture")
        self.assertEqual(values["mapping-alias"], "*representation")


    def test_process_model_pair_accepts_translated_named_endpoints(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_process_model_pair(
                Path(directory),
                "- 一 -> 二",
            )
            errors, warnings = CHECKER.check_pair(
                english,
                japanese,
                set(CHECKER.DEFAULT_JA_TERMS),
                "fixture",
            )
            self.assertEqual(errors, [], errors)
            self.assertTrue(any("unverified" in warning for warning in warnings), warnings)

    def test_process_model_pair_preserves_canonical_endpoint_comparison(self) -> None:
        english_relationships = "- One (`skill:#one`) -> Two (`skill:#two`)"
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_process_model_pair(
                Path(directory),
                "- 一 (`skill:#one`) -> 二 (`skill:#two`)",
                english_relationships,
            )
            errors, warnings = CHECKER.check_pair(
                english,
                japanese,
                set(CHECKER.DEFAULT_JA_TERMS),
                "fixture",
            )
            self.assertEqual(errors, [], errors)
            self.assertEqual(warnings, [], warnings)
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_process_model_pair(
                Path(directory),
                "- 二 (`skill:#two`) -> 一 (`skill:#one`)",
                english_relationships,
            )
            errors, warnings = CHECKER.check_pair(
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
            self.assertEqual(warnings, [], warnings)

    def test_process_model_pair_accepts_outer_and_unpiped_relationship_tables(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_process_model_pair(
                Path(directory),
                "提供側プロセス | 情報 | 受領側プロセス | 関係\n--- | --- | --- | ---\n一 | 情報 | 二 | プロセス間の関係。",
                "| Provider Process | Information | Recipient Process | Relationship |\n| --- | --- | --- | --- |\n| One | information | Two | relates the Processes. |",
            )
            errors, warnings = CHECKER.check_pair(
                english,
                japanese,
                set(CHECKER.DEFAULT_JA_TERMS),
                "fixture",
            )
            self.assertEqual(errors, [], errors)
            self.assertTrue(any("unverified" in warning for warning in warnings), warnings)

    def test_process_model_pair_reports_reversed_unpiped_relationship_as_unverified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_process_model_pair(
                Path(directory),
                "提供側プロセス | 情報 | 受領側プロセス | 関係\n--- | --- | --- | ---\n二 | 情報 | 一 | プロセス間の関係。",
                "| Provider Process | Information | Recipient Process | Relationship |\n| --- | --- | --- | --- |\n| One | information | Two | relates the Processes. |",
            )
            errors, warnings = CHECKER.check_pair(
                english,
                japanese,
                set(CHECKER.DEFAULT_JA_TERMS),
                "fixture",
            )
            self.assertEqual(errors, [], errors)
            self.assertTrue(any("unverified" in warning for warning in warnings), warnings)

    def test_process_model_pair_correlates_table_process_names_with_skill_references(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_table_process_model_pair(
                Path(directory),
                "- 二 -> 一",
            )
            errors, warnings = CHECKER.check_pair(
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
            self.assertEqual(warnings, [], warnings)

    def test_process_model_pair_reports_reversed_translated_endpoints_as_unverified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_process_model_pair(
                Path(directory),
                "- 二 -> 一",
            )
            errors, warnings = CHECKER.check_pair(
                english,
                japanese,
                set(CHECKER.DEFAULT_JA_TERMS),
                "fixture",
            )
            self.assertEqual(errors, [], errors)
            self.assertTrue(any("unverified" in warning for warning in warnings), warnings)

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

    def test_inline_code_exact_runs_keep_following_reference_operative(self) -> None:
        delimiter = chr(96) * 2
        triple_run = chr(96) * 3
        value = delimiter + "literal " + triple_run + " content" + delimiter
        self.assertEqual(
            CHECKER.references(value + " skill:#missing"),
            ["skill:#missing"],
        )
        errors = check_model("- " + value + " skill:#missing")
        self.assertTrue(
            any("unresolved Skill reference skill:#missing" in error for error in errors),
            errors,
        )

    def test_japanese_naturalness_masks_exact_arbitrary_inline_code_runs(self) -> None:
        lines = (
            "これは ``HiddenWord ``` inner`` と VisibleWord。",
            "これは ```HiddenTriple``` と VisibleTriple。",
        )
        for line in lines:
            errors = CHECKER.japanese_naturalness_errors(Path("fixture"), line, set())
            self.assertTrue(any("Visible" in error for error in errors), (line, errors))
            self.assertFalse(any("Hidden" in error for error in errors), (line, errors))
        unclosed = CHECKER.japanese_naturalness_errors(
            Path("fixture"), "これは ``UnclosedWord と VisibleUnclosed。", set()
        )
        self.assertTrue(any("UnclosedWord" in error for error in unclosed), unclosed)
        self.assertTrue(any("VisibleUnclosed" in error for error in unclosed), unclosed)

    def test_japanese_naturalness_checks_decoded_description_forms(self) -> None:
        forms = (
            '"description": "English prose ALPS準拠。"\n',
            'description: "English prose ALPS準拠。"\n',
            'description: "English\n  prose ALPS準拠。"\n',
            "description: >-\n  English prose ALPS準拠。\n",
        )
        for description in forms:
            with self.subTest(description=description):
                text = "---\nname: fixture\n" + description + "---\n"
                errors = CHECKER.japanese_naturalness_errors(
                    Path("fixture"), text, set()
                )
                self.assertTrue(any("English" in error for error in errors), errors)
                self.assertEqual(errors, list(dict.fromkeys(errors)), errors)

    def test_process_model_validates_two_column_provider_recipient_tables(self) -> None:
        outer = """| Provider | Recipient |
| --- | --- |
| One | Two |"""
        unpiped = """Provider Process | Recipient Process
--- | ---
One | Two"""
        self.assertEqual(check_model(outer), [])
        self.assertEqual(check_model(unpiped), [])
        errors = check_model(
            """Provider | Recipient
--- | ---
Missing | Also Missing"""
        )
        self.assertTrue(
            any("provider Process 'Missing' is not declared" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("recipient Process 'Also Missing' is not declared" in error for error in errors),
            errors,
        )

    def test_process_model_rejects_unidentified_two_column_relationship_table(self) -> None:
        errors = check_model(
            """| Left | Right |
| --- | --- |
| One | Two |"""
        )
        self.assertTrue(
            any("two-column relationship table must identify Provider" in error for error in errors),
            errors,
        )

    def test_process_model_validates_all_relationship_tables(self) -> None:
        first = """| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| One | information | Two | relates the Processes. |"""
        second_valid = """| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| Two | information | One | relates the Processes. |"""
        second_invalid = """| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| Two | information | Missing | relates the Processes. |"""
        self.assertEqual(
            check_model(first + "\n\nA second category.\n\n" + second_valid),
            [],
        )
        errors = check_model(first + "\n\nA second category.\n\n" + second_invalid)
        self.assertTrue(
            any("recipient Process 'Missing' is not declared" in error for error in errors),
            errors,
        )

    def test_process_models_validate_mixed_table_and_list_relationships(self) -> None:
        table = """| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| One | information | Two | relates the Processes. |"""
        mixed = table + "\n\n- Missing -> Also Missing"
        for checker in (check_model, check_reference_model_fixture):
            with self.subTest(checker=checker.__name__):
                errors = checker(mixed)
                self.assertTrue(
                    any(
                        "provider Process 'Missing' is not declared" in error
                        for error in errors
                    ),
                    errors,
                )
                self.assertTrue(
                    any(
                        "recipient Process 'Also Missing' is not declared" in error
                        for error in errors
                    ),
                    errors,
                )

    def test_process_models_reject_endpointless_mixed_relationship_list_item(self) -> None:
        table = """| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| One | information | Two | relates the Processes. |"""
        mixed = table + "\n\n- Nothing structured here"
        for checker in (check_model, check_reference_model_fixture):
            with self.subTest(checker=checker.__name__):
                errors = checker(mixed)
                self.assertTrue(
                    any(
                        "relationship item 1 must identify provider and recipient Processes"
                        in error
                        for error in errors
                    ),
                    errors,
                )

    def test_process_models_accept_mixed_relationships_and_ignore_fenced_code(self) -> None:
        table = """| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| One | information | Two | relates the Processes. |"""
        mixed = (
            table
            + "\n\n- Two -> One\n\n"
            + "```markdown\n"
            + table
            + "\n- Missing -> Also Missing\n```")
        for checker in (check_model, check_reference_model_fixture):
            with self.subTest(checker=checker.__name__):
                self.assertEqual(checker(mixed), [])

    def test_relationship_semantic_entries_preserve_mixed_document_order(self) -> None:
        first = """| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| One | information | Two | relates the Processes. |"""
        second = """| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| Two | information | One | relates the Processes. |"""
        value = (
            first
            + "\n\n- One -> Two\n\n"
            + second
            + "\n\n```markdown\n"
            + first
            + "\n- Missing -> Also Missing\n```")
        entries = CHECKER.relationship_semantic_entries(value)
        self.assertEqual(
            [(entry.kind, entry.number) for entry in entries],
            [("row", 1), ("item", 1), ("row", 2)],
        )
        self.assertEqual(
            [
                (entry_kind, entry_number, role, cell)
                for entry_kind, entry_number, role, cell in CHECKER.relationship_endpoint_cells(value)
            ],
            [
                ("row", 1, "provider", "One"),
                ("row", 1, "recipient", "Two"),
                ("item", 1, "provider", "One"),
                ("item", 1, "recipient", "Two"),
                ("row", 2, "provider", "Two"),
                ("row", 2, "recipient", "One"),
            ],
        )

    def test_process_model_pair_compares_mixed_relationship_entries(self) -> None:
        table_en = """| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| One | information | Two | relates the Processes. |"""
        table_ja = """提供側プロセス | 情報 | 受領側プロセス | 関係
--- | --- | --- | ---
一 | 情報 | 二 | プロセス間の関係。"""
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_process_model_pair(
                Path(directory), table_ja + "\n\n- 一 -> 二", table_en + "\n\n- One -> Two"
            )
            errors, _ = CHECKER.check_pair(
                english, japanese, set(CHECKER.DEFAULT_JA_TERMS), "fixture"
            )
            self.assertEqual(errors, [], errors)

            write(
                japanese,
                japanese.read_text(encoding="utf-8").replace(
                    "\n\n- 一 -> 二", ""
                ),
            )
            errors, _ = CHECKER.check_pair(
                english, japanese, set(CHECKER.DEFAULT_JA_TERMS), "fixture"
            )
            self.assertTrue(
                any("Relationship count differs" in error for error in errors),
                errors,
            )

    def test_process_model_pair_detects_mixed_relationship_endpoint_order(self) -> None:
        table_en = """| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| One (`skill:#one`) | information | Two (`skill:#two`) | relates the Processes. |"""
        table_ja = """| 提供側プロセス | 情報 | 受領側プロセス | 関係 |
| --- | --- | --- | --- |
| 一 (`skill:#one`) | 情報 | 二 (`skill:#two`) | プロセス間の関係。 |"""
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_table_process_model_pair(
                Path(directory),
                table_ja + "\n\n- 二 (`skill:#two`) -> 一 (`skill:#one`)",
                table_en + "\n\n- One (`skill:#one`) -> Two (`skill:#two`)",
            )
            errors, _ = CHECKER.check_pair(
                english, japanese, set(CHECKER.DEFAULT_JA_TERMS), "fixture"
            )
            self.assertTrue(
                any(
                    "relationship provider/recipient endpoint identity or order differs"
                    in error
                    for error in errors
                ),
                errors,
            )

    def test_process_reference_model_pair_detects_mixed_relationship_endpoint_order(self) -> None:
        table_en = """| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| Define ALPS (`skill:#define-alps`) | information | Apply ALPS (`skill:#apply-alps`) | relates the Processes. |"""
        table_ja = """| 提供側プロセス | 情報 | 受領側プロセス | 関係 |
| --- | --- | --- | --- |
| ALPS定義 (`skill:#define-alps`) | 情報 | ALPS適用 (`skill:#apply-alps`) | プロセス間の関係。 |"""
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_reference_model_pair(
                Path(directory),
                table_ja + "\n\n- `skill:#apply-alps` -> `skill:#define-alps`",
            )
            write(
                english,
                english.read_text(encoding="utf-8").replace(
                    "| Define ALPS | information | Apply ALPS | relates the Processes. |",
                    "| Define ALPS (`skill:#define-alps`) | information | Apply ALPS (`skill:#apply-alps`) | relates the Processes. |\n\n- `skill:#define-alps` -> `skill:#apply-alps`",
                ),
            )
            errors, _ = CHECKER.check_pair(
                english, japanese, set(CHECKER.DEFAULT_JA_TERMS), "fixture"
            )
            self.assertTrue(
                any(
                    "relationship provider/recipient endpoint identity or order differs"
                    in error
                    for error in errors
                ),
                errors,
            )

    def test_process_reference_model_pair_compares_mixed_relationship_entries(self) -> None:
        table_en = """| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| Define ALPS | information | Apply ALPS | relates the Processes. |"""
        table_ja = """| 提供側プロセス | 情報 | 受領側プロセス | 関係 |
| --- | --- | --- | --- |
| ALPS定義 | 情報 | ALPS適用 | プロセス間の関係。 |"""
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_reference_model_pair(
                Path(directory), table_ja + "\n\n- ALPS定義 -> ALPS適用"
            )
            write(
                english,
                english.read_text(encoding="utf-8").replace(
                    "| Define ALPS | information | Apply ALPS | relates the Processes. |",
                    "| Define ALPS | information | Apply ALPS | relates the Processes. |\n\n- Define ALPS -> Apply ALPS",
                ),
            )
            errors, _ = CHECKER.check_pair(
                english, japanese, set(CHECKER.DEFAULT_JA_TERMS), "fixture"
            )
            self.assertEqual(errors, [], errors)

            write(
                japanese,
                japanese.read_text(encoding="utf-8").replace(
                    "\n\n- ALPS定義 -> ALPS適用", ""
                ),
            )
            errors, _ = CHECKER.check_pair(
                english, japanese, set(CHECKER.DEFAULT_JA_TERMS), "fixture"
            )
            self.assertTrue(
                any("Relationship count differs" in error for error in errors),
                errors,
            )

    def test_process_model_pair_reports_reversed_two_column_relationship_as_unverified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_process_model_pair(
                Path(directory),
                "提供側プロセス | 受領側プロセス\n--- | ---\n二 | 一",
                "Provider | Recipient\n--- | ---\nOne | Two",
            )
            errors, warnings = CHECKER.check_pair(
                english,
                japanese,
                set(CHECKER.DEFAULT_JA_TERMS),
                "fixture",
            )
            self.assertEqual(errors, [], errors)
            self.assertTrue(any("unverified" in warning for warning in warnings), warnings)

    def test_frontmatter_parses_scalar_anchors_tags_and_preserves_yaml_forms(self) -> None:
        text = """---
name: &skill-name fixture
description: !!str Fixture process. ALPS-conformant. # discovery comment
metadata: &representation # mapping comment
  alps.kind: !!str &kind process
alias: *representation
quoted: 'keep # this text'
---
"""
        values, errors = CHECKER.frontmatter(text)
        self.assertEqual(errors, [])
        self.assertEqual(values["name"], "fixture")
        self.assertEqual(values["description"], "Fixture process. ALPS-conformant.")
        self.assertEqual(values["alps.kind"], "process")
        self.assertEqual(values["alias"], "*representation")
        self.assertEqual(values["quoted"], "keep # this text")
        block_values, block_errors = CHECKER.frontmatter(
            """---
name: fixture
description: &description |
  Fixture process. ALPS-conformant.
---
"""
        )
        self.assertEqual(block_errors, [])
        self.assertEqual(block_values["description"], "Fixture process. ALPS-conformant.")

    def test_frontmatter_parses_quoted_block_keys_and_dispatches_nested_view_kind(self) -> None:
        text = r'''---
"name": fixture
"description": Fixture process. ALPS-conformant.
metadata:
  "alps.kind": process-view
  'note''key': !!str value
  "quote\"key": &kind process-view
  "alias": *kind
  "display: key": scalar
---
'''
        values, errors = CHECKER.frontmatter(text)
        self.assertEqual(errors, [], errors)
        self.assertEqual(values["name"], "fixture")
        self.assertEqual(values["description"], "Fixture process. ALPS-conformant.")
        self.assertEqual(values["alps.kind"], "process-view")
        self.assertEqual(values["metadata.note'key"], "value")
        self.assertEqual(values['metadata.quote"key'], "process-view")
        self.assertEqual(values["metadata.alias"], "process-view")
        self.assertEqual(values["metadata.display: key"], "scalar")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "skills" / "fixture" / "SKILL.md"
            write(
                path,
                text
                + "# Fixture\n\n## Purpose\n\nPurpose.\n\n"
                "## Outcomes\n\n- Outcome.\n",
            )
            asset_errors, _ = CHECKER.check_asset(path, {"": root}, None)
            self.assertTrue(
                any("Process View requires Source Processes" in error for error in asset_errors),
                asset_errors,
            )
            self.assertFalse(
                any("Process representation requires" in error for error in asset_errors),
                asset_errors,
            )

        flow_values, flow_errors = CHECKER.frontmatter(
            """---
name: fixture
description: Fixture process. ALPS-conformant.
metadata: {"alps.kind": process-view}
---
"""
        )
        self.assertEqual(flow_errors, [], flow_errors)
        self.assertEqual(flow_values["alps.kind"], "process-view")

        complex_values, complex_errors = CHECKER.frontmatter(
            """---
name: fixture
description: Fixture process. ALPS-conformant.
metadata:
  [alps.kind]: process-view
---
"""
        )
        self.assertTrue(
            any("invalid YAML mapping key" in error for error in complex_errors),
            complex_errors,
        )
        self.assertNotEqual(complex_values.get("alps.kind"), "process-view")

    def test_frontmatter_scalar_anchor_fixture_passes_asset_checks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "skills" / "fixture" / "SKILL.md"
            write(
                path,
                """---
name: &skill-name fixture
description: !!str Fixture process. ALPS-conformant.
metadata:
  alps.kind: &kind process
---

# Fixture

## Purpose

The fixture has a purpose.

## Outcomes

- The fixture is complete.
""",
            )
            errors, _ = CHECKER.check_asset(path, {"": root}, None)
            self.assertEqual(errors, [], errors)

    def test_frontmatter_multiline_quoted_scalars_accept_anchor_and_tag_properties(self) -> None:
        for quote in ('"', "'"):
            for properties in ("&d", "!!str"):
                text = (
                    "---\n"
                    "name: fixture\n"
                    f"description: {properties} {quote}Fixture process.\n"
                    f"  ALPS-conformant.{quote}\n"
                    "---\n"
                )
                values, errors = CHECKER.frontmatter(text)
                self.assertEqual(errors, [], (quote, properties, errors))
                self.assertEqual(
                    values["description"],
                    "Fixture process. ALPS-conformant.",
                    (quote, properties, values),
                )

    def test_frontmatter_single_line_quoted_scalars_accept_anchor_and_tag_properties(self) -> None:
        for quote in ('"', "'"):
            for properties in ("&d", "!!str"):
                text = (
                    "---\n"
                    "name: fixture\n"
                    f"description: {properties} {quote}Fixture process. "
                    f"ALPS-conformant.{quote}\n"
                    "---\n"
                )
                values, errors = CHECKER.frontmatter(text)
                self.assertEqual(errors, [], (quote, properties, errors))
                self.assertEqual(
                    values["description"],
                    "Fixture process. ALPS-conformant.",
                    (quote, properties, values),
                )

    def test_frontmatter_decodes_full_yaml_double_quoted_escape_set(self) -> None:
        text = (
            "---\n"
            'value: "\\0\\a\\b\\t\\n\\v\\f\\r\\e\\ \\"\\/\\\\\\N\\_\\L\\P\\x70\\u0072\\U0000006f"\n'
            "---\n"
        )
        values, errors = CHECKER.frontmatter(text)
        expected = (
            "\0\a\b\t\n\v\f\r\x1b "
            + '"'
            + "/"
            + "\\"
            + "\x85\xa0\u2028\u2029pro"
        )
        self.assertEqual(errors, [], errors)
        self.assertEqual(values["value"], expected)

    def test_frontmatter_double_quoted_escapes_decode_name_description_and_kind(self) -> None:
        text = r'''---
name: "\x70"
description: "Fixture process. ALPS-conformant."
metadata:
  "alps.\x6bind": "process-view"
---
'''
        values, errors = CHECKER.frontmatter(text)
        self.assertEqual(errors, [], errors)
        self.assertEqual(values["name"], "p")
        self.assertEqual(values["description"], "Fixture process. ALPS-conformant.")
        self.assertEqual(values["alps.kind"], "process-view")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "skills" / "fixture" / "SKILL.md"
            write(
                path,
                text
                + "# Fixture\n\n## Purpose\n\nPurpose.\n\n"
                "## Outcomes\n\n- Outcome.\n",
            )
            asset_errors, _ = CHECKER.check_asset(path, {"": root}, None)
            self.assertTrue(
                any("Process View requires Source Processes" in error for error in asset_errors),
                asset_errors,
            )
            self.assertFalse(
                any("Process representation requires" in error for error in asset_errors),
                asset_errors,
            )

    def test_frontmatter_double_quoted_escaped_line_break_is_folded(self) -> None:
        text = r'''---
name: fixture
description: "Fixture process.\
  ALPS-conformant."
metadata:
  alps.kind: process
---
'''
        values, errors = CHECKER.frontmatter(text)
        self.assertEqual(errors, [], errors)
        self.assertEqual(values["description"], "Fixture process.ALPS-conformant.")

    def test_frontmatter_rejects_invalid_yaml_double_quoted_escapes(self) -> None:
        for escape in (r"\q", r"\x1", r"\uD800", r"\U00110000"):
            with self.subTest(escape=escape):
                text = (
                    "---\n"
                    "name: fixture\n"
                    "description: Fixture process. ALPS-conformant.\n"
                    'metadata:\n  alps.kind: "' + escape + '"\n'
                    "---\n"
                )
                values, errors = CHECKER.frontmatter(text)
                self.assertTrue(
                    any(
                        "invalid YAML double-quoted" in error
                        for error in errors
                    ),
                    (escape, errors),
                )
                self.assertNotEqual(values.get("alps.kind"), escape)

    def test_frontmatter_parses_anchored_tagged_flow_metadata_with_comments(self) -> None:
        for metadata in (
            "metadata: &m {alps.kind: &k process} # representation comment",
            "metadata: !!map &m {alps.kind: !!str process} # representation comment",
        ):
            text = (
                "---\n"
                "name: fixture\n"
                "description: Fixture process. ALPS-conformant.\n"
                f"{metadata}\n"
                "---\n"
            )
            values, errors = CHECKER.frontmatter(text)
            self.assertEqual(errors, [], (metadata, errors))
            self.assertEqual(values["alps.kind"], "process", (metadata, values))

    def test_frontmatter_folds_plain_description_continuations_and_checks_suffix(self) -> None:
        cases = (
            (
                "description: Fixture process.\n"
                "  ALPS-conformant.\n",
                "Fixture process. ALPS-conformant.",
            ),
            (
                "description: Fixture process.\n"
                "  # description comment\n"
                "  ALPS-conformant.\n",
                "Fixture process. ALPS-conformant.",
            ),
            (
                "description: Fixture process.\n"
                "\n"
                "  ALPS-conformant.\n",
                "Fixture process.\nALPS-conformant.",
            ),
            (
                "description: Fixture process. # first comment\n"
                "  ALPS-conformant. # continuation comment\n",
                "Fixture process. ALPS-conformant.",
            ),
        )
        for description, expected in cases:
            with self.subTest(description=description):
                text = (
                    "---\n"
                    "name: fixture\n"
                    + description
                    + "metadata:\n"
                    "  alps.kind: process\n"
                    "---\n"
                )
                values, errors = CHECKER.frontmatter(text)
                self.assertEqual(errors, [], (description, errors))
                self.assertEqual(values["description"], expected, values)
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    path = root / "skills" / "fixture" / "SKILL.md"
                    write(
                        path,
                        text
                        + "\n# Fixture\n\n## Purpose\n\nPurpose.\n\n"
                        "## Outcomes\n\n- Outcome.\n",
                    )
                    self.assertEqual(CHECKER.check_frontmatter(path, text), [], errors)

    def test_frontmatter_does_not_fold_name_or_kind_and_keeps_tab_diagnostic(self) -> None:
        text = (
            "---\n"
            "name: fixture\n"
            "  not a name continuation\n"
            "description: Fixture process. ALPS-conformant.\n"
            "metadata:\n"
            "  alps.kind: process\n"
            "\tALPS-conformant.\n"
            "---\n"
        )
        values, errors = CHECKER.frontmatter(text)
        self.assertEqual(values["name"], "fixture")
        self.assertEqual(values["alps.kind"], "process")
        self.assertTrue(any("uses a tab for indentation" in error for error in errors), errors)

    def test_frontmatter_preserves_quoted_scalar_error_checks_with_properties(self) -> None:
        unbalanced = (
            "---\n"
            "name: fixture\n"
            "description: &d \"Fixture process.\n"
            "  ALPS-conformant.\n"
            "---\n"
        )
        _, errors = CHECKER.frontmatter(unbalanced)
        self.assertTrue(
            any("unbalanced quoted scalar" in error for error in errors),
            errors,
        )
        trailing = (
            "---\n"
            "name: fixture\n"
            "description: !!str \"Fixture process. ALPS-conformant.\" trailing\n"
            "---\n"
        )
        _, errors = CHECKER.frontmatter(trailing)
        self.assertTrue(
            any("content after a quoted scalar" in error for error in errors),
            errors,
        )

    def test_process_activities_accept_alternate_heading_levels_and_exclude_later_sections(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "skills" / "fixture" / "SKILL.md"
            write(
                path,
                """---
name: fixture
description: Fixture process. ALPS-conformant.
---

# Fixture

## Purpose

The fixture has a purpose.

## Outcomes

- The fixture is complete.

## Activities & Tasks

### Plan

1. The agent must plan.

#### Work

1. The agent should work.

## Inputs

### Unrelated later heading

1. Perform an action.
""",
            )
            errors, _ = CHECKER.check_asset(path, {"": root}, None)
            self.assertEqual(errors, [], errors)

    def test_process_activities_keep_deeper_explanatory_headings_in_activity_body(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "skills" / "fixture" / "SKILL.md"
            write(
                path,
                """---
name: fixture
description: Fixture process. ALPS-conformant.
---

# Fixture

## Purpose

The fixture has a purpose.

## Outcomes

- The fixture is complete.

## Activities & Tasks

### Work

1. The agent must work.

#### Notes

- Informational note.

### Review

1. The agent should review.
""",
            )
            structure = CHECKER.parse_process_structure(
                path.read_text(encoding="utf-8"), "en"
            )
            self.assertEqual(structure.activities, ("Work", "Review"))
            self.assertEqual(tuple(map(len, structure.tasks)), (1, 1))
            errors, _ = CHECKER.check_asset(path, {"": root}, None)
            self.assertEqual(errors, [], errors)

    def test_process_tasks_under_alternate_heading_require_normative_force(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "skills" / "fixture" / "SKILL.md"
            write(
                path,
                """---
name: fixture
description: Fixture process. ALPS-conformant.
---

# Fixture

## Purpose

The fixture has a purpose.

## Outcomes

- The fixture is complete.

## Activities & Tasks

#### Work

1. Perform an action.
""",
            )
            errors, _ = CHECKER.check_asset(path, {"": root}, None)
            self.assertTrue(
                any(
                    "Activity 1 Task 1 has no recognizable normative attribute"
                    in error
                    for error in errors
                ),
                errors,
            )

    def test_process_tasks_under_recognized_child_sections_preserve_order_and_boundaries(self) -> None:
        text = """---
name: fixture
description: Fixture process. ALPS-conformant.
---

# Fixture

## Purpose

The fixture has a purpose.

## Outcomes

- The fixture is complete.

## Activities & Tasks

### Work

1. The agent must prepare.
   The preparation continues here.

#### Tasks

2. The agent should record.
   The record action continues here.

##### Notes

- This explanatory item is not a Task.

##### Tasks

3. The agent may verify.

#### Notes

- This second explanatory item is not a Task.

#### Task

4. The agent must finish.

### Review

- The agent may review.
"""
        structure = CHECKER.parse_process_structure(text, "en")
        self.assertEqual(structure.activities, ("Work", "Review"))
        self.assertEqual(
            structure.tasks,
            (
                (
                    "The agent must prepare. The preparation continues here.",
                    "The agent should record. The record action continues here.",
                    "The agent may verify.",
                    "The agent must finish.",
                ),
                ("The agent may review.",),
            ),
        )

    def test_process_tasks_under_child_heading_require_normative_force(self) -> None:
        def document(activities: str) -> str:
            return """---
name: fixture
description: Fixture process. ALPS-conformant.
---

# Fixture

## Purpose

The fixture has a purpose.

## Outcomes

- The fixture is complete.

## Activities & Tasks

""" + activities + "\n"

        for activities, expected_error in (
            ("### Work\n#### Tasks\n1. Perform the action.", True),
            ("### Work\n#### Tasks\n1. The agent must perform the action.", False),
        ):
            with self.subTest(expected_error=expected_error), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                path = root / "skills" / "fixture" / "SKILL.md"
                write(path, document(activities))
                errors, _ = CHECKER.check_asset(path, {"": root}, None)
                has_normative_error = any(
                    "Activity 1 Task 1 has no recognizable normative attribute" in error
                    for error in errors
                )
                self.assertEqual(has_normative_error, expected_error, errors)

    def test_process_pair_counts_child_tasks_and_compares_normative_force(self) -> None:
        english_activities = """### Work
1. The agent must prepare.
#### Tasks
2. The agent should record.
#### Notes
- Explanatory note.
### Review
- The agent may review.
"""
        japanese_activities = """### 作業
1. 担当者は準備する必要がある。
#### タスク
2. 担当者は記録することが望ましい。
#### 注記
- 説明用の注記。
### 確認
- 担当者は確認してもよい。
"""

        def write_pair(root: Path, ja_activities: str) -> tuple[Path, Path]:
            english = root / "process" / "SKILL.md"
            japanese = english.parent / "references" / "locales" / "ja" / "SKILL.md"
            write(
                english,
                """---
name: fixture-process
description: Fixture process.
---

# Fixture Process

## Purpose

The fixture has a purpose.

## Outcomes

- The fixture is complete.

## Activities & Tasks

""" + english_activities,
            )
            write(
                japanese,
                """---
name: fixture-process
description: フィクスチャのプロセス。
---

# フィクスチャプロセス

## 目的

フィクスチャには目的がある。

## 成果

- フィクスチャが完成している。

## 活動とタスク

""" + ja_activities,
            )
            return english, japanese

        with tempfile.TemporaryDirectory() as directory:
            english, japanese = write_pair(Path(directory), japanese_activities)
            errors, _ = CHECKER.check_pair(
                english, japanese, set(CHECKER.DEFAULT_JA_TERMS), "fixture"
            )
            self.assertEqual(errors, [], errors)

            japanese_text = japanese.read_text(encoding="utf-8").replace(
                "#### タスク\n2. 担当者は記録することが望ましい。\n", ""
            )
            write(japanese, japanese_text)
            errors, _ = CHECKER.check_pair(
                english, japanese, set(CHECKER.DEFAULT_JA_TERMS), "fixture"
            )
            self.assertTrue(
                any("Task counts by Activity differ" in error for error in errors),
                errors,
            )

    def test_process_resolves_operative_references_and_ignores_masked_forms(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "package"
            other_root = Path(directory) / "other-package"
            process_skill(root, "one", "One")
            process_skill(other_root, "two", "Two")
            path = root / "skills" / "fixture" / "SKILL.md"
            write(
                path,
                """---
name: fixture
description: Fixture process. ALPS-conformant.
---

# Fixture

## Purpose

The Process uses `skill:#one` and skill:other#two.

[ignored](https://example.com/skill:#missing)

<!-- skill:#missing -->

```markdown
skill:#missing
```

    skill:#missing

`not a canonical reference: skill:#missing`

## Outcomes

- The Process is complete.

## Activities & Tasks

### Work

1. The agent must work.
""",
            )
            errors, _ = CHECKER.check_asset(
                path, {"": root, "other": other_root}, None
            )
            self.assertEqual(errors, [], errors)

    def test_process_resolves_localized_references_and_rejects_unsafe_targets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "package"
            process_skill(root, "one", "One")
            localized_target = root / "skills" / "one" / "references" / "locales" / "ja" / "SKILL.md"
            write(localized_target, "# ワン\n")
            outside = Path(directory) / "outside" / "escape"
            write(outside / "SKILL.md", "# Escaped\n")
            escape_link = root / "skills" / "escape"
            try:
                escape_link.symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"symlinks unavailable: {exc}")

            path = root / "skills" / "fixture" / "references" / "locales" / "ja" / "SKILL.md"
            write(
                path,
                """---
name: fixture
description: フィクスチャプロセス。ALPS準拠。
---

# フィクスチャ

## 目的

`skill:#one`

## 成果

- プロセスが完了している。

## 活動とタスク

### 作業

- 担当者は作業する必要がある。
""",
            )
            errors, _ = CHECKER.check_asset(path, {"": root}, None)
            self.assertEqual(errors, [], errors)

            unsafe = path.read_text(encoding="utf-8").replace(
                "`skill:#one`",
                "`skill:#missing` skill:unknown#one skill:#escape `skill:#missing`",
            )
            write(path, unsafe)
            errors, _ = CHECKER.check_asset(path, {"": root}, None)
            process_reference_errors = [
                error for error in errors if "Process reference" in error
            ]
            self.assertEqual(len(process_reference_errors), 3, errors)
            self.assertTrue(
                any("unresolved Skill reference skill:#missing" in error for error in errors),
                errors,
            )
            self.assertTrue(
                any("unresolved package identity 'unknown'" in error for error in errors),
                errors,
            )
            self.assertTrue(
                any("escapes package root" in error for error in errors),
                errors,
            )
            self.assertFalse(any("invalid canonical Skill reference" in error for error in errors), errors)

    def test_semantic_heading_extractors_normalize_atx_closing_markers(self) -> None:
        english = """---
name: fixture
description: Fixture process. ALPS-conformant.
---

# Fixture #

## Purpose ##

The Process has C# and value# literals.

## Outcomes ##

- The Process is complete.

## Activities & Tasks ##

### Work ###

1. The agent must work.

#### Tasks ####

2. The agent should record.

```markdown
### Code fake ###
```

<!--
### Comment fake ###
-->
"""
        self.assertEqual(CHECKER.heading1(english), "Fixture")
        self.assertEqual(
            CHECKER.section(english, "Purpose"),
            "The Process has C# and value# literals.",
        )
        structure = CHECKER.parse_process_structure(english, "en")
        self.assertEqual(structure.activities, ("Work",))
        self.assertEqual(
            structure.tasks,
            (("The agent must work.", "The agent should record."),),
        )
        self.assertEqual(CHECKER.heading1("# Name #\n"), "Name")
        self.assertEqual(CHECKER.heading1("# C# value#\n"), "C# value#")

        japanese = """---
name: fixture
description: フィクスチャプロセス。ALPS準拠。
---

# フィクスチャ #

## 目的 ##

プロセスには目的がある。

## 成果 ##

- プロセスが完了している。

## 活動とタスク ##

### 作業 ###

1. 担当者は作業する必要がある。

#### タスク ####

2. 担当者は記録することが望ましい。
"""
        japanese_structure = CHECKER.parse_process_structure(japanese, "ja")
        self.assertEqual(japanese_structure.activities, ("作業",))
        self.assertEqual(
            japanese_structure.tasks,
            (("担当者は作業する必要がある。", "担当者は記録することが望ましい。"),),
        )

    def test_closing_markers_apply_to_model_reference_and_view_extractors(self) -> None:
        processes = "### One ###\n\n### Two ###\n\n### C# value# ###"
        self.assertEqual(
            CHECKER.process_model_entries(processes),
            ["One", "Two", "C# value#"],
        )
        reference_processes = """### One ###

#### Purpose ####

One purpose.

#### Outcomes ####

- One is achieved.

`skill:#one`

### Two ###

#### Purpose ####

Two purpose.

#### Outcomes ####

- Two is achieved.

`skill:#two`
"""
        self.assertEqual(
            [name for name, _, _ in CHECKER.process_block_details(reference_processes)],
            ["One", "Two"],
        )
        self.assertEqual(
            CHECKER.source_entries("### One ###\n### Two ###"),
            ["One", "Two"],
        )
        included = """### Activity: Work ###

#### Task: Review ####

```markdown
### Activity: Fake ###
```
"""
        self.assertEqual(
            CHECKER.included_semantic_items(included, "en"),
            [("activity", "Activity: Work"), ("task", "Task: Review")],
        )

    def test_process_view_rejects_unstructured_included_content_and_keeps_supported_forms(self) -> None:
        for included in (
            "Nothing structured here.",
            "No Activity has been selected.",
            "The Activity is Work and the Task is Review.",
        ):
            with self.subTest(included=included):
                errors = check_view_fixture("- One\n- Two", included)
                self.assertTrue(
                    any("must identify at least one Activity or Task" in error for error in errors),
                    errors,
                )
        self.assertEqual(
            check_view_fixture("- One\n- Two", "- Activity: Work\n- Task: Review"),
            [],
        )


if __name__ == "__main__":
    unittest.main()
