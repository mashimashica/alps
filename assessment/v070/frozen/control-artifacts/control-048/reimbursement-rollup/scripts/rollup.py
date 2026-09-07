#!/usr/bin/env python3
"""Complete, resumable reimbursement rollup through the paginated ledger CLI."""
import argparse
import datetime
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


class Failure(Exception):
    pass


def require(condition, message):
    if not condition:
        raise Failure(message)


def integer(value, minimum=0):
    return type(value) is int and value >= minimum


def date(value):
    require(isinstance(value, str), "date must be a string")
    require(datetime.date.fromisoformat(value).isoformat() == value,
            "dates must use YYYY-MM-DD")
    return value


def record(row):
    fields = {"entry_id", "vendor_id", "posted_on", "kind", "status", "amount_cents", "currency"}
    require(isinstance(row, dict) and set(row) == fields, "invalid record fields")
    for key in ("entry_id", "vendor_id"):
        require(isinstance(row[key], str) and bool(row[key]), "invalid record identifier")
    date(row["posted_on"])
    require(row["kind"] in ("charge", "credit"), "invalid kind")
    require(row["status"] in ("settled", "pending", "void"), "invalid status")
    require(integer(row["amount_cents"]) and row["currency"] == "USD", "invalid amount/currency")


def invoke(args, *command):
    result = subprocess.run([sys.executable, args.api, "--state", args.state, *command],
                            capture_output=True, text=True, timeout=60)
    try:
        body = json.loads(result.stdout)
    except (ValueError, TypeError) as exc:
        raise Failure("source response missing or malformed; a page call may have consumed quota") from exc
    require(isinstance(body, dict), "source response must be an object")
    if result.returncode == 75 and body.get("error") == "call_budget_exhausted":
        return None
    require(result.returncode == 0, "source error: " + str(body))
    return body


def describe(args):
    meta = invoke(args, "describe")
    require(isinstance(meta, dict), "invalid metadata")
    require(isinstance(meta.get("snapshot_id"), str) and bool(meta["snapshot_id"]), "invalid snapshot")
    require(integer(meta.get("total_records")), "invalid total")
    require(meta.get("page_size") == 3 and meta.get("calls_per_tranche") == 2,
            "unsupported page/tranche limits")
    require(integer(meta.get("tranche"), 1) and integer(meta.get("remaining_calls"))
            and meta["remaining_calls"] <= 2, "invalid quota metadata")
    return meta


def save(path, value):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, prefix=path.name + ".",
                                         suffix=".tmp", delete=False) as handle:
            temporary = handle.name
            json.dump(value, handle, sort_keys=True, separators=(",", ":"))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def incorporate(state, response, cursor):
    require(response.get("snapshot_id") == state["snapshot_id"] and
            response.get("total_records") == state["total_records"], "page identity mismatch")
    require(integer(response.get("tranche"), 1), "invalid page tranche")
    require("next_cursor" in response, "missing terminal marker")
    following = response["next_cursor"]
    require(following is None or isinstance(following, str) and bool(following), "invalid cursor")
    rows = response.get("items")
    require(isinstance(rows, list) and len(rows) <= 3, "invalid page items")
    require(bool(rows) or following is None, "empty nonterminal page")
    require(cursor not in state["cursors"], "request cursor already incorporated")
    require(following is None or following not in state["cursors"] + [cursor], "cursor cycle")
    seen = {row["entry_id"] for row in state["entries"]}
    for row in rows:
        record(row)
        require(row["entry_id"] not in seen, "duplicate source entry")
        seen.add(row["entry_id"])
    require(len(seen) <= state["total_records"], "source count exceeded")
    require(following is not None or len(seen) == state["total_records"], "terminal count mismatch")
    state["entries"].extend(rows)
    state["cursors"].append(cursor)
    state["next_cursor"] = following
    state["complete"] = following is None


def validate_checkpoint(state, identity, meta):
    require(isinstance(state, dict) and state.get("version") == 1, "unsupported checkpoint")
    require(state.get("request") == identity, "checkpoint belongs to another request")
    require(state.get("snapshot_id") == meta["snapshot_id"] and
            state.get("total_records") == meta["total_records"], "snapshot/count changed")
    require(type(state.get("complete")) is bool and isinstance(state.get("entries"), list)
            and isinstance(state.get("cursors"), list), "invalid checkpoint structure")
    cursors = state["cursors"]
    require(not cursors or cursors[0] is None, "invalid initial cursor")
    require(all(isinstance(c, str) and c for c in cursors[1:]), "invalid saved cursor")
    require(len(set(cursors)) == len(cursors), "duplicate saved cursor")
    seen = set()
    for row in state["entries"]:
        record(row)
        require(row["entry_id"] not in seen, "duplicate checkpoint entry")
        seen.add(row["entry_id"])
    require(len(seen) <= meta["total_records"] and len(seen) <= 3 * len(cursors), "invalid saved count")
    following = state.get("next_cursor")
    if state["complete"]:
        require(bool(cursors) and following is None and len(seen) == meta["total_records"],
                "invalid completion evidence")
    elif cursors:
        require(isinstance(following, str) and following and following not in cursors,
                "invalid continuation cursor")
    else:
        require(not seen and following is None, "invalid initial checkpoint")


def report(state, reason):
    result = {"complete": state["complete"], "reason": reason,
              "snapshot_id": state["snapshot_id"], "start": state["request"]["start"],
              "end": state["request"]["end"], "currency": "USD",
              "examined_records": len(state["entries"]), "total_records": state["total_records"]}
    if state["complete"]:
        vendors = {}
        for row in state["entries"]:
            if row["status"] != "settled" or not result["start"] <= row["posted_on"] <= result["end"]:
                continue
            vendor = vendors.setdefault(row["vendor_id"], {"vendor_id": row["vendor_id"],
                "settled_charge_cents": 0, "settled_credit_cents": 0, "net_cents": 0,
                "qualifying_entry_count": 0})
            vendor["settled_" + row["kind"] + "_cents"] += row["amount_cents"]
            vendor["net_cents"] += row["amount_cents"] * (1 if row["kind"] == "charge" else -1)
            vendor["qualifying_entry_count"] += 1
        result["vendors"] = [vendors[key] for key in sorted(vendors)]
    print(json.dumps(result, sort_keys=True))
    return 0 if state["complete"] else 75


def run(args):
    date(args.start)
    date(args.end)
    require(args.start <= args.end, "start must not be after end")
    args.api = str(Path(args.api).resolve(strict=True))
    args.state = str(Path(args.state).resolve(strict=True))
    path = Path(args.checkpoint).resolve()
    require(path not in (Path(args.api), Path(args.state)), "checkpoint must be separate from source")
    require(path.parent.is_dir(), "checkpoint parent directory must exist")
    identity = {"api": args.api, "state": args.state, "start": args.start, "end": args.end}
    with open(str(path) + ".lock", "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        meta = describe(args)
        if path.exists():
            state = json.loads(path.read_text())
            validate_checkpoint(state, identity, meta)
        else:
            state = {"version": 1, "request": identity, "snapshot_id": meta["snapshot_id"],
                     "total_records": meta["total_records"], "entries": [], "cursors": [],
                     "next_cursor": None, "complete": False}
            save(path, state)
        if state["complete"]:
            return report(state, "source_exhausted")
        tranche = meta["tranche"]
        for _ in range(2):
            meta = describe(args)
            require(meta["snapshot_id"] == state["snapshot_id"] and
                    meta["total_records"] == state["total_records"], "snapshot/count changed")
            if meta["tranche"] != tranche:
                return report(state, "tranche_changed")
            if meta["remaining_calls"] == 0:
                return report(state, "awaiting_operator_tranche")
            cursor = state["next_cursor"]
            command = ["page", "--snapshot", state["snapshot_id"]]
            if cursor is not None:
                command.extend(["--cursor", cursor])
            response = invoke(args, *command)
            if response is None:
                return report(state, "awaiting_operator_tranche")
            incorporate(state, response, cursor)
            save(path, state)
            if state["complete"]:
                return report(state, "source_exhausted")
            if response["tranche"] != tranche:
                return report(state, "tranche_changed")
        return report(state, "execution_tranche_limit")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name, help_text in (("api", "path to supplied ledger_api.py"),
                            ("state", "existing authorized source state"),
                            ("checkpoint", "persistent JSON checkpoint for this request"),
                            ("start", "inclusive YYYY-MM-DD start"),
                            ("end", "inclusive YYYY-MM-DD end")):
        parser.add_argument("--" + name, required=True, help=help_text)
    args = parser.parse_args()
    try:
        return run(args)
    except (Failure, OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as exc:
        print(json.dumps({"complete": False, "error": str(exc),
                          "recovery": "Preserve checkpoint; resolve error and rerun with remaining approved quota."}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
