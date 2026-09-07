#!/usr/bin/env python3
"""Verify supplied providers and native CLI, not target Skills or business answers.

All writable setup state is original synthetic data in a fresh temporary directory.
"""

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

CASES = Path(__file__).resolve().parents[1] / "main-cases"


class ProviderChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="main-system-provider-check-")
        self.work = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def command(self, case, state, *arguments, expected=0):
        program = CASES / case / ("ledger_api.py" if case == "S06" else "booking.py")
        result = subprocess.run(
            [sys.executable, str(program), "--state", str(state), *map(str, arguments)],
            capture_output=True, text=True, timeout=10,
        )
        if expected is not None:
            self.assertEqual(result.returncode, expected, (result.stdout, result.stderr))
        return result

    def invoke(self, case, state, *arguments, expected=0):
        return json.loads(self.command(case, state, *arguments, expected=expected).stdout)

    def initialize(self, case, filename="state.sqlite", fixture=None):
        state = self.work / filename
        self.invoke(case, state, "init", "--fixture", fixture or CASES / case / "fixture.json")
        return state

    def remaining(self, state, slot):
        slots = self.invoke("S08", state, "availability")["slots"]
        return next(row["remaining"] for row in slots if row["slot_id"] == slot)

    def reservation(self, key, slot="paper-lab-am", seats=1, party="crew-cedar"):
        return ("reserve", "--request-key", key, "--party-id", party,
                "--slot-id", slot, "--seats", str(seats))

    def test_ledger_budget_retry_and_full_provider_traversal(self):
        state = self.initialize("S06")
        meta = self.invoke("S06", state, "describe")
        self.assertEqual((meta["total_records"], meta["page_size"], meta["remaining_calls"]), (17, 3, 2))
        snapshot = meta["snapshot_id"]
        self.invoke("S06", state, "page", "--snapshot", "wrong", expected=4)
        self.invoke("S06", state, "page", "--snapshot", snapshot, "--cursor", "invalid", expected=2)
        self.assertEqual(self.invoke("S06", state, "describe")["remaining_calls"], 2)
        first = self.invoke("S06", state, "page", "--snapshot", snapshot)
        repeat = self.invoke("S06", state, "page", "--snapshot", snapshot)
        self.assertEqual(first, repeat)
        exhausted = self.invoke("S06", state, "page", "--snapshot", snapshot,
                                "--cursor", first["next_cursor"], expected=75)
        self.assertEqual(exhausted["error"], "call_budget_exhausted")
        self.assertNotIn("items", exhausted)
        observed = first["items"][:]
        following = first["next_cursor"]
        while following is not None:
            meta = self.invoke("S06", state, "describe")
            if not meta["remaining_calls"]:
                self.invoke("S06", state, "grant-tranche")  # Test operator, not target work.
            page = self.invoke("S06", state, "page", "--snapshot", snapshot, "--cursor", following)
            self.assertEqual(page["snapshot_id"], snapshot)
            observed.extend(page["items"])
            following = page["next_cursor"]
        supplied = json.loads((CASES / "S06" / "fixture.json").read_text())["records"]
        self.assertEqual(observed, supplied)  # Provider coverage only; no business rollup computed.
        self.assertEqual(len({row["entry_id"] for row in observed}), 17)

    def test_ledger_empty_snapshot_cursor_binding_and_no_overwrite(self):
        empty_fixture = self.work / "empty-original-ledger.json"
        empty_fixture.write_text('{"records": []}\n')
        empty = self.initialize("S06", "empty.sqlite", empty_fixture)
        meta = self.invoke("S06", empty, "describe")
        page = self.invoke("S06", empty, "page", "--snapshot", meta["snapshot_id"])
        self.assertEqual((page["items"], page["next_cursor"], page["total_records"]), ([], None, 0))
        populated = self.initialize("S06", "populated.sqlite")
        other_meta = self.invoke("S06", populated, "describe")
        other_page = self.invoke("S06", populated, "page", "--snapshot", other_meta["snapshot_id"])
        self.invoke("S06", empty, "page", "--snapshot", meta["snapshot_id"],
                    "--cursor", other_page["next_cursor"], expected=2)
        original = populated.read_bytes()
        self.invoke("S06", populated, "init", "--fixture", CASES / "S06" / "fixture.json", expected=2)
        self.assertEqual(populated.read_bytes(), original)
        missing = self.work / "missing-ledger.sqlite"
        self.invoke("S06", missing, "describe", expected=2)
        self.assertFalse(missing.exists())

    def test_native_sqlite_cli_and_setup_fixture(self):
        self.assertGreaterEqual(sys.version_info[:2], (3, 12))
        help_result = subprocess.run([sys.executable, "-m", "sqlite3", "--help"],
                                     capture_output=True, text=True, timeout=10)
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("An SQL query to execute", help_result.stdout)
        state = self.work / "queue.sqlite"
        setup = subprocess.run([sys.executable, "-m", "sqlite3", str(state)],
                               input=(CASES / "S07" / "queue_fixture.sql").read_text(),
                               capture_output=True, text=True, timeout=10)
        self.assertEqual(setup.returncode, 0, (setup.stdout, setup.stderr))
        self.assertNotIn("Error", setup.stderr)
        before = hashlib.sha256(state.read_bytes()).digest()
        probe = subprocess.run([sys.executable, "-m", "sqlite3", str(state),
                                "SELECT COUNT(*) FROM queue_items;"],
                               capture_output=True, text=True, timeout=10)
        self.assertEqual(probe.returncode, 0, probe.stderr)
        self.assertEqual(probe.stdout.strip(), "(12,)")
        self.assertEqual(hashlib.sha256(state.read_bytes()).digest(), before)
        # A separate arithmetic probe, not a queue-handoff query or expected answer.
        sql = """WITH samples(g, v) AS (VALUES ('b',10),('a',4),('a',7)),
            labels(g, label) AS (VALUES ('a','A'),('b','B'))
            SELECT label, COUNT(*), SUM(CASE WHEN v > 5 THEN 1 ELSE 0 END), SUM(v)
            FROM samples JOIN labels USING (g) WHERE v >= 4 GROUP BY g ORDER BY g;"""
        capabilities = subprocess.run([sys.executable, "-m", "sqlite3", ":memory:", sql],
                                      capture_output=True, text=True, timeout=10)
        self.assertEqual(capabilities.returncode, 0, capabilities.stderr)
        self.assertEqual(capabilities.stdout.splitlines(), ["('A', 2, 1, 11)", "('B', 1, 1, 10)"])

    def test_booking_unknown_outcome_on_both_sides_of_commit(self):
        state = self.initialize("S08")
        before_args = self.reservation("before-01", seats=2)
        before = self.command("S08", state, *before_args, "--fault", "before-commit", expected=75)
        self.assertEqual(before.stdout, "")
        self.assertEqual(self.invoke("S08", state, "lookup", "--request-key", "before-01")["state"], "not_seen")
        self.assertEqual(self.remaining(state, "paper-lab-am"), 6)
        recovered = self.invoke("S08", state, *before_args)
        self.assertEqual((recovered["state"], recovered["replayed"]), ("confirmed", False))
        replay = self.invoke("S08", state, *before_args)
        self.assertTrue(replay["replayed"])
        self.assertEqual(replay["booking_id"], recovered["booking_id"])
        self.assertEqual(self.remaining(state, "paper-lab-am"), 4)
        after_args = self.reservation("after-01", slot="paper-lab-pm", seats=2)
        after = self.command("S08", state, *after_args, "--fault", "after-commit", expected=75)
        self.assertEqual((after.stdout, after.stderr), ("", before.stderr))
        saved = self.invoke("S08", state, "lookup", "--request-key", "after-01")
        self.assertEqual(saved["state"], "confirmed")
        retried = self.invoke("S08", state, *after_args)
        self.assertTrue(retried["replayed"])
        self.assertEqual(retried["booking_id"], saved["booking_id"])
        self.assertEqual(self.remaining(state, "paper-lab-pm"), 2)
        # The fault control does not hide a previously saved identical receipt.
        still_saved = self.invoke("S08", state, *after_args, "--fault", "after-commit")
        self.assertTrue(still_saved["replayed"])

    def test_booking_conflicts_rejections_invalid_input_and_no_overwrite(self):
        state = self.initialize("S08")
        self.invoke("S08", state, *self.reservation("kept-01", seats=2))
        for changed in (self.reservation("kept-01", seats=3),
                        self.reservation("kept-01", seats=2, party="crew-elm"),
                        self.reservation("kept-01", seats=2, slot="paper-lab-pm")):
            conflict = self.invoke("S08", state, *changed, expected=3)
            self.assertEqual(conflict["error"], "idempotency_conflict")
        self.assertEqual(self.remaining(state, "paper-lab-am"), 4)
        for key, slot, seats, reason in (("missing-slot", "unknown", 1, "unknown_slot"),
                                          ("too-many", "paper-lab-am", 5, "insufficient_capacity")):
            args = self.reservation(key, slot=slot, seats=seats)
            receipt = self.invoke("S08", state, *args)
            self.assertEqual((receipt["state"], receipt["reason"]), ("rejected", reason))
            repeated = self.invoke("S08", state, *args)
            self.assertTrue(repeated["replayed"])
            self.assertEqual(repeated["reason"], reason)
        self.invoke("S08", state, *self.reservation("invalid-01", seats=0), expected=2)
        self.assertEqual(self.invoke("S08", state, "lookup", "--request-key", "invalid-01")["state"], "not_seen")
        self.assertEqual(self.remaining(state, "paper-lab-am"), 4)
        saved_bytes = state.read_bytes()
        self.invoke("S08", state, "init", "--fixture", CASES / "S08" / "fixture.json", expected=2)
        self.assertEqual(state.read_bytes(), saved_bytes)
        missing = self.work / "missing-bookings.sqlite"
        self.invoke("S08", missing, "availability", expected=2)
        self.assertFalse(missing.exists())

    def concurrent_attempts(self, state, requests):
        with ThreadPoolExecutor(max_workers=len(requests)) as executor:
            futures = [executor.submit(self.command, "S08", state, *args, expected=None) for args in requests]
            for future in futures:
                result = future.result()
                self.assertIn(result.returncode, (0, 75), (result.stdout, result.stderr))
        # Reconcile under original keys after all concurrent processes have ended.
        return [self.invoke("S08", state, *args) for args in requests]

    def test_booking_concurrent_distinct_keys_and_same_key(self):
        state = self.initialize("S08")
        requests = [self.reservation(f"last-seat-{index}", slot="press-demo") for index in range(6)]
        outcomes = self.concurrent_attempts(state, requests)
        self.assertEqual(sum(row["state"] == "confirmed" for row in outcomes), 1)
        self.assertEqual(sum(row["state"] == "rejected" for row in outcomes), 5)
        self.assertEqual(self.remaining(state, "press-demo"), 0)
        duplicate = self.reservation("same-request", seats=2)
        outcomes = self.concurrent_attempts(state, [duplicate] * 6)
        self.assertTrue(all(row["state"] == "confirmed" for row in outcomes))
        self.assertEqual(len({row["booking_id"] for row in outcomes}), 1)
        self.assertEqual(self.remaining(state, "paper-lab-am"), 4)

    def test_booking_lock_contention_is_recoverable(self):
        state = self.initialize("S08")
        args = self.reservation("held-lock-01")
        with sqlite3.connect(state) as lock_holder:
            lock_holder.execute("BEGIN IMMEDIATE")  # Original disposable setup condition only.
            result = self.command("S08", state, *args, expected=75)
            self.assertEqual(result.stdout, "")
            self.assertIn("outcome unavailable", result.stderr)
            self.assertEqual(self.invoke("S08", state, "lookup", "--request-key", "held-lock-01")["state"], "not_seen")
            lock_holder.rollback()
        recovered = self.invoke("S08", state, *args)
        self.assertEqual(recovered["state"], "confirmed")
        self.assertEqual(self.remaining(state, "paper-lab-am"), 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
