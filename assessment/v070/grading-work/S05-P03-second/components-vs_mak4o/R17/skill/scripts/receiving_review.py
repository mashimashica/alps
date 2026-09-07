#!/usr/bin/env python3
"""Build an evidence-aware monthly purchase-order receiving review from JSON."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


class InputError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InputError(message)


def nonempty_string(value: Any, path: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{path} must be a non-empty string")
    return value


def validate(data: Any) -> None:
    require(isinstance(data, dict), "input must be a JSON object")
    for key in ("month", "orders", "events", "coverage", "responsibilities"):
        require(key in data, f"missing required field: {key}")
    require(isinstance(data["month"], str) and MONTH_RE.fullmatch(data["month"]) is not None,
            "month must use YYYY-MM")
    for key in ("orders", "events", "coverage"):
        require(isinstance(data[key], list), f"{key} must be an array")
    require(isinstance(data["responsibilities"], dict), "responsibilities must be an object")

    order_keys: set[tuple[str, str]] = set()
    for i, row in enumerate(data["orders"]):
        require(isinstance(row, dict), f"orders[{i}] must be an object")
        oid = nonempty_string(row.get("order_id"), f"orders[{i}].order_id")
        sku = nonempty_string(row.get("sku"), f"orders[{i}].sku")
        require(type(row.get("ordered")) is int and row["ordered"] > 0,
                f"orders[{i}].ordered must be a positive integer")
        require((oid, sku) not in order_keys, f"duplicate order line: {oid}/{sku}")
        order_keys.add((oid, sku))
        if "supplier_contact" in row and row["supplier_contact"] is not None:
            nonempty_string(row["supplier_contact"], f"orders[{i}].supplier_contact")

    for i, row in enumerate(data["events"]):
        require(isinstance(row, dict), f"events[{i}] must be an object")
        for key in ("event_id", "order_id", "sku"):
            nonempty_string(row.get(key), f"events[{i}].{key}")
        require(isinstance(row.get("event_month"), str) and MONTH_RE.fullmatch(row["event_month"]) is not None,
                f"events[{i}].event_month must use YYYY-MM")
        require(type(row.get("quantity")) is int, f"events[{i}].quantity must be an integer")

    for i, row in enumerate(data["coverage"]):
        require(isinstance(row, dict), f"coverage[{i}] must be an object")
        for key in ("order_id", "sku"):
            nonempty_string(row.get(key), f"coverage[{i}].{key}")
        require(isinstance(row.get("month"), str) and MONTH_RE.fullmatch(row["month"]) is not None,
                f"coverage[{i}].month must use YYYY-MM")
        require(type(row.get("complete")) is bool, f"coverage[{i}].complete must be boolean")


def recipient(responsibilities: dict[str, Any], role: str) -> tuple[str | None, bool]:
    value = responsibilities.get(role)
    return (value, True) if isinstance(value, str) and value.strip() else (None, False)


def followup(kind: str, order: dict[str, Any], month: str, responsibilities: dict[str, Any],
             observed: int | None = None, amount: int | None = None) -> dict[str, Any]:
    oid, sku = order["order_id"], order["sku"]
    pc, pc_ok = recipient(responsibilities, "purchasing_coordinator")
    ds, ds_ok = recipient(responsibilities, "data_steward")
    wl, wl_ok = recipient(responsibilities, "warehouse_lead")
    if kind == "identity_reconciliation":
        roles, recipients = ["purchasing_coordinator", "data_steward"], [pc, ds]
        action = f"Reconcile order and event identity for {oid}/{sku}, correct or confirm the source records, then rerun the {month} comparison."
        available = pc_ok and ds_ok
    elif kind == "complete_export":
        roles, recipients = ["data_steward"], [ds]
        action = f"Provide or confirm the complete {month} event export for {oid}/{sku}, then rerun the final comparison."
        available = ds_ok
    elif kind == "remaining_receipt":
        contact = order.get("supplier_contact")
        roles, recipients = ["purchasing_coordinator", "supplier_contact"], [pc, contact]
        action = f"Follow up on the remaining {amount} units for {oid}/{sku} with the supplied supplier contact and confirm the expected receipt disposition."
        available = pc_ok and isinstance(contact, str) and bool(contact.strip())
    else:
        roles, recipients = ["warehouse_lead"], [wl]
        action = f"Reconcile the {amount}-unit surplus for {oid}/{sku} against the order and receiving evidence."
        available = wl_ok
    shown = [r if isinstance(r, str) and r.strip() else "[recipient missing]" for r in recipients]
    return {"kind": kind, "recipient_roles": roles, "recipients": shown,
            "recipient_information_complete": available, "next_action": action,
            "draft": f"To: {'; '.join(shown)}\nSubject: {month} receiving review — {oid}/{sku}\nAction requested: {action}",
            "send_status": "draft_not_sent"}


def build_review(data: dict[str, Any]) -> dict[str, Any]:
    month = data["month"]
    orders = data["orders"]
    order_by_key = {(o["order_id"], o["sku"]): o for o in orders}
    order_ids = {o["order_id"] for o in orders}
    skus_by_order: dict[str, set[str]] = defaultdict(set)
    for oid, sku in order_by_key:
        skus_by_order[oid].add(sku)

    event_variants: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    exact_duplicates = 0
    for event in data["events"]:
        signature = json.dumps(event, sort_keys=True, separators=(",", ":"))
        if signature in event_variants[event["event_id"]]:
            exact_duplicates += 1
        event_variants[event["event_id"]][signature] = event
    conflicts = {eid: list(variants.values()) for eid, variants in event_variants.items() if len(variants) > 1}
    unique_events = [next(iter(v.values())) for eid, v in event_variants.items() if eid not in conflicts]

    conflict_orders: set[str] = set()
    conflict_keys: set[tuple[str, str]] = set()
    for variants in conflicts.values():
        for event in variants:
            if event["event_month"] == month and event["order_id"] in order_ids:
                key = (event["order_id"], event["sku"])
                if key in order_by_key:
                    conflict_keys.add(key)
                else:
                    conflict_orders.add(event["order_id"])

    identity_orders: set[str] = set()
    outside_events: list[str] = []
    totals: dict[tuple[str, str], int] = defaultdict(int)
    counted_ids: dict[tuple[str, str], list[str]] = defaultdict(list)
    for event in unique_events:
        if event["event_month"] != month:
            continue
        if event["order_id"] not in order_ids:
            outside_events.append(event["event_id"])
            continue
        if event["sku"] not in skus_by_order[event["order_id"]]:
            identity_orders.add(event["order_id"])
            continue
        key = (event["order_id"], event["sku"])
        totals[key] += event["quantity"]
        counted_ids[key].append(event["event_id"])

    coverage_values: dict[tuple[str, str], list[bool]] = defaultdict(list)
    for row in data["coverage"]:
        key = (row["order_id"], row["sku"])
        if row["month"] == month and key in order_by_key:
            coverage_values[key].append(row["complete"])

    results = []
    for order in orders:
        key = (order["order_id"], order["sku"])
        observed = totals[key]
        reasons: list[str] = []
        if order["order_id"] in identity_orders or order["order_id"] in conflict_orders or key in conflict_keys:
            evidence, position = "conflicting_identity", "undetermined"
            reasons.append("Order/event identity must be reconciled before final comparison.")
            actions = [followup("identity_reconciliation", order, month, data["responsibilities"], observed)]
        else:
            declarations = coverage_values.get(key, [])
            if not declarations:
                evidence, position = "coverage_missing", "undetermined"
                reasons.append("No applicable completeness declaration was supplied; observed quantity is provisional.")
                actions = [followup("complete_export", order, month, data["responsibilities"], observed)]
            elif len(set(declarations)) > 1:
                evidence, position = "coverage_conflicting", "undetermined"
                reasons.append("Completeness declarations conflict; observed quantity is provisional.")
                actions = [followup("complete_export", order, month, data["responsibilities"], observed)]
            elif declarations[0] is False:
                evidence, position = "export_incomplete", "undetermined"
                reasons.append("Export is declared incomplete; observed quantity is a subtotal, not a final position.")
                actions = [followup("complete_export", order, month, data["responsibilities"], observed)]
            else:
                evidence = "complete_valid"
                delta = observed - order["ordered"]
                if delta == 0:
                    position, actions = "received_as_ordered", []
                elif delta < 0:
                    position = "shortfall"
                    actions = [followup("remaining_receipt", order, month, data["responsibilities"], observed, -delta)]
                else:
                    position = "excess"
                    actions = [followup("surplus_reconciliation", order, month, data["responsibilities"], observed, delta)]
        if any(not a["recipient_information_complete"] for a in actions):
            reasons.append("Required recipient information is missing; the role remains responsible but the draft cannot be fully addressed.")
        results.append({"order_id": key[0], "sku": key[1], "ordered_quantity": order["ordered"],
                        "observed_net_received": observed, "observed_quantity_label":
                        "final_net" if evidence == "complete_valid" else "provisional_subtotal",
                        "counted_event_ids": counted_ids[key], "evidence_condition": evidence,
                        "receipt_position": position, "judgment_notes": reasons, "follow_ups": actions})

    return {"month": month, "scope": {"order_line_count": len(orders),
            "reviewed_line_count": len(results)}, "source_checks": {
            "input_event_rows": len(data["events"]), "exact_duplicate_rows_ignored": exact_duplicates,
            "conflicting_event_ids": sorted(conflicts), "outside_order_event_ids_excluded": sorted(outside_events),
            "identity_reconciliation_order_ids": sorted(identity_orders | conflict_orders)},
            "issues": [f"event_id {eid} has conflicting content" for eid in sorted(conflicts)],
            "lines": results}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 JSON input file")
    parser.add_argument("--output", type=Path, help="write JSON here; defaults to stdout")
    args = parser.parse_args(argv)
    try:
        with args.input.open(encoding="utf-8") as handle:
            data = json.load(handle)
        validate(data)
        result = build_review(data)
        encoded = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(encoded, encoding="utf-8")
        else:
            sys.stdout.write(encoded)
        return 0
    except (OSError, json.JSONDecodeError, InputError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

