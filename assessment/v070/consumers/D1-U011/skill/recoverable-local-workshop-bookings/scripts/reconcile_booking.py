#!/usr/bin/env python3
"""Durable, conservative adapter for the supplied local booking simulator."""
import argparse, json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BOOKING = os.path.join(HERE, "booking.py")

def load(path):
    try:
        with open(path) as f: return json.load(f)
    except FileNotFoundError: return {}

def save(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".booking-journal-", dir=os.path.dirname(os.path.abspath(path)))
    try:
        with os.fdopen(fd, "w") as f: json.dump(data, f, sort_keys=True); f.write("\n"); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def call(state, args):
    p = subprocess.run([sys.executable, BOOKING, "--state", state] + args, text=True, capture_output=True)
    try: obj = json.loads(p.stdout) if p.stdout.strip() else None
    except json.JSONDecodeError: obj = None
    return p.returncode, obj, p.stderr.strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("reserve", "recover")); ap.add_argument("--state", required=True)
    ap.add_argument("--request-key", required=True); ap.add_argument("--party-id"); ap.add_argument("--slot-id"); ap.add_argument("--seats", type=int)
    ap.add_argument("--journal")
    ns = ap.parse_args(); journal = ns.journal or ns.state + ".requests.json"
    db = load(journal); key = ns.request_key; rec = db.get(key)
    if ns.mode == "reserve":
        if rec and rec.get("request") != {"request_key": key, "party_id": ns.party_id, "slot_id": ns.slot_id, "seats": ns.seats}:
            print(json.dumps({"state":"error","reason":"idempotency_conflict"})); return 3
        req = {"request_key":key,"party_id":ns.party_id,"slot_id":ns.slot_id,"seats":ns.seats}
        if not rec: db[key] = {"request": req, "state":"unresolved"}; save(journal, db)
    else:
        if not rec: print(json.dumps({"state":"error","reason":"unknown_request_key"})); return 2
        req = rec["request"]
    code, obj, err = call(ns.state, (["lookup", "--request-key", key] if ns.mode == "recover" else ["reserve", "--request-key", key, "--party-id", req["party_id"], "--slot-id", req["slot_id"], "--seats", str(req["seats"])]))
    if ns.mode == "recover" and obj and obj.get("state") == "not_seen":
        code, obj, err = call(ns.state, ["reserve", "--request-key", key, "--party-id", req["party_id"], "--slot-id", req["slot_id"], "--seats", str(req["seats"])])
    if obj and obj.get("state") in ("confirmed", "rejected"):
        db[key] = {"request": req, "state": obj["state"], "receipt": obj}; save(journal, db); print(json.dumps(obj, sort_keys=True)); return 0
    db[key]["state"] = "unresolved"; db[key]["last_error"] = err or "outcome unavailable"; save(journal, db)
    print(json.dumps({"state":"unresolved","request":req,"reason":err or "outcome unavailable"}, sort_keys=True)); return 75

if __name__ == "__main__": sys.exit(main())
