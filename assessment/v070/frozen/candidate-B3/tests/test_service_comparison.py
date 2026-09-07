"""Behavioral checks for the example tool; Outcome judgments need review."""

from __future__ import annotations

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
SPEC = importlib.util.spec_from_file_location("compare_measurements", SCRIPT)
assert SPEC and SPEC.loader
COMPARISON = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COMPARISON)
LIMITS = ["--min-samples", "4", "--max-p95-ms", "200",
          "--max-error-rate", "0.05", "--max-p95-increase-ms", "50"]
HEADER = "request_id,duration_ms,status\n"


class ServiceComparisonTests(unittest.TestCase):
    def invoke(self, candidate: Path, *extra: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(EXAMPLE / "assets/baseline.csv"),
             str(candidate), *LIMITS, *extra],
            capture_output=True, text=True, check=False,
        )

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
        for name in ("baseline", "candidate"):
            data = (EXAMPLE / f"assets/{name}.csv").read_bytes()
            self.assertEqual(evidence[name]["sha256"], hashlib.sha256(data).hexdigest())

    def test_completed_calculation_can_fail_pilot_limits(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.csv"
            data = HEADER + "c1,110,ok\nc2,120,ok\nc3,140,ok\nc4,2000,error\n"
            candidate.write_text(data)
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
            self.assertEqual(candidate.read_text(), data)
            self.assertEqual(list(Path(directory).iterdir()), [candidate])

    def test_nearest_rank_and_failed_requests_are_included(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "measurements.csv"
            rows = [f"r{i},{i},{'error' if i == 19 else 'ok'}\n"
                    for i in range(20, 0, -1)]
            path.write_text(HEADER + "".join(rows))
            evidence = COMPARISON.summarize(path)
            self.assertEqual(evidence["p95_ms"], 19)
            self.assertEqual(evidence["error_rate"], 0.05)

    def test_limits_are_inclusive_and_selected_by_caller(self) -> None:
        result = self.invoke(EXAMPLE / "assets/candidate.csv",
                             "--max-p95-ms", "160", "--max-error-rate", "0",
                             "--max-p95-increase-ms", "30")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(all(json.loads(result.stdout)["checks"].values()))
        result = self.invoke(EXAMPLE / "assets/candidate.csv", "--min-samples", "5")
        self.assertEqual(result.returncode, 0, result.stderr)
        evidence = json.loads(result.stdout)
        self.assertFalse(evidence["checks"]["baseline_sample_count"])
        self.assertFalse(evidence["checks"]["candidate_sample_count"])

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
            "status": HEADER + "r1,1,unknown\n",
            "nan": HEADER + "r1,NaN,ok\n",
            "infinity": HEADER + "r1,inf,ok\n",
            "negative": HEADER + "r1,-1,ok\n",
            "not_numeric": HEADER + "r1,slow,ok\n",
            "broken_quote": HEADER + '"r1,1,ok\n',
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.csv"
            for name, content in cases.items():
                with self.subTest(case=name):
                    path.write_text(content)
                    result = self.invoke(path)
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(result.stdout, "")
                    self.assertIn("measurement error", result.stderr)

    def test_unreadable_or_invalid_encoding_has_no_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.csv"
            result = self.invoke(path)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertIn(str(path), result.stderr)
            path.write_bytes(b"\xff\xfe")
            result = self.invoke(path)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")

    def test_invalid_limits_do_not_produce_measurement_results(self) -> None:
        for option, value in [
            ("--min-samples", "0"), ("--max-error-rate", "1.1"),
            ("--max-p95-ms", "NaN"), ("--max-p95-ms", "-1"),
            ("--max-p95-increase-ms", "inf"),
        ]:
            with self.subTest(option=option, value=value):
                result = self.invoke(EXAMPLE / "assets/candidate.csv", option, value)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertTrue(result.stderr)

    def test_help_is_available_without_inputs(self) -> None:
        result = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0)
        self.assertIn("--max-p95-increase-ms", result.stdout)


if __name__ == "__main__":
    unittest.main()
