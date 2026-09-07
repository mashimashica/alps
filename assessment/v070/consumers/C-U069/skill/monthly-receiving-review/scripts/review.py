#!/usr/bin/env python3
"""Read local receiving evidence and produce a review with unsent follow-up drafts."""
import argparse
import json
import re
import sys
from collections import defaultdict


def string(value):
    return isinstance(value, str) and bool(value.strip())


def month(value):
    return (isinstance(value, str) and
            re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])", value) is not None and
            value[:4] != "0000")


def integer(value):
    return type(value) is int


def fingerprint(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def key(row):
    if isinstance(row, dict) and string(row.get("order_id")) and string(row.get("sku")):
        return row["order_id"], row["sku"]
    return None


def review(data):
    if not isinstance(data, dict) or not month(data.get("month")):
        raise ValueError("Input must be an object with a valid month YYYY-MM.")
    for field in ("orders", "events", "coverage"):
        if not isinstance(data.get(field), list):
            raise ValueError(f"{field} must be an array; missing evidence is not zero.")
    if not isinstance(data.get("responsibilities"), dict):
        raise ValueError("responsibilities must be an object; missing roles may be omitted within it.")
    requested = data["month"]
    responsibilities = data["responsibilities"]
    notices, invalid_orders, lines = [], [], {}
    order_rows = defaultdict(list)
    known_orders = set()

    def followup(kind, action, owner_roles, recipient_roles, supplier=None):
        missing = []

        def resolve(roles):
            values = []
            for role in roles:
                value = supplier if role == "supplier_contact" else responsibilities.get(role)
                if string(value):
                    if value not in values:
                        values.append(value)
                elif role not in missing:
                    missing.append(role)
            return values

        owners = resolve(owner_roles)
        recipients = resolve(recipient_roles)
        address = "; ".join(recipients) or "[recipient information required]"
        return {"kind": kind, "owners": owners, "recipients": recipients,
                "missing_roles": missing, "action": action,
                "draft": f"To: {address}\nSubject: Receiving review {requested}\n\n{action}",
                "ready_to_address": not missing}

    for index, row in enumerate(data["orders"]):
        if isinstance(row, dict) and string(row.get("order_id")):
            known_orders.add(row["order_id"])
        k = key(row)
        if k is None:
            action = f"Reconcile orders record {index}: supply a valid order_id and sku to establish the review scope for {requested}."
            invalid_orders.append({"record_index": index, "issue": "Unidentifiable order line",
                                   "follow_ups": [followup("identity_reconciliation", action,
                                       ["purchasing_coordinator", "data_steward"],
                                       ["purchasing_coordinator", "data_steward"])]})
        else:
            order_rows[k].append((index, row))

    for k, records in order_rows.items():
        indexes = [i for i, _ in records]
        row = records[0][1]
        quantity = row.get("ordered")
        issues = []
        if len({fingerprint(r) for _, r in records}) > 1:
            issues.append({"kind": "identity", "message": f"Conflicting orders records {indexes} for this line."})
            quantity = None
        elif len(records) > 1:
            notices.append(f"Exact repeated orders records {indexes} coalesced.")
        if not integer(quantity) or quantity <= 0:
            issues.append({"kind": "order_data", "message": f"No unambiguous positive integer ordered quantity in orders records {indexes}."})
            quantity = None
        lines[k] = {"order_id": k[0], "sku": k[1], "order_record_indexes": indexes,
                    "ordered": quantity, "coverage": "missing", "observed_net": 0,
                    "accepted_event_ids": [], "issues": issues}

    def issue(keys, kind, message):
        for k in keys:
            item = {"kind": kind, "message": message}
            if item not in lines[k]["issues"]:
                lines[k]["issues"].append(item)

    # Find conflicting IDs before month filtering, so reused IDs cannot silently pass.
    ids = defaultdict(list)
    for index, row in enumerate(data["events"]):
        if isinstance(row, dict) and string(row.get("event_id")):
            ids[row["event_id"]].append((index, row))
    conflicts = {eid: [i for i, _ in records] for eid, records in ids.items()
                 if len({fingerprint(r) for _, r in records}) > 1}
    seen = set()
    for index, row in enumerate(data["events"]):
        if not isinstance(row, dict):
            issue(lines, "event_data", f"Non-object events record {index}; identity and month unknown.")
            continue
        event_month = row.get("event_month")
        if month(event_month) and event_month != requested:
            notices.append(f"Events record {index} excluded: outside requested month.")
            continue
        order_id = row.get("order_id")
        if string(order_id) and order_id not in known_orders:
            notices.append(f"Events record {index} excluded: order outside supplied scope.")
            continue
        if not string(order_id):
            issue(lines, "identity", f"Events record {index} has no valid order_id; cannot attribute current/unknown-month evidence.")
            continue
        k = key(row)
        if k not in lines:
            affected = [line_key for line_key in lines if line_key[0] == order_id]
            issue(affected, "identity", f"Events record {index} identifies unknown/malformed SKU {row.get('sku')!r} on order {order_id}; reconcile this order's receiving identity.")
            if not affected:
                notices.append(f"Events record {index} cannot be assigned to a valid line of supplied order {order_id}; reconcile invalid_orders.")
            continue
        bad = False
        if not month(event_month):
            issue([k], "event_data", f"Events record {index} has invalid/missing event_month; temporal membership unknown.")
            bad = True
        event_id = row.get("event_id")
        if not string(event_id):
            issue([k], "identity", f"Events record {index} has invalid/missing event_id.")
            bad = True
        elif event_id in conflicts:
            issue([k], "identity", f"Conflicting event_id {event_id!r} in events records {conflicts[event_id]}; excluded from subtotal.")
            bad = True
        if not integer(row.get("quantity")):
            issue([k], "event_data", f"Events record {index} has invalid/missing signed integer quantity; excluded from subtotal.")
            bad = True
        if bad:
            continue
        signature = fingerprint(row)
        if signature in seen:
            notices.append(f"Exact repeated events record {index} counted once.")
            continue
        seen.add(signature)
        lines[k]["observed_net"] += row["quantity"]
        lines[k]["accepted_event_ids"].append(event_id)

    declarations = defaultdict(list)
    invalid_coverage = set()
    for index, row in enumerate(data["coverage"]):
        k = key(row)
        if k not in lines:
            notices.append(f"Coverage record {index} ignored: unknown or malformed line identity; cannot establish completeness.")
            continue
        cm = row.get("month")
        if month(cm) and cm != requested:
            notices.append(f"Coverage record {index} ignored: outside requested month.")
            continue
        if not month(cm) or type(row.get("complete")) is not bool:
            invalid_coverage.add(k)
            issue([k], "coverage", f"Coverage record {index} has invalid month or complete declaration.")
        else:
            declarations[k].append((index, row["complete"]))

    for k, line in lines.items():
        flags = {value for _, value in declarations[k]}
        if len(flags) > 1:
            invalid_coverage.add(k)
            issue([k], "coverage", f"Contradictory coverage records {[i for i, _ in declarations[k]]}.")
        line["coverage"] = ("invalid" if k in invalid_coverage else "complete" if flags == {True}
                            else "partial" if flags == {False} else "missing")
        line.update(receipt_position="blocked" if line["issues"] else "not_final",
                    final_net=None, remaining=None, excess=None, follow_ups=[])
        label = f"{requested} order {k[0]}, SKU {k[1]}"
        tasks = line["follow_ups"]
        kinds = {i["kind"] for i in line["issues"]}
        if "identity" in kinds or "order_data" in kinds:
            details = " ".join(i["message"] for i in line["issues"] if i["kind"] in {"identity", "order_data"})
            tasks.append(followup("identity_reconciliation", f"Reconcile source records for {label} before final comparison. {details} Confirm the order quantity and event-to-line identities, then rerun the review.",
                                  ["purchasing_coordinator", "data_steward"], ["purchasing_coordinator", "data_steward"]))
        if "event_data" in kinds:
            details = " ".join(i["message"] for i in line["issues"] if i["kind"] == "event_data")
            tasks.append(followup("evidence_repair", f"Provide corrected receiving evidence for {label}. {details} Confirm signed quantities and requested-month membership, then rerun the review.",
                                  ["data_steward"], ["data_steward"]))
        if line["coverage"] != "complete":
            details = " ".join(i["message"] for i in line["issues"] if i["kind"] == "coverage")
            tasks.append(followup("full_export", f"Provide or confirm the full event export and an explicit complete coverage declaration for {label} before final comparison. Coverage is {line['coverage']}; accepted-event observed subtotal is {line['observed_net']}. {details}".strip(),
                                  ["data_steward"], ["data_steward"]))
        if not line["issues"] and line["coverage"] == "complete":
            net, ordered = line["observed_net"], line["ordered"]
            line["final_net"] = net
            if net == ordered:
                line["receipt_position"] = "received_as_ordered"
            elif net < ordered:
                line["receipt_position"] = "shortfall"
                line["remaining"] = ordered - net
                tasks.append(followup("supplier_shortfall", f"For {label}, complete evidence shows {net} net received against {ordered} ordered. Please confirm the status and expected receipt date of the remaining {ordered - net} units and the next receiving action.",
                                      ["purchasing_coordinator"], ["supplier_contact"], order_rows[k][0][1].get("supplier_contact")))
            else:
                line["receipt_position"] = "excess"
                line["excess"] = net - ordered
                tasks.append(followup("warehouse_excess", f"For {label}, complete evidence shows {net} net received against {ordered} ordered. Reconcile the surplus {net - ordered} units against the order and receiving evidence, and report the cause and proposed correction or disposition.",
                                      ["warehouse_lead"], ["warehouse_lead"]))
    return {"schema_version": 1, "month": requested, "scope_line_count": len(lines),
            "lines": list(lines.values()), "invalid_orders": invalid_orders, "notices": notices}


def unique_object(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(f"Duplicate JSON object key: {name}")
        result[name] = value
    return result


def reject_constant(value):
    raise ValueError(f"Non-finite JSON number: {value}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="UTF-8 JSON input; review JSON is written to stdout, errors to stderr")
    args = parser.parse_args()
    try:
        with open(args.input, encoding="utf-8") as stream:
            data = json.load(stream, object_pairs_hook=unique_object, parse_constant=reject_constant)
        result = review(data)
    except (OSError, UnicodeError, ValueError) as exc:
        print(json.dumps({"error": str(exc), "review_produced": False}), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
