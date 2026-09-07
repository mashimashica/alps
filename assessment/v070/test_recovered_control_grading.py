"""Disposable packaging checks, never a consumer run or a real grading packet."""

import csv
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import prepare_control_grading as grading
import recovered_control_grading as recovery

SOURCE = Path(__file__).resolve().parent


class RecoveredGradingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="alps-recovered-grading-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "assessment"
        self.root.mkdir()
        for relative in ("control-consumer-list.tsv", "RECOVERY-ENVIRONMENT-OFFLINE.md",
                         "state-snapshots/C-U073/final.sql", "state-snapshots/C-U074/final.sql"):
            self.copy(relative)
        shutil.copytree(SOURCE / "recovery/consumer-evidence", self.root / "recovery/consumer-evidence")
        for consumer_id in recovery.ASSIGNMENT_SHA256:
            self.copy(f"consumer-assignments/{consumer_id}.json")
            self.copy(f"consumer-setup/{consumer_id}.json")
            self.copy(f"recovery/control-use-{consumer_id[-3:]}-relay.md")
            for label in ("initial.sql", "initial.json"):
                self.copy(f"state-snapshots/{consumer_id}/{label}")
            shutil.copytree(SOURCE / "consumers" / consumer_id, self.root / "consumers" / consumer_id)
        self.initial_hashes = self.hashes(self.root)

    def copy(self, relative):
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE / relative, target)

    def hashes(self, folder):
        return {str(path.relative_to(folder)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in folder.rglob("*") if path.is_file()}

    def assignment(self, consumer_id):
        return json.loads((self.root / "consumer-assignments" / f"{consumer_id}.json").read_text())

    def plan(self, consumer_id="C-U086"):
        return recovery.plan_application(self.root, consumer_id, self.assignment(consumer_id))

    def write(self, consumer_id="C-U086"):
        destination = self.root / "disposable-packets" / consumer_id
        recovery.write_application(self.root, self.plan(consumer_id), destination, grading.copy_file)
        return destination

    def test_all_ten_packets_keep_prepared_original_recovered_and_missing_evidence_distinct(self):
        for consumer_id in recovery.ASSIGNMENT_SHA256:
            with self.subTest(consumer=consumer_id):
                destination = self.write(consumer_id)
                self.assertTrue((destination / "prepared-input/request.md").is_file())
                self.assertTrue((destination / "prepared-skill").is_dir())
                for forbidden in ("observed-final-skill", "final-input-state", "resource-observations.json", "committed-state"):
                    self.assertFalse((destination / forbidden).exists())
                self.assertEqual(list(destination.rglob("final.json")), [])
                self.assertTrue((destination / "committed-initial-state/initial.json").is_file())
                original = consumer_id in recovery.ORIGINAL_OBSERVATIONS
                public = "original-public-observations" if original else "recovered-public-text"
                for name in ("answer.md", "execution-note.md"):
                    self.assertTrue((destination / public / name).is_file())
                self.assertEqual((destination / "original-work-evidence").is_dir(), original)
                self.assertEqual((destination / "recovered-work-evidence/checkpoint-rendering.json").is_file(),
                                 consumer_id not in {"C-U084", "C-U085", "C-U093"})
                self.assertEqual((destination / "logical-state-supplement/matched-final-state.sql").is_file(), consumer_id != "C-U092")
                provenance = json.loads((destination / "recovery-provenance.json").read_text())
                self.assertTrue(all(item["consumer_id"] == consumer_id for item in provenance["source_entries"]))
                self.assertNotIn("requested_model", provenance)
                self.assertNotIn("requested_effort", provenance)
                for item in provenance["files"]:
                    copied = destination / item["destination"]
                    self.assertEqual(recovery.sha_bytes(copied.read_bytes()), item["sha256"])
                    self.assertEqual(copied.stat().st_mode & 0o777, item["observed_copy_source_mode"])
                history = (destination / "recovery-provenance/historical-state-observations.md").read_text()
                self.assertNotIn("It grades seven applications", history)
                self.assertNotIn("B1, B2", history)
                self.assertNotIn("grading-work/", history)
        current = self.hashes(self.root)
        self.assertTrue(all(current[path] == digest for path, digest in self.initial_hashes.items()))

    def test_missing_checkpoint_rendering_blocks_instead_of_silently_dropping_it(self):
        (self.root / "recovery/consumer-evidence/C-U091/checkpoint-rendering.json").unlink()
        with self.assertRaisesRegex(ValueError, "Missing, changed or unknown"):
            self.plan("C-U091")

    def test_changed_or_added_supplement_is_rejected(self):
        path = self.root / "recovery/consumer-evidence/C-U086/answer.md"
        original = path.read_bytes()
        path.write_bytes(original + b"invented\n")
        with self.assertRaisesRegex(ValueError, "Missing, changed or unknown"):
            self.plan()
        path.write_bytes(original)
        (path.parent / "final.json").write_text("{}\n")
        with self.assertRaisesRegex(ValueError, "Missing, changed or unknown"):
            self.plan()

    def test_changed_manifest_cannot_reanchor_new_evidence(self):
        path = self.root / recovery.MANIFEST_PATH
        value = json.loads(path.read_text())
        value["files"][0]["consumer_id"] = "C-U094"
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, "Preserved recovery evidence changed"):
            self.plan()

    def test_relay_and_committed_matching_sql_source_are_required(self):
        path = self.root / "recovery/control-use-086-relay.md"
        original = path.read_bytes()
        path.write_bytes(original + b"modified\n")
        with self.assertRaisesRegex(ValueError, "Preserved recovery evidence changed"):
            self.plan()
        path.write_bytes(original)
        (self.root / "state-snapshots/C-U073/final.sql").write_text("not the committed source\n")
        with self.assertRaisesRegex(ValueError, "Preserved recovery evidence changed"):
            self.plan()

    def test_surviving_original_answer_mismatch_does_not_fall_back_to_relay(self):
        (self.root / "consumers/C-U084/answer.md").write_text("changed original\n")
        with self.assertRaisesRegex(ValueError, "surviving original observations differ"):
            self.plan("C-U084")

    def test_prepared_resource_mode_and_content_remain_anchored(self):
        path = self.root / "consumers/C-U086/input/request.md"
        path.chmod(0o600)
        with self.assertRaisesRegex(ValueError, "Original resource mode differs"):
            self.plan()
        path.chmod(0o644)
        path.write_text("changed task\n")
        with self.assertRaisesRegex(ValueError, "Prepared resources"):
            self.plan()

    def test_unexpected_original_final_metadata_or_replacement_answer_requires_reconciliation(self):
        path = self.root / "state-snapshots/C-U086/final.json"
        path.write_text("{}\n")
        with self.assertRaisesRegex(ValueError, "Unexpected original final"):
            self.plan()
        path.unlink()
        (self.root / "consumers/C-U086/answer.md").write_text("newly invented original\n")
        with self.assertRaisesRegex(ValueError, "surviving original observations differ"):
            self.plan()

    def test_rejects_unknown_identity_or_noncompleted_original(self):
        with self.assertRaisesRegex(ValueError, "limited to original completed"):
            recovery.plan_application(self.root, "C-U094", {})
        path = self.root / "control-consumer-list.tsv"
        with path.open(newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            fields, rows = reader.fieldnames, list(reader)
        for row in rows:
            if row["consumer_id"] == "C-U086":
                row["execution"] = "prepared"
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)
        with self.assertRaisesRegex(ValueError, "explicitly completed"):
            self.plan()

    def test_changed_source_after_preflight_leaves_explicit_partial_packet(self):
        plan = self.plan()
        changed = self.root / plan["files"][0]["source"]
        changed.write_bytes(changed.read_bytes() + b"changed\n")
        target = self.root / "disposable-packets/interrupted"
        with self.assertRaisesRegex(ValueError, "Preserved recovery evidence changed"):
            recovery.write_application(self.root, plan, target, grading.copy_file)
        self.assertTrue(target.is_dir())
        with self.assertRaisesRegex(ValueError, "existing/partial"):
            recovery.write_application(self.root, plan, target, grading.copy_file)

    def test_historical_excerpt_changes_are_not_silently_accepted(self):
        path = self.root / "RECOVERY-ENVIRONMENT-OFFLINE.md"
        path.write_text(path.read_text().replace("Actual final native API SQL was captured locally", "Actual final native API SQL was captured locally WRONG"))
        with self.assertRaisesRegex(ValueError, "Historical captured-state"):
            self.plan()

    def test_symlink_source_is_rejected_and_no_packet_created(self):
        path = self.root / "recovery/consumer-evidence/C-U086/answer.md"
        original = self.root / "elsewhere.md"
        path.rename(original)
        path.symlink_to(original)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.plan()
        self.assertFalse((self.root / "disposable-packets").exists())


if __name__ == "__main__":
    unittest.main()
