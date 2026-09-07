#!/usr/bin/env python3
"""Deterministic evidence processing for monthly receiving review."""
import json, sys

def fail(msg):
    print(json.dumps({"status":"error","error":msg}), file=sys.stderr)
    raise SystemExit(2)

def main(path):
    try:
        with open(path, encoding="utf-8") as f: d=json.load(f)
    except Exception as e: fail(f"cannot read JSON: {e}")
    if not isinstance(d,dict): fail("input must be an object")
    month=d.get("month")
    if not isinstance(month,str) or len(month)!=7 or month[4]!="-": fail("month must be YYYY-MM")
    for k in ("orders","events","coverage","responsibilities"):
        if k not in d: fail(f"missing field: {k}")
    orders=d["orders"]; events=d["events"]; cov=d["coverage"]
    if not all(isinstance(x,dict) for x in orders+events+cov): fail("orders/events/coverage entries must be objects")
    lines={}; errors=[]
    for o in orders:
        key=(o.get("order_id"),o.get("sku"))
        if not isinstance(o.get("order_id"),str) or not isinstance(o.get("sku"),str) or not isinstance(o.get("ordered"),int) or o["ordered"]<=0: errors.append({"type":"invalid_order","order":o}); continue
        if key in lines: errors.append({"type":"duplicate_order_line","key":key}); continue
        lines[key]=o
    # Same event id with differing content is conflict; exact copies count once.
    byid={}; conflict_ids=set()
    for e in events:
        if not isinstance(e.get("event_id"),str) or not isinstance(e.get("order_id"),str) or not isinstance(e.get("sku"),str) or not isinstance(e.get("event_month"),str) or not isinstance(e.get("quantity"),int):
            errors.append({"type":"invalid_event","event":e}); continue
        sig=tuple((k,e.get(k)) for k in ("event_id","order_id","sku","event_month","quantity"))
        if e["event_id"] in byid and byid[e["event_id"]]!=sig: conflict_ids.add(e["event_id"])
        else: byid.setdefault(e["event_id"],sig)
    seen=set(); unique=[]
    for e in events:
        eid=e.get("event_id")
        if eid in seen or eid in conflict_ids or not isinstance(eid,str): continue
        seen.add(eid); unique.append(e)
    out=[]
    for key,o in lines.items():
        oid,sku=key; applicable=[e for e in unique if e["order_id"]==oid and e["sku"]==sku and e["event_month"]==month]
        conflict=[e for e in events if e.get("event_id") in conflict_ids and (e.get("order_id")==oid or e.get("sku")==sku)]
        foreign_sku=[e for e in unique if e["order_id"]==oid and e["event_month"]==month and (e["order_id"],e["sku"]) not in lines]
        c=[x for x in cov if x.get("order_id")==oid and x.get("sku")==sku and x.get("month")==month]
        complete=(c[0].get("complete") if c and isinstance(c[0].get("complete"),bool) else None)
        subtotal=sum(e["quantity"] for e in applicable)
        if conflict: status="conflicting_event"
        elif foreign_sku: status="identity_reconciliation"
        elif complete is not True: status="incomplete_export"
        elif subtotal==o["ordered"]: status="received_as_ordered"
        elif subtotal<o["ordered"]: status="shortfall"
        else: status="excess"
        row={"order_id":oid,"sku":sku,"ordered":o["ordered"],"observed_subtotal":subtotal,"coverage_complete":complete,"status":status,"event_ids":[e["event_id"] for e in applicable]}
        if status=="shortfall": row["follow_up"]={"recipient_role":"supplier_contact","recipient":o.get("supplier_contact"),"action":f"Confirm remaining receipt of {o['ordered']-subtotal} units for {oid}/{sku}."}
        elif status=="excess": row["follow_up"]={"recipient_role":"warehouse_lead","recipient":d["responsibilities"].get("warehouse_lead"),"action":f"Reconcile surplus of {subtotal-o['ordered']} units for {oid}/{sku} against order and receiving evidence."}
        elif status=="incomplete_export": row["follow_up"]={"recipient_role":"data_steward","recipient":d["responsibilities"].get("data_steward"),"action":f"Provide or confirm the full {month} receipt export for {oid}/{sku} before final comparison."}
        elif status in ("identity_reconciliation","conflicting_event"): row["follow_up"]={"recipient_roles":["purchasing_coordinator","data_steward"],"recipients":[d["responsibilities"].get("purchasing_coordinator"),d["responsibilities"].get("data_steward")],"action":f"Reconcile the identified source records for {oid}/{sku} before final line comparison."}
        out.append(row)
    return {"status":"ok","month":month,"line_count":len(lines),"lines":out,"input_issues":errors}

if __name__=="__main__":
    if len(sys.argv)!=2: fail("usage: monthly_review.py INPUT.json")
    print(json.dumps(main(sys.argv[1]), indent=2, sort_keys=True))
