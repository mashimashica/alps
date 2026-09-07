#!/usr/bin/env python3
"""Deterministic evidence processing for monthly receiving review."""
import json, sys
from collections import defaultdict
from pathlib import Path

def fail(msg):
    print(json.dumps({"error": msg}, ensure_ascii=False), file=sys.stderr)
    raise SystemExit(2)

def main(argv):
    if len(argv) not in (2, 3): fail("usage: review_receiving.py INPUT.json [OUTPUT.json]")
    try: data=json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except Exception as e: fail(f"cannot read JSON: {e}")
    if not isinstance(data, dict): fail("input must be an object")
    for k in ("month","orders","events","coverage","responsibilities"):
        if k not in data: fail(f"missing required field: {k}")
    month=data["month"]
    if not isinstance(month,str) or len(month)!=7 or month[4]!="-": fail("month must be YYYY-MM")
    orders=data["orders"]; events=data["events"]; cov=data["coverage"]
    if not all(isinstance(x,list) for x in (orders,events,cov)): fail("orders, events, coverage must be arrays")
    lines={};
    for o in orders:
        if not isinstance(o,dict) or not isinstance(o.get("order_id"),str) or not isinstance(o.get("sku"),str): fail("each order needs order_id and sku")
        if not isinstance(o.get("ordered"),int) or isinstance(o.get("ordered"),bool) or o["ordered"]<=0: fail(f"invalid ordered quantity for {o.get('order_id')}/{o.get('sku')}")
        key=(o["order_id"],o["sku"])
        if key in lines: fail(f"duplicate order line: {key[0]}/{key[1]}")
        lines[key]=o
    seen={}; conflicts=[]; relevant=defaultdict(list); out_scope=[]; identity=[]
    for e in events:
        if not isinstance(e,dict) or not all(isinstance(e.get(k),str) for k in ("event_id","order_id","sku","event_month")) or not isinstance(e.get("quantity"),(int,float)) or isinstance(e.get("quantity"),bool): fail("invalid event")
        eid=e["event_id"]; canonical=json.dumps(e,sort_keys=True,separators=(",",":"))
        if eid in seen:
            if seen[eid]!=canonical: conflicts.append({"event_id":eid,"details":"same event_id has different content"})
            continue
        seen[eid]=canonical
        key=(e["order_id"],e["sku"])
        if e["event_month"]==month and e["order_id"] not in {k[0] for k in lines}: out_scope.append(eid)
        if e["event_month"]==month and key in lines: relevant[key].append(e)
        if e["event_month"]==month and e["order_id"] in {k[0] for k in lines} and key not in lines: identity.append(e)
    coverage={(x.get("order_id"),x.get("sku"),x.get("month")):x for x in cov if isinstance(x,dict)}
    result=[]
    for key,o in lines.items():
        ev=relevant[key]; subtotal=sum(e["quantity"] for e in ev); c=coverage.get((key[0],key[1],month)); gaps=[]
        if c is None: gaps.append("no coverage declaration")
        elif c.get("complete") is not True: gaps.append("receiving export is not declared complete")
        if any(x["event_id"] in {e["event_id"] for e in ev} for x in conflicts): gaps.append("conflicting event evidence")
        if any(x["order_id"]==key[0] for x in identity): gaps.append("current-month event SKU absent from supplied order")
        complete=bool(c and c.get("complete") is True) and not gaps
        if complete: status="received_as_ordered" if subtotal==o["ordered"] else ("shortfall" if subtotal<o["ordered"] else "excess")
        else: status="final_position_unconfirmed"
        result.append({"order_id":key[0],"sku":key[1],"ordered":o["ordered"],"supplier_contact":o.get("supplier_contact"),"event_ids":[e["event_id"] for e in ev],"observed_subtotal":subtotal,"coverage":c,"status":status,"evidence_gaps":gaps})
    out={"month":month,"lines":result,"conflicting_events":conflicts,"identity_anomalies":identity,"out_of_scope_event_ids":out_scope}
    text=json.dumps(out,indent=2,ensure_ascii=False)+"\n"
    if len(argv)==3: Path(argv[2]).write_text(text,encoding="utf-8")
    else: print(text,end="")
if __name__=="__main__": main(sys.argv)
