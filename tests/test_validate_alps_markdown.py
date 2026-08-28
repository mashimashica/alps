from __future__ import annotations

from contextlib import contextmanager, redirect_stderr, redirect_stdout
from dataclasses import asdict
import io
import importlib.util
import json
import os
import re
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
CHECKER_PATH = ROOT / ".agents/skills/review-alps/scripts/validate_alps_markdown.py"
SPEC = importlib.util.spec_from_file_location("validate_alps_markdown", CHECKER_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)
from alps_markdown import Severity, locale_for, package_roots, resolve_reference  # noqa: E402


def _clean(value: str) -> str:
    return textwrap.dedent(value).strip("\n") + "\n"


def _frontmatter(
    name: str,
    kind: str,
    locale: str,
    *,
    metadata: bool = True,
    description: str | None = None,
) -> str:
    suffix = "ALPS-conformant." if locale == "en" else "ALPS準拠。"
    description = description or (
        f"Canonical {kind} fixture. {suffix}" if kind == "process"
        else f"Canonical {kind} fixture."
    )
    lines = ["---", f"name: {name}", f"description: {description}"]
    if metadata:
        lines.extend(["metadata:", f"  alps.kind: {kind}"])
    return "\n".join(lines + ["---", ""])


def _heading(locale: str, key: str) -> str:
    names = {
        "en": {
            "purpose": "Purpose", "outcomes": "Outcomes", "activities": "Activities & Tasks",
            "inputs": "Inputs", "processes": "Processes", "relationships": "Relationships",
            "source": "Source Processes", "included": "Included Activities and Tasks",
            "application": "Application",
        },
        "ja": {
            "purpose": "目的", "outcomes": "成果", "activities": "活動とタスク",
            "inputs": "入力", "processes": "プロセス", "relationships": "関係",
            "source": "出典プロセス", "included": "含まれる活動およびタスク", "application": "適用",
        },
    }
    return names[locale][key]


def _process_body(
    locale: str = "en",
    *,
    outcome_lines: tuple[str, ...] | None = None,
    task_lines: tuple[str, ...] | None = None,
    activity: str | None = None,
    title: str | None = None,
    extra: str = "",
) -> str:
    if locale == "ja":
        purpose = "このフィクスチャの目的を定義する。"
        outcome_lines = outcome_lines or ("成果が準備される。",)
        task_lines = task_lines or ("エージェントは入力を確認する必要がある。",)
        activity = activity or "確認"
        title = title or "フィクスチャプロセス"
    else:
        purpose = "Defines the purpose of this fixture."
        outcome_lines = outcome_lines or ("The result is ready.",)
        task_lines = task_lines or ("The agent must inspect the input.",)
        activity = activity or "Inspect"
        title = title or "Fixture Process"
    outcome_block = "\n".join(f"- {line}" for line in outcome_lines)
    task_block = "\n".join(f"{index}. {text}" for index, text in enumerate(task_lines, 1))
    return _clean(
        f"""# {title}

## {_heading(locale, 'purpose')}

{purpose}

## {_heading(locale, 'outcomes')}

Introductory prose is opaque.
{outcome_block}

## {_heading(locale, 'activities')}

### {activity}

Activity introduction is opaque.

{task_block}
{extra}
"""
    )


def _model_body(locale: str = "en") -> str:
    if locale == "ja":
        return _clean(
            """
            # フィクスチャモデル

            ## 目的

            関連プロセスを整理する。

            ## プロセス

            | プロセス | スキル |
            | --- | --- |
            | アルファ | `skill:#alpha` |
            | ベータ | |

            ## 関係

            | 提供側プロセス | 情報 | 受領側プロセス | 関係 |
            | --- | --- | --- | --- |
            | アルファ | 情報 | ベータ | 支援 |
            """
        )
    return _clean(
        """
        # Fixture Model

        ## Purpose

        Organizes related Processes.

        ## Processes

        | Process | Skill |
        | --- | --- |
        | Alpha | `skill:#alpha` |
        | Beta | |

        ## Relationships

        | Provider Process | Information | Recipient Process | Relationship |
        | --- | --- | --- | --- |
        | Alpha | Information | Beta | Supports |
        """
    )


def _reference_model_body(locale: str = "en") -> str:
    if locale == "ja":
        return _clean(
            """
            # フィクスチャ参照モデル

            ## 目的

            プロセスの意味中心を整理する。

            ## プロセス

            ### アルファ

            スキル: `skill:#alpha`

            #### 目的

            アルファを定義する。

            #### 成果

            - アルファの成果が整う。

            ### ベータ

            #### 目的

            ベータを定義する。

            #### 成果

            - ベータの成果が整う。

            ## 関係

            | 提供側プロセス | 情報 | 受領側プロセス | 関係 |
            | --- | --- | --- | --- |
            | アルファ | 情報 | ベータ | 支援 |
            """
        )
    return _clean(
        """
        # Fixture Reference Model

        ## Purpose

        Organizes Process semantic centers.

        ## Processes

        ### Alpha

        Skill: `skill:#alpha`

        #### Purpose

        Define Alpha.

        #### Outcomes

        - Alpha is ready.

        ### Beta

        #### Purpose

        Define Beta.

        #### Outcomes

        - Beta is ready.

        ## Relationships

        | Provider Process | Information | Recipient Process | Relationship |
        | --- | --- | --- | --- |
        | Alpha | Information | Beta | Supports |
        """
    )


def _view_body(locale: str = "en") -> str:
    if locale == "ja":
        return _clean(
            """
            # フィクスチャビュー

            ## 目的

            共通の観点でプロセスを表示する。

            ## 成果

            - ビューの成果が整う。

            ## 出典プロセス

            | 出典プロセス | 参照 |
            | --- | --- |
            | アルファ | `skill:#alpha` |
            | ベータ | `skill:#beta` |

            ## 含まれる活動およびタスク

            | 出典プロセス | 出典要素 |
            | --- | --- |
            | アルファ (`skill:#alpha`) | 活動: 確認 |
            | ベータ (`skill:#beta`) | タスク: 記録 |

            ## 適用

            このビューを適用する。
            """
        )
    return _clean(
        """
        # Fixture View

        ## Purpose

        Presents Processes through one concern.

        ## Outcomes

        - The view outcome is ready.

        ## Source Processes

        | Source Process | Reference |
        | --- | --- |
        | Alpha | `skill:#alpha` |
        | Beta | `skill:#beta` |

        ## Included Activities and Tasks

        | Source Process | Source element |
        | --- | --- |
        | Alpha (`skill:#alpha`) | Activity: Inspect |
        | Beta (`skill:#beta`) | Task: Record |

        ## Application

        Apply this view.
        """
    )


def _local_view_body(locale: str = "en") -> str:
    if locale == "ja":
        return _clean(
            """
            # ローカルビュー

            ## 目的

            ビュー固有の観点を適用する。

            ## 成果

            - 観点 `skill:#local-view` が明確になる。

            ## 活動とタスク

            ### 確認

            1. エージェントは観点を確認する必要がある。

            ## 適用

            関連するプロセスにこのビューを適用する。
            """
        )
    return _clean(
        """
        # Local View

        ## Purpose

        Applies a View-local concern.

        ## Outcomes

        - The concern `skill:#local-view` is visible.

        ## Activities & Tasks

        ### Review

        1. The agent must review the concern.

        ## Application

        Apply this View to the relevant Processes.
        """
    )


def _asset(name: str, kind: str, locale: str, body: str, *, metadata: bool = True) -> str:
    return _frontmatter(name, kind, locale, metadata=metadata) + body


def _write(root: Path, relative: str, content: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


@contextmanager
def _temp_root():
    with tempfile.TemporaryDirectory() as directory:
        yield Path(directory)


def _parse(root: Path, content: str, *, locale: str = "en", name: str = "fixture"):
    return CHECKER.parse_asset(_write(root, f"{name}.md", content), locale)


def _codes(result) -> tuple[str, ...]:
    return tuple(item.code for item in result.diagnostics)


def _classes(result) -> tuple[str, ...]:
    return tuple(item.class_name for item in result.diagnostics)


_RAW_CHECK_PAIR = CHECKER.check_pair


def _check_pair(
    english: Path,
    japanese: Path,
    allowed_terms: object = None,
    package_identity: object = None,
    *,
    roots: object = None,
    package_id: str | None = None,
):
    selected_identity = package_identity or "example/alps@1.2.3"
    selected_package = package_id
    if selected_package is None and isinstance(selected_identity, str):
        selected_package = selected_identity.rsplit("@", 1)[0]
    return _RAW_CHECK_PAIR(
        english,
        japanese,
        allowed_terms,
        package_identity=selected_identity,
        roots=roots,
        package_id=selected_package,
    )


class AlpsMarkdownProfileMilestoneATests(unittest.TestCase):
    def assert_no_errors(self, result) -> None:
        errors = [item.render() for item in result.diagnostics if item.severity.value == "error"]
        self.assertEqual(errors, [], "\n".join(errors))

    def test_profile_version_and_diagnostic_rendered_contract(self) -> None:
        self.assertEqual(CHECKER.PROFILE_VERSION, "alps-markdown/v2")
        diagnostic = CHECKER.Diagnostic(
            "unsupported-profile-syntax", "tab-heading", Severity.ERROR,
            "fixture.md", 12, "headings require one ASCII space",
        )
        self.assertEqual(
            diagnostic.render(),
            "fixture.md:12: error unsupported-profile-syntax/tab-heading: headings require one ASCII space",
        )
        warning = CHECKER.Diagnostic(
            "quality-review", "outcome-recorded-language", Severity.WARNING,
            "fixture.md", None, "review wording",
        )
        self.assertEqual(warning.render(), "fixture.md: warning quality-review/outcome-recorded-language: review wording")

    def test_canonical_english_japanese_and_kind_fixtures_produce_ir(self) -> None:
        cases = (
            ("process", "en", False, _process_body("en"), ("purpose", "outcomes", "activities")),
            ("process", "ja", False, _process_body("ja"), ("purpose", "outcomes", "activities")),
            ("process-model", "en", True, _model_body("en"), ("purpose", "processes", "relationships")),
            ("process-model", "ja", True, _model_body("ja"), ("purpose", "processes", "relationships")),
            ("process-reference-model", "en", True, _reference_model_body("en"), ("purpose", "processes", "relationships")),
            ("process-reference-model", "ja", True, _reference_model_body("ja"), ("purpose", "processes", "relationships")),
            ("process-view", "en", True, _view_body("en"), ("purpose", "outcomes", "source", "included", "application")),
            ("process-view", "ja", True, _view_body("ja"), ("purpose", "outcomes", "source", "included", "application")),
        )
        with _temp_root() as root:
            for kind, locale, metadata, body, section_keys in cases:
                with self.subTest(kind=kind, locale=locale):
                    name = f"fixture-{kind}-{locale}"
                    result = _parse(root, _asset(name, kind, locale, body, metadata=metadata), locale=locale, name=name)
                    self.assert_no_errors(result)
                    self.assertIsNotNone(result.ir)
                    self.assertEqual(result.frontmatter.name, name)
                    self.assertEqual(result.frontmatter.kind, kind)
                    self.assertEqual(result.ir.locale, locale)
                    self.assertEqual(result.ir.kind, kind)
                    self.assertEqual(tuple(section.key for section in result.ir.sections), section_keys)
                    self.assertEqual(result.ir.purpose is not None, True)
                    if kind == "process":
                        self.assertEqual(len(result.ir.outcomes), 1)
                        self.assertEqual(len(result.ir.activities), 1)
                        self.assertEqual(len(result.ir.activities[0].tasks), 1)
                    elif kind == "process-model":
                        self.assertEqual(tuple(item.name for item in result.ir.processes), ("Alpha", "Beta") if locale == "en" else ("アルファ", "ベータ"))
                        self.assertEqual(len(result.ir.relationships), 1)
                    elif kind == "process-reference-model":
                        self.assertEqual(len(result.ir.processes), 2)
                        self.assertEqual(tuple(len(item.outcomes) for item in result.ir.processes), (1, 1))
                    else:
                        self.assertEqual(len(result.ir.source_processes), 2)
                        self.assertEqual(len(result.ir.included_activities_tasks), 2)
                        self.assertEqual(len(result.ir.application), 1)

            minimal_process = _clean(
                """
                # Minimal Process

                ## Purpose

                Establishes a minimal Process result.

                ## Outcomes

                - The minimal result is available.
                """
            )
            minimal = _parse(
                root,
                _asset("minimal-process", "process", "en", minimal_process, metadata=False),
                name="minimal-process",
            )
            self.assert_no_errors(minimal)
            self.assertEqual(minimal.ir.activities, ())

            local_en = _write(
                root,
                "skills/local-view/SKILL.md",
                _asset("local-view", "process-view", "en", _local_view_body("en")),
            )
            local_ja = _write(
                root,
                "skills/local-view/references/locales/ja/SKILL.md",
                _asset("local-view", "process-view", "ja", _local_view_body("ja")),
            )
            local = CHECKER.parse_asset(local_en, "en")
            self.assert_no_errors(local)
            self.assertEqual(len(local.ir.activities), 1)
            self.assertEqual(local.ir.source_processes, ())
            self.assertEqual(local.ir.included_activities_tasks, ())
            self.assertEqual(
                _check_pair(
                    local_en,
                    local_ja,
                    roots={"example/alps@1.2.3": root},
                ),
                ([], []),
            )

    def test_typed_ir_snapshot_keeps_spans_identities_and_roles(self) -> None:
        body = _process_body(
            "en",
            outcome_lines=("The outcome `skill:#alpha` is ready.",),
            task_lines=("The agent must inspect the input.",),
        )
        with _temp_root() as root:
            result = _parse(root, _asset("snapshot-process", "process", "en", body, metadata=False), locale="en", name="snapshot-process")
            self.assert_no_errors(result)
            ir = result.ir
            snapshot = asdict(ir)
            json.dumps(snapshot, ensure_ascii=False)
            self.assertEqual(snapshot["locale"], "en")
            self.assertEqual(snapshot["kind"], "process")
            self.assertEqual([item["key"] for item in snapshot["sections"]], ["purpose", "outcomes", "activities"])
            self.assertEqual(snapshot["outcomes"][0]["identity"], "`skill:#alpha`")
            self.assertEqual(snapshot["activities"][0]["tasks"][0]["normative_class"], "must")
            self.assertEqual(ir.frontmatter.name_span.line, 2)
            self.assertEqual(ir.frontmatter.name_span.column, len("name: "))
            self.assertEqual(ir.sections[0].span.line, 7)
            self.assertEqual(ir.outcomes[0].references[0].span.line, ir.outcomes[0].line)
            self.assertEqual(ir.outcomes[0].references[0].token, "`skill:#alpha`")

            model = _parse(root, _asset("snapshot-model", "process-model", "en", _model_body()), name="snapshot-model")
            self.assert_no_errors(model)
            self.assertEqual(tuple(item.name for item in model.ir.processes), ("Alpha", "Beta"))
            self.assertEqual(model.ir.processes[0].reference.skill_name, "alpha")
            self.assertEqual(model.ir.relationships[0].provider_process, "Alpha")

            view = _parse(root, _asset("snapshot-view", "process-view", "en", _view_body()), name="snapshot-view")
            self.assert_no_errors(view)
            self.assertEqual(view.ir.source_processes[0].reference.token, "`skill:#alpha`")
            self.assertEqual(view.ir.included_activities_tasks[0].kind, "activity")

    def test_document_reference_aggregation_is_unique_without_collapsing_record_order(self) -> None:
        process = _process_body(
            outcome_lines=("The outcome `skill:#alpha` and `skill:#alpha` is ready.",),
            task_lines=("The agent must inspect `skill:#alpha` and `skill:#alpha`.",),
        )
        with _temp_root() as root:
            parsed = _parse(root, _asset("reference-aggregation", "process", "en", process), name="reference-aggregation")
            self.assert_no_errors(parsed)
            self.assertEqual(
                tuple(reference.token for reference in parsed.ir.outcomes[0].references),
                ("`skill:#alpha`", "`skill:#alpha`"),
            )
            self.assertEqual(
                tuple(reference.token for reference in parsed.ir.activities[0].tasks[0].references),
                ("`skill:#alpha`", "`skill:#alpha`"),
            )
            self.assertEqual(tuple(reference.token for reference in parsed.ir.references), ("`skill:#alpha`",))

            view_body = _view_body().replace("Apply this view.", "Apply `skill:#alpha` and `skill:#alpha`.")
            view = _parse(root, _asset("reference-application", "process-view", "en", view_body), name="reference-application")
            self.assert_no_errors(view)
            self.assertEqual(
                tuple(reference.token for reference in view.ir.application[0].references),
                ("`skill:#alpha`", "`skill:#alpha`"),
            )
            aggregate_tokens = tuple(reference.token for reference in view.ir.references)
            self.assertEqual(len(aggregate_tokens), len(set(aggregate_tokens)))

    def test_shipped_assets_parse_and_cli_default_requires_japanese(self) -> None:
        self.assertTrue(CHECKER_PATH.is_file())
        self.assertFalse((ROOT / "skills/define-alps/scripts/check_alps_asset.py").exists())
        self.assertFalse((ROOT / "skills/define-alps/scripts/alps_check").exists())
        self.assertTrue((ROOT / "spec/alps-markdown.md").is_file())
        self.assertTrue((ROOT / "spec/alps-markdown-v2.md").is_file())
        self.assertFalse((ROOT / "spec/checker-profile.md").exists())
        shipped = sorted(ROOT.glob("skills/*/SKILL.md")) + sorted(ROOT.glob("skills/*/references/locales/ja/SKILL.md"))
        self.assertEqual(len(shipped), 8)
        for path in shipped:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                result = CHECKER.parse_asset(path)
                self.assert_no_errors(result)
                self.assertIsNotNone(result.ir)

        templates = (
            ("en", ROOT / "skills/define-alps/references/SKILL-template.md", "Example"),
            ("ja", ROOT / "skills/define-alps/references/locales/ja/SKILL-template.md", "例"),
        )
        with _temp_root() as root:
            for locale, path, replacement in templates:
                with self.subTest(template=locale):
                    source = path.read_text(encoding="utf-8")
                    self.assertIn("alps-markdown/v2", source)
                    self.assertNotIn('description: "', source)
                    fenced = source.split("```markdown\n", 1)[1].split("\n```", 1)[0] + "\n"
                    fenced = fenced.replace(
                        "name: <lowercase-hyphen-name>", "name: template-process"
                    )
                    materialized = re.sub(r"<[^>\n]+>", replacement, fenced)
                    parsed = CHECKER.parse_asset(
                        _write(root, f"template-{locale}.md", materialized), locale
                    )
                    self.assert_no_errors(parsed)
                    self.assertEqual(parsed.ir.kind, "process")

        original = os.getcwd()
        try:
            os.chdir(ROOT)
            binding = f"alps@0.5.0-test={ROOT}"
            for args in (
                ("--package-binding", binding, "--package-id", "alps", "--package-version", "0.5.0-test"),
                ("--package-binding", binding, "--package-id", "alps", "--package-version", "0.5.0-test", "--require-japanese"),
            ):
                with self.subTest(cli_args=args):
                    stdout, stderr = io.StringIO(), io.StringIO()
                    with redirect_stdout(stdout), redirect_stderr(stderr):
                        status = CHECKER.main(list(args))
                    self.assertEqual(status, 0, stderr.getvalue())
                    self.assertIn("PROFILE_VERSION=alps-markdown/v2", stdout.getvalue())
                    self.assertIn("not an ALPS Conformance claim", stdout.getvalue())
        finally:
            os.chdir(original)

    def test_frontmatter_exact_order_fields_defaults_suffix_and_rejections(self) -> None:
        base = _frontmatter("fixture", "process", "en", metadata=False)
        metadata = _frontmatter("fixture", "process-view", "en")
        cases = (
            ("unknown", base.replace("\ndescription:", "\nextra: value\ndescription:", 1), "unknown-key", "unsupported-profile-syntax"),
            ("duplicate", base.replace("description:", "name: other\ndescription:"), "duplicate-key", "unsupported-profile-syntax"),
            ("missing-required", base.replace("description: Canonical process fixture. ALPS-conformant.\n", ""), "missing-field", "profile-structure"),
            ("wrong-order", base.replace("name: fixture\ndescription:", "description: Canonical process fixture. ALPS-conformant.\nname: fixture\n#"), "field-order", "profile-structure"),
            ("alias", metadata.replace("alps.kind: process-view", "alps.kind: *view"), "unsupported-scalar", "unsupported-profile-syntax"),
            ("anchor", metadata.replace("alps.kind: process-view", "alps.kind: &view process-view"), "unsupported-scalar", "unsupported-profile-syntax"),
            ("merge", metadata.replace("metadata:\n", "<<: *base\nmetadata:\n"), "unknown-key", "unsupported-profile-syntax"),
            ("tag", metadata.replace("alps.kind: process-view", "alps.kind: !str process-view"), "unsupported-scalar", "unsupported-profile-syntax"),
            ("flow", metadata.replace("alps.kind: process-view", "alps.kind: {kind: process-view}"), "unsupported-scalar", "unsupported-profile-syntax"),
            ("block", base.replace("description: Canonical process fixture. ALPS-conformant.", "description: |"), "unsupported-scalar", "unsupported-profile-syntax"),
            ("sequence", metadata.replace("alps.kind: process-view", "alps.kind: - process-view"), "unsupported-scalar", "unsupported-profile-syntax"),
            ("quoted", base.replace("name: fixture", 'name: "fixture"'), "unsupported-scalar", "unsupported-profile-syntax"),
            ("tab", base.replace("description:", "\tdescription:"), "tab-indentation", "unsupported-profile-syntax"),
            ("continuation", base.replace("description: Canonical process fixture. ALPS-conformant.\n", "description: Canonical process fixture. ALPS-conformant.\n continuation\n"), "continuation-line", "unsupported-profile-syntax"),
            ("wrong-indent", metadata.replace("  alps.kind:", "   alps.kind:"), "unknown-metadata-child", "unsupported-profile-syntax"),
            ("empty-metadata", metadata.replace("  alps.kind: process-view\n", ""), "empty-metadata", "unsupported-profile-syntax"),
        )
        with _temp_root() as root:
            for label, frontmatter, code, class_name in cases:
                with self.subTest(case=label):
                    result = _parse(root, frontmatter + _process_body(), name=f"frontmatter-{label}")
                    self.assertIn(code, _codes(result))
                    self.assertIn(class_name, _classes(result))

            default = _parse(root, base + _process_body(), name="frontmatter-default")
            self.assert_no_errors(default)
            self.assertEqual(default.frontmatter.kind, "process")

            japanese = _frontmatter("fixture", "process", "ja", metadata=False).replace("ALPS準拠。", "ALPS-conformant.")
            japanese_path = _write(root, "references/locales/ja/suffix.md", japanese + _process_body("ja"))
            checked = CHECKER.check_document(japanese_path, {"example/alps@1.2.3": root})
            self.assertIn("description-suffix", _codes(checked))
            self.assertTrue(any(item.class_name == "profile-structure" for item in checked.diagnostics))

    def test_h1_h2_exact_grammar_order_duplicates_required_and_html_boundary(self) -> None:
        canonical = _asset("heading", "process", "en", _process_body(), metadata=False)
        replacements = (
            ("setext-h1", "# Fixture Process\n", "Fixture Process\n===\n", "setext-heading"),
            ("closing-h1", "# Fixture Process\n", "# Fixture Process ##\n", "closing-heading"),
            ("indented-h1", "# Fixture Process\n", " # Fixture Process\n", "indented-container"),
            ("h1-tab", "# Fixture Process\n", "#\tFixture Process\n", "literal-tab-h1"),
            ("h7", "# Fixture Process\n", "####### Too Deep\n# Fixture Process\n", "heading-level"),
            ("unknown-h2", "## Purpose\n", "## Unknown\n\n## Purpose\n", "unrecognized-h2"),
            ("duplicate", "\n## Activities & Tasks\n", "\n## Activities & Tasks\n\n## Activities & Tasks\n", "duplicate-section"),
            ("out-of-order", "## Purpose\n\n", "## Outcomes\n\n## Purpose\n\n", "section-order"),
            ("missing-required", "## Outcomes\n", "", "missing-section"),
        )
        with _temp_root() as root:
            for label, old, new, code in replacements:
                with self.subTest(case=label):
                    content = canonical.replace(old, new, 1)
                    result = _parse(root, content, name=f"heading-{label}")
                    self.assertIn(code, _codes(result))

            html = canonical.replace(
                "## Activities & Tasks\n",
                "## Inputs\n\n<pre>\n# Fake H1\n## Outcomes\n- Fake outcome\n</pre>\n\n## Activities & Tasks\n",
            )
            result = _parse(root, html, name="heading-html")
            self.assertIn("raw-html", _codes(result))
            self.assertEqual(result.ir.title, "Fixture Process")
            self.assertEqual(len(result.ir.outcomes), 1)
            self.assertEqual(len(result.ir.activities), 1)

    def test_opaque_containers_are_hidden_and_boundaries_are_diagnostic(self) -> None:
        opaque = _process_body() + _clean(
            """
                ## Inputs

                Ordinary prose remains opaque.

                ```markdown
                # Fake H1
                ### Fake Activity
                1. Fake task must not enter the IR.
                `skill:#hidden-fence`
                ```

                > ## Fake Blockquote
                > - Fake outcome
                > `skill:#hidden-quote`

                <!--
                ## Fake Comment
                - Fake outcome
                `skill:#hidden-comment`
                -->
            """
        )
        negative = (
            ("unclosed-fence", opaque.replace("```\n\n> ## Fake", "```\n\n> ## Fake", 1).rsplit("```", 1)[0], "unclosed-fence"),
            ("nested-fence", opaque.replace("```markdown", "- ```markdown", 1), "nested-container"),
            ("indented-fence", opaque.replace("```markdown", "   ```markdown", 1), "indented-container"),
            ("nested-blockquote", opaque.replace("> ## Fake Blockquote", "> > Fake Blockquote", 1), "nested-blockquote"),
            ("indented-block", opaque.replace("> ## Fake Blockquote", "    ## Fake Blockquote", 1), "indented-container"),
            ("unclosed-comment", opaque.replace("<!--\n", "<!--\n", 1).rsplit("-->\n", 1)[0], "unclosed-comment"),
        )
        with _temp_root() as root:
            result = _parse(root, _asset("opaque", "process", "en", opaque, metadata=False), name="opaque")
            self.assert_no_errors(result)
            self.assertEqual(len(result.ir.outcomes), 1)
            self.assertEqual(len(result.ir.activities), 1)
            self.assertEqual(len(result.ir.activities[0].tasks), 1)
            self.assertEqual(result.ir.references, ())
            for label, body, code in negative:
                with self.subTest(case=label):
                    parsed = _parse(root, _asset(label, "process", "en", body, metadata=False), name=label)
                    self.assertIn(code, _codes(parsed))

    def test_process_outcome_activity_task_structure_and_normative_classes(self) -> None:
        markers = (
            ("en-must-not", "The agent must not skip this step.", "must-not"),
            ("en-must", "The agent must inspect this step.", "must"),
            ("en-should-not", "The agent should not skip this step.", "should-not"),
            ("en-should", "The agent should inspect this step.", "should"),
            ("en-may", "The agent may inspect this step.", "may"),
            ("en-typically", "The agent typically inspects this step.", "typically"),
            ("ja-must-not", "この手順を省略してはならない。", "must-not"),
            ("ja-must", "この手順を実施する必要がある。", "must"),
            ("ja-should-not", "この手順は避けるのが望ましい。", "should-not"),
            ("ja-should", "この手順を行うのが望ましい。", "should"),
            ("ja-may", "この手順を変更してもよい。", "may"),
            ("ja-typically", "通常この手順を使う。", "typically"),
            ("precedence-must-not", "The agent must not skip this step.", "must-not"),
            ("precedence-should", "The agent must not skip; it should proceed.", "should"),
            ("precedence-should-not", "The agent should not skip this step.", "should-not"),
            ("precedence-must", "The agent should not skip; it must proceed.", "must"),
        )
        with _temp_root() as root:
            for label, task, expected in markers:
                locale = "ja" if label.startswith("ja-") else "en"
                with self.subTest(case=label):
                    parsed = _parse(
                        root,
                        _asset(label, "process", locale, _process_body(locale, task_lines=(task,)), metadata=False),
                        locale=locale,
                        name=label,
                    )
                    self.assert_no_errors(parsed)
                    self.assertEqual(parsed.ir.activities[0].tasks[0].normative_class, expected)

            continued = _process_body(
                outcome_lines=("The outcome starts.",),
                task_lines=("The agent must act.",),
            ).replace("- The outcome starts.", "- The outcome starts.\n   and continues.")
            continued = continued.replace("1. The agent must act.", "1. The agent must act.\n   with evidence.")
            parsed = _parse(root, _asset("continuations", "process", "en", continued, metadata=False), name="continuations")
            self.assert_no_errors(parsed)
            self.assertEqual(parsed.ir.outcomes[0].text, "The outcome starts. and continues.")
            self.assertEqual(parsed.ir.activities[0].tasks[0].text, "The agent must act. with evidence.")

            syntax_cases = (
                ("outcome-table", "- The result is ready.\n", "| Result |\n| --- |\n| ready |\n", "outcome-list-syntax"),
                ("outcome-prose", "- The result is ready.\n", "The result is ready.\n", "outcome-list-missing"),
                ("outcome-second-list", "- The result is ready.\n", "- The result is ready.\n\n- Another result.\n", "outcome-second-list"),
                ("outcome-nested-list", "- The result is ready.\n", "- The result is ready.\n   - Nested result.\n", "indented-container"),
                ("task-second-list", "1. The agent must act.\n", "1. The agent must act.\n\n2. The agent must record.\n", "task-second-list"),
                ("task-nested-list", "1. The agent must act.\n", "1. The agent must act.\n   - Nested task.\n", "indented-container"),
                ("h4-child", "### Inspect\n", "### Inspect\n\n#### Tasks\n\n", "activity-heading"),
            )
            for label, old, new, code in syntax_cases:
                with self.subTest(case=label):
                    source = _process_body(task_lines=("The agent must act.",)) if label.startswith("task-") else _process_body()
                    body = source.replace(old, new, 1)
                    parsed = _parse(root, _asset(label, "process", "en", body, metadata=False), name=label)
                    self.assertIn(code, _codes(parsed))

            quality = _parse(
                root,
                _asset("quality", "process", "en", _process_body(outcome_lines=("The result is recorded.",)), metadata=False),
                name="quality",
            )
            self.assertIn("outcome-recorded-language", _codes(quality))
            self.assertIn("quality-review", _classes(quality))
            self.assertFalse(any(item.severity is Severity.ERROR for item in quality.diagnostics))

            control_body = _process_body(extra="\n## Inputs\n\nApplicable Controls are listed here.\n")
            control = _parse(root, _asset("control", "process", "en", control_body, metadata=False), name="control")
            self.assertIn("input-classified-control", _codes(control))
            self.assertIn("semantic", _classes(control))


    def test_required_prose_rejects_headings_for_all_kinds_and_view_application(self) -> None:
        purpose_cases = (
            ("process", _process_body(), "Defines the purpose of this fixture."),
            ("process-model", _model_body(), "Organizes related Processes."),
            ("process-reference-model", _reference_model_body(), "Organizes Process semantic centers."),
            ("process-view", _view_body(), "Presents Processes through one concern."),
        )
        with _temp_root() as root:
            for kind, body, purpose in purpose_cases:
                for variant, replacement in (
                    ("heading-only", "### Hidden Purpose\n"),
                    ("heading-plus-prose", "### Hidden Purpose\n\n" + purpose),
                ):
                    with self.subTest(kind=kind, purpose_variant=variant):
                        parsed = _parse(
                            root,
                            _asset(f"required-purpose-{kind}-{variant}", kind, "en", body.replace(purpose, replacement, 1)),
                            name=f"required-purpose-{kind}-{variant}",
                        )
                        self.assertIn("required-prose-heading", _codes(parsed))
                        if variant == "heading-only":
                            self.assertIn("purpose-empty", _codes(parsed))
                        else:
                            self.assertEqual(parsed.ir.purpose, purpose)

            entry_body = _reference_model_body().replace(
                "Define Alpha.", "##### Hidden Entry Purpose\n\nDefine Alpha.", 1
            )
            entry = _parse(
                root,
                _asset("required-entry-purpose", "process-reference-model", "en", entry_body),
                name="required-entry-purpose",
            )
            self.assertIn("required-prose-heading", _codes(entry))

            for variant, replacement in (
                ("heading-only", "### Hidden Application\n"),
                ("heading-plus-prose", "### Hidden Application\n\nApply this view."),
            ):
                with self.subTest(application_variant=variant):
                    body = _view_body().replace("Apply this view.", replacement, 1)
                    parsed = _parse(
                        root,
                        _asset(f"required-application-{variant}", "process-view", "en", body),
                        name=f"required-application-{variant}",
                    )
                    self.assertIn("required-prose-heading", _codes(parsed))
                    if variant == "heading-only":
                        self.assertIn("application-empty", _codes(parsed))
                    else:
                        self.assertEqual(parsed.ir.application[0].text, "Apply this view.")

    def test_decimal_task_marker_is_bounded_without_internal_failure(self) -> None:
        huge_marker = "9" * 5000
        body = _process_body().replace(
            "1. The agent must inspect the input.",
            f"{huge_marker}. The agent must inspect the input.",
            1,
        )
        with _temp_root() as root:
            path = _write(root, "huge-task-marker.md", _asset("huge-task-marker", "process", "en", body))
            checked = CHECKER.check_document(path, {"example/alps@1.2.3": root})
            self.assertEqual(checked.exit_status, 1)
            self.assertIn("task-list-start", _codes(checked))
            self.assertNotIn("internal", _classes(checked))


class AlpsMarkdownProfileMilestoneBTests(unittest.TestCase):
    PACKAGE_ID = "example/alps"
    PACKAGE_VERSION = "1.2.3"

    @staticmethod
    def _roots(root: Path, qualified: bool = False) -> dict[str, Path]:
        del qualified
        return {
            f"{AlpsMarkdownProfileMilestoneBTests.PACKAGE_ID}"
            f"@{AlpsMarkdownProfileMilestoneBTests.PACKAGE_VERSION}": root
        }

    @staticmethod
    def _qualified(body: str) -> str:
        return body.replace(
            "skill:#",
            f"skill:{AlpsMarkdownProfileMilestoneBTests.PACKAGE_ID}#",
        )

    @staticmethod
    def _write_targets(
        root: Path,
        *,
        japanese: bool = True,
        titles: dict[str, str] | None = None,
        japanese_titles: dict[str, str] | None = None,
    ) -> None:
        titles = titles or {"alpha": "Alpha", "beta": "Beta"}
        japanese_titles = japanese_titles or {
            key: {"alpha": "アルファ", "beta": "ベータ"}.get(key, value)
            for key, value in titles.items()
        }
        for skill, title in titles.items():
            _write(
                root,
                f"skills/{skill}/SKILL.md",
                _asset(skill, "process", "en", _process_body("en", title=title), metadata=False),
            )
            if japanese:
                _write(
                    root,
                    f"skills/{skill}/references/locales/ja/SKILL.md",
                    _asset(skill, "process", "ja", _process_body("ja", title=japanese_titles[skill]), metadata=False),
                )

    @staticmethod
    def _check(root: Path, relative: str, content: str, *, qualified: bool = False, package_id: str | None = None):
        path = _write(root, relative, content)
        current_package = package_id or AlpsMarkdownProfileMilestoneBTests.PACKAGE_ID
        return CHECKER.check_document(
            path,
            AlpsMarkdownProfileMilestoneBTests._roots(root, qualified),
            current_package,
        )

    @staticmethod
    def _reference_body(locale: str = "en", *, reversed_relationship: bool = False) -> str:
        if locale == "ja":
            alpha_name, beta_name = "アルファ", "ベータ"
            purpose, outcome = "このフィクスチャの目的を定義する。", "成果が準備される。"
            skill, purpose_heading, outcomes_heading, relationships = "スキル", "目的", "成果", "関係"
            headers = "| 提供側プロセス | 情報 | 受領側プロセス | 関係 |\n| --- | --- | --- | --- |"
        else:
            alpha_name, beta_name = "Alpha", "Beta"
            purpose, outcome = "Defines the purpose of this fixture.", "The result is ready."
            skill, purpose_heading, outcomes_heading, relationships = "Skill", "Purpose", "Outcomes", "Relationships"
            headers = "| Provider Process | Information | Recipient Process | Relationship |\n| --- | --- | --- | --- |"
        headers = headers.replace("\n", "\n            ")
        provider, recipient = (beta_name, alpha_name) if reversed_relationship else (alpha_name, beta_name)
        return _clean(
            f"""
            # Fixture Reference Model

            ## {_heading(locale, 'purpose')}

            Organizes Process semantic centers.

            ## {_heading(locale, 'processes')}

            ### {alpha_name}

            {skill}: `skill:#alpha`

            #### {purpose_heading}

            {purpose}

            #### {outcomes_heading}

            - {outcome}

            ### {beta_name}

            {skill}: `skill:#beta`

            #### {purpose_heading}

            {purpose}

            #### {outcomes_heading}

            - {outcome}

            ## {relationships}

            {headers}
            | {provider} | Information | {recipient} | Supports |
            """
        )

    def assert_no_errors(self, result) -> None:
        errors = [item.render() for item in result.diagnostics if item.severity is Severity.ERROR]
        self.assertEqual(errors, [], "\n".join(errors))

    def test_exact_machine_tables_reject_profile_boundary_forms(self) -> None:
        specs = (
            ("processes", _model_body(), "| Process | Skill |", "| --- | --- |", "| Beta | |", "## Relationships\n", "Process"),
            ("relationships", _model_body(), "| Provider Process | Information | Recipient Process | Relationship |", "| --- | --- | --- | --- |", "| Alpha | Information | Beta | Supports |", "## Relationships\n", "Provider Process"),
            ("source", _view_body(), "| Source Process | Reference |", "| --- | --- |", "| Alpha | `skill:#alpha` |", "## Included Activities and Tasks\n", "Source Process"),
            ("included", _view_body(), "| Source Process | Source element |", "| --- | --- |", "| Alpha (`skill:#alpha`) | Activity: Inspect |", "## Application\n", "Source Process"),
        )
        boundaries = (
            ("no-padding", lambda header, separator, row: (header, separator, row.replace("| ", "|", 1)), "table-width"),
            ("multi-padding", lambda header, separator, row: (header, separator, row.replace("| ", "|  ", 1)), "table-width"),
            ("unpiped", lambda header, separator, row: (header[1:], separator, row), "table-width"),
            ("wrong-header", lambda header, separator, row: (header.replace(header.split(" | ")[0].lstrip("| "), "Name", 1), separator, row), "table-header"),
            ("reordered-header", lambda header, separator, row: ("| " + " | ".join(reversed(header.strip("| ").split(" | "))) + " |", separator, row), "table-header"),
            ("localized-header", lambda header, separator, row: ("| プロセス | スキル |" if "Skill" in header else "| プロセス | 情報 | 受領側プロセス | 関係 |" if "Provider" in header else "| 出典プロセス | 参照 |" if "Reference" in header else "| 出典プロセス | 出典要素 |", separator, row), "table-header"),
            ("alignment-separator", lambda header, separator, row: (header, separator.replace("---", ":---", 1), row), "table-separator"),
            ("short-row", lambda header, separator, row: (header, separator, "|".join(row.split("|")[:-2]) + "|"), "table-width"),
            ("extra-row", lambda header, separator, row: (header, separator, row.rsplit(" |", 1)[0] + " | Extra |"), "table-width"),
            ("cell-pipe", lambda header, separator, row: (header, separator, row.rsplit(" |", 1)[0] + " | pipe |"), "table-width"),
        )
        with _temp_root() as root:
            for schema, source, header, separator, row, next_heading, _ in specs:
                for boundary, mutate, expected in boundaries:
                    with self.subTest(schema=schema, boundary=boundary):
                        changed_header, changed_separator, changed_row = mutate(header, separator, row)
                        body = source.replace(header, changed_header, 1).replace(separator, changed_separator, 1).replace(row, changed_row, 1)
                        result = _parse(root, _asset(f"table-{schema}-{boundary}", "process-model" if schema in ("processes", "relationships") else "process-view", "en", body), name=f"table-{schema}-{boundary}")
                        self.assertIn(expected, _codes(result))

                with self.subTest(schema=schema, boundary="second-table"):
                    second = f"\n{header}\n{separator}\n{row}\n"
                    body = source.replace(next_heading, second + next_heading, 1)
                    result = _parse(root, _asset(f"table-{schema}-second", "process-model" if schema in ("processes", "relationships") else "process-view", "en", body), name=f"table-{schema}-second")
                    self.assertIn("table-second", _codes(result))
                with self.subTest(schema=schema, boundary="mixed-list"):
                    body = source.replace(row, row + "\n- mixed content", 1)
                    result = _parse(root, _asset(f"table-{schema}-mixed", "process-model" if schema in ("processes", "relationships") else "process-view", "en", body), name=f"table-{schema}-mixed")
                    self.assertIn("table-mixed-content", _codes(result))

            rejected = (
                ("process-list", _model_body().replace("| Process | Skill |\n| --- | --- |\n| Alpha | `skill:#alpha` |\n| Beta | |", "- Alpha\n- Beta"), "table-missing"),
                ("process-h3", _model_body().replace("| Process | Skill |\n| --- | --- |\n| Alpha | `skill:#alpha` |\n| Beta | |", "### Alpha\n\nPurpose"), "table-heading"),
                ("relationship-arrow", _model_body().replace("| Provider Process | Information | Recipient Process | Relationship |\n| --- | --- | --- | --- |\n| Alpha | Information | Beta | Supports |", "- Alpha -> Beta"), "table-missing"),
            )
            for label, body, expected in rejected:
                with self.subTest(case=label):
                    result = _parse(root, _asset(label, "process-model", "en", body), name=label)
                    self.assertIn(expected, _codes(result))

    def test_process_model_semantics_references_endpoints_and_locale_identity(self) -> None:
        with _temp_root() as root:
            self._write_targets(root)
            valid = self._check(root, "model.md", _asset("model", "process-model", "en", _model_body()))
            self.assert_no_errors(valid)

            qualified = self._check(
                root,
                "qualified-model.md",
                _asset("model", "process-model", "en", self._qualified(_model_body())),
                qualified=True,
                package_id="example/alps",
            )
            self.assert_no_errors(qualified)

            cases = (
                ("duplicate-name", _model_body().replace("| Beta | |", "| Alpha | |"), "process-duplicate"),
                ("duplicate-reference", _model_body().replace("| Beta | |", "| Beta | `skill:#alpha` |"), "process-duplicate"),
                ("undeclared-endpoint", _model_body().replace("| Alpha | Information | Beta | Supports |", "| Gamma | Information | Beta | Supports |"), "relationship-endpoint"),
                ("reference-endpoint", _model_body().replace("| Alpha | Information | Beta | Supports |", "| `skill:#alpha` | Information | Beta | Supports |"), "relationship-endpoint-reference"),
            )
            for label, body, expected in cases:
                with self.subTest(case=label):
                    result = self._check(root, f"model-{label}.md", _asset(label, "process-model", "en", body))
                    self.assertIn(expected, _codes(result))

        with _temp_root() as root:
            self._write_targets(root, titles={"alpha": "Not Alpha", "beta": "Beta"})
            mismatch = self._check(root, "display-mismatch.md", _asset("model", "process-model", "en", _model_body()))
            self.assertIn("reference-display", _codes(mismatch))

        with _temp_root() as root:
            _write(root, "skills/alpha/SKILL.md", _asset("alpha", "process-model", "en", _model_body()))
            self._write_targets(root, titles={"beta": "Beta"})
            target_kind = self._check(root, "target-kind.md", _asset("model", "process-model", "en", _model_body()))
            self.assertIn("reference-target-kind", _codes(target_kind))

        en_body = _model_body().replace("| Beta | |", "| Beta | `skill:#beta` |")
        ja_body = _model_body("ja").replace("| ベータ | |", "| ベータ | `skill:#beta` |")
        with _temp_root() as root:
            self._write_targets(root)
            english = _write(root, "model-en.md", _asset("model", "process-model", "en", en_body))
            japanese = _write(root, "model-ja.md", _asset("model", "process-model", "ja", ja_body))
            errors, warnings = _check_pair(english, japanese, roots=self._roots(root))
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

            reversed_body = ja_body.replace("| アルファ | 情報 | ベータ |", "| ベータ | 情報 | アルファ |")
            reversed_path = _write(root, "model-reversed-ja.md", _asset("model", "process-model", "ja", reversed_body))
            errors, _ = _check_pair(english, reversed_path, roots=self._roots(root))
            self.assertTrue(any("model-relationship-provider-mismatch" in item for item in errors))

            empty_en = en_body.replace("| Alpha | `skill:#alpha` |", "| Alpha | |", 1).replace("| Beta | `skill:#beta` |", "| Beta | |", 1)
            empty_ja = ja_body.replace("| アルファ | `skill:#alpha` |", "| アルファ | |", 1).replace("| ベータ | `skill:#beta` |", "| ベータ | |", 1)
            empty_path = _write(root, "model-empty-ja.md", _asset("model", "process-model", "ja", empty_ja))
            warning_errors, warning_only = _check_pair(
                _write(root, "model-empty-en.md", _asset("model", "process-model", "en", empty_en)),
                empty_path,
                roots=self._roots(root),
            )
            self.assertEqual(warning_errors, [])
            self.assertTrue(any("warning unverified-locale-identity" in item for item in warning_only))

    def test_reference_model_structure_skill_position_target_equality_and_pairs(self) -> None:
        with _temp_root() as root:
            self._write_targets(root, japanese=False)
            valid = self._check(root, "reference.md", _asset("reference", "process-reference-model", "en", self._reference_body()))
            self.assert_no_errors(valid)

            structural = (
                ("wrong-h4-order", self._reference_body().replace("#### Purpose\n\nDefines the purpose of this fixture.\n\n#### Outcomes\n\n- The result is ready.", "#### Outcomes\n\n- The result is ready.\n\n#### Purpose\n\nDefines the purpose of this fixture.", 1), "reference-entry-purpose"),
                ("no-pre-h4-prose", self._reference_body().replace("Skill: `skill:#alpha`\n", "Skill: `skill:#alpha`\nPreamble is not permitted.\n", 1), "reference-entry-preamble"),
                ("skill-after-h4", self._reference_body().replace("Skill: `skill:#alpha`\n", "", 1).replace("#### Purpose\n\n", "#### Purpose\n\nSkill: `skill:#alpha`\n\n", 1), "skill-position"),
                ("wrong-entry-level", self._reference_body().replace("### Alpha", "#### Alpha", 1).replace("### Beta", "#### Beta", 1), "process-empty"),
            )
            for label, body, expected in structural:
                with self.subTest(case=label):
                    result = _parse(root, _asset(label, "process-reference-model", "en", body), name=label)
                    self.assertIn(expected, _codes(result))

            japanese = _parse(root, _asset("reference-ja", "process-reference-model", "ja", self._reference_body("ja")), locale="ja", name="reference-ja")
            self.assert_no_errors(japanese)
            wrong_locale_skill = self._reference_body("ja").replace("スキル:", "Skill:", 1)
            wrong_locale = _parse(root, _asset("reference-ja-skill", "process-reference-model", "ja", wrong_locale_skill), locale="ja", name="reference-ja-skill")
            self.assertIn("skill-locale", _codes(wrong_locale))

            purpose_bad = self._reference_body().replace("Defines the purpose of this fixture.", "A different purpose.", 1)
            result = self._check(root, "reference-purpose-bad.md", _asset("reference", "process-reference-model", "en", purpose_bad))
            self.assertIn("reference-purpose", _codes(result))
            outcome_bad = self._reference_body().replace("- The result is ready.", "- A different outcome is ready.", 1)
            result = self._check(root, "reference-outcome-bad.md", _asset("reference", "process-reference-model", "en", outcome_bad))
            self.assertIn("reference-outcomes", _codes(result))

        with _temp_root() as root:
            self._write_targets(root)
            english = _write(root, "reference-en.md", _asset("reference", "process-reference-model", "en", self._reference_body()))
            japanese = _write(root, "reference-ja-reversed.md", _asset("reference", "process-reference-model", "ja", self._reference_body("ja", reversed_relationship=True)))
            errors, warnings = _check_pair(english, japanese, roots=self._roots(root))
            self.assertTrue(any("reference-relationship-provider-mismatch" in item for item in errors))
            self.assertTrue(all("error locale-mismatch/" in item for item in errors))
            self.assertEqual(warnings, [])

            shipped_en = ROOT / "skills/alps-reference-model/SKILL.md"
            shipped_ja = ROOT / "skills/alps-reference-model/references/locales/ja/SKILL.md"
            errors, warnings = _check_pair(
                shipped_en,
                shipped_ja,
                package_identity="alps@0.5.0-candidate",
                roots={"alps@0.5.0-candidate": ROOT},
                package_id="alps",
            )
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])


class AlpsMarkdownProfileMilestoneCTests(unittest.TestCase):
    def assert_no_errors(self, result) -> None:
        errors = [item.render() for item in result.diagnostics if item.severity is Severity.ERROR]
        self.assertEqual(errors, [], "\n".join(errors))

    def test_process_view_sources_inclusions_and_locale_matrices(self) -> None:
        helper = AlpsMarkdownProfileMilestoneBTests
        with _temp_root() as root:
            helper._write_targets(root)
            valid = helper._check(root, "view.md", _asset("view", "process-view", "en", _view_body()))
            self.assert_no_errors(valid)

            one_source = _view_body().replace("| Beta | `skill:#beta` |\n", "").replace(
                "| Beta (`skill:#beta`) | Task: Record |\n", ""
            )
            self.assert_no_errors(
                helper._check(root, "view-one-source.md", _asset("view", "process-view", "en", one_source))
            )

            cases = (
                ("duplicate-source", _view_body().replace("| Beta | `skill:#beta` |", "| Alpha | `skill:#alpha` |"), "source-duplicate"),
                ("empty-source-reference", _view_body().replace("| Beta | `skill:#beta` |", "| Beta | |"), "malformed-reference"),
                ("multiple-source-references", _view_body().replace("| Beta | `skill:#beta` |", "| Beta | `skill:#beta` `skill:#alpha` |"), "malformed-reference"),
                ("display-target-mismatch", _view_body().replace("| Alpha | `skill:#alpha` |", "| Wrong | `skill:#alpha` |").replace("Alpha (`skill:#alpha`)", "Wrong (`skill:#alpha`)"), "source-display"),
                ("undeclared-inclusion", _view_body().replace("Alpha (`skill:#alpha`)", "Gamma (`skill:#gamma`)"), "included-source"),
                ("mismatched-inclusion", _view_body().replace("Alpha (`skill:#alpha`)", "Beta (`skill:#alpha`)"), "included-source"),
                ("duplicate-inclusion", _view_body().replace("| Beta (`skill:#beta`) | Task: Record |", "| Beta (`skill:#beta`) | Task: Record |\n| Beta (`skill:#beta`) | Task: Record |"), "included-duplicate"),
                ("bad-inclusion-prefix", _view_body().replace("Activity: Inspect", "Item: Inspect"), "included-prefix"),
                ("missing-inclusion", _view_body().replace("| Alpha (`skill:#alpha`) | Activity: Inspect |\n", "").replace("| Beta (`skill:#beta`) | Task: Record |\n", ""), "included-empty"),
            )
            for label, body, expected in cases:
                with self.subTest(case=label):
                    result = helper._check(root, f"view-{label}.md", _asset(label, "process-view", "en", body))
                    self.assertIn(expected, _codes(result))

            reused = _view_body().replace(
                "| Beta (`skill:#beta`) | Task: Record |",
                "| Alpha (`skill:#alpha`) | Task: Record |\n| Beta (`skill:#beta`) | Task: Record |",
            )
            reused_result = helper._check(root, "view-reused-source.md", _asset("view", "process-view", "en", reused))
            self.assert_no_errors(reused_result)

            japanese = _write(root, "view-ja.md", _asset("view", "process-view", "ja", _view_body("ja")))
            english = _write(root, "view-en.md", _asset("view", "process-view", "en", _view_body()))
            errors, warnings = _check_pair(
                english,
                japanese,
                roots=helper._roots(root),
            )
            self.assertEqual(errors, [])
            self.assertTrue(all("warning unverified-locale-identity" in item for item in warnings), warnings)

            locale_cases = (
                ("source-order", _view_body("ja").replace("| アルファ | `skill:#alpha` |\n| ベータ | `skill:#beta` |", "| ベータ | `skill:#beta` |\n| アルファ | `skill:#alpha` |"), "view-source-reference-mismatch"),
                ("included-kind", _view_body("ja").replace("タスク: 記録", "活動: 記録"), "view-included-kind-mismatch"),
                ("included-source-reference", _view_body("ja"), "view-included-source-reference-mismatch"),
            )
            for label, body, expected in locale_cases:
                with self.subTest(locale_case=label):
                    if label == "included-source-reference":
                        _write(root, "skills/gamma/SKILL.md", _asset("gamma", "process", "en", _process_body(title="Beta"), metadata=False))
                        _write(
                            root,
                            "skills/gamma/references/locales/ja/SKILL.md",
                            _asset(
                                "gamma",
                                "process",
                                "ja",
                                _process_body("ja", title="ベータ"),
                                metadata=False,
                            ),
                        )
                        body = body.replace("| ベータ | `skill:#beta` |", "| ベータ | `skill:#gamma` |")
                        body = body.replace("ベータ (`skill:#beta`)", "ベータ (`skill:#gamma`)")
                    changed = _write(root, f"view-{label}-ja.md", _asset("view", "process-view", "ja", body))
                    pair_errors, _ = _check_pair(
                        english,
                        changed,
                        roots=helper._roots(root),
                    )
                    self.assertTrue(any(expected in item for item in pair_errors), pair_errors)

    def test_resolved_identity_duplicates_and_locale_context(self) -> None:
        helper = AlpsMarkdownProfileMilestoneBTests
        package = "example/alps"

        with _temp_root() as root:
            helper._write_targets(root)

            duplicate_model_body = _model_body().replace(
                "| Beta | |",
                f"| Beta | `skill:{package}#alpha` |",
            )
            duplicate_model = helper._check(
                root,
                "resolved-duplicate-model.md",
                _asset("resolved-duplicate-model", "process-model", "en", duplicate_model_body),
                qualified=True,
                package_id=package,
            )
            self.assertIn("process-duplicate", _codes(duplicate_model))

            duplicate_reference_body = helper._reference_body().replace(
                "Skill: `skill:#beta`",
                f"Skill: `skill:{package}#alpha`",
            )
            duplicate_reference = helper._check(
                root,
                "resolved-duplicate-reference.md",
                _asset("resolved-duplicate-reference", "process-reference-model", "en", duplicate_reference_body),
                qualified=True,
                package_id=package,
            )
            self.assertIn("process-duplicate", _codes(duplicate_reference))

            mixed_inclusion_body = _view_body().replace(
                "Alpha (`skill:#alpha`)",
                f"Alpha (`skill:{package}#alpha`)",
            )
            mixed_inclusion = helper._check(
                root,
                "resolved-inclusion.md",
                _asset("resolved-inclusion", "process-view", "en", mixed_inclusion_body),
                qualified=True,
                package_id=package,
            )
            self.assert_no_errors(mixed_inclusion)
            self.assertEqual(mixed_inclusion.ir.source_processes[0].reference.token, "`skill:#alpha`")
            self.assertEqual(
                mixed_inclusion.ir.included_activities_tasks[0].source_reference.token,
                f"`skill:{package}#alpha`",
            )

            duplicate_view_body = _view_body().replace(
                "| Beta | `skill:#beta` |",
                f"| Beta | `skill:{package}#alpha` |",
            ).replace(
                "| Beta (`skill:#beta`) |",
                f"| Beta (`skill:{package}#alpha`) |",
            )
            duplicate_view = helper._check(
                root,
                "resolved-duplicate-view.md",
                _asset("resolved-duplicate-view", "process-view", "en", duplicate_view_body),
                qualified=True,
                package_id=package,
            )
            self.assertIn("source-duplicate", _codes(duplicate_view))

        with _temp_root() as root:
            _write(
                root,
                "skills/beta/SKILL.md",
                _asset("beta", "process", "en", _process_body(title="Beta"), metadata=False),
            )
            unresolved = helper._check(root, "unresolved-inclusion.md", _asset("unresolved-inclusion", "process-view", "en", _view_body()))
            self.assertIn("target-not-found", _codes(unresolved))

        with _temp_root() as root:
            helper._write_targets(root)
            roots = helper._roots(root)
            process_en = _asset(
                "identity-process",
                "process",
                "en",
                _process_body(outcome_lines=("The result `skill:#alpha` is ready.",)),
            )
            process_ja = _asset(
                "identity-process",
                "process",
                "ja",
                _process_body("ja", outcome_lines=(f"成果 `skill:{package}#alpha` が整う。",)),
            )
            process_errors, process_warnings = _check_pair(
                _write(root, "identity-process-en.md", process_en),
                _write(root, "identity-process-ja.md", process_ja),
                package_identity=f"{package}@{helper.PACKAGE_VERSION}",
                roots=roots,
            )
            self.assertEqual(process_errors, [])
            self.assertEqual(process_warnings, [])

            model_en_body = _model_body().replace("| Beta | |", "| Beta | `skill:#beta` |")
            model_ja_body = _model_body("ja").replace("| ベータ | |", "| ベータ | `skill:#beta` |")
            model_ja_body = model_ja_body.replace("skill:#", f"skill:{package}#")
            model_errors, model_warnings = _check_pair(
                _write(root, "identity-model-en.md", _asset("identity-model", "process-model", "en", model_en_body)),
                _write(root, "identity-model-ja.md", _asset("identity-model", "process-model", "ja", model_ja_body)),
                package_identity=f"{package}@{helper.PACKAGE_VERSION}",
                roots=roots,
            )
            self.assertEqual(model_errors, [])
            self.assertEqual(model_warnings, [])

            view_en_body = _view_body().replace(
                "- The view outcome is ready.",
                "- The view outcome `skill:#alpha` is ready.",
            )
            view_ja_body = _view_body("ja").replace(
                "- ビューの成果が整う。",
                f"- ビューの成果 `skill:{package}#alpha` が整う。",
            ).replace("skill:#", f"skill:{package}#")
            view_errors, view_warnings = _check_pair(
                _write(root, "identity-view-en.md", _asset("identity-view", "process-view", "en", view_en_body)),
                _write(root, "identity-view-ja.md", _asset("identity-view", "process-view", "ja", view_ja_body)),
                package_identity=f"{package}@{helper.PACKAGE_VERSION}",
                roots=roots,
            )
            self.assertEqual(view_errors, [])
            self.assertEqual(view_warnings, [])

            reference_en_body = helper._reference_body().replace(
                "- The result is ready.",
                "- The result `skill:#alpha` is ready.",
            )
            reference_ja_body = helper._reference_body("ja").replace(
                "- 成果が準備される。",
                f"- 成果 `skill:{package}#alpha` が整う。",
            ).replace("skill:#", f"skill:{package}#")
            _write(
                root,
                "skills/alpha/SKILL.md",
                _asset(
                    "alpha",
                    "process",
                    "en",
                    _process_body(
                        outcome_lines=("The result `skill:#alpha` is ready.",),
                        title="Alpha",
                    ),
                    metadata=False,
                ),
            )
            _write(
                root,
                "skills/alpha/references/locales/ja/SKILL.md",
                _asset(
                    "alpha",
                    "process",
                    "ja",
                    _process_body(
                        "ja",
                        outcome_lines=(f"成果 `skill:{package}#alpha` が整う。",),
                        title="アルファ",
                    ),
                    metadata=False,
                ),
            )
            _write(
                root,
                "skills/beta/SKILL.md",
                _asset(
                    "beta",
                    "process",
                    "en",
                    _process_body(
                        outcome_lines=("The result `skill:#alpha` is ready.",),
                        title="Beta",
                    ),
                    metadata=False,
                ),
            )
            _write(
                root,
                "skills/beta/references/locales/ja/SKILL.md",
                _asset(
                    "beta",
                    "process",
                    "ja",
                    _process_body(
                        "ja",
                        outcome_lines=(f"成果 `skill:{package}#alpha` が整う。",),
                        title="ベータ",
                    ),
                    metadata=False,
                ),
            )
            reference_errors, reference_warnings = _check_pair(
                _write(root, "identity-reference-en.md", _asset("identity-reference", "process-reference-model", "en", reference_en_body)),
                _write(root, "identity-reference-ja.md", _asset("identity-reference", "process-reference-model", "ja", reference_ja_body)),
                package_identity=f"{package}@{helper.PACKAGE_VERSION}",
                roots=roots,
            )
            self.assertEqual(reference_errors, [])
            self.assertEqual(reference_warnings, [])

            different_package_ja = _process_body(
                "ja",
                outcome_lines=("成果 `skill:other/pkg#alpha` が整う。",),
            )
            other_root = root / "other-package"
            helper._write_targets(other_root)
            cross_package_roots = {
                f"{package}@{helper.PACKAGE_VERSION}": root,
                "other/pkg@9.0": other_root,
            }
            different_errors, _ = _check_pair(
                _write(root, "different-package-en.md", process_en),
                _write(root, "different-package-ja.md", _asset("identity-process", "process", "ja", different_package_ja)),
                package_identity=f"{package}@{helper.PACKAGE_VERSION}",
                roots=cross_package_roots,
            )
            self.assertTrue(any("process-outcome-reference-mismatch" in item for item in different_errors))

    def test_cli_passes_configured_package_identity_to_locale_comparison(self) -> None:
        helper = AlpsMarkdownProfileMilestoneBTests
        package = "example/alps"
        with _temp_root() as root:
            helper._write_targets(root, japanese=False)
            model_en_body = _model_body().replace("| Beta | |", "| Beta | `skill:#beta` |")
            model_ja_body = _model_body("ja").replace("| ベータ | |", "| ベータ | `skill:#beta` |")
            model_ja_body = model_ja_body.replace("skill:#", f"skill:{package}#")
            model_en = _write(
                root,
                "skills/model/SKILL.md",
                _asset("cli-model", "process-model", "en", model_en_body),
            )
            model_ja = _write(
                root,
                "skills/model/references/locales/ja/SKILL.md",
                _asset("cli-model", "process-model", "ja", model_ja_body),
            )
            previous = Path.cwd()
            output, errors = io.StringIO(), io.StringIO()
            try:
                with redirect_stdout(output), redirect_stderr(errors):
                    status = CHECKER.main([
                        "--package-binding",
                        f"{package}@{helper.PACKAGE_VERSION}={root}",
                        "--package-id",
                        package,
                        "--package-version",
                        helper.PACKAGE_VERSION,
                        str(model_en),
                    ])
            finally:
                os.chdir(previous)
            self.assertTrue(model_ja.is_file())
            self.assertEqual(status, 0, errors.getvalue())
            self.assertIn("PROFILE_VERSION=alps-markdown/v2", output.getvalue())

    def test_exact_version_is_part_of_resolved_identity(self) -> None:
        helper = AlpsMarkdownProfileMilestoneBTests
        package = helper.PACKAGE_ID
        with _temp_root() as root:
            helper._write_targets(root, japanese=False)
            first = resolve_reference(
                f"skill:{package}#alpha",
                package_roots([f"{package}@1.2.3={root}"]),
            )
            second = resolve_reference(
                f"skill:{package}#alpha",
                package_roots([f"{package}@1.2.4={root}"]),
            )
            self.assertIsNotNone(first.resolved)
            self.assertIsNotNone(second.resolved)
            self.assertEqual(str(first.resolved.identity), f"{package}@1.2.3#alpha")
            self.assertEqual(str(second.resolved.identity), f"{package}@1.2.4#alpha")
            self.assertNotEqual(first.resolved.identity, second.resolved.identity)

            duplicate = package_roots([
                f"{package}@1.2.3={root}",
                f"{package}@1.2.4={root}",
            ])
            self.assertTrue(any(item.code == "duplicate-package-id" for item in duplicate.diagnostics))

    def test_exact_version_grammar_accepts_slash_and_colon_and_rejects_unsafe_values(self) -> None:
        helper = AlpsMarkdownProfileMilestoneBTests
        package = helper.PACKAGE_ID
        with _temp_root() as root:
            helper._write_targets(root, japanese=False)
            for version in ("release/2026:08", "候補版:2026/08"):
                with self.subTest(valid=version):
                    config = package_roots([f"{package}@{version}={root}"])
                    self.assertEqual(config.diagnostics, ())
                    result = resolve_reference(f"skill:{package}#alpha", config)
                    self.assertIsNotNone(result.resolved)
                    self.assertEqual(result.resolved.identity.exact_version, version)

            for version in (
                "",
                "has space",
                "bad@value",
                "bad=value",
                "bad\x7fvalue",
                "bad\u202evalue",
                "bad\u2066value",
            ):
                with self.subTest(invalid=repr(version)):
                    config = package_roots({f"{package}@{version}": root})
                    self.assertTrue(config.diagnostics)
                    self.assertNotIn(package, config.roots)

    def test_short_reference_requires_declared_scope_and_ignores_nested_root_inference(self) -> None:
        helper = AlpsMarkdownProfileMilestoneBTests
        with _temp_root() as root:
            outer_package = "example/outer"
            inner_package = "example/inner"
            nested = root / "nested"
            _write(
                root,
                "skills/alpha/SKILL.md",
                _asset("alpha", "process", "en", _process_body(title="Outer Alpha"), metadata=False),
            )
            _write(
                nested,
                "skills/alpha/SKILL.md",
                _asset("alpha", "process", "en", _process_body(title="Inner Alpha"), metadata=False),
            )
            referring = _write(nested, "skills/model/SKILL.md", _asset("model", "process-model", "en", _model_body()))
            config = package_roots(
                [
                    f"{outer_package}@1.0={root}",
                    f"{inner_package}@2.0={nested}",
                ]
            )

            missing = resolve_reference("skill:#alpha", config, containing_path=referring)
            self.assertIsNone(missing.resolved)
            self.assertIn("missing-declared-package-scope", _codes(missing))

            outer = resolve_reference(
                "skill:#alpha",
                config,
                containing_path=referring,
                current_package_id=outer_package,
            )
            self.assertIsNotNone(outer.resolved)
            self.assertEqual(str(outer.resolved.identity), f"{outer_package}@1.0#alpha")
            self.assertEqual(outer.resolved.target, root / "skills/alpha/SKILL.md")

            inner = resolve_reference(
                "skill:#alpha",
                config,
                containing_path=referring,
                current_package_id=inner_package,
            )
            self.assertIsNotNone(inner.resolved)
            self.assertEqual(str(inner.resolved.identity), f"{inner_package}@2.0#alpha")

    def test_locale_comparison_requires_identity_context_and_required_dependency_locale(self) -> None:
        helper = AlpsMarkdownProfileMilestoneBTests
        with _temp_root() as root:
            english = _write(
                root,
                "pair-en.md",
                _asset(
                    "pair",
                    "process",
                    "en",
                    _process_body(outcome_lines=("The result `skill:#alpha` is ready.",)),
                ),
            )
            japanese = _write(
                root,
                "pair-ja.md",
                _asset(
                    "pair",
                    "process",
                    "ja",
                    _process_body("ja", outcome_lines=("成果 `skill:#beta` が整う。",)),
                ),
            )
            errors, _ = _RAW_CHECK_PAIR(english, japanese)
            self.assertTrue(
                any("unresolved-locale-reference-identity" in item for item in errors),
                errors,
            )

            matching_japanese = _write(
                root,
                "pair-matching-ja.md",
                _asset(
                    "pair",
                    "process",
                    "ja",
                    _process_body("ja", outcome_lines=("成果 `skill:#alpha` が整う。",)),
                ),
            )
            separated_errors, _ = _RAW_CHECK_PAIR(
                english,
                matching_japanese,
                package_identity="example/alps",
                package_versions={"example/alps": "1.2.3"},
            )
            self.assertTrue(
                any("unresolved-locale-reference-identity" in item for item in separated_errors),
                separated_errors,
            )

            helper._write_targets(root)
            resolved_errors, resolved_warnings = _RAW_CHECK_PAIR(
                english,
                matching_japanese,
                package_identity="example/alps",
                package_versions={"example/alps": "1.2.3"},
                roots=helper._roots(root),
                package_id=helper.PACKAGE_ID,
            )
            self.assertEqual((resolved_errors, resolved_warnings), ([], []))

        with _temp_root() as root:
            helper._write_targets(root, japanese=False)
            model = _write(
                root,
                "skills/model/SKILL.md",
                _asset("model", "process-model", "en", _model_body()),
            )
            _write(
                root,
                "skills/model/references/locales/ja/SKILL.md",
                _asset("model", "process-model", "ja", _model_body("ja")),
            )
            checked = CHECKER.check_document(
                model,
                helper._roots(root),
                helper.PACKAGE_ID,
                require_locale_counterpart=True,
            )
            self.assertIn("missing-japanese-reference-counterpart", _codes(checked))

    def test_locale_dependency_completeness_is_explicit_and_transitive(self) -> None:
        helper = AlpsMarkdownProfileMilestoneBTests
        package = helper.PACKAGE_ID
        with _temp_root() as root:
            _write(
                root,
                "skills/alpha/SKILL.md",
                _asset("alpha", "process", "en", _process_body(title="Alpha"), metadata=False),
            )
            english = _write(
                root,
                "pair-en.md",
                _asset(
                    "pair",
                    "process",
                    "en",
                    _process_body(outcome_lines=("The result `skill:#alpha` is ready.",)),
                ),
            )
            japanese = _write(
                root,
                "pair-ja.md",
                _asset(
                    "pair",
                    "process",
                    "ja",
                    _process_body("ja", outcome_lines=("成果 `skill:#alpha` が整う。",)),
                ),
            )
            default_errors, default_warnings = _RAW_CHECK_PAIR(
                english,
                japanese,
                package_identity=f"{package}@{helper.PACKAGE_VERSION}",
                roots=helper._roots(root),
                package_id=package,
            )
            self.assertEqual((default_errors, default_warnings), ([], []))

            required_errors, _ = _RAW_CHECK_PAIR(
                english,
                japanese,
                package_identity=f"{package}@{helper.PACKAGE_VERSION}",
                roots=helper._roots(root),
                package_id=package,
                require_locale_counterpart=True,
            )
            self.assertTrue(
                any("missing-japanese-reference-counterpart" in item for item in required_errors),
                required_errors,
            )

        with _temp_root() as root:
            beta_outcome_en = "The result is ready."
            beta_outcome_ja = "成果が準備される。"
            alpha_outcome_en = "The result `skill:#beta` is ready."
            alpha_outcome_ja = "成果 `skill:#beta` が整う。"
            _write(
                root,
                "skills/alpha/SKILL.md",
                _asset(
                    "alpha",
                    "process",
                    "en",
                    _process_body(outcome_lines=(alpha_outcome_en,), title="Alpha"),
                    metadata=False,
                ),
            )
            _write(
                root,
                "skills/alpha/references/locales/ja/SKILL.md",
                _asset(
                    "alpha",
                    "process",
                    "ja",
                    _process_body("ja", outcome_lines=(alpha_outcome_ja,), title="アルファ"),
                    metadata=False,
                ),
            )
            _write(
                root,
                "skills/beta/SKILL.md",
                _asset(
                    "beta",
                    "process",
                    "en",
                    _process_body(outcome_lines=(beta_outcome_en,), title="Beta"),
                    metadata=False,
                ),
            )
            top = _write(
                root,
                "skills/model/SKILL.md",
                _asset(
                    "model",
                    "process",
                    "en",
                    _process_body(
                        outcome_lines=("The result `skill:#alpha` is ready.",),
                        title="Model",
                    ),
                ),
            )
            _write(
                root,
                "skills/model/references/locales/ja/SKILL.md",
                _asset(
                    "model",
                    "process",
                    "ja",
                    _process_body(
                        "ja",
                        outcome_lines=("成果 `skill:#alpha` が整う。",),
                        title="モデル",
                    ),
                ),
            )
            transitive = CHECKER.check_document(
                top,
                helper._roots(root),
                package,
                require_locale_counterpart=True,
            )
            self.assertIn("missing-japanese-reference-counterpart", _codes(transitive))

            _write(
                root,
                "skills/beta/references/locales/ja/SKILL.md",
                _asset(
                    "beta",
                    "process",
                    "ja",
                    _process_body("ja", outcome_lines=(beta_outcome_ja,), title="ベータ"),
                    metadata=False,
                ).replace("name: beta", "name beta", 1),
            )
            malformed = CHECKER.check_document(
                top,
                helper._roots(root),
                package,
                require_locale_counterpart=True,
            )
            self.assertNotEqual(malformed.exit_status, 0)
            self.assertTrue(
                any(item.path.endswith("skills/beta/references/locales/ja/SKILL.md") for item in malformed.diagnostics),
                malformed.diagnostics,
            )

    def test_document_locale_completeness_includes_the_selected_root(self) -> None:
        helper = AlpsMarkdownProfileMilestoneBTests
        with _temp_root() as root:
            english = _write(
                root,
                "skills/lonely/SKILL.md",
                _asset("lonely", "process", "en", _process_body(title="Lonely")),
            )
            missing = CHECKER.check_document(
                english,
                helper._roots(root),
                helper.PACKAGE_ID,
                require_locale_counterpart=True,
            )
            self.assertIn("missing-japanese-counterpart", _codes(missing))

            japanese = _write(
                root,
                "skills/lonely/references/locales/ja/SKILL.md",
                _asset(
                    "lonely",
                    "process",
                    "ja",
                    _process_body("ja", title="単独"),
                ).replace("name: lonely", "name lonely", 1),
            )
            malformed = CHECKER.check_document(
                english,
                helper._roots(root),
                helper.PACKAGE_ID,
                require_locale_counterpart=True,
            )
            self.assertNotEqual(malformed.exit_status, 0)
            self.assertTrue(
                any(item.path == os.fspath(japanese) for item in malformed.diagnostics),
                malformed.diagnostics,
            )

            japanese.write_text(
                _asset("lonely", "process", "ja", _process_body("ja", title="単独")),
                encoding="utf-8",
            )
            complete = CHECKER.check_document(
                english,
                helper._roots(root),
                helper.PACKAGE_ID,
                require_locale_counterpart=True,
            )
            self.assert_no_errors(complete)

    def test_locale_detection_ignores_ambient_japanese_path_prefix(self) -> None:
        helper = AlpsMarkdownProfileMilestoneBTests
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "references/locales/ja/package"
            root.mkdir(parents=True)
            english = _write(
                root,
                "skills/ordinary/SKILL.md",
                _asset("ordinary", "process", "en", _process_body(title="Ordinary")),
            )
            self.assertEqual(locale_for(english), "en")
            checked = CHECKER.check_document(
                english,
                helper._roots(root),
                helper.PACKAGE_ID,
            )
            self.assert_no_errors(checked)

    def test_selected_root_locale_counterpart_cannot_escape_package_root(self) -> None:
        helper = AlpsMarkdownProfileMilestoneBTests
        with _temp_root() as root, _temp_root() as outside:
            english = _write(
                root,
                "skills/root/SKILL.md",
                _asset("root", "process", "en", _process_body(title="Root")),
            )
            external_japanese = _write(
                outside,
                "SKILL.md",
                _asset("root", "process", "ja", _process_body("ja", title="ルート")),
            )
            japanese = root / "skills/root/references/locales/ja/SKILL.md"
            japanese.parent.mkdir(parents=True, exist_ok=True)
            try:
                japanese.symlink_to(external_japanese)
            except OSError as error:
                self.skipTest(f"symlinks unsupported: {error}")

            checked = CHECKER.check_document(
                english,
                helper._roots(root),
                helper.PACKAGE_ID,
                require_locale_counterpart=True,
            )
            self.assertIn("source-outside-package-root", _codes(checked))

    def test_locale_dependency_walk_handles_deep_cycles_without_recursion(self) -> None:
        helper = AlpsMarkdownProfileMilestoneBTests
        depth = 1020
        with _temp_root() as root:
            for index in range(depth):
                name = f"s{index:04d}"
                next_name = f"s{index + 1:04d}" if index + 1 < depth else "s0000"
                _write(
                    root,
                    f"skills/{name}/SKILL.md",
                    _asset(
                        name,
                        "process",
                        "en",
                        _process_body(
                            outcome_lines=(f"The result `skill:#{next_name}` is ready.",),
                            title=name,
                        ),
                        metadata=False,
                    ),
                )
                _write(
                    root,
                    f"skills/{name}/references/locales/ja/SKILL.md",
                    _asset(
                        name,
                        "process",
                        "ja",
                        _process_body(
                            "ja",
                            outcome_lines=(f"成果 `skill:#{next_name}` が整う。",),
                            title=name,
                        ),
                        metadata=False,
                    ),
                )

            checked = CHECKER.check_document(
                root / "skills/s0000/SKILL.md",
                helper._roots(root),
                helper.PACKAGE_ID,
                require_locale_counterpart=True,
            )
            self.assert_no_errors(checked)
            self.assertFalse(
                any(item.code in {"parse-failed", "locale-dependency-validation-failed"} for item in checked.diagnostics),
                checked.diagnostics,
            )

    def test_pair_rejects_conflicting_containing_package_declarations(self) -> None:
        helper = AlpsMarkdownProfileMilestoneBTests
        with _temp_root() as root:
            helper._write_targets(root)
            english = _write(root, "pair-en.md", _asset("pair", "process", "en", _process_body()))
            japanese = _write(root, "pair-ja.md", _asset("pair", "process", "ja", _process_body("ja")))
            errors, _ = _RAW_CHECK_PAIR(
                english,
                japanese,
                package_identity=f"{helper.PACKAGE_ID}@{helper.PACKAGE_VERSION}",
                roots=helper._roots(root),
                package_id="other/package",
            )
            self.assertTrue(any("conflicting-package-identity" in item for item in errors), errors)

        with _temp_root() as root:
            helper._write_targets(root, japanese=False)
            process = _write(
                root,
                "skills/process/SKILL.md",
                _asset(
                    "process",
                    "process",
                    "en",
                    _process_body(outcome_lines=("The result `skill:#alpha` is ready.",)),
                ),
            )
            _write(
                root,
                "skills/process/references/locales/ja/SKILL.md",
                _asset(
                    "process",
                    "process",
                    "ja",
                    _process_body(
                        "ja",
                        outcome_lines=("成果 `skill:#alpha` が整う。",),
                    ),
                ),
            )
            checked = CHECKER.check_document(
                process,
                helper._roots(root),
                helper.PACKAGE_ID,
                require_locale_counterpart=True,
            )
            self.assertIn("missing-japanese-reference-counterpart", _codes(checked))

    def test_cli_rejects_declared_scope_that_does_not_contain_asset(self) -> None:
        helper = AlpsMarkdownProfileMilestoneBTests
        with _temp_root() as root, _temp_root() as outside:
            helper._write_targets(root, japanese=False)
            model = _write(
                outside,
                "model.md",
                _asset("model", "process-model", "en", _model_body()),
            )
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = CHECKER.main(
                    [
                        "--package-binding",
                        f"{helper.PACKAGE_ID}@{helper.PACKAGE_VERSION}={root}",
                        "--package-id",
                        helper.PACKAGE_ID,
                        "--package-version",
                        helper.PACKAGE_VERSION,
                        "--no-locale-pairs",
                        str(model),
                    ]
                )
            self.assertEqual(status, 2)
            self.assertIn("source-outside-package-root", stderr.getvalue())

    def test_canonical_reference_resolution_and_package_containment(self) -> None:
        helper = AlpsMarkdownProfileMilestoneBTests
        with _temp_root() as root:
            helper._write_targets(root)
            local = helper._check(root, "local-model.md", _asset("model", "process-model", "en", _model_body()))
            self.assert_no_errors(local)
            qualified = helper._check(
                root, "qualified-model.md", _asset("model", "process-model", "en", helper._qualified(_model_body())),
                qualified=True, package_id="example/alps",
            )
            self.assert_no_errors(qualified)

            malformed = (
                ("empty-skill", "skill:#"),
                ("empty-package-segment", "skill:mashimashica//alps#alpha"),
                ("dot-segment", "skill:mashimashica/./alps#alpha"),
                ("dot-dot-segment", "skill:mashimashica/../alps#alpha"),
                ("backslash", r"skill:mashimashica\alps#alpha"),
                ("uppercase-segment", "skill:Mashimashica/alps#alpha"),
            )
            for label, token in malformed:
                with self.subTest(reference=label):
                    body = _model_body().replace("`skill:#alpha`", f"`{token}`")
                    result = helper._check(root, f"reference-{label}.md", _asset(label, "process-model", "en", body))
                    self.assertIn("malformed-reference", _codes(result))

        with _temp_root() as root:
            _write(root, "skills/beta/SKILL.md", _asset("beta", "process", "en", _process_body(title="Beta"), metadata=False))
            missing = helper._check(root, "missing-target.md", _asset("model", "process-model", "en", _model_body()))
            self.assertIn("target-not-found", _codes(missing))

        with _temp_root() as root:
            _write(root, "skills/beta/SKILL.md", _asset("beta", "process", "en", _process_body(title="Beta"), metadata=False))
            target_directory = root / "skills" / "alpha" / "SKILL.md"
            target_directory.mkdir(parents=True)
            nonregular = helper._check(root, "nonregular-target.md", _asset("model", "process-model", "en", _model_body()))
            self.assertIn("target-not-regular-file", _codes(nonregular))

        with _temp_root() as root:
            outside = root.parent / "outside-package"
            _write(outside, "model.md", _asset("model", "process-model", "en", _model_body()))
            outside_result = CHECKER.check_document(
                outside / "model.md",
                {"example/alps@1.2.3": root},
                "example/alps",
            )
            self.assertIn("source-outside-package-root", _codes(outside_result))

        with _temp_root() as root:
            if not hasattr(os, "symlink"):
                self.skipTest("symlink support is unavailable")
            inside = root / "linked-alpha"
            _write(inside, "SKILL.md", _asset("alpha", "process", "en", _process_body(title="Alpha"), metadata=False))
            link = root / "skills" / "alpha"
            link.parent.mkdir(parents=True, exist_ok=True)
            try:
                link.symlink_to(inside, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"symlinks unsupported: {error}")
            _write(root, "skills/beta/SKILL.md", _asset("beta", "process", "en", _process_body(title="Beta"), metadata=False))
            accepted = helper._check(root, "in-root-symlink.md", _asset("model", "process-model", "en", _model_body()))
            self.assert_no_errors(accepted)

        with _temp_root() as root:
            if not hasattr(os, "symlink"):
                self.skipTest("symlink support is unavailable")
            outside = root.parent / "outside-target"
            _write(outside, "SKILL.md", _asset("alpha", "process", "en", _process_body(title="Alpha"), metadata=False))
            link = root / "skills" / "alpha"
            link.parent.mkdir(parents=True, exist_ok=True)
            try:
                link.symlink_to(outside, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"symlinks unsupported: {error}")
            _write(root, "skills/beta/SKILL.md", _asset("beta", "process", "en", _process_body(title="Beta"), metadata=False))
            escaped = helper._check(root, "symlink-target.md", _asset("model", "process-model", "en", _model_body()))
            self.assertIn("target-escapes-package-root", _codes(escaped))

        with _temp_root() as root, _temp_root() as outside:
            if not hasattr(os, "symlink"):
                self.skipTest("symlink support is unavailable")
            helper._write_targets(root, japanese=False)
            source = outside / "source.md"
            source.write_text(_asset("source", "process", "en", _process_body()), encoding="utf-8")
            link = root / "source.md"
            try:
                link.symlink_to(source)
            except OSError as error:
                self.skipTest(f"symlinks unsupported: {error}")
            escaped_source = CHECKER.check_document(
                link,
                helper._roots(root),
                helper.PACKAGE_ID,
            )
            self.assertIn("source-outside-package-root", _codes(escaped_source))

        with _temp_root() as root, _temp_root() as outside:
            if not hasattr(os, "symlink"):
                self.skipTest("symlink support is unavailable")
            helper._write_targets(root, japanese=False)
            outside_ja = _write(
                outside,
                "SKILL.md",
                _asset("alpha", "process", "ja", _process_body("ja", title="アルファ"), metadata=False),
            )
            localized = root / "skills/alpha/references/locales/ja/SKILL.md"
            localized.parent.mkdir(parents=True, exist_ok=True)
            try:
                localized.symlink_to(outside_ja)
            except OSError as error:
                self.skipTest(f"symlinks unsupported: {error}")
            model = _write(root, "skills/model/SKILL.md", _asset("model", "process-model", "en", _model_body()))
            _write(
                root,
                "skills/model/references/locales/ja/SKILL.md",
                _asset("model", "process-model", "ja", _model_body("ja")),
            )
            escaped_locale = CHECKER.check_document(
                model,
                helper._roots(root),
                helper.PACKAGE_ID,
                require_locale_counterpart=True,
            )
            self.assertIn("localized-target-escapes-package-root", _codes(escaped_locale))

        with _temp_root() as root:
            helper._write_targets(root, japanese=True, japanese_titles={"alpha": "アルファ", "beta": "ベータ"})
            japanese_path = _write(root, "skills/model/references/locales/ja/SKILL.md", _asset("model", "process-model", "ja", _model_body("ja")))
            localized = CHECKER.check_document(
                japanese_path,
                {"example/alps@1.2.3": root},
                "example/alps",
            )
            self.assert_no_errors(localized)

        with _temp_root() as root:
            helper._write_targets(root, japanese=False)
            fallback_body = _model_body("ja").replace("アルファ", "Alpha").replace("ベータ", "Beta")
            japanese_path = _write(root, "skills/model/references/locales/ja/SKILL.md", _asset("model", "process-model", "ja", fallback_body))
            fallback = CHECKER.check_document(
                japanese_path,
                {"example/alps@1.2.3": root},
                "example/alps",
            )
            self.assert_no_errors(fallback)

    def test_ir_only_validator_locale_guard_parse_once_and_serialized_contract(self) -> None:
        import inspect
        from unittest import mock
        import alps_markdown.checker as checker_module
        import alps_markdown.locale_compare as locale_compare
        import alps_markdown.validators as validators

        for function in (CHECKER.validate_ir, validators.validate_ir, locale_compare.compare_locale_ir):
            with self.subTest(function=function.__module__ + "." + function.__name__):
                names = set(inspect.signature(function).parameters)
                self.assertFalse(names & {"source", "source_text", "raw_text", "markdown", "text"}, names)

        for module in (validators, locale_compare):
            with self.subTest(module=module.__name__):
                source = inspect.getsource(module)
                self.assertNotIn("read_text", source)
                self.assertNotIn("read_bytes", source)
                self.assertNotIn("open(", source)
                self.assertNotIn("parse_markdown", source)
                self.assertNotIn("re.", source)
                self.assertNotIn("re.compile", source)

        with _temp_root() as root:
            path = _write(root, "process.md", _asset("process", "process", "en", _process_body()))
            with mock.patch.object(checker_module, "parse_asset", wraps=checker_module.parse_asset) as parse_mock:
                result = CHECKER.check_document(path, {"example/alps@1.2.3": root})
            self.assert_no_errors(result)
            self.assertEqual(parse_mock.call_count, 1)
            serialized = json.dumps(
                {"profile_version": CHECKER.PROFILE_VERSION, "result": asdict(result)},
                ensure_ascii=False,
                sort_keys=True,
            )
            self.assertIn(CHECKER.PROFILE_VERSION, serialized)
            self.assertIn('"ir":', serialized)
            self.assertIn('"kind": "process"', serialized)

    def test_cli_shares_parse_cache_across_top_level_and_referenced_assets(self) -> None:
        from unittest import mock
        import alps_markdown.checker as checker_module

        with _temp_root() as root:
            process = _write(
                root,
                "skills/process/SKILL.md",
                _asset("process", "process", "en", _process_body(title="Process"), metadata=False),
            )
            model_body = _clean(
                """
                # Process Model

                ## Purpose

                Organizes the Process.

                ## Processes

                | Process | Skill |
                | --- | --- |
                | Process | `skill:#process` |

                ## Relationships

                | Provider Process | Information | Recipient Process | Relationship |
                | --- | --- | --- | --- |
                | Process | Information | Process | Supports |
                """
            )
            model = _write(
                root,
                "skills/model/SKILL.md",
                _asset("model", "process-model", "en", model_body),
            )
            previous = Path.cwd()
            output, errors = io.StringIO(), io.StringIO()
            os.chdir(root)
            try:
                with mock.patch.object(
                    checker_module, "parse_asset", wraps=checker_module.parse_asset
                ) as parse_mock:
                    with redirect_stdout(output), redirect_stderr(errors):
                        status = CHECKER.main(
                            [
                                "--root",
                                str(root),
                                "--package-id",
                                "example/alps",
                                "--package-version",
                                "1.2.3",
                                "--no-locale-pairs",
                                str(process),
                                str(model),
                            ]
                        )
            finally:
                os.chdir(previous)

            self.assertEqual(status, 0, errors.getvalue())
            observed = []
            for call in parse_mock.call_args_list:
                path = call.args[0]
                requested_locale = call.args[1] if len(call.args) > 1 else None
                effective_locale = requested_locale or checker_module.locale_for(path)
                observed.append(
                    (
                        os.path.normcase(os.path.abspath(os.fspath(path))),
                        effective_locale,
                    )
                )
            expected = {
                (
                    os.path.normcase(os.path.abspath(os.fspath(process))),
                    "en",
                ),
                (
                    os.path.normcase(os.path.abspath(os.fspath(model))),
                    "en",
                ),
            }
            self.assertEqual(set(observed), expected)
            self.assertEqual(len(observed), len(set(observed)))
            self.assertEqual(parse_mock.call_count, len(expected))

    def test_locale_pair_frontmatter_process_model_reference_and_view_contracts(self) -> None:
        helper = AlpsMarkdownProfileMilestoneBTests
        en_outcomes = ("Outcome one `skill:#alpha`.", "Outcome two `skill:#beta`.")
        en_tasks = ("The agent must inspect `skill:#alpha`.", "The agent should review `skill:#beta`.")
        ja_outcomes = ("成果一 `skill:#alpha`。", "成果二 `skill:#beta`。")
        ja_tasks = ("エージェントは `skill:#alpha` を確認する必要がある。", "エージェントは `skill:#beta` を確認するのが望ましい。")

        def pair(en_body: str, ja_body: str, *, en_kind: str = "process", ja_kind: str = "process", ja_name: str = "fixture"):
            with _temp_root() as root:
                helper._write_targets(root)
                if "skill:#local-view" in en_body or "skill:#local-view" in ja_body:
                    _write(
                        root,
                        "skills/local-view/SKILL.md",
                        _asset(
                            "local-view",
                            "process",
                            "en",
                            _process_body(title="Local View"),
                            metadata=False,
                        ),
                    )
                    _write(
                        root,
                        "skills/local-view/references/locales/ja/SKILL.md",
                        _asset(
                            "local-view",
                            "process",
                            "ja",
                            _process_body("ja", title="ローカルビュー"),
                            metadata=False,
                        ),
                    )
                english = _write(root, "en.md", _asset("fixture", en_kind, "en", en_body))
                japanese = _write(root, "ja.md", _asset(ja_name, ja_kind, "ja", ja_body))
                return _check_pair(
                    english,
                    japanese,
                    roots=helper._roots(root),
                )

        errors, warnings = pair(
            _process_body("en", outcome_lines=en_outcomes, task_lines=en_tasks),
            _process_body("ja", outcome_lines=ja_outcomes, task_lines=ja_tasks),
        )
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

        process_cases = (
            ("frontmatter-name", _process_body("ja", outcome_lines=ja_outcomes, task_lines=ja_tasks), "fixture-jp", "frontmatter-name-mismatch"),
            ("outcome-count", _process_body("ja", outcome_lines=ja_outcomes[:1], task_lines=ja_tasks), "fixture", "process-outcome-count-mismatch"),
            ("outcome-reference-sequence", _process_body("ja", outcome_lines=("成果一 `skill:#beta`。", "成果二 `skill:#alpha`。"), task_lines=ja_tasks), "fixture", "process-outcome-reference-mismatch"),
            ("task-count", _process_body("ja", outcome_lines=ja_outcomes, task_lines=ja_tasks[:1]), "fixture", "process-task-count-mismatch"),
            ("normative-class", _process_body("ja", outcome_lines=ja_outcomes, task_lines=(ja_tasks[0], "エージェントは `skill:#beta` を確認する必要がある。")), "fixture", "process-task-normative-class-mismatch"),
            ("activity-count", _process_body("ja", outcome_lines=ja_outcomes, task_lines=ja_tasks, extra="\n### 追加\n\n1. エージェントは追加を確認する必要がある。\n"), "fixture", "process-activity-count-mismatch"),
        )
        for label, body, name, expected in process_cases:
            with self.subTest(process_case=label):
                errors, _ = pair(_process_body("en", outcome_lines=en_outcomes, task_lines=en_tasks), body, ja_name=name)
                self.assertTrue(any(expected in item for item in errors), errors)
                self.assertTrue(all("error locale-mismatch/" in item for item in errors), errors)

        model_en = _model_body().replace("| Beta | |", "| Beta | `skill:#beta` |")
        model_ja = _model_body("ja").replace("| ベータ | |", "| ベータ | `skill:#beta` |")
        errors, warnings = pair(model_en, model_ja, en_kind="process-model", ja_kind="process-model")
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        model_cases = (
            ("process-count", model_ja.replace("| ベータ | `skill:#beta` |\n", "").replace("| アルファ | 情報 | ベータ | 支援 |", "| アルファ | 情報 | アルファ | 支援 |"), "model-process-count-mismatch"),
            ("process-identity", model_ja.replace("| アルファ | `skill:#alpha` |\n| ベータ | `skill:#beta` |", "| ベータ | `skill:#beta` |\n| アルファ | `skill:#alpha` |"), "model-process-identity-mismatch"),
            ("relationship-provider", model_ja.replace("| アルファ | 情報 | ベータ |", "| ベータ | 情報 | アルファ |"), "model-relationship-provider-mismatch"),
        )
        for label, body, expected in model_cases:
            with self.subTest(model_case=label):
                errors, _ = pair(model_en, body, en_kind="process-model", ja_kind="process-model")
                self.assertTrue(any(expected in item for item in errors), errors)

        reference_en = helper._reference_body()
        reference_ja = helper._reference_body("ja")
        errors, _ = pair(reference_en, reference_ja, en_kind="process-reference-model", ja_kind="process-reference-model")
        self.assertEqual(errors, [])
        reversed_reference = helper._reference_body("ja", reversed_relationship=True)
        errors, _ = pair(reference_en, reversed_reference, en_kind="process-reference-model", ja_kind="process-reference-model")
        self.assertTrue(any("reference-relationship-provider-mismatch" in item for item in errors), errors)

        view_en = _view_body().replace("The view outcome is ready.", "The view outcome `skill:#alpha` is ready.")
        view_ja = _view_body("ja").replace("ビューの成果が整う。", "ビューの成果 `skill:#alpha` が整う。")
        errors, _ = pair(view_en, view_ja, en_kind="process-view", ja_kind="process-view")
        self.assertEqual(errors, [])
        changed_view_ja = view_ja.replace("`skill:#alpha`", "`skill:#beta`", 1)
        errors, _ = pair(view_en, changed_view_ja, en_kind="process-view", ja_kind="process-view")
        self.assertTrue(any("view-outcome-identity-mismatch" in item for item in errors), errors)

        local_view_en = _local_view_body("en")
        local_view_ja = _local_view_body("ja")
        errors, warnings = pair(
            local_view_en,
            local_view_ja,
            en_kind="process-view",
            ja_kind="process-view",
        )
        self.assertEqual((errors, warnings), ([], []))
        changed_local_view_ja = local_view_ja.replace("確認する必要がある", "確認するのが望ましい")
        errors, _ = pair(
            local_view_en,
            changed_local_view_ja,
            en_kind="process-view",
            ja_kind="process-view",
        )
        self.assertTrue(any("view-task-normative-class-mismatch" in item for item in errors), errors)

        empty_model_en = model_en.replace("| Alpha | `skill:#alpha` |", "| Alpha | |").replace("| Beta | `skill:#beta` |", "| Beta | |")
        empty_model_ja = model_ja.replace("| アルファ | `skill:#alpha` |", "| アルファ | |").replace("| ベータ | `skill:#beta` |", "| ベータ | |")
        errors, warnings = pair(empty_model_en, empty_model_ja, en_kind="process-model", ja_kind="process-model")
        self.assertEqual(errors, [])
        self.assertTrue(warnings)
        self.assertTrue(all("warning unverified-locale-identity/" in item for item in warnings), warnings)

    def test_cli_exit_statuses_version_warning_success_and_no_conformance_claim(self) -> None:
        from unittest import mock
        import alps_markdown.cli as cli_module

        def run(root: Path, argv: list[str]):
            previous = Path.cwd()
            output, errors = io.StringIO(), io.StringIO()
            os.chdir(root)
            try:
                with redirect_stdout(output), redirect_stderr(errors):
                    status = CHECKER.main(argv)
            finally:
                os.chdir(previous)
            return status, output.getvalue(), errors.getvalue()

        with _temp_root() as root:
            helper = AlpsMarkdownProfileMilestoneBTests
            helper._write_targets(root, japanese=True)
            model = _model_body().replace("| Alpha | `skill:#alpha` |", "| Alpha | |")
            model = model.replace("| Beta | |", "| Beta | |")
            _write(root, "skills/model/SKILL.md", _asset("model", "process-model", "en", model))
            model_ja = _model_body("ja").replace("| アルファ | `skill:#alpha` |", "| アルファ | |")
            _write(root, "skills/model/references/locales/ja/SKILL.md", _asset("model", "process-model", "ja", model_ja))
            status, output, errors = run(root, [])
            self.assertEqual(status, 0)
            self.assertIn(f"PROFILE_VERSION={CHECKER.PROFILE_VERSION}", output)
            self.assertIn("not an ALPS Conformance claim", output)
            self.assertIn("warning unverified-locale-identity", errors)

        with _temp_root() as root:
            unsupported = _write(root, "unsupported.md", _asset("unsupported", "process", "en", _process_body().replace("## Purpose", "## Unknown", 1)))
            semantic = _write(root, "semantic.md", _asset("semantic", "process-model", "en", _model_body().replace("| Alpha | Information | Beta | Supports |", "| Gamma | Information | Beta | Supports |")))
            pair_dir = root / "skills" / "pair"
            english = _write(pair_dir, "SKILL.md", _asset("pair", "process", "en", _process_body(outcome_lines=("One.", "Two."))))
            japanese = _write(pair_dir, "references/locales/ja/SKILL.md", _asset("pair", "process", "ja", _process_body("ja", outcome_lines=("一つ。",))))
            for label, path, expected in (
                ("unsupported", unsupported, "unsupported-profile-syntax"),
                ("semantic", semantic, "relationship-endpoint"),
                ("locale", english, "process-outcome-count-mismatch"),
            ):
                with self.subTest(document_status=label):
                    status, _, errors = run(root, [str(path)])
                    self.assertEqual(status, 1)
                    self.assertIn(expected, errors)

            valid = _write(root, "valid.md", _asset("valid", "process", "en", _process_body()))
            invalid_utf8 = root / "invalid-utf8.md"
            invalid_utf8.write_bytes(b"\xff")
            for label, argv, expected in (
                ("invalid-utf8", [str(invalid_utf8)], "host-input/invalid-utf8"),
                ("missing", [str(root / "does-not-exist.md")], "host-input/read-failed"),
                ("config", ["--package-root", "invalid-spec", str(valid)], "host-input/invalid-package-root-spec"),
                (
                    "version-conflict",
                    [
                        "--package-binding",
                        f"example/alps@1.2.3={root}",
                        "--package-id",
                        "example/alps",
                        "--package-version",
                        "1.2.4",
                        str(valid),
                    ],
                    "host-input/conflicting-package-version",
                ),
            ):
                with self.subTest(input_status=label):
                    status, _, errors = run(root, argv)
                    self.assertEqual(status, 2)
                    self.assertIn(expected, errors)

            with mock.patch.object(cli_module, "_run", side_effect=RuntimeError("boom")):
                status, _, errors = run(root, [])
            self.assertEqual(status, 2)
            self.assertIn("internal/cli-failed", errors)

        with _temp_root() as root:
            previous = Path.cwd()
            output, errors = io.StringIO(), io.StringIO()
            os.chdir(root)
            try:
                with self.assertRaises(SystemExit) as raised, redirect_stdout(output), redirect_stderr(errors):
                    CHECKER.main(["--version"])
            finally:
                os.chdir(previous)
            self.assertEqual(raised.exception.code, 0)
            self.assertIn(CHECKER.PROFILE_VERSION, output.getvalue())
            self.assertEqual(errors.getvalue(), "")

        with _temp_root() as root:
            _write(root, "skills/lonely/SKILL.md", _asset("lonely", "process", "en", _process_body()))
            status, _, errors = run(root, ["--require-japanese"])
            self.assertEqual(status, 1)
            self.assertIn("locale-mismatch/missing-japanese-counterpart", errors)

    def test_cli_resolves_relative_asset_paths_against_configured_root_from_other_cwd(self) -> None:
        with _temp_root() as root:
            asset = _write(
                root,
                "skills/relative/SKILL.md",
                _asset("relative", "process", "en", _process_body()),
            )
            outside = root / "outside"
            outside.mkdir()
            previous = Path.cwd()
            output, errors = io.StringIO(), io.StringIO()
            os.chdir(outside)
            try:
                with redirect_stdout(output), redirect_stderr(errors):
                    status = CHECKER.main(
                        ["--root", str(root), "--no-locale-pairs", "skills/relative/SKILL.md"]
                    )
            finally:
                os.chdir(previous)
            self.assertEqual(status, 0, errors.getvalue())
            self.assertIn(f"PROFILE_VERSION={CHECKER.PROFILE_VERSION}", output.getvalue())
            self.assertNotIn(str(outside / "skills"), errors.getvalue())
            self.assertTrue(asset.is_file())

    def test_cli_rejects_removed_legacy_ja_allow_term_option(self) -> None:
        with _temp_root() as root:
            previous = Path.cwd()
            errors = io.StringIO()
            os.chdir(root)
            try:
                with self.assertRaises(SystemExit) as raised, redirect_stderr(errors):
                    CHECKER.main(["--ja-allow-term", "用語"])
            finally:
                os.chdir(previous)
            self.assertEqual(raised.exception.code, 2)
            self.assertIn("unrecognized arguments: --ja-allow-term", errors.getvalue())

    def test_input_diagnostics_compose_and_invalid_utf8_keeps_host_status(self) -> None:
        with _temp_root() as root:
            valid = _asset("input-boundary", "process", "en", _process_body()).encode()
            standalone = (
                ("bom", b"\xef\xbb\xbf" + valid, "utf8-bom"),
                ("nul", valid.replace(b"Fixture Process", b"Fixture\x00Process", 1), "nul-byte"),
                ("bare-cr", valid.replace(b"\n", b"\r", 1), "bare-cr"),
            )
            for label, data, code in standalone:
                with self.subTest(standalone=label):
                    path = root / f"standalone-{label}.md"
                    path.write_bytes(data)
                    parsed = CHECKER.parse_asset(path)
                    self.assertIn(code, _codes(parsed))

            combined = b"\xef\xbb\xbf" + (b"x\x00\r\xff\n" * 20_001)
            path = root / "combined-input-boundaries.md"
            path.write_bytes(combined)
            parsed = CHECKER.parse_asset(path)
            self.assertIn("utf8-bom", _codes(parsed))
            self.assertIn("nul-byte", _codes(parsed))
            self.assertIn("bare-cr", _codes(parsed))
            self.assertIn("line-limit", _codes(parsed))
            self.assertIn("invalid-utf8", _codes(parsed))
            self.assertIn("host-input", _classes(parsed))

            previous = Path.cwd()
            errors = io.StringIO()
            os.chdir(root)
            try:
                with redirect_stderr(errors):
                    status = CHECKER.main([str(path)])
            finally:
                os.chdir(previous)
            self.assertEqual(status, 2)
            self.assertIn("host-input/invalid-utf8", errors.getvalue())

    def test_exact_and_plus_one_resource_limits_records_and_container_state_bound(self) -> None:
        from unittest import mock
        from alps_markdown import markdown_profile
        from alps_markdown.model import (
            MAX_ACTIVE_CONTAINER_STATES,
            MAX_FRONTMATTER_BYTES,
            MAX_INPUT_BYTES,
            MAX_INPUT_LINES,
            MAX_LINE_BYTES,
            MAX_RECORDS_PER_SECTION,
        )
        self.assertEqual(MAX_ACTIVE_CONTAINER_STATES, 1)

        def parse_bytes(root: Path, label: str, data: bytes):
            path = root / f"{label}.md"
            path.write_bytes(data)
            return CHECKER.parse_asset(path)

        with _temp_root() as root:
            base = _asset("bytes-limit", "process", "en", _process_body(extra="\n## Inputs\n\n")).encode()
            remaining = MAX_INPUT_BYTES - len(base)
            filler = bytearray()
            while remaining >= MAX_LINE_BYTES + 1:
                filler.extend(b"x" * MAX_LINE_BYTES + b"\n")
                remaining -= MAX_LINE_BYTES + 1
            if remaining == 1:
                filler.extend(b"\n")
            elif remaining > 1:
                filler.extend(b"x" * (remaining - 1) + b"\n")
            exact = base + bytes(filler)
            over = exact + b"x"
            self.assertEqual(len(exact), MAX_INPUT_BYTES)
            self.assertLess(exact.count(b"\n"), MAX_INPUT_LINES)
            exact_result = parse_bytes(root, "bytes-exact", exact)
            self.assert_no_errors(exact_result)
            self.assertIn("input-too-large", _codes(parse_bytes(root, "bytes-plus-one", over)))

        with _temp_root() as root:
            base_lines = _asset("lines-limit", "process", "en", _process_body(extra="\n## Inputs\n\n")).splitlines()
            exact = "\n".join(base_lines + ["x"] * (MAX_INPUT_LINES - len(base_lines))).encode()
            over = exact + b"\nx"
            self.assert_no_errors(parse_bytes(root, "lines-exact", exact))
            self.assertIn("line-limit", _codes(parse_bytes(root, "lines-plus-one", over)))

        with _temp_root() as root:
            base = _asset("line-bytes", "process", "en", _process_body(extra="\n## Inputs\n\n")).encode()
            exact = base + b"x" * MAX_LINE_BYTES
            over = base + b"x" * (MAX_LINE_BYTES + 1)
            self.assert_no_errors(parse_bytes(root, "line-bytes-exact", exact))
            self.assertIn("line-too-long", _codes(parse_bytes(root, "line-bytes-plus-one", over)))

        with _temp_root() as root:
            front = _frontmatter("frontmatter-limit", "process", "en").encode()
            close = b"---\n"
            prefix = front[:front.rfind(close)]

            # The exact v1 five-line mapping is deliberately surrounded by
            # rejected filler: field grammar is stricter than this independent
            # upper-byte guard, so validity is not the assertion for this case.
            def frontmatter_asset(limit: int) -> bytes:
                available = limit - len(prefix) - len(close)
                unit = b"x:" + b"a" * 997 + b"\n"
                filler = bytearray()
                while available > len(unit) + 2:
                    filler.extend(unit)
                    available -= len(unit)
                final_length = available
                filler += b"x:" + b"a" * (final_length - 3) + b"\n"
                return prefix + filler + close + _process_body(extra="\n## Inputs\n\n").encode()

            exact = frontmatter_asset(MAX_FRONTMATTER_BYTES)
            over = frontmatter_asset(MAX_FRONTMATTER_BYTES + 1)
            self.assertEqual(exact.find(close, len(prefix)) + len(close), MAX_FRONTMATTER_BYTES)
            exact_result = parse_bytes(root, "frontmatter-exact", exact)
            self.assertNotIn("frontmatter-too-large", _codes(exact_result))
            self.assertTrue(exact_result.diagnostics)
            self.assertIn("frontmatter-too-large", _codes(parse_bytes(root, "frontmatter-plus-one", over)))

        def process_with_records(count: int, *, tasks: bool = False) -> str:
            if tasks:
                return _asset("records", "process", "en", _process_body(task_lines=tuple(f"The agent must complete step {i}." for i in range(count))))
            return _asset("records", "process", "en", _process_body(outcome_lines=tuple(f"Outcome item {i} exists." for i in range(count))))

        def model_with_records(process_count: int, relationship_count: int) -> str:
            processes = "\n".join(f"| Process {i} | |" for i in range(process_count))
            relationships = "\n".join("| Process 0 | Information | Process 1 | Supports |" for _ in range(relationship_count))
            return _asset(
                "records-model", "process-model", "en", _clean(
                    f"""# Records Model

## Purpose

Bounded records.

## Processes

| Process | Skill |
| --- | --- |
{processes}

## Relationships

| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
{relationships}
"""
                ),
            )

        def view_with_records(source_count: int, included_count: int) -> str:
            sources = "\n".join(
                f"| Source {index} | `skill:#source-{index}` |"
                for index in range(source_count)
            )
            included = "\n".join(
                f"| Source 0 (`skill:#source-0`) | Activity: Inspect {index} |"
                for index in range(included_count)
            )
            return _asset("records-view", "process-view", "en", _clean(
                f"""# Records View

## Purpose

Bounded view records.

## Outcomes

- The view is ready.

## Source Processes

| Source Process | Reference |
| --- | --- |
{sources}

## Included Activities and Tasks

| Source Process | Source element |
| --- | --- |
{included}

## Application

Apply this view.
"""
            ))

        def reference_model_with_records(count: int) -> str:
            entries = "\n".join(
                f"""### Process {index}

#### Purpose

Defines process {index}.

#### Outcomes

- Process {index} is ready.
"""
                for index in range(count)
            )
            return _asset("records-reference", "process-reference-model", "en", _clean(
                f"""# Records Reference Model

## Purpose

Bounded reference entries.

## Processes

{entries}

## Relationships

| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| Process 0 | Information | Process 1 | Supports |
"""
            ))

        def aggregate_references(count: int) -> str:
            references = "\n".join(f"`skill:#reference-{index}`" for index in range(count))
            return _asset(
                "records-references",
                "process",
                "en",
                _process_body(extra=f"\n## Inputs\n\n{references}\n"),
            )

        with _temp_root() as root:
            record_cases = (
                ("outcomes", lambda n: process_with_records(n), "record-limit"),
                ("tasks", lambda n: process_with_records(n, tasks=True), "record-limit"),
                ("process-table", lambda n: model_with_records(n, 1), "record-limit"),
                ("relationship-table", lambda n: model_with_records(2, n), "record-limit"),
                ("view-source-table", lambda n: view_with_records(n, 1), "record-limit"),
                ("view-included-table", lambda n: view_with_records(2, n), "record-limit"),
                ("reference-model-processes", reference_model_with_records, "record-limit"),
                ("aggregate-references", aggregate_references, "reference-limit"),
            )
            for label, factory, expected in record_cases:
                with self.subTest(record_section=label, limit="exact"):
                    exact = CHECKER.parse_asset(_write(root, f"records-{label}-exact.md", factory(MAX_RECORDS_PER_SECTION)))
                    self.assert_no_errors(exact)
                with self.subTest(record_section=label, limit="plus-one"):
                    over = CHECKER.parse_asset(_write(root, f"records-{label}-plus-one.md", factory(MAX_RECORDS_PER_SECTION + 1)))
                    self.assertIn(expected, _codes(over))

        with _temp_root() as root:
            nested = _parse(root, _asset("nested-state", "process", "en", _process_body(extra="\n## Inputs\n\n- ```\n# hidden\n```\n")), name="nested-state")
            self.assertIn("nested-container", _codes(nested))
            with mock.patch.object(markdown_profile, "MAX_ACTIVE_CONTAINER_STATES", MAX_ACTIVE_CONTAINER_STATES):
                _, bounded = markdown_profile._scan("nested-state.md", ["- ```", "# hidden", "```"], 0)
            self.assertIn("nested-container", tuple(item.code for item in bounded))
            _, closed = markdown_profile._scan("closed-state.md", ["```", "hidden", "```"], 0)
            self.assertNotIn("state-limit", tuple(item.code for item in closed))
            with mock.patch.object(markdown_profile, "MAX_ACTIVE_CONTAINER_STATES", 0):
                _, limited = markdown_profile._scan("state-limit.md", ["```"], 0)
            self.assertIn("state-limit", tuple(item.code for item in limited))

    def test_diagnostic_class_whitelist_and_profile_version_serialization_contract(self) -> None:
        from alps_markdown import locale_compare

        allowed = frozenset(
            {
                "host-input",
                "unsupported-profile-syntax",
                "profile-structure",
                "semantic",
                "locale-mismatch",
                "unverified-locale-identity",
                "quality-review",
                "internal",
            }
        )
        with _temp_root() as root:
            malformed = _parse(root, _asset("malformed", "process", "en", _process_body()).replace("name: malformed", "unknown: value"), name="malformed")
            quality = _parse(root, _asset("quality", "process", "en", _process_body(outcome_lines=("The outcome is recorded.",))), name="quality")
            semantic = CHECKER.check_document(
                _write(root, "semantic.md", _asset("semantic", "process-model", "en", _model_body().replace("| Alpha | Information | Beta | Supports |", "| Gamma | Information | Beta | Supports |"))),
                {"example/alps@1.2.3": root},
            )
            invalid = root / "invalid.md"
            invalid.write_bytes(b"\xff")
            host = CHECKER.parse_asset(invalid)
            internal = CHECKER.check_document(root / "missing.md", object())
            english = CHECKER.parse_asset(_write(root, "pair-en.md", _asset("pair", "process", "en", _process_body(outcome_lines=("One `skill:#alpha`.",)))))
            japanese = CHECKER.parse_asset(_write(root, "pair-ja.md", _asset("pair", "process", "ja", _process_body("ja", outcome_lines=("一つ `skill:#beta`。",)))))
            locale_diagnostics = locale_compare.compare_locale_ir(english.ir, japanese.ir)

            observed = set()
            for result in (malformed, quality, semantic, host, internal):
                observed.update(_classes(result))
            observed.update(item.class_name for item in locale_diagnostics)
            self.assertTrue(observed <= allowed, sorted(observed - allowed))
            self.assertIn("quality-review", observed)
            self.assertIn("host-input", observed)
            self.assertIn("internal", observed)
            self.assertIn("locale-mismatch", observed)

            valid = CHECKER.check_document(_write(root, "serialized.md", _asset("serialized", "process", "en", _process_body())), {"example/alps@1.2.3": root})
            contract = {
                "profile_version": CHECKER.PROFILE_VERSION,
                "diagnostics": [asdict(item) for item in valid.diagnostics],
                "ir": asdict(valid.ir) if valid.ir is not None else None,
            }
            encoded = json.dumps(contract, ensure_ascii=False, sort_keys=True)
            decoded = json.loads(encoded)
            self.assertEqual(decoded["profile_version"], "alps-markdown/v2")
            self.assertEqual(decoded["ir"]["kind"], "process")
            self.assertIn("sections", decoded["ir"])


if __name__ == "__main__":
    unittest.main()
