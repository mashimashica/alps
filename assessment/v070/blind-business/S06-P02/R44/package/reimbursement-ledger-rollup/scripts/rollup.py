#!/usr/bin/env python3
"""Resumable exact-cent rollup over the local paginated ledger API."""

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


EXIT_OK = 0
EXIT_ERROR = 2
EXIT_INCOMPLETE = 75

RECORD_FIELDS = {
    "entry_id", "vendor_id", "posted_on", "kind", "status", "amount_cents", "currency"
}
KINDS = {"charge", "credit"}
STATUSES = {"settled", "pending", "void"}


class RollupError(Exception):
    """A caller-actionable validation or source-contract error."""


def fail(message: str, **details: Any) -> None:
    body = {"status": "error", "error": message}
    body.update(details)
    print(json.dumps(body, sort_keys=True, separators=(",", ":")))


def parse_date(value: str, label: str) -> dt.date:
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError as exc:
        raise RollupError(f"{label} must be an ISO calendar date (YYYY-MM-DD)") from exc
    if parsed.isoformat() != value:
        raise RollupError(f"{label} must be an ISO calendar date (YYYY-MM-DD)")
    return parsed


def read_json(text: str, context: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RollupError(f"{context} did not return valid JSON") from exc
    if not isinstance(value, dict):
        raise RollupError(f"{context} did not return a JSON object")
    return value


def run_api(api: Path, state: Path, args: list[str]) -> tuple[int, dict[str, Any] | None, str]:
    command = [sys.executable, str(api), "--state", str(state), *args]
    try:
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
    except OSError as exc:
        raise RollupError(f"could not execute ledger API: {exc}") from exc
    stdout = completed.stdout.strip()
    if not stdout:
        return completed.returncode, None, ""
    try:
        response = read_json(stdout, "ledger API")
    except RollupError:
        return completed.returncode, None, stdout
    return completed.returncode, response, stdout


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
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def load_checkpoint(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RollupError(f"cannot read checkpoint {path}: {exc}") from exc
    if not isinstance(value, dict) or value.get("version") != 1:
        raise RollupError("checkpoint is not a version 1 rollup checkpoint")
    required = {
        "version", "source_state", "snapshot_id", "from_date", "to_date",
        "total_records", "next_cursor", "seen_entry_ids", "totals", "pages_fetched",
    }
    if set(value) != required:
        raise RollupError("checkpoint fields do not match the rollup format")
    if not isinstance(value["seen_entry_ids"], list) or not isinstance(value["totals"], dict):
        raise RollupError("checkpoint collections are malformed")
    return value


def new_checkpoint(state: Path, descriptor: dict[str, Any], start: str, end: str) -> dict[str, Any]:
    try:
        snapshot = descriptor["snapshot_id"]
        total = descriptor["total_records"]
    except KeyError as exc:
        raise RollupError("describe response is missing source metadata") from exc
    if not isinstance(snapshot, str) or not snapshot or type(total) is not int or total < 0:
        raise RollupError("describe response has invalid source metadata")
    return {
        "version": 1,
        "source_state": str(state),
        "snapshot_id": snapshot,
        "from_date": start,
        "to_date": end,
        "total_records": total,
        "next_cursor": None,
        "seen_entry_ids": [],
        "totals": {},
        "pages_fetched": 0,
    }


def check_checkpoint(checkpoint: dict[str, Any], state: Path, start: str, end: str,
                     descriptor: dict[str, Any]) -> None:
    if checkpoint["source_state"] != str(state) or checkpoint["from_date"] != start or checkpoint["to_date"] != end:
        raise RollupError("checkpoint belongs to a different source state or date interval")
    if checkpoint["snapshot_id"] != descriptor.get("snapshot_id"):
        raise RollupError("source snapshot changed since the checkpoint was created")
    if checkpoint["total_records"] != descriptor.get("total_records"):
        raise RollupError("source record count changed since the checkpoint was created")
    if len(set(checkpoint["seen_entry_ids"])) != len(checkpoint["seen_entry_ids"]):
        raise RollupError("checkpoint contains duplicate entry IDs")


def validate_item(item: Any) -> None:
    if not isinstance(item, dict) or set(item) != RECORD_FIELDS:
        raise RollupError("page item fields do not match the ledger contract")
    if not isinstance(item["entry_id"], str) or not item["entry_id"]:
        raise RollupError("page item has an invalid entry_id")
    if not isinstance(item["vendor_id"], str) or not item["vendor_id"]:
        raise RollupError("page item has an invalid vendor_id")
    try:
        posted = dt.date.fromisoformat(item["posted_on"])
    except (TypeError, ValueError) as exc:
        raise RollupError("page item has an invalid posted_on date") from exc
    if posted.isoformat() != item["posted_on"]:
        raise RollupError("page item posted_on is not canonical ISO format")
    if item["kind"] not in KINDS or item["status"] not in STATUSES:
        raise RollupError("page item has an invalid kind or status")
    if type(item["amount_cents"]) is not int or item["amount_cents"] < 0:
        raise RollupError("page item has an invalid integer amount")
    if item["currency"] != "USD":
        raise RollupError("page item is not in USD")


def add_page(checkpoint: dict[str, Any], response: dict[str, Any], start: dt.date, end: dt.date,
             current_cursor: str | None) -> None:
    if response.get("snapshot_id") != checkpoint["snapshot_id"]:
        raise RollupError("page snapshot does not match the checkpoint")
    if response.get("total_records") != checkpoint["total_records"]:
        raise RollupError("page total_records does not match the checkpoint")
    items = response.get("items")
    if not isinstance(items, list):
        raise RollupError("page response is missing an items list")
    next_cursor = response.get("next_cursor")
    if next_cursor is not None and (not isinstance(next_cursor, str) or not next_cursor):
        raise RollupError("page next_cursor is invalid")
    if next_cursor == current_cursor:
        raise RollupError("page next_cursor did not advance")
    if len(items) > 3 or (not items and next_cursor is not None):
        raise RollupError("page size or empty-page cursor is invalid")
    seen = set(checkpoint["seen_entry_ids"])
    page_ids: set[str] = set()
    for item in items:
        validate_item(item)
        entry_id = item["entry_id"]
        if entry_id in page_ids:
            raise RollupError("page contains a duplicate entry_id")
        page_ids.add(entry_id)
        if entry_id in seen:
            continue  # A retry of a previously incorporated page is safe.
        seen.add(entry_id)
        if item["status"] != "settled" or not (start.isoformat() <= item["posted_on"] <= end.isoformat()):
            continue
        vendor = item["vendor_id"]
        bucket = checkpoint["totals"].setdefault(vendor, {"charge_cents": 0, "credit_cents": 0, "qualifying_entry_count": 0})
        if item["kind"] == "charge":
            bucket["charge_cents"] += item["amount_cents"]
        else:
            bucket["credit_cents"] += item["amount_cents"]
        bucket["qualifying_entry_count"] += 1
    checkpoint["seen_entry_ids"] = sorted(seen)
    checkpoint["next_cursor"] = next_cursor
    checkpoint["pages_fetched"] += 1


def rows(checkpoint: dict[str, Any]) -> list[dict[str, Any]]:
    output = []
    for vendor in sorted(checkpoint["totals"]):
        bucket = checkpoint["totals"][vendor]
        output.append({
            "vendor_id": vendor,
            "settled_charge_cents": bucket["charge_cents"],
            "settled_credit_cents": bucket["credit_cents"],
            "net_cents": bucket["charge_cents"] - bucket["credit_cents"],
            "qualifying_entry_count": bucket["qualifying_entry_count"],
        })
    return output


def main(arguments: argparse.Namespace) -> int:
    start = parse_date(arguments.start, "--from")
    end = parse_date(arguments.end, "--to")
    if start > end:
        raise RollupError("--from must be on or before --to")
    state = Path(arguments.state).resolve()
    api = Path(arguments.api).resolve()
    checkpoint_path = Path(arguments.checkpoint).resolve()
    if not state.is_file() or not api.is_file():
        raise RollupError("--state and --api must name existing files")

    code, descriptor, raw = run_api(api, state, ["describe"])
    if code != 0 or descriptor is None:
        raise RollupError(f"describe failed with exit {code}: {raw or descriptor}")
    checkpoint = load_checkpoint(checkpoint_path)
    if checkpoint is None:
        checkpoint = new_checkpoint(state, descriptor, start.isoformat(), end.isoformat())
        atomic_write(checkpoint_path, checkpoint)
    else:
        check_checkpoint(checkpoint, state, start.isoformat(), end.isoformat(), descriptor)

    pages_this_run = 0
    while checkpoint["next_cursor"] is not None or checkpoint["pages_fetched"] == 0:
        page_args = ["page", "--snapshot", checkpoint["snapshot_id"]]
        if checkpoint["next_cursor"] is not None:
            page_args += ["--cursor", checkpoint["next_cursor"]]
        code, response, raw = run_api(api, state, page_args)
        if code == EXIT_INCOMPLETE:
            print(json.dumps({
                "status": "incomplete", "reason": "call_budget_exhausted", "final": False,
                "snapshot_id": checkpoint["snapshot_id"], "from_date": checkpoint["from_date"],
                "to_date": checkpoint["to_date"], "pages_fetched_this_run": pages_this_run,
                "next_cursor": checkpoint["next_cursor"], "partial_rows": rows(checkpoint),
                "checkpoint": str(checkpoint_path),
            }, sort_keys=True, separators=(",", ":")))
            return EXIT_INCOMPLETE
        if code != 0:
            raise RollupError(f"page failed with exit {code}: {raw or response}")
        if response is None:
            print(json.dumps({
                "status": "recovery_required", "reason": "page_response_unusable", "final": False,
                "snapshot_id": checkpoint["snapshot_id"], "from_date": checkpoint["from_date"],
                "to_date": checkpoint["to_date"], "pages_fetched_this_run": pages_this_run,
                "next_cursor": checkpoint["next_cursor"], "partial_rows": rows(checkpoint),
                "checkpoint": str(checkpoint_path),
            }, sort_keys=True, separators=(",", ":")))
            return EXIT_INCOMPLETE
        add_page(checkpoint, response, start, end, checkpoint["next_cursor"])
        atomic_write(checkpoint_path, checkpoint)
        pages_this_run += 1

    if len(checkpoint["seen_entry_ids"]) != checkpoint["total_records"]:
        raise RollupError("source ended before all metadata records were observed")
    print(json.dumps({
        "status": "complete", "final": True, "snapshot_id": checkpoint["snapshot_id"],
        "from_date": checkpoint["from_date"], "to_date": checkpoint["to_date"],
        "source_total_records": checkpoint["total_records"], "pages_fetched": checkpoint["pages_fetched"],
        "result": {"rows": rows(checkpoint)}, "checkpoint": str(checkpoint_path),
    }, sort_keys=True, separators=(",", ":")))
    return EXIT_OK


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--state", required=True, help="initialized ledger_api.py state")
    result.add_argument("--api", required=True, help="ledger_api.py executable path")
    result.add_argument("--from", dest="start", required=True, help="inclusive YYYY-MM-DD")
    result.add_argument("--to", dest="end", required=True, help="inclusive YYYY-MM-DD")
    result.add_argument("--checkpoint", required=True, help="durable JSON checkpoint path")
    return result


if __name__ == "__main__":
    try:
        sys.exit(main(parser().parse_args()))
    except RollupError as error:
        fail(str(error))
        sys.exit(EXIT_ERROR)
