#!/usr/bin/env python3
"""Produce a deterministic monthly receiving evidence review from JSON."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

MONTH = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
ROLES = ("purchasing_coordinator", "warehouse_lead", "data_steward")


class ContractError(ValueError):
    pass


def nonempty(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{path} must be a non-empty string")
    return value


def array(data: dict[str, Any], key: str) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list):
        raise ContractError(f"{key} must be an array")
    return value


def obj(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{path} must be an object")
    return value


def load_contract(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON input: {exc}") from exc
    return obj(data, "input")


def validate(data: dict[str, Any]) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, str]]:
    month = nonempty(data.get("month"), "month")
    if not MONTH.fullmatch(month):
        raise ContractError("month must use YYYY-MM")

    orders, seen = [], set()
    for i, raw in enumerate(array(data, "orders")):
        row = obj(raw, f"orders[{i}]")
        oid = nonempty(row.get("order_id"), f"orders[{i}].order_id")
        sku = nonempty(row.get("sku"), f"orders[{i}].sku")
        ordered = row.get("ordered")
        if isinstance(ordered, bool) or not isinstance(ordered, int) or ordered <= 0:
            raise ContractError(f"orders[{i}].ordered must be a positive integer")
        contact = nonempty(row.get("supplier_contact"), f"orders[{i}].supplier_contact")
        if (oid, sku) in seen:
            raise ContractError(f"duplicate order line: {oid}/{sku}")
        seen.add((oid, sku))
        orders.append({"order_id": oid, "sku": sku, "ordered": ordered, "supplier_contact": contact})

    events = []
    for i, raw in enumerate(array(data, "events")):
        row = obj(raw, f"events[{i}]")
        normalized = {k: nonempty(row.get(k), f"events[{i}].{k}") for k in ("event_id", "order_id", "sku", "event_month")}
        if not MONTH.fullmatch(normalized["event_month"]):
            raise ContractError(f"events[{i}].event_month must use YYYY-MM")
        quantity = row.get("quantity")
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise ContractError(f"events[{i}].quantity must be an integer")
        normalized["quantity"] = quantity
        events.append(normalized)

    coverage = []
    for i, raw in enumerate(array(data, "coverage")):
        row = obj(raw, f"coverage[{i}]")
        normalized = {k: nonempty(row.get(k), f"coverage[{i}].{k}") for k in ("order_id", "sku", "month")}
        if not MONTH.fullmatch(normalized["month"]):
            raise ContractError(f"coverage[{i}].month must use YYYY-MM")
        if not isinstance(row.get("complete"), bool):
            raise ContractError(f"coverage[{i}].complete must be Boolean")
        normalized["complete"] = row["complete"]
        coverage.append(normalized)

    raw_roles = obj(data.get("responsibilities"), "responsibilities")
    roles = {role: nonempty(raw_roles.get(role), f"responsibilities.{role}") for role in ROLES}
    return month, orders, events, coverage, roles


def followup(owner: str | list[str], recipient: str | list[str], action: str, draft: str, kind: str) -> dict[str, Any]:
    return {"type": kind, "owner": owner, "recipient": recipient, "action": action, "draft": draft}


def review(data: dict[str, Any]) -> dict[str, Any]:
    month, orders, events, coverage, roles = validate(data)
    order_keys = {(r["order_id"], r["sku"]) for r in orders}
    order_ids = {r["order_id"] for r in orders}
    scope_issues: list[dict[str, Any]] = []

    # Exact copies count once. Any event_id with distinct records is conflicting.
    unique_events = list({(e["event_id"], e["order_id"], e["sku"], e["event_month"], e["quantity"]): e for e in events}.values())
    by_event_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in unique_events:
        by_event_id[event["event_id"]].append(event)
    conflicts = {eid: rows for eid, rows in by_event_id.items() if len(rows) > 1}

    conflict_keys: dict[tuple[str, str], set[str]] = defaultdict(set)
    conflict_orders: dict[str, set[str]] = defaultdict(set)
    for eid, variants in conflicts.items():
        for event in variants:
            if event["event_month"] != month:
                continue
            key = (event["order_id"], event["sku"])
            if key in order_keys:
                conflict_keys[key].add(eid)
            elif event["order_id"] in order_ids:
                conflict_orders[event["order_id"]].add(eid)

    current_valid = [e for e in unique_events if e["event_month"] == month and e["event_id"] not in conflicts]
    identity_orders: dict[str, list[str]] = defaultdict(list)
    outside = []
    totals: Counter[tuple[str, str]] = Counter()
    for event in current_valid:
        key = (event["order_id"], event["sku"])
        if event["order_id"] not in order_ids:
            outside.append(event["event_id"])
        elif key not in order_keys:
            identity_orders[event["order_id"]].append(event["event_id"])
        else:
            totals[key] += event["quantity"]

    coverage_values: dict[tuple[str, str], list[bool]] = defaultdict(list)
    for row in coverage:
        key = (row["order_id"], row["sku"])
        if row["month"] == month and key in order_keys:
            coverage_values[key].append(row["complete"])
        elif row["month"] == month:
            scope_issues.append({"type": "extra_coverage", "order_id": row["order_id"], "sku": row["sku"], "effect": "does not expand review scope"})

    lines = []
    for order in orders:
        oid, sku = order["order_id"], order["sku"]
        key = (oid, sku)
        issues, drafts = [], []
        values = coverage_values.get(key, [])
        complete = len(values) > 0 and all(values) and len(set(values)) == 1
        if not values:
            issues.append("No coverage declaration exists for this line and requested month.")
        elif len(set(values)) > 1:
            issues.append("Coverage declarations conflict for this line and requested month.")
        elif not values[0]:
            issues.append("The event export is declared incomplete for this line and requested month.")
        if conflict_keys.get(key):
            issues.append("Conflicting content shares event_id(s): " + ", ".join(sorted(conflict_keys[key])) + ".")
        order_conflicts = sorted(set(identity_orders.get(oid, [])) | conflict_orders.get(oid, set()))
        if order_conflicts:
            issues.append("Current-month event identity must be reconciled for this order; event_id(s): " + ", ".join(order_conflicts) + ".")

        if order_conflicts or conflict_keys.get(key):
            owners = [roles["purchasing_coordinator"], roles["data_steward"]]
            action = f"Reconcile order/SKU or conflicting event source records for {oid}/{sku} before final comparison."
            drafts.append(followup(owners, owners, action, f"Please reconcile the identified source records affecting {oid}/{sku} for {month}. A final receipt position is blocked until the event identity/content is confirmed.", "identity_reconciliation"))
        elif not complete:
            action = f"Provide or confirm the complete {month} event export for {oid}/{sku}, then rerun the comparison."
            drafts.append(followup(roles["data_steward"], roles["data_steward"], action, f"Please provide or confirm the complete receiving-event export for {oid}/{sku} for {month}. The observed subtotal is {totals[key]}, but the final receipt position cannot yet be determined.", "complete_export"))

        blocked = bool(issues)
        disposition, variance = "indeterminate", None
        if not blocked:
            variance = totals[key] - order["ordered"]
            if variance == 0:
                disposition = "received_as_ordered"
            elif variance < 0:
                disposition = "shortfall"
                remaining = -variance
                action = f"Ask {order['supplier_contact']} to follow up the remaining {remaining} units for {oid}/{sku}."
                drafts.append(followup(roles["purchasing_coordinator"], order["supplier_contact"], action, f"Please confirm the plan for the remaining {remaining} units of {oid}/{sku} for {month}. The order quantity is {order['ordered']} and confirmed net received is {totals[key]}.", "remaining_receipt"))
            else:
                disposition = "excess"
                action = f"Reconcile the surplus {variance} units for {oid}/{sku} against the order and receiving evidence."
                drafts.append(followup(roles["warehouse_lead"], roles["warehouse_lead"], action, f"Please reconcile the {variance}-unit surplus for {oid}/{sku} for {month} against the purchase order and receiving evidence. Ordered: {order['ordered']}; confirmed net received: {totals[key]}.", "surplus_reconciliation"))

        lines.append({"order_id": oid, "sku": sku, "ordered": order["ordered"], "observed_net_received": totals[key], "coverage_complete": complete, "final_comparison_allowed": not blocked, "disposition": disposition, "variance_received_minus_ordered": variance, "evidence_issues": issues, "follow_ups": drafts})

    counts = Counter(line["disposition"] for line in lines)
    return {"month": month, "summary": {"line_count": len(lines), "dispositions": dict(sorted(counts.items())), "unresolved_line_count": sum(bool(x["follow_ups"]) for x in lines)}, "scope_issues": scope_issues, "outside_scope_events": sorted(set(outside)), "lines": lines}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 JSON input file")
    parser.add_argument("--output", type=Path, help="write review JSON here (default: stdout)")
    args = parser.parse_args()
    try:
        result = review(load_contract(args.input))
        rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 0
    except (ContractError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
