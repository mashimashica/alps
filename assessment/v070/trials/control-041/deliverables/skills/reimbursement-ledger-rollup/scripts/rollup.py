#!/usr/bin/env python3
"""Complete, resumable vendor rollup over the supplied ledger CLI."""

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

FIELDS = {"entry_id", "vendor_id", "posted_on", "kind", "status", "amount_cents", "currency"}


class RollupError(Exception):
    pass


def iso_date(value):
    try:
        parsed = dt.date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("must be a valid ISO date (YYYY-MM-DD)") from exc
    if parsed.isoformat() != value:
        raise argparse.ArgumentTypeError("must be a valid ISO date (YYYY-MM-DD)")
    return value


def call(api, state, command, snapshot=None, cursor=None):
    argv = [sys.executable, api, "--state", state, command]
    if snapshot is not None:
        argv += ["--snapshot", snapshot]
    if cursor is not None:
        argv += ["--cursor", cursor]
    proc = subprocess.run(argv, text=True, capture_output=True)
    try:
        body = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RollupError(f"API returned non-JSON output (exit {proc.returncode})") from exc
    if not isinstance(body, dict):
        raise RollupError("API response must be a JSON object")
    return proc.returncode, body


def atomic_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w") as stream:
            json.dump(value, stream, sort_keys=True, separators=(",", ":"))
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def validate_description(body):
    required = {"snapshot_id", "total_records", "page_size", "calls_per_tranche", "tranche", "remaining_calls"}
    if not required <= set(body) or not isinstance(body["snapshot_id"], str) or not body["snapshot_id"]:
        raise RollupError("invalid describe response")
    for key in ("total_records", "page_size", "calls_per_tranche", "tranche", "remaining_calls"):
        if type(body[key]) is not int or body[key] < 0:
            raise RollupError("invalid describe response")


def validate_item(item):
    if not isinstance(item, dict) or set(item) != FIELDS:
        raise RollupError("record fields do not match contract")
    if not isinstance(item["entry_id"], str) or not item["entry_id"]:
        raise RollupError("invalid entry_id")
    if not isinstance(item["vendor_id"], str) or not item["vendor_id"]:
        raise RollupError("invalid vendor_id")
    try:
        if dt.date.fromisoformat(item["posted_on"]).isoformat() != item["posted_on"]:
            raise ValueError
    except (TypeError, ValueError) as exc:
        raise RollupError("invalid posted_on") from exc
    if item["kind"] not in ("charge", "credit") or item["status"] not in ("settled", "pending", "void"):
        raise RollupError("invalid kind or status")
    if type(item["amount_cents"]) is not int or item["amount_cents"] < 0 or item["currency"] != "USD":
        raise RollupError("invalid integer USD amount")


def validate_page(body, snapshot, total):
    required = {"snapshot_id", "items", "next_cursor", "total_records", "tranche"}
    if set(body) != required or body["snapshot_id"] != snapshot or body["total_records"] != total:
        raise RollupError("page metadata does not match checkpointed snapshot")
    if not isinstance(body["items"], list):
        raise RollupError("page items must be a list")
    if body["next_cursor"] is not None and (not isinstance(body["next_cursor"], str) or not body["next_cursor"]):
        raise RollupError("invalid next_cursor")
    if type(body["tranche"]) is not int or body["tranche"] < 0:
        raise RollupError("invalid page tranche")
    for item in body["items"]:
        validate_item(item)


def initial_checkpoint(args, description):
    return {
        "version": 1,
        "request": {"from_date": args.from_date, "through_date": args.through_date,
                    "api": str(Path(args.api).resolve()), "state": str(Path(args.state).resolve())},
        "snapshot_id": description["snapshot_id"], "total_records": description["total_records"],
        "next_cursor": None, "started": False, "exhausted": False, "seen": {}, "vendors": {}
    }


def load_checkpoint(path):
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise RollupError(f"cannot read checkpoint: {exc}") from exc
    if not isinstance(value, dict) or value.get("version") != 1:
        raise RollupError("unsupported or invalid checkpoint")
    return value


def incorporate(checkpoint, items, start, end):
    for item in items:
        entry_id = item["entry_id"]
        canonical = json.dumps(item, sort_keys=True, separators=(",", ":"))
        previous = checkpoint["seen"].get(entry_id)
        if previous is not None:
            if previous != canonical:
                raise RollupError(f"entry_id {entry_id!r} changed across repeated pages")
            continue
        checkpoint["seen"][entry_id] = canonical
        if item["status"] != "settled" or not (start <= item["posted_on"] <= end):
            continue
        totals = checkpoint["vendors"].setdefault(item["vendor_id"], {"charges": 0, "credits": 0, "count": 0})
        totals["charges" if item["kind"] == "charge" else "credits"] += item["amount_cents"]
        totals["count"] += 1


def result(checkpoint):
    vendors = []
    for vendor_id in sorted(checkpoint["vendors"]):
        totals = checkpoint["vendors"][vendor_id]
        vendors.append({"vendor_id": vendor_id, "settled_charge_cents": totals["charges"],
                        "settled_credit_cents": totals["credits"],
                        "net_cents": totals["charges"] - totals["credits"],
                        "qualifying_entry_count": totals["count"]})
    return vendors


def emit(value, output):
    rendered = json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    if output:
        Path(output).write_text(rendered)
    sys.stdout.write(rendered)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", required=True, help="ledger_api.py path")
    parser.add_argument("--state", required=True, help="existing immutable source state")
    parser.add_argument("--checkpoint", required=True, help="durable per-request progress JSON")
    parser.add_argument("--from-date", required=True, type=iso_date)
    parser.add_argument("--through-date", required=True, type=iso_date)
    parser.add_argument("--output", help="also write the current status JSON here")
    args = parser.parse_args()
    if args.from_date > args.through_date:
        parser.error("--from-date must be on or before --through-date")
    try:
        code, description = call(args.api, args.state, "describe")
        if code != 0:
            raise RollupError(f"describe failed with exit {code}: {description.get('error', 'unknown_error')}")
        validate_description(description)
        checkpoint_path = Path(args.checkpoint)
        expected = {"from_date": args.from_date, "through_date": args.through_date,
                    "api": str(Path(args.api).resolve()), "state": str(Path(args.state).resolve())}
        checkpoint = load_checkpoint(checkpoint_path) if checkpoint_path.exists() else initial_checkpoint(args, description)
        if checkpoint.get("request") != expected:
            raise RollupError("checkpoint belongs to a different request")
        if checkpoint.get("snapshot_id") != description["snapshot_id"] or checkpoint.get("total_records") != description["total_records"]:
            raise RollupError("source snapshot or record count changed")
        if checkpoint.get("exhausted"):
            status = {"status": "complete", "snapshot_id": checkpoint["snapshot_id"],
                      "date_interval": {"from": args.from_date, "through": args.through_date},
                      "vendors": result(checkpoint), "source_records_examined": len(checkpoint["seen"])}
            emit(status, args.output)
            return 0

        calls_available = description["remaining_calls"]
        for _ in range(calls_available):
            cursor = checkpoint["next_cursor"] if checkpoint["started"] else None
            code, page = call(args.api, args.state, "page", checkpoint["snapshot_id"], cursor)
            if code == 75 and page.get("error") == "call_budget_exhausted":
                break
            if code != 0:
                raise RollupError(f"page call failed with exit {code}: {page.get('error', 'unknown_error')}")
            validate_page(page, checkpoint["snapshot_id"], checkpoint["total_records"])
            incorporate(checkpoint, page["items"], args.from_date, args.through_date)
            checkpoint["started"] = True
            checkpoint["next_cursor"] = page["next_cursor"]
            checkpoint["exhausted"] = page["next_cursor"] is None
            atomic_write(checkpoint_path, checkpoint)
            if checkpoint["exhausted"]:
                break

        if checkpoint["exhausted"]:
            if len(checkpoint["seen"]) != checkpoint["total_records"]:
                raise RollupError("exhausted source count differs from metadata")
            status = {"status": "complete", "snapshot_id": checkpoint["snapshot_id"],
                      "date_interval": {"from": args.from_date, "through": args.through_date},
                      "vendors": result(checkpoint), "source_records_examined": len(checkpoint["seen"])}
            emit(status, args.output)
            return 0
        atomic_write(checkpoint_path, checkpoint)
        emit({"status": "incomplete", "snapshot_id": checkpoint["snapshot_id"],
              "date_interval": {"from": args.from_date, "through": args.through_date},
              "source_records_examined": len(checkpoint["seen"]),
              "message": "Source is not exhausted; retain checkpoint and continue only in a later approved tranche."}, args.output)
        return 75
    except RollupError as exc:
        emit({"status": "error", "error": str(exc)}, args.output)
        return 2


if __name__ == "__main__":
    sys.exit(main())
