#!/usr/bin/env python3
"""Deterministic evidence processing for the receiving-review Skill."""
import json, sys
from collections import defaultdict

def fail(msg):
    print(json.dumps({"validation_errors": [msg], "lines": [], "follow_ups": [], "issues": []}, indent=2))
    return 2

def main(path):
    try:
        with open(path, encoding="utf-8") as f: d = json.load(f)
    except Exception as e: return fail(f"cannot read JSON input: {e}")
    errs=[]
    month=d.get("month")
    if not isinstance(month,str) or len(month)!=7 or month[4]!="-": errs.append("month must be YYYY-MM")
    for k in ("orders","events","coverage","responsibilities"):
        if k not in d: errs.append(f"missing {k}")
    orders=d.get("orders",[]); events=d.get("events",[]); coverage=d.get("coverage",[])
    if not isinstance(orders,list) or not isinstance(events,list) or not isinstance(coverage,list): errs.append("orders, events, and coverage must be arrays")
    if errs: return fail("; ".join(errs))
    om={}; order_skus=defaultdict(set)
    for i,o in enumerate(orders):
        if not isinstance(o,dict): errs.append(f"orders[{i}] must be object"); continue
        key=(o.get("order_id"),o.get("sku")); q=o.get("ordered")
        if not isinstance(q,int) or isinstance(q,bool) or q<=0: errs.append(f"orders[{i}].ordered must be a positive integer")
        if key in om: errs.append(f"duplicate order line {key}")
        om[key]=o; order_skus[key[0]].add(key[1])
    if errs: return fail("; ".join(errs))
    # Keep all event records by ID to detect content conflicts; exact duplicates count once.
    byid=defaultdict(list)
    for i,e in enumerate(events):
        if not isinstance(e,dict): errs.append(f"events[{i}] must be object"); continue
        for x in ("event_id","order_id","sku","event_month","quantity"):
            if x not in e: errs.append(f"events[{i}] missing {x}")
        if not isinstance(e.get("quantity"),int) or isinstance(e.get("quantity"),bool): errs.append(f"events[{i}].quantity must be integer")
        byid[e.get("event_id")].append(e)
    cov={}
    for i,c in enumerate(coverage):
        if not isinstance(c,dict): errs.append(f"coverage[{i}] must be object"); continue
        key=(c.get("order_id"),c.get("sku"),c.get("month"))
        if key in cov and cov[key] != c: errs.append(f"conflicting coverage for {key}")
        cov[key]=c
    if errs: return fail("; ".join(errs))
    conflict_ids={eid for eid,rows in byid.items() if len({json.dumps(x,sort_keys=True) for x in rows})>1}
    unique=[]
    for eid,rows in byid.items():
        unique.append(rows[0])
    subtotal=defaultdict(int); relevant_events=defaultdict(list); issues=defaultdict(list); identity_orders=set()
    for e in unique:
        key=(e["order_id"],e["sku"])
        if e["event_id"] in conflict_ids:
            if e["event_month"]==month and e["order_id"] in order_skus: issues[key].append(f"conflicting content for event_id {e['event_id']}")
            continue
        if e["event_month"] != month: continue
        if e["order_id"] not in order_skus: continue
        relevant_events[key].append(e["event_id"])
        if key not in om:
            identity_orders.add(e["order_id"])
            issues[key].append("event SKU is absent from the supplied order")
        else: subtotal[key]+=e["quantity"]
    lines=[]; follow=[]; allissues=[]
    resp=d.get("responsibilities",{})
    for key,o in om.items():
        covr=cov.get((key[0],key[1],month)); complete=isinstance(covr,dict) and covr.get("complete") is True
        li=list(issues.get(key,[])); evs=relevant_events.get(key,[])
        if covr is None: li.append("no coverage declaration for requested month")
        elif covr.get("complete") is not True: li.append("receiving export is not confirmed complete")
        if key[0] in identity_orders: li.append("order/event identity reconciliation required")
        status="undetermined"
        if complete and not li:
            n=subtotal.get(key,0); q=o["ordered"]
            status="received as ordered" if n==q else ("shortfall" if n<q else "excess")
        line={"order_id":key[0],"sku":key[1],"ordered":o["ordered"],"event_ids":evs,"evidence_issues":sorted(set(li)),"evidence_complete":complete and not li,"observed_net_received":subtotal.get(key) if evs and not li else (subtotal.get(key) if evs else None),"position":status}
        lines.append(line)
        if status=="shortfall": rec=o.get("supplier_contact"); action=f"Ask the supplier contact to confirm the remaining {o['ordered']-subtotal[key]} unit(s) for {key[0]} / {key[1]}."
        elif status=="excess": rec=resp.get("warehouse_lead"); action=f"Reconcile the {subtotal[key]-o['ordered']} unit surplus for {key[0]} / {key[1]} against the order and receiving evidence."
        elif not (complete and not li):
            rec=resp.get("data_steward") if not any("identity" in x or "conflicting content" in x for x in li) else ", ".join(x for x in (resp.get("purchasing_coordinator"),resp.get("data_steward")) if x)
            action=f"Provide or confirm the full {month} export for {key[0]} / {key[1]} before making the final receipt comparison." if rec==resp.get("data_steward") else f"Reconcile the identified order/event source records for {key[0]} / {key[1]} before comparing receipts."
        else: rec=None; action=None
        if action: follow.append({"order_id":key[0],"sku":key[1],"recipient":rec,"draft":action})
        allissues.extend({"order_id":key[0],"sku":key[1],"issue":x} for x in sorted(set(li)))
    return_code=0
    print(json.dumps({"month":month,"lines":lines,"follow_ups":follow,"issues":allissues,"validation_errors":[]},indent=2))
    return return_code

if __name__=="__main__": sys.exit(main(sys.argv[1]) if len(sys.argv)==2 else fail("usage: review_receipts.py INPUT.json"))
