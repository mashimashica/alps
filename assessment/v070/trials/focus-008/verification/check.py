"""Local authorized verification, not an operational ledger reader."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "deliverables/skills/reimbursement-ledger-rollup/scripts/rollup.py"
API = ROOT / "input/ledger_api.py"
FIXTURE = ROOT / "input/fixture.json"
spec = importlib.util.spec_from_file_location("rollup", SCRIPT)
rollup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rollup)


class Checks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "verification")
        self.path = Path(self.temp.name)
        self.source = self.path / "source.sqlite"
        self.cp = self.path / "checkpoint.json"
        self.out = self.path / "report.json"
        self.tranche = 1

    def tearDown(self):
        self.temp.cleanup()

    def api(self, *args):
        result = subprocess.run([sys.executable, str(API), "--state", str(self.source), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def init(self, records=None):
        fixture = FIXTURE
        if records is not None:
            fixture = self.path / "fixture.json"
            fixture.write_text(json.dumps({"records": records}))
        self.api("init", "--fixture", str(fixture))

    def command(self, start="2026-02-01", end="2026-02-15", api=None):
        return [sys.executable, str(SCRIPT), "--api", str(api or API), "--source", str(self.source),
                "--checkpoint", str(self.cp), "--output", str(self.out), "--start", start,
                "--end", end, "--tranche", str(self.tranche)]

    def run_job(self, expected, **kwargs):
        result = subprocess.run(self.command(**kwargs), capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def grant(self):
        self.tranche = self.api("grant-tranche")["tranche"]

    def finish(self, **kwargs):
        for _ in range(8):
            result = subprocess.run(self.command(**kwargs), capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(self.out.read_text())
            self.assertEqual(result.returncode, 75, result.stdout)
            self.grant()
        self.fail("did not complete after sufficient test-controlled grants")

    def test_fixture_complete_and_repeated_invocation(self):
        self.init()
        first = self.run_job(75)
        self.assertEqual((first["examined_records"], first["pages_committed"]), (6, 2))
        self.assertIn("partial_vendors", json.loads(self.out.read_text()))
        self.assertEqual(self.api("describe")["remaining_calls"], 0)
        self.assertEqual(self.run_job(75)["successful_calls_this_run"], 0)
        self.grant()
        self.assertEqual(self.run_job(75)["examined_records"], 12)
        self.grant()
        self.run_job(0)
        final = json.loads(self.out.read_text())
        actual = [(v["vendor_id"], v["charge_cents"], v["credit_cents"], v["net_cents"], v["qualifying_entry_count"]) for v in final["vendors"]]
        self.assertEqual(actual, [("alder", 14000, 1500, 12500, 4), ("birch", 7000, 200, 6800, 2),
                                  ("cedar", 3250, 3250, 0, 2), ("dune", 400, 1200, -800, 2), ("elm", 2345, 0, 2345, 1)])
        self.assertEqual((final["examined_records"], final["pages_committed"], final["next_cursor"]), (17, 6, None))
        self.assertEqual(self.run_job(0)["successful_calls_this_run"], 0)
        self.assertEqual(json.loads(self.out.read_text()), final)

    def test_invalid_interval_no_traversal(self):
        self.init()
        for start, end in [("2026-02-16", "2026-02-01"), ("2026-02-30", "2026-03-01"), ("20260201", "2026-02-15")]:
            self.run_job(2, start=start, end=end)
        self.assertEqual(self.api("describe")["remaining_calls"], 2)
        self.assertFalse(self.cp.exists())

    def test_empty_source(self):
        self.init([])
        self.run_job(0)
        result = json.loads(self.out.read_text())
        self.assertEqual((result["vendors"], result["examined_records"], result["pages_committed"]), ([], 0, 1))

    def test_no_matches_still_exhausts(self):
        self.init()
        result = self.finish(start="2027-01-01", end="2027-01-31")
        self.assertEqual((result["vendors"], result["examined_records"]), ([], 17))

    def test_large_integer_and_single_day(self):
        row = {"entry_id": "huge", "vendor_id": "v", "posted_on": "2026-02-15", "kind": "charge", "status": "settled", "amount_cents": 10**30, "currency": "USD"}
        self.init([row, dict(row, entry_id="credit", kind="credit", amount_cents=1)])
        self.run_job(0, start="2026-02-15", end="2026-02-15")
        self.assertEqual(json.loads(self.out.read_text())["vendors"][0]["net_cents"], 10**30 - 1)

    def test_lost_response(self):
        self.init()
        wrapper = self.path / "wrapper.py"
        wrapper.write_text("import subprocess,sys,pathlib\n" +
            f"r=subprocess.run([sys.executable, {str(API)!r}, *sys.argv[1:]],capture_output=True,text=True)\n" +
            f"flag=pathlib.Path({str(self.path / 'lost')!r})\n" +
            "if 'page' in sys.argv and r.returncode==0 and not flag.exists():\n flag.touch()\n print('lost response')\nelse:\n print(r.stdout,end='')\nsys.exit(r.returncode)\n")
        self.run_job(3, api=wrapper)
        self.assertEqual(self.api("describe")["remaining_calls"], 1)
        self.assertEqual(json.loads(self.cp.read_text())["pages_committed"], 0)
        self.assertEqual(self.run_job(75, api=wrapper)["examined_records"], 3)
        final = self.finish(api=wrapper)
        self.assertEqual((final["examined_records"], final["pages_committed"]), (17, 6))
        self.assertEqual(final["vendors"][0]["net_cents"], 12500)

    def test_failed_checkpoint_commit_replays_without_double_count(self):
        self.init()
        args = type("Args", (), dict(api=str(API), source=str(self.source), checkpoint=str(self.cp),
            output=str(self.out), start="2026-02-01", end="2026-02-15", tranche=1))()
        original = rollup.atomic_json
        def fail_page(path, value):
            if path == self.cp and value.get("pages_committed") == 1:
                raise OSError("simulated persistence failure before replace")
            return original(path, value)
        with patch.object(rollup, "atomic_json", fail_page), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(OSError):
                rollup.run(args)
        self.assertEqual(self.api("describe")["remaining_calls"], 1)
        self.assertEqual(json.loads(self.cp.read_text())["pages_committed"], 0)
        final = self.finish()
        self.assertEqual(final["examined_records"], 17)
        self.assertEqual(final["vendors"][0]["qualifying_entry_count"], 4)

    def test_request_identity_and_tranche_boundary(self):
        self.init()
        self.tranche = 2
        self.assertEqual(self.run_job(75)["reason"], "approved_tranche_not_current")
        self.assertEqual(self.api("describe")["remaining_calls"], 2)
        self.tranche = 1
        self.run_job(2, end="2026-02-14")
        self.assertEqual(self.api("describe")["remaining_calls"], 2)
        self.run_job(75)

    def test_page_contract_failures_do_not_advance(self):
        self.init()
        self.run_job(75)
        state = json.loads(self.cp.read_text())
        before = json.dumps(state, sort_keys=True)
        page = {"snapshot_id": state["snapshot_id"], "total_records": 17,
                "tranche": 2, "items": [], "next_cursor": None}
        with self.assertRaises(rollup.Failure):
            rollup.incorporate(state, page)  # Premature exhaustion.
        with self.assertRaises(rollup.Failure) as caught:
            rollup.incorporate(state, dict(page, snapshot_id="another_snapshot"))
        self.assertEqual(caught.exception.code, 4)
        row = json.loads(FIXTURE.read_text())["records"][0]
        with self.assertRaises(rollup.Failure):
            rollup.incorporate(state, dict(page, items=[row], next_cursor="opaque_new"))
        with self.assertRaises(rollup.Failure):
            rollup.incorporate(state, dict(page, items=[dict(row, entry_id="fresh", amount_cents=0.1)], next_cursor="opaque_new"))
        self.assertEqual(json.dumps(state, sort_keys=True), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
