#!/usr/bin/env python3
"""Traverse a paginated ledger safely and emit a complete reimbursement rollup."""

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
MAX_SUCCESSFUL_PAGE_CALLS = 2
ITEM_FIELDS = {
    "entry_id",
    "vendor_id",
    "posted_on",
    "kind",
    "status",
    "amount_cents",
    "currency",
}


class RollupError(Exception):
    """A controlled failure with a stable public error label."""

    def __init__(self, error: str, detail: str):
        super().__init__(detail)
        self.error = error
        self.detail = detail


def emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, sort_keys=True, separators=(",", ":")))


def parse_iso_date(value: str, label: str) -> dt.date:
    try:
        parsed = dt.date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise RollupError("invalid_interval", f"{label} must be a valid YYYY-MM-DD date") from exc
    if parsed.isoformat() != value:
        raise RollupError("invalid_interval", f"{label} must use canonical YYYY-MM-DD form")
    return parsed


def read_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RollupError("checkpoint_error", f"cannot read checkpoint: {exc}") from exc
    if not isinstance(value, dict):
        raise RollupError("checkpoint_error", "checkpoint must contain one JSON object")
    return value


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(value, handle, sort_keys=True, separators=(",", ":"))
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_name, path)
        except BaseException:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise
    except OSError as exc:
        raise RollupError("checkpoint_error", f"cannot write checkpoint: {exc}") from exc


def invoke_api(api: Path, source_state: Path, *arguments: str) -> tuple[int, dict[str, Any] | None, str]:
    command = [sys.executable, str(api), "--state", str(source_state), *arguments]
    try:
        result = subprocess.run(command, text=True, capture_output=True, check=False)
    except OSError as exc:
        raise RollupError("source_invocation_failed", str(exc)) from exc
    raw = result.stdout.strip()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = None
    if payload is not None and not isinstance(payload, dict):
        payload = None
    diagnostic = result.stderr.strip()
    return result.returncode, payload, diagnostic


def require_int(value: Any, label: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise RollupError("source_contract_error", f"{label} must be an integer >= {minimum}")
    return value


def describe(api: Path, source_state: Path) -> dict[str, Any]:
    code, payload, diagnostic = invoke_api(api, source_state, "describe")
    if code != 0 or payload is None:
        detail = f"describe exited {code}"
        if payload and isinstance(payload.get("error"), str):
            detail += f": {payload['error']}"
        elif diagnostic:
            detail += f": {diagnostic}"
        raise RollupError("source_describe_failed", detail)

    required = {
        "snapshot_id",
        "total_records",
        "page_size",
        "calls_per_tranche",
        "tranche",
        "remaining_calls",
    }
    if set(payload) != required or not isinstance(payload["snapshot_id"], str) or not payload["snapshot_id"]:
        raise RollupError("source_contract_error", "describe response fields are invalid")
    for key in required - {"snapshot_id"}:
        require_int(payload[key], f"describe.{key}")
    if payload["page_size"] == 0 or payload["calls_per_tranche"] == 0:
        raise RollupError("source_contract_error", "page_size and calls_per_tranche must be positive")
    if payload["remaining_calls"] > payload["calls_per_tranche"]:
        raise RollupError("source_contract_error", "remaining_calls exceeds calls_per_tranche")
    return payload


def request_identity(
    api: Path, source_state: Path, checkpoint: Path, start: str, end: str
) -> dict[str, str]:
    return {
        "api": str(api),
        "source_state": str(source_state),
        "checkpoint": str(checkpoint),
        "start": start,
        "end": end,
    }


def new_checkpoint(identity: dict[str, str], metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": CHECKPOINT_VERSION,
        "request": identity,
        "snapshot_id": metadata["snapshot_id"],
        "total_records": metadata["total_records"],
        "page_size": metadata["page_size"],
        "calls_per_tranche": metadata["calls_per_tranche"],
        "status": "in_progress",
        "next_cursor": None,
        "inflight_cursor": None,
        "pages_processed": 0,
        "records_examined": 0,
        "seen_entry_ids": [],
        "vendors": {},
    }


def validate_checkpoint(
    state: dict[str, Any], identity: dict[str, str], metadata: dict[str, Any]
) -> None:
    if state.get("version") != CHECKPOINT_VERSION:
        raise RollupError("checkpoint_error", "unsupported checkpoint version")
    if state.get("request") != identity:
        raise RollupError("checkpoint_request_mismatch", "checkpoint belongs to different inputs")
    expected = {
        "snapshot_id": metadata["snapshot_id"],
        "total_records": metadata["total_records"],
        "page_size": metadata["page_size"],
        "calls_per_tranche": metadata["calls_per_tranche"],
    }
    for key, value in expected.items():
        if state.get(key) != value:
            raise RollupError("snapshot_changed", f"checkpoint {key} does not match source metadata")
    if state.get("status") not in {"in_progress", "complete"}:
        raise RollupError("checkpoint_error", "invalid checkpoint status")
    for key in ("next_cursor", "inflight_cursor"):
        if state.get(key) is not None and (not isinstance(state[key], str) or not state[key]):
            raise RollupError("checkpoint_error", f"invalid {key}")
    if type(state.get("pages_processed")) is not int or state["pages_processed"] < 0:
        raise RollupError("checkpoint_error", "invalid pages_processed")
    if type(state.get("records_examined")) is not int or state["records_examined"] < 0:
        raise RollupError("checkpoint_error", "invalid records_examined")
    seen = state.get("seen_entry_ids")
    if not isinstance(seen, list) or any(not isinstance(item, str) or not item for item in seen):
        raise RollupError("checkpoint_error", "invalid seen_entry_ids")
    if len(seen) != len(set(seen)) or len(seen) != state["records_examined"]:
        raise RollupError("checkpoint_error", "entry coverage in checkpoint is inconsistent")
    if state["records_examined"] > state["total_records"]:
        raise RollupError("checkpoint_error", "examined count exceeds source record count")
    if state["status"] == "complete" and (
        state["next_cursor"] is not None
        or state["inflight_cursor"] is not None
        or state["records_examined"] != state["total_records"]
    ):
        raise RollupError("checkpoint_error", "complete checkpoint has inconsistent coverage")
    if not isinstance(state.get("vendors"), dict):
        raise RollupError("checkpoint_error", "invalid vendor aggregation")
    for vendor_id, totals in state["vendors"].items():
        if not isinstance(vendor_id, str) or not vendor_id or not isinstance(totals, dict):
            raise RollupError("checkpoint_error", "invalid vendor aggregation")
        if set(totals) != {"settled_charge_cents", "settled_credit_cents", "qualifying_entry_count"}:
            raise RollupError("checkpoint_error", "invalid vendor total fields")
        for key, value in totals.items():
            require_int(value, f"checkpoint vendor {vendor_id}.{key}")


def validate_item(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict) or set(item) != ITEM_FIELDS:
        raise RollupError("source_contract_error", "ledger item fields are invalid")
    if not isinstance(item["entry_id"], str) or not item["entry_id"]:
        raise RollupError("source_contract_error", "entry_id must be a nonempty string")
    if not isinstance(item["vendor_id"], str) or not item["vendor_id"]:
        raise RollupError("source_contract_error", "vendor_id must be a nonempty string")
    try:
        posted = dt.date.fromisoformat(item["posted_on"])
    except (TypeError, ValueError) as exc:
        raise RollupError("source_contract_error", "posted_on is not a valid ISO date") from exc
    if posted.isoformat() != item["posted_on"]:
        raise RollupError("source_contract_error", "posted_on is not canonical YYYY-MM-DD")
    if item["kind"] not in {"charge", "credit"}:
        raise RollupError("source_contract_error", "kind is invalid")
    if item["status"] not in {"settled", "pending", "void"}:
        raise RollupError("source_contract_error", "status is invalid")
    require_int(item["amount_cents"], "amount_cents")
    if item["currency"] != "USD":
        raise RollupError("source_contract_error", "currency must be USD")
    return item


def validate_page(
    payload: dict[str, Any] | None, metadata: dict[str, Any], expected_tranche: int
) -> list[dict[str, Any]]:
    required = {"snapshot_id", "items", "next_cursor", "total_records", "tranche"}
    if payload is None or set(payload) != required:
        raise RollupError("source_contract_error", "page response is not the required JSON object")
    if payload["snapshot_id"] != metadata["snapshot_id"]:
        raise RollupError("source_contract_error", "page snapshot_id changed")
    if payload["total_records"] != metadata["total_records"]:
        raise RollupError("source_contract_error", "page total_records changed")
    if payload["tranche"] != expected_tranche:
        raise RollupError("source_contract_error", "page came from a different source tranche")
    if payload["next_cursor"] is not None and (
        not isinstance(payload["next_cursor"], str) or not payload["next_cursor"]
    ):
        raise RollupError("source_contract_error", "next_cursor must be a nonempty string or null")
    if not isinstance(payload["items"], list) or len(payload["items"]) > metadata["page_size"]:
        raise RollupError("source_contract_error", "page items are invalid")
    items = [validate_item(item) for item in payload["items"]]
    page_ids = [item["entry_id"] for item in items]
    if len(page_ids) != len(set(page_ids)):
        raise RollupError("source_contract_error", "page repeats an entry_id")
    if not items and payload["next_cursor"] is not None:
        raise RollupError("source_contract_error", "empty page cannot advance traversal")
    return items


def coverage(state: dict[str, Any], exhausted: bool) -> dict[str, Any]:
    return {
        "pages_processed": state["pages_processed"],
        "records_examined": state["records_examined"],
        "source_exhausted": exhausted,
        "total_records": state["total_records"],
    }


def complete_output(state: dict[str, Any]) -> dict[str, Any]:
    vendors = []
    for vendor_id in sorted(state["vendors"]):
        totals = state["vendors"][vendor_id]
        charges = totals["settled_charge_cents"]
        credits = totals["settled_credit_cents"]
        vendors.append(
            {
                "vendor_id": vendor_id,
                "settled_charge_cents": charges,
                "settled_credit_cents": credits,
                "net_cents": charges - credits,
                "qualifying_entry_count": totals["qualifying_entry_count"],
            }
        )
    return {
        "status": "complete",
        "snapshot_id": state["snapshot_id"],
        "interval": {"start": state["request"]["start"], "end": state["request"]["end"]},
        "coverage": coverage(state, True),
        "vendors": vendors,
    }


def incomplete_output(state: dict[str, Any], metadata: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "status": "incomplete",
        "reason": reason,
        "snapshot_id": state["snapshot_id"],
        "interval": {"start": state["request"]["start"], "end": state["request"]["end"]},
        "coverage": coverage(state, False),
        "source_tranche": metadata["tranche"],
        "remaining_calls": metadata["remaining_calls"],
        "checkpoint": state["request"]["checkpoint"],
        "partial_aggregation_withheld": True,
    }


def process(args: argparse.Namespace) -> int:
    start_date = parse_iso_date(args.start, "start")
    end_date = parse_iso_date(args.end, "end")
    if start_date > end_date:
        raise RollupError("invalid_interval", "start must be on or before end")

    api = Path(args.api).expanduser().resolve()
    source_state = Path(args.source_state).expanduser().resolve()
    checkpoint = Path(args.checkpoint).expanduser().resolve()
    if not api.is_file():
        raise RollupError("invalid_path", "api must name an existing file")
    if not source_state.is_file():
        raise RollupError("invalid_path", "source-state must name an existing file")
    identity = request_identity(api, source_state, checkpoint, args.start, args.end)

    if checkpoint.exists():
        state = read_json_object(checkpoint)
        if state.get("request") != identity:
            raise RollupError("checkpoint_request_mismatch", "checkpoint belongs to different inputs")
    else:
        state = None

    metadata = describe(api, source_state)
    if state is None:
        state = new_checkpoint(identity, metadata)
        atomic_write_json(checkpoint, state)
    validate_checkpoint(state, identity, metadata)

    if state["status"] == "complete":
        emit(complete_output(state))
        return 0

    starting_tranche = metadata["tranche"]
    successful_calls = 0
    call_limit = min(MAX_SUCCESSFUL_PAGE_CALLS, metadata["calls_per_tranche"])
    while successful_calls < call_limit:
        current_metadata = describe(api, source_state)
        for key in ("snapshot_id", "total_records", "page_size", "calls_per_tranche"):
            if current_metadata[key] != metadata[key]:
                raise RollupError("snapshot_changed", f"source {key} changed during execution")
        if current_metadata["tranche"] != starting_tranche:
            emit(incomplete_output(state, current_metadata, "source_tranche_changed"))
            return 75
        if current_metadata["remaining_calls"] == 0:
            emit(incomplete_output(state, current_metadata, "tranche_boundary"))
            return 75

        cursor = state["inflight_cursor"] if state["inflight_cursor"] is not None else state["next_cursor"]
        state["inflight_cursor"] = cursor
        atomic_write_json(checkpoint, state)
        page_arguments = ["page", "--snapshot", state["snapshot_id"]]
        if cursor is not None:
            page_arguments.extend(["--cursor", cursor])
        code, payload, diagnostic = invoke_api(api, source_state, *page_arguments)
        if code != 0:
            after_error = describe(api, source_state)
            if code == 75 and payload and payload.get("error") == "call_budget_exhausted":
                emit(incomplete_output(state, after_error, "call_budget_exhausted"))
                return 75
            error_name = payload.get("error") if payload and isinstance(payload.get("error"), str) else "unknown"
            detail = f"page call exited {code}: {error_name}"
            if diagnostic:
                detail += f" ({diagnostic})"
            raise RollupError("source_page_failed", detail)

        items = validate_page(payload, metadata, starting_tranche)
        seen = set(state["seen_entry_ids"])
        overlaps = seen.intersection(item["entry_id"] for item in items)
        if overlaps:
            raise RollupError("source_contract_error", "a new page repeated a previously incorporated entry_id")

        for item in items:
            state["seen_entry_ids"].append(item["entry_id"])
            state["records_examined"] += 1
            if item["status"] != "settled" or not (args.start <= item["posted_on"] <= args.end):
                continue
            totals = state["vendors"].setdefault(
                item["vendor_id"],
                {
                    "settled_charge_cents": 0,
                    "settled_credit_cents": 0,
                    "qualifying_entry_count": 0,
                },
            )
            totals[f"settled_{item['kind']}_cents"] += item["amount_cents"]
            totals["qualifying_entry_count"] += 1

        state["pages_processed"] += 1
        state["next_cursor"] = payload["next_cursor"]
        state["inflight_cursor"] = None
        successful_calls += 1

        if payload["next_cursor"] is None:
            if state["records_examined"] != state["total_records"]:
                raise RollupError(
                    "coverage_mismatch",
                    "source reported exhaustion before examined entry count matched total_records",
                )
            state["status"] = "complete"
            atomic_write_json(checkpoint, state)
            emit(complete_output(state))
            return 0
        atomic_write_json(checkpoint, state)

    latest = describe(api, source_state)
    emit(incomplete_output(state, latest, "tranche_boundary"))
    return 75


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compute an exact vendor reimbursement rollup only after complete traversal; "
            "exit 75 and preserve a checkpoint at a tranche boundary."
        )
    )
    parser.add_argument("--api", required=True, help="source API Python file")
    parser.add_argument("--source-state", required=True, help="immutable source state database")
    parser.add_argument("--checkpoint", required=True, help="durable checkpoint dedicated to this request")
    parser.add_argument("--start", required=True, help="inclusive YYYY-MM-DD start date")
    parser.add_argument("--end", required=True, help="inclusive YYYY-MM-DD end date")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return process(args)
    except RollupError as exc:
        category = "invalid_request" if exc.error in {
            "invalid_interval",
            "invalid_path",
            "checkpoint_request_mismatch",
        } else "error"
        emit({"status": category, "error": exc.error, "detail": exc.detail})
        return 2 if category == "invalid_request" else 1


if __name__ == "__main__":
    sys.exit(main())
