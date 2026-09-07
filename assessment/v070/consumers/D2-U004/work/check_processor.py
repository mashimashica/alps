#!/usr/bin/env python3
import json
import sys

source_path, review_path = sys.argv[1:3]
with open(source_path, encoding="utf-8") as f:
    source = json.load(f)
with open(review_path, encoding="utf-8") as f:
    review = json.load(f)

assert review["validation_errors"] == []
lines = {(x["order_id"], x["sku"]): x for x in review["lines"]}
events = source["events"]

checks = []
checks.append(("complete", lines[("PO-S2607-821", "STRAP-20")]["position"] == "received as ordered"))
checks.append(("shortfall", lines[("PO-S2607-827", "WRAP-500")]["observed_net_received"] == 18 and lines[("PO-S2607-827", "WRAP-500")]["position"] == "shortfall"))
checks.append(("excess", lines[("PO-S2607-826", "INSERT-G")]["observed_net_received"] == 75 and lines[("PO-S2607-826", "INSERT-G")]["position"] == "excess"))
checks.append(("incomplete", lines[("PO-S2607-823", "POUCH-12")]["evidence_complete"] is False and lines[("PO-S2607-823", "POUCH-12")]["position"] == "undetermined"))
checks.append(("return", lines[("PO-S2607-829", "PAD-FOAM")]["observed_net_received"] == -4))
reported_ids = {eid for line in review["lines"] for eid in line["event_ids"]}
checks.append(("out-of-month", not ({"RCV-K6990", "RCV-K6991", "RCV-K6992"} & reported_ids)))
checks.append(("unknown-order", all(line["order_id"] != "PO-S2607-899" for line in review["lines"])))
checks.append(("SKU-mismatch", all(lines[("PO-S2607-820", sku)]["position"] == "undetermined" for sku in ("BOLT-M8", "WASHER-M8"))))
checks.append(("exact-duplicate", lines[("PO-S2607-823", "POUCH-12")]["event_ids"].count("RCV-K7110") == 1 and lines[("PO-S2607-826", "INSERT-G")]["event_ids"].count("RCV-K7114") == 1))
checks.append(("conflicting-event-primary", lines[("PO-S2607-821", "PACK-RACK")]["position"] == "undetermined" and "RCV-K7107" not in lines[("PO-S2607-821", "PACK-RACK")]["event_ids"]))

for name, passed in checks:
    print(f"{'PASS' if passed else 'FAIL'} {name}")
assert all(passed for _, passed in checks)

conflict_rows = [e for e in events if e["event_id"] == "RCV-K7107"]
affected = sorted({(e["order_id"], e["sku"]) for e in conflict_rows})
assert affected == [("PO-S2607-821", "PACK-RACK"), ("PO-S2607-822", "SHIELD-CLR")]
assert lines[("PO-S2607-822", "SHIELD-CLR")]["evidence_complete"] is True
print("LIMITATION conflicting event RCV-K7107 also affects PO-S2607-822/SHIELD-CLR, but processor did not block that line; agent override required")
