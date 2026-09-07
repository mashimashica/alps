"""Local authoring checks. Grants below simulate the operator, not runner behavior."""
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
API = ROOT / "input/ledger_api.py"
RUNNER = ROOT / "deliverables/skills/reimbursement-ledger-rollup/scripts/rollup.py"
spec = importlib.util.spec_from_file_location("rollup", RUNNER)
rollup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rollup)


class Checks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT, prefix="verification-")
        self.base = Path(self.tmp.name)
        self.source = self.base / "source.sqlite"
        self.checkpoint = self.base / "checkpoint.sqlite"

    def tearDown(self):
        self.tmp.cleanup()

    def api(self, command, *extra):
        result = subprocess.run([sys.executable, str(API), "--state", str(self.source), command, *extra], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def initialize(self, records=None):
        fixture = ROOT / "input/fixture.json"
        if records is not None:
            fixture = self.base / "fixture.json"
            fixture.write_text(json.dumps({"records": records}))
        self.api("init", "--fixture", str(fixture))

    def args(self, start="2026-02-01", end="2026-02-15"):
        import argparse
        return argparse.Namespace(api=str(API), source=str(self.source), checkpoint=str(self.checkpoint), start=start, end=end)

    def execute(self, start="2026-02-01", end="2026-02-15"):
        result = subprocess.run([sys.executable, str(RUNNER), "--api", str(API), "--source", str(self.source), "--checkpoint", str(self.checkpoint), "--start", start, "--end", end], capture_output=True, text=True)
        return json.loads(result.stdout), result.returncode

    def finish(self, start="2026-02-01", end="2026-02-15"):
        for _ in range(10):
            result, code = self.execute(start, end)
            if code == 0:
                return result
            self.assertEqual(code, 75, result)
            self.assertFalse(result["complete"])
            self.api("grant-tranche")
        self.fail("did not complete within bounded test grants")

    def test_fixture_complete_across_three_tranches_and_repeat(self):
        self.initialize()
        result, code = self.execute()
        self.assertEqual((code, result["examined_records"], result["complete"]), (75, 6, False))
        repeated, code = self.execute()
        self.assertEqual(repeated, result)
        self.assertEqual(code, 75)
        self.api("grant-tranche")
        result, code = self.execute()
        self.assertEqual((code, result["examined_records"]), (75, 12))
        self.api("grant-tranche")
        result, code = self.execute()
        self.assertEqual((code, result["examined_records"], result["committed_pages"]), (0, 17, 6))
        self.assertEqual([(v["vendor_id"], v["settled_charge_cents"], v["settled_credit_cents"], v["net_cents"], v["qualifying_entry_count"]) for v in result["vendors"]], [
            ("alder", 14000, 1500, 12500, 4), ("birch", 7000, 200, 6800, 2),
            ("cedar", 3250, 3250, 0, 2), ("dune", 400, 1200, -800, 2), ("elm", 2345, 0, 2345, 1)])
        before = self.api("describe")
        self.assertEqual(self.execute(), (result, 0))
        self.assertEqual(self.api("describe"), before)

    def test_empty_and_invalid(self):
        self.initialize([])
        for start, end in [("2026-02-30", "2026-03-01"), ("20260201", "2026-02-15"), ("2026-03-01", "2026-02-01")]:
            result, code = self.execute(start, end)
            self.assertEqual(code, 2, result)
            self.assertFalse(self.checkpoint.exists())
            self.assertEqual(self.api("describe")["remaining_calls"], 2)
        result, code = self.execute()
        self.assertEqual((code, result["vendors"], result["examined_records"], result["committed_pages"]), (0, [], 0, 1))

    def test_no_matches_still_traverses_all(self):
        self.initialize()
        result = self.finish("2025-01-01", "2025-01-31")
        self.assertEqual((result["vendors"], result["examined_records"], result["committed_pages"]), ([], 17, 6))

    def test_lost_counted_response(self):
        self.initialize()
        original = rollup.api
        def lose(args, command, *extra):
            result = original(args, command, *extra)
            if command == "page":
                raise rollup.Failure("response_unavailable: simulated loss after successful source call")
            return result
        with patch.object(rollup, "api", lose):
            with self.assertRaises(rollup.Failure):
                rollup.run(self.args())
        self.assertEqual(self.api("describe")["remaining_calls"], 1)
        result, code = self.execute()
        self.assertEqual((code, result["examined_records"], result["committed_pages"]), (75, 3, 1))
        result = self.finish()
        self.assertEqual((result["examined_records"], result["committed_pages"]), (17, 6))
        self.assertEqual(result["vendors"][0]["net_cents"], 12500)

    def test_rollback_uncommitted_page(self):
        self.initialize()
        original = rollup.apply_page
        def crash(*args):
            original(*args)
            raise RuntimeError("simulated failure after all page writes, before commit")
        with patch.object(rollup, "apply_page", crash):
            with self.assertRaises(RuntimeError):
                rollup.run(self.args())
        with sqlite3.connect(self.checkpoint) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM entries").fetchone()[0], 0)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM vendors").fetchone()[0], 0)
        result = self.finish()
        self.assertEqual(result["vendors"][0]["qualifying_entry_count"], 4)
        self.assertEqual(result["examined_records"], 17)

    def test_binding_mismatch_does_not_spend_calls(self):
        self.initialize()
        self.execute()
        self.api("grant-tranche")
        result, code = self.execute("2026-02-02", "2026-02-15")
        self.assertEqual(code, 2, result)
        self.assertEqual(self.api("describe")["remaining_calls"], 2)

    def test_single_day_and_unbounded_cents(self):
        records = json.loads((ROOT / "input/fixture.json").read_text())["records"]
        records = [records[0], {**records[2], "posted_on": "2026-02-01", "amount_cents": 10**30}]
        self.initialize(records)
        result, code = self.execute("2026-02-01", "2026-02-01")
        self.assertEqual(code, 0, result)
        self.assertEqual(result["vendors"][0]["net_cents"], 12000 - 10**30)
        self.assertEqual(result["vendors"][0]["qualifying_entry_count"], 2)

    def test_snapshot_mismatch(self):
        self.initialize()
        self.execute()
        self.api("grant-tranche")
        original = rollup.metadata
        def changed(args):
            return {**original(args), "snapshot_id": "different_snapshot"}
        with patch.object(rollup, "metadata", changed):
            with self.assertRaises(rollup.Failure) as caught:
                rollup.run(self.args())
        self.assertEqual(caught.exception.code, 4)
        self.assertEqual(self.api("describe")["remaining_calls"], 2)

    def test_duplicate_page_rejected_without_partial_commit(self):
        self.initialize()
        original = rollup.api
        first = None
        def repeated(args, command, *extra):
            nonlocal first
            result = original(args, command, *extra)
            if command == "page":
                if first is None:
                    first = result
                else:
                    result = {**result, "items": first["items"]}
            return result
        with patch.object(rollup, "api", repeated):
            with self.assertRaises(sqlite3.IntegrityError):
                rollup.run(self.args())
        with sqlite3.connect(self.checkpoint) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM entries").fetchone()[0], 3)
        result = self.finish()
        self.assertEqual(result["examined_records"], 17)
        self.assertEqual(result["vendors"][0]["net_cents"], 12500)

    def test_budget_error_is_incomplete(self):
        self.initialize()
        original = rollup.api
        def exhausted(args, command, *extra):
            if command == "page":
                raise rollup.Failure("call_budget_exhausted", 75)
            return original(args, command, *extra)
        with patch.object(rollup, "api", exhausted):
            result, code = rollup.run(self.args())
        self.assertEqual((code, result["complete"], result["examined_records"]), (75, False, 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
