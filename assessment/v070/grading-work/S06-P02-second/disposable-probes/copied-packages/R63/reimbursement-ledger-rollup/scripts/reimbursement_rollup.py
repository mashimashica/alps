#!/usr/bin/env python3
"""Complete a paginated USD reimbursement-ledger rollup with resumable state."""

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


PAGE_LIMIT = 2
EXIT_INCOMPLETE = 75
EXIT_RESPONSE_LOST = 74
FIELDS = {
    "entry_id", "vendor_id", "posted_on", "kind", "status", "amount_cents", "currency"
}


class RollupError(Exception):
    """An error that can be represented as a public JSON result."""

    def __init__(self, reason: str, detail: str = "", *, recovery_required: bool = False):
        self.reason = reason
        self.detail = detail
        self.recovery_required = recovery_required


def fail(reason: str, detail: str = "", *, recovery_required: bool = False) -> RollupError:
    return RollupError(reason, detail, recovery_required=recovery_required)


def strict_date(value: str) -> dt.date:
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError as exc:
        raise fail("invalid_interval", f"invalid ISO date: {value!r}") from exc
    if parsed.isoformat() != value:
        raise fail("invalid_interval", "dates must use YYYY-MM-DD")
    return parsed


def run_api(python_cmd: str, api: Path, state: Path, command: str,
            snapshot: str | None = None, cursor: str | None = None) -> tuple[int, str, str]:
    args = [python_cmd, str(api), "--state", str(state), command]
    if command == "page":
        assert snapshot is not None
        args.extend(["--snapshot", snapshot])
        if cursor is not None:
            args.extend(["--cursor", cursor])
    completed = subprocess.run(args, text=True, capture_output=True, check=False)
    return completed.returncode, completed.stdout, completed.stderr


def response_json(stdout: str, stderr: str, *, consumed: bool) -> dict[str, Any]:
    try:
        value = json.loads(stdout)
    except (TypeError, json.JSONDecodeError) as exc:
        suffix = stderr.strip()
        detail = "page response was not valid JSON"
        if suffix:
            detail += f"; stderr: {suffix[:500]}"
        raise fail("response_unusable", detail, recovery_required=consumed) from exc
    if not isinstance(value, dict):
        raise fail("response_unusable", "API response must be a JSON object", recovery_required=consumed)
    return value


def atomic_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def load_progress(path: Path, request: dict[str, str], state: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise fail("progress_unreadable", str(exc)) from exc
    if not isinstance(value, dict) or value.get("version") != 1:
        raise fail("progress_unreadable", "progress file has an unsupported format")
    if value.get("request") != request:
        raise fail("progress_mismatch", "progress file belongs to a different date interval")
    if value.get("source_state") != str(state):
        raise fail("progress_mismatch", "progress file belongs to a different source state")
    if not isinstance(value.get("aggregates"), dict) or not isinstance(value.get("seen"), dict):
        raise fail("progress_unreadable", "progress file is missing aggregation state")
    return value


def initial_progress(path: Path, request: dict[str, str], state: Path,
                     descriptor: dict[str, Any]) -> dict[str, Any]:
    required = ("snapshot_id", "total_records", "page_size", "calls_per_tranche", "tranche")
    if any(key not in descriptor for key in required):
        raise fail("metadata_unusable", "describe response is missing required metadata")
    if not isinstance(descriptor["snapshot_id"], str) or not descriptor["snapshot_id"]:
        raise fail("metadata_unusable", "describe returned an invalid snapshot_id")
    if type(descriptor["total_records"]) is not int or descriptor["total_records"] < 0:
        raise fail("metadata_unusable", "describe returned an invalid total_records")
    if descriptor["page_size"] != 3:
        raise fail("unsupported_source", "source page_size is not three")
    if descriptor["calls_per_tranche"] != PAGE_LIMIT:
        raise fail("unsupported_source", "source calls_per_tranche is not two")
    result = {
        "version": 1,
        "request": request,
        "source_state": str(state),
        "snapshot_id": descriptor["snapshot_id"],
        "total_records": descriptor["total_records"],
        "aggregates": {},
        "seen": {},
        "next_cursor": None,
        "complete": False,
        "recovery_required": False,
        "pages_applied": 0,
    }
    atomic_write(path, result)
    return result


def validate_item(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict) or set(item) != FIELDS:
        raise fail("response_unusable", "page item fields do not match the ledger contract")
    if (not isinstance(item["entry_id"], str) or not item["entry_id"] or
            not isinstance(item["vendor_id"], str) or not item["vendor_id"]):
        raise fail("response_unusable", "page item has an invalid identifier")
    try:
        posted = dt.date.fromisoformat(item["posted_on"])
    except (TypeError, ValueError) as exc:
        raise fail("response_unusable", "page item has an invalid posted_on date") from exc
    if posted.isoformat() != item["posted_on"]:
        raise fail("response_unusable", "page item posted_on is not YYYY-MM-DD")
    if item["kind"] not in {"charge", "credit"} or item["status"] not in {"settled", "pending", "void"}:
        raise fail("response_unusable", "page item has an invalid kind or status")
    if type(item["amount_cents"]) is not int or item["amount_cents"] < 0 or item["currency"] != "USD":
        raise fail("response_unusable", "page item amount must be a nonnegative USD integer")
    return item


def item_fingerprint(item: dict[str, Any]) -> str:
    return json.dumps(item, sort_keys=True, separators=(",", ":"))


def apply_page(progress: dict[str, Any], items: list[Any], start: dt.date, end: dt.date) -> None:
    seen: dict[str, str] = progress["seen"]
    aggregates: dict[str, dict[str, int]] = progress["aggregates"]
    for raw_item in items:
        item = validate_item(raw_item)
        entry_id = item["entry_id"]
        fingerprint = item_fingerprint(item)
        if entry_id in seen:
            if seen[entry_id] != fingerprint:
                raise fail("response_unusable", f"entry_id {entry_id!r} changed on a repeated page")
            continue
        seen[entry_id] = fingerprint
        posted = dt.date.fromisoformat(item["posted_on"])
        if item["status"] != "settled" or not (start <= posted <= end):
            continue
        vendor = item["vendor_id"]
        aggregate = aggregates.setdefault(vendor, {"charge_cents": 0, "credit_cents": 0, "count": 0})
        aggregate["count"] += 1
        if item["kind"] == "charge":
            aggregate["charge_cents"] += item["amount_cents"]
        else:
            aggregate["credit_cents"] += item["amount_cents"]


def final_rows(progress: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for vendor_id, aggregate in progress["aggregates"].items():
        rows.append({
            "vendor_id": vendor_id,
            "settled_charge_cents": aggregate["charge_cents"],
            "settled_credit_cents": aggregate["credit_cents"],
            "net_cents": aggregate["charge_cents"] - aggregate["credit_cents"],
            "qualifying_entry_count": aggregate["count"],
        })
    return sorted(rows, key=lambda row: row["vendor_id"])


def public_result(progress: dict[str, Any], progress_path: Path, *, status: str,
                  tranche: Any, pages_this_run: int, reason: str | None = None,
                  detail: str | None = None, recovery_required: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": status,
        "interval": progress["request"],
        "snapshot_id": progress["snapshot_id"],
        "source_total_records": progress["total_records"],
        "tranche": tranche,
        "pages_applied_this_run": pages_this_run,
        "progress_path": str(progress_path),
    }
    if status == "complete":
        result["results"] = final_rows(progress)
    else:
        result["next_cursor"] = progress["next_cursor"]
        if reason:
            result["reason"] = reason
        if detail:
            result["detail"] = detail
        result["recovery_required"] = recovery_required
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", required=True, help="path to ledger_api.py")
    parser.add_argument("--state", required=True, help="path to the source state database")
    parser.add_argument("--progress", required=True, help="durable JSON continuation state")
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--python", default="python3.12", dest="python_cmd",
                        help="Python executable used to invoke the API (default: python3.12)")
    args = parser.parse_args()

    try:
        start = strict_date(args.start_date)
        end = strict_date(args.end_date)
        if start > end:
            raise fail("invalid_interval", "start-date must be on or before end-date")
        request = {"start_date": args.start_date, "end_date": args.end_date}
        api = Path(args.api).resolve()
        state = Path(args.state).resolve()
        progress_path = Path(args.progress).resolve()
        if not api.is_file() or not state.is_file():
            raise fail("input_unavailable", "api and state must be existing files")

        descriptor_code, descriptor_out, descriptor_err = run_api(args.python_cmd, api, state, "describe")
        descriptor = response_json(descriptor_out, descriptor_err, consumed=False)
        if descriptor_code != 0:
            raise fail(descriptor.get("error", "metadata_error"), descriptor.get("detail", "describe failed"))
        progress = load_progress(progress_path, request, state)
        if progress is None:
            progress = initial_progress(progress_path, request, state, descriptor)
        elif progress["snapshot_id"] != descriptor.get("snapshot_id") or progress["total_records"] != descriptor.get("total_records"):
            raise fail("snapshot_changed", "source metadata does not match the saved continuation state")
        if progress.get("complete"):
            print(json.dumps(public_result(progress, progress_path, status="complete",
                                            tranche=descriptor.get("tranche"), pages_this_run=0),
                             sort_keys=True, separators=(",", ":")))
            return 0

        pages_this_run = 0
        while pages_this_run < PAGE_LIMIT and not progress.get("complete"):
            cursor = progress.get("next_cursor")
            page_code, page_out, page_err = run_api(args.python_cmd, api, state, "page",
                                                    snapshot=progress["snapshot_id"], cursor=cursor)
            try:
                page = response_json(page_out, page_err, consumed=True)
            except RollupError as exc:
                progress["recovery_required"] = exc.recovery_required
                atomic_write(progress_path, progress)
                result = public_result(progress, progress_path, status="error",
                                       tranche=descriptor.get("tranche"), pages_this_run=pages_this_run,
                                       reason=exc.reason, detail=exc.detail,
                                       recovery_required=exc.recovery_required)
                print(json.dumps(result, sort_keys=True, separators=(",", ":")))
                return EXIT_RESPONSE_LOST if exc.recovery_required else 2
            if page_code == 75 or page.get("error") == "call_budget_exhausted":
                result = public_result(progress, progress_path, status="incomplete",
                                       tranche=page.get("tranche", descriptor.get("tranche")),
                                       pages_this_run=pages_this_run,
                                       reason="call_budget_exhausted")
                print(json.dumps(result, sort_keys=True, separators=(",", ":")))
                return EXIT_INCOMPLETE
            if page_code != 0 or page.get("error"):
                raise fail(page.get("error", "page_error"), page.get("detail", "page failed"))
            try:
                if page.get("snapshot_id") != progress["snapshot_id"] or page.get("total_records") != progress["total_records"]:
                    raise fail("response_unusable", "page metadata does not match the saved snapshot")
                items = page.get("items")
                if not isinstance(items, list) or "next_cursor" not in page:
                    raise fail("response_unusable", "page response is missing items or next_cursor")
                if page["next_cursor"] is not None and (
                        not isinstance(page["next_cursor"], str) or not page["next_cursor"]):
                    raise fail("response_unusable", "page next_cursor must be a nonempty string or null")
                apply_page(progress, items, start, end)
                progress["next_cursor"] = page["next_cursor"]
                progress["complete"] = page["next_cursor"] is None
                progress["recovery_required"] = False
                progress["pages_applied"] += 1
                atomic_write(progress_path, progress)
            except RollupError as exc:
                # The source call succeeded, but the page could not be incorporated.
                # Preserve the old cursor and make the billable retry explicit.
                progress["recovery_required"] = True
                atomic_write(progress_path, progress)
                result = public_result(progress, progress_path, status="error",
                                       tranche=descriptor.get("tranche"), pages_this_run=pages_this_run,
                                       reason=exc.reason, detail=exc.detail, recovery_required=True)
                print(json.dumps(result, sort_keys=True, separators=(",", ":")))
                return EXIT_RESPONSE_LOST
            pages_this_run += 1

        if progress.get("complete"):
            result = public_result(progress, progress_path, status="complete",
                                   tranche=descriptor.get("tranche"), pages_this_run=pages_this_run)
            print(json.dumps(result, sort_keys=True, separators=(",", ":")))
            return 0
        result = public_result(progress, progress_path, status="incomplete",
                               tranche=descriptor.get("tranche"), pages_this_run=pages_this_run,
                               reason="tranche_boundary")
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return EXIT_INCOMPLETE
    except RollupError as exc:
        result = {"status": "error", "reason": exc.reason}
        if exc.detail:
            result["detail"] = exc.detail
        result["recovery_required"] = exc.recovery_required
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return EXIT_RESPONSE_LOST if exc.recovery_required else 2
    except (OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "error", "reason": "local_io_error", "detail": str(exc),
                          "recovery_required": False}, sort_keys=True, separators=(",", ":")))
        return 2


if __name__ == "__main__":
    sys.exit(main())
