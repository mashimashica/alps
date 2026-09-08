#!/usr/bin/env python3
"""Exact, resumable ledger rollup via the supplied paginated CLI only."""
import argparse
import datetime
import json
from pathlib import Path
import sqlite3
import subprocess
import sys


class Failure(Exception):
    def __init__(self, message, code=2):
        self.code = code
        super().__init__(message)


def iso(value):
    if not isinstance(value, str) or datetime.date.fromisoformat(value).isoformat() != value:
        raise ValueError("dates must have exact YYYY-MM-DD form")
    return value


def api(args, command, *extra):
    try:
        result = subprocess.run(
            [sys.executable, str(args.api), "--state", str(args.source), command, *extra],
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Failure("response_unavailable: " + str(exc)) from exc
    if result.returncode:
        if result.returncode == 75:
            raise Failure("call_budget_exhausted", 75)
        if result.returncode == 4:
            raise Failure("snapshot_mismatch", 4)
        raise Failure("API error: " + result.stdout.strip() + result.stderr.strip())
    try:
        body = json.loads(result.stdout)
        if not isinstance(body, dict):
            raise ValueError("expected object")
        return body
    except ValueError as exc:
        raise Failure("response_unavailable: invalid JSON; call may have been counted") from exc


def metadata(args):
    data = api(args, "describe")
    if not isinstance(data.get("snapshot_id"), str) or not data["snapshot_id"]:
        raise Failure("invalid snapshot metadata")
    for key in ("total_records", "page_size", "calls_per_tranche", "tranche", "remaining_calls"):
        if type(data.get(key)) is not int or data[key] < 0:
            raise Failure("invalid metadata: " + key)
    if data["page_size"] != 3 or data["calls_per_tranche"] != 2 or data["remaining_calls"] > 2:
        raise Failure("unsupported source quota/page contract")
    return data


def store(db, state):
    db.execute("INSERT OR REPLACE INTO state VALUES (1, ?)", (json.dumps(state),))


def report(db, state, reason=None, remaining=None):
    rows = []
    for vendor, charges, credits, count in db.execute("SELECT * FROM vendors ORDER BY vendor_id"):
        rows.append({"vendor_id": vendor, "settled_charge_cents": int(charges),
                     "settled_credit_cents": int(credits), "net_cents": int(charges) - int(credits),
                     "qualifying_entry_count": count})
    result = {"complete": state["complete"], "snapshot_id": state["snapshot"],
              "interval": {"start": state["start"], "end": state["end"], "inclusive": True},
              "currency": "USD", "examined_records": db.execute("SELECT COUNT(*) FROM entries").fetchone()[0],
              "total_records": state["total"], "committed_pages": db.execute("SELECT COUNT(*) FROM pages").fetchone()[0],
              "checkpoint": state["checkpoint"], "vendors": rows}
    if reason:
        result.update(reason=reason, remaining_calls=remaining, totals_are_final=False)
    return result


def apply_page(db, state, page, tranche):
    if page.get("snapshot_id") != state["snapshot"] or page.get("total_records") != state["total"]:
        raise Failure("page snapshot/count mismatch")
    if type(page.get("tranche")) is not int or page["tranche"] != tranche:
        raise Failure("tranche changed during page call; preserve checkpoint and retry later")
    if "next_cursor" not in page or not isinstance(page.get("items"), list):
        raise Failure("invalid page contract")
    cursor = page["next_cursor"]
    if cursor is not None and (not isinstance(cursor, str) or not cursor):
        raise Failure("invalid returned cursor")
    if len(page["items"]) > 3 or (not page["items"] and cursor is not None):
        raise Failure("invalid page size or empty nonterminal page")
    # JSON encoding distinguishes the initial null cursor from every string.
    db.execute("INSERT INTO pages VALUES (?)", (json.dumps(state["next_cursor"]),))
    if cursor is not None and db.execute("SELECT 1 FROM pages WHERE cursor=?", (json.dumps(cursor),)).fetchone():
        raise Failure("cursor cycle")
    fields = {"entry_id", "vendor_id", "posted_on", "kind", "status", "amount_cents", "currency"}
    for item in page["items"]:
        if not isinstance(item, dict) or set(item) != fields:
            raise Failure("invalid record fields")
        for key in ("entry_id", "vendor_id"):
            if not isinstance(item[key], str) or not item[key]:
                raise Failure("invalid " + key)
        iso(item["posted_on"])
        if item["kind"] not in ("charge", "credit") or item["status"] not in ("settled", "pending", "void"):
            raise Failure("invalid kind/status")
        if type(item["amount_cents"]) is not int or item["amount_cents"] < 0 or item["currency"] != "USD":
            raise Failure("invalid integer USD amount")
        db.execute("INSERT INTO entries VALUES (?)", (item["entry_id"],))
        if item["status"] != "settled" or not state["start"] <= item["posted_on"] <= state["end"]:
            continue
        vendor = item["vendor_id"]
        previous = db.execute("SELECT charges, credits, count FROM vendors WHERE vendor_id=?", (vendor,)).fetchone()
        charges, credits, count = (int(previous[0]), int(previous[1]), previous[2]) if previous else (0, 0, 0)
        if item["kind"] == "charge":
            charges += item["amount_cents"]
        else:
            credits += item["amount_cents"]
        # Store amounts as TEXT, avoiding SQLite's signed 64-bit arithmetic limit.
        db.execute("INSERT OR REPLACE INTO vendors VALUES (?, ?, ?, ?)", (vendor, str(charges), str(credits), count + 1))
    examined = db.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    if examined > state["total"] or (cursor is None and examined != state["total"]):
        raise Failure("coverage mismatch")
    state["next_cursor"] = cursor
    state["complete"] = cursor is None
    store(db, state)


def run(args):
    iso(args.start)
    iso(args.end)
    if args.start > args.end:
        raise Failure("start date must not be after end date")
    for key in ("api", "source", "checkpoint"):
        setattr(args, key, Path(getattr(args, key)).resolve())
    if not args.api.is_file() or not args.source.is_file():
        raise Failure("supply an existing API script and source state")
    if args.checkpoint in (args.api, args.source) or any(
        args.checkpoint.exists() and args.checkpoint.samefile(path) for path in (args.api, args.source)
    ):
        raise Failure("checkpoint must be separate from API and source")
    identity = {"version": 1, "api": str(args.api), "source": str(args.source),
                "checkpoint": str(args.checkpoint), "start": args.start, "end": args.end}
    db = sqlite3.connect(args.checkpoint, timeout=2, isolation_level=None)
    try:
        db.execute("PRAGMA synchronous=FULL")
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS entries (entry_id TEXT PRIMARY KEY)")
        db.execute("CREATE TABLE IF NOT EXISTS pages (cursor TEXT PRIMARY KEY)")
        db.execute("CREATE TABLE IF NOT EXISTS vendors (vendor_id TEXT PRIMARY KEY, charges TEXT, credits TEXT, count INTEGER)")
        row = db.execute("SELECT payload FROM state WHERE id=1").fetchone()
        state = json.loads(row[0]) if row else None
        if state and any(state.get(key) != value for key, value in identity.items()):
            raise Failure("checkpoint request/source binding mismatch")
        desc = metadata(args)
        if state is None:
            state = {**identity, "snapshot": desc["snapshot_id"], "total": desc["total_records"],
                     "next_cursor": None, "complete": False}
            store(db, state)
        if state["snapshot"] != desc["snapshot_id"] or state["total"] != desc["total_records"]:
            raise Failure("snapshot_mismatch", 4)
        db.commit()
        initial_tranche = desc["tranche"]
        successes = 0
        while True:
            db.execute("BEGIN IMMEDIATE")
            # Re-read after taking the lock; another invocation may have progressed.
            state = json.loads(db.execute("SELECT payload FROM state WHERE id=1").fetchone()[0])
            if state["complete"]:
                return report(db, state), 0
            desc = metadata(args)
            if desc["snapshot_id"] != state["snapshot"] or desc["total_records"] != state["total"]:
                raise Failure("snapshot_mismatch", 4)
            if not desc["remaining_calls"] or desc["tranche"] != initial_tranche or successes >= 2:
                reason = "await_operator_tranche" if not desc["remaining_calls"] else "execution_boundary"
                return report(db, state, reason, desc["remaining_calls"]), 75
            extra = ["--snapshot", state["snapshot"]]
            if state["next_cursor"] is not None:
                extra += ["--cursor", state["next_cursor"]]
            try:
                page = api(args, "page", *extra)
            except Failure as exc:
                if exc.code == 75:
                    return report(db, state, "await_operator_tranche", 0), 75
                raise
            apply_page(db, state, page, initial_tranche)
            db.commit()
            successes += 1
    finally:
        if db.in_transaction:
            db.rollback()
        db.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", required=True, help="trusted supplied ledger_api.py")
    parser.add_argument("--source", required=True, help="existing source SQLite state; accessed only via API")
    parser.add_argument("--checkpoint", required=True, help="dedicated durable SQLite checkpoint; reused on continuation")
    parser.add_argument("--start", required=True, help="inclusive YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="inclusive YYYY-MM-DD")
    args = parser.parse_args()
    try:
        result, code = run(args)
    except (Failure, ValueError, TypeError, KeyError, OSError, sqlite3.Error) as exc:
        result, code = {"complete": False, "error": str(exc), "checkpoint": args.checkpoint}, getattr(exc, "code", 2)
    print(json.dumps(result, sort_keys=True, default=str))
    return code


if __name__ == "__main__":
    sys.exit(main())
