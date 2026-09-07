#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "deliverables/skills/monthly-receiving-review/scripts/receiving_review.py"


def run(payload):
    source = ROOT / "verification/case.json"
    output = ROOT / "verification/result.json"
    source.write_text(json.dumps(payload), encoding="utf-8")
    proc = subprocess.run([sys.executable, str(SCRIPT), str(source), "--output", str(output)],
                          text=True, capture_output=True)
    assert proc.returncode == 0, proc.stderr
    return json.loads(output.read_text(encoding="utf-8"))


base = {
    "month": "2026-08",
    "orders": [
        {"order_id": "PO-1", "sku": "A", "ordered": 10, "supplier_contact": "Supplier A"},
        {"order_id": "PO-1", "sku": "B", "ordered": 3, "supplier_contact": "Supplier A"},
        {"order_id": "PO-2", "sku": "C", "ordered": 5, "supplier_contact": "Supplier C"},
    ],
    "events": [
        {"event_id": "E1", "order_id": "PO-1", "sku": "A", "event_month": "2026-08", "quantity": 12},
        {"event_id": "E2", "order_id": "PO-1", "sku": "A", "event_month": "2026-08", "quantity": -2},
        {"event_id": "E2", "order_id": "PO-1", "sku": "A", "event_month": "2026-08", "quantity": -2},
        {"event_id": "OLD", "order_id": "PO-1", "sku": "B", "event_month": "2026-07", "quantity": 50},
        {"event_id": "B1", "order_id": "PO-1", "sku": "B", "event_month": "2026-08", "quantity": 1},
        {"event_id": "OUT", "order_id": "PO-X", "sku": "Z", "event_month": "2026-08", "quantity": 99},
        {"event_id": "C1", "order_id": "PO-2", "sku": "C", "event_month": "2026-08", "quantity": 7},
    ],
    "coverage": [
        {"order_id": "PO-1", "sku": "A", "month": "2026-08", "complete": True},
        {"order_id": "PO-1", "sku": "B", "month": "2026-08", "complete": False},
        {"order_id": "PO-2", "sku": "C", "month": "2026-08", "complete": True},
    ],
    "responsibilities": {"purchasing_coordinator": "Pat", "warehouse_lead": "Wren", "data_steward": "Dana"},
}

result = run(base)
lines = {(x["order_id"], x["sku"]): x for x in result["lines"]}
assert lines[("PO-1", "A")]["receipt_position"] == "received_as_ordered"
assert lines[("PO-1", "A")]["observed_net_received"] == 10
assert lines[("PO-1", "B")]["receipt_position"] == "undetermined"
assert lines[("PO-1", "B")]["observed_quantity_label"] == "provisional_subtotal"
assert lines[("PO-1", "B")]["follow_ups"][0]["kind"] == "complete_export"
assert lines[("PO-2", "C")]["receipt_position"] == "excess"
assert lines[("PO-2", "C")]["follow_ups"][0]["recipients"] == ["Wren"]
assert result["source_checks"]["exact_duplicate_rows_ignored"] == 1
assert result["source_checks"]["outside_order_event_ids_excluded"] == ["OUT"]

identity = json.loads(json.dumps(base))
identity["events"].append({"event_id": "BADSKU", "order_id": "PO-1", "sku": "NOPE", "event_month": "2026-08", "quantity": 1})
result = run(identity)
lines = {(x["order_id"], x["sku"]): x for x in result["lines"]}
assert lines[("PO-1", "A")]["evidence_condition"] == "conflicting_identity"
assert lines[("PO-1", "B")]["evidence_condition"] == "conflicting_identity"
assert lines[("PO-2", "C")]["receipt_position"] == "excess"

conflict = json.loads(json.dumps(base))
conflict["events"].append({"event_id": "C1", "order_id": "PO-2", "sku": "C", "event_month": "2026-08", "quantity": 8})
result = run(conflict)
lines = {(x["order_id"], x["sku"]): x for x in result["lines"]}
assert lines[("PO-2", "C")]["receipt_position"] == "undetermined"
assert result["source_checks"]["conflicting_event_ids"] == ["C1"]

bad = ROOT / "verification/bad.json"
bad.write_text(json.dumps({"month": "2026-13"}), encoding="utf-8")
proc = subprocess.run([sys.executable, str(SCRIPT), str(bad)], text=True, capture_output=True)
assert proc.returncode == 2 and "month" not in proc.stdout
print("all receiving-review checks passed")
