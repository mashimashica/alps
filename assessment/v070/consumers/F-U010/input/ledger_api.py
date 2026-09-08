#!/usr/bin/env python3
"""Original local paginated-ledger stand-in; not a target Skill implementation."""

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys

PAGE_SIZE = 3
CALLS_PER_TRANCHE = 2


class ApiError(Exception):
    def __init__(self, code, error, **details):
        self.code = code
        self.body = {"error": error, **details}


def emit(body):
    print(json.dumps(body, sort_keys=True, separators=(",", ":")))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def cursor_for(snapshot, offset):
    value = f"{snapshot}:{offset}".encode()
    return "p_" + hashlib.sha256(value).hexdigest()[:32]


def read_fixture(path):
    source = json.loads(Path(path).read_text())
    if not isinstance(source, dict) or set(source) != {"records"}:
        raise ValueError("fixture must contain only a records list")
    rows = source["records"]
    if not isinstance(rows, list):
        raise ValueError("records must be a list")
    seen = set()
    fields = {"entry_id", "vendor_id", "posted_on", "kind", "status", "amount_cents", "currency"}
    for row in rows:
        if not isinstance(row, dict) or set(row) != fields:
            raise ValueError("record fields do not match the interface")
        for field in ("entry_id", "vendor_id"):
            if not isinstance(row[field], str) or not row[field]:
                raise ValueError(f"invalid {field}")
        if row["entry_id"] in seen:
            raise ValueError("entry IDs must be unique")
        seen.add(row["entry_id"])
        if datetime.date.fromisoformat(row["posted_on"]).isoformat() != row["posted_on"]:
            raise ValueError("posted_on must be an ISO calendar date")
        if row["kind"] not in ("charge", "credit") or row["status"] not in ("settled", "pending", "void"):
            raise ValueError("invalid kind or status")
        if type(row["amount_cents"]) is not int or row["amount_cents"] < 0 or row["currency"] != "USD":
            raise ValueError("invalid integer USD amount")
    return rows


def initialize(path, fixture):
    rows = read_fixture(fixture)
    snapshot = "snap_" + hashlib.sha256(canonical(rows).encode()).hexdigest()[:24]
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(descriptor)
    with sqlite3.connect(path) as connection:
        connection.executescript("""
            PRAGMA journal_mode = DELETE;
            CREATE TABLE source_state (
                singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                snapshot_id TEXT NOT NULL, tranche INTEGER NOT NULL,
                calls_used INTEGER NOT NULL CHECK (calls_used >= 0)
            );
            CREATE TABLE records (position INTEGER PRIMARY KEY, payload TEXT NOT NULL);
        """)
        connection.execute("INSERT INTO source_state VALUES (1, ?, 1, 0)", (snapshot,))
        connection.executemany("INSERT INTO records VALUES (?, ?)", enumerate(map(canonical, rows)))
    emit({"state": "ready", "snapshot_id": snapshot, "total_records": len(rows)})


def run(args):
    path = Path(args.state).resolve()
    if args.command == "init":
        initialize(path, args.fixture)
        return
    connection = sqlite3.connect(path.as_uri() + "?mode=rw", uri=True, timeout=0.5)
    try:
        connection.execute("BEGIN IMMEDIATE" if args.command != "describe" else "BEGIN")
        snapshot, tranche, used = connection.execute(
            "SELECT snapshot_id, tranche, calls_used FROM source_state WHERE singleton = 1"
        ).fetchone()
        total = connection.execute("SELECT COUNT(*) FROM records").fetchone()[0]
        if args.command == "describe":
            emit({"snapshot_id": snapshot, "total_records": total, "page_size": PAGE_SIZE,
                  "calls_per_tranche": CALLS_PER_TRANCHE, "tranche": tranche,
                  "remaining_calls": max(0, CALLS_PER_TRANCHE - used)})
            return
        if args.command == "grant-tranche":
            connection.execute("UPDATE source_state SET tranche = tranche + 1, calls_used = 0")
            connection.commit()
            emit({"state": "tranche_granted", "tranche": tranche + 1, "remaining_calls": CALLS_PER_TRANCHE})
            return
        if args.snapshot != snapshot:
            raise ApiError(4, "snapshot_mismatch")
        cursors = {cursor_for(snapshot, offset): offset for offset in range(PAGE_SIZE, total, PAGE_SIZE)}
        if args.cursor is not None and args.cursor not in cursors:
            raise ApiError(2, "invalid_cursor")
        offset = 0 if args.cursor is None else cursors[args.cursor]
        if used >= CALLS_PER_TRANCHE:
            raise ApiError(75, "call_budget_exhausted", tranche=tranche, remaining_calls=0)
        items = [json.loads(row[0]) for row in connection.execute(
            "SELECT payload FROM records ORDER BY position LIMIT ? OFFSET ?", (PAGE_SIZE, offset)
        )]
        next_offset = offset + len(items)
        following = cursor_for(snapshot, next_offset) if next_offset < total else None
        connection.execute("UPDATE source_state SET calls_used = calls_used + 1")
        connection.commit()
        emit({"snapshot_id": snapshot, "items": items, "next_cursor": following,
              "total_records": total, "tranche": tranche})
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True, help="explicit local SQLite state path")
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="create new state from original synthetic setup data")
    init.add_argument("--fixture", required=True)
    commands.add_parser("describe", help="read unmetered metadata")
    commands.add_parser("grant-tranche", help="operator-only simulator control")
    page = commands.add_parser("page", help="fetch one metered page")
    page.add_argument("--snapshot", required=True)
    page.add_argument("--cursor")
    args = parser.parse_args()
    try:
        run(args)
    except ApiError as error:
        emit(error.body)
        return error.code
    except (OSError, ValueError, TypeError, sqlite3.Error) as error:
        emit({"error": "state_or_input_error", "detail": str(error)})
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
