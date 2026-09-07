#!/usr/bin/env python3
"""Deterministically prepare evidence for a monthly receiving review."""
import argparse, json, sys
from collections import defaultdict

REQUIRED_RESP = ("purchasing_coordinator", "warehouse_lead", "data_steward")

def fail(msg):
    raise ValueError(msg)

def main(data):
    if not isinstance(data, dict): fail("input must be a JSON object")
    month = data.get("month")
    if not isinstance(month, str) or len(month) != 7 or month[4] != "-": fail("month must be YYYY-MM")
    orders = data.get("orders"); events = data.get("events"); coverage = data.get("coverage")
    if not isinstance(orders, list) or not isinstance(events, list) or not isinstance(coverage, list): fail("orders, events, and coverage must be arrays")
    resp = data.get("responsibilities")
    if not isinstance(resp, dict): fail("responsibilities must be an object")
    missing_resp = [k for k in REQUIRED_RESP if not isinstance(resp.get(k), str) or not resp[k].strip()]
    if missing_resp: fail("missing responsibility values: " + ", ".join(missing_resp))

    order_map, order_errors = {}, []
    for i, o in enumerate(orders):
        if not isinstance(o, dict): order_errors.append(f"orders[{i}] is not an object"); continue
        key = (o.get("order_id"), o.get("sku"))
        if not all(isinstance(x, str) and x for x in key): order_errors.append(f"orders[{i}] needs order_id and sku"); continue
        q = o.get("ordered")
        if isinstance(q, bool) or not isinstance(q, int) or q <= 0: order_errors.append(f"orders[{i}].ordered must be a positive integer"); continue
        if key in order_map: order_errors.append(f"duplicate order line {key[0]}/{key[1]}"); continue
        order_map[key] = {"order_id": key[0], "sku": key[1], "ordered": q, "supplier_contact": o.get("supplier_contact")}
    if order_errors: fail("; ".join(order_errors))

    # Exact duplicate event objects count once; same ID with differing content conflicts.
    by_id, conflicts, event_errors = {}, set(), []
    for i, e in enumerate(events):
        if not isinstance(e, dict): event_errors.append(f"events[{i}] is not an object"); continue
        for k in ("event_id", "order_id", "sku", "event_month"):
            if not isinstance(e.get(k), str) or not e[k]: event_errors.append(f"events[{i}] missing {k}")
        q = e.get("quantity")
        if isinstance(q, bool) or not isinstance(q, int): event_errors.append(f"events[{i}].quantity must be an integer")
        if any(isinstance(e.get(k), str) and e.get(k) for k in ("event_id", "order_id", "sku", "event_month")) and isinstance(q, int) and not isinstance(q, bool):
            eid = e["event_id"]
            canon = json.dumps(e, sort_keys=True, separators=(",", ":"))
            if eid in by_id and by_id[eid] != canon: conflicts.add(eid)
            else: by_id.setdefault(eid, canon)
    if event_errors: fail("; ".join(event_errors))
    unique_events = [json.loads(s) for s in by_id.values()]
    event_by_line = defaultdict(list)
    for e in unique_events:
        if e["event_month"] == month and (e["order_id"], e["sku"]) in order_map:
            event_by_line[(e["order_id"], e["sku"])].append(e)
    # Any current-month event for an in-scope order but absent SKU is identity evidence.
    identity_issues = defaultdict(list)
    for e in unique_events:
        if e["event_month"] == month and any(k[0] == e["order_id"] for k in order_map) and (e["order_id"], e["sku"]) not in order_map:
            identity_issues[e["order_id"]].append(e["event_id"])

    cov = {}
    for i, c in enumerate(coverage):
        if not isinstance(c, dict): fail(f"coverage[{i}] is not an object")
        key = (c.get("order_id"), c.get("sku"), c.get("month"))
        if key[:2] not in order_map or key[2] != month: continue
        if not isinstance(c.get("complete"), bool): fail(f"coverage[{i}].complete must be boolean")
        cov[key[:2]] = c["complete"]

    lines = []
    for key, o in order_map.items():
        complete = cov.get(key)
        evs = event_by_line.get(key, [])
        out = {**o, "evidence": {"coverage_complete": complete, "event_ids": [e["event_id"] for e in evs], "observed_net_received": sum(e["quantity"] for e in evs)}}
        flags = []
        if complete is None: flags.append("coverage_missing")
        if key[0] in identity_issues: flags.append("identity_reconciliation_needed")
        if any(eid in conflicts for eid in [e["event_id"] for e in evs]): flags.append("conflicting_event_evidence")
        out["evidence"]["flags"] = flags
        if complete is True and not flags:
            net = out["evidence"]["observed_net_received"]
            out["position"] = "received_as_ordered" if net == o["ordered"] else ("shortfall" if net < o["ordered"] else "excess")
        else: out["position"] = "undetermined"
        lines.append(out)
    return {"month": month, "lines": lines, "identity_issues": {k: v for k, v in identity_issues.items()}, "conflicting_event_ids": sorted(conflicts), "responsibilities": resp,
            "notes": ["Events outside the requested month or outside supplied orders are excluded from in-scope totals.", "Observed subtotals are not final positions when evidence is incomplete or flagged."]}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Prepare evidence and positions for a monthly receiving review")
    ap.add_argument("input", nargs="?", help="JSON input path; defaults to stdin")
    args = ap.parse_args()
    try:
        with open(args.input, encoding="utf-8") if args.input else sys.stdin as f: data = json.load(f)
        print(json.dumps(main(data), indent=2, sort_keys=True))
    except (OSError, json.JSONDecodeError, ValueError) as e:
        print(f"receiving-review: {e}", file=sys.stderr); sys.exit(2)
