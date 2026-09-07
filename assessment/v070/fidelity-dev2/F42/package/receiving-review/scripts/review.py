#!/usr/bin/env python3
"""Deterministic monthly receiving evidence processor."""
import argparse, json, sys

def main(data):
    errors=[]; warnings=[]
    month=data.get("month") if isinstance(data,dict) else None
    if not isinstance(month,str) or len(month)!=7 or month[4]!="-" or not month[:4].isdigit() or not month[5:].isdigit():
        errors.append("month must be YYYY-MM")
    orders=data.get("orders",[]) if isinstance(data,dict) else []
    events=data.get("events",[]) if isinstance(data,dict) else []
    coverage=data.get("coverage",[]) if isinstance(data,dict) else []
    resp=data.get("responsibilities",{}) if isinstance(data,dict) else {}
    if not isinstance(orders,list) or not isinstance(events,list) or not isinstance(coverage,list) or not isinstance(resp,dict):
        errors.append("orders, events, coverage must be arrays and responsibilities an object")
        return {"ok":False,"errors":errors,"warnings":warnings,"scope":{},"lines":[],"out_of_scope_events":[]}
    lines={}; order_skus={}
    for i,o in enumerate(orders):
        if not isinstance(o,dict): errors.append(f"orders[{i}] must be an object"); continue
        k=(o.get("order_id"),o.get("sku")); q=o.get("ordered")
        if not isinstance(k[0],str) or not isinstance(k[1],str) or not k[0] or not k[1]: errors.append(f"orders[{i}] missing order_id or sku"); continue
        if not isinstance(q,int) or isinstance(q,bool) or q<=0: errors.append(f"orders[{i}].ordered must be a positive integer"); continue
        if k in lines: errors.append(f"duplicate order line: {k[0]}/{k[1]}"); continue
        lines[k]={"order_id":k[0],"sku":k[1],"ordered":q,"supplier_contact":o.get("supplier_contact"),"events":[],"coverage_complete":None,"gaps":[],"flags":[]}
        order_skus.setdefault(k[0],set()).add(k[1])
    cov={}
    for i,c in enumerate(coverage):
        if not isinstance(c,dict): errors.append(f"coverage[{i}] must be an object"); continue
        k=(c.get("order_id"),c.get("sku")); key=(k[0],k[1],c.get("month"))
        if k in lines and c.get("month")==month:
            if key in cov and cov[key] != c.get("complete"): errors.append(f"conflicting coverage for {k[0]}/{k[1]}")
            cov[key]=c.get("complete")
    for k,line in lines.items(): line["coverage_complete"]=cov.get((k[0],k[1],month))
    seen={}; valid_events=[]; out=[]
    for i,e in enumerate(events):
        if not isinstance(e,dict): errors.append(f"events[{i}] must be an object"); continue
        eid=e.get("event_id"); k=(e.get("order_id"),e.get("sku")); q=e.get("quantity")
        if not isinstance(eid,str) or not eid: errors.append(f"events[{i}] missing event_id"); continue
        if not isinstance(q,int) or isinstance(q,bool): errors.append(f"events[{i}].quantity must be an integer"); continue
        frozen=tuple((x,e.get(x)) for x in ("event_id","order_id","sku","event_month","quantity"))
        if eid in seen:
            if seen[eid]!=frozen: 
                for lk in lines:
                    if lk[0]==k[0] or lk==(seen[eid][1],seen[eid][2]): lines[lk]["flags"].append("conflicting event content for event_id "+eid)
            continue
        seen[eid]=frozen
        if e.get("event_month")!=month: continue
        if k not in lines:
            if k[0] in order_skus: warnings.append(f"current-month event {eid} has SKU absent from order {k[0]}");
            else: out.append(eid)
            if k[0] in order_skus:
                for lk in lines:
                    if lk[0]==k[0]: lines[lk]["flags"].append("order/SKU identity reconciliation required")
            continue
        lines[k]["events"].append((eid,q)); valid_events.append(eid)
    result_lines=[]
    for k,l in lines.items():
        subtotal=sum(q for _,q in l["events"]); l["observed_subtotal"]=subtotal
        if l["coverage_complete"] is not True: status="incomplete export"; l["gaps"].append("coverage is not explicitly complete")
        elif l["flags"]: status="conflicting evidence"; l["gaps"].extend(l["flags"])
        elif subtotal==l["ordered"]: status="received as ordered"
        elif subtotal<l["ordered"]: status="complete shortfall"
        else: status="complete excess"
        if l["coverage_complete"] is True and l["flags"]: l["gaps"].extend(x for x in l["flags"] if x not in l["gaps"])
        f=[]
        if status=="complete shortfall": f=[{"recipient":l["supplier_contact"],"action":f"Draft request for the remaining {l['ordered']-subtotal} unit(s) on {l['order_id']}/{l['sku']}."}] if l["supplier_contact"] else [{"recipient":None,"action":"Blocked: supplier_contact is missing; request the remaining receipt."}]
        elif status=="complete excess": f=[{"recipient":resp.get("warehouse_lead"),"action":f"Draft reconciliation of the {subtotal-l['ordered']} excess unit(s) against {l['order_id']}/{l['sku']} and receiving evidence."}]
        elif status=="incomplete export": f=[{"recipient":resp.get("data_steward"),"action":"Draft request to provide or confirm the full receiving export before final comparison."}]
        elif status=="conflicting evidence": f=[{"recipient":resp.get("purchasing_coordinator"),"action":"Draft request to reconcile the identified order/event source records."},{"recipient":resp.get("data_steward"),"action":"Draft request to reconcile the identified order/event source records."}]
        l["status"]=status; l["evidence_gaps"]=sorted(set(l["gaps"])); l["follow_ups"]=f; l["event_ids"]=[x for x,_ in l["events"]]
        l.pop("events"); result_lines.append(l)
    return {"ok":not errors,"errors":errors,"warnings":warnings,"scope":{"month":month,"line_count":len(result_lines)},"lines":result_lines,"out_of_scope_events":out}

if __name__=="__main__":
    ap=argparse.ArgumentParser(description="Review monthly receiving evidence"); ap.add_argument("input"); ap.add_argument("--pretty",action="store_true"); a=ap.parse_args()
    try:
        with open(a.input,encoding="utf-8") as f: data=json.load(f)
        result=main(data); print(json.dumps(result,indent=2 if a.pretty else None,ensure_ascii=False))
        sys.exit(0 if result["ok"] else 2)
    except (OSError,json.JSONDecodeError) as e: print(json.dumps({"ok":False,"errors":[str(e)]}),file=sys.stderr); sys.exit(2)
