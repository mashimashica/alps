#!/usr/bin/env python3
"""Calculate an evidence-aware monthly receiving review from JSON."""
import json, sys
from collections import defaultdict

def fail(msg):
    raise ValueError(msg)

def main(path):
    with open(path, encoding="utf-8") as f: data=json.load(f)
    month=data.get("month")
    if not isinstance(month,str) or len(month)!=7 or month[4]!="-": fail("month must be YYYY-MM")
    orders=data.get("orders"); events=data.get("events"); coverage=data.get("coverage")
    if not all(isinstance(x,list) for x in (orders,events,coverage)): fail("orders, events, and coverage must be arrays")
    issues=[]; order_map={}; lines=[]
    for o in orders:
        try: key=(o["order_id"],o["sku"]); qty=o["ordered"]
        except (KeyError,TypeError): issues.append({"type":"invalid_order","record":o}); continue
        if not isinstance(qty,int) or isinstance(qty,bool) or qty<=0: issues.append({"type":"invalid_order_quantity","line":list(key)}); continue
        if key in order_map: issues.append({"type":"duplicate_order_line","line":list(key)})
        order_map[key]=o; lines.append(key)
    cov={}
    for c in coverage:
        try:
            k=(c["order_id"],c["sku"],c["month"]); cov[k]=c["complete"]
        except (KeyError,TypeError): issues.append({"type":"invalid_coverage","record":c})
    by_line=defaultdict(list); seen={}; conflicts=set()
    for e in events:
        try: eid=e["event_id"]; key=(e["order_id"],e["sku"])
        except (KeyError,TypeError): issues.append({"type":"invalid_event","record":e}); continue
        fingerprint=tuple((k,e.get(k)) for k in ("order_id","sku","event_month","quantity"))
        if eid in seen and seen[eid]!=fingerprint: conflicts.add(key); issues.append({"type":"conflicting_event_id","event_id":eid})
        elif eid in seen: continue
        else: seen[eid]=fingerprint
        if key not in order_map:
            if key[0] in {k[0] for k in order_map}: issues.append({"type":"identity_mismatch","order_id":key[0],"sku":key[1]})
            else: issues.append({"type":"out_of_scope_event","event_id":eid,"line":list(key)})
            continue
        by_line[key].append(e)
    resp=data.get("responsibilities") if isinstance(data.get("responsibilities"),dict) else {}
    out=[]
    for key in lines:
        o=order_map[key]; ev=[e for e in by_line[key] if e.get("event_month")==month]
        subtotal=sum(e.get("quantity") for e in ev if isinstance(e.get("quantity"),int) and not isinstance(e.get("quantity"),bool))
        invalid=any(not isinstance(e.get("quantity"),int) or isinstance(e.get("quantity"),bool) for e in ev)
        complete=cov.get((key[0],key[1],month),None)
        status="complete" if complete is True else "incomplete_export" if complete is False or complete is None else "invalid_coverage"
        pos="undetermined_conflicting_evidence" if key in conflicts else "undetermined_identity_reconciliation" if any(i.get("type")=="identity_mismatch" and i.get("order_id")==key[0] for i in issues) else "undetermined_invalid_evidence" if invalid or status=="invalid_coverage" else "undetermined_incomplete_export" if status!="complete" else ("received_as_ordered" if subtotal==o["ordered"] else "shortfall" if subtotal<o["ordered"] else "excess")
        recipient=None; follow=None
        if pos=="shortfall": recipient=resp.get("purchasing_coordinator"); follow=f"Ask the supplier contact ({o.get('supplier_contact','supplied contact')}) about the remaining {o['ordered']-subtotal} units."
        elif pos=="excess": recipient=resp.get("warehouse_lead"); follow=f"Reconcile the surplus of {subtotal-o['ordered']} units against the order and receiving evidence."
        elif pos=="undetermined_incomplete_export": recipient=resp.get("data_steward"); follow="Provide or confirm the full receipt export for this order line and month before final comparison."
        elif pos in ("undetermined_identity_reconciliation","undetermined_conflicting_evidence"): recipient=f"{resp.get('purchasing_coordinator','[missing purchasing coordinator]')} and {resp.get('data_steward','[missing data steward]')}"; follow="Reconcile the identified order/event source records before final line comparison."
        out.append({"order_id":key[0],"sku":key[1],"ordered":o["ordered"],"event_count":len(ev),"observed_subtotal":subtotal,"evidence_status":status,"position":pos,"recipient":recipient,"follow_up":follow})
    return {"month":month,"lines":out,"issues":issues}

if __name__=="__main__":
    try: print(json.dumps(main(sys.argv[1]),indent=2,sort_keys=True))
    except (IndexError, OSError, ValueError, json.JSONDecodeError) as e: print(f"error: {e}",file=sys.stderr); sys.exit(2)
