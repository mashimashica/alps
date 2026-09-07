#!/usr/bin/env python3
"""Deterministic monthly receiving review. Reads JSON path or stdin; writes JSON."""
import json, sys
from collections import defaultdict

def err(msg, errors): errors.append(msg)

def main(obj):
    errors=[]
    if not isinstance(obj,dict): return {"status":"invalid_input","errors":["input must be an object"]}
    month=obj.get("month"); orders=obj.get("orders"); events=obj.get("events"); coverage=obj.get("coverage"); resp=obj.get("responsibilities")
    if not isinstance(month,str): err("month must be a string",errors)
    if not isinstance(orders,list): err("orders must be an array",errors); orders=[]
    if not isinstance(events,list): err("events must be an array",errors); events=[]
    if not isinstance(coverage,list): err("coverage must be an array",errors); coverage=[]
    if not isinstance(resp,dict): err("responsibilities must be an object",errors); resp={}
    lines={}; order_skus=defaultdict(set)
    for i,o in enumerate(orders):
        if not isinstance(o,dict): err(f"orders[{i}] must be an object",errors); continue
        key=(o.get("order_id"),o.get("sku")); q=o.get("ordered")
        if not all(isinstance(x,str) and x for x in key): err(f"orders[{i}] needs order_id and sku",errors); continue
        if not isinstance(q,int) or isinstance(q,bool) or q<=0: err(f"orders[{i}].ordered must be a positive integer",errors); continue
        if key in lines: err(f"duplicate order line {key[0]}/{key[1]}",errors)
        lines[key]={"order_id":key[0],"sku":key[1],"ordered":q,"supplier_contact":o.get("supplier_contact"),"evidence":[]}
        order_skus[key[0]].add(key[1])
    cov={}
    for i,c in enumerate(coverage):
        if not isinstance(c,dict): err(f"coverage[{i}] must be an object",errors); continue
        k=(c.get("order_id"),c.get("sku"),c.get("month")); cov[k]=c.get("complete")
    seen={}; valid_events=[]; issues=[]
    for i,e in enumerate(events):
        if not isinstance(e,dict): err(f"events[{i}] must be an object",errors); continue
        required=[e.get("event_id"),e.get("order_id"),e.get("sku"),e.get("event_month")]
        if not all(isinstance(x,str) and x for x in required) or not isinstance(e.get("quantity"),int) or isinstance(e.get("quantity"),bool):
            err(f"events[{i}] has invalid required fields",errors); continue
        eid=e["event_id"]; signature=tuple(e.get(k) for k in ("event_id","order_id","sku","event_month","quantity"))
        if eid in seen:
            if seen[eid]!=signature: issues.append({"type":"conflicting_event_id","event_id":eid,"message":"same event_id has different content"})
            continue
        seen[eid]=signature; valid_events.append(e)
    totals=defaultdict(int); counts=defaultdict(int); conflict_keys=set()
    for issue in issues:
        for e in valid_events:
            if e["event_id"]==issue["event_id"]: conflict_keys.add((e["order_id"],e["sku"]))
    for e in valid_events:
        k=(e["order_id"],e["sku"])
        if e["event_month"]==month and k in lines: totals[k]+=e["quantity"]; counts[k]+=1
        if e["event_month"]==month and e["order_id"] in order_skus and e["sku"] not in order_skus[e["order_id"]]:
            issues.append({"type":"identity_mismatch","order_id":e["order_id"],"sku":e["sku"],"message":"current-month event SKU is absent from supplied order"})
    follow=[]; output=[]
    for k,line in lines.items():
        complete=cov.get((k[0],k[1],month)); evidence=[]
        if complete is None: evidence.append("coverage missing for requested month")
        elif complete is not True and complete is not False: evidence.append("coverage complete must be boolean")
        if k in conflict_keys: evidence.append("event_id content conflict affects this line")
        observed=totals.get(k,0); rec=dict(line); rec["observed_subtotal"]=observed; rec["event_count"]=counts.get(k,0)
        if evidence or complete is not True:
            rec["status"]="incomplete_evidence"; rec["evidence"]=evidence or ["manifest marks export incomplete"]
            recipient=resp.get("data_steward"); action="Provide or confirm the full receipt export before making the final comparison."
        elif k in conflict_keys:
            rec["status"]="identity_reconciliation_required"; rec["evidence"]=evidence
            recipient=resp.get("purchasing_coordinator"); action="Reconcile the conflicting order/event source records with the data steward before final comparison." 
        else:
            rec["net_received"]=observed
            if observed==line["ordered"]: rec["status"]="received_as_ordered"; recipient=None; action=None
            elif observed<line["ordered"]: rec["status"]="complete_shortfall"; recipient=resp.get("supplier_contact") or line.get("supplier_contact") or resp.get("purchasing_coordinator"); action=f"Follow up on the remaining {line['ordered']-observed} units with the supplier contact."
            else: rec["status"]="complete_excess"; recipient=resp.get("warehouse_lead"); action=f"Reconcile the surplus of {observed-line['ordered']} units against the order and receiving evidence."
            rec["evidence"]=["coverage marks current-month export complete"]
        if recipient and action: follow.append({"order_id":k[0],"sku":k[1],"recipient":recipient,"draft":action})
        output.append(rec)
    return {"status":"invalid_input" if errors else "ok","month":month,"lines":output,"issues":issues,"follow_ups":follow,**({"errors":errors} if errors else {})}

if __name__=="__main__":
    try:
        raw=sys.stdin.read() if len(sys.argv)==1 else open(sys.argv[1],encoding="utf-8").read()
        print(json.dumps(main(json.loads(raw)),indent=2,sort_keys=True))
    except (OSError,json.JSONDecodeError) as e:
        print(json.dumps({"status":"invalid_input","errors":[str(e)]},indent=2)); sys.exit(2)
