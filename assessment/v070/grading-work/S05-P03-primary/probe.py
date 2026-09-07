"""Narrow component checks on disposable copies, not consumer applications."""
import copy
import json
import subprocess
from pathlib import Path

root = Path(__file__).parent
base = {
    "month": "2026-08",
    "orders": [
        {"order_id": "P-A", "sku": "X", "ordered": 10, "supplier_contact": "Supplier A"},
        {"order_id": "P-B", "sku": "Y", "ordered": 5, "supplier_contact": "Supplier B"},
    ],
    "events": [
        {"event_id": "e-a", "order_id": "P-A", "sku": "X", "event_month": "2026-08", "quantity": 6},
        {"event_id": "e-b", "order_id": "P-B", "sku": "Y", "event_month": "2026-08", "quantity": 5},
    ],
    "coverage": [
        {"order_id": "P-A", "sku": "X", "month": "2026-08", "complete": False},
        {"order_id": "P-B", "sku": "Y", "month": "2026-08", "complete": True},
    ],
    "responsibilities": {
        "purchasing_coordinator": "Buyer",
        "warehouse_lead": "Warehouse",
        "data_steward": "Data",
    },
}

combined = copy.deepcopy(base)
combined["events"].append({"event_id": "e-unknown", "order_id": "P-A", "sku": "Z", "event_month": "2026-08", "quantity": 1})
contradictory = copy.deepcopy(base)
contradictory["coverage"].append({"order_id": "P-A", "sku": "X", "month": "2026-08", "complete": True})

fixtures = {"combined_identity_incomplete": combined, "contradictory_coverage_false_then_true": contradictory}
scripts = {"R17": "receiving_review.py", "R28": "review.py", "R63": "review_receipts.py"}
runs = [("combined_identity_incomplete", "R17"), ("combined_identity_incomplete", "R63"),
        ("contradictory_coverage_false_then_true", "R28"), ("contradictory_coverage_false_then_true", "R63")]
for name, data in fixtures.items():
    (root / (name + ".json")).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

for name, candidate in runs:
    command = ["python3", "-B", str(root / "components" / candidate / "scripts" / scripts[candidate]), str(root / (name + ".json"))]
    result = subprocess.run(command, cwd=root, text=True, capture_output=True)
    stem = root / (name + "-" + candidate)
    stem.with_suffix(".stdout.json").write_text(result.stdout, encoding="utf-8")
    stem.with_suffix(".stderr.txt").write_text(result.stderr, encoding="utf-8")
    print(json.dumps({"probe": name, "candidate": candidate, "command": command,
                      "exit_code": result.returncode, "stderr": result.stderr}))
    if result.returncode == 0:
        report = json.loads(result.stdout)
        print(json.dumps({"line_results": report["lines"]}, ensure_ascii=False))
