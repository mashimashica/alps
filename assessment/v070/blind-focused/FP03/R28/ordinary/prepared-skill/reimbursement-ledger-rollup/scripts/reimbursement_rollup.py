#!/usr/bin/env python3
"""Traverse a tranche-limited ledger API and emit a complete reimbursement rollup."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


CHECKPOINT_VERSION = 1
ITEM_FIELDS = {
    "entry_id", "vendor_id", "posted_on", "kind", "status",
    "amount_cents", "currency",
}


class RollupError(Exception):
    """A request, checkpoint, source, or response failed validation."""


def emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, sort_keys=True, separators=(",", ":")))


def parse_date(value: str, label: str) -> dt.date:
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError as exc:
        raise RollupError(f"{label} must be a valid ISO date (YYYY-MM-DD)") from exc
    if parsed.isoformat() != value:
        raise RollupError(f"{label} must be a canonical ISO date (YYYY-MM-DD)")
    return parsed


def read_json_object(text: str, operation: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RollupError(f"{operation} returned invalid JSON; the page may have consumed a call") from exc
    if not isinstance(value, dict):
        raise RollupError(f"{operation} returned a non-object JSON value")
    return value


def run_api(api: Path, source_state: Path, arguments: list[str]) -> tuple[int, str, str]:
    completed = subprocess.run(
        [sys.executable, str(api), "--state", str(source_state), *arguments],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def require_int(value: Any, label: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise RollupError(f"invalid {label} in source response")
    return value


def validate_description(value: dict[str, Any]) -> dict[str, Any]:
    required = {
        "snapshot_id", "total_records", "page_size", "calls_per_tranche",
        "tranche", "remaining_calls",
    }
    if set(value) != required:
        raise RollupError("describe response fields do not match the contract")
    snapshot = value["snapshot_id"]
    if not isinstance(snapshot, str) or not snapshot:
        raise RollupError("invalid snapshot_id in describe response")
    total = require_int(value["total_records"], "total_records")
    page_size = require_int(value["page_size"], "page_size", minimum=1)
    allowance = require_int(value["calls_per_tranche"], "calls_per_tranche", minimum=1)
    tranche = require_int(value["tranche"], "tranche", minimum=1)
    remaining = require_int(value["remaining_calls"], "remaining_calls")
    if remaining > allowance:
        raise RollupError("remaining_calls exceeds calls_per_tranche")
    if allowance != 2:
        raise RollupError("calls_per_tranche must be 2 for this ledger contract")
    return {
        "snapshot_id": snapshot,
        "total_records": total,
        "page_size": page_size,
        "calls_per_tranche": allowance,
        "tranche": tranche,
        "remaining_calls": remaining,
    }


def validate_item(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != ITEM_FIELDS:
        raise RollupError("ledger item fields do not match the contract")
    for field in ("entry_id", "vendor_id"):
        if not isinstance(value[field], str) or not value[field]:
            raise RollupError(f"invalid {field} in ledger item")
    parse_date(value["posted_on"], "posted_on")
    if value["kind"] not in {"charge", "credit"}:
        raise RollupError("invalid kind in ledger item")
    if value["status"] not in {"settled", "pending", "void"}:
        raise RollupError("invalid status in ledger item")
    require_int(value["amount_cents"], "amount_cents")
    if value["currency"] != "USD":
        raise RollupError("ledger item currency must be USD")
    return value


def validate_page(
    value: dict[str, Any], snapshot: str, total_records: int, page_size: int
) -> dict[str, Any]:
    required = {"snapshot_id", "items", "next_cursor", "total_records", "tranche"}
    if set(value) != required:
        raise RollupError("page response fields do not match the contract")
    if value["snapshot_id"] != snapshot:
        raise RollupError("page response snapshot does not match the checkpoint")
    response_total = require_int(value["total_records"], "total_records")
    if response_total != total_records:
        raise RollupError("page response total_records changed")
    require_int(value["tranche"], "tranche", minimum=1)
    cursor = value["next_cursor"]
    if cursor is not None and (not isinstance(cursor, str) or not cursor):
        raise RollupError("invalid next_cursor in page response")
    items = value["items"]
    if not isinstance(items, list) or len(items) > page_size:
        raise RollupError("invalid items array in page response")
    validated = [validate_item(item) for item in items]
    ids = [item["entry_id"] for item in validated]
    if len(ids) != len(set(ids)):
        raise RollupError("duplicate entry_id within one page")
    return {**value, "items": validated}


def atomic_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def new_checkpoint(
    api: Path, source_state: Path, start: str, end: str, description: dict[str, Any]
) -> dict[str, Any]:
    return {
        "version": CHECKPOINT_VERSION,
        "request": {
            "api": str(api),
            "source_state": str(source_state),
            "start": start,
            "end": end,
            "snapshot_id": description["snapshot_id"],
            "total_records": description["total_records"],
            "page_size": description["page_size"],
        },
        "complete": False,
        "next_cursor": None,
        "pages_incorporated": 0,
        "seen_entry_ids": [],
        "aggregates": {},
    }


def load_checkpoint(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RollupError(f"cannot read checkpoint: {exc}") from exc
    if not isinstance(value, dict):
        raise RollupError("checkpoint must contain one JSON object")
    required = {
        "version", "request", "complete", "next_cursor", "pages_incorporated",
        "seen_entry_ids", "aggregates",
    }
    if set(value) != required or value["version"] != CHECKPOINT_VERSION:
        raise RollupError("checkpoint schema or version is invalid")
    request = value["request"]
    request_fields = {
        "api", "source_state", "start", "end", "snapshot_id", "total_records", "page_size",
    }
    if not isinstance(request, dict) or set(request) != request_fields:
        raise RollupError("checkpoint request identity is invalid")
    if type(value["complete"]) is not bool:
        raise RollupError("checkpoint complete flag is invalid")
    if value["next_cursor"] is not None and not isinstance(value["next_cursor"], str):
        raise RollupError("checkpoint cursor is invalid")
    require_int(value["pages_incorporated"], "checkpoint pages_incorporated")
    require_int(request["total_records"], "checkpoint total_records")
    require_int(request["page_size"], "checkpoint page_size", minimum=1)
    seen = value["seen_entry_ids"]
    if not isinstance(seen, list) or any(not isinstance(item, str) or not item for item in seen):
        raise RollupError("checkpoint seen_entry_ids is invalid")
    if len(seen) != len(set(seen)):
        raise RollupError("checkpoint contains duplicate seen entry IDs")
    if not isinstance(value["aggregates"], dict):
        raise RollupError("checkpoint aggregates is invalid")
    for vendor, aggregate in value["aggregates"].items():
        if not isinstance(vendor, str) or not vendor or not isinstance(aggregate, dict):
            raise RollupError("checkpoint aggregate is invalid")
        if set(aggregate) != {"charges", "credits", "count"}:
            raise RollupError("checkpoint aggregate fields are invalid")
        for field in ("charges", "credits", "count"):
            require_int(aggregate[field], f"checkpoint aggregate {field}")
    return value


def assert_identity(
    checkpoint: dict[str, Any], api: Path, source_state: Path,
    start: str, end: str, description: dict[str, Any],
) -> None:
    expected = {
        "api": str(api),
        "source_state": str(source_state),
        "start": start,
        "end": end,
        "snapshot_id": description["snapshot_id"],
        "total_records": description["total_records"],
        "page_size": description["page_size"],
    }
    if checkpoint["request"] != expected:
        raise RollupError("checkpoint does not match this request or source description")


def incorporate(checkpoint: dict[str, Any], page: dict[str, Any]) -> None:
    start = checkpoint["request"]["start"]
    end = checkpoint["request"]["end"]
    seen = set(checkpoint["seen_entry_ids"])
    for item in page["items"]:
        entry_id = item["entry_id"]
        if entry_id in seen:
            continue
        checkpoint["seen_entry_ids"].append(entry_id)
        seen.add(entry_id)
        if item["status"] != "settled" or not (start <= item["posted_on"] <= end):
            continue
        aggregate = checkpoint["aggregates"].setdefault(
            item["vendor_id"], {"charges": 0, "credits": 0, "count": 0}
        )
        aggregate["count"] += 1
        if item["kind"] == "charge":
            aggregate["charges"] += item["amount_cents"]
        else:
            aggregate["credits"] += item["amount_cents"]
    checkpoint["pages_incorporated"] += 1
    checkpoint["next_cursor"] = page["next_cursor"]
    checkpoint["complete"] = page["next_cursor"] is None


def complete_output(checkpoint: dict[str, Any], checkpoint_path: Path) -> dict[str, Any]:
    request = checkpoint["request"]
    if len(checkpoint["seen_entry_ids"]) != request["total_records"]:
        raise RollupError(
            "source exhausted but unique incorporated entry count does not match total_records"
        )
    vendors = []
    qualifying_total = 0
    for vendor in sorted(checkpoint["aggregates"]):
        aggregate = checkpoint["aggregates"][vendor]
        qualifying_total += aggregate["count"]
        vendors.append({
            "vendor_id": vendor,
            "settled_charge_cents": aggregate["charges"],
            "settled_credit_cents": aggregate["credits"],
            "net_cents": aggregate["charges"] - aggregate["credits"],
            "qualifying_entry_count": aggregate["count"],
        })
    return {
        "status": "complete",
        "snapshot_id": request["snapshot_id"],
        "interval": {"start": request["start"], "end": request["end"], "inclusive": True},
        "total_source_entries": request["total_records"],
        "source_entries_examined": len(checkpoint["seen_entry_ids"]),
        "qualifying_entry_count": qualifying_total,
        "vendors": vendors,
        "checkpoint": str(checkpoint_path),
    }


def incomplete_output(
    checkpoint: dict[str, Any], checkpoint_path: Path, reason: str, tranche: int
) -> dict[str, Any]:
    request = checkpoint["request"]
    return {
        "status": "incomplete",
        "reason": reason,
        "snapshot_id": request["snapshot_id"],
        "interval": {"start": request["start"], "end": request["end"], "inclusive": True},
        "progress": {
            "source_entries_examined": len(checkpoint["seen_entry_ids"]),
            "total_source_entries": request["total_records"],
            "pages_incorporated": checkpoint["pages_incorporated"],
            "tranche": tranche,
        },
        "checkpoint": str(checkpoint_path),
        "continuation": "rerun the same command after the operator grants another tranche if needed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create or continue an exact vendor reimbursement rollup."
    )
    parser.add_argument("--api", required=True, help="absolute or resolvable ledger_api.py path")
    parser.add_argument("--source-state", required=True, help="existing source SQLite state path")
    parser.add_argument("--checkpoint", required=True, help="request-specific JSON checkpoint path")
    parser.add_argument("--start", required=True, help="inclusive start date, YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="inclusive end date, YYYY-MM-DD")
    args = parser.parse_args()

    try:
        start = parse_date(args.start, "start")
        end = parse_date(args.end, "end")
        if start > end:
            raise RollupError("start must be on or before end")

        api = Path(args.api).resolve()
        source_state = Path(args.source_state).resolve()
        checkpoint_path = Path(args.checkpoint).resolve()
        if not api.is_file():
            raise RollupError(f"API program does not exist: {api}")
        if not source_state.is_file():
            raise RollupError(f"source state does not exist: {source_state}")

        code, stdout, stderr = run_api(api, source_state, ["describe"])
        if code != 0:
            detail = stderr.strip() or stdout.strip() or f"exit {code}"
            raise RollupError(f"describe failed: {detail}")
        description = validate_description(read_json_object(stdout, "describe"))

        if checkpoint_path.exists():
            checkpoint = load_checkpoint(checkpoint_path)
            assert_identity(checkpoint, api, source_state, args.start, args.end, description)
        else:
            checkpoint = new_checkpoint(
                api, source_state, args.start, args.end, description
            )
            atomic_write(checkpoint_path, checkpoint)

        if checkpoint["complete"]:
            emit(complete_output(checkpoint, checkpoint_path))
            return 0

        calls_available = description["remaining_calls"]
        if calls_available == 0:
            emit(incomplete_output(
                checkpoint, checkpoint_path, "current_tranche_has_no_remaining_calls",
                description["tranche"],
            ))
            return 3

        for _ in range(calls_available):
            page_arguments = ["page", "--snapshot", description["snapshot_id"]]
            if checkpoint["next_cursor"] is not None:
                page_arguments.extend(["--cursor", checkpoint["next_cursor"]])
            code, stdout, stderr = run_api(api, source_state, page_arguments)
            if code == 75:
                emit(incomplete_output(
                    checkpoint, checkpoint_path, "call_budget_exhausted",
                    description["tranche"],
                ))
                return 3
            if code != 0:
                detail = stderr.strip() or stdout.strip() or f"exit {code}"
                raise RollupError(f"page call failed: {detail}")
            try:
                page = validate_page(
                    read_json_object(stdout, "page"),
                    description["snapshot_id"],
                    description["total_records"],
                    description["page_size"],
                )
            except RollupError as exc:
                emit(incomplete_output(
                    checkpoint, checkpoint_path,
                    f"page_response_not_incorporated: {exc}", description["tranche"],
                ))
                return 3
            incorporate(checkpoint, page)
            atomic_write(checkpoint_path, checkpoint)
            if checkpoint["complete"]:
                emit(complete_output(checkpoint, checkpoint_path))
                return 0

        emit(incomplete_output(
            checkpoint, checkpoint_path, "current_tranche_allowance_consumed",
            description["tranche"],
        ))
        return 3
    except RollupError as exc:
        emit({"status": "error", "error": str(exc)})
        return 2
    except OSError as exc:
        emit({"status": "error", "error": f"local operation failed: {exc}"})
        return 2


if __name__ == "__main__":
    sys.exit(main())
