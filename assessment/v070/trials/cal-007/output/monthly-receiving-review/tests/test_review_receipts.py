from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "review_receipts.py"


def invoke(document: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "-"],
        input=json.dumps(document),
        text=True,
        capture_output=True,
        check=False,
    )


class ReviewReceiptsTests(unittest.TestCase):
    def base(self) -> dict[str, object]:
        return {
            "month": "2026-08",
            "orders": [
                {
                    "order_id": "PO-1",
                    "sku": "A",
                    "ordered": 10,
                    "supplier_contact": "Supplier A",
                },
                {
                    "order_id": "PO-2",
                    "sku": "B",
                    "ordered": 5,
                    "supplier_contact": "Supplier B",
                },
                {
                    "order_id": "PO-3",
                    "sku": "C",
                    "ordered": 9,
                    "supplier_contact": "Supplier C",
                },
            ],
            "events": [
                {"event_id": "E-1", "order_id": "PO-1", "sku": "A", "event_month": "2026-08", "quantity": 8},
                {"event_id": "E-2", "order_id": "PO-1", "sku": "A", "event_month": "2026-08", "quantity": 3},
                {"event_id": "E-3", "order_id": "PO-1", "sku": "A", "event_month": "2026-08", "quantity": -1},
                {"event_id": "E-3", "order_id": "PO-1", "sku": "A", "event_month": "2026-08", "quantity": -1},
                {"event_id": "E-4", "order_id": "PO-2", "sku": "B", "event_month": "2026-08", "quantity": 7},
                {"event_id": "E-5", "order_id": "PO-3", "sku": "C", "event_month": "2026-08", "quantity": 4},
                {"event_id": "E-OLD", "order_id": "PO-1", "sku": "A", "event_month": "2026-07", "quantity": 999},
                {"event_id": "E-OUT", "order_id": "PO-X", "sku": "Z", "event_month": "2026-08", "quantity": 999},
            ],
            "coverage": [
                {"order_id": "PO-1", "sku": "A", "month": "2026-08", "complete": True},
                {"order_id": "PO-2", "sku": "B", "month": "2026-08", "complete": True},
                {"order_id": "PO-3", "sku": "C", "month": "2026-08", "complete": False},
            ],
            "responsibilities": {
                "purchasing_coordinator": "Pat",
                "warehouse_lead": "Wren",
                "data_steward": "Dana",
            },
        }

    def test_positions_duplicates_signed_quantities_and_scope(self) -> None:
        completed = invoke(self.base())
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        lines = {(line["order_id"], line["sku"]): line for line in result["lines"]}

        self.assertEqual(lines[("PO-1", "A")]["observed_uncontested_net_received"], 10)
        self.assertEqual(lines[("PO-1", "A")]["position"], "received_as_ordered")
        self.assertEqual(lines[("PO-2", "B")]["position"], "excess")
        self.assertEqual(lines[("PO-2", "B")]["excess_quantity"], 2)
        self.assertEqual(lines[("PO-3", "C")]["position"], "unconfirmed")
        self.assertEqual(lines[("PO-3", "C")]["observed_uncontested_net_received"], 4)
        self.assertEqual(result["exact_event_duplicates"], [{"copies_ignored": 1, "event_id": "E-3"}])
        self.assertEqual(result["summary"]["lines_requiring_follow_up"], 2)
        self.assertEqual(
            {item["type"] for item in result["exclusions"]},
            {"event_outside_requested_month", "event_order_outside_supplied_scope"},
        )

    def test_conflict_and_unknown_sku_block_only_affected_orders(self) -> None:
        document = self.base()
        events = document["events"]
        assert isinstance(events, list)
        events.extend([
            {"event_id": "E-C", "order_id": "PO-1", "sku": "A", "event_month": "2026-08", "quantity": 1},
            {"event_id": "E-C", "order_id": "PO-2", "sku": "B", "event_month": "2026-08", "quantity": 1},
            {"event_id": "E-BADSKU", "order_id": "PO-3", "sku": "NOPE", "event_month": "2026-08", "quantity": 1},
        ])

        completed = invoke(document)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        lines = {(line["order_id"], line["sku"]): line for line in result["lines"]}
        self.assertTrue(all(line["position"] == "unconfirmed" for line in lines.values()))
        for key in (("PO-1", "A"), ("PO-2", "B"), ("PO-3", "C")):
            self.assertIn("source_identity_reconciliation", {item["type"] for item in lines[key]["follow_ups"]})

    def test_unlocalizable_current_month_event_blocks_all_lines(self) -> None:
        document = self.base()
        events = document["events"]
        assert isinstance(events, list)
        events.append({"event_id": "E-NO-ORDER", "sku": "A", "event_month": "2026-08", "quantity": 1})

        completed = invoke(document)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertTrue(all(not line["position_is_final"] for line in result["lines"]))

    def test_invalid_requested_month_is_fatal(self) -> None:
        document = self.base()
        document["month"] = "2026-13"
        completed = invoke(document)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertIn("valid string in YYYY-MM form", completed.stderr)


if __name__ == "__main__":
    unittest.main()
