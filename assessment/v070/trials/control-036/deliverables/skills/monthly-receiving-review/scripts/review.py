#!/usr/bin/env python3
"""Deterministic local receipt evidence processing; no external side effects."""

import argparse
import json
import re
import sys
from pathlib import Path


def string(value):
    return isinstance(value, str) and bool(value.strip())


def integer(value):
    return type(value) is int


def month(value):
    return (isinstance(value, str)
            and re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])", value) is not None
            and value[:4] != "0000")


def fingerprint(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def review(data, source="local input"):
    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object")
    requested = data.get("month")
    if not month(requested):
        raise ValueError("month must be a valid YYYY-MM with year 0001–9999")
    orders = data.get("orders")
    if not isinstance(orders, list):
        raise ValueError("orders must be an array to establish scope")
    report = {"month": requested, "source": source, "scope": {}, "lines": [],
              "issues": [], "excluded_events": [], "excluded_coverage": []}
    lines = report["lines"]
    indexed = {}
    order_lines = {}

    def issue(code, refs, message, affected, kind="event"):
        item = {"id": f"I-{len(report['issues']) + 1}", "code": code,
                "source_refs": refs, "message": message}
        report["issues"].append(item)
        for line in affected:
            line["issue_ids"].append(item["id"])
            line["_problems"].add(kind)

    for index, row in enumerate(orders):
        valid_identity = (isinstance(row, dict) and string(row.get("order_id"))
                          and string(row.get("sku")))
        key = (row["order_id"], row["sku"]) if valid_identity else None
        if key is not None and key in indexed:
            line = indexed[key]
            line["order_record_indexes"].append(index)
            if fingerprint(row) != fingerprint(line["_order"]):
                line["ordered"] = None
                line["_contact"] = None
                issue("conflicting_order", [f"orders[{i}]" for i in line["order_record_indexes"]],
                      "Different source records identify the same order line; reconcile them.",
                      [line], "order")
            continue
        line = {"order_id": row.get("order_id") if isinstance(row, dict) else None,
                "sku": row.get("sku") if isinstance(row, dict) else None,
                "order_record_indexes": [index], "ordered": None,
                "coverage": "missing", "coverage_refs": [], "accepted_events": [],
                "issue_ids": [], "valid_event_subtotal": 0, "observed_net": None,
                "final_net": None, "status": None, "remaining": None, "excess": None,
                "actions": [], "_problems": set(), "_order": row,
                "_contact": row.get("supplier_contact") if isinstance(row, dict) else None,
                "_coverage": [], "_identity": valid_identity}
        lines.append(line)
        if valid_identity:
            indexed[key] = line
            order_lines.setdefault(key[0], []).append(line)
        else:
            issue("invalid_order_identity", [f"orders[{index}]"],
                  "Order record lacks a usable order_id/SKU; its identity and scope need reconciliation.",
                  [line], "order")
        if isinstance(row, dict) and integer(row.get("ordered")) and row["ordered"] > 0:
            line["ordered"] = row["ordered"]
        else:
            issue("invalid_order_quantity", [f"orders[{index}]"],
                  "ordered must be a positive integer; it has not been replaced with zero.",
                  [line], "order")

    identifiable = list(indexed.values())

    def targets(row, time_field):
        """Return relevant lines, identity issue, and reason for exclusion."""
        if not isinstance(row, dict):
            return identifiable, "Record is not an object; attribution is unknown.", None
        period = row.get(time_field)
        if month(period) and period != requested:
            return [], None, "outside_requested_month"
        oid = row.get("order_id")
        sku = row.get("sku")
        if not string(oid):
            return identifiable, "Missing usable order_id; attribution is unknown.", None
        if oid not in order_lines:
            return [], None, "outside_supplied_order_set"
        if not string(sku) or (oid, sku) not in indexed:
            return order_lines[oid], "SKU is absent or does not identify a supplied line on this order.", None
        return [indexed[(oid, sku)]], None, None

    events = data.get("events")
    if not isinstance(events, list):
        issue("missing_or_invalid_events", ["events"],
              "No usable event array was supplied; a received quantity cannot be calculated.",
              identifiable)
        for line in identifiable:
            line["valid_event_subtotal"] = None
        events = []

    groups = {}
    for i, row in enumerate(events):
        if isinstance(row, dict) and string(row.get("event_id")):
            groups.setdefault(row["event_id"], []).append((i, row))
    conflicts = {eid for eid, rows in groups.items()
                 if len({fingerprint(row) for _, row in rows}) > 1}
    seen = set()
    for i, row in enumerate(events):
        ref = f"events[{i}]"
        affected, identity_error, excluded = targets(row, "event_month")
        if excluded:
            report["excluded_events"].append({"source_ref": ref, "reason": excluded})
            continue
        eid = row.get("event_id") if isinstance(row, dict) else None
        if string(eid) and eid in conflicts:
            issue("conflicting_event_id", [f"events[{j}]" for j, _ in groups[eid]],
                  f"Event ID {eid!r} has different contents; no variant contributes.", affected)
            if identity_error:
                issue("event_identity", [ref], identity_error, affected)
            continue
        if identity_error:
            issue("event_identity", [ref], identity_error, affected)
            continue
        if not isinstance(row, dict):
            continue
        errors = []
        if not string(eid):
            errors.append("event_id must be a nonblank string")
        if not month(row.get("event_month")):
            errors.append("event_month is missing or invalid; month inclusion is unknown")
        if not integer(row.get("quantity")):
            errors.append("quantity must be a signed integer")
        if errors:
            issue("invalid_event", [ref], "; ".join(errors), affected)
            continue
        signature = fingerprint(row)
        if signature in seen:
            report["excluded_events"].append({"source_ref": ref, "reason": "exact_duplicate"})
            continue
        seen.add(signature)
        for line in affected:
            line["valid_event_subtotal"] += row["quantity"]
            line["accepted_events"].append({"source_ref": ref, "event_id": eid,
                                             "quantity": row["quantity"]})

    coverage = data.get("coverage")
    if not isinstance(coverage, list):
        issue("missing_or_invalid_coverage", ["coverage"],
              "No usable coverage array was supplied; completeness is unknown.", identifiable, "coverage")
        coverage = []
    for i, row in enumerate(coverage):
        ref = f"coverage[{i}]"
        affected, identity_error, excluded = targets(row, "month")
        # Unlike receipt events, extra SKU declarations do not taint an order's receipts.
        if (isinstance(row, dict) and string(row.get("order_id"))
                and string(row.get("sku")) and (row["order_id"], row["sku"]) not in indexed):
            excluded = excluded or "outside_supplied_lines"
        if excluded:
            report["excluded_coverage"].append({"source_ref": ref, "reason": excluded})
            continue
        for line in affected:
            line["coverage_refs"].append(ref)
        if (identity_error or not isinstance(row, dict) or not month(row.get("month"))
                or type(row.get("complete")) is not bool):
            issue("invalid_coverage", [ref],
                  identity_error or "Coverage requires a valid month and Boolean complete value.",
                  affected, "coverage")
        else:
            for line in affected:
                line["_coverage"].append(row["complete"])

    roles = data.get("responsibilities")
    if not isinstance(roles, dict):
        roles = {}

    def action(line, kind, owner_roles, recipient_roles, next_action):
        owners = [{"role": role, "name": roles.get(role) if string(roles.get(role)) else None}
                  for role in owner_roles]
        recipients = []
        for role in recipient_roles:
            value = line["_contact"] if role == "supplier_contact" else roles.get(role)
            recipients.append({"role": role, "name": value if string(value) else None})
        missing = list(dict.fromkeys(item["role"] for item in owners + recipients if item["name"] is None))
        destination = "; ".join(item["name"] or f"[recipient required: {item['role']}]"
                                 for item in recipients)
        line_name = (f"{line['order_id']} / {line['sku']}" if line["_identity"]
                     else f"unresolved order record(s) {line['order_record_indexes']}")
        line["actions"].append({"kind": kind, "responsible": owners, "recipients": recipients,
                                "missing_routing": missing, "next_action": next_action,
                                "draft_seed": f"Draft — not sent\nTo: {destination}\n"
                                              f"Subject: {requested} receiving review — {line_name}\n"
                                              f"For {requested}, {line_name}: {next_action}"})

    for line in lines:
        cov = set(line["_coverage"])
        if len(cov) > 1:
            issue("conflicting_coverage", line["coverage_refs"],
                  "Coverage declarations disagree about completeness.", [line], "coverage")
        if "coverage" in line["_problems"]:
            line["coverage"] = "invalid"
        elif cov:
            line["coverage"] = "complete" if True in cov else "partial"
        else:
            issue("missing_coverage", [], "No declaration confirms coverage for this line and month.",
                  [line], "coverage")
        if not line["_identity"]:
            line["valid_event_subtotal"] = None
        elif "event" not in line["_problems"]:
            line["observed_net"] = line["valid_event_subtotal"]
        if "order" in line["_problems"] or "event" in line["_problems"]:
            line["status"] = "invalid_order" if not line["_identity"] else "blocked_evidence"
            refs = list(dict.fromkeys(ref for item in report["issues"]
                                     if item["id"] in line["issue_ids"]
                                     and item["code"] not in {"missing_coverage", "invalid_coverage", "conflicting_coverage"}
                                     for ref in item["source_refs"]))
            action(line, "reconcile_sources", ["purchasing_coordinator", "data_steward"],
                   ["purchasing_coordinator", "data_steward"],
                   "Reconcile the order/event source records " + ", ".join(refs)
                   + "; supply corrected identities, quantities, or export records before final comparison.")
        elif line["coverage"] != "complete":
            line["status"] = "incomplete_evidence"
        else:
            line["final_net"] = line["observed_net"]
            difference = line["final_net"] - line["ordered"]
            if difference == 0:
                line["status"] = "received_as_ordered"
            elif difference < 0:
                line["status"] = "shortfall"
                line["remaining"] = -difference
                action(line, "supplier_follow_up", ["purchasing_coordinator"], ["supplier_contact"],
                       f"The complete export shows net received {line['final_net']} against ordered "
                       f"{line['ordered']}; confirm the receipt plan for the remaining {-difference} units.")
            else:
                line["status"] = "excess"
                line["excess"] = difference
                action(line, "reconcile_surplus", ["warehouse_lead"], ["warehouse_lead"],
                       f"Reconcile the surplus of {difference} units (net received {line['final_net']}, "
                       f"ordered {line['ordered']}) against the order and receiving evidence.")
        if line["coverage"] != "complete":
            action(line, "confirm_export", ["data_steward"], ["data_steward"],
                   f"Coverage is {line['coverage']}; provide or confirm the full receiving export and "
                   "an explicit coverage declaration for this line and month before final comparison.")
        for key in list(line):
            if key.startswith("_"):
                del line[key]
    report["scope"] = {"supplied_order_records": len(orders), "unique_identifiable_lines": len(indexed),
                       "unresolved_order_records": sum(len(line["order_record_indexes"]) for line in lines
                                                        if line["status"] == "invalid_order"),
                       "reported_entries": len(lines)}
    return report


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"Nonfinite JSON number is not allowed: {value}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="UTF-8 JSON business input (read only)")
    parser.add_argument("--output", type=Path, help="new JSON report path; default stdout; never overwrites")
    args = parser.parse_args(argv)
    try:
        with args.input.open(encoding="utf-8") as handle:
            data = json.load(handle, object_pairs_hook=unique_object, parse_constant=reject_constant)
        result = review(data, str(args.input))
        payload = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(payload)
        else:
            sys.stdout.write(payload)
        return 0
    except (OSError, ValueError, TypeError, UnicodeError) as error:
        print(f"receiving-review: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
