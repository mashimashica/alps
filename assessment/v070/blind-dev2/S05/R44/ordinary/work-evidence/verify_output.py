#!/usr/bin/env python3
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    data = json.load(handle)

assert data["validation_errors"] == []
lines = {(row["order_id"], row["sku"]): row for row in data["lines"]}
assert lines[("PO-T1", "COMPLETE")]["position"] == "received as ordered"
assert lines[("PO-T1", "COMPLETE")]["observed_net_received"] == 10
assert lines[("PO-T1", "COMPLETE")]["event_ids"] == ["EV-DUP"]
assert lines[("PO-T2", "SHORT")]["position"] == "shortfall"
assert lines[("PO-T3", "EXCESS")]["position"] == "excess"
assert lines[("PO-T4", "INCOMPLETE")]["position"] == "undetermined"
assert lines[("PO-T4", "INCOMPLETE")]["observed_net_received"] == 4
assert lines[("PO-T5", "RETURN")]["observed_net_received"] == 10
assert lines[("PO-T5", "RETURN")]["position"] == "received as ordered"
assert lines[("PO-T6", "MONTH-FILTER")]["observed_net_received"] == 10
assert lines[("PO-T6", "MONTH-FILTER")]["event_ids"] == ["EV-MON-A"]
assert lines[("PO-T7", "EXPECTED-SKU")]["position"] == "undetermined"
assert "order/event identity reconciliation required" in lines[("PO-T7", "EXPECTED-SKU")]["evidence_issues"]
assert lines[("PO-T8", "CONFLICT")]["position"] == "undetermined"
assert "conflicting content for event_id EV-CONFLICT" in lines[("PO-T8", "CONFLICT")]["evidence_issues"]
assert all(row["order_id"] != "PO-OUTSIDE" for row in data["lines"])
print("PASS: complete, shortfall, excess, incomplete, return, out-of-month, unknown-order, SKU-mismatch, exact-duplicate, and conflicting-event cases")
