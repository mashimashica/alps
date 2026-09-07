"""Local behavior checks. Grants are test-harness operator actions only."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "input" / "ledger_api.py"
RUNNER = ROOT / "deliverables/skills/reimbursement-rollup/scripts/rollup.py"


class RollupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "verification")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.state = self.folder / "source.sqlite"
        self.checkpoint = self.folder / "request.json"

    def api(self, *args):
        proc = subprocess.run([sys.executable, str(API), "--state", str(self.state), *args],
                              text=True, capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return json.loads(proc.stdout)

    def setup_source(self, rows=None):
        fixture = ROOT / "input/fixture.json"
        if rows is not None:
            fixture = self.folder / "fixture.json"
            fixture.write_text(json.dumps({"records": rows}))
        self.api("init", "--fixture", str(fixture))

    def run_rollup(self, start="2026-02-01", end="2026-02-15", api=API):
        proc = subprocess.run([sys.executable, str(RUNNER), "--api", str(api), "--state", str(self.state),
            "--checkpoint", str(self.checkpoint), "--start", start, "--end", end],
            text=True, capture_output=True)
        self.assertFalse(proc.stderr, proc.stderr)
        return proc.returncode, json.loads(proc.stdout)

    def finish(self, **kwargs):
        for _ in range(10):
            code, result = self.run_rollup(**kwargs)
            if code == 0:
                return result
            self.assertEqual(code, 75, result)
            self.assertFalse(result["complete"])
            self.assertNotIn("vendors", result)
            self.api("grant-tranche")
        self.fail("did not complete")

    def test_fixture_three_tranches_and_repeat(self):
        self.setup_source()
        for examined in (6, 12):
            code, result = self.run_rollup()
            self.assertEqual(code, 75)
            self.assertEqual(result["examined_records"], examined)
            self.assertNotIn("vendors", result)
            self.assertEqual(self.api("describe")["remaining_calls"], 0)
            before = self.checkpoint.read_bytes()
            self.assertEqual(self.run_rollup()[0], 75)
            self.assertEqual(before, self.checkpoint.read_bytes())
            self.api("grant-tranche")
        code, result = self.run_rollup()
        self.assertEqual(code, 0, result)
        self.assertEqual(result["examined_records"], 17)
        self.assertEqual([(v["vendor_id"], v["settled_charge_cents"], v["settled_credit_cents"],
                           v["net_cents"], v["qualifying_entry_count"]) for v in result["vendors"]],
                         [("alder", 14000, 1500, 12500, 4), ("birch", 7000, 200, 6800, 2),
                          ("cedar", 3250, 3250, 0, 2), ("dune", 400, 1200, -800, 2),
                          ("elm", 2345, 0, 2345, 1)])
        metadata = self.api("describe")
        self.assertEqual(self.run_rollup(), (0, result))
        self.assertEqual(self.api("describe"), metadata)

    def test_invalid_interval_no_calls(self):
        self.setup_source()
        before = self.api("describe")
        for start, end in [("2026-02-16", "2026-02-01"), ("2026-02-30", "2026-03-01"),
                           ("20260201", "2026-02-15")]:
            code, result = self.run_rollup(start, end)
            self.assertEqual(code, 2)
            self.assertFalse(result["complete"])
            self.assertFalse(self.checkpoint.exists())
        self.assertEqual(self.api("describe"), before)

    def test_empty_source(self):
        self.setup_source([])
        code, result = self.run_rollup()
        self.assertEqual(code, 0)
        self.assertEqual(result["vendors"], [])
        self.assertEqual(result["examined_records"], 0)
        self.assertEqual(self.api("describe")["remaining_calls"], 1)

    def test_no_matches_still_traverses_every_page(self):
        self.setup_source()
        result = self.finish(start="1999-01-01", end="1999-01-01")
        self.assertEqual(result["vendors"], [])
        self.assertEqual(result["examined_records"], 17)
        self.assertEqual(self.api("describe")["tranche"], 3)

    def test_lost_response_retry_not_free_not_double_counted(self):
        self.setup_source()
        adapter = ROOT / "verification/lossy_api.py"
        code, result = self.run_rollup(api=adapter)
        self.assertEqual(code, 2)
        self.assertFalse(result["complete"])
        self.assertEqual(self.api("describe")["remaining_calls"], 1)
        self.assertEqual(json.loads(self.checkpoint.read_text())["entries"], [])
        code, result = self.run_rollup(api=adapter)
        self.assertEqual(code, 75)
        self.assertEqual(result["examined_records"], 3)
        self.assertEqual(self.api("describe")["remaining_calls"], 0)
        self.api("grant-tranche")
        result = self.finish(api=adapter)
        self.assertEqual(result["examined_records"], 17)
        self.assertEqual(sum(v["qualifying_entry_count"] for v in result["vendors"]), 11)
        self.assertEqual(result["vendors"][0]["net_cents"], 12500)
        self.assertEqual(self.api("describe")["tranche"], 4)

    def test_binding_and_corrupt_checkpoint_fail_closed(self):
        self.setup_source()
        self.assertEqual(self.run_rollup()[0], 75)
        self.api("grant-tranche")
        before = self.api("describe")
        self.assertEqual(self.run_rollup(start="2026-02-02")[0], 2)
        self.checkpoint.write_text("{")
        self.assertEqual(self.run_rollup()[0], 2)
        self.assertEqual(self.api("describe"), before)

    def test_nonchronological_large_integer_and_zero(self):
        rows = json.loads((ROOT / "input/fixture.json").read_text())["records"]
        rows = [dict(rows[0], entry_id="x1", posted_on="2099-01-01"),
                dict(rows[0], entry_id="x2", posted_on="1900-01-01"),
                dict(rows[0], entry_id="x3", status="pending"),
                dict(rows[0], entry_id="x4", vendor_id="z", amount_cents=10**40),
                dict(rows[0], entry_id="x5", vendor_id="a", amount_cents=0)]
        self.setup_source(rows)
        result = self.finish()
        self.assertEqual([v["vendor_id"] for v in result["vendors"]], ["a", "z"])
        self.assertEqual(result["vendors"][0]["qualifying_entry_count"], 1)
        self.assertEqual(result["vendors"][1]["net_cents"], 10**40)

    def test_protocol_rejection_before_incorporation(self):
        spec = importlib.util.spec_from_file_location("rollup", RUNNER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        row = json.loads((ROOT / "input/fixture.json").read_text())["records"][0]
        initial = {"snapshot_id": "s", "total_records": 2, "entries": [],
                   "cursors": [], "next_cursor": None, "complete": False}
        good = {"snapshot_id": "s", "total_records": 2, "items": [row],
                "next_cursor": "opaque", "tranche": 1}
        invalid = [dict(good, snapshot_id="other"), dict(good, next_cursor=None),
                   dict(good, items=[row, row]), dict(good, items=[dict(row, amount_cents=1.5)]),
                   dict(good, items=[], next_cursor="opaque")]
        missing = dict(good)
        del missing["next_cursor"]
        invalid.append(missing)
        for response in invalid:
            state = copy.deepcopy(initial)
            with self.assertRaises(module.Failure):
                module.incorporate(state, response, None)
            self.assertEqual(state, initial)
        state = copy.deepcopy(initial)
        module.incorporate(state, good, None)
        saved = copy.deepcopy(state)
        with self.assertRaises(module.Failure):
            module.incorporate(state, good, None)
        self.assertEqual(state, saved)


if __name__ == "__main__":
    unittest.main(verbosity=2)
