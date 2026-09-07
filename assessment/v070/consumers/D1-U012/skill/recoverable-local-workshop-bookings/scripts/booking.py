#!/usr/bin/env python3
"""Original local booking stand-in; all mutations stay in an explicit state DB."""

import argparse
import datetime
import json
import os
from pathlib import Path
import re
import sqlite3
import sys

IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}\Z", re.ASCII)
UNAVAILABLE = "outcome unavailable; reconcile using the same request key"


class BookingError(Exception):
    def __init__(self, code, error, **details):
        self.code = code
        self.body = {"error": error, **details}


class OutcomeUnavailable(Exception):
    pass


def emit(body):
    print(json.dumps(body, sort_keys=True, separators=(",", ":")))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def check_identifier(value):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ValueError("identifier must match [A-Za-z0-9][A-Za-z0-9._-]{0,79}")
    return value


def initialize(path, fixture):
    source = json.loads(Path(fixture).read_text())
    if not isinstance(source, dict) or set(source) != {"slots"} or not isinstance(source["slots"], list):
        raise ValueError("fixture must contain only a slots list")
    seen = set()
    slots = []
    for slot in source["slots"]:
        if not isinstance(slot, dict) or set(slot) != {"slot_id", "starts_at", "capacity"}:
            raise ValueError("slot fields do not match the interface")
        slot_id = check_identifier(slot["slot_id"])
        if slot_id in seen:
            raise ValueError("slot IDs must be unique")
        seen.add(slot_id)
        if not isinstance(slot["starts_at"], str) or not slot["starts_at"].endswith("Z"):
            raise ValueError("starts_at must be an ISO UTC timestamp ending in Z")
        datetime.datetime.fromisoformat(slot["starts_at"].replace("Z", "+00:00"))
        capacity = slot["capacity"]
        if type(capacity) is not int or not 1 <= capacity <= 100:
            raise ValueError("capacity must be an integer from 1 through 100")
        slots.append((slot_id, slot["starts_at"], capacity, capacity))
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(descriptor)
    with sqlite3.connect(path) as connection:
        connection.executescript("""
            PRAGMA journal_mode = DELETE;
            CREATE TABLE slots (
                slot_id TEXT PRIMARY KEY, starts_at TEXT NOT NULL,
                capacity INTEGER NOT NULL CHECK (capacity > 0),
                remaining INTEGER NOT NULL CHECK (remaining >= 0 AND remaining <= capacity)
            );
            CREATE TABLE operations (
                request_key TEXT PRIMARY KEY, payload TEXT NOT NULL, receipt TEXT NOT NULL
            );
        """)
        connection.executemany("INSERT INTO slots VALUES (?, ?, ?, ?)", slots)
    emit({"state": "ready", "slots": len(slots)})


def reserve(connection, args):
    for value in (args.request_key, args.party_id, args.slot_id):
        check_identifier(value)
    if not 1 <= args.seats <= 100:
        raise ValueError("seats must be an integer from 1 through 100")
    payload = {"party_id": args.party_id, "slot_id": args.slot_id, "seats": args.seats}
    connection.execute("BEGIN IMMEDIATE")
    previous = connection.execute(
        "SELECT payload, receipt FROM operations WHERE request_key = ?", (args.request_key,)
    ).fetchone()
    if previous is not None:
        if previous[0] != canonical(payload):
            raise BookingError(3, "idempotency_conflict", request_key=args.request_key)
        connection.commit()
        emit({**json.loads(previous[1]), "replayed": True})
        return
    slot = connection.execute("SELECT remaining FROM slots WHERE slot_id = ?", (args.slot_id,)).fetchone()
    receipt = {"request_key": args.request_key, **payload}
    if slot is None:
        receipt.update(state="rejected", reason="unknown_slot")
    elif slot[0] < args.seats:
        receipt.update(state="rejected", reason="insufficient_capacity")
    else:
        connection.execute("UPDATE slots SET remaining = remaining - ? WHERE slot_id = ?", (args.seats, args.slot_id))
        receipt.update(state="confirmed", booking_id="booking:" + args.request_key)
    connection.execute("INSERT INTO operations VALUES (?, ?, ?)",
                       (args.request_key, canonical(payload), canonical(receipt)))
    if args.fault == "before-commit":
        connection.rollback()
        raise OutcomeUnavailable
    connection.commit()
    if args.fault == "after-commit":
        raise OutcomeUnavailable
    emit({**receipt, "replayed": False})


def run(args):
    path = Path(args.state).resolve()
    if args.command == "init":
        initialize(path, args.fixture)
        return
    connection = sqlite3.connect(path.as_uri() + "?mode=rw", uri=True, timeout=0.5)
    try:
        if args.command == "availability":
            fields = ("slot_id", "starts_at", "capacity", "remaining")
            rows = connection.execute("SELECT slot_id, starts_at, capacity, remaining FROM slots ORDER BY slot_id")
            emit({"slots": [dict(zip(fields, row)) for row in rows]})
        elif args.command == "lookup":
            check_identifier(args.request_key)
            row = connection.execute("SELECT receipt FROM operations WHERE request_key = ?", (args.request_key,)).fetchone()
            emit(json.loads(row[0]) if row else {"state": "not_seen", "request_key": args.request_key})
        else:
            reserve(connection, args)
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True, help="explicit local SQLite state path")
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="create new state from original synthetic setup data")
    init.add_argument("--fixture", required=True)
    commands.add_parser("availability", help="read point-in-time session availability")
    lookup = commands.add_parser("lookup", help="read a saved receipt by request key")
    lookup.add_argument("--request-key", required=True)
    book = commands.add_parser("reserve", help="idempotently attempt an atomic reservation")
    book.add_argument("--request-key", required=True)
    book.add_argument("--party-id", required=True)
    book.add_argument("--slot-id", required=True)
    book.add_argument("--seats", type=int, required=True)
    book.add_argument("--fault", choices=("before-commit", "after-commit"), help="simulator-only verification control")
    args = parser.parse_args()
    try:
        run(args)
    except OutcomeUnavailable:
        print(UNAVAILABLE, file=sys.stderr)
        return 75
    except BookingError as error:
        emit(error.body)
        return error.code
    except sqlite3.OperationalError as error:
        if "locked" in str(error).lower() or "busy" in str(error).lower():
            print(UNAVAILABLE, file=sys.stderr)
            return 75
        emit({"error": "state_or_input_error", "detail": str(error)})
        return 2
    except (OSError, ValueError, TypeError, sqlite3.Error) as error:
        emit({"error": "state_or_input_error", "detail": str(error)})
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
