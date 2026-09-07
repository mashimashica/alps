#!/usr/bin/env python3
"""Analyze monthly purchase-order receipt evidence from a JSON input."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


MONTH_RE = re.compile(r"^(?:[0-9]{4})-(?:0[1-9]|1[0-2])$")
ROLES = ("purchasing_coordinator", "warehouse_lead", "data_steward")


class ContractError(ValueError):
    """A fatal root-level input contract error."""


def is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def diagnostic(code: str, message: str, *, severity: str = "error", **context: Any) -> dict[str, Any]:
    item = {"code": code, "severity": severity, "message": message}
    item.update(context)
    return item


def require_root(data: Any) -> tuple[str, list[Any], list[Any], list[Any], dict[str, Any]]:
    if not isinstance(data, dict):
        raise ContractError("input root must be a JSON object")
    month = data.get("month")
    if not isinstance(month, str) or not MONTH_RE.fullmatch(month):
        raise ContractError("month must be a valid YYYY-MM string")
    for field in ("orders", "events", "coverage"):
        if not isinstance(data.get(field), list):
            raise ContractError(f"{field} must be a JSON array")
    responsibilities = data.get("responsibilities")
    if not isinstance(responsibilities, dict):
        raise ContractError("responsibilities must be a JSON object")
    return month, data["orders"], data["events"], data["coverage"], responsibilities


def clean_responsibilities(raw: dict[str, Any], diagnostics: list[dict[str, Any]]) -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    for role in ROLES:
        value = raw.get(role)
        if nonempty_string(value):
            result[role] = value.strip()
        else:
            result[role] = None
            diagnostics.append(diagnostic(
                "missing_responsibility",
                f"No usable recipient was supplied for {role}.",
                severity="warning",
                role=role,
            ))
    return result


def normalize_orders(raw_orders: list[Any], diagnostics: list[dict[str, Any]]) -> tuple[dict[tuple[str, str], dict[str, Any]], int]:
    variants: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    usable_rows = 0
    for index, raw in enumerate(raw_orders):
        if not isinstance(raw, dict):
            diagnostics.append(diagnostic("invalid_order_row", "Order row must be an object.", row=index))
            continue
        order_id, sku = raw.get("order_id"), raw.get("sku")
        if not nonempty_string(order_id) or not nonempty_string(sku):
            diagnostics.append(diagnostic(
                "invalid_order_identity",
                "Order row needs nonempty order_id and sku and cannot define an in-scope line without them.",
                row=index,
            ))
            continue
        key = (order_id.strip(), sku.strip())
        ordered = raw.get("ordered")
        supplier = raw.get("supplier_contact")
        normalized = {
            "order_id": key[0],
            "sku": key[1],
            "ordered": ordered if is_int(ordered) and ordered > 0 else None,
            "supplier_contact": supplier.strip() if nonempty_string(supplier) else None,
        }
        usable_rows += 1
        if normalized["ordered"] is None:
            diagnostics.append(diagnostic(
                "invalid_order_quantity",
                "Order quantity must be a positive integer; final comparison is blocked for this line.",
                row=index,
                order_id=key[0],
                sku=key[1],
            ))
        if normalized["supplier_contact"] is None:
            diagnostics.append(diagnostic(
                "missing_supplier_contact",
                "No usable supplier contact was supplied; a shortfall recipient cannot be completed.",
                severity="warning",
                row=index,
                order_id=key[0],
                sku=key[1],
            ))
        variants[key].append(normalized)

    orders: dict[tuple[str, str], dict[str, Any]] = {}
    for key, rows in variants.items():
        unique = {(row["ordered"], row["supplier_contact"]) for row in rows}
        if len(unique) == 1:
            orders[key] = {**rows[0], "order_conflict": False, "exact_duplicate_rows": len(rows) - 1}
            if len(rows) > 1:
                diagnostics.append(diagnostic(
                    "duplicate_order_row",
                    "Exact repeated order rows were collapsed to one in-scope line.",
                    severity="warning",
                    order_id=key[0],
                    sku=key[1],
                    ignored_rows=len(rows) - 1,
                ))
        else:
            orders[key] = {
                "order_id": key[0],
                "sku": key[1],
                "ordered": None,
                "supplier_contact": None,
                "order_conflict": True,
                "exact_duplicate_rows": 0,
            }
            diagnostics.append(diagnostic(
                "conflicting_order_rows",
                "Different order content was supplied for the same order_id and sku; final comparison is blocked.",
                order_id=key[0],
                sku=key[1],
                variants=len(unique),
            ))
    return orders, usable_rows


def normalize_coverage(
    raw_coverage: list[Any],
    month: str,
    orders: dict[tuple[str, str], dict[str, Any]],
    diagnostics: list[dict[str, Any]],
) -> dict[tuple[str, str], str]:
    values: dict[tuple[str, str], list[bool]] = defaultdict(list)
    for index, raw in enumerate(raw_coverage):
        if not isinstance(raw, dict):
            diagnostics.append(diagnostic("invalid_coverage_row", "Coverage row must be an object.", row=index))
            continue
        order_id, sku, row_month, complete = raw.get("order_id"), raw.get("sku"), raw.get("month"), raw.get("complete")
        if not nonempty_string(order_id) or not nonempty_string(sku) or not isinstance(row_month, str) or not isinstance(complete, bool):
            diagnostics.append(diagnostic(
                "invalid_coverage_row",
                "Coverage needs nonempty order_id and sku, a month string, and a boolean complete value.",
                row=index,
            ))
            continue
        key = (order_id.strip(), sku.strip())
        if row_month != month:
            diagnostics.append(diagnostic(
                "coverage_outside_month",
                "Coverage declaration is for a different month and does not establish requested-month completeness.",
                severity="warning",
                row=index,
                order_id=key[0],
                sku=key[1],
                month=row_month,
            ))
            continue
        if key not in orders:
            diagnostics.append(diagnostic(
                "coverage_outside_scope",
                "Coverage declaration does not match a supplied usable order line.",
                severity="warning",
                row=index,
                order_id=key[0],
                sku=key[1],
            ))
            continue
        values[key].append(complete)

    states: dict[tuple[str, str], str] = {}
    for key in orders:
        declared = values.get(key, [])
        distinct = set(declared)
        if not declared:
            states[key] = "missing"
            diagnostics.append(diagnostic(
                "missing_coverage",
                "No valid requested-month coverage declaration was supplied; final comparison is blocked.",
                order_id=key[0],
                sku=key[1],
            ))
        elif len(distinct) > 1:
            states[key] = "conflicting"
            diagnostics.append(diagnostic(
                "conflicting_coverage",
                "Coverage declarations disagree; final comparison is blocked.",
                order_id=key[0],
                sku=key[1],
            ))
        else:
            states[key] = "complete" if declared[0] else "incomplete"
            if len(declared) > 1:
                diagnostics.append(diagnostic(
                    "duplicate_coverage_row",
                    "Exact repeated coverage declarations were collapsed.",
                    severity="warning",
                    order_id=key[0],
                    sku=key[1],
                    ignored_rows=len(declared) - 1,
                ))
    return states


def normalize_events(
    raw_events: list[Any],
    month: str,
    orders: dict[tuple[str, str], dict[str, Any]],
    diagnostics: list[dict[str, Any]],
) -> tuple[dict[tuple[str, str], list[dict[str, Any]]], dict[tuple[str, str], int], set[tuple[str, str]], dict[str, Any]]:
    event_variants: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    invalid_rows = 0
    order_ids = {key[0] for key in orders}
    lines_by_order: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for key in orders:
        lines_by_order[key[0]].add(key)
    blocked_lines: set[tuple[str, str]] = set()

    for index, raw in enumerate(raw_events):
        if not isinstance(raw, dict):
            diagnostics.append(diagnostic("invalid_event_row", "Event row must be an object.", row=index))
            invalid_rows += 1
            continue
        event_id = raw.get("event_id")
        if not nonempty_string(event_id):
            affected: set[tuple[str, str]] = set()
            order_id = raw.get("order_id").strip() if nonempty_string(raw.get("order_id")) else None
            sku = raw.get("sku").strip() if nonempty_string(raw.get("sku")) else None
            row_month = raw.get("event_month")
            month_may_affect_review = row_month == month or not (
                isinstance(row_month, str) and MONTH_RE.fullmatch(row_month)
            )
            if month_may_affect_review and order_id in order_ids:
                key = (order_id, sku)
                affected = {key} if key in orders else set(lines_by_order[order_id])
                blocked_lines.update(affected)
            diagnostics.append(diagnostic(
                "invalid_event_id",
                "Event row needs a nonempty event_id; any identifiable requested-month lines are blocked because deduplication cannot be verified.",
                row=index,
                affected_lines=[{"order_id": key[0], "sku": key[1]} for key in sorted(affected)],
            ))
            invalid_rows += 1
            continue
        normalized = {
            "event_id": event_id.strip(),
            "order_id": raw.get("order_id").strip() if nonempty_string(raw.get("order_id")) else None,
            "sku": raw.get("sku").strip() if nonempty_string(raw.get("sku")) else None,
            "event_month": raw.get("event_month"),
            "quantity": raw.get("quantity") if is_int(raw.get("quantity")) else None,
        }
        event_variants[normalized["event_id"]].append((index, normalized))

    counted: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    duplicate_counts: dict[tuple[str, str], int] = defaultdict(int)
    outside_month: list[str] = []
    outside_scope: list[str] = []
    conflict_ids: list[str] = []

    for event_id, indexed_rows in event_variants.items():
        rows = [row for _, row in indexed_rows]
        signatures = {(r["order_id"], r["sku"], r["event_month"], r["quantity"]) for r in rows}
        if len(signatures) > 1:
            conflict_ids.append(event_id)
            affected: set[tuple[str, str]] = set()
            for row in rows:
                if row["event_month"] != month or row["order_id"] not in order_ids:
                    continue
                key = (row["order_id"], row["sku"])
                if key in orders:
                    affected.add(key)
                else:
                    affected.update(lines_by_order[row["order_id"]])
            blocked_lines.update(affected)
            diagnostics.append(diagnostic(
                "conflicting_event_id",
                "The same event_id has different content; all variants were excluded and affected lines require source reconciliation.",
                event_id=event_id,
                rows=[index for index, _ in indexed_rows],
                affected_lines=[{"order_id": key[0], "sku": key[1]} for key in sorted(affected)],
            ))
            continue

        row = rows[0]
        repeats = len(rows) - 1
        if not isinstance(row["event_month"], str) or not MONTH_RE.fullmatch(row["event_month"]):
            affected: set[tuple[str, str]] = set()
            if row["order_id"] in order_ids:
                key = (row["order_id"], row["sku"])
                affected = {key} if key in orders else set(lines_by_order[row["order_id"]])
                blocked_lines.update(affected)
            diagnostics.append(diagnostic(
                "invalid_event_month",
                "Event month is missing or invalid; identifiable in-scope lines are blocked because month inclusion cannot be determined.",
                event_id=event_id,
                rows=[index for index, _ in indexed_rows],
                affected_lines=[{"order_id": key[0], "sku": key[1]} for key in sorted(affected)],
            ))
            continue
        if row["event_month"] != month:
            outside_month.append(event_id)
            continue
        if row["order_id"] not in order_ids:
            outside_scope.append(event_id)
            continue
        key = (row["order_id"], row["sku"])
        if key not in orders:
            affected = lines_by_order[row["order_id"]]
            blocked_lines.update(affected)
            diagnostics.append(diagnostic(
                "unknown_sku_for_in_scope_order",
                "Requested-month event names an in-scope order but a SKU absent from that order; all lines on the order require identity reconciliation.",
                event_id=event_id,
                order_id=row["order_id"],
                sku=row["sku"],
                affected_lines=[{"order_id": item[0], "sku": item[1]} for item in sorted(affected)],
            ))
            continue
        if row["sku"] is None or row["quantity"] is None:
            blocked_lines.add(key)
            diagnostics.append(diagnostic(
                "invalid_in_scope_event",
                "Requested-month in-scope event has invalid identity, month, or signed integer quantity; final comparison is blocked.",
                event_id=event_id,
                rows=[index for index, _ in indexed_rows],
                order_id=key[0],
                sku=key[1],
            ))
            continue
        counted[key].append(row)
        if repeats:
            duplicate_counts[key] += repeats
            diagnostics.append(diagnostic(
                "duplicate_event_row",
                "Exact repeated event copies count once.",
                severity="warning",
                event_id=event_id,
                order_id=key[0],
                sku=key[1],
                ignored_rows=repeats,
            ))

    excluded = {
        "outside_requested_month": {"count": len(outside_month), "event_ids": sorted(outside_month)},
        "outside_supplied_order_set": {"count": len(outside_scope), "event_ids": sorted(outside_scope)},
        "conflicting_event_ids": {"count": len(conflict_ids), "event_ids": sorted(conflict_ids)},
        "invalid_rows_without_usable_event_id": invalid_rows,
    }
    return counted, duplicate_counts, blocked_lines, excluded


def role_entry(role: str, responsibilities: dict[str, str | None]) -> dict[str, Any]:
    return {"role": role, "recipient": responsibilities.get(role)}


def follow_up_for(
    key: tuple[str, str],
    order: dict[str, Any],
    position: str,
    difference: int | None,
    blockers: list[str],
    responsibilities: dict[str, str | None],
) -> dict[str, Any] | None:
    order_id, sku = key
    if position == "received_as_ordered":
        return None

    owners: list[dict[str, Any]] = []
    external_recipient: str | None = None
    reasons: list[str] = []
    actions: list[str] = []

    identity_codes = {
        "conflicting_order_rows",
        "invalid_order_quantity",
        "conflicting_event_id",
        "unknown_sku_for_in_scope_order",
        "invalid_in_scope_event",
        "invalid_event_id",
        "invalid_event_month",
    }
    coverage_codes = {"missing_coverage", "incomplete_coverage", "conflicting_coverage"}
    if any(code in identity_codes for code in blockers):
        owners.extend([
            role_entry("purchasing_coordinator", responsibilities),
            role_entry("data_steward", responsibilities),
        ])
        reasons.append("conflicting or invalid order/event identity evidence")
        actions.append("reconcile the identified source records, then rerun the line comparison")
    if any(code in coverage_codes for code in blockers):
        owners.append(role_entry("data_steward", responsibilities))
        reasons.append("the requested-month receipt export is not confirmed complete")
        actions.append("provide or confirm the full requested-month export, then rerun the comparison")
    if position == "shortfall":
        owners.append(role_entry("purchasing_coordinator", responsibilities))
        external_recipient = order.get("supplier_contact")
        reasons.append(f"a confirmed shortfall of {difference}")
        actions.append(f"ask the supplier contact to confirm the plan and timing for the remaining {difference} units")
    elif position == "excess":
        owners.append(role_entry("warehouse_lead", responsibilities))
        reasons.append(f"a confirmed excess of {difference}")
        actions.append(f"reconcile the {difference} surplus units against the order and receiving evidence")

    deduped_owners: list[dict[str, Any]] = []
    seen_roles: set[str] = set()
    for owner in owners:
        if owner["role"] not in seen_roles:
            deduped_owners.append(owner)
            seen_roles.add(owner["role"])

    recipient_gaps = [owner["role"] for owner in deduped_owners if owner["recipient"] is None]
    if position == "shortfall" and external_recipient is None:
        recipient_gaps.append("supplier_contact")

    owner_text = "; ".join(
        f"{owner['role']}: {owner['recipient']}" if owner["recipient"] else f"{owner['role']}: recipient not supplied"
        for owner in deduped_owners
    )
    if external_recipient:
        owner_text += ("; " if owner_text else "") + f"supplier_contact: {external_recipient}"
    elif position == "shortfall":
        owner_text += ("; " if owner_text else "") + "supplier_contact: not supplied"
    next_action = "; ".join(actions)
    draft = (
        f"Draft — not sent. To/owner: {owner_text}. Order {order_id}, SKU {sku}: "
        f"{' and '.join(reasons)}. Next action: {next_action}."
    )
    return {
        "reason": "; ".join(reasons),
        "owners": deduped_owners,
        "external_recipient": external_recipient,
        "recipient_gaps": recipient_gaps,
        "next_action": next_action,
        "draft": draft,
        "sent": False,
    }


def analyze(data: Any) -> dict[str, Any]:
    month, raw_orders, raw_events, raw_coverage, raw_responsibilities = require_root(data)
    diagnostics: list[dict[str, Any]] = []
    responsibilities = clean_responsibilities(raw_responsibilities, diagnostics)
    orders, usable_order_rows = normalize_orders(raw_orders, diagnostics)
    coverage = normalize_coverage(raw_coverage, month, orders, diagnostics)
    counted, duplicate_counts, event_blocked, excluded = normalize_events(raw_events, month, orders, diagnostics)

    diagnostics_by_line: dict[tuple[str, str], list[str]] = defaultdict(list)
    for item in diagnostics:
        key = (item.get("order_id"), item.get("sku"))
        if key in orders:
            diagnostics_by_line[key].append(item["code"])
        for affected in item.get("affected_lines", []):
            affected_key = (affected.get("order_id"), affected.get("sku"))
            if affected_key in orders:
                diagnostics_by_line[affected_key].append(item["code"])

    lines: list[dict[str, Any]] = []
    for key in sorted(orders):
        order = orders[key]
        events = counted.get(key, [])
        net = sum(event["quantity"] for event in events)
        blockers: list[str] = []
        if order["order_conflict"]:
            blockers.append("conflicting_order_rows")
        elif order["ordered"] is None:
            blockers.append("invalid_order_quantity")
        coverage_state = coverage[key]
        if coverage_state == "incomplete":
            blockers.append("incomplete_coverage")
        elif coverage_state == "missing":
            blockers.append("missing_coverage")
        elif coverage_state == "conflicting":
            blockers.append("conflicting_coverage")
        if key in event_blocked:
            blockers.extend(code for code in diagnostics_by_line[key] if code in {
                "conflicting_event_id",
                "unknown_sku_for_in_scope_order",
                "invalid_in_scope_event",
                "invalid_event_id",
                "invalid_event_month",
            })
        blockers = list(dict.fromkeys(blockers))

        if blockers:
            position, difference = "undetermined", None
        elif net == order["ordered"]:
            position, difference = "received_as_ordered", 0
        elif net < order["ordered"]:
            position, difference = "shortfall", order["ordered"] - net
        else:
            position, difference = "excess", net - order["ordered"]

        follow_up = follow_up_for(key, order, position, difference, blockers, responsibilities)
        lines.append({
            "order_id": key[0],
            "sku": key[1],
            "ordered_quantity": order["ordered"],
            "observed_net_received_quantity": net,
            "position": position,
            "difference_quantity": difference,
            "coverage_state": coverage_state,
            "evidence": {
                "counted_event_ids": sorted(event["event_id"] for event in events),
                "exact_duplicate_event_rows_ignored": duplicate_counts.get(key, 0),
                "blockers": blockers,
                "diagnostic_codes": list(dict.fromkeys(diagnostics_by_line[key])),
            },
            "follow_up": follow_up,
        })

    counts = Counter(line["position"] for line in lines)
    review = {
        "review_month": month,
        "summary": {
            "supplied_order_rows": len(raw_orders),
            "usable_order_rows": usable_order_rows,
            "in_scope_lines": len(lines),
            "received_as_ordered": counts["received_as_ordered"],
            "shortfall": counts["shortfall"],
            "excess": counts["excess"],
            "undetermined": counts["undetermined"],
            "lines_requiring_follow_up": sum(line["follow_up"] is not None for line in lines),
            "lines_with_evidence_gaps": sum(bool(line["evidence"]["blockers"]) for line in lines),
        },
        "lines": lines,
        "excluded_events": excluded,
        "diagnostics": diagnostics,
        "drafts_sent": False,
    }
    return review


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calculate and classify a monthly purchase-order receiving review from JSON evidence.",
        epilog="Exit codes: 0 review produced; 1 file/JSON I/O error; 2 unusable root contract.",
    )
    parser.add_argument("input", type=Path, help="UTF-8 JSON input file")
    parser.add_argument("--output", type=Path, help="write formatted JSON to this path (default: stdout)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        with args.input.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 1
    try:
        review = analyze(data)
    except ContractError as exc:
        print(f"contract error: {exc}", file=sys.stderr)
        return 2

    rendered = json.dumps(review, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    try:
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
    except OSError as exc:
        print(f"output error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
