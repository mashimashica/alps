"""Assessment-only booking fixture setup and native SQL evidence snapshots.

No target Skill imports this helper. Setup uses only the explicitly reviewed
local interface. Read-only SQLite dumps preserve committed logical state as
plain UTF-8 for direct Git API checkpoints, without claiming byte identity.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def snapshot(consumer_id, label):
    if not re.fullmatch(r"D1-U\d{3}", consumer_id) or not re.fullmatch(r"[a-z0-9-]+", label):
        raise ValueError("Explicit consumer ID and simple snapshot label required")
    setup = json.loads((ROOT / "consumer-setup" / f"{consumer_id}.json").read_text())
    path = Path(setup["state_path"])
    if path.parent.parent != ROOT.parent or not path.parent.name.startswith(consumer_id + "-booking-state-"):
        raise ValueError("State path is outside this consumer's allocated temporary directory")
    connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    try:
        connection.execute("BEGIN")
        if connection.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
            raise ValueError("State integrity check failed")
        sql = "\n".join(connection.iterdump()) + "\n"
    finally:
        connection.close()
    target = ROOT / "state-snapshots" / consumer_id
    target.mkdir(parents=True, exist_ok=True)
    with (target / f"{label}.sql").open("x", encoding="utf-8") as stream:
        stream.write(sql)
    metadata = {"state_path": str(path), "snapshot": label,
                "representation": "Native SQL of a consistent committed read transaction; not a byte-identical SQLite file",
                "sql_sha256": hashlib.sha256(sql.encode()).hexdigest()}
    with (target / f"{label}.json").open("x", encoding="utf-8") as stream:
        json.dump(metadata, stream, indent=2)
        stream.write("\n")
    return metadata


def prepare(folder, source):
    inputs = folder / "input"
    inputs.mkdir()
    shutil.copy2(ROOT / "main-cases/S08/booking.py", inputs / "booking.py")
    state_dir = Path(tempfile.mkdtemp(prefix=folder.name + "-booking-state-", dir=ROOT.parent))
    state = state_dir / "bookings.sqlite"
    bindings = {"{{PYTHON}}": sys.executable, "{{BOOKING_PY}}": str(inputs / "booking.py"),
                "{{STATE_DB}}": str(state), "{{FIXTURE_JSON}}": str(source / "fixture.json"),
                "{{WORK_DIR}}": str(folder / "work")}
    recipe = json.loads((source / "setup.json").read_text())
    expected = json.loads((source / "setup-observations.json").read_text())["calls"]
    if len(recipe["steps"]) != len(expected):
        raise ValueError("Setup recipe and observation counts differ")
    setup_dir = ROOT / "consumer-setup"
    setup_dir.mkdir(exist_ok=True)
    record_path = setup_dir / f"{folder.name}.json"
    record = {"consumer": folder.name, "state_path": str(state), "source_packet": str(source),
              "setup_verified": False, "calls": []}
    for step, oracle in zip(recipe["steps"], expected):
        argv = [bindings.get(value, value) for value in step["argv"]]
        if argv[:2] != [sys.executable, str(inputs / "booking.py")] or argv[2:4] != ["--state", str(state)]:
            raise ValueError("Unexpected setup interface or state target")
        if any("{{" in value for value in argv):
            raise ValueError("Unresolved setup token")
        result = subprocess.run(argv, capture_output=True, text=True, timeout=15)
        capture = {"id": step["id"], "argv": argv, "exit_code": result.returncode,
                   "stdout": result.stdout, "stderr": result.stderr}
        record["calls"].append(capture)
        record_path.write_text(json.dumps(record, indent=2) + "\n")
        if step["id"] != oracle["id"] or result.returncode != oracle["exit_code"] or result.stderr != oracle["stderr"]:
            raise ValueError(f"Setup observation mismatch: {step['id']}")
        observed_stdout = json.loads(result.stdout) if result.stdout.strip() else None
        expected_stdout = json.loads(oracle["stdout"]) if oracle["stdout"].strip() else None
        if observed_stdout != expected_stdout:
            raise ValueError(f"Setup JSON mismatch: {step['id']}")
    record["setup_verified"] = True
    record_path.write_text(json.dumps(record, indent=2) + "\n")
    body = (source / "request.md").read_text(encoding="utf-8")
    for token, value in bindings.items():
        body = body.replace(token, value)
    if "{{" in body:
        raise ValueError("Unresolved request token")
    (inputs / "request.md").write_text(body, encoding="utf-8")
    snapshot(folder.name, "initial")
    return state


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("consumer_ids", nargs="+")
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    for consumer_id in args.consumer_ids:
        print(json.dumps(snapshot(consumer_id, args.label)))
