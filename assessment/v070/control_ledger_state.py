"""C-control ledger setup and read-only native SQL evidence snapshots.

Experiment-only. Hidden fixtures and setup evidence stay outside the consumer
task. SQLite bytes stay outside the evidence root; native SQL preserves a
consistent committed logical state, not byte identity or task adequacy.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def snapshot(consumer_id, label):
    if not re.fullmatch(r"C-U\d{3}", consumer_id) or not re.fullmatch(r"[a-z0-9-]+", label):
        raise ValueError("Explicit C consumer ID and simple snapshot label required")
    setup_path = ROOT / "consumer-setup" / f"{consumer_id}.json"
    if setup_path.is_symlink() or setup_path.parent.is_symlink():
        raise ValueError("Unexpected setup evidence symlink")
    setup = json.loads(setup_path.read_text())
    if setup.get("consumer_id") != consumer_id or not setup.get("setup_verified"):
        raise ValueError("Matching completed setup evidence is required")
    path = Path(setup["state_path"])
    if (path.parent.parent != ROOT.parent or path.name != "ledger.sqlite"
            or not path.parent.name.startswith(consumer_id + "-ledger-state-")
            or path.is_symlink() or path.parent.is_symlink() or not path.is_file()):
        raise ValueError("State is outside this consumer's allocated native file")
    target = ROOT / "state-snapshots" / consumer_id
    for candidate in (target.parent, target):
        if candidate.is_symlink() or (candidate.exists() and not candidate.is_dir()):
            raise ValueError(f"Unexpected snapshot directory: {candidate}")
    for suffix in ("sql", "json"):
        destination = target / f"{label}.{suffix}"
        if destination.exists() or destination.is_symlink():
            raise ValueError(f"Preserve existing or partial snapshot: {destination}")
    connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    try:
        connection.execute("BEGIN")
        if connection.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
            raise ValueError("Native state integrity check failed")
        sql = "\n".join(connection.iterdump()) + "\n"
    finally:
        connection.close()
    target.mkdir(parents=True, exist_ok=True)
    with (target / f"{label}.sql").open("x", encoding="utf-8") as stream:
        stream.write(sql)
    metadata = {"consumer_id": consumer_id, "state_path": str(path), "snapshot": label,
                "representation": "Native SQL from a consistent committed read transaction; not byte-identical SQLite",
                "sqlite_version": sqlite3.sqlite_version,
                "sql_sha256": hashlib.sha256(sql.encode()).hexdigest()}
    with (target / f"{label}.json").open("x", encoding="utf-8") as stream:
        json.dump(metadata, stream, indent=2)
        stream.write("\n")
    return metadata


def prepare(folder, source):
    """Called only after the packaging helper's whole-batch preflight."""
    if folder.parent != ROOT / "consumers" or not re.fullmatch(r"C-U\d{3}", folder.name):
        raise ValueError("Expected the explicit consumer task folder")
    fixture = source / "fixture.json"
    api = folder / "input/ledger_api.py"
    records = json.loads(fixture.read_text())["records"]
    canonical = json.dumps(records, sort_keys=True, separators=(",", ":"))
    expected_snapshot = "snap_" + hashlib.sha256(canonical.encode()).hexdigest()[:24]
    setup_dir = ROOT / "consumer-setup"
    if setup_dir.is_symlink() or (setup_dir.exists() and not setup_dir.is_dir()):
        raise ValueError("Unexpected setup evidence directory")
    setup_dir.mkdir(exist_ok=True)
    record_path = setup_dir / f"{folder.name}.json"
    if record_path.exists() or record_path.is_symlink() or any(ROOT.parent.glob(folder.name + "-ledger-state-*")):
        raise ValueError("Preserve an existing or partial native state setup")
    state_dir = Path(tempfile.mkdtemp(prefix=folder.name + "-ledger-state-", dir=ROOT.parent))
    state = state_dir / "ledger.sqlite"
    record = {"consumer_id": folder.name, "state_path": str(state), "source_packet": str(source),
              "fixture_sha256": hashlib.sha256(fixture.read_bytes()).hexdigest(),
              "interface_sha256": hashlib.sha256(api.read_bytes()).hexdigest(),
              "setup_verified": False, "calls": []}
    with record_path.open("x", encoding="utf-8") as stream:
        json.dump(record, stream, indent=2)
        stream.write("\n")
    calls = [([sys.executable, str(api), "--state", str(state), "init", "--fixture", str(fixture)],
              {"state": "ready", "snapshot_id": expected_snapshot, "total_records": len(records)}),
             ([sys.executable, str(api), "--state", str(state), "describe"],
              {"snapshot_id": expected_snapshot, "total_records": len(records), "page_size": 3,
               "calls_per_tranche": 2, "tranche": 1, "remaining_calls": 2})]
    for argv, expected in calls:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=15, cwd=folder)
        record["calls"].append({"argv": argv, "exit_code": result.returncode,
                                "stdout": result.stdout, "stderr": result.stderr})
        record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        if result.returncode != 0 or result.stderr or json.loads(result.stdout) != expected:
            raise ValueError(f"Native state setup observation mismatch: {folder.name}")
    record["setup_verified"] = True
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    snapshot(folder.name, "initial")
    return state


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("consumer_ids", nargs="+")
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    for consumer_id in args.consumer_ids:
        print(json.dumps(snapshot(consumer_id, args.label)))
