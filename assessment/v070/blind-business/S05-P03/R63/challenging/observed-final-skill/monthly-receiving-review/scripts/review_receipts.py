#!/usr/bin/env python3
"""Deterministic monthly receiving evidence processor."""
import argparse, json, sys

def fail(msg):
    raise ValueError(msg)

def main(path):
    with open(path, encoding="utf-8") as f: data=json.load(f)
    if not isinstance(data, dict): fail("input must be an object")
    month=data.get("month")
    orders=data.get("orders"); events=data.get("events", []); coverage=data.get("coverage", [])
    resp=data.get("responsibilities", {})
    if not isinstance(month,str) or len(month)!=7 or month[4]!="-": fail("month must be YYYY-MM")
    if not isinstance(orders,list) or not isinstance(events,list) or not isinstance(coverage,list): fail("orders, events and coverage must be arrays")
    key=lambda x:(x.get("order_id"),x.get("sku"))
    om={}
    for o in orders:
        if not isinstance(o,dict) or not isinstance(o.get("order_id"),str) or not isinstance(o.get("sku"),str) or not isinstance(o.get("ordered"),int) or o["ordered"]<=0: fail("each order needs positive integer ordered and string order_id/sku")
        k=key(o)
        if k in om: fail("duplicate order line: %s/%s"%k)
        om[k]=o
    cm={}
    for c in coverage:
        if isinstance(c,dict) and c.get("month")==month: cm[key(c)]=c
    seen={}; conflicts=[]; in_scope_identity={}
    for e in events:
        if not isinstance(e,dict): fail("event must be object")
        required=("event_id","order_id","sku","event_month","quantity")
        if any(x not in e for x in required) or not isinstance(e["quantity"],int): fail("event missing required fields or integer quantity")
        eid=e["event_id"]
        if eid in seen and seen[eid] != e: conflicts.append({"event_id":eid,"events":[seen[eid],e]})
        else: seen[eid]=e
        if e["event_month"]==month and e["order_id"] in {k[0] for k in om}: in_scope_identity.setdefault(e["order_id"],set()).add(e["sku"])
    report=[]
    for k,o in om.items():
        relevant=[e for eid,e in seen.items() if e.get("event_month")==month and key(e)==k]
        subtotal=sum(e["quantity"] for e in relevant)
        cov=cm.get(k); complete=bool(cov and cov.get("complete") is True)
        order_skus={sku for (oid,sku) in om if oid==k[0]}
        identity_conflict=any(sku not in order_skus for sku in in_scope_identity.get(k[0], set()))
        line={"order_id":k[0],"sku":k[1],"ordered":o["ordered"],"observed_net_received":subtotal,"evidence":{"coverage_complete":complete,"event_count":len(relevant),"conflicting_event_ids":[c["event_id"] for c in conflicts if any(x.get("order_id")==k[0] and x.get("sku")==k[1] for x in c["events"])]}}
        if identity_conflict: line.update(position="unavailable", evidence_status="identity_conflict", follow_up={"recipients":[resp.get("purchasing_coordinator"),resp.get("data_steward")],"action":"Reconcile the identified order/SKU source records before final comparison."})
        elif line["evidence"]["conflicting_event_ids"]: line.update(position="unavailable", evidence_status="conflicting_event_evidence", follow_up={"recipients":[resp.get("purchasing_coordinator"),resp.get("data_steward")],"action":"Reconcile conflicting event source records before final comparison."})
        elif not complete: line.update(position="unavailable", evidence_status="incomplete_export", follow_up={"recipients":[resp.get("data_steward")],"action":"Provide or confirm the full receiving export for this order line and month."})
        else:
            pos="received_as_ordered" if subtotal==o["ordered"] else ("shortfall" if subtotal<o["ordered"] else "excess")
            line["position"]=pos; line["evidence_status"]="complete"
            if pos=="shortfall": line["follow_up"]={"recipients":[o.get("supplier_contact")],"action":"Confirm and arrange receipt of the remaining quantity."}
            elif pos=="excess": line["follow_up"]={"recipients":[resp.get("warehouse_lead")],"action":"Reconcile the surplus against the order and receiving evidence."}
            else: line["follow_up"]=None
        report.append(line)
    return {"month":month,"lines":report,"conflicts":conflicts}

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("input"); a=p.parse_args()
    try: print(json.dumps(main(a.input), indent=2, sort_keys=True))
    except (OSError, json.JSONDecodeError, ValueError) as e: print("error: "+str(e), file=sys.stderr); sys.exit(2)
