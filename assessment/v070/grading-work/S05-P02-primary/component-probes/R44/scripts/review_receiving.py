#!/usr/bin/env python3
"""Build a controlled monthly purchase-order receiving review from JSON."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any


MONTH_RE = re.compile(r"^(?:\d{4})-(?:0[1-9]|1[0-2])$")
ROLES = ("purchasing_coordinator", "warehouse_lead", "data_steward")


class ScopeError(ValueError):
    """The top-level review scope cannot be processed."""


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def issue(source: str, message: str, **context: Any) -> dict[str, Any]:
    result = {"source": source, "message": message}
    result.update(context)
    return result


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def load_input(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ScopeError(f"cannot read input JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ScopeError("top-level JSON value must be an object")
    month = data.get("month")
    if not nonempty_string(month) or not MONTH_RE.fullmatch(month):
        raise ScopeError("month must use YYYY-MM with a valid month number")
    for field in ("orders", "events", "coverage"):
        if not isinstance(data.get(field), list):
            raise ScopeError(f"{field} must be an array")
    if not isinstance(data.get("responsibilities"), dict):
        raise ScopeError("responsibilities must be an object")
    return data


def add_gap(line: dict[str, Any], text: str) -> None:
    if text not in line["evidence_gaps"]:
        line["evidence_gaps"].append(text)


def role_value(responsibilities: dict[str, Any], role: str) -> str | None:
    value = responsibilities.get(role)
    return value.strip() if nonempty_string(value) else None


def make_follow_up(
    *,
    reason: str,
    role: str,
    responsible: str | None,
    recipient: str | None,
    next_action: str,
    draft_body: str,
) -> dict[str, Any]:
    draft = None
    if responsible is not None and recipient is not None:
        draft = f"To: {recipient}\nFrom/owner: {responsible}\n\n{draft_body}"
    return {
        "reason": reason,
        "responsible_role": role,
        "responsible": responsible,
        "recipient": recipient,
        "next_action": next_action,
        "draft": draft,
    }


def build_review(data: dict[str, Any]) -> dict[str, Any]:
    month: str = data["month"]
    input_issues: list[dict[str, Any]] = []
    responsibilities = data["responsibilities"]
    people = {role: role_value(responsibilities, role) for role in ROLES}
    for role, value in people.items():
        if value is None:
            input_issues.append(issue("responsibilities", f"missing or invalid {role}", role=role))

    lines: dict[tuple[str, str], dict[str, Any]] = {}
    order_keys: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for index, row in enumerate(data["orders"]):
        source = f"orders[{index}]"
        if not isinstance(row, dict):
            input_issues.append(issue(source, "order line must be an object"))
            continue
        order_id, sku = row.get("order_id"), row.get("sku")
        if not nonempty_string(order_id) or not nonempty_string(sku):
            input_issues.append(issue(source, "order_id and sku must be non-empty strings"))
            continue
        key = (order_id, sku)
        if key in lines:
            input_issues.append(issue(source, "duplicate supplied order line", order_id=order_id, sku=sku))
            add_gap(lines[key], "Duplicate supplied order line makes the order evidence ambiguous.")
            lines[key]["blocking_issue"] = True
            continue
        ordered = row.get("ordered")
        supplier = row.get("supplier_contact")
        line = {
            "order_id": order_id,
            "sku": sku,
            "ordered": ordered if integer(ordered) and ordered > 0 else None,
            "supplier_contact": supplier.strip() if nonempty_string(supplier) else None,
            "observed_net_received": 0,
            "accepted_event_ids": [],
            "excluded_conflicting_event_ids": [],
            "coverage_status": "missing",
            "final_net_received": None,
            "difference_from_order": None,
            "receipt_position": "undetermined",
            "evidence_gaps": [],
            "follow_up": [],
            "blocking_issue": False,
        }
        if line["ordered"] is None:
            input_issues.append(issue(source, "ordered must be a positive integer", order_id=order_id, sku=sku))
            add_gap(line, "The ordered quantity is missing or invalid, so no final comparison is possible.")
            line["blocking_issue"] = True
        if line["supplier_contact"] is None:
            input_issues.append(issue(source, "supplier_contact is missing or invalid", order_id=order_id, sku=sku))
        lines[key] = line
        order_keys[order_id].append(key)

    event_groups: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    anonymous_events: list[tuple[int, Any]] = []
    for index, row in enumerate(data["events"]):
        if not isinstance(row, dict) or not nonempty_string(row.get("event_id")):
            anonymous_events.append((index, row))
            continue
        event_groups[row["event_id"]][canonical(row)] = row

    for index, row in anonymous_events:
        source = f"events[{index}]"
        input_issues.append(issue(source, "event must be an object with a non-empty event_id"))
        if isinstance(row, dict) and row.get("order_id") in order_keys:
            sku = row.get("sku")
            affected = [(row["order_id"], sku)] if (row["order_id"], sku) in lines else order_keys[row["order_id"]]
            for key in affected:
                add_gap(lines[key], "An identifiable event row is invalid and was excluded from the subtotal.")
                lines[key]["blocking_issue"] = True

    ignored_out_of_month: list[str] = []
    ignored_out_of_scope: list[str] = []
    identity_event_ids: dict[tuple[str, str], set[str]] = defaultdict(set)
    conflict_event_ids: dict[tuple[str, str], set[str]] = defaultdict(set)

    for event_id, variants_by_text in event_groups.items():
        variants = list(variants_by_text.values())
        if len(variants) > 1:
            current_variants = [row for row in variants if row.get("event_month") == month]
            if not current_variants:
                ignored_out_of_month.append(event_id)
                continue
            affected: set[tuple[str, str]] = set()
            for row in variants:
                order_id, sku = row.get("order_id"), row.get("sku")
                if (order_id, sku) in lines:
                    affected.add((order_id, sku))
                elif order_id in order_keys and row.get("event_month") == month:
                    affected.update(order_keys[order_id])
            if not affected:
                ignored_out_of_scope.append(event_id)
            for key in affected:
                conflict_event_ids[key].add(event_id)
                lines[key]["excluded_conflicting_event_ids"].append(event_id)
                add_gap(lines[key], f"Event ID {event_id} has conflicting content; its variants were excluded.")
                lines[key]["blocking_issue"] = True
            continue

        row = variants[0]
        source = f"event_id {event_id}"
        order_id, sku = row.get("order_id"), row.get("sku")
        event_month, quantity = row.get("event_month"), row.get("quantity")
        errors = []
        if not nonempty_string(order_id) or not nonempty_string(sku):
            errors.append("order_id and sku must be non-empty strings")
        if not nonempty_string(event_month) or not MONTH_RE.fullmatch(event_month):
            errors.append("event_month must be YYYY-MM")
        if not integer(quantity):
            errors.append("quantity must be a signed integer")
        if errors:
            input_issues.append(issue(source, "; ".join(errors), event_id=event_id))
            if order_id in order_keys:
                affected = [(order_id, sku)] if (order_id, sku) in lines else order_keys[order_id]
                for key in affected:
                    add_gap(lines[key], f"Event ID {event_id} is invalid and was excluded from the subtotal.")
                    lines[key]["blocking_issue"] = True
            continue
        if event_month != month:
            ignored_out_of_month.append(event_id)
            continue
        if order_id not in order_keys:
            ignored_out_of_scope.append(event_id)
            continue
        key = (order_id, sku)
        if key not in lines:
            for affected_key in order_keys[order_id]:
                identity_event_ids[affected_key].add(event_id)
                add_gap(
                    lines[affected_key],
                    f"Current-month event {event_id} uses unknown SKU {sku!r} for in-scope order {order_id}.",
                )
                lines[affected_key]["blocking_issue"] = True
            continue
        lines[key]["observed_net_received"] += quantity
        lines[key]["accepted_event_ids"].append(event_id)

    coverage_values: dict[tuple[str, str], set[bool]] = defaultdict(set)
    invalid_coverage: set[tuple[str, str]] = set()
    ignored_coverage = 0
    for index, row in enumerate(data["coverage"]):
        source = f"coverage[{index}]"
        if not isinstance(row, dict):
            input_issues.append(issue(source, "coverage declaration must be an object"))
            continue
        order_id, sku, declared_month = row.get("order_id"), row.get("sku"), row.get("month")
        if declared_month != month:
            ignored_coverage += 1
            continue
        key = (order_id, sku)
        if key not in lines:
            ignored_coverage += 1
            continue
        complete = row.get("complete")
        if not isinstance(complete, bool):
            input_issues.append(issue(source, "complete must be Boolean", order_id=order_id, sku=sku))
            invalid_coverage.add(key)
            continue
        coverage_values[key].add(complete)

    for key, line in lines.items():
        values = coverage_values.get(key, set())
        if key in invalid_coverage:
            line["coverage_status"] = "invalid"
            add_gap(line, "The applicable coverage declaration is invalid, so export completeness is unknown.")
        elif values == {True}:
            line["coverage_status"] = "complete"
        elif values == {False}:
            line["coverage_status"] = "incomplete"
            add_gap(line, "The event export is incomplete; the observed subtotal is not a final receipt position.")
        elif values == {True, False}:
            line["coverage_status"] = "conflicting"
            add_gap(line, "Coverage declarations conflict, so export completeness is unresolved.")
        else:
            line["coverage_status"] = "missing"
            add_gap(line, "No applicable coverage declaration confirms whether the event export is complete.")

        can_finalize = (
            not line["blocking_issue"]
            and line["coverage_status"] == "complete"
            and line["ordered"] is not None
        )
        if can_finalize:
            line["final_net_received"] = line["observed_net_received"]
            difference = line["final_net_received"] - line["ordered"]
            line["difference_from_order"] = difference
            if difference == 0:
                line["receipt_position"] = "received_as_ordered"
            elif difference < 0:
                line["receipt_position"] = "shortfall"
            else:
                line["receipt_position"] = "excess"

        order_id, sku = key
        conflict_ids = sorted(conflict_event_ids.get(key, set()))
        identity_ids = sorted(identity_event_ids.get(key, set()))
        if conflict_ids or identity_ids or line["blocking_issue"]:
            ids = sorted(set(conflict_ids + identity_ids))
            record_text = ", ".join(ids) if ids else f"order {order_id}, SKU {sku}"
            recipient = people["data_steward"]
            follow = make_follow_up(
                reason="source_or_identity_reconciliation",
                role="purchasing_coordinator",
                responsible=people["purchasing_coordinator"],
                recipient=recipient,
                next_action=f"Reconcile the identified order and event source records ({record_text}) with the data steward before final comparison.",
                draft_body=(
                    f"Please reconcile the source records for order {order_id}, SKU {sku}. "
                    f"The affected event/reference set is {record_text}. Confirm the correct identity and content, then provide corrected evidence for the {month} review."
                ),
            )
            line["follow_up"].append(follow)
            if follow["draft"] is None:
                add_gap(line, "The source-reconciliation draft lacks a supplied purchasing coordinator or data steward identity.")

        if line["coverage_status"] != "complete":
            follow = make_follow_up(
                reason="export_completeness",
                role="data_steward",
                responsible=people["data_steward"],
                recipient=people["data_steward"],
                next_action=f"Provide or confirm the full {month} event export for order {order_id}, SKU {sku}, and resolve the coverage declaration.",
                draft_body=(
                    f"Please provide or confirm the complete {month} receiving-event export for order {order_id}, SKU {sku}, "
                    f"and confirm its coverage status. The current observed subtotal is {line['observed_net_received']} and is not being treated as final."
                ),
            )
            line["follow_up"].append(follow)
            if follow["draft"] is None:
                add_gap(line, "The export-completeness draft lacks a supplied data steward identity.")
        elif line["receipt_position"] == "shortfall":
            remaining = -line["difference_from_order"]
            follow = make_follow_up(
                reason="complete_shortfall",
                role="purchasing_coordinator",
                responsible=people["purchasing_coordinator"],
                recipient=line["supplier_contact"],
                next_action=f"Ask the supplier contact to confirm the plan for the remaining {remaining} units.",
                draft_body=(
                    f"For order {order_id}, SKU {sku}, the complete {month} evidence shows {line['final_net_received']} received "
                    f"against {line['ordered']} ordered. Please confirm the receipt plan for the remaining {remaining} units."
                ),
            )
            line["follow_up"].append(follow)
            if follow["draft"] is None:
                add_gap(line, "The shortfall follow-up lacks a supplied purchasing coordinator or supplier contact identity.")
        elif line["receipt_position"] == "excess":
            excess = line["difference_from_order"]
            follow = make_follow_up(
                reason="complete_excess",
                role="warehouse_lead",
                responsible=people["warehouse_lead"],
                recipient=people["warehouse_lead"],
                next_action=f"Reconcile the excess {excess} units against the order and receiving evidence.",
                draft_body=(
                    f"Please reconcile order {order_id}, SKU {sku}: complete {month} evidence shows {line['final_net_received']} received "
                    f"against {line['ordered']} ordered, an excess of {excess}. Confirm the source and corrective disposition."
                ),
            )
            line["follow_up"].append(follow)
            if follow["draft"] is None:
                add_gap(line, "The excess-reconciliation draft lacks a supplied warehouse lead identity.")

        line["accepted_event_ids"].sort()
        line["excluded_conflicting_event_ids"] = sorted(set(line["excluded_conflicting_event_ids"]))
        line["evidence_gaps"].sort()
        del line["blocking_issue"]

    return {
        "review_month": month,
        "scope": {
            "supplied_order_rows": len(data["orders"]),
            "identifiable_order_lines": len(lines),
        },
        "input_issues": input_issues,
        "ignored": {
            "out_of_month_event_ids": sorted(set(ignored_out_of_month)),
            "out_of_scope_event_ids": sorted(set(ignored_out_of_scope)),
            "non_applicable_coverage_rows": ignored_coverage,
        },
        "lines": [lines[key] for key in sorted(lines)],
    }


def write_json_atomic(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as handle:
            temp_name = handle.name
            json.dump(result, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(temp_name, path)
    finally:
        if temp_name is not None and os.path.exists(temp_name):
            os.unlink(temp_name)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Review monthly purchase-order receipts from the documented JSON contract."
    )
    parser.add_argument("input", type=Path, help="UTF-8 input JSON path")
    parser.add_argument("--output", type=Path, help="write review JSON atomically; default: stdout")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        result = build_review(load_input(args.input))
        if args.output:
            write_json_atomic(args.output, result)
        else:
            json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
            sys.stdout.write("\n")
    except ScopeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: cannot write output: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
