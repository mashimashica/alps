#!/usr/bin/env python3
"""Durable, conservative coordinator for the supplied local booking CLI."""
import argparse, json, os, subprocess, sys, tempfile, uuid
from pathlib import Path

def atomic_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name+".", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as f: json.dump(value, f, sort_keys=True, indent=2); f.write("\n")
        os.replace(name, path)
    finally:
        if os.path.exists(name): os.unlink(name)

def run_cli(state, args):
    cmd=[sys.executable, str(Path(__file__).with_name("booking.py")), "--state", str(Path(state).resolve()), *args]
    return subprocess.run(cmd, text=True, capture_output=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--state", required=True); p.add_argument("--ledger", required=True)
    sub=p.add_subparsers(dest="op", required=True)
    i=sub.add_parser("init"); i.add_argument("--fixture", default=str(Path(__file__).parents[1]/"assets.fixture.json"))
    r=sub.add_parser("reserve"); r.add_argument("--request-key"); r.add_argument("--party-id", required=True); r.add_argument("--slot-id", required=True); r.add_argument("--seats", type=int, required=True)
    q=sub.add_parser("reconcile"); q.add_argument("--request-key", required=True)
    sub.add_parser("availability")
    a=p.parse_args(); state=Path(a.state); ledger=Path(a.ledger)
    records=json.loads(ledger.read_text()) if ledger.exists() else {}
    if a.op=="init":
        x=run_cli(state,["init","--fixture",a.fixture]); sys.stdout.write(x.stdout); sys.stderr.write(x.stderr); return x.returncode
    if a.op=="availability":
        x=run_cli(state,["availability"]); sys.stdout.write(x.stdout); sys.stderr.write(x.stderr); return x.returncode
    if a.op=="reconcile":
        key=a.request_key; rec=records.get(key)
        if not rec: print(json.dumps({"state":"unresolved","reason":"request key is not in durable ledger","request_key":key})); return 4
        x=run_cli(state,["lookup","--request-key",key]);
        if x.returncode==0 and x.stdout.strip():
            out=json.loads(x.stdout); print(json.dumps(out,sort_keys=True));
            if out.get("state") in ("confirmed","rejected"): records[key]["last_receipt"]=out; atomic_write(ledger,records)
            return 0
        print(json.dumps({"state":"unresolved","request_key":key,"party_id":rec["party_id"],"slot_id":rec["slot_id"],"seats":rec["seats"],"detail":"lookup unavailable; retry reconcile with same key"})); return 4
    key=a.request_key or ("req-"+uuid.uuid4().hex)
    old=records.get(key)
    if old and (old["party_id"],old["slot_id"],old["seats"]) != (a.party_id,a.slot_id,a.seats):
        print(json.dumps({"state":"unresolved","reason":"local request-key conflict","request_key":key})); return 3
    records[key]={"request_key":key,"party_id":a.party_id,"slot_id":a.slot_id,"seats":a.seats}
    atomic_write(ledger,records)
    x=run_cli(state,["reserve","--request-key",key,"--party-id",a.party_id,"--slot-id",a.slot_id,"--seats",str(a.seats)])
    if x.returncode==0 and x.stdout.strip():
        out=json.loads(x.stdout); records[key]["last_receipt"]=out; atomic_write(ledger,records); print(json.dumps(out,sort_keys=True)); return 0
    if x.returncode in (3,): print(x.stdout or json.dumps({"state":"unresolved","request_key":key})); return x.returncode
    print(json.dumps({"state":"unresolved","request_key":key,"party_id":a.party_id,"slot_id":a.slot_id,"seats":a.seats,"detail":"attempt outcome unavailable; run reconcile with the same key"})); return 4
if __name__=="__main__": sys.exit(main())
