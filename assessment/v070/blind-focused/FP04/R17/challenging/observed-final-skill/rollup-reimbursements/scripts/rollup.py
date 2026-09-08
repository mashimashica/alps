#!/usr/bin/env python3
"""Exact, resumable reimbursement rollup. Python 3.12 standard library, POSIX.

Example: python3.12 scripts/rollup.py run --api /path/ledger_api.py
  --state /path/source.sqlite --start 2026-02-01 --end 2026-02-15
  --checkpoint /path/request.json --output /path/result.json

Exit codes: 0 complete; 10 incomplete (needs operator tranche); 2 invalid
arguments/identity/protocol/local state; 3 uncertain source failure; 4 source
snapshot mismatch; 75 source budget exhausted. All nonzero results are not final.
No operation grants tranches or initializes the source. Reissue the identical
run after recovery or an operator grant. status regenerates output without calls.
"""

import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


class Failure(Exception):
    def __init__(self, detail, code=2):
        super().__init__(detail)
        self.code = code


def require(condition, message):
    if not condition:
        raise Failure(message)


def date(value):
    try:
        require(isinstance(value, str) and dt.date.fromisoformat(value).isoformat() == value,
                "Dates must be valid YYYY-MM-DD calendar dates")
    except (ValueError, TypeError):
        raise Failure("Dates must be valid YYYY-MM-DD calendar dates") from None
    return value


def atomic(path, value):
    """Commit one complete JSON value; readers see old or new state."""
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, sort_keys=True, separators=(",", ":"))
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def api_call(api, state, *args):
    try:
        result = subprocess.run([sys.executable, api, "--state", state, *args],
                                text=True, capture_output=True, timeout=60)
    except (subprocess.TimeoutExpired, OSError) as exc:
        raise Failure("Source effect uncertain; preserve checkpoint, inspect describe, "
                      "then resume same request: " + str(exc), 3) from None
    if result.returncode:
        code = result.returncode if result.returncode in (2, 4, 75) else 3
        raise Failure("Source failed; no page committed. Check quota before retry. "
                      + (result.stdout or result.stderr).strip(), code)
    try:
        value = json.loads(result.stdout)
        require(isinstance(value, dict), "Source returned a non-object")
        return value
    except (ValueError, Failure):
        raise Failure("Source response unreadable; call may have consumed quota. "
                      "Preserve checkpoint and inspect describe before resuming.", 3) from None


def metadata(value):
    require(isinstance(value.get("snapshot_id"), str) and value["snapshot_id"],
            "Missing snapshot identity")
    for key in ("total_records", "page_size", "calls_per_tranche", "tranche", "remaining_calls"):
        require(type(value.get(key)) is int, "Invalid metadata: " + key)
    require(value["total_records"] >= 0 and value["page_size"] == 3
            and value["calls_per_tranche"] == 2 and value["tranche"] >= 1
            and 0 <= value["remaining_calls"] <= 2, "Unsupported source contract")
    return value


def record(row):
    fields = {"entry_id", "vendor_id", "posted_on", "kind", "status", "amount_cents", "currency"}
    require(isinstance(row, dict) and set(row) == fields, "Record fields violate contract")
    for key in ("entry_id", "vendor_id"):
        require(isinstance(row[key], str) and row[key], "Invalid " + key)
    date(row["posted_on"])
    require(row["kind"] in ("charge", "credit") and row["status"] in ("settled", "pending", "void"),
            "Invalid kind/status")
    require(type(row["amount_cents"]) is int and row["amount_cents"] >= 0
            and row["currency"] == "USD", "Expected nonnegative integer USD cents")


def validate_checkpoint(cp):
    require(cp.get("version") == 1, "Unsupported checkpoint version")
    date(cp["start"])
    date(cp["end"])
    require(cp["start"] <= cp["end"], "Invalid checkpoint interval")
    require(type(cp["exhausted"]) is bool and isinstance(cp["records"], list)
            and isinstance(cp["page_cursors"], list), "Invalid checkpoint structure")
    ids = set()
    for row in cp["records"]:
        record(row)
        require(row["entry_id"] not in ids, "Duplicate checkpoint entry")
        ids.add(row["entry_id"])
    require(type(cp["total_records"]) is int and 0 <= len(ids) <= cp["total_records"],
            "Checkpoint coverage mismatch")
    cursors = cp["page_cursors"]
    require(all(isinstance(c, str) and c for c in cursors[1:])
            and (not cursors or cursors[0] is None)
            and len(set(cursors)) == len(cursors), "Invalid checkpoint cursor chain")
    if cp["exhausted"]:
        require(cp["next_cursor"] is None and cursors and len(ids) == cp["total_records"],
                "Incomplete checkpoint marked exhausted")
    elif cursors:
        require(isinstance(cp["next_cursor"], str) and cp["next_cursor"]
                and cp["next_cursor"] not in cursors, "Invalid continuation cursor")
    else:
        require(cp["next_cursor"] is None and not ids, "Invalid initial checkpoint")


def incorporate(cp, page, tranche):
    require(page.get("snapshot_id") == cp["snapshot_id"], "Response snapshot mismatch")
    require(page.get("total_records") == cp["total_records"], "Source record count changed")
    require(page.get("tranche") == tranche, "Tranche changed during run; coordinate operator grants")
    require("next_cursor" in page and isinstance(page.get("items"), list), "Invalid page response")
    following = page["next_cursor"]
    require(following is None or isinstance(following, str) and following,
            "Invalid next cursor")
    items = page["items"]
    require(len(items) <= 3 and (len(items) == 3 or following is None), "Invalid page size")
    used = cp["page_cursors"] + [cp["next_cursor"]]
    require(following is None or following not in used, "Cursor loop detected")
    # New state is built without modifying the committed checkpoint object.
    new = {**cp, "records": cp["records"] + items, "page_cursors": used,
           "next_cursor": following, "exhausted": following is None,
           "last_tranche": tranche}
    validate_checkpoint(new)
    return new


def result(cp):
    vendors = {}
    for row in cp["records"]:
        if row["status"] != "settled" or not cp["start"] <= row["posted_on"] <= cp["end"]:
            continue
        v = vendors.setdefault(row["vendor_id"], {"vendor_id": row["vendor_id"],
                              "settled_charge_cents": 0, "settled_credit_cents": 0,
                              "net_cents": 0, "qualifying_entry_count": 0})
        v["settled_" + row["kind"] + "_cents"] += row["amount_cents"]
        v["net_cents"] += row["amount_cents"] * (1 if row["kind"] == "charge" else -1)
        v["qualifying_entry_count"] += 1
    return {"status": "complete" if cp["exhausted"] else "incomplete",
            "complete": cp["exhausted"], "snapshot_id": cp["snapshot_id"],
            "start": cp["start"], "end": cp["end"], "currency": "USD",
            "examined_entries": len(cp["records"]), "total_records": cp["total_records"],
            "committed_pages": len(cp["page_cursors"]), "next_cursor": cp["next_cursor"],
            "vendors": [vendors[v] for v in sorted(vendors)]}


def publish(cp, args, reason):
    value = result(cp)
    value["reason"] = reason
    atomic(args.output, value)
    print(json.dumps({k: v for k, v in value.items() if k != "vendors"}
                     | {"output": args.output, "checkpoint": args.checkpoint}, sort_keys=True))
    return 0 if cp["exhausted"] else 10


def run(args):
    if args.command == "run":
        # Validate the entire interval before even an unmetered source query.
        date(args.start)
        date(args.end)
        require(args.start <= args.end, "start must be on or before end")
    args.checkpoint = str(Path(args.checkpoint).resolve())
    args.output = str(Path(args.output).resolve())
    lockpath = args.checkpoint + ".lock"
    require(args.output not in (args.checkpoint, lockpath), "Output must be separate from checkpoint/lock")
    for path in (args.checkpoint, args.output):
        require(Path(path).parent.is_dir(), "Output/checkpoint parent directories must already exist")
    if args.command == "run":
        args.api, args.state = str(Path(args.api).resolve()), str(Path(args.state).resolve())
        require(Path(args.api).is_file() and Path(args.state).is_file(), "API and initialized state must exist")
        protected = {args.api, args.state, args.state + "-journal", args.state + "-wal", args.state + "-shm"}
        require(not protected.intersection({args.checkpoint, args.output, lockpath}),
                "Work products must not overwrite source files")
    with open(lockpath, "a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Failure("Checkpoint is in use; do not run concurrently") from None
        cp = None
        if Path(args.checkpoint).exists():
            cp = json.loads(Path(args.checkpoint).read_text())
            validate_checkpoint(cp)
            protected = {cp["api"], cp["state"], cp["state"] + "-journal",
                         cp["state"] + "-wal", cp["state"] + "-shm"}
            require(args.output not in protected, "Output must not overwrite source files")
        if args.command == "status":
            require(cp is not None, "Checkpoint does not exist")
            return publish(cp, args, "source_exhausted" if cp["exhausted"] else "checkpoint_only")
        identity = {"api": args.api, "state": args.state, "start": args.start, "end": args.end}
        if cp is not None:
            require(all(cp[k] == v for k, v in identity.items()),
                    "Request identity differs; resume with original arguments or use a new checkpoint")
        meta = metadata(api_call(args.api, args.state, "describe"))
        if cp is None:
            cp = {"version": 1, **identity, "snapshot_id": meta["snapshot_id"],
                  "total_records": meta["total_records"], "records": [], "page_cursors": [],
                  "next_cursor": None, "exhausted": False, "last_tranche": None}
            atomic(args.checkpoint, cp)
        require(cp["snapshot_id"] == meta["snapshot_id"] and cp["total_records"] == meta["total_records"],
                "Source identity changed; never merge snapshots")
        if cp["exhausted"]:
            return publish(cp, args, "source_exhausted")
        tranche = meta["tranche"]
        for _ in range(meta["remaining_calls"]):
            current = metadata(api_call(args.api, args.state, "describe"))
            require(current["snapshot_id"] == cp["snapshot_id"]
                    and current["total_records"] == cp["total_records"], "Source changed during run")
            if current["tranche"] != tranche or current["remaining_calls"] == 0:
                break
            command = ["page", "--snapshot", cp["snapshot_id"]]
            if cp["next_cursor"] is not None:
                command.extend(["--cursor", cp["next_cursor"]])
            page = api_call(args.api, args.state, *command)
            new = incorporate(cp, page, tranche)
            atomic(args.checkpoint, new)
            cp = new
            if cp["exhausted"]:
                return publish(cp, args, "source_exhausted")
        return publish(cp, args, "awaiting_operator_tranche")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "status"):
        p = commands.add_parser(name, help="traverse current tranche" if name == "run" else "read committed progress only")
        p.add_argument("--checkpoint", required=True, help="durable request JSON; never delete to resume")
        p.add_argument("--output", required=True, help="JSON result path, overwritten; parents must exist")
        if name == "run":
            p.add_argument("--api", required=True, help="trusted ledger_api.py implementing supplied CLI contract")
            p.add_argument("--state", required=True, help="existing immutable source state")
            p.add_argument("--start", required=True, help="inclusive YYYY-MM-DD")
            p.add_argument("--end", required=True, help="inclusive YYYY-MM-DD")
    args = parser.parse_args()
    try:
        return run(args)
    except (Failure, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "error", "complete": False, "detail": str(exc),
                          "checkpoint": args.checkpoint,
                          "recovery": "Preserve checkpoint; status shows committed progress. "
                                      "Inspect source describe before retry; output may be stale."}), file=sys.stderr)
        return exc.code if isinstance(exc, Failure) else 2


if __name__ == "__main__":
    sys.exit(main())
