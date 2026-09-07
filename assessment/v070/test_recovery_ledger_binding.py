"""Disposable recovery component checks; no original business state is operated."""

import csv
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import control_ledger_state
import prepare_control_consumers
import prepare_control_grading
import recovery_ledger_binding as recovery

SOURCE = Path(__file__).resolve().parent


class RecoveryBindingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="alps-recovery-binding-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "assessment"
        self.root.mkdir()
        for consumer_id in recovery.ASSIGNMENT_SHA256:
            assignment = json.loads((SOURCE / "consumer-assignments" / f"{consumer_id}.json").read_text())
            relatives = {f"consumer-assignments/{consumer_id}.json", f"consumers/{consumer_id}/prompt.md",
                         *assignment["initial_state_evidence_sha256"],
                         *(f"consumers/{consumer_id}/{p}" for p in assignment["copied_sha256"]),
                         f"control-consumer-cases/S06/{assignment['variant']}/fixture.json"}
            for relative in relatives:
                target = self.root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(SOURCE / relative, target)
        shutil.copy2(SOURCE / "control-consumer-list.tsv", self.root / "control-consumer-list.tsv")
        # The fixture ledger copy remains a prepared assignment regardless of
        # later real progress; this is never written back to the assessment.
        for consumer_id in recovery.ASSIGNMENT_SHA256:
            self.set_status(consumer_id, "prepared")
        self.originals = self.file_hashes()

    def file_hashes(self):
        return {str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in self.root.rglob("*") if path.is_file()}

    def assert_originals_unchanged(self):
        current = self.file_hashes()
        self.assertTrue(all(current.get(path) == digest for path, digest in self.originals.items()))

    def set_status(self, consumer_id, execution):
        path = self.root / "control-consumer-list.tsv"
        with path.open(newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            fields, rows = reader.fieldnames, list(reader)
        for row in rows:
            if row["consumer_id"] == consumer_id:
                row["execution"] = execution
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)

    def directory(self, consumer_id="C-U094", suffix="test"):
        return self.root.parent / f"{consumer_id}-ledger-recovery-{suffix}"

    def restore(self, consumer_id="C-U094"):
        return recovery.restore(self.root, consumer_id, self.directory(consumer_id))

    def setup_record(self, consumer_id="C-U094"):
        return json.loads((self.root / "consumer-setup" / f"{consumer_id}.json").read_text())

    def test_three_assignments_restore_exact_unused_state_without_changing_originals(self):
        for consumer_id in recovery.ASSIGNMENT_SHA256:
            with self.subTest(consumer=consumer_id):
                binding = self.restore(consumer_id)
                state = Path(binding["restored_state_path"])
                self.assertNotEqual(str(state), binding["original_state_path"])
                with sqlite3.connect(state.as_uri() + "?mode=ro", uri=True) as connection:
                    sql = "\n".join(connection.iterdump()) + "\n"
                    self.assertEqual(connection.execute("SELECT tranche, calls_used FROM source_state").fetchall(), [(1, 0)])
                original = self.root / "state-snapshots" / consumer_id / "initial.sql"
                self.assertEqual(sql, original.read_text())
                self.assertEqual(binding["restored_binary_sha256"], recovery.digest(state))
                self.assertEqual(state.stat().st_mode & 0o777, 0o600)
                self.assertEqual(binding["initial_state_observation"]["remaining_calls"], 2)
        self.assert_originals_unchanged()

    def test_rejects_other_or_completed_assignment_before_creating_state(self):
        with self.assertRaisesRegex(ValueError, "preserved recovery assignment"):
            recovery.restore(self.root, "C-U093", self.directory("C-U093"))
        self.set_status("C-U094", "completed")
        with self.assertRaisesRegex(ValueError, "still-prepared"):
            self.restore()
        self.assertFalse(self.directory().exists())

    def test_changed_assignment_and_source_hashes_are_not_reanchored(self):
        assignment_path = self.root / "consumer-assignments/C-U094.json"
        original = assignment_path.read_bytes()
        assignment_path.write_bytes(original + b"\n")
        with self.assertRaisesRegex(ValueError, "preserved recovery assignment"):
            self.restore()
        assignment_path.write_bytes(original)
        initial = self.root / "state-snapshots/C-U094/initial.sql"
        initial.write_text(initial.read_text().replace(",1,0);", ",1,1);"))
        with self.assertRaisesRegex(ValueError, "anchored initial evidence changed"):
            self.restore()
        self.assertFalse(self.directory().exists())

    def test_initial_state_requires_unused_quota_and_correct_snapshot(self):
        sql = (self.root / "state-snapshots/C-U094/initial.sql").read_text()
        records = json.loads((self.root / "control-consumer-cases/S06/challenging/fixture.json").read_text())["records"]
        for replacement in (",1,1);", ",2,0);"):
            altered = sql.replace(",1,0);", replacement)
            with sqlite3.connect(":memory:") as connection:
                connection.executescript(altered)
                with self.assertRaisesRegex(ValueError, "snapshot, first tranche or unused quota"):
                    recovery.inspect_initial(connection, altered, records)
        altered = sql.replace("snap_fb322d1120ca406ad668bc26", "snap_wrong")
        with sqlite3.connect(":memory:") as connection:
            connection.executescript(altered)
            with self.assertRaisesRegex(ValueError, "snapshot, first tranche or unused quota"):
                recovery.inspect_initial(connection, altered, records)

    def test_changed_prompt_or_application_evidence_blocks_restoration(self):
        prompt = self.root / "consumers/C-U094/prompt.md"
        original = prompt.read_bytes()
        prompt.write_bytes(original + b"changed\n")
        with self.assertRaisesRegex(ValueError, "consumer prompt changed"):
            self.restore()
        prompt.write_bytes(original)
        (prompt.parent / "execution-note.md").write_text("Existing execution observation\n")
        with self.assertRaisesRegex(ValueError, "existing application evidence"):
            self.restore()
        self.assertFalse(self.directory().exists())

    def test_existing_directory_and_partial_recovery_are_preserved(self):
        directory = self.directory()
        directory.mkdir()
        (directory / "partial.txt").write_text("retain\n")
        for destination in (directory, self.directory(suffix="different")):
            with self.assertRaisesRegex(ValueError, "existing or partial"):
                recovery.restore(self.root, "C-U094", destination)
        self.assertEqual((directory / "partial.txt").read_text(), "retain\n")
        self.assertFalse(self.directory(suffix="different").exists())

    def test_symlink_and_wrong_consumer_destination_refused(self):
        actual = self.root.parent / "elsewhere"
        actual.mkdir()
        self.directory().symlink_to(actual, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.restore()
        with self.assertRaisesRegex(ValueError, "consumer-specific"):
            recovery.restore(self.root, "C-U094", self.directory("C-U095"))
        self.assertEqual(list(actual.iterdir()), [])

    def test_final_snapshot_and_offline_grading_preserve_both_identities(self):
        binding = self.restore()
        state = Path(binding["restored_state_path"])
        # A disposable component fixture represents a changed final quota.
        # This is neither a business API call nor a recorded consumer run.
        with sqlite3.connect(state) as connection:
            connection.execute("UPDATE source_state SET calls_used = 2")
        with patch.object(control_ledger_state, "ROOT", self.root):
            final = control_ledger_state.snapshot("C-U094", "final")
        self.assertEqual(final["state_path"], str(state))
        self.assertEqual(final["original_state_path"], binding["original_state_path"])
        self.assertEqual(final["recovery_binding_sha256"], recovery.digest(recovery.record_path(self.root, "C-U094")))
        setup = self.setup_record()
        initial = json.loads((self.root / "state-snapshots/C-U094/initial.json").read_text())
        for label, metadata in (("initial", initial), ("final", final)):
            prepare_control_grading.validate_snapshot_identity(self.root, "C-U094", setup, label, metadata)
        for key in ("state_path", "original_state_path", "recovery_binding_sha256"):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "binding differs"):
                prepare_control_grading.validate_snapshot_identity(self.root, "C-U094", setup, "final", {**final, key: "wrong"})
        copied = self.root / "disposable-grading-packet/recovery-binding.json"
        with patch.object(prepare_control_consumers, "ROOT", self.root):
            prepare_control_grading.copy_file(recovery.record_path(self.root, "C-U094"), copied)
        self.assertEqual(recovery.digest(copied), final["recovery_binding_sha256"])
        state.unlink()
        prepare_control_grading.validate_snapshot_identity(self.root, "C-U094", setup, "final", final)
        self.assert_originals_unchanged()

    def test_missing_or_cross_consumer_binding_cannot_validate_recovered_final(self):
        binding = self.restore()
        path = recovery.record_path(self.root, "C-U094")
        setup = self.setup_record()
        metadata = recovery.snapshot_identity(self.root, "C-U094", setup, "final")
        path.unlink()
        with self.assertRaisesRegex(ValueError, "binding differs"):
            recovery.validate_snapshot_identity(self.root, "C-U094", setup, "final", metadata)
        binding["restored_state_path"] = str(self.directory("C-U095") / "ledger.sqlite")
        path.write_text(json.dumps(binding))
        with self.assertRaisesRegex(ValueError, "consumer-specific"):
            recovery.validate_snapshot_identity(self.root, "C-U094", setup, "final", metadata)

    def test_failed_native_restore_is_preserved_and_cannot_be_restarted(self):
        inspect = recovery.inspect_initial
        calls = 0

        def fail_native(*args):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise ValueError("Injected disposable native validation failure")
            return inspect(*args)

        with patch.object(recovery, "inspect_initial", side_effect=fail_native):
            with self.assertRaisesRegex(ValueError, "Injected disposable"):
                self.restore()
        self.assertTrue((self.directory() / "ledger.sqlite").is_file())
        self.assertFalse(recovery.record_path(self.root, "C-U094").exists())
        with self.assertRaisesRegex(ValueError, "existing or partial"):
            recovery.restore(self.root, "C-U094", self.directory(suffix="second"))
        self.assert_originals_unchanged()

    def test_unrecovered_snapshot_binding_keeps_original_behavior(self):
        setup = {"state_path": "/unused/original/ledger.sqlite"}
        metadata = recovery.snapshot_identity(self.root, "C-U073", setup, "final")
        self.assertEqual(metadata, setup)
        recovery.validate_snapshot_identity(self.root, "C-U073", setup, "final", metadata)
        with self.assertRaisesRegex(ValueError, "binding differs"):
            recovery.validate_snapshot_identity(self.root, "C-U073", setup, "final", {**metadata, "original_state_path": "fabricated"})


if __name__ == "__main__":
    unittest.main()
