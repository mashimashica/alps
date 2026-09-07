#!/usr/bin/env python3
"""Deterministic evidence preparation for the monthly receiving-review Skill."""
import json, sys
from pathlib import Path

def fail(msg):
    print(f"error: {msg}", file=sys.stderr); raise SystemExit(2)

def main(path):
    try: data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as e: fail(f"cannot read JSON: {e}")
    if not isinstance(data, dict): fail("top-level JSON must be an object")
    month = data.get("month")
    if not isinstance(month, str) or len(month) != 7 or month[4] != "-": fail("month must be YYYY-MM")
    orders = data.get("orders"); events = data.get("events", []); coverage = data.get("coverage", [])
    if not isinstance(orders, list) or not isinstance(events, list) or not isinstance(coverage, list): fail("orders, events, and coverage must be arrays")
    key = lambda x: (x.get("order_id"), x.get("sku"))
    order_map = {}
    for o in orders:
        if not isinstance(o, dict) or not isinstance(o.get("order_id"), str) or not isinstance(o.get("sku"), str) or not isinstance(o.get("ordered"), int) or o["ordered"] <= 0: fail("each order needs string order_id/sku and positive integer ordered")
        k=key(o)
        if k in order_map: fail(f"duplicate order line {k}")
        order_map[k]=o
    cov={}
    for c in coverage:
        if not isinstance(c, dict) or c.get("month") != month: continue
        cov[key(c)] = c.get("complete")
    byline={k:[] for k in order_map}; conflicts=[]; seen={}
    identity=[]; outscope=[]
    for e in events:
        if not isinstance(e, dict): fail("each event must be an object")
        eid=e.get("event_id"); ek=key(e)
        if not isinstance(eid, str) or not isinstance(e.get("order_id"), str) or not isinstance(e.get("sku"), str) or not isinstance(e.get("event_month"), str) or not isinstance(e.get("quantity"), int): fail("event has invalid fields")
        signature=(e.get("order_id"),e.get("sku"),e.get("event_month"),e.get("quantity"))
        if eid in seen and seen[eid] != signature: conflicts.append({"event_id":eid,"contents":[seen[eid],signature]})
        if eid in seen: continue
        seen[eid]=signature
        if e["order_id"] not in {k[0] for k in order_map}: outscope.append(eid); continue
        if ek not in order_map: identity.append({"event_id":eid,"order_id":e["order_id"],"sku":e["sku"]}); continue
        if e["event_month"] == month: byline[ek].append(e)
    lines=[]
    for k,o in order_map.items():
        ev=byline[k]; subtotal=sum(e["quantity"] for e in ev); complete=cov.get(k)
        issues=[]
        if complete is not True: issues.append("coverage is absent or incomplete; final position is not established")
        if any(c["event_id"]==e["event_id"] for c in conflicts for e in ev): issues.append("event ID has conflicting content")
        if complete is True and not issues:
            status="received_as_ordered" if subtotal==o["ordered"] else "complete_shortfall" if subtotal<o["ordered"] else "complete_excess"
        else: status="incomplete_evidence"
        lines.append({"order_id":k[0],"sku":k[1],"ordered":o["ordered"],"event_ids":[e["event_id"] for e in ev],"observed_subtotal":subtotal,"coverage_complete":complete is True,"status":status,"evidence_gaps":issues,"supplier_contact":o.get("supplier_contact")})
    print(json.dumps({"month":month,"lines":lines,"identity_reconciliation":identity,"conflicting_events":conflicts,"out_of_scope_event_ids":outscope,"responsibilities":data.get("responsibilities",{})},indent=2,sort_keys=True))

if __name__ == "__main__":
    if len(sys.argv)!=2: fail("usage: review_receipts.py INPUT.json")
    main(sys.argv[1])
