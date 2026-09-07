#!/usr/bin/env python3
"""Create an evidence-aware monthly receiving review from a JSON input."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
LINE_KEYS = ("order_id", "sku")
REQUIRED_RESPONSIBILITIES = ("purchasing_coordinator", "warehouse_lead", "data_steward")


def fail(message: str) -> int:
    print(f"receiving_review: error: {message}", file=sys.stderr)
    return 2


def is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def line_key(order_id: Any, sku: Any) -> tuple[str, str]:
    return (str(order_id), str(sku))


def line_json(key: tuple[str, str]) -> dict[str, str]:
    return {"order_id": key[0], "sku": key[1]}


def month_valid(value: Any) -> bool:
    return isinstance(value, str) and MONTH_RE.fullmatch(value) is not None


def load_input(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def add_warning(warnings: list[dict[str, Any]], code: str, message: str, **extra: Any) -> None:
    item: dict[str, Any] = {"code": code, "message": message}
    item.update(extra)
    warnings.append(item)


def draft_for(
    status: str,
    line: dict[str, Any],
    responsibilities: dict[str, str],
    observed: int | None,
    ordered: int,
    blocking: list[str],
) -> dict[str, Any] | None:
    contact = line.get("supplier_contact")
    if status == "complete_shortfall":
        remaining = ordered - int(observed)  # final_position guarantees observed here
        recipient = responsibilities["purchasing_coordinator"]
        return {
            "recipient": recipient,
            "role": "purchasing_coordinator",
            "subject": f"Receipt follow-up for {line['order_id']} / {line['sku']}",
            "action": f"Ask {contact} to confirm and arrange receipt of the remaining {remaining} unit(s).",
            "draft": (
                f"To: {contact}\nSubject: Receipt follow-up for {line['order_id']} / {line['sku']}\n\n"
                f"Please confirm the remaining {remaining} unit(s) for order {line['order_id']} "
                f"and advise the expected receipt date."
            ),
        }
    if status == "complete_excess":
        excess = int(observed) - ordered
        recipient = responsibilities["warehouse_lead"]
        return {
            "recipient": recipient,
            "role": "warehouse_lead",
            "subject": f"Receipt reconciliation for {line['order_id']} / {line['sku']}",
            "action": f"Reconcile the surplus of {excess} unit(s) against the order and receiving evidence.",
            "draft": (
                f"To: {recipient}\nSubject: Receipt reconciliation for {line['order_id']} / {line['sku']}\n\n"
                f"Please reconcile the {excess} unit surplus for order {line['order_id']} "
                "against the order and receiving records, and document the result."
            ),
        }
    if status == "incomplete_export":
        recipient = responsibilities["data_steward"]
        return {
            "recipient": recipient,
            "role": "data_steward",
            "subject": f"Complete receiving export for {line['order_id']} / {line['sku']}",
            "action": "Provide or confirm the full requested-month receipt export before final comparison.",
            "draft": (
                f"To: {recipient}\nSubject: Complete receiving export for {line['order_id']} / {line['sku']}\n\n"
                f"Please provide or confirm the complete receiving export for {line['order_id']} / "
                f"{line['sku']} for the requested month so its final receipt position can be assessed."
            ),
        }
    if status in {"identity_reconciliation_required", "conflicting_evidence"}:
        recipient = (
            f"{responsibilities['purchasing_coordinator']} and {responsibilities['data_steward']}"
        )
        detail = " and ".join(blocking)
        return {
            "recipient": recipient,
            "role": "purchasing_coordinator_and_data_steward",
            "subject": f"Reconcile receiving evidence for {line['order_id']} / {line['sku']}",
            "action": f"Reconcile the identified source records before final line comparison ({detail}).",
            "draft": (
                f"To: {recipient}\nSubject: Reconcile receiving evidence for {line['order_id']} / {line['sku']}\n\n"
                f"Please reconcile the order and receiving source records for {line['order_id']} / "
                f"{line['sku']} ({detail}) and confirm the evidence to use for the final review."
            ),
        }
    return None


def process(data: Any) -> dict[str, Any]:
    root = require_object(data, "input")
    month = root.get("month")
    if not month_valid(month):
        raise ValueError("month must be a YYYY-MM string")
    orders = root.get("orders")
    events = root.get("events")
    coverage = root.get("coverage")
    responsibilities = root.get("responsibilities")
    if not isinstance(orders, list):
        raise ValueError("orders must be an array")
    if not isinstance(events, list):
        raise ValueError("events must be an array")
    if not isinstance(coverage, list):
        raise ValueError("coverage must be an array")
    responsibilities = require_object(responsibilities, "responsibilities")
    missing_roles = [r for r in REQUIRED_RESPONSIBILITIES if not isinstance(responsibilities.get(r), str) or not responsibilities[r].strip()]
    if missing_roles:
        raise ValueError("responsibilities missing non-empty roles: " + ", ".join(missing_roles))

    warnings: list[dict[str, Any]] = []
    lines: list[dict[str, Any]] = []
    order_lines: dict[str, set[str]] = defaultdict(set)
    line_map: dict[tuple[str, str], dict[str, Any]] = {}
    for index, raw in enumerate(orders):
        try:
            item = require_object(raw, f"orders[{index}]")
            if not isinstance(item.get("order_id"), str) or not item["order_id"]:
                raise ValueError("order_id must be a non-empty string")
            if not isinstance(item.get("sku"), str) or not item["sku"]:
                raise ValueError("sku must be a non-empty string")
            if not is_int(item.get("ordered")) or item["ordered"] <= 0:
                raise ValueError("ordered must be a positive integer")
            if not isinstance(item.get("supplier_contact"), str) or not item["supplier_contact"].strip():
                raise ValueError("supplier_contact must be a non-empty string")
            key = line_key(item["order_id"], item["sku"])
            if key in line_map:
                raise ValueError(f"duplicate order line {key[0]} / {key[1]}")
            record = {
                "order_id": item["order_id"],
                "sku": item["sku"],
                "ordered": item["ordered"],
                "supplier_contact": item["supplier_contact"],
            }
            line_map[key] = record
            order_lines[key[0]].add(key[1])
            lines.append(record)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"orders[{index}]: {exc}") from exc

    coverage_map: dict[tuple[str, str], list[bool]] = defaultdict(list)
    for index, raw in enumerate(coverage):
        if not isinstance(raw, dict):
            add_warning(warnings, "invalid_coverage", f"coverage[{index}] is not an object", row=index)
            continue
        key_values = (raw.get("order_id"), raw.get("sku"))
        if not all(isinstance(v, str) and v for v in key_values):
            add_warning(warnings, "invalid_coverage", "coverage row has no usable order_id and sku", row=index)
            continue
        if raw.get("month") != month:
            add_warning(warnings, "coverage_month_ignored", "coverage row is for another month", row=index)
            continue
        if not isinstance(raw.get("complete"), bool):
            add_warning(warnings, "invalid_coverage", "coverage complete must be boolean", row=index, line=line_json(line_key(*key_values)))
            continue
        key = line_key(*key_values)
        coverage_map[key].append(raw["complete"])
        if key not in line_map:
            add_warning(warnings, "coverage_outside_scope", "coverage row does not identify a supplied order line", row=index, line=line_json(key))

    # Validate and de-duplicate events while retaining row-level problems.
    event_by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    invalid_event_lines: set[tuple[str, str]] = set()
    out_of_scope_events: list[dict[str, Any]] = []
    for index, raw in enumerate(events):
        if not isinstance(raw, dict):
            add_warning(warnings, "invalid_event", f"events[{index}] is not an object", row=index)
            continue
        required = ("event_id", "order_id", "sku", "event_month", "quantity")
        if any(key not in raw for key in required):
            add_warning(warnings, "invalid_event", "event is missing a required value; no zero was substituted", row=index)
            if (isinstance(raw.get("order_id"), str) and isinstance(raw.get("sku"), str)
                    and raw.get("event_month") == month
                    and line_key(raw["order_id"], raw["sku"]) in line_map):
                invalid_event_lines.add(line_key(raw["order_id"], raw["sku"]))
            continue
        if not all(isinstance(raw[key], str) and raw[key] for key in ("event_id", "order_id", "sku")) or not month_valid(raw["event_month"]) or not is_int(raw["quantity"]):
            add_warning(warnings, "invalid_event", "event has an invalid identifier, month, or signed integer quantity; no zero was substituted", row=index)
            if (isinstance(raw.get("order_id"), str) and isinstance(raw.get("sku"), str)
                    and raw.get("event_month") == month
                    and line_key(raw["order_id"], raw["sku"]) in line_map):
                invalid_event_lines.add(line_key(raw["order_id"], raw["sku"]))
            continue
        item = {
            "event_id": raw["event_id"],
            "order_id": raw["order_id"],
            "sku": raw["sku"],
            "event_month": raw["event_month"],
            "quantity": raw["quantity"],
        }
        event_by_id[item["event_id"]].append(item)
        if item["order_id"] not in order_lines:
            out_of_scope_events.append({**item, "reason": "order outside supplied order set"})

    # Same ID with differing content is a conflict. Exact copies are harmless.
    conflict_ids: set[str] = set()
    conflict_lines: set[tuple[str, str]] = set()
    for event_id, records in event_by_id.items():
        unique = {json.dumps(record, sort_keys=True, separators=(",", ":")) for record in records}
        if len(unique) <= 1:
            continue
        conflict_ids.add(event_id)
        for record in records:
            if record["order_id"] in order_lines and record["sku"] in order_lines[record["order_id"]] and record["event_month"] == month:
                conflict_lines.add(line_key(record["order_id"], record["sku"]))
    # Distinct event IDs are the units used for a subtotal; identical rows count once.
    usable_events: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    seen_event_content: set[str] = set()
    for records in event_by_id.values():
        for record in records:
            signature = json.dumps(record, sort_keys=True, separators=(",", ":"))
            if signature in seen_event_content:
                continue
            seen_event_content.add(signature)
            key = line_key(record["order_id"], record["sku"])
            if key in line_map and record["event_month"] == month:
                usable_events[key].append(record)

    identity_orders: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for records in event_by_id.values():
        for item in records:
            if item["event_month"] == month and item["order_id"] in order_lines and item["sku"] not in order_lines[item["order_id"]]:
                identity_orders[item["order_id"]].append(item)

    report_lines: list[dict[str, Any]] = []
    follow_up_drafts: list[dict[str, Any]] = []
    for base in lines:
        key = line_key(base["order_id"], base["sku"])
        records = usable_events.get(key, [])
        observed = sum(item["quantity"] for item in records)
        coverage_values = coverage_map.get(key, [])
        blocking: list[str] = []
        if key[0] in identity_orders:
            blocking.append("current-month event SKU is absent from this order")
        if key in conflict_lines:
            blocking.append("event_id has conflicting content")
        if key in invalid_event_lines:
            blocking.append("current-month event evidence is invalid")
        if not coverage_values:
            blocking.append("coverage declaration is missing")
        elif any(value is False for value in coverage_values):
            blocking.append("coverage declares an incomplete export")
        elif len(set(coverage_values)) > 1:
            blocking.append("coverage declarations conflict")
        if any(w.get("code") == "invalid_event" for w in warnings) and not records:
            # Do not assign an unidentifiable malformed row to every line; explain only the observable gap.
            pass

        complete = bool(coverage_values) and all(coverage_values) and len(set(coverage_values)) == 1
        if key[0] in identity_orders:
            status = "identity_reconciliation_required"
        elif key in conflict_lines or (coverage_values and len(set(coverage_values)) > 1):
            status = "conflicting_evidence"
        elif not complete or key in invalid_event_lines:
            status = "incomplete_export"
        elif observed == base["ordered"]:
            status = "received_as_ordered"
        elif observed < base["ordered"]:
            status = "complete_shortfall"
        else:
            status = "complete_excess"
        item: dict[str, Any] = {
            "order_id": base["order_id"],
            "sku": base["sku"],
            "ordered": base["ordered"],
            "supplier_contact": base["supplier_contact"],
            "status": status,
            "coverage": ("complete" if complete else ("incomplete" if coverage_values else "missing")),
            "supporting_event_ids": sorted({r["event_id"] for r in records}),
            "observed_subtotal": observed,
        }
        if blocking:
            item["blocking_conditions"] = blocking
        if status in {"received_as_ordered", "complete_shortfall", "complete_excess"}:
            item["final_position"] = {
                "net_received": observed,
                "ordered": base["ordered"],
                "difference": observed - base["ordered"],
            }
        draft = draft_for(status, item, responsibilities, observed, base["ordered"], blocking)
        if draft is not None:
            item["follow_up"] = draft
            follow_up_drafts.append({"order_id": base["order_id"], "sku": base["sku"], **draft})
        report_lines.append(item)

    anomalies: list[dict[str, Any]] = []
    for event_id in sorted(conflict_ids):
        anomalies.append({"type": "conflicting_event_id", "event_id": event_id, "message": "Different content was supplied for the same event_id."})
    for order_id, records in sorted(identity_orders.items()):
        anomalies.append({"type": "order_sku_identity_mismatch", "order_id": order_id, "events": sorted({r["event_id"] for r in records}), "message": "A current-month event uses a SKU absent from the supplied order."})

    return {
        "schema_version": "1.0",
        "scope": {"month": month, "order_line_count": len(lines)},
        "lines": report_lines,
        "anomalies": anomalies,
        "out_of_scope_events": out_of_scope_events,
        "validation_warnings": warnings,
        "follow_up_drafts": follow_up_drafts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Review monthly purchase-order receiving evidence")
    parser.add_argument("input", help="JSON input path, or - for stdin")
    parser.add_argument("--output", help="write report JSON to this path instead of stdout")
    parser.add_argument("--pretty", action="store_true", help="indent report JSON")
    args = parser.parse_args()
    try:
        report = process(load_input(args.input))
    except FileNotFoundError as exc:
        return fail(str(exc))
    except json.JSONDecodeError as exc:
        return fail(f"invalid JSON: {exc}")
    except (OSError, ValueError, TypeError) as exc:
        return fail(str(exc))
    rendered = json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=False) + "\n"
    if args.output:
        try:
            Path(args.output).write_text(rendered, encoding="utf-8")
        except OSError as exc:
            return fail(f"cannot write output: {exc}")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
