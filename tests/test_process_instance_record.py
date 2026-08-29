from __future__ import annotations

import importlib.util
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "skills/apply-alps/scripts/process_instance_record.py"
SPEC = importlib.util.spec_from_file_location("process_instance_record", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
RECORD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = RECORD
SPEC.loader.exec_module(RECORD)


def _record(tailoring_scope: str | None) -> str:
    scope_line = f"- `scope`: {tailoring_scope}\n" if tailoring_scope is not None else ""
    return (
        "# Example\n\n"
        "## Application basis\n"
        "- `kind`: application\n"
        "- `record_format`: process-instance-record/1\n"
        "- `source`: skill:example#process -> example@1#process\n"
        "- `context`: Example context\n"
        "- `scope`: Example application scope\n\n"
        "## Intended Outcome\n"
        "- `kind`: outcome\n"
        "- `source_statement`: The result is ready.\n\n"
        "## Tailoring\n"
        "- `kind`: tailoring\n"
        f"{scope_line}"
        "- `basis`: Risk and requirements\n"
        "- `candidate_evaluation`: Candidate Processes evaluated\n"
        "- `process_name_change`: not changed\n"
        "- `name_consistency`: not applicable\n"
        "- `source_traceability`: not applicable\n"
        "- `decision`: Approved\n"
        "- `affected_party_input`: No affected parties identified\n"
        "- `controls_constraints`: None apply\n"
    )


class ProcessInstanceRecordTests(unittest.TestCase):
    def _check(self, content: str) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.md"
            path.write_text(content, encoding="utf-8")
            return RECORD.check_record(path, "instantiation")

    def test_tailoring_scope_is_required(self) -> None:
        errors = self._check(_record(None))
        self.assertTrue(any("`scope` is required" in error for error in errors), errors)

    def test_tailoring_with_scope_passes_instantiation_check(self) -> None:
        self.assertEqual(self._check(_record("Affected Tasks")), [])

    def test_tailoring_name_fields_are_required(self) -> None:
        content = _record("Affected Tasks").replace(
            "- `source_traceability`: not applicable\n", ""
        )
        errors = self._check(content)
        self.assertTrue(
            any("`source_traceability` is required" in error for error in errors),
            errors,
        )

    def test_conformance_process_basis_and_basis_value_are_checked(self) -> None:
        conformance = (
            _record("Affected Tasks")
            + "\n## Conformance\n"
            + "- `kind`: conformance\n"
            + "- `subject`: Recorded Process Instance\n"
            + "- `scope`: Full Process\n"
            + "- `basis`: Outcome\n"
            + "- `claim`: Full\n"
            + "- `evidence`: Evidence set\n"
        )
        errors = self._check(conformance)
        self.assertTrue(any("`process_basis` is required" in error for error in errors), errors)
        self.assertTrue(any("`basis` must be" in error for error in errors), errors)

        valid = conformance.replace(
            "- `scope`: Full Process\n",
            "- `process_basis`: Process and authoritative description\n"
            "- `scope`: Full Process\n",
        ).replace("- `basis`: Outcome\n", "- `basis`: Outcome Conformance\n")
        self.assertEqual(self._check(valid), [])

    def test_japanese_record_uses_language_neutral_conformance_basis_literals(self) -> None:
        content = (
            _record("影響を受けるタスク")
            + "\n## 適合\n"
            + "- `kind`: conformance\n"
            + "- `subject`: 記録対象のプロセスインスタンス\n"
            + "- `process_basis`: プロセスおよび正本プロセス記述\n"
            + "- `scope`: プロセス全体\n"
            + "- `basis`: Task Conformance\n"
            + "- `claim`: Full\n"
            + "- `evidence`: 証拠集合\n"
        )
        self.assertEqual(self._check(content), [])

    def test_binding_boundaries_and_completion_fields_are_checked(self) -> None:
        boundary_cases = {
            "raw-html": _record("Affected Tasks") + "\n<section>hidden</section>\n",
            "html-comment": _record("Affected Tasks") + "\n<!-- hidden -->\n",
            "unclosed-comment": _record("Affected Tasks") + "\n<!-- hidden\n",
            "unclosed-fence": _record("Affected Tasks") + "\n```text\nhidden\n",
        }
        for label, content in boundary_cases.items():
            with self.subTest(label=label):
                self.assertTrue(self._check(content))

        incomplete = (
            _record("Affected Tasks")
            + "\n## Handoff\n"
            + "- `kind`: handoff\n"
            + "- `provider`: Provider\n"
            + "- `output`: Output\n"
            + "- `receiver`: Receiver\n"
            + "- `input`: Input\n"
            + "- `correspondence`: Same meaning\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.md"
            path.write_text(incomplete, encoding="utf-8")
            errors = RECORD.check_record(path, "completion")
        self.assertTrue(any("`status` is required" in error for error in errors), errors)
        self.assertTrue(any("`result` is required" in error for error in errors), errors)
        self.assertTrue(any("`assessment` is required" in error for error in errors), errors)

    def _new_arguments(self, output: Path, *, force: bool = False):
        parser = RECORD.build_parser()
        arguments = [
            "new",
            "--title", "Example",
            "--source", "skill:example#process -> example@1#process",
            "--context", "Example context",
            "--scope", "Example scope",
            "--outcome", "The result is ready.",
            "--output", str(output),
        ]
        if force:
            arguments.insert(1, "--force")
        return parser, parser.parse_args(arguments)

    def test_generator_rejects_existing_regular_output_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "record.md"
            output.write_text("original\n", encoding="utf-8")
            parser, args = self._new_arguments(output)
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    args.handler(args, parser)
            self.assertEqual(output.read_text(encoding="utf-8"), "original\n")

    def test_generator_rejects_symbolic_link_output_with_or_without_force(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symlink support is unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.md"
            target.write_text("original\n", encoding="utf-8")
            output = root / "record.md"
            try:
                output.symlink_to(target)
            except OSError as error:
                self.skipTest(f"symlinks unsupported: {error}")
            for force in (False, True):
                with self.subTest(force=force):
                    parser, args = self._new_arguments(output, force=force)
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        with self.assertRaises(SystemExit):
                            args.handler(args, parser)
                    self.assertTrue(output.is_symlink())
                    self.assertEqual(target.read_text(encoding="utf-8"), "original\n")


if __name__ == "__main__":
    unittest.main()
