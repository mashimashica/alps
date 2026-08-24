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
            "    # } remains quoted\",\n"
            "  alps: {kind: process-view}\n"
            "} # representation comment\n"
            "---\n"
        )
        values, errors = CHECKER.frontmatter(text)
        self.assertEqual(errors, [], errors)
        self.assertEqual(values["metadata.note"], "line one\n# } remains quoted")
        self.assertEqual(values["alps.kind"], "process-view")

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

    def test_process_view_rejects_unstructured_included_content_and_keeps_supported_forms(self) -> None:
        errors = check_view_fixture("- One\n- Two", "Nothing structured here.")
        self.assertTrue(
            any("must identify at least one Activity or Task" in error for error in errors),
            errors,
        )
        self.assertEqual(
            check_view_fixture("- One\n- Two", "- Activity: Work\n- Task: Review"),
            [],
        )
        self.assertEqual(
            check_view_fixture(
                "- One\n- Two",
                "The Activity is Work and the Task is Review.",
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
