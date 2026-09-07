#!/usr/bin/env python3
"""Checkpointed, exact vendor rollup over the supplied ledger API."""

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ITEM_FIELDS = {"entry_id", "vendor_id", "posted_on", "kind", "status", "amount_cents", "currency"}


class RollupError(Exception):
    pass


def emit(value):
    print(json.dumps(value, sort_keys=True, separators=(",", ":")))


def iso_date(value, label):
    try:
        parsed = dt.date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise RollupError(f"invalid {label}: expected YYYY-MM-DD calendar date") from exc
    if parsed.isoformat() != value:
        raise RollupError(f"invalid {label}: expected canonical YYYY-MM-DD")
    return parsed


def api_call(api, state, command, snapshot=None, cursor=None):
    argv = [sys.executable, str(api), "--state", str(state), command]
    if snapshot is not None:
        argv += ["--snapshot", snapshot]
    if cursor is not None:
        argv += ["--cursor", cursor]
    result = subprocess.run(argv, text=True, capture_output=True)
    try:
        body = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RollupError(f"API {command} returned non-JSON output (exit {result.returncode})") from exc
    if result.returncode:
        return result.returncode, body
    if not isinstance(body, dict):
        raise RollupError(f"API {command} response must be a JSON object")
    return 0, body


def atomic_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, sort_keys=True, separators=(",", ":"))
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def validate_description(body):
    required = {"snapshot_id", "total_records", "page_size", "calls_per_tranche", "tranche", "remaining_calls"}
    if not required <= set(body):
        raise RollupError("describe response is missing required fields")
    if not isinstance(body["snapshot_id"], str) or not body["snapshot_id"]:
        raise RollupError("describe returned an invalid snapshot_id")
    for key in ("total_records", "page_size", "calls_per_tranche", "tranche", "remaining_calls"):
        if type(body[key]) is not int or body[key] < 0:
            raise RollupError(f"describe returned invalid {key}")


def new_checkpoint(snapshot, total, start, end):
    return {"version": 1, "snapshot_id": snapshot, "total_records": total,
            "start": start, "end": end, "next_cursor": None, "started": False,
            "complete": False, "entries": {}}


def load_checkpoint(path):
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise RollupError(f"cannot read checkpoint: {exc}") from exc
    required = {"version", "snapshot_id", "total_records", "start", "end", "next_cursor", "started", "complete", "entries"}
    if not isinstance(value, dict) or set(value) != required or value["version"] != 1:
        raise RollupError("checkpoint has an unsupported or malformed structure")
    if not isinstance(value["entries"], dict):
        raise RollupError("checkpoint entries must be an object")
    return value


def validate_item(item):
    if not isinstance(item, dict) or set(item) != ITEM_FIELDS:
        raise RollupError("page item fields do not match the ledger contract")
    if not isinstance(item["entry_id"], str) or not item["entry_id"]:
        raise RollupError("invalid entry_id")
    if not isinstance(item["vendor_id"], str) or not item["vendor_id"]:
        raise RollupError("invalid vendor_id")
    iso_date(item["posted_on"], "posted_on")
    if item["kind"] not in ("charge", "credit") or item["status"] not in ("settled", "pending", "void"):
        raise RollupError("invalid kind or status")
    if type(item["amount_cents"]) is not int or item["amount_cents"] < 0 or item["currency"] != "USD":
        raise RollupError("invalid integer USD amount")


def incorporate(checkpoint, page):
    required = {"snapshot_id", "items", "next_cursor", "total_records", "tranche"}
    if not isinstance(page, dict) or set(page) != required:
        raise RollupError("page response fields do not match the API contract")
    if page["snapshot_id"] != checkpoint["snapshot_id"] or page["total_records"] != checkpoint["total_records"]:
        raise RollupError("page metadata changed during traversal")
    if not isinstance(page["items"], list):
        raise RollupError("page items must be a list")
    if page["next_cursor"] is not None and (not isinstance(page["next_cursor"], str) or not page["next_cursor"]):
        raise RollupError("invalid next_cursor")
    for item in page["items"]:
        validate_item(item)
        old = checkpoint["entries"].get(item["entry_id"])
        if old is not None and old != item:
            raise RollupError(f"entry_id {item['entry_id']} changed on replay")
        checkpoint["entries"][item["entry_id"]] = item
    checkpoint["started"] = True
    checkpoint["next_cursor"] = page["next_cursor"]
    checkpoint["complete"] = page["next_cursor"] is None


def vendors(checkpoint):
    result = {}
    for item in checkpoint["entries"].values():
        if item["status"] != "settled" or not (checkpoint["start"] <= item["posted_on"] <= checkpoint["end"]):
            continue
        row = result.setdefault(item["vendor_id"], {"vendor_id": item["vendor_id"],
            "settled_charge_amount_cents": 0, "settled_credit_amount_cents": 0,
            "net_amount_cents": 0, "qualifying_entry_count": 0})
        key = "settled_charge_amount_cents" if item["kind"] == "charge" else "settled_credit_amount_cents"
        row[key] += item["amount_cents"]
        row["qualifying_entry_count"] += 1
    for row in result.values():
        row["net_amount_cents"] = row["settled_charge_amount_cents"] - row["settled_credit_amount_cents"]
    return [result[key] for key in sorted(result)]


def report(checkpoint, description):
    base = {"snapshot_id": checkpoint["snapshot_id"],
            "interval": {"start": checkpoint["start"], "end": checkpoint["end"]},
            "source_records_examined": len(checkpoint["entries"]),
            "source_total_records": checkpoint["total_records"]}
    rows = vendors(checkpoint)
    if checkpoint["complete"]:
        if len(checkpoint["entries"]) != checkpoint["total_records"]:
            raise RollupError("source exhausted but distinct examined entry count does not match total_records")
        return {"status": "complete", **base, "vendors": rows}
    return {"status": "incomplete", "reason": "tranche_capacity_required", **base,
            "next_cursor": checkpoint["next_cursor"], "partial_vendors": rows,
            "tranche": description["tranche"], "remaining_calls": description["remaining_calls"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", required=True, type=Path)
    parser.add_argument("--source-state", required=True, type=Path)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    args = parser.parse_args()
    try:
        start = iso_date(args.start, "start")
        end = iso_date(args.end, "end")
        if start > end:
            raise RollupError("invalid interval: start is after end")
        code, description = api_call(args.api, args.source_state, "describe")
        if code:
            raise RollupError(f"API describe failed (exit {code}): {description}")
        validate_description(description)
        if args.checkpoint.exists():
            checkpoint = load_checkpoint(args.checkpoint)
            expected = (description["snapshot_id"], description["total_records"], args.start, args.end)
            actual = (checkpoint["snapshot_id"], checkpoint["total_records"], checkpoint["start"], checkpoint["end"])
            if actual != expected:
                raise RollupError("checkpoint does not match this snapshot, record count, or interval")
        else:
            checkpoint = new_checkpoint(description["snapshot_id"], description["total_records"], args.start, args.end)
            atomic_write(args.checkpoint, checkpoint)
        while not checkpoint["complete"] and description["remaining_calls"] > 0:
            cursor = checkpoint["next_cursor"] if checkpoint["started"] else None
            code, page = api_call(args.api, args.source_state, "page", checkpoint["snapshot_id"], cursor)
            if code == 75 and isinstance(page, dict) and page.get("error") == "call_budget_exhausted":
                break
            if code:
                raise RollupError(f"API page failed (exit {code}): {page}")
            incorporate(checkpoint, page)
            atomic_write(args.checkpoint, checkpoint)
            code, description = api_call(args.api, args.source_state, "describe")
            if code:
                raise RollupError(f"API describe failed after page (exit {code}): {description}")
            validate_description(description)
        emit(report(checkpoint, description))
        return 0
    except RollupError as exc:
        emit({"status": "error", "error": str(exc)})
        return 2


if __name__ == "__main__":
    sys.exit(main())
