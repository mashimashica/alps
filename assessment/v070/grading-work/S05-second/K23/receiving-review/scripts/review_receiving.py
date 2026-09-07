#!/usr/bin/env python3
"""Deterministic monthly receiving evidence normalization."""
import json, sys
from collections import defaultdict

def fail(msg):
    raise ValueError(msg)

def main(path):
    with open(path, encoding="utf-8") as f: data = json.load(f)
    month = data.get("month")
    if not isinstance(month, str) or len(month) != 7 or month[4] != "-": fail("month must be YYYY-MM")
    orders = data.get("orders"); events = data.get("events", []); coverage = data.get("coverage", [])
    resp = data.get("responsibilities", {})
    if not isinstance(orders, list) or not isinstance(events, list) or not isinstance(coverage, list): fail("orders, events, and coverage must be arrays")
    keys = [] ; order_map = {}
    for o in orders:
        k=(o.get("order_id"),o.get("sku"))
        if k in order_map: fail(f"duplicate order line: {k}")
        if not isinstance(o.get("ordered"), int) or isinstance(o.get("ordered"), bool) or o["ordered"] <= 0: fail(f"ordered must be a positive integer: {k}")
        order_map[k]=o; keys.append(k)
    scope=set(keys); by_id=defaultdict(list); excluded=[]
    for e in events:
        if not all(x in e for x in ("event_id","order_id","sku","event_month","quantity")): fail("event missing required field")
        if not isinstance(e["quantity"], int) or isinstance(e["quantity"], bool): fail("event quantity must be integer")
        if e["event_month"] != month or e["order_id"] not in {k[0] for k in keys}:
            excluded.append({"event_id":e["event_id"],"reason":"outside requested month or order scope"}); continue
        by_id[e["event_id"]].append(e)
    valid=[]; conflicts=[]; seen=set()
    for eid, rows in by_id.items():
        sigs={json.dumps(r, sort_keys=True, separators=(",",":")) for r in rows}
        if len(sigs)>1:
            conflicts.append({"event_id":eid,"lines":[[r["order_id"],r["sku"]] for r in rows]}); continue
        r=rows[0]; k=(r["order_id"],r["sku"])
        if k in scope: valid.append(r); seen.add(k)
        else:
            excluded.append({"event_id":eid,"reason":"SKU absent from supplied order line","order_id":r["order_id"],"sku":r["sku"]})
    cov={(c.get("order_id"),c.get("sku"),c.get("month")):c for c in coverage}
    order_ids={k[0] for k in keys}; identity_orders={e["order_id"] for e in valid if e["order_id"] in order_ids and (e["order_id"],e["sku"]) not in scope}
    lines=[]
    for k in keys:
        o=order_map[k]; c=cov.get((k[0],k[1],month)); complete=bool(c and c.get("complete") is True)
        qty=sum(e["quantity"] for e in valid if (e["order_id"],e["sku"])==k)
        conflict=any(k in [(x,y) for x,y in z["lines"]] for z in conflicts)
        identity=k[0] in identity_orders
        item={"order_id":k[0],"sku":k[1],"ordered":o["ordered"],"coverage_complete":complete,"observed_subtotal":qty}
        if not complete or conflict or identity:
            item["position"]="undetermined"
            if conflict or identity:
                item["evidence_status"]="identity_conflict"; item["follow_up"]={"recipient":[resp.get("purchasing_coordinator"),resp.get("data_steward")],"draft_action":"Reconcile the identified order/event source records before final line comparison."}
            else:
                item["evidence_status"]="incomplete_export"; item["follow_up"]={"recipient":resp.get("data_steward"),"draft_action":"Provide or confirm the full receiving export for this order line and month."}
        else:
            item["evidence_status"]="complete_valid"; item["net_received"]=qty
            if qty==o["ordered"]: item["position"]="received_as_ordered"; item["follow_up"]=None
            elif qty<o["ordered"]: item["position"]="complete_shortfall"; item["follow_up"]={"recipient":o.get("supplier_contact"),"draft_action":f"Confirm the remaining receipt of {o['ordered']-qty} unit(s) for {k[0]}/{k[1]}."}
            else: item["position"]="complete_excess"; item["follow_up"]={"recipient":resp.get("warehouse_lead"),"draft_action":f"Reconcile the surplus of {qty-o['ordered']} unit(s) for {k[0]}/{k[1]} against order and receiving evidence."}
        lines.append(item)
    return {"scope":{"month":month,"line_count":len(keys)},"lines":lines,"excluded_events":excluded,"issues":{"conflicting_event_ids":conflicts,"identity_conflict_orders":sorted(identity_orders)}}

if __name__ == "__main__":
    try:
        if len(sys.argv)!=2: fail("usage: review_receiving.py INPUT.json")
        print(json.dumps(main(sys.argv[1]), indent=2, sort_keys=True))
    except (OSError, json.JSONDecodeError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr); sys.exit(2)
