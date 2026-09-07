#!/usr/bin/env python3
"""Calculate a monthly receiving review from the documented JSON contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
REQUIRED_TOP = ("month", "orders", "events", "coverage", "responsibilities")


class InputError(ValueError):
    pass


def fail(message: str) -> None:
    raise InputError(message)


def require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{label} must be an array")
    return value


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a non-empty string")
    return value


def require_month(value: Any, label: str) -> str:
    value = require_string(value, label)
    if not MONTH_RE.fullmatch(value):
        fail(f"{label} must use YYYY-MM with a valid month")
    return value


def require_int(value: Any, label: str, positive: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        fail(f"{label} must be an integer")
    if positive and value <= 0:
        fail(f"{label} must be a positive integer")
    return value


def normalize(data: Any) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    root = require_object(data, "input")
    missing = [key for key in REQUIRED_TOP if key not in root]
    if missing:
        fail("input is missing required field(s): " + ", ".join(missing))
    month = require_month(root["month"], "month")

    orders: list[dict[str, Any]] = []
    order_keys: set[tuple[str, str]] = set()
    order_ids: set[str] = set()
    for index, raw in enumerate(require_list(root["orders"], "orders")):
        item = require_object(raw, f"orders[{index}]")
        order_id = require_string(item.get("order_id"), f"orders[{index}].order_id")
        sku = require_string(item.get("sku"), f"orders[{index}].sku")
        ordered = require_int(item.get("ordered"), f"orders[{index}].ordered", positive=True)
        key = (order_id, sku)
        if key in order_keys:
            fail(f"duplicate order line: {order_id}/{sku}")
        order_keys.add(key)
        order_ids.add(order_id)
        orders.append({
            "order_id": order_id,
            "sku": sku,
            "ordered": ordered,
            "supplier_contact": item.get("supplier_contact"),
        })

    events: list[dict[str, Any]] = []
    for index, raw in enumerate(require_list(root["events"], "events")):
        item = require_object(raw, f"events[{index}]")
        event = {
            "event_id": require_string(item.get("event_id"), f"events[{index}].event_id"),
            "order_id": require_string(item.get("order_id"), f"events[{index}].order_id"),
            "sku": require_string(item.get("sku"), f"events[{index}].sku"),
            "event_month": require_month(item.get("event_month"), f"events[{index}].event_month"),
            "quantity": require_int(item.get("quantity"), f"events[{index}].quantity"),
        }
        events.append(event)

    coverage: list[dict[str, Any]] = []
    for index, raw in enumerate(require_list(root["coverage"], "coverage")):
        item = require_object(raw, f"coverage[{index}]")
        complete = item.get("complete")
        if not isinstance(complete, bool):
            fail(f"coverage[{index}].complete must be boolean")
        coverage.append({
            "order_id": require_string(item.get("order_id"), f"coverage[{index}].order_id"),
            "sku": require_string(item.get("sku"), f"coverage[{index}].sku"),
            "month": require_month(item.get("month"), f"coverage[{index}].month"),
            "complete": complete,
        })

    responsibilities = require_object(root["responsibilities"], "responsibilities")
    return month, orders, events, coverage, responsibilities


def recipient(responsibilities: dict[str, Any], role: str) -> str | None:
    value = responsibilities.get(role)
    return value.strip() if isinstance(value, str) and value.strip() else None


def draft_for(line: dict[str, Any], status: str, responsibilities: dict[str, Any], month: str) -> dict[str, Any] | None:
    oid, sku = line["order_id"], line["sku"]
    amount = line.get("remaining_or_surplus")
    if status == "shortfall":
        contact = line.get("supplier_contact")
        draft = (f"Please confirm and arrange receipt of {amount} remaining unit(s) for "
                 f"order {oid}, SKU {sku}, for {month}.")
        return {"action": "draft_only", "recipient": contact if isinstance(contact, str) and contact.strip() else None,
                "recipient_source": "orders[].supplier_contact", "draft": draft}
    if status == "excess":
        lead = recipient(responsibilities, "warehouse_lead")
        draft = (f"Please reconcile the {amount} surplus unit(s) for order {oid}, SKU {sku}, "
                 f"against the order and receiving evidence for {month}.")
        return {"action": "draft_only", "recipient": lead, "recipient_role": "warehouse_lead", "draft": draft}
    if status in {"incomplete_export", "coverage_missing", "coverage_conflict"}:
        steward = recipient(responsibilities, "data_steward")
        draft = (f"Please provide or confirm the full receiving export and coverage evidence for "
                 f"order {oid}, SKU {sku}, for {month}; the current evidence supports only an observed subtotal.")
        return {"action": "draft_only", "recipient": steward, "recipient_role": "data_steward", "draft": draft}
    if status in {"identity_reconciliation_required", "conflicting_evidence"}:
        coordinator = recipient(responsibilities, "purchasing_coordinator")
        steward = recipient(responsibilities, "data_steward")
        draft = (f"Please reconcile the identified order/event source records for order {oid}, SKU {sku}, "
                 f"before finalizing the {month} receipt position.")
        return {"action": "draft_only", "recipients": [coordinator, steward],
                "recipient_roles": ["purchasing_coordinator", "data_steward"], "draft": draft}
    return None


def review(data: Any) -> dict[str, Any]:
    month, orders, events, coverage, responsibilities = normalize(data)
    lines_by_key = {(o["order_id"], o["sku"]): o for o in orders}

    # Collapse exact duplicate event rows, while retaining all content variants for conflict reporting.
    by_event_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        if event not in by_event_id[event["event_id"]]:
            by_event_id[event["event_id"]].append(event)
    conflicting_ids = {eid for eid, variants in by_event_id.items() if len(variants) > 1}
    conflict_keys: dict[tuple[str, str], list[str]] = defaultdict(list)
    for eid in conflicting_ids:
        for event in by_event_id[eid]:
            key = (event["order_id"], event["sku"])
            if key in lines_by_key and eid not in conflict_keys[key]:
                conflict_keys[key].append(eid)

    # Coverage is keyed to the requested month. Conflicting declarations are an evidence issue.
    coverage_values: dict[tuple[str, str], set[bool]] = defaultdict(set)
    for item in coverage:
        if item["month"] == month:
            coverage_values[(item["order_id"], item["sku"])].add(item["complete"])

    observed: dict[tuple[str, str], int] = defaultdict(int)
    used_event_ids: dict[tuple[str, str], list[str]] = defaultdict(list)
    ignored_ids: set[str] = set()
    identity_keys: set[tuple[str, str]] = set()
    identity_orders: set[str] = set()
    for eid, variants in by_event_id.items():
        for event in variants:
            key = (event["order_id"], event["sku"])
            if event["event_month"] != month:
                continue
            if event["order_id"] not in {o["order_id"] for o in orders}:
                ignored_ids.add(eid)
                continue
            if key not in lines_by_key:
                identity_keys.add(key)
                identity_orders.add(event["order_id"])
                continue
            if eid in conflicting_ids:
                continue
            if eid not in used_event_ids[key]:
                observed[key] += event["quantity"]
                used_event_ids[key].append(eid)

    global_issues: list[dict[str, Any]] = []
    for key in sorted(identity_keys):
        global_issues.append({"type": "order_sku_not_in_supplied_orders", "order_id": key[0], "sku": key[1]})
    for key in sorted(set(coverage_values) - set(lines_by_key)):
        global_issues.append({"type": "coverage_for_out_of_scope_line", "order_id": key[0], "sku": key[1], "month": month})

    scope_lines: list[dict[str, Any]] = []
    for order in orders:
        key = (order["order_id"], order["sku"])
        values = coverage_values.get(key, set())
        issues: list[dict[str, Any]] = []
        status = "pending"
        final_received: int | None = None
        remaining: int | None = None
        if key in conflict_keys:
            issues.append({"type": "conflicting_event_id", "event_ids": sorted(conflict_keys[key])})
            status = "conflicting_evidence"
        if order["order_id"] in identity_orders:
            issues.append({"type": "order_has_current_month_event_for_absent_sku"})
            if status == "pending":
                status = "identity_reconciliation_required"
        if len(values) > 1:
            issues.append({"type": "conflicting_coverage_declarations", "values": sorted(values)})
            if status == "pending":
                status = "coverage_conflict"
        elif not values:
            issues.append({"type": "missing_coverage_declaration"})
            if status == "pending":
                status = "coverage_missing"
        elif values == {False}:
            issues.append({"type": "receiving_export_incomplete"})
            if status == "pending":
                status = "incomplete_export"
        else:
            # Only a clean complete declaration permits a final comparison.
            if status == "pending":
                final_received = observed[key]
                if final_received == order["ordered"]:
                    status = "received_as_ordered"
                elif final_received < order["ordered"]:
                    status = "shortfall"
                    remaining = order["ordered"] - final_received
                else:
                    status = "excess"
                    remaining = final_received - order["ordered"]
        line = {
            "order_id": order["order_id"], "sku": order["sku"], "ordered": order["ordered"],
            "supplier_contact": order.get("supplier_contact"), "observed_received": observed[key],
            "event_ids": sorted(used_event_ids[key]),
            "coverage": {"month": month, "complete": True} if values == {True} else ({"month": month, "complete": False} if values == {False} else None),
            "issues": issues, "status": status,
        }
        if final_received is not None:
            line["final_received"] = final_received
        if remaining is not None:
            line["remaining_or_surplus"] = remaining
        follow_up = draft_for(line, status, responsibilities, month)
        if follow_up is not None:
            line["follow_up"] = follow_up
        scope_lines.append(line)

    counts: dict[str, int] = defaultdict(int)
    for line in scope_lines:
        counts[line["status"]] += 1
    return {
        "month": month,
        "scope_lines": scope_lines,
        "ignored_out_of_scope_event_ids": sorted(ignored_ids),
        "global_issues": global_issues,
        "summary": {"line_count": len(scope_lines), "status_counts": dict(sorted(counts.items())),
                     "conflicting_event_ids": sorted(conflicting_ids)},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Calculate a monthly receiving review from JSON input.")
    parser.add_argument("input", metavar="INPUT.json", help="path to the receiving-review input JSON")
    parser.add_argument("--output", "-o", metavar="REPORT.json", help="write report JSON to this path (default: stdout)")
    parser.add_argument("--pretty", action="store_true", help="indent report JSON for readability")
    args = parser.parse_args(argv)
    try:
        raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = review(raw)
        rendered = json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True) + "\n"
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 0
    except (OSError, json.JSONDecodeError, InputError) as exc:
        print(f"review_receipts: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
