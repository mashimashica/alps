"""Restore the three interrupted S06 initial states at exclusive new paths.

Assessment recovery only. The original assignments, requests and observations
remain unchanged. This does not run the business API or replace an attempt.
"""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import stat

ROOT = Path(__file__).resolve().parent
# Exact assignments preserved at evidence commit 75c0ea9. No other consumer is
# eligible for this one-time restoration of an unstarted logical state.
ASSIGNMENT_SHA256 = {
    "C-U094": "b2f7ff3927349317b1530a8bf60ce8104a598f8126232fef8b722d8476e680da",
    "C-U095": "d9e3317c51a2d27f5b996a50f6eb68b28a4fd777d03cef2dcc00bcf62e4f5554",
    "C-U096": "b15900cd1edc6db475aedc5ea7b3dd3211ff22d68a0af781cf7cc262cf833ec4",
}
RECOVERY_FIELDS = ("original_state_path", "recovery_binding_path", "recovery_binding_sha256")


def checked(path):
    if not path.is_absolute() or path.resolve() != path:
        raise ValueError(f"Noncanonical path or symlink: {path}")
    return path


def digest(path):
    return hashlib.sha256(checked(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(checked(path).read_text(encoding="utf-8"))


def record_path(root, consumer_id):
    if not re.fullmatch(r"C-U\d{3}", consumer_id):
        raise ValueError("Explicit C consumer identity required")
    return checked(root / "recovery-bindings" / f"{consumer_id}.json")


def restored_path(root, consumer_id, directory):
    checked(directory)
    if (directory.parent != root.parent or
            not re.fullmatch(re.escape(consumer_id) + r"-ledger-recovery-[a-z0-9-]+", directory.name)):
        raise ValueError("Use a new consumer-specific recovery directory beside the assessment")
    return directory / "ledger.sqlite"


def inspect_initial(connection, sql, records):
    if connection.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
        raise ValueError("Restored native integrity check failed")
    if "\n".join(connection.iterdump()) + "\n" != sql:
        raise ValueError("Restored native dump differs from the anchored initial SQL")
    canonical = json.dumps(records, sort_keys=True, separators=(",", ":"))
    snapshot_id = "snap_" + hashlib.sha256(canonical.encode()).hexdigest()[:24]
    rows = [(i, json.dumps(value, sort_keys=True, separators=(",", ":")))
            for i, value in enumerate(records)]
    if connection.execute("SELECT position, payload FROM records ORDER BY position").fetchall() != rows:
        raise ValueError("Prescribed source records differ")
    if connection.execute("SELECT singleton, snapshot_id, tranche, calls_used FROM source_state").fetchall() != [
            (1, snapshot_id, 1, 0)]:
        raise ValueError("Prescribed snapshot, first tranche or unused quota differs")
    return {"snapshot_id": snapshot_id, "total_records": len(records), "page_size": 3,
            "calls_per_tranche": 2, "tranche": 1, "calls_used": 0, "remaining_calls": 2,
            "records_sha256": hashlib.sha256(canonical.encode()).hexdigest()}


def source_evidence(root, consumer_id):
    """Check the immutable assignment chain, without touching any native source."""
    checked(root)
    assignment_path = root / "consumer-assignments" / f"{consumer_id}.json"
    if consumer_id not in ASSIGNMENT_SHA256 or digest(assignment_path) != ASSIGNMENT_SHA256[consumer_id]:
        raise ValueError("No matching preserved recovery assignment")
    assignment = read_json(assignment_path)
    if (assignment["consumer_id"] != consumer_id or assignment["case"] != "S06"
            or assignment["context"] != "fresh"):
        raise ValueError("Assignment identity differs")
    expected = {f"consumer-setup/{consumer_id}.json", f"state-snapshots/{consumer_id}/initial.sql",
                f"state-snapshots/{consumer_id}/initial.json"}
    initial = assignment["initial_state_evidence_sha256"]
    if set(initial) != expected or any(digest(root / path) != value for path, value in initial.items()):
        raise ValueError("Assignment-anchored initial evidence changed")
    setup = read_json(root / "consumer-setup" / f"{consumer_id}.json")
    metadata = read_json(root / "state-snapshots" / consumer_id / "initial.json")
    original = checked(Path(setup["state_path"]))
    if (setup.get("consumer_id") != consumer_id or setup.get("setup_verified") is not True
            or original.name != "ledger.sqlite"
            or not original.parent.name.startswith(consumer_id + "-ledger-state-")
            or metadata.get("consumer_id") != consumer_id or metadata.get("snapshot") != "initial"
            or metadata.get("state_path") != str(original)
            or metadata.get("sql_sha256") != initial[f"state-snapshots/{consumer_id}/initial.sql"]):
        raise ValueError("Original setup or snapshot identity differs")
    substitutions = [item for item in assignment["request_substitutions"] if item["token"] == "{{STATE_PATH}}"]
    if substitutions != [{"token": "{{STATE_PATH}}", "value": str(original), "occurrences": 1}]:
        raise ValueError("Original request state binding differs")
    fixture = root / "control-consumer-cases/S06" / assignment["variant"] / "fixture.json"
    if (digest(fixture) != setup["fixture_sha256"] or
            setup["interface_sha256"] != assignment["copied_sha256"]["input/ledger_api.py"]):
        raise ValueError("Prescribed fixture or interface identity differs")
    records = read_json(fixture)["records"]
    sql = (root / "state-snapshots" / consumer_id / "initial.sql").read_text(encoding="utf-8")
    connection = sqlite3.connect(":memory:")
    try:
        connection.executescript(sql)
        observation = inspect_initial(connection, sql, records)
    finally:
        connection.close()
    expected_calls = [{"state": "ready", "snapshot_id": observation["snapshot_id"], "total_records": len(records)},
                      {key: value for key, value in observation.items() if key not in {"calls_used", "records_sha256"}}]
    calls = setup["calls"]
    if len(calls) != 2 or any(call["exit_code"] != 0 or call["stderr"] or
                             json.loads(call["stdout"]) != expected
                             for call, expected in zip(calls, expected_calls)):
        raise ValueError("Original setup observations do not establish the unused initial state")
    return assignment, setup, sql, records, observation


def load_binding(root, consumer_id, setup):
    """Validate preserved recovery evidence; never require the live DB for grading."""
    path = record_path(root, consumer_id)
    if not path.exists():
        return None
    assignment, original_setup, sql, records, observation = source_evidence(root, consumer_id)
    binding = read_json(path)
    state = restored_path(root, consumer_id, Path(binding["restored_state_path"]).parent)
    if (setup != original_setup or binding.get("consumer_id") != consumer_id
            or binding.get("original_state_path") != setup["state_path"]
            or binding.get("restored_state_path") != str(state)
            or binding.get("assignment_sha256") != ASSIGNMENT_SHA256[consumer_id]
            or binding.get("source_evidence_sha256") != assignment["initial_state_evidence_sha256"]
            or binding.get("restored_sql_sha256") != hashlib.sha256(sql.encode()).hexdigest()
            or binding.get("initial_state_observation") != observation
            or not re.fullmatch(r"[0-9a-f]{64}", binding.get("restored_binary_sha256", ""))
            or datetime.fromisoformat(binding["observed_utc"]).utcoffset() != timezone.utc.utcoffset(None)):
        raise ValueError("Recovery record does not preserve the original and restored identities")
    return binding


def snapshot_identity(root, consumer_id, setup, label):
    binding = load_binding(root, consumer_id, setup)
    if binding is None or label == "initial":
        return {"state_path": setup["state_path"]}
    path = record_path(root, consumer_id)
    return {"state_path": binding["restored_state_path"], "original_state_path": setup["state_path"],
            "recovery_binding_path": path.relative_to(root).as_posix(), "recovery_binding_sha256": digest(path)}


def validate_snapshot_identity(root, consumer_id, setup, label, metadata):
    expected = snapshot_identity(root, consumer_id, setup, label)
    if any(metadata.get(key) != expected.get(key) for key in ("state_path", *RECOVERY_FIELDS)):
        raise ValueError(f"Native snapshot original/recovered binding differs: {consumer_id}/{label}")


def restore(root, consumer_id, directory):
    assignment, setup, sql, records, observation = source_evidence(root, consumer_id)
    with checked(root / "control-consumer-list.tsv").open(newline="", encoding="utf-8") as stream:
        rows = [row for row in csv.DictReader(stream, delimiter="\t") if row["consumer_id"] == consumer_id]
    if (len(rows) != 1 or rows[0]["execution"] != "prepared" or any(
            rows[0][field] != assignment[field] for field in ("creator_id", "case", "variant"))):
        raise ValueError("Only this still-prepared original assignment may be restored")
    folder = root / "consumers" / consumer_id
    if digest(folder / "prompt.md") != assignment["prompt_sha256"]:
        raise ValueError("Original consumer prompt changed")
    if set(assignment["copied_file_modes"]) != set(assignment["copied_sha256"]):
        raise ValueError("Original resource mode identities incomplete")
    for relative, value in assignment["copied_sha256"].items():
        path = folder / relative
        if digest(path) != value or stat.S_IMODE(path.stat().st_mode) != assignment["copied_file_modes"][relative]:
            raise ValueError(f"Original consumer resource changed: {relative}")
    allowed_files = set(assignment["copied_sha256"]) | {"prompt.md"}
    if any(path.is_symlink() or (path.is_file() and path.relative_to(folder).as_posix() not in allowed_files)
           for path in folder.rglob("*")):
        raise ValueError("Preserve existing application evidence; no new initial restoration")
    record = record_path(root, consumer_id)
    state = restored_path(root, consumer_id, directory)
    if (record.exists() or directory.exists()
            or any(root.parent.glob(consumer_id + "-ledger-recovery-*"))
            or Path(setup["state_path"]).parent.exists()
            or any((root / "state-snapshots" / consumer_id).glob("final.*"))):
        raise ValueError("Preserve an original, existing or partial recovery/application state")
    record.parent.mkdir(exist_ok=True)
    directory.mkdir(mode=0o700, exist_ok=False)
    descriptor = os.open(state, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(descriptor)
    connection = sqlite3.connect(state.as_uri() + "?mode=rw", uri=True)
    try:
        connection.executescript(sql)
        inspect_initial(connection, sql, records)
    finally:
        connection.close()
    binding = {"consumer_id": consumer_id, "original_state_path": setup["state_path"],
               "restored_state_path": str(state), "assignment_sha256": ASSIGNMENT_SHA256[consumer_id],
               "source_evidence_sha256": assignment["initial_state_evidence_sha256"],
               "restored_sql_sha256": hashlib.sha256(sql.encode()).hexdigest(),
               "restored_binary_sha256": digest(state), "initial_state_observation": observation,
               "sqlite_version": sqlite3.sqlite_version, "observed_utc": datetime.now(timezone.utc).isoformat(),
               "scope": "New native file restored from preserved initial SQL for the same pending attempt; no business API operation"}
    with record.open("x", encoding="utf-8") as stream:
        json.dump(binding, stream, indent=2)
        stream.write("\n")
    if load_binding(root, consumer_id, setup) != binding:
        raise ValueError("Written recovery identity failed read-back")
    return binding


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("consumer_id", choices=tuple(ASSIGNMENT_SHA256))
    parser.add_argument("--destination-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(restore(ROOT, args.consumer_id, args.destination_dir), indent=2))
