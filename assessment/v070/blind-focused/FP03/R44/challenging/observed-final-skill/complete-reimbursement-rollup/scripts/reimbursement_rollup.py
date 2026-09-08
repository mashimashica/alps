#!/usr/bin/env python3
"""Complete an exact reimbursement rollup over a call-limited paginated ledger."""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


CHECKPOINT_VERSION = 1
EXPECTED_PAGE_SIZE = 3
EXPECTED_CALLS_PER_TRANCHE = 2
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
    """A safe, actionable failure."""

    def __init__(self, error: str, detail: str, **extra: Any):
        super().__init__(detail)
        self.payload = {"status": "error", "final": False, "error": error, "detail": detail, **extra}


class UncertainPageError(RollupError):
    """A page call may have consumed quota without a usable response."""


def emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, sort_keys=True, indent=2))


def iso_date(value: str, label: str) -> str:
    try:
        parsed = dt.date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise RollupError("invalid_interval", f"{label} must be a valid ISO date (YYYY-MM-DD)") from exc
    if parsed.isoformat() != value:
        raise RollupError("invalid_interval", f"{label} must use canonical YYYY-MM-DD form")
    return value


def invoke(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, text=True, capture_output=True, check=False)
    except OSError as exc:
        raise RollupError("source_command_unavailable", str(exc)) from exc


def parse_object(text: str, context: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{context} did not return one valid JSON value") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{context} JSON must be an object")
    return value


def require_nonnegative_int(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{label} must be a nonnegative integer")
    return value


def describe(python: str, api: Path, source_state: Path) -> dict[str, Any]:
    result = invoke([python, str(api), "--state", str(source_state), "describe"])
    if result.returncode != 0:
        detail = result.stdout.strip() or result.stderr.strip() or f"exit {result.returncode}"
        raise RollupError("describe_failed", detail, source_exit_code=result.returncode)
    try:
        body = parse_object(result.stdout, "describe")
        snapshot_id = body["snapshot_id"]
        if not isinstance(snapshot_id, str) or not snapshot_id:
            raise ValueError("snapshot_id must be a nonempty string")
        total_records = require_nonnegative_int(body["total_records"], "total_records")
        page_size = require_nonnegative_int(body["page_size"], "page_size")
        calls_per_tranche = require_nonnegative_int(body["calls_per_tranche"], "calls_per_tranche")
        tranche = require_nonnegative_int(body["tranche"], "tranche")
        remaining_calls = require_nonnegative_int(body["remaining_calls"], "remaining_calls")
    except (KeyError, ValueError) as exc:
        raise RollupError("source_contract_violation", f"invalid describe response: {exc}") from exc
    if page_size != EXPECTED_PAGE_SIZE or calls_per_tranche != EXPECTED_CALLS_PER_TRANCHE:
        raise RollupError(
            "incompatible_source",
            "source metadata does not match the required page-size and tranche contract",
            observed_page_size=page_size,
            observed_calls_per_tranche=calls_per_tranche,
        )
    if remaining_calls > calls_per_tranche:
        raise RollupError("source_contract_violation", "remaining_calls exceeds calls_per_tranche")
    return {
        "snapshot_id": snapshot_id,
        "total_records": total_records,
        "page_size": page_size,
        "calls_per_tranche": calls_per_tranche,
        "tranche": tranche,
        "remaining_calls": remaining_calls,
    }


def new_checkpoint(
    api: Path, source_state: Path, checkpoint: Path, output: Path | None,
    start: str, end: str, metadata: dict[str, Any]
) -> dict[str, Any]:
    return {
        "version": CHECKPOINT_VERSION,
        "request": {
            "api": str(api),
            "source_state": str(source_state),
            "checkpoint": str(checkpoint),
            "output": str(output) if output is not None else None,
            "start": start,
            "end": end,
        },
        "source": {
            "snapshot_id": metadata["snapshot_id"],
            "total_records": metadata["total_records"],
            "page_size": metadata["page_size"],
        },
        "progress": {
            "started": False,
            "complete": False,
            "next_cursor": None,
            "processed_records": 0,
            "seen_entry_ids": [],
            "last_tranche": None,
        },
        "aggregates": {},
    }


def load_checkpoint(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RollupError("invalid_checkpoint", str(exc)) from exc
    if not isinstance(value, dict):
        raise RollupError("invalid_checkpoint", "checkpoint root must be an object")
    return value


def validate_checkpoint(
    value: dict[str, Any], api: Path, source_state: Path, checkpoint: Path, output: Path | None,
    start: str, end: str,
    metadata: dict[str, Any]
) -> None:
    try:
        if value["version"] != CHECKPOINT_VERSION:
            raise ValueError("unsupported checkpoint version")
        request = value["request"]
        expected_request = {
            "api": str(api),
            "source_state": str(source_state),
            "checkpoint": str(checkpoint),
            "output": str(output) if output is not None else None,
            "start": start,
            "end": end,
        }
        if request != expected_request:
            raise ValueError("checkpoint belongs to different paths or date interval")
        source = value["source"]
        expected_source = {
            "snapshot_id": metadata["snapshot_id"],
            "total_records": metadata["total_records"],
            "page_size": metadata["page_size"],
        }
        if source != expected_source:
            raise ValueError("checkpoint belongs to different source metadata or snapshot")
        progress = value["progress"]
        if set(progress) != {
            "started", "complete", "next_cursor", "processed_records", "seen_entry_ids", "last_tranche"
        }:
            raise ValueError("unexpected progress fields")
        if type(progress["started"]) is not bool or type(progress["complete"]) is not bool:
            raise ValueError("progress flags must be booleans")
        if progress["next_cursor"] is not None and not isinstance(progress["next_cursor"], str):
            raise ValueError("next_cursor must be a string or null")
        processed = require_nonnegative_int(progress["processed_records"], "processed_records")
        seen = progress["seen_entry_ids"]
        if not isinstance(seen, list) or any(not isinstance(item, str) or not item for item in seen):
            raise ValueError("seen_entry_ids must be a list of nonempty strings")
        if len(set(seen)) != len(seen) or len(seen) != processed:
            raise ValueError("seen_entry_ids do not match processed_records")
        if processed > metadata["total_records"]:
            raise ValueError("processed_records exceeds total_records")
        if progress["complete"] and (progress["next_cursor"] is not None or processed != metadata["total_records"]):
            raise ValueError("completed checkpoint does not prove full coverage")
        if progress["started"] and not progress["complete"] and progress["next_cursor"] is None:
            raise ValueError("started incomplete checkpoint lacks a continuation cursor")
        if not progress["started"] and (processed != 0 or progress["complete"]):
            raise ValueError("unstarted checkpoint contains progress")
        if progress["last_tranche"] is not None:
            require_nonnegative_int(progress["last_tranche"], "last_tranche")
        aggregates = value["aggregates"]
        if not isinstance(aggregates, dict):
            raise ValueError("aggregates must be an object")
        for vendor, row in aggregates.items():
            if not isinstance(vendor, str) or not vendor or not isinstance(row, dict):
                raise ValueError("invalid aggregate vendor")
            if set(row) != {"charge", "credit", "count"}:
                raise ValueError("unexpected aggregate fields")
            require_nonnegative_int(row["charge"], "aggregate charge")
            require_nonnegative_int(row["credit"], "aggregate credit")
            require_nonnegative_int(row["count"], "aggregate count")
    except (KeyError, TypeError, ValueError) as exc:
        raise RollupError("invalid_checkpoint", str(exc)) from exc


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def page_command(
    python: str, api: Path, source_state: Path, snapshot_id: str, cursor: str | None
) -> list[str]:
    command = [python, str(api), "--state", str(source_state), "page", "--snapshot", snapshot_id]
    if cursor is not None:
        command.extend(["--cursor", cursor])
    return command


def validate_item(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict) or set(item) != ITEM_FIELDS:
        raise ValueError("item fields do not match the source contract")
    if not isinstance(item["entry_id"], str) or not item["entry_id"]:
        raise ValueError("entry_id must be a nonempty string")
    if not isinstance(item["vendor_id"], str) or not item["vendor_id"]:
        raise ValueError("vendor_id must be a nonempty string")
    posted = item["posted_on"]
    if not isinstance(posted, str) or dt.date.fromisoformat(posted).isoformat() != posted:
        raise ValueError("posted_on must be a valid canonical ISO date")
    if item["kind"] not in {"charge", "credit"}:
        raise ValueError("kind must be charge or credit")
    if item["status"] not in {"settled", "pending", "void"}:
        raise ValueError("status is outside the source contract")
    require_nonnegative_int(item["amount_cents"], "amount_cents")
    if item["currency"] != "USD":
        raise ValueError("currency must be USD")
    return item


def validate_page(body: dict[str, Any], checkpoint: dict[str, Any]) -> tuple[list[dict[str, Any]], str | None, int]:
    expected_fields = {"snapshot_id", "items", "next_cursor", "total_records", "tranche"}
    if set(body) != expected_fields:
        raise ValueError("page fields do not match the source contract")
    if body["snapshot_id"] != checkpoint["source"]["snapshot_id"]:
        raise ValueError("page snapshot_id does not match the checkpoint")
    if body["total_records"] != checkpoint["source"]["total_records"]:
        raise ValueError("page total_records changed")
    items = body["items"]
    if not isinstance(items, list) or len(items) > checkpoint["source"]["page_size"]:
        raise ValueError("items must be a page-sized list")
    validated = [validate_item(item) for item in items]
    next_cursor = body["next_cursor"]
    if next_cursor is not None and (not isinstance(next_cursor, str) or not next_cursor):
        raise ValueError("next_cursor must be a nonempty string or null")
    if not validated and next_cursor is not None:
        raise ValueError("empty page cannot have a continuation cursor")
    tranche = require_nonnegative_int(body["tranche"], "tranche")
    return validated, next_cursor, tranche


def incorporate(checkpoint: dict[str, Any], items: list[dict[str, Any]], next_cursor: str | None, tranche: int) -> dict[str, Any]:
    candidate = copy.deepcopy(checkpoint)
    progress = candidate["progress"]
    seen = set(progress["seen_entry_ids"])
    for item in items:
        entry_id = item["entry_id"]
        if entry_id in seen:
            raise ValueError(f"duplicate entry_id across pages: {entry_id}")
        seen.add(entry_id)
        progress["seen_entry_ids"].append(entry_id)
        progress["processed_records"] += 1
        if item["status"] == "settled" and candidate["request"]["start"] <= item["posted_on"] <= candidate["request"]["end"]:
            row = candidate["aggregates"].setdefault(item["vendor_id"], {"charge": 0, "credit": 0, "count": 0})
            row[item["kind"]] += item["amount_cents"]
            row["count"] += 1
    progress["started"] = True
    progress["next_cursor"] = next_cursor
    progress["last_tranche"] = tranche
    if progress["processed_records"] > candidate["source"]["total_records"]:
        raise ValueError("page sequence exceeds advertised total_records")
    if next_cursor is None:
        if progress["processed_records"] != candidate["source"]["total_records"]:
            raise ValueError("source exhausted before advertised total_records were examined")
        progress["complete"] = True
    return candidate


def common_output(checkpoint: dict[str, Any]) -> dict[str, Any]:
    return {
        "snapshot_id": checkpoint["source"]["snapshot_id"],
        "interval": {
            "start": checkpoint["request"]["start"],
            "end": checkpoint["request"]["end"],
            "inclusive": True,
        },
        "coverage": {
            "processed_records": checkpoint["progress"]["processed_records"],
            "total_records": checkpoint["source"]["total_records"],
            "source_exhausted": checkpoint["progress"]["complete"],
        },
        "checkpoint": checkpoint["request"]["checkpoint"],
    }


def complete_output(checkpoint: dict[str, Any]) -> dict[str, Any]:
    vendors = []
    for vendor_id in sorted(checkpoint["aggregates"]):
        row = checkpoint["aggregates"][vendor_id]
        vendors.append({
            "vendor_id": vendor_id,
            "settled_charge_amount_cents": row["charge"],
            "settled_credit_amount_cents": row["credit"],
            "net_amount_cents": row["charge"] - row["credit"],
            "qualifying_entry_count": row["count"],
        })
    return {
        "status": "complete",
        "final": True,
        **common_output(checkpoint),
        "currency": "USD",
        "vendors": vendors,
    }


def emit_complete(checkpoint: dict[str, Any], calls_committed: int, output: Path | None) -> None:
    business_result = complete_output(checkpoint)
    if output is None:
        emit({**business_result, "page_calls_committed_this_run": calls_committed})
        return
    try:
        write_json_atomic(output, business_result)
    except OSError as exc:
        raise RollupError("result_write_failed", str(exc), output=str(output)) from exc
    emit({
        "status": "complete",
        "final": True,
        "snapshot_id": checkpoint["source"]["snapshot_id"],
        "interval": business_result["interval"],
        "coverage": business_result["coverage"],
        "currency": "USD",
        "vendor_count": len(business_result["vendors"]),
        "result_file": str(output),
        "page_calls_committed_this_run": calls_committed,
    })


def incomplete_output(checkpoint: dict[str, Any], calls_committed: int, reason: str, tranche: int) -> dict[str, Any]:
    return {
        "status": "incomplete",
        "final": False,
        **common_output(checkpoint),
        "pause_reason": reason,
        "tranche": tranche,
        "page_calls_committed_this_run": calls_committed,
        "continuation": "After the operator grants or confirms call capacity, rerun the identical command.",
    }


def run(args: argparse.Namespace) -> int:
    start = iso_date(args.start, "start")
    end = iso_date(args.end, "end")
    if start > end:
        raise RollupError("invalid_interval", "start must be on or before end")

    api = Path(args.api).resolve()
    source_state = Path(args.source_state).resolve()
    checkpoint_path = Path(args.checkpoint).resolve()
    output_path = Path(args.output).resolve() if args.output is not None else None
    if not api.is_file():
        raise RollupError("invalid_input", f"API script does not exist: {api}")
    if not source_state.is_file():
        raise RollupError("invalid_input", f"source state does not exist: {source_state}")
    reserved_paths = {api, source_state, checkpoint_path, Path(str(checkpoint_path) + ".lock")}
    if output_path is not None and output_path in reserved_paths:
        raise RollupError("invalid_input", "output must differ from the API, source state, checkpoint, and lock paths")

    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = Path(str(checkpoint_path) + ".lock")
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        metadata = describe(args.python, api, source_state)
        if checkpoint_path.exists():
            checkpoint = load_checkpoint(checkpoint_path)
            validate_checkpoint(checkpoint, api, source_state, checkpoint_path, output_path, start, end, metadata)
            if not checkpoint["progress"]["complete"] and output_path is not None and output_path.exists():
                raise RollupError(
                    "unexpected_result_file",
                    "result path exists while the checkpoint is incomplete; move it aside or use a new request path",
                    output=str(output_path),
                )
        else:
            if output_path is not None and output_path.exists():
                raise RollupError(
                    "result_path_exists",
                    "result path already exists for a new checkpoint; choose an unused output path",
                    output=str(output_path),
                )
            checkpoint = new_checkpoint(api, source_state, checkpoint_path, output_path, start, end, metadata)
            write_json_atomic(checkpoint_path, checkpoint)

        if checkpoint["progress"]["complete"]:
            emit_complete(checkpoint, 0, output_path)
            return 0

        allowance = min(EXPECTED_CALLS_PER_TRANCHE, metadata["remaining_calls"])
        if allowance == 0:
            emit(incomplete_output(checkpoint, 0, "tranche_call_budget_exhausted", metadata["tranche"]))
            return 10

        calls_committed = 0
        for _ in range(allowance):
            progress = checkpoint["progress"]
            cursor = progress["next_cursor"] if progress["started"] else None
            result = invoke(page_command(args.python, api, source_state, metadata["snapshot_id"], cursor))
            if result.returncode == 75:
                try:
                    error_body = parse_object(result.stdout, "page error")
                except ValueError:
                    error_body = {}
                if error_body.get("error") == "call_budget_exhausted":
                    emit(incomplete_output(checkpoint, calls_committed, "tranche_call_budget_exhausted", metadata["tranche"]))
                    return 10
            if result.returncode != 0:
                detail = result.stdout.strip() or result.stderr.strip() or f"exit {result.returncode}"
                try:
                    error_body = parse_object(result.stdout, "page error")
                except ValueError:
                    error_body = {}
                if result.returncode in {2, 4} and error_body.get("error") in {"invalid_cursor", "snapshot_mismatch"}:
                    raise RollupError(
                        "source_rejected_request", detail, source_exit_code=result.returncode,
                        checkpoint=str(checkpoint_path)
                    )
                raise UncertainPageError(
                    "page_response_uncertain",
                    "page command failed or its response was unavailable; quota may have been consumed",
                    source_exit_code=result.returncode,
                    source_detail=detail,
                    checkpoint=str(checkpoint_path),
                )
            try:
                body = parse_object(result.stdout, "page")
                items, next_cursor, tranche = validate_page(body, checkpoint)
                candidate = incorporate(checkpoint, items, next_cursor, tranche)
            except (KeyError, TypeError, ValueError) as exc:
                raise RollupError(
                    "source_contract_violation",
                    f"successful page call returned unusable data: {exc}",
                    page_call_consumed=True,
                    checkpoint=str(checkpoint_path),
                ) from exc
            try:
                write_json_atomic(checkpoint_path, candidate)
            except OSError as exc:
                raise UncertainPageError(
                    "checkpoint_commit_uncertain",
                    "page was returned but its checkpoint commit could not be confirmed",
                    checkpoint=str(checkpoint_path),
                    detail_os=str(exc),
                ) from exc
            checkpoint = candidate
            calls_committed += 1
            if checkpoint["progress"]["complete"]:
                emit_complete(checkpoint, calls_committed, output_path)
                return 0

        emit(incomplete_output(checkpoint, calls_committed, "tranche_boundary_reached", metadata["tranche"]))
        return 10


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Produce or continue a complete vendor reimbursement rollup from a ledger_api.py snapshot.",
        epilog="Exit codes: 0 complete; 10 safely incomplete; 20 invalid or rejected; 21 uncertain page effect.",
    )
    parser.add_argument("--api", required=True, help="path to the compatible ledger_api.py")
    parser.add_argument("--source-state", required=True, help="path to the existing immutable snapshot state")
    parser.add_argument("--checkpoint", required=True, help="durable checkpoint path, reused for continuation")
    parser.add_argument("--output", help="write the completed result atomically to this path; omit for stdout")
    parser.add_argument("--start", required=True, help="inclusive start date, YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="inclusive end date, YYYY-MM-DD")
    parser.add_argument("--python", default="python3.12", help="Python executable for ledger_api.py (default: python3.12)")
    return parser


def main() -> int:
    try:
        return run(build_parser().parse_args())
    except UncertainPageError as exc:
        emit(exc.payload)
        return 21
    except RollupError as exc:
        emit(exc.payload)
        return 20
    except KeyboardInterrupt:
        emit({"status": "error", "final": False, "error": "interrupted", "detail": "execution was interrupted"})
        return 21


if __name__ == "__main__":
    sys.exit(main())
