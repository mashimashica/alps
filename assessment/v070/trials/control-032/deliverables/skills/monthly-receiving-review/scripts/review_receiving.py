#!/usr/bin/env python3
"""Build an evidence-aware monthly receiving review from ordinary JSON."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


MONTH_RE = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")
ROLE_LABELS = {
    "purchasing_coordinator": "purchasing coordinator",
    "warehouse_lead": "warehouse lead",
    "data_steward": "data steward",
}


class InputError(ValueError):
    """A blocking input or file error suitable for a concise CLI diagnostic."""


def is_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def is_month(value: Any) -> bool:
    return isinstance(value, str) and MONTH_RE.fullmatch(value) is not None


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def unique_records(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    repeats = 0
    for record in records:
        marker = canonical(record)
        if marker in seen:
            repeats += 1
            continue
        seen.add(marker)
        unique.append(record)
    return unique, repeats


def role_entry(role: str, responsibilities: dict[str, Any]) -> dict[str, Any]:
    value = responsibilities.get(role)
    return {
        "role": role,
        "role_label": ROLE_LABELS[role],
        "recipient": value.strip() if is_text(value) else None,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calculate an evidence-aware monthly purchase-order receiving review."
    )
    parser.add_argument("input", type=Path, help="UTF-8 JSON input file")
    parser.add_argument(
        "-o", "--output", type=Path, help="write JSON to this file instead of stdout"
    )
    return parser.parse_args(argv)


def load_input(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InputError(f"cannot read valid UTF-8 JSON from {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise InputError("input root must be a JSON object")
    if not is_month(data.get("month")):
        raise InputError("month must be a valid YYYY-MM string")
    for field in ("orders", "events", "coverage"):
        if not isinstance(data.get(field), list):
            raise InputError(f"{field} must be a JSON array; missing data is not treated as empty")
    return data


def review(data: dict[str, Any]) -> dict[str, Any]:
    month = data["month"]
    raw_orders = data["orders"]
    raw_events = data["events"]
    raw_coverage = data["coverage"]
    responsibilities = data.get("responsibilities")
    unassigned: list[dict[str, Any]] = []
    if not isinstance(responsibilities, dict):
        responsibilities = {}
        unassigned.append(
            {
                "source": "responsibilities",
                "issue": "responsibilities must be an object; required recipients may be unavailable",
            }
        )

    # Keep every identifiable supplied order line, while exact record repeats count once.
    order_objects: list[dict[str, Any]] = []
    unidentifiable_order_records = 0
    for index, record in enumerate(raw_orders):
        if not isinstance(record, dict):
            unidentifiable_order_records += 1
            unassigned.append(
                {"source": "orders", "index": index, "issue": "order record is not an object"}
            )
            continue
        order_objects.append(record)
    unique_orders, duplicate_order_records = unique_records(order_objects)
    order_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in unique_orders:
        if not is_text(record.get("order_id")) or not is_text(record.get("sku")):
            unidentifiable_order_records += 1
            unassigned.append(
                {
                    "source": "orders",
                    "record": record,
                    "issue": "order line lacks usable order_id and sku identifiers",
                }
            )
            continue
        key = (record["order_id"].strip(), record["sku"].strip())
        order_groups[key].append(record)

    line_state: dict[tuple[str, str], dict[str, Any]] = {}
    lines_by_order: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for key, records in order_groups.items():
        order_id, sku = key
        lines_by_order[order_id].append(key)
        relevant_variants = {
            canonical(
                {
                    "ordered": record.get("ordered"),
                    "supplier_contact": record.get("supplier_contact"),
                }
            )
            for record in records
        }
        ordered_values = {
            record.get("ordered")
            for record in records
            if is_int(record.get("ordered")) and record["ordered"] > 0
        }
        contacts = {
            record["supplier_contact"].strip()
            for record in records
            if is_text(record.get("supplier_contact"))
        }
        gaps: list[str] = []
        tags: set[str] = set()
        if len(relevant_variants) > 1:
            gaps.append("supplied order records for this line have different content")
            tags.add("conflict")
        if len(ordered_values) != 1 or any(
            not is_int(record.get("ordered")) or record.get("ordered", 0) <= 0
            for record in records
        ):
            gaps.append("ordered quantity is missing, invalid, or inconsistent; expected one positive integer")
            tags.add("invalid")
        if len(contacts) > 1:
            gaps.append("supplier contact is conflicting across supplied order records")
        elif not contacts:
            gaps.append("supplier contact is not supplied")
        line_state[key] = {
            "order_id": order_id,
            "sku": sku,
            "ordered": next(iter(ordered_values)) if len(ordered_values) == 1 else None,
            "supplier_contact": next(iter(contacts)) if len(contacts) == 1 else None,
            "subtotal": 0,
            "event_ids": [],
            "gaps": gaps,
            "tags": tags,
        }

    scope_order_ids = set(lines_by_order)

    # Coverage is affirmative evidence for one line and month. Absence is not completeness.
    coverage_objects: list[dict[str, Any]] = []
    for index, record in enumerate(raw_coverage):
        if not isinstance(record, dict):
            unassigned.append(
                {"source": "coverage", "index": index, "issue": "coverage record is not an object"}
            )
            continue
        coverage_objects.append(record)
    unique_coverage, duplicate_coverage_records = unique_records(coverage_objects)
    coverage_values: dict[tuple[str, str], list[Any]] = defaultdict(list)
    for record in unique_coverage:
        order_id = record.get("order_id")
        sku = record.get("sku")
        coverage_month = record.get("month")
        if not (is_text(order_id) and is_text(sku)):
            unassigned.append(
                {"source": "coverage", "record": record, "issue": "coverage identifiers are unusable"}
            )
            continue
        key = (order_id.strip(), sku.strip())
        if not is_month(coverage_month):
            if key in line_state:
                line_state[key]["gaps"].append("coverage month is missing or invalid")
                line_state[key]["tags"].add("invalid")
            else:
                unassigned.append(
                    {"source": "coverage", "record": record, "issue": "coverage month is invalid"}
                )
            continue
        if coverage_month != month:
            continue
        if key not in line_state:
            continue
        coverage_values[key].append(record.get("complete"))

    for key, state in line_state.items():
        values = coverage_values.get(key, [])
        valid_values = {value for value in values if isinstance(value, bool)}
        has_invalid = any(not isinstance(value, bool) for value in values)
        if not values:
            state["gaps"].append("no requested-month coverage declaration is supplied")
            state["tags"].add("incomplete")
        elif has_invalid or len(valid_values) != 1:
            state["gaps"].append("requested-month coverage declarations are invalid or conflicting")
            state["tags"].add("conflict" if len(valid_values) > 1 else "invalid")
        elif valid_values == {False}:
            state["gaps"].append("requested-month event export is declared incomplete")
            state["tags"].add("incomplete")

    # Group events by ID after removing exact copies. Differing content under one ID conflicts.
    event_objects: list[dict[str, Any]] = []
    opaque_event_records = 0
    for index, record in enumerate(raw_events):
        if not isinstance(record, dict):
            opaque_event_records += 1
            unassigned.append(
                {"source": "events", "index": index, "issue": "event record is not an object"}
            )
            continue
        event_objects.append(record)
    unique_events, duplicate_event_records = unique_records(event_objects)
    event_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    no_id_events: list[dict[str, Any]] = []
    for record in unique_events:
        if is_text(record.get("event_id")):
            event_groups[record["event_id"].strip()].append(record)
        else:
            no_id_events.append(record)

    outside_scope_events: list[str] = []
    ignored_other_month: list[str] = []

    def mark_all_lines_invalid(message: str) -> None:
        for state in line_state.values():
            state["gaps"].append(message)
            state["tags"].add("invalid")

    if opaque_event_records:
        mark_all_lines_invalid(
            f"{opaque_event_records} event record(s) are not objects and cannot be assigned to a line"
        )

    def potential_keys(record: dict[str, Any]) -> list[tuple[str, str]]:
        order_id = record.get("order_id")
        sku = record.get("sku")
        if not is_text(order_id) or order_id.strip() not in scope_order_ids:
            return []
        oid = order_id.strip()
        if is_text(sku) and (oid, sku.strip()) in line_state:
            return [(oid, sku.strip())]
        return list(lines_by_order[oid])

    for record in no_id_events:
        affected = potential_keys(record)
        if affected:
            for key in affected:
                line_state[key]["gaps"].append("an event potentially affecting this line lacks a usable event_id")
                line_state[key]["tags"].add("invalid")
        else:
            order_id = record.get("order_id")
            if not is_text(order_id):
                mark_all_lines_invalid(
                    "an event lacks both a usable event_id and an assignable order_id"
                )
            unassigned.append(
                {"source": "events", "record": record, "issue": "event_id is missing or invalid"}
            )

    for event_id, records in event_groups.items():
        if len(records) > 1:
            affected: set[tuple[str, str]] = set()
            for record in records:
                event_month = record.get("event_month")
                if event_month == month or not is_month(event_month):
                    affected.update(potential_keys(record))
            if affected:
                for key in affected:
                    line_state[key]["gaps"].append(
                        f"event_id {event_id} has conflicting content and was not counted"
                    )
                    line_state[key]["tags"].add("conflict")
            else:
                if any(
                    (record.get("event_month") == month or not is_month(record.get("event_month")))
                    and not is_text(record.get("order_id"))
                    for record in records
                ):
                    mark_all_lines_invalid(
                        f"conflicting event_id {event_id} includes an unassignable order_id"
                    )
                unassigned.append(
                    {
                        "source": "events",
                        "event_id": event_id,
                        "issue": "event_id has conflicting content but no requested-month in-scope line can be assigned",
                    }
                )
            continue

        record = records[0]
        order_id = record.get("order_id")
        if not is_text(order_id):
            mark_all_lines_invalid(
                f"event {event_id} has no assignable order_id and could affect an in-scope line"
            )
            unassigned.append(
                {"source": "events", "event_id": event_id, "issue": "order_id is missing or invalid"}
            )
            continue
        order_id = order_id.strip()
        if order_id not in scope_order_ids:
            outside_scope_events.append(event_id)
            continue
        event_month = record.get("event_month")
        keys = potential_keys(record)
        if not is_month(event_month):
            for key in keys:
                line_state[key]["gaps"].append(
                    f"event {event_id} has a missing or invalid event_month"
                )
                line_state[key]["tags"].add("invalid")
            continue
        if event_month != month:
            ignored_other_month.append(event_id)
            continue
        sku = record.get("sku")
        if not is_text(sku) or (order_id, sku.strip()) not in line_state:
            for key in lines_by_order[order_id]:
                line_state[key]["gaps"].append(
                    f"current-month event {event_id} has SKU {sku!r}, absent from supplied order {order_id}"
                )
                line_state[key]["tags"].add("identity")
            continue
        key = (order_id, sku.strip())
        quantity = record.get("quantity")
        if not is_int(quantity):
            line_state[key]["gaps"].append(
                f"current-month event {event_id} has a missing or invalid signed quantity"
            )
            line_state[key]["tags"].add("invalid")
            continue
        line_state[key]["subtotal"] += quantity
        line_state[key]["event_ids"].append(event_id)

    def make_follow_up(state: dict[str, Any], status: str, position: str) -> dict[str, Any] | None:
        order_id = state["order_id"]
        sku = state["sku"]
        if status == "complete" and position == "received_as_ordered":
            return None
        if status == "complete" and position == "shortfall":
            remaining = state["ordered"] - state["subtotal"]
            owner = role_entry("purchasing_coordinator", responsibilities)
            supplier = state["supplier_contact"]
            return {
                "type": "supplier_remaining_receipt",
                "owners": [owner],
                "external_recipient": supplier,
                "next_action": f"Confirm the receipt plan and timing for the remaining {remaining} units.",
                "draft_basis": (
                    f"Order {order_id}, SKU {sku}, is short by {remaining} units for {month}; "
                    "ask the supplied supplier contact to confirm receipt plan and timing."
                ),
            }
        if status == "complete" and position == "excess":
            excess = state["subtotal"] - state["ordered"]
            owner = role_entry("warehouse_lead", responsibilities)
            return {
                "type": "surplus_reconciliation",
                "owners": [owner],
                "external_recipient": None,
                "next_action": f"Reconcile the {excess}-unit surplus against the order and receiving evidence.",
                "draft_basis": (
                    f"Order {order_id}, SKU {sku}, has a {excess}-unit excess for {month}; "
                    "reconcile the surplus against the order and receiving records."
                ),
            }
        if status in {"conflicting_evidence", "identity_reconciliation"}:
            owners = [
                role_entry("purchasing_coordinator", responsibilities),
                role_entry("data_steward", responsibilities),
            ]
            return {
                "type": "source_record_reconciliation",
                "owners": owners,
                "external_recipient": None,
                "next_action": "Reconcile the identified order and event source records, then rerun the line comparison.",
                "draft_basis": (
                    f"Order {order_id}, SKU {sku}, has conflicting or mismatched receiving evidence for {month}; "
                    "reconcile the identified source records before recalculation."
                ),
            }
        owner = role_entry("data_steward", responsibilities)
        return {
            "type": "complete_or_correct_export",
            "owners": [owner],
            "external_recipient": None,
            "next_action": "Provide, correct, or confirm the full requested-month event export, then rerun the final comparison.",
            "draft_basis": (
                f"Order {order_id}, SKU {sku}, cannot be finalized for {month}; "
                "provide, correct, or confirm the full event export described by the evidence gaps."
            ),
        }

    output_lines: list[dict[str, Any]] = []
    for key in sorted(line_state):
        state = line_state[key]
        tags = state["tags"]
        if "identity" in tags:
            evidence_status = "identity_reconciliation"
        elif "conflict" in tags:
            evidence_status = "conflicting_evidence"
        elif "invalid" in tags:
            evidence_status = "invalid_evidence"
        elif "incomplete" in tags:
            evidence_status = "incomplete_export"
        else:
            evidence_status = "complete"

        ordered = state["ordered"]
        final_net: int | None = None
        variance: int | None = None
        position = "undetermined"
        if evidence_status == "complete" and ordered is not None:
            final_net = state["subtotal"]
            variance = final_net - ordered
            if variance == 0:
                position = "received_as_ordered"
            elif variance < 0:
                position = "shortfall"
            else:
                position = "excess"

        follow_up = make_follow_up(state, evidence_status, position)
        gaps = list(dict.fromkeys(state["gaps"]))
        if follow_up:
            missing_roles = [
                owner["role"] for owner in follow_up["owners"] if owner["recipient"] is None
            ]
            if missing_roles:
                gaps.append("missing supplied recipient for role(s): " + ", ".join(missing_roles))
            if follow_up["type"] == "supplier_remaining_receipt" and not state["supplier_contact"]:
                gaps.append("missing unambiguous supplied supplier contact for shortfall follow-up")

        output_lines.append(
            {
                "order_id": state["order_id"],
                "sku": state["sku"],
                "ordered": ordered,
                "counted_event_ids": sorted(state["event_ids"]),
                "observed_subtotal": state["subtotal"],
                "observed_subtotal_is_final": final_net is not None,
                "final_net_received": final_net,
                "variance_received_minus_ordered": variance,
                "evidence_status": evidence_status,
                "position": position,
                "evidence_gaps": gaps,
                "follow_up": follow_up,
            }
        )

    resolved = sum(line["position"] != "undetermined" for line in output_lines)
    follow_ups = sum(line["follow_up"] is not None for line in output_lines)
    return {
        "review_month": month,
        "review_summary": {
            "supplied_order_records": len(raw_orders),
            "identifiable_supplied_lines": len(output_lines),
            "unidentifiable_order_records": unidentifiable_order_records,
            "resolved_positions": resolved,
            "undetermined_positions": len(output_lines) - resolved,
            "lines_requiring_follow_up": follow_ups,
        },
        "lines": output_lines,
        "outside_scope_events": sorted(set(outside_scope_events)),
        "ignored_other_month_event_ids": sorted(set(ignored_other_month)),
        "unassigned_issues": unassigned,
        "processing_notes": {
            "exact_duplicate_order_records_ignored": duplicate_order_records,
            "exact_duplicate_event_records_ignored": duplicate_event_records,
            "exact_duplicate_coverage_records_ignored": duplicate_coverage_records,
            "observed_subtotal_rule": "sum of valid, unique, matching requested-month events; may be non-final",
            "no_external_actions": "No messages were sent and no order or receiving records were changed.",
        },
    }


def write_output(result: dict[str, Any], path: Path | None) -> None:
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if path is None:
        sys.stdout.write(rendered)
        return
    try:
        path.write_text(rendered, encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise InputError(f"cannot write output to {path}: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = review(load_input(args.input))
        write_output(result, args.output)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
