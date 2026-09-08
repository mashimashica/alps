"""Local component and CLI integration checks; all state remains in verification/."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "input/ledger_api.py"
SCRIPT = ROOT / "deliverables/skills/rollup-reimbursements/scripts/rollup.py"
spec = importlib.util.spec_from_file_location("rollup", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RollupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "verification", prefix="case-")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.state = self.work / "source.sqlite"
        self.cp = self.work / "request.json"
        self.output = self.work / "result.json"

    def call(self, *args, code=0):
        response = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)
        self.assertEqual(response.returncode, code, response.stdout + response.stderr)
        return json.loads(response.stdout or response.stderr)

    def source(self, *args, code=0):
        return self.call(API, "--state", self.state, *args, code=code)

    def init(self, rows=None):
        fixture = ROOT / "input/fixture.json"
        if rows is not None:
            fixture = self.work / "fixture.json"
            fixture.write_text(json.dumps({"records": rows}))
        return self.source("init", "--fixture", fixture)

    def run_rollup(self, code=10, start="2026-02-01", end="2026-02-15", api=API):
        return self.call(SCRIPT, "run", "--api", api, "--state", self.state,
                         "--start", start, "--end", end, "--checkpoint", self.cp,
                         "--output", self.output, code=code)

    def result(self):
        return json.loads(self.output.read_text())

    def complete(self, **kwargs):
        for _ in range(10):
            result = subprocess.run([sys.executable, str(SCRIPT), "run", "--api", str(API),
                                     "--state", str(self.state), "--start", kwargs.get("start", "2026-02-01"),
                                     "--end", kwargs.get("end", "2026-02-15"), "--checkpoint", str(self.cp),
                                     "--output", str(self.output)], capture_output=True, text=True)
            if result.returncode == 0:
                return self.result()
            self.assertEqual(result.returncode, 10, result.stderr)
            # This is the test harness acting as the operator, never target code.
            self.source("grant-tranche")
        self.fail("Did not terminate")

    def test_fixture_three_tranches_and_no_approval(self):
        self.init()
        first = self.run_rollup()
        self.assertEqual((first["complete"], first["examined_entries"], first["committed_pages"]), (False, 6, 2))
        before = self.cp.read_bytes()
        self.run_rollup()
        self.assertEqual(self.cp.read_bytes(), before)
        self.assertEqual(self.source("describe")["remaining_calls"], 0)
        self.source("grant-tranche")
        second = self.run_rollup()
        self.assertEqual(second["examined_entries"], 12)
        self.source("grant-tranche")
        third = self.run_rollup(code=0)
        self.assertEqual((third["complete"], third["examined_entries"], third["committed_pages"]), (True, 17, 6))
        actual = [(v["vendor_id"], v["settled_charge_cents"], v["settled_credit_cents"],
                   v["net_cents"], v["qualifying_entry_count"]) for v in self.result()["vendors"]]
        self.assertEqual(actual, [("alder", 14000, 1500, 12500, 4), ("birch", 7000, 200, 6800, 2),
                                  ("cedar", 3250, 3250, 0, 2), ("dune", 400, 1200, -800, 2),
                                  ("elm", 2345, 0, 2345, 1)])
        self.run_rollup(code=0)
        self.assertEqual(self.source("describe")["remaining_calls"], 0)

    def test_invalid_intervals_before_source_calls(self):
        self.init()
        for start, end in [("2026-02-30", "2026-03-01"), ("2026-02-16", "2026-02-15"),
                           ("20260201", "2026-02-15")]:
            self.run_rollup(code=2, start=start, end=end)
        self.assertFalse(self.cp.exists())
        self.assertEqual(self.source("describe")["remaining_calls"], 2)

    def test_empty_ledger(self):
        self.init([])
        self.run_rollup(code=0)
        value = self.result()
        self.assertEqual((value["complete"], value["examined_entries"], value["vendors"]), (True, 0, []))
        self.assertEqual(self.source("describe")["remaining_calls"], 1)

    def test_empty_interval_still_full_coverage(self):
        self.init()
        value = self.complete(start="2025-01-01", end="2025-12-31")
        self.assertEqual((value["examined_entries"], value["vendors"]), (17, []))

    def test_other_snapshot_single_day_and_big_integer(self):
        rows = [dict(entry_id=str(i), vendor_id="z", posted_on="2024-02-29", kind=kind,
                     status="settled", amount_cents=amount, currency="USD")
                for i, kind, amount in [(1, "charge", 2**80), (2, "credit", 2**80 + 7), (3, "charge", 0)]]
        self.init(rows)
        self.run_rollup(code=0, start="2024-02-29", end="2024-02-29")
        self.assertEqual(self.result()["vendors"][0]["net_cents"], -7)
        self.assertEqual(self.result()["vendors"][0]["qualifying_entry_count"], 3)

    def test_lost_response_retries_metered_page_once_in_aggregation(self):
        self.init()
        adapter = ROOT / "verification/lost_response_api.py"
        self.run_rollup(code=3, api=adapter)
        self.assertEqual(self.source("describe")["remaining_calls"], 1)
        self.assertEqual(len(json.loads(self.cp.read_text())["records"]), 0)
        first = self.run_rollup(api=adapter)
        self.assertEqual(first["examined_entries"], 3)
        for expected in (9, 15):
            self.source("grant-tranche")
            self.assertEqual(self.run_rollup(api=adapter)["examined_entries"], expected)
        self.source("grant-tranche")
        self.run_rollup(code=0, api=adapter)
        self.assertEqual(self.result()["examined_entries"], 17)
        self.assertEqual(self.result()["vendors"][0]["net_cents"], 12500)

    def test_interruption_after_call_before_commit(self):
        self.init()
        parser_args = type("Args", (), dict(command="run", api=str(API), state=str(self.state),
                                          start="2026-02-01", end="2026-02-15",
                                          checkpoint=str(self.cp), output=str(self.output)))()
        original = module.atomic
        def interrupt(path, value):
            if path == str(self.cp) and value.get("records"):
                raise OSError("simulated pre-commit interruption")
            original(path, value)
        with mock.patch.object(module, "atomic", side_effect=interrupt):
            with self.assertRaises(OSError):
                module.run(parser_args)
        self.assertEqual(self.source("describe")["remaining_calls"], 1)
        self.assertEqual(self.run_rollup()["examined_entries"], 3)
        final = self.complete()
        self.assertEqual((final["examined_entries"], final["committed_pages"]), (17, 6))

    def test_output_failure_after_checkpoint_commits(self):
        self.init([])
        args = type("Args", (), dict(command="run", api=str(API), state=str(self.state),
                                    start="2026-02-01", end="2026-02-15",
                                    checkpoint=str(self.cp), output=str(self.output)))()
        original = module.atomic
        def interrupt(path, value):
            if path == str(self.output):
                raise OSError("simulated output failure")
            original(path, value)
        with mock.patch.object(module, "atomic", side_effect=interrupt):
            with self.assertRaises(OSError):
                module.run(args)
        self.assertTrue(json.loads(self.cp.read_text())["exhausted"])
        self.call(SCRIPT, "status", "--checkpoint", self.cp, "--output", self.output)
        self.assertEqual(self.source("describe")["remaining_calls"], 1)

    def test_changed_request_and_snapshot_fail_before_new_page(self):
        self.init()
        self.run_rollup()
        before = self.cp.read_bytes()
        self.source("grant-tranche")
        self.run_rollup(code=2, start="2026-02-02")
        self.assertEqual(self.source("describe")["remaining_calls"], 2)
        self.assertEqual(self.cp.read_bytes(), before)
        self.state.unlink()  # Verification-only replacement, never recovery guidance.
        self.init([])
        self.run_rollup(code=2)
        self.assertEqual(self.source("describe")["remaining_calls"], 2)
        self.assertEqual(self.cp.read_bytes(), before)

    def test_source_errors_and_duplicate_response(self):
        self.init()
        meta = self.source("describe")
        self.source("page", "--snapshot", meta["snapshot_id"], "--cursor", "invalid", code=2)
        self.source("page", "--snapshot", "wrong", code=4)
        self.assertEqual(self.source("describe")["remaining_calls"], 2)
        page = self.source("page", "--snapshot", meta["snapshot_id"])
        replay = self.source("page", "--snapshot", meta["snapshot_id"])
        self.assertEqual(page, replay)
        self.source("page", "--snapshot", meta["snapshot_id"], code=75)
        cp = dict(version=1, start="2026-02-01", end="2026-02-15", records=[], page_cursors=[],
                  total_records=17, snapshot_id=meta["snapshot_id"], next_cursor=None, exhausted=False)
        first = module.incorporate(cp, page, 1)
        with self.assertRaises(module.Failure):
            module.incorporate(first, replay, 1)
        self.assertEqual(len(first["records"]), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
