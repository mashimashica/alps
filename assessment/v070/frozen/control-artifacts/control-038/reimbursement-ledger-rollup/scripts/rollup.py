#!/usr/bin/env python3
"""Resumable, exact-cent rollup over ledger_api.py's paginated interface."""
import argparse, datetime, json, os, subprocess, tempfile

def die(msg):
    print(json.dumps({"complete": False, "error": msg}, sort_keys=True)); raise SystemExit(2)

def call(api, state, args):
    cmd = ["python3.12", api, "--state", state] + args
    p = subprocess.run(cmd, text=True, capture_output=True)
    try: body = json.loads(p.stdout)
    except Exception: body = {"error": "invalid_api_output", "stdout": p.stdout, "stderr": p.stderr}
    return p.returncode, body

def atomic(path, obj):
    d = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(prefix=".rollup-", dir=d, text=True)
    with os.fdopen(fd, "w") as f: json.dump(obj, f, sort_keys=True); f.write("\n")
    os.replace(tmp, path)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", required=True); ap.add_argument("--state", required=True)
    ap.add_argument("--start", required=True); ap.add_argument("--end", required=True)
    ap.add_argument("--checkpoint", required=True)
    a = ap.parse_args()
    try:
        start = datetime.date.fromisoformat(a.start); end = datetime.date.fromisoformat(a.end)
    except ValueError: die("invalid ISO date interval")
    if start > end: die("invalid interval: start is after end")
    rc, meta = call(a.api, a.state, ["describe"])
    if rc: die("describe failed: " + str(meta.get("error", meta)))
    snap = meta.get("snapshot_id")
    cp = {"snapshot_id": snap, "start": a.start, "end": a.end, "cursor": None, "entries": {}}
    if os.path.exists(a.checkpoint):
        try: cp = json.load(open(a.checkpoint))
        except Exception: die("checkpoint is not valid JSON")
        if (cp.get("snapshot_id"), cp.get("start"), cp.get("end")) != (snap, a.start, a.end): die("checkpoint does not match snapshot or interval")
        cp.setdefault("entries", {})
    used = 0
    while used < 2 and not cp.get("complete"):
        args = ["page", "--snapshot", snap]
        if cp.get("cursor") is not None: args += ["--cursor", cp["cursor"]]
        rc, page = call(a.api, a.state, args)
        if rc:
            cp["calls_used_last_run"] = used; atomic(a.checkpoint, cp)
            print(json.dumps({"complete": False, "snapshot_id": snap, "interval": {"start": a.start, "end": a.end}, "calls_used": used, "error": page.get("error", "page failed")}, sort_keys=True)); return 0
        used += 1
        for e in page.get("items", []): cp["entries"][e["entry_id"]] = e
        cp["cursor"] = page.get("next_cursor")
        cp["complete"] = cp["cursor"] is None
        atomic(a.checkpoint, cp)
    totals = {}
    for e in cp["entries"].values():
        if e["status"] != "settled" or not (a.start <= e["posted_on"] <= a.end): continue
        v = totals.setdefault(e["vendor_id"], {"vendor_id": e["vendor_id"], "settled_charge_cents": 0, "settled_credit_cents": 0, "net_cents": 0, "qualifying_entry_count": 0})
        key = "settled_charge_cents" if e["kind"] == "charge" else "settled_credit_cents"
        v[key] += e["amount_cents"]; v["qualifying_entry_count"] += 1
    out = []
    for v in totals.values():
        v["net_cents"] = v["settled_charge_cents"] - v["settled_credit_cents"]
        if v["net_cents"] <= 0: out.append(v)
    print(json.dumps({"complete": bool(cp.get("complete")), "snapshot_id": snap, "interval": {"start": a.start, "end": a.end}, "calls_used": used, "vendors": sorted(out, key=lambda x: x["vendor_id"])}, sort_keys=True))
if __name__ == "__main__": main()
