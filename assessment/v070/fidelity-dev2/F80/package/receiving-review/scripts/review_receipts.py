#!/usr/bin/env python3
"""Deterministically summarize monthly receipt evidence; no external effects."""
import json, sys
from collections import defaultdict
from pathlib import Path
from datetime import datetime

def fail(msg):
    return {"month": None, "lines": [], "out_of_scope_events": [], "validation_errors": [msg]}

def main(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as e:
        return fail(f"cannot read JSON: {e}")
    if not isinstance(data, dict): return fail("input must be a JSON object")
    required = ["month", "orders", "events", "coverage", "responsibilities"]
    missing = [k for k in required if k not in data]
    if missing: return fail("missing required fields: " + ", ".join(missing))
    month = data["month"]
    try: datetime.strptime(month, "%Y-%m")
    except Exception: return fail("month must be YYYY-MM")
    errors=[]
    orders=data["orders"] if isinstance(data["orders"], list) else []
    if not isinstance(data["orders"], list): errors.append("orders must be an array")
    keys=[]; order_map={}
    for i,o in enumerate(orders):
        if not isinstance(o,dict): errors.append(f"orders[{i}] must be an object"); continue
        k=(o.get("order_id"),o.get("sku")); keys.append(k)
        q=o.get("ordered")
        if not isinstance(q,int) or isinstance(q,bool) or q<=0: errors.append(f"orders[{i}].ordered must be a positive integer")
        if k in order_map: errors.append(f"duplicate order identity: {k[0]}/{k[1]}")
        order_map[k]=o
    events=data["events"] if isinstance(data["events"],list) else []
    if not isinstance(data["events"],list): errors.append("events must be an array")
    by_id={}; valid_events=[]; out=[]; anomalous_orders=set()
    for i,e in enumerate(events):
        if not isinstance(e,dict): errors.append(f"events[{i}] must be an object"); continue
        eid=e.get("event_id"); q=e.get("quantity")
        if not isinstance(q,int) or isinstance(q,bool): errors.append(f"events[{i}].quantity must be an integer")
        if not isinstance(eid,str) or not eid: errors.append(f"events[{i}].event_id required")
        sig=tuple(e.get(x) for x in ("order_id","sku","event_month","quantity"))
        if eid in by_id and by_id[eid] != sig: anomalous_orders.add(e.get("order_id")); anomalous_orders.add(by_id[eid][0])
        else: by_id[eid]=sig
        k=(e.get("order_id"),e.get("sku"))
        if e.get("order_id") not in {x[0] for x in keys}: out.append(e); continue
        if e.get("event_month") == month and k not in order_map: anomalous_orders.add(e.get("order_id"))
        valid_events.append(e)
    # exact duplicate event copies count once
    unique={}
    for e in valid_events: unique[(e.get("event_id"), tuple(e.get(x) for x in ("order_id","sku","event_month","quantity")))] = e
    cov={}
    if not isinstance(data["coverage"],list): errors.append("coverage must be an array")
    else:
        for c in data["coverage"]:
            if isinstance(c,dict) and c.get("month")==month: cov[(c.get("order_id"),c.get("sku"))]=c
    lines=[]
    for k in keys:
        ev=[e for e in unique.values() if (e.get("order_id"),e.get("sku"))==k and e.get("event_month")==month]
        subtotal=sum(e.get("quantity",0) for e in ev if isinstance(e.get("quantity"),int))
        c=cov.get(k)
        lines.append({"order_id":k[0],"sku":k[1],"ordered":order_map[k].get("ordered"),"observed_subtotal":subtotal,"event_ids":[e.get("event_id") for e in ev],"coverage_complete": c.get("complete") is True if c else False,"coverage_declared": c is not None,"identity_conflict": k[0] in anomalous_orders})
    return {"month":month,"lines":lines,"out_of_scope_events":out,"validation_errors":errors}

if __name__ == "__main__":
    if len(sys.argv) not in (2,3):
        print("usage: review_receipts.py INPUT.json [OUTPUT.json]", file=sys.stderr); sys.exit(2)
    result=main(sys.argv[1]); text=json.dumps(result,indent=2,sort_keys=True)
    if len(sys.argv)==3: Path(sys.argv[2]).write_text(text+"\n",encoding="utf-8")
    else: print(text)
    sys.exit(1 if result["validation_errors"] else 0)
