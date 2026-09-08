#!/usr/bin/env python3
"""Exact, resumable reimbursement rollup; Python 3.12, Unix, standard library only."""
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
    def __init__(self, message, code=2):
        super().__init__(message)
        self.code = code


def date(value):
    try:
        if dt.date.fromisoformat(value).isoformat() == value:
            return value
    except (ValueError, TypeError):
        pass
    raise Failure("Dates must be valid YYYY-MM-DD calendar dates")


def atomic_json(path, value):
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def api(args, command, *extra):
    # Only metadata and page operations are exposed. Never initialize or grant quota.
    if command not in ("describe", "page"):
        raise Failure("Unsupported API operation")
    try:
        result = subprocess.run(
            [sys.executable, args.api, "--state", args.source, command, *extra],
            capture_output=True, text=True, timeout=30, check=False,
        )
    except subprocess.TimeoutExpired:
        raise Failure("API response lost or timed out; quota may be consumed. Resume the same checkpoint after checking describe.", 3)
    if result.returncode == 75:
        raise Failure("call_budget_exhausted", 75)
    if result.returncode:
        raise Failure(f"API exit {result.returncode}: {result.stdout.strip()} {result.stderr.strip()}; checkpoint not advanced", 4 if result.returncode == 4 else 3)
    try:
        body = json.loads(result.stdout)
        if not isinstance(body, dict):
            raise ValueError("expected JSON object")
        return body
    except ValueError:
        raise Failure("Unreadable API response; quota may be consumed. Resume the same checkpoint; retry is metered.", 3)


def metadata(args):
    body = api(args, "describe")
    if (not isinstance(body.get("snapshot_id"), str) or not body["snapshot_id"]
            or type(body.get("total_records")) is not int or body["total_records"] < 0
            or body.get("page_size") != 3 or body.get("calls_per_tranche") != 2
            or type(body.get("tranche")) is not int or body["tranche"] < 1
            or type(body.get("remaining_calls")) is not int or not 0 <= body["remaining_calls"] <= 2):
        raise Failure("Source metadata violates the supported interface", 3)
    return body


def incorporate(state, page):
    if page.get("snapshot_id") != state["snapshot_id"]:
        raise Failure("Page snapshot mismatch", 4)
    if page.get("total_records") != state["total_records"]:
        raise Failure("Record count changed within immutable snapshot", 3)
    items = page.get("items")
    cursor = page.get("next_cursor")
    if (not isinstance(items, list) or len(items) > 3 or "next_cursor" not in page
            or (cursor is not None and (not isinstance(cursor, str) or not cursor))
            or (not items and cursor is not None)):
        raise Failure("Invalid page shape", 3)
    if cursor is not None and (cursor == state["next_cursor"] or cursor in state["consumed_cursors"]):
        raise Failure("Cursor cycle; cannot establish complete coverage", 3)
    # Work on an independent copy: a validation failure must not mutate durable progress.
    updated = json.loads(json.dumps(state))
    seen = set(updated["seen_entry_ids"])
    fields = {"entry_id", "vendor_id", "posted_on", "kind", "status", "amount_cents", "currency"}
    for row in items:
        if (not isinstance(row, dict) or set(row) != fields
                or not isinstance(row["entry_id"], str) or not row["entry_id"]
                or not isinstance(row["vendor_id"], str) or not row["vendor_id"]
                or row["kind"] not in ("charge", "credit")
                or row["status"] not in ("settled", "pending", "void")
                or type(row["amount_cents"]) is not int or row["amount_cents"] < 0
                or row["currency"] != "USD"):
            raise Failure("Entry violates ledger contract", 3)
        date(row["posted_on"])
        if row["entry_id"] in seen:
            raise Failure("Duplicate entry in disjoint page chain; checkpoint not advanced", 3)
        seen.add(row["entry_id"])
        updated["seen_entry_ids"].append(row["entry_id"])
        if row["status"] == "settled" and state["start"] <= row["posted_on"] <= state["end"]:
            vendor = updated["vendors"].setdefault(row["vendor_id"], {
                "charge_cents": 0, "credit_cents": 0, "qualifying_entry_count": 0})
            vendor[row["kind"] + "_cents"] += row["amount_cents"]
            vendor["qualifying_entry_count"] += 1
    if len(seen) > state["total_records"] or (cursor is None and len(seen) != state["total_records"]):
        raise Failure("Exhaustion/coverage count mismatch; result remains incomplete", 3)
    updated["consumed_cursors"].append(state["next_cursor"])
    updated["next_cursor"] = cursor
    updated["complete"] = cursor is None
    updated["pages_committed"] += 1
    updated["last_tranche"] = page["tranche"]
    return updated


def report(state, reason):
    vendors = [dict(vendor_id=key, **value, net_cents=value["charge_cents"] - value["credit_cents"])
               for key, value in sorted(state["vendors"].items())]
    return {"status": "complete" if state["complete"] else "incomplete", "reason": reason,
            "snapshot_id": state["snapshot_id"], "start": state["start"], "end": state["end"],
            "currency": "USD", "examined_records": len(state["seen_entry_ids"]),
            "total_records": state["total_records"], "pages_committed": state["pages_committed"],
            "next_cursor": state["next_cursor"], "last_tranche": state["last_tranche"],
            "vendors" if state["complete"] else "partial_vendors": vendors}


def run(args):
    date(args.start)
    date(args.end)
    if args.start > args.end:
        raise Failure("Invalid interval: start must be on or before end; no source traversal started")
    if args.tranche < 1:
        raise Failure("--tranche must be the positive operator-approved tranche number")
    args.api, args.source = str(Path(args.api).resolve()), str(Path(args.source).resolve())
    checkpoint, output = Path(args.checkpoint).resolve(), Path(args.output).resolve()
    lock = Path(str(checkpoint) + ".lock")
    paths = [Path(args.api), Path(args.source), checkpoint, output, lock]
    if len(set(paths)) != len(paths) or any(str(p) == args.source + "-journal" for p in (checkpoint, output, lock)):
        raise Failure("API, source, checkpoint, report, lock and source journal paths must be distinct")
    if not Path(args.api).is_file() or not Path(args.source).is_file():
        raise Failure("Supply the existing ledger API script and immutable source state")
    if not checkpoint.parent.is_dir() or not output.parent.is_dir():
        raise Failure("Checkpoint and output parent directories must already exist")
    identity = {"version": 1, "api": args.api, "source": args.source, "start": args.start, "end": args.end}
    with lock.open("a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Failure("Checkpoint is in use; wait for its runner to exit", 3)
        meta = metadata(args)
        if checkpoint.exists():
            state = json.loads(checkpoint.read_text())
            if any(state.get(key) != value for key, value in identity.items()):
                raise Failure("Checkpoint belongs to another request or source; do not reset it")
            if state["snapshot_id"] != meta["snapshot_id"] or state["total_records"] != meta["total_records"]:
                raise Failure("Checkpoint snapshot or source count mismatch", 4)
        else:
            state = dict(identity, snapshot_id=meta["snapshot_id"], total_records=meta["total_records"],
                         complete=False, next_cursor=None, seen_entry_ids=[], consumed_cursors=[],
                         pages_committed=0, last_tranche=None, vendors={})
            atomic_json(checkpoint, state)
        reason = "source_exhausted" if state["complete"] else "tranche_boundary"
        calls = 0
        while not state["complete"] and calls < 2:
            meta = metadata(args)
            if meta["snapshot_id"] != state["snapshot_id"] or meta["total_records"] != state["total_records"]:
                raise Failure("Source changed during traversal", 4)
            if meta["tranche"] != args.tranche:
                reason = "approved_tranche_not_current"
                break
            if meta["remaining_calls"] == 0:
                reason = "call_budget_exhausted"
                break
            extra = ["--snapshot", state["snapshot_id"]]
            if state["next_cursor"] is not None:
                extra += ["--cursor", state["next_cursor"]]
            try:
                page = api(args, "page", *extra)
            except Failure as error:
                if error.code != 75:
                    raise
                reason = "call_budget_exhausted"
                break
            calls += 1
            if page.get("tranche") != args.tranche:
                raise Failure("Operator changed tranche during execution; stop concurrent source control", 3)
            updated = incorporate(state, page)
            atomic_json(checkpoint, updated)
            state = updated
        if state["complete"]:
            reason = "source_exhausted"
        body = report(state, reason)
        atomic_json(output, body)
        print(json.dumps({key: value for key, value in body.items() if key not in ("vendors", "partial_vendors")} | {
            "output": str(output), "checkpoint": str(checkpoint), "successful_calls_this_run": calls}))
        return 0 if state["complete"] else 75


def main():
    parser = argparse.ArgumentParser(description=__doc__, epilog=(
        "Example: python3.12 rollup.py --api /path/ledger_api.py --source /path/source.sqlite "
        "--checkpoint /path/job.json --output /path/report.json --start 2026-02-01 --end 2026-02-15 --tranche 1. "
        "Exit 0 complete, 75 incomplete/pause, 2 invalid input/state, 3 source/recovery error, 4 snapshot mismatch. "
        "Only run in an operator-approved tranche; no quota grants are performed."))
    for name, help_text in {
        "api": "Existing supplied ledger_api.py path", "source": "Existing immutable source SQLite state",
        "checkpoint": "Durable job JSON path; reused unchanged for continuation",
        "output": "JSON result path to atomically replace (full vendor list stays in this file)",
        "start": "Inclusive YYYY-MM-DD posting start", "end": "Inclusive YYYY-MM-DD posting end",
    }.items():
        parser.add_argument("--" + name, required=True, help=help_text)
    parser.add_argument("--tranche", type=int, required=True, help="Current operator-approved tranche number")
    args = parser.parse_args()
    try:
        return run(args)
    except (Failure, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "error", "error": str(error),
                          "action": "Do not treat an older report as the result of this invocation. Preserve checkpoint; inspect source metadata before recovery."}))
        return error.code if isinstance(error, Failure) else 2


if __name__ == "__main__":
    sys.exit(main())
