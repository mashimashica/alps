"""Behavioral checks for the example tool; Outcome judgments need review."""

from __future__ import annotations

import codecs
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/assess-service-change"
SCRIPT = EXAMPLE / "scripts/compare_measurements.py"
BASELINE = EXAMPLE / "assets/baseline.csv"
CANDIDATE = EXAMPLE / "assets/candidate.csv"
SPEC = importlib.util.spec_from_file_location("compare_measurements", SCRIPT)
assert SPEC and SPEC.loader
COMPARISON = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COMPARISON)
LIMITS = ["--min-samples", "4", "--max-p95-ms", "200",
          "--max-error-rate", "0.05", "--max-p95-increase-ms", "50"]
HEADER = "request_id,duration_ms,status\n"


class ServiceComparisonTests(unittest.TestCase):
    def invoke(self, candidate: Path, *extra: str,
               baseline: Path = BASELINE) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(baseline), str(candidate),
             *LIMITS, *extra],
            capture_output=True, text=True, check=False,
        )

    def assertMeasurementError(self, result: subprocess.CompletedProcess) -> None:
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("measurement error", result.stderr)

    def test_documented_command_and_evidence(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/compare_measurements.py",
             "assets/baseline.csv", "assets/candidate.csv", *LIMITS],
            cwd=EXAMPLE, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        evidence = json.loads(result.stdout)
        self.assertEqual(evidence["baseline"]["p95_ms"], 130)
        self.assertEqual(evidence["candidate"]["p95_ms"], 160)
        self.assertEqual(evidence["candidate"]["count"], 4)
        self.assertEqual(evidence["candidate"]["error_rate"], 0)
        self.assertEqual(evidence["p95_increase_ms"], 30)
        self.assertTrue(all(evidence["checks"].values()))
        self.assertEqual(evidence["limits"]["max_error_rate"], 0.05)
        self.assertEqual(evidence["input_relationship"],
                         {"identical_bytes": False, "same_request_ids": True})
        for name in ("baseline", "candidate"):
            data = (EXAMPLE / f"assets/{name}.csv").read_bytes()
            self.assertEqual(evidence[name]["sha256"], hashlib.sha256(data).hexdigest())

    def test_completed_calculation_can_fail_pilot_limits(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.csv"
            data = HEADER + "r1,110,ok\nr2,120,ok\nr3,140,ok\nr4,2000,error\n"
            candidate.write_text(data, encoding="utf-8")
            result = self.invoke(candidate)
            self.assertEqual(result.returncode, 0, result.stderr)
            evidence = json.loads(result.stdout)
            self.assertEqual(evidence["candidate"]["error_rate"], 0.25)
            self.assertEqual(evidence["candidate"]["p95_ms"], 2000)
            self.assertEqual(evidence["p95_increase_ms"], 1870)
            self.assertEqual(evidence["checks"], {
                "baseline_sample_count": True, "candidate_sample_count": True,
                "candidate_p95": False, "candidate_error_rate": False,
                "p95_increase": False,
            })
            self.assertTrue(evidence["input_relationship"]["same_request_ids"])
            self.assertEqual(candidate.read_text(encoding="utf-8"), data)
            self.assertEqual(list(Path(directory).iterdir()), [candidate])

    def test_input_relationship_reports_identical_and_mismatched_inputs(self) -> None:
        result = self.invoke(BASELINE)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["input_relationship"],
                         {"identical_bytes": True, "same_request_ids": True})
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.csv"
            candidate.write_text(
                HEADER + "c1,110,ok\nc2,120,ok\nc3,140,ok\nc4,160,ok\n",
                encoding="utf-8")
            result = self.invoke(candidate)
            self.assertEqual(result.returncode, 0, result.stderr)
            evidence = json.loads(result.stdout)
            self.assertEqual(evidence["input_relationship"],
                             {"identical_bytes": False, "same_request_ids": False})
            self.assertTrue(all(evidence["checks"].values()))

    def test_nearest_rank_and_failed_requests_are_included(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "measurements.csv"
            rows = [f"r{i},{i},{'error' if i == 19 else 'ok'}\n"
                    for i in range(20, 0, -1)]
            path.write_text(HEADER + "".join(rows), encoding="utf-8")
            evidence = COMPARISON.summarize(path)
            self.assertEqual(evidence["p95_ms"], 19)
            self.assertEqual(evidence["error_rate"], 0.05)

    def test_limits_are_inclusive_and_selected_by_caller(self) -> None:
        result = self.invoke(CANDIDATE,
                             "--max-p95-ms", "160", "--max-error-rate", "0",
                             "--max-p95-increase-ms", "30")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(all(json.loads(result.stdout)["checks"].values()))
        result = self.invoke(CANDIDATE, "--min-samples", "5")
        self.assertEqual(result.returncode, 0, result.stderr)
        evidence = json.loads(result.stdout)
        self.assertFalse(evidence["checks"]["baseline_sample_count"])
        self.assertFalse(evidence["checks"]["candidate_sample_count"])
        result = self.invoke(CANDIDATE, "--max-error-rate", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["limits"]["max_error_rate"], 1)

    def test_invalid_measurements_produce_diagnostics_without_results(self) -> None:
        cases = {
            "empty": "",
            "no_data": HEADER,
            "wrong_header": "duration_ms,request_id,status\n1,r1,ok\n",
            "short_row": HEADER + "r1,1\n",
            "long_row": HEADER + "r1,1,ok,extra\n",
            "blank_row": HEADER + "\n",
            "duplicate": HEADER + "r1,1,ok\nr1,2,ok\n",
            "empty_identifier": HEADER + ",1,ok\n",
            "blank_identifier": HEADER + "  ,1,ok\n",
            "trailing_space_identifier": HEADER + "r1 ,1,ok\n",
            "leading_space_identifier": HEADER + " r1,1,ok\n",
            "status": HEADER + "r1,1,unknown\n",
            "nan": HEADER + "r1,NaN,ok\n",
            "infinity": HEADER + "r1,inf,ok\n",
            "negative": HEADER + "r1,-1,ok\n",
            "not_numeric": HEADER + "r1,slow,ok\n",
            "exponent": HEADER + "r1,1e2,ok\n",
            "underscore": HEADER + "r1,1_000,ok\n",
            "padded_number": HEADER + "r1, 100,ok\n",
            "plus_sign": HEADER + "r1,+1,ok\n",
            "broken_quote": HEADER + '"r1,1,ok\n',
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.csv"
            for name, content in cases.items():
                with self.subTest(case=name, side="candidate"):
                    path.write_text(content, encoding="utf-8")
                    self.assertMeasurementError(self.invoke(path))
                with self.subTest(case=name, side="baseline"):
                    self.assertMeasurementError(
                        self.invoke(CANDIDATE, baseline=path))

    def test_whitespace_identifier_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "padded.csv"
            path.write_text(HEADER + "r1 ,1,ok\n", encoding="utf-8")
            result = self.invoke(path)
            self.assertMeasurementError(result)
            self.assertIn("leading or trailing whitespace", result.stderr)

    def test_utf8_bom_is_rejected_with_specific_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bom.csv"
            path.write_bytes(codecs.BOM_UTF8 + CANDIDATE.read_bytes())
            for side, result in (("candidate", self.invoke(path)),
                                 ("baseline", self.invoke(CANDIDATE, baseline=path))):
                with self.subTest(side=side):
                    self.assertMeasurementError(result)
                    self.assertIn("UTF-8 BOM is not supported", result.stderr)

    def test_unreadable_or_invalid_encoding_has_no_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.csv"
            result = self.invoke(path)
            self.assertMeasurementError(result)
            self.assertIn(str(path), result.stderr)
            path.write_bytes(b"\xff\xfe")
            self.assertMeasurementError(self.invoke(path))
            self.assertMeasurementError(self.invoke(Path(directory)))
            self.assertMeasurementError(self.invoke(CANDIDATE, baseline=Path(directory)))

    def test_invalid_limits_do_not_produce_measurement_results(self) -> None:
        for option, value in [
            ("--min-samples", "0"), ("--min-samples", "1.5"),
            ("--max-error-rate", "1.1"),
            ("--max-p95-ms", "NaN"), ("--max-p95-ms", "-1"),
            ("--max-p95-ms", "1e2"), ("--max-p95-ms", "1_000"),
            ("--max-p95-ms", " 100"), ("--max-p95-ms", "+1"),
            ("--max-p95-increase-ms", "inf"),
        ]:
            with self.subTest(option=option, value=value):
                result = self.invoke(CANDIDATE, option, value)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("usage:", result.stderr)
                self.assertNotIn("measurement error", result.stderr)

    def test_help_is_available_without_inputs(self) -> None:
        result = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0)
        self.assertIn("--max-p95-increase-ms", result.stdout)


if __name__ == "__main__":
    unittest.main()
