"""Disposable packaging checks, never a consumer run or a real grading packet."""

import ast
import csv
import hashlib
import json
import os
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
                         "state-snapshots/C-U073/final.sql", "state-snapshots/C-U074/final.sql",
                         "recovery/C-U092-request-hash-matched.json", recovery.REQUEST_PROVENANCE_PATH,
                         "audits/recovered-evidence-sufficiency-review.md"):
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

    def test_hash_matched_request_bytes_stay_distinct_from_missing_api_state(self):
        destination = self.write("C-U092")
        request = destination / "recovered-work-evidence/request-hash-matched.json"
        self.assertEqual(len(request.read_bytes()), 1454)
        self.assertEqual(recovery.sha_bytes(request.read_bytes()), "cf3b8effece5f3c1c9be5e405b5240a66d68d83c984a9795304481974fc486ee")
        self.assertEqual((destination / "recovered-work-evidence/checkpoint-rendering.json").read_bytes(), request.read_bytes() + b"\n")
        self.assertFalse((destination / "logical-state-supplement").exists())
        self.assertIn("Final API SQL and its historical captured digest are unavailable", (destination / "evidence-availability.md").read_text())
        (self.root / "recovery/C-U092-request-hash-matched.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "Preserved recovery evidence changed"):
            self.plan("C-U092")

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

    def test_actual_application_loop_packages_supplement_without_original_final_claims(self):
        node = next(node for node in ast.walk(ast.parse(Path(grading.__file__).read_text()))
                    if isinstance(node, ast.For) and isinstance(node.target, ast.Tuple)
                    and [item.id for item in node.target.elts] == ["variant", "use_id", "folder", "assignment", "recovered"])
        use_id = "C-U086"
        assignment = self.assignment(use_id)
        candidate = self.root / "disposable-packets/integrated/R17"
        mapping = {"R17": {"creator": assignment["creator_id"], "consumers": []}}
        environment = {**vars(grading), "ROOT": self.root, "candidate": candidate, "code": "R17", "mapping": mapping,
                       "excluded_caches": {}, "family": "S06", "applications": [
                           (assignment["variant"], use_id, self.root / "consumers" / use_id, assignment, self.plan(use_id))]}
        exec(compile(ast.Module(body=[node], type_ignores=[]), "actual-grading-application-loop", "exec"), environment)
        destination = candidate / assignment["variant"]
        self.assertEqual(mapping["R17"]["consumers"], [use_id])
        self.assertTrue((destination / "recovered-public-text/answer.md").is_file())
        self.assertFalse((destination / "observed-final-skill").exists())

    def test_noncanonical_destination_is_refused(self):
        destination = self.root / "unused" / ".." / "outside"
        with self.assertRaisesRegex(ValueError, "existing/partial"):
            recovery.write_application(self.root, self.plan(), destination, grading.copy_file)
        self.assertFalse((self.root / "outside").exists())


class CreatorRecoveryGradingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="alps-creator-recovery-grading-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "assessment"
        self.root.mkdir()
        companion = json.loads((SOURCE / recovery.CREATOR_COMPANION_PATH).read_text())
        paths = {recovery.CREATOR_COMPANION_PATH}
        paths.update(item["path"] for item in (*companion["evidence_reviews"], companion["rematerialization"], companion["common_display_recovery"]))
        self.packages = {}
        for creator_id, entry in companion["creators"].items():
            paths.update(item["path"] for item in (entry["relay"], entry["format_observation"], entry["freeze_manifest"], *entry["consumer_assignments"]))
            freeze = json.loads((SOURCE / entry["freeze_manifest"]["path"]).read_text())
            relative = Path("frozen/control-artifacts") / creator_id / Path(freeze["frozen_path"]).name
            paths.update(str(relative / name) for name in freeze["file_sha256"])
            paths.add(f"trials/{creator_id}/execution-note.md")
            paths.update(f"trials/{creator_id}/deliverables/skills/{relative.name}/{name}" for name in freeze["file_sha256"])
            self.packages[creator_id] = self.root / relative
        for relative in paths:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE / relative, target)

    def plan(self, creator_id="control-071"):
        return recovery.plan_creator(self.root, creator_id, self.packages[creator_id])

    def test_all_four_attach_only_the_candidates_recovery_evidence(self):
        for creator_id in recovery.RECOVERED_CREATORS:
            with self.subTest(creator=creator_id):
                plan = self.plan(creator_id)
                destination = self.root / "disposable-packets" / creator_id
                recovery.write_creator(self.root, plan, destination, grading.copy_file)
                names = {path.name for path in destination.iterdir()}
                self.assertEqual(names, {"source-relay.md", "format-observation.json", "creator-recovery-provenance.json", "README.md"})
                provenance = json.loads((destination / "creator-recovery-provenance.json").read_text())
                self.assertNotIn("creators", provenance)
                self.assertEqual(provenance["creator"]["frozen_resource_sha256"], recovery.file_hashes(self.packages[creator_id]))
                self.assertTrue(all(item["destination_path"].startswith(f"trials/{creator_id}/") for item in provenance["this_creator_rematerialized_files"]))
                self.assertIn("lost original coordinator format report", (destination / "README.md").read_text())
                self.assertEqual(json.loads((destination / "format-observation.json").read_text())["trial"], creator_id)
                for outside in recovery.RECOVERED_CREATORS - {creator_id}:
                    self.assertNotIn(outside, json.dumps(provenance))
                self.assertNotIn("requested_model", json.dumps(provenance))
                self.assertNotIn("requested_effort", json.dumps(provenance))

    def test_non_recovered_creator_does_not_require_a_companion(self):
        (self.root / recovery.CREATOR_COMPANION_PATH).unlink()
        self.assertIsNone(recovery.plan_creator(self.root, "control-068", self.root / "unused"))
        with self.assertRaises(FileNotFoundError):
            self.plan()

    def test_missing_review_or_changed_consumer_assignment_blocks_new_freeze_attachment(self):
        review = self.root / "audits/recovered-evidence-sufficiency-review.md"
        original = review.read_bytes()
        review.unlink()
        with self.assertRaises(FileNotFoundError):
            self.plan()
        review.write_bytes(original)
        (self.root / "consumer-assignments/C-U141.json").write_text("{}\n")
        with self.assertRaisesRegex(ValueError, "Preserved recovery evidence changed"):
            self.plan()

    def test_changed_frozen_resource_or_mode_is_rejected(self):
        resource = self.packages["control-071"] / "SKILL.md"
        original = resource.read_bytes()
        resource.write_bytes(original + b"changed\n")
        with self.assertRaisesRegex(ValueError, "freeze/resource identity differs"):
            self.plan()
        resource.write_bytes(original)
        resource.chmod(0o600)
        with self.assertRaisesRegex(ValueError, "freeze/resource identity differs"):
            self.plan()

    def canonical(self, creator_id):
        return self.root / "trials" / creator_id / "deliverables"

    def test_both_note_provenance_paths_reject_changed_missing_or_wrong_mode_notes(self):
        for creator_id in ("control-069", "control-071"):
            with self.subTest(creator=creator_id):
                note = self.root / "trials" / creator_id / "execution-note.md"
                original = note.read_bytes()
                note.write_text("UNREVIEWED REPLACEMENT CREATOR NOTE\n")
                with self.assertRaisesRegex(ValueError, "Preserved recovery evidence changed"):
                    self.plan(creator_id)
                note.unlink()
                with self.assertRaisesRegex(ValueError, "public note must be a regular file"):
                    self.plan(creator_id)
                note.write_bytes(original)
                note.chmod(0o600)
                with self.assertRaisesRegex(ValueError, "public-note mode differs"):
                    self.plan(creator_id)
                note.chmod(0o644)

    def test_both_provenance_paths_reject_unknown_files_directories_and_nonregular_entries(self):
        for creator_id in ("control-069", "control-071"):
            with self.subTest(creator=creator_id):
                folder = self.canonical(creator_id)
                extra = folder / "unreviewed-summary.md"
                extra.write_text("SYNTHETIC OTHER-GRADE/MODEL-MAPPING SENTINEL\n")
                with self.assertRaisesRegex(ValueError, "Closed recovered creator resource inventory"):
                    self.plan(creator_id)
                extra.unlink()
                extra.mkdir()
                with self.assertRaisesRegex(ValueError, "Unknown or missing recovered creator deliverable directory"):
                    self.plan(creator_id)
                extra.rmdir()
                os.mkfifo(extra)
                with self.assertRaisesRegex(ValueError, "Unsupported filesystem entry"):
                    self.plan(creator_id)
                extra.unlink()
                extra.symlink_to(folder / "skills")
                with self.assertRaisesRegex(ValueError, "symlink"):
                    self.plan(creator_id)
                extra.unlink()

    def test_both_provenance_paths_reject_missing_changed_and_wrong_mode_canonical_resources(self):
        for creator_id in ("control-069", "control-071"):
            with self.subTest(creator=creator_id):
                resource = self.canonical(creator_id) / "skills" / self.packages[creator_id].name / "SKILL.md"
                original = resource.read_bytes()
                resource.unlink()
                with self.assertRaisesRegex(ValueError, "Closed recovered creator resource inventory"):
                    self.plan(creator_id)
                resource.write_bytes(original + b"changed\n")
                with self.assertRaisesRegex(ValueError, "Closed recovered creator resource inventory"):
                    self.plan(creator_id)
                resource.write_bytes(original)
                resource.chmod(0o600)
                with self.assertRaisesRegex(ValueError, "Closed recovered creator resource modes"):
                    self.plan(creator_id)
                resource.chmod(0o644)

    def test_complete_candidate_copy_keeps_reviewed_note_package_and_provenance_together(self):
        for creator_id in recovery.RECOVERED_CREATORS:
            with self.subTest(creator=creator_id):
                plan = self.plan(creator_id)
                destination = self.root / "disposable-candidates" / creator_id
                recovery.write_creator_candidate(self.root, plan, destination, grading.copy_file)
                for item in plan["candidate_files"]:
                    copied = destination / item["destination"]
                    self.assertEqual(recovery.sha_bytes(copied.read_bytes()), item["sha256"])
                    self.assertEqual(copied.stat().st_mode & 0o777, item["observed_copy_source_mode"])
                self.assertTrue((destination / "recovery-provenance/creator-recovery-provenance.json").is_file())
                self.assertFalse((destination / "other-creator-deliverables").exists())

    def test_post_plan_note_resource_mode_and_extra_file_changes_block_copy(self):
        for creator_id in ("control-069", "control-071"):
            folder = self.canonical(creator_id)
            note = folder.parent / "execution-note.md"
            resource = folder / "skills" / self.packages[creator_id].name / "SKILL.md"
            for changed in (note, resource):
                with self.subTest(creator=creator_id, path=changed.name):
                    plan = self.plan(creator_id)
                    original = changed.read_bytes()
                    changed.write_bytes(original + b"changed after plan\n")
                    destination = self.root / "disposable-candidates" / creator_id
                    with self.assertRaises(ValueError):
                        recovery.write_creator_candidate(self.root, plan, destination, grading.copy_file)
                    self.assertFalse(destination.exists())
                    changed.write_bytes(original)
                    changed.chmod(0o600)
                    with self.assertRaises(ValueError):
                        recovery.write_creator_candidate(self.root, plan, destination, grading.copy_file)
                    self.assertFalse(destination.exists())
                    changed.chmod(0o644)
            plan = self.plan(creator_id)
            extra = folder / "after-plan.md"
            extra.write_text("new unreviewed evidence\n")
            with self.assertRaisesRegex(ValueError, "Closed recovered creator resource inventory"):
                recovery.write_creator_candidate(self.root, plan, self.root / "disposable-candidates" / creator_id, grading.copy_file)
            extra.unlink()

    def test_mutation_during_copy_retains_partial_candidate_and_refuses_replacement(self):
        for creator_id in ("control-069", "control-071"):
            with self.subTest(creator=creator_id):
                plan = self.plan(creator_id)
                extra = self.canonical(creator_id) / "injected-after-note.md"
                destination = self.root / "disposable-candidates" / creator_id

                def inject_extra(original, target):
                    grading.copy_file(original, target)
                    if target.name == "creator-reported-checks.md":
                        extra.write_text("unreviewed mid-copy evidence\n")

                with self.assertRaisesRegex(ValueError, "Closed recovered creator resource inventory"):
                    recovery.write_creator_candidate(self.root, plan, destination, inject_extra)
                self.assertTrue((destination / "creator-reported-checks.md").is_file())
                self.assertFalse((destination / "recovery-provenance").exists())
                extra.unlink()
                with self.assertRaisesRegex(ValueError, "existing/partial recovered creator candidate"):
                    recovery.write_creator_candidate(self.root, plan, destination, grading.copy_file)

    def test_permitted_runtime_cache_is_recorded_excluded_and_bound_after_planning(self):
        folder = self.canonical("control-071") / "__pycache__"
        folder.mkdir()
        cache = folder / "fixture.cpython-312.pyc"
        cache.write_bytes(b"disposable runtime cache bytes")
        plan = self.plan()
        observation = plan["provenance"]["excluded_canonical_runtime_caches"]
        self.assertEqual(observation["__pycache__/fixture.cpython-312.pyc"]["sha256"], recovery.sha_bytes(cache.read_bytes()))
        destination = self.root / "disposable-candidates/with-cache"
        recovery.write_creator_candidate(self.root, plan, destination, grading.copy_file)
        self.assertEqual(list(destination.rglob("*.pyc")), [])
        cache.write_bytes(b"changed after plan")
        with self.assertRaisesRegex(ValueError, "changed after planning"):
            recovery.write_creator_candidate(self.root, plan, self.root / "disposable-candidates/changed-cache", grading.copy_file)
        (folder / "not-cache.md").write_text("unreviewed\n")
        with self.assertRaisesRegex(ValueError, "non-cache resource"):
            self.plan()

    def test_selected_note_and_frozen_file_bytes_or_modes_are_rechecked_during_copy(self):
        for creator_id in ("control-069", "control-071"):
            for mutation in ("note-bytes", "frozen-bytes", "frozen-mode"):
                with self.subTest(creator=creator_id, mutation=mutation):
                    plan = self.plan(creator_id)
                    changed = (self.canonical(creator_id).parent / "execution-note.md" if mutation == "note-bytes"
                               else self.packages[creator_id] / "SKILL.md")
                    original = changed.read_bytes()
                    original_mode = changed.stat().st_mode & 0o777
                    destination = self.root / "disposable-candidates" / f"{creator_id}-{mutation}"

                    def inject_change(source, target):
                        grading.copy_file(source, target)
                        if target.name == "creator-reported-checks.md":
                            if mutation == "frozen-mode":
                                changed.chmod(0o600)
                            else:
                                changed.write_bytes(original + b"mid-copy change\n")

                    try:
                        with self.assertRaises(ValueError):
                            recovery.write_creator_candidate(self.root, plan, destination, inject_change)
                        self.assertTrue((destination / "creator-reported-checks.md").is_file())
                        self.assertFalse((destination / "recovery-provenance").exists())
                    finally:
                        changed.write_bytes(original)
                        changed.chmod(original_mode)

    def test_actual_creator_copy_loop_cannot_admit_changed_note_or_extra_deliverable(self):
        loop = next(node for node in ast.walk(ast.parse(Path(grading.__file__).read_text()))
                    if isinstance(node, ast.For) and isinstance(node.target, ast.Tuple)
                    and [getattr(item, "id", None) for item in node.target.elts] == ["code", "creator_id", "package", "applications"])
        for creator_id in ("control-069", "control-071"):
            plan = self.plan(creator_id)
            note = self.canonical(creator_id).parent / "execution-note.md"
            original = note.read_bytes()
            for mutation in ("note", "extra"):
                with self.subTest(creator=creator_id, mutation=mutation):
                    extra = self.canonical(creator_id) / "unreviewed-summary.md"
                    if mutation == "note":
                        note.write_text("UNREVIEWED REPLACEMENT CREATOR NOTE\n")
                    else:
                        extra.write_text("SYNTHETIC OTHER-GRADE/MODEL-MAPPING SENTINEL\n")
                    target = self.root / "disposable-copy-loop" / f"{creator_id}-{mutation}"
                    environment = {**vars(grading), "ROOT": self.root, "target": target,
                                   "creator_recoveries": {creator_id: plan}, "mapping": {}, "excluded_caches": {},
                                   "plans": [("R17", creator_id, self.packages[creator_id], [])]}
                    with self.assertRaises(ValueError):
                        exec(compile(ast.Module(body=[loop], type_ignores=[]), "actual-creator-copy-loop", "exec"), environment)
                    self.assertFalse(target.exists())
                    note.write_bytes(original)
                    if extra.exists():
                        extra.unlink()


if __name__ == "__main__":
    unittest.main()
