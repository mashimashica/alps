#!/usr/bin/env python3
"""Produce a deterministic monthly receiving review report from contract JSON."""
import json, sys

def fail(msg):
    print(json.dumps({"error": msg}, indent=2), file=sys.stderr)
    return 2

def main(argv):
    if len(argv) != 2:
        return fail("usage: review.py INPUT.json (or - for stdin)")
    try:
        with open(0 if argv[1] == "-" else argv[1], encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        return fail(f"cannot read JSON input: {e}")
    if not isinstance(data, dict) or not isinstance(data.get("month"), str):
        return fail("input requires month string")
    month = data["month"]
    orders = data.get("orders", []); events = data.get("events", [])
    coverage = data.get("coverage", []); resp = data.get("responsibilities", {})
    if not all(isinstance(x, list) and all(isinstance(y, dict) for y in x) for x in (orders, events, coverage)):
        return fail("orders, events, and coverage must be arrays of objects")
    key = lambda x: (x.get("order_id"), x.get("sku"))
    order_map = {}; warnings = []
    for o in orders:
        k = key(o)
        if k in order_map: warnings.append(f"duplicate order line: {k}")
        order_map[k] = o
    cov_map = {(c.get("order_id"), c.get("sku"), c.get("month")): c for c in coverage}
    event_groups = {}; unique = {}
    for e in events:
        eid = e.get("event_id")
        frozen = json.dumps(e, sort_keys=True, separators=(",", ":"))
        if eid in unique and unique[eid] != frozen:
            event_groups.setdefault((e.get("order_id"), e.get("sku")), set()).add("conflicting_event_evidence")
            old = json.loads(unique[eid]); event_groups.setdefault((old.get("order_id"), old.get("sku")), set()).add("conflicting_event_evidence")
        else: unique[eid] = frozen
    for e in events:
        eid=e.get("event_id")
        if eid not in unique: continue
        if unique[eid] != json.dumps(e, sort_keys=True, separators=(",", ":")): continue
        k=key(e); event_groups.setdefault(k,set())
    seen_ids=set(); line_reports=[]; in_scope_orders={o.get("order_id") for o in orders}
    for e in events:
        if e.get("order_id") not in in_scope_orders or e.get("event_month") != month: continue
        if e.get("event_id") in seen_ids: continue
        seen_ids.add(e.get("event_id"))
        if key(e) not in order_map: event_groups.setdefault(key(e),set()).add("identity_reconciliation")
    out_scope=[e for e in events if e.get("order_id") not in in_scope_orders]
    for k,o in order_map.items():
        issues=set(event_groups.get(k,set()))
        c=cov_map.get((k[0],k[1],month)); complete = c.get("complete") if c else None
        vals=[]; ids=set(); invalid=False
        for e in events:
            if key(e)==k and e.get("event_month")==month and e.get("event_id") not in ids:
                ids.add(e.get("event_id")); q=e.get("quantity")
                if isinstance(q,(int,float)) and not isinstance(q,bool): vals.append(q)
                else: invalid=True
        observed=sum(vals) if vals else (None if invalid or not vals else 0)
        if invalid: issues.add("invalid_quantity")
        if complete is True and not issues:
            if observed is None: status="missing_received_value"
            elif observed==o.get("ordered"): status="received_as_ordered"
            elif observed<o.get("ordered"): status="complete_shortfall"
            else: status="complete_excess"
        elif "identity_reconciliation" in issues or "conflicting_event_evidence" in issues: status="identity_reconciliation" if "identity_reconciliation" in issues else "conflicting_event_evidence"
        elif complete is not True: status="incomplete_export"
        else: status="evidence_issue"
        recipient=None; action=None
        if status=="complete_shortfall": recipient=resp.get("purchasing_coordinator"); action=f"Ask {recipient or 'the supplied supplier contact'} about the remaining receipt for {k[0]}/{k[1]}."
        elif status=="complete_excess": recipient=resp.get("warehouse_lead"); action=f"Ask {recipient or 'the supplied warehouse lead'} to reconcile the surplus for {k[0]}/{k[1]} against order and receiving evidence."
        elif status=="incomplete_export": recipient=resp.get("data_steward"); action=f"Ask {recipient or 'the supplied data steward'} to provide or confirm the full export for {k[0]}/{k[1]} for {month}."
        elif status in ("identity_reconciliation","conflicting_event_evidence"): recipient=resp.get("purchasing_coordinator"); action=f"Ask {recipient or 'the supplied purchasing coordinator'} and {resp.get('data_steward') or 'the supplied data steward'} to reconcile the identified source records for {k[0]}/{k[1]}."
        line_reports.append({"order_id":k[0],"sku":k[1],"ordered":o.get("ordered"),"observed_received":observed,"status":status,"evidence_issues":sorted(issues),"follow_up":{"recipient":recipient,"draft":action} if action else None})
    print(json.dumps({"month":month,"scope":[{"order_id":k[0],"sku":k[1]} for k in order_map],"lines":line_reports,"out_of_scope_events":out_scope,"warnings":warnings}, indent=2, sort_keys=True))
    return 0
if __name__ == "__main__": sys.exit(main(sys.argv))
