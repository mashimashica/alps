#!/usr/bin/env python3
"""Build or continue an exact reimbursement rollup from a paginated ledger CLI."""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


CHECKPOINT_VERSION = 1
CALLS_PER_TRANCHE = 2
ITEM_FIELDS = {
    "entry_id",
    "vendor_id",
    "posted_on",
    "kind",
    "status",
    "amount_cents",
    "currency",
}
PAGE_FIELDS = {"snapshot_id", "items", "next_cursor", "total_records", "tranche"}
DESCRIBE_FIELDS = {
    "snapshot_id",
    "total_records",
    "page_size",
    "calls_per_tranche",
    "tranche",
    "remaining_calls",
}


class RollupError(Exception):
    def __init__(self, code: int, error: str, **details: Any) -> None:
        super().__init__(error)
        self.code = code
        self.body = {"status": "error", "error": error, **details}


class PageResponseUnusable(Exception):
    def __init__(self, reason: str, **details: Any) -> None:
        super().__init__(reason)
        self.reason = reason
        self.details = details


def emit(body: dict[str, Any]) -> None:
    print(json.dumps(body, sort_keys=True, separators=(",", ":")))


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def canonical_date(value: str, label: str) -> str:
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError as exc:
        raise RollupError(2, "invalid_interval", detail=f"{label} must be a valid YYYY-MM-DD date") from exc
    if parsed.isoformat() != value:
        raise RollupError(2, "invalid_interval", detail=f"{label} must use canonical YYYY-MM-DD form")
    return value


def canonical_source_date(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise RollupError(3, "source_contract_error", detail=f"{label} must be a YYYY-MM-DD string")
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError as exc:
        raise RollupError(3, "source_contract_error", detail=f"{label} must be a valid YYYY-MM-DD date") from exc
    if parsed.isoformat() != value:
        raise RollupError(3, "source_contract_error", detail=f"{label} must use canonical YYYY-MM-DD form")
    return value


def require_nonnegative_int(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise RollupError(3, "source_contract_error", detail=f"{label} must be a nonnegative integer")
    return value


def parse_one_json(stdout: str, label: str) -> dict[str, Any]:
    text = stdout.strip()
    if not text:
        raise ValueError(f"{label} returned no JSON object")
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} returned malformed JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} response must be a JSON object")
    return value


def run_source(
    api: Path,
    source_state: Path,
    arguments: list[str],
    timeout_seconds: float,
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(api), "--state", str(source_state), *arguments]
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )


def describe(api: Path, source_state: Path, timeout_seconds: float) -> dict[str, Any]:
    try:
        result = run_source(api, source_state, ["describe"], timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        raise RollupError(3, "source_describe_failed", detail="describe timed out") from exc
    if result.returncode != 0:
        details: dict[str, Any] = {"source_exit_code": result.returncode}
        try:
            details["source_response"] = parse_one_json(result.stdout, "describe")
        except ValueError:
            details["detail"] = result.stderr.strip() or "describe returned no usable error object"
        raise RollupError(3, "source_describe_failed", **details)
    try:
        body = parse_one_json(result.stdout, "describe")
    except ValueError as exc:
        raise RollupError(3, "source_contract_error", detail=str(exc)) from exc
    if set(body) != DESCRIBE_FIELDS:
        raise RollupError(3, "source_contract_error", detail="describe fields do not match the required contract")
    if not isinstance(body["snapshot_id"], str) or not body["snapshot_id"]:
        raise RollupError(3, "source_contract_error", detail="describe snapshot_id must be a nonempty string")
    for field in ("total_records", "page_size", "calls_per_tranche", "tranche", "remaining_calls"):
        require_nonnegative_int(body[field], f"describe.{field}")
    if body["page_size"] < 1:
        raise RollupError(3, "source_contract_error", detail="describe.page_size must be positive")
    if body["calls_per_tranche"] != CALLS_PER_TRANCHE:
        raise RollupError(
            3,
            "unsupported_call_limit",
            expected_calls_per_tranche=CALLS_PER_TRANCHE,
            observed_calls_per_tranche=body["calls_per_tranche"],
        )
    if body["remaining_calls"] > body["calls_per_tranche"]:
        raise RollupError(3, "source_contract_error", detail="describe.remaining_calls exceeds the tranche limit")
    return body


def request_identity(
    api: Path,
    source_state: Path,
    start_date: str,
    end_date: str,
) -> dict[str, str]:
    return {
        "api": str(api),
        "source_state": str(source_state),
        "start_date": start_date,
        "end_date": end_date,
    }


def new_checkpoint(identity: dict[str, str], metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": CHECKPOINT_VERSION,
        "request": identity,
        "snapshot_id": metadata["snapshot_id"],
        "total_records": metadata["total_records"],
        "phase": "active",
        "cursor": None,
        "pages_processed": 0,
        "processed_cursors": [],
        "entries": {},
        "aggregates": {},
    }


def load_checkpoint(path: Path) -> dict[str, Any]:
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RollupError(4, "checkpoint_unreadable", checkpoint=str(path), detail=str(exc)) from exc
    if not isinstance(body, dict) or body.get("version") != CHECKPOINT_VERSION:
        raise RollupError(4, "checkpoint_unsupported", checkpoint=str(path))
    required = {
        "version",
        "request",
        "snapshot_id",
        "total_records",
        "phase",
        "cursor",
        "pages_processed",
        "processed_cursors",
        "entries",
        "aggregates",
    }
    if set(body) != required:
        raise RollupError(4, "checkpoint_invalid", checkpoint=str(path), detail="checkpoint fields are inconsistent")
    if body["phase"] not in ("active", "complete", "invalid"):
        raise RollupError(4, "checkpoint_invalid", checkpoint=str(path), detail="unknown checkpoint phase")
    if not isinstance(body["entries"], dict) or not isinstance(body["aggregates"], dict):
        raise RollupError(4, "checkpoint_invalid", checkpoint=str(path), detail="checkpoint maps are invalid")
    if type(body["total_records"]) is not int or body["total_records"] < 0:
        raise RollupError(4, "checkpoint_invalid", checkpoint=str(path), detail="invalid total_records")
    if type(body["pages_processed"]) is not int or body["pages_processed"] < 0:
        raise RollupError(4, "checkpoint_invalid", checkpoint=str(path), detail="invalid pages_processed")
    if not isinstance(body["processed_cursors"], list):
        raise RollupError(4, "checkpoint_invalid", checkpoint=str(path), detail="invalid processed_cursors")
    if len(body["processed_cursors"]) != body["pages_processed"]:
        raise RollupError(4, "checkpoint_invalid", checkpoint=str(path), detail="page and cursor counts disagree")
    if any(cursor is not None and (not isinstance(cursor, str) or not cursor) for cursor in body["processed_cursors"]):
        raise RollupError(4, "checkpoint_invalid", checkpoint=str(path), detail="invalid processed cursor")
    if len({canonical(cursor) for cursor in body["processed_cursors"]}) != len(body["processed_cursors"]):
        raise RollupError(4, "checkpoint_invalid", checkpoint=str(path), detail="processed cursors are not unique")
    if body["cursor"] is not None and (not isinstance(body["cursor"], str) or not body["cursor"]):
        raise RollupError(4, "checkpoint_invalid", checkpoint=str(path), detail="invalid cursor")
    if body["cursor"] is not None and body["cursor"] in body["processed_cursors"]:
        raise RollupError(4, "checkpoint_invalid", checkpoint=str(path), detail="current cursor was already processed")
    if not isinstance(body["request"], dict) or set(body["request"]) != {
        "api", "source_state", "start_date", "end_date"
    }:
        raise RollupError(4, "checkpoint_invalid", checkpoint=str(path), detail="invalid request identity")
    if not isinstance(body["snapshot_id"], str) or not body["snapshot_id"]:
        raise RollupError(4, "checkpoint_invalid", checkpoint=str(path), detail="invalid snapshot_id")
    if any(not isinstance(key, str) or not key or not isinstance(value, str) for key, value in body["entries"].items()):
        raise RollupError(4, "checkpoint_invalid", checkpoint=str(path), detail="invalid entry digest map")
    for vendor_id, values in body["aggregates"].items():
        if not isinstance(vendor_id, str) or not vendor_id or not isinstance(values, dict):
            raise RollupError(4, "checkpoint_invalid", checkpoint=str(path), detail="invalid aggregate vendor")
        if set(values) != {"settled_charge_cents", "settled_credit_cents", "qualifying_entry_count"}:
            raise RollupError(4, "checkpoint_invalid", checkpoint=str(path), detail="invalid aggregate fields")
        if any(type(value) is not int or value < 0 for value in values.values()):
            raise RollupError(4, "checkpoint_invalid", checkpoint=str(path), detail="invalid aggregate values")
    if body["phase"] == "complete" and (body["cursor"] is not None or len(body["entries"]) != body["total_records"]):
        raise RollupError(4, "checkpoint_invalid", checkpoint=str(path), detail="complete checkpoint is inconsistent")
    return body


def save_checkpoint(path: Path, body: dict[str, Any]) -> None:
    payload = canonical(body) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        if temporary.exists():
            temporary.unlink()


def validate_item(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict) or set(item) != ITEM_FIELDS:
        raise RollupError(3, "source_contract_error", detail="item fields do not match the required contract")
    for field in ("entry_id", "vendor_id"):
        if not isinstance(item[field], str) or not item[field]:
            raise RollupError(3, "source_contract_error", detail=f"item.{field} must be a nonempty string")
    canonical_source_date(item["posted_on"], "item.posted_on")
    if item["kind"] not in ("charge", "credit"):
        raise RollupError(3, "source_contract_error", detail="item.kind must be charge or credit")
    if item["status"] not in ("settled", "pending", "void"):
        raise RollupError(3, "source_contract_error", detail="item.status is invalid")
    require_nonnegative_int(item["amount_cents"], "item.amount_cents")
    if item["currency"] != "USD":
        raise RollupError(3, "source_contract_error", detail="item.currency must be USD")
    return item


def validate_page(
    body: dict[str, Any],
    checkpoint: dict[str, Any],
    metadata: dict[str, Any],
) -> list[dict[str, Any]]:
    if set(body) != PAGE_FIELDS:
        raise RollupError(3, "source_contract_error", detail="page fields do not match the required contract")
    require_nonnegative_int(body["total_records"], "page.total_records")
    if body["snapshot_id"] != checkpoint["snapshot_id"]:
        raise RollupError(3, "source_contract_error", detail="page snapshot_id changed")
    if body["total_records"] != checkpoint["total_records"]:
        raise RollupError(3, "source_contract_error", detail="page total_records changed")
    require_nonnegative_int(body["tranche"], "page.tranche")
    if not isinstance(body["items"], list):
        raise RollupError(3, "source_contract_error", detail="page.items must be a list")
    if len(body["items"]) > metadata["page_size"]:
        raise RollupError(3, "source_contract_error", detail="page exceeds described page size")
    cursor = body["next_cursor"]
    if cursor is not None and (not isinstance(cursor, str) or not cursor):
        raise RollupError(3, "source_contract_error", detail="next_cursor must be null or a nonempty string")
    if cursor is not None and cursor == checkpoint["cursor"]:
        raise RollupError(3, "source_contract_error", detail="source returned the current cursor again")
    if cursor is not None and cursor in checkpoint["processed_cursors"]:
        raise RollupError(3, "source_contract_error", detail="source returned a previously processed cursor")
    if not body["items"] and cursor is not None:
        raise RollupError(3, "source_contract_error", detail="empty page cannot have a continuation cursor")
    return [validate_item(item) for item in body["items"]]


def incorporate_page(
    checkpoint: dict[str, Any],
    body: dict[str, Any],
    items: list[dict[str, Any]],
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    updated = copy.deepcopy(checkpoint)
    cursor_key = checkpoint["cursor"]
    if cursor_key in updated["processed_cursors"]:
        raise RollupError(3, "source_contract_error", detail="checkpoint would process a cursor twice")
    updated["processed_cursors"].append(cursor_key)
    for item in items:
        entry_id = item["entry_id"]
        digest = hashlib.sha256(canonical(item).encode("utf-8")).hexdigest()
        if entry_id in updated["entries"]:
            conflict = updated["entries"][entry_id] != digest
            raise RollupError(
                3,
                "source_contract_error",
                detail="conflicting duplicate entry_id" if conflict else "duplicate entry_id across pages",
                entry_id=entry_id,
            )
        updated["entries"][entry_id] = digest
        if item["status"] != "settled" or not (start_date <= item["posted_on"] <= end_date):
            continue
        vendor = updated["aggregates"].setdefault(
            item["vendor_id"],
            {"settled_charge_cents": 0, "settled_credit_cents": 0, "qualifying_entry_count": 0},
        )
        if item["kind"] == "charge":
            vendor["settled_charge_cents"] += item["amount_cents"]
        else:
            vendor["settled_credit_cents"] += item["amount_cents"]
        vendor["qualifying_entry_count"] += 1
    updated["pages_processed"] += 1
    updated["cursor"] = body["next_cursor"]
    examined = len(updated["entries"])
    total = updated["total_records"]
    if body["next_cursor"] is None:
        updated["phase"] = "complete" if examined == total else "invalid"
    elif examined >= total:
        updated["phase"] = "invalid"
    return updated


def complete_result(checkpoint: dict[str, Any], checkpoint_path: Path) -> dict[str, Any]:
    vendors = []
    for vendor_id in sorted(checkpoint["aggregates"]):
        values = checkpoint["aggregates"][vendor_id]
        charges = values["settled_charge_cents"]
        credits = values["settled_credit_cents"]
        vendors.append(
            {
                "vendor_id": vendor_id,
                "settled_charge_cents": charges,
                "settled_credit_cents": credits,
                "net_cents": charges - credits,
                "qualifying_entry_count": values["qualifying_entry_count"],
            }
        )
    return {
        "status": "complete",
        "snapshot_id": checkpoint["snapshot_id"],
        "interval": {
            "start": checkpoint["request"]["start_date"],
            "end": checkpoint["request"]["end_date"],
            "inclusive": True,
        },
        "currency": "USD",
        "source_records_examined": len(checkpoint["entries"]),
        "source_records_total": checkpoint["total_records"],
        "vendors": vendors,
        "checkpoint": str(checkpoint_path),
    }


def incomplete_result(
    checkpoint: dict[str, Any],
    checkpoint_path: Path,
    metadata: dict[str, Any],
    reason: str,
    **details: Any,
) -> dict[str, Any]:
    return {
        "status": "incomplete",
        "final_result": False,
        "reason": reason,
        "snapshot_id": checkpoint["snapshot_id"],
        "interval": {
            "start": checkpoint["request"]["start_date"],
            "end": checkpoint["request"]["end_date"],
            "inclusive": True,
        },
        "source_records_examined": len(checkpoint["entries"]),
        "source_records_total": checkpoint["total_records"],
        "tranche": metadata["tranche"],
        "remaining_calls_observed": metadata["remaining_calls"],
        "checkpoint": str(checkpoint_path),
        **details,
    }


def fetch_page(
    api: Path,
    source_state: Path,
    checkpoint: dict[str, Any],
    timeout_seconds: float,
) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    arguments = ["page", "--snapshot", checkpoint["snapshot_id"]]
    if checkpoint["cursor"] is not None:
        arguments.extend(["--cursor", checkpoint["cursor"]])
    try:
        result = run_source(api, source_state, arguments, timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        raise PageResponseUnusable("page command timed out", timeout_seconds=timeout_seconds) from exc
    if result.returncode == 0:
        try:
            return result, parse_one_json(result.stdout, "page")
        except ValueError as exc:
            raise PageResponseUnusable(str(exc)) from exc
    try:
        body = parse_one_json(result.stdout, "page")
    except ValueError:
        body = {"detail": result.stderr.strip() or "source returned no usable error object"}
    return result, body


def execute(args: argparse.Namespace) -> int:
    start_date = canonical_date(args.start_date, "start-date")
    end_date = canonical_date(args.end_date, "end-date")
    if start_date > end_date:
        raise RollupError(2, "invalid_interval", detail="start-date must not be after end-date")
    if args.command_timeout_seconds <= 0:
        raise RollupError(2, "invalid_timeout", detail="command-timeout-seconds must be positive")

    api = Path(args.api).expanduser().resolve()
    source_state = Path(args.source_state).expanduser().resolve()
    checkpoint_path = Path(args.checkpoint).expanduser().resolve()
    for path, label in ((api, "api"), (source_state, "source-state")):
        if not path.is_file():
            raise RollupError(2, "path_not_found", path_label=label, path=str(path))
    if not checkpoint_path.parent.is_dir():
        raise RollupError(2, "checkpoint_parent_not_found", path=str(checkpoint_path.parent))
    identity = request_identity(api, source_state, start_date, end_date)

    lock_path = checkpoint_path.with_name(checkpoint_path.name + ".lock")
    try:
        lock_stream = lock_path.open("a+", encoding="utf-8")
    except OSError as exc:
        raise RollupError(2, "checkpoint_lock_failed", path=str(lock_path), detail=str(exc)) from exc
    with lock_stream:
        fcntl.flock(lock_stream.fileno(), fcntl.LOCK_EX)
        checkpoint = load_checkpoint(checkpoint_path) if checkpoint_path.exists() else None
        if checkpoint is not None and checkpoint["request"] != identity:
            raise RollupError(
                2,
                "checkpoint_request_mismatch",
                checkpoint=str(checkpoint_path),
                expected=checkpoint["request"],
                received=identity,
            )
        metadata = describe(api, source_state, args.command_timeout_seconds)
        if checkpoint is None:
            checkpoint = new_checkpoint(identity, metadata)
            save_checkpoint(checkpoint_path, checkpoint)
        elif (
            checkpoint["snapshot_id"] != metadata["snapshot_id"]
            or checkpoint["total_records"] != metadata["total_records"]
        ):
            raise RollupError(
                3,
                "source_identity_changed",
                checkpoint_snapshot=checkpoint["snapshot_id"],
                observed_snapshot=metadata["snapshot_id"],
                checkpoint_total_records=checkpoint["total_records"],
                observed_total_records=metadata["total_records"],
            )

        if checkpoint["phase"] == "complete":
            emit(complete_result(checkpoint, checkpoint_path))
            return 0
        if checkpoint["phase"] == "invalid":
            raise RollupError(
                4,
                "checkpoint_records_do_not_match_source_total",
                checkpoint=str(checkpoint_path),
                source_records_examined=len(checkpoint["entries"]),
                source_records_total=checkpoint["total_records"],
            )

        available = min(CALLS_PER_TRANCHE, metadata["remaining_calls"])
        if available == 0:
            emit(
                incomplete_result(
                    checkpoint,
                    checkpoint_path,
                    metadata,
                    "no_calls_remaining_in_current_tranche",
                    next_action="Wait for an operator-granted tranche, then rerun the same command.",
                )
            )
            return 75

        successful_pages = 0
        for _ in range(available):
            try:
                result, page = fetch_page(api, source_state, checkpoint, args.command_timeout_seconds)
            except PageResponseUnusable as exc:
                refresh_details: dict[str, Any] = {}
                try:
                    observed = describe(api, source_state, args.command_timeout_seconds)
                except RollupError as refresh_error:
                    observed = dict(metadata)
                    observed["remaining_calls"] = None
                    refresh_details["quota_refresh_error"] = refresh_error.body
                emit(
                    incomplete_result(
                        checkpoint,
                        checkpoint_path,
                        observed,
                        "page_response_unusable",
                        page_call_effect="source quota may have been consumed; checkpoint cursor was not advanced",
                        next_action="Rerun the same command; it will inspect current quota before retrying the stored cursor.",
                        detail=exc.reason,
                        **exc.details,
                        **refresh_details,
                    )
                )
                return 75
            if result.returncode != 0:
                if result.returncode == 75 and page.get("error") == "call_budget_exhausted":
                    observed = dict(metadata)
                    observed["remaining_calls"] = 0
                    emit(
                        incomplete_result(
                            checkpoint,
                            checkpoint_path,
                            observed,
                            "no_calls_remaining_in_current_tranche",
                            next_action="Wait for an operator-granted tranche, then rerun the same command.",
                            source_response=page,
                        )
                    )
                    return 75
                raise RollupError(
                    3,
                    "source_page_failed",
                    source_exit_code=result.returncode,
                    source_response=page,
                    checkpoint=str(checkpoint_path),
                )

            items = validate_page(page, checkpoint, metadata)
            checkpoint = incorporate_page(checkpoint, page, items, start_date, end_date)
            save_checkpoint(checkpoint_path, checkpoint)
            successful_pages += 1
            if checkpoint["phase"] == "invalid":
                raise RollupError(
                    3,
                    "source_record_count_mismatch",
                    source_records_examined=len(checkpoint["entries"]),
                    source_records_total=checkpoint["total_records"],
                    source_exhausted=page["next_cursor"] is None,
                    checkpoint=str(checkpoint_path),
                )
            if checkpoint["phase"] == "complete":
                emit(complete_result(checkpoint, checkpoint_path))
                return 0

        observed = dict(metadata)
        observed["remaining_calls"] = max(0, metadata["remaining_calls"] - successful_pages)
        emit(
            incomplete_result(
                checkpoint,
                checkpoint_path,
                observed,
                "tranche_call_limit_reached",
                successful_page_calls_this_run=successful_pages,
                next_action="Wait for an operator-granted tranche, then rerun the same command.",
            )
        )
        return 75


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build or continue a complete vendor reimbursement rollup using an atomic checkpoint.",
        epilog=(
            "Outputs one JSON object. Exit 0 means complete; 75 means safely resumable but incomplete; "
            "2 means invalid local input; 3 means source failure or contract violation; 4 means invalid checkpoint."
        ),
    )
    parser.add_argument("--api", required=True, help="path to the local ledger API Python program")
    parser.add_argument("--source-state", required=True, help="path to the immutable ledger source state")
    parser.add_argument("--checkpoint", required=True, help="durable JSON checkpoint path for this request")
    parser.add_argument("--start-date", required=True, help="inclusive canonical date, YYYY-MM-DD")
    parser.add_argument("--end-date", required=True, help="inclusive canonical date, YYYY-MM-DD")
    parser.add_argument(
        "--command-timeout-seconds",
        type=float,
        default=30.0,
        help="timeout for each source CLI call (default: 30)",
    )
    return parser


def main() -> int:
    try:
        return execute(build_parser().parse_args())
    except RollupError as exc:
        emit(exc.body)
        return exc.code
    except (OSError, TypeError, ValueError) as exc:
        emit({"status": "error", "error": "local_processing_error", "detail": str(exc)})
        return 4


if __name__ == "__main__":
    sys.exit(main())
