import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "review_receipts.py"
SPEC = importlib.util.spec_from_file_location("review_receipts", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def base_input():
    return {
        "month": "2026-08",
        "orders": [
            {"order_id": "PO-1", "sku": "A", "ordered": 10, "supplier_contact": "Aya at Supply Co"},
            {"order_id": "PO-2", "sku": "B", "ordered": 5, "supplier_contact": "Bo at Parts Co"},
            {"order_id": "PO-3", "sku": "C", "ordered": 4, "supplier_contact": "Cy at Goods Co"},
        ],
        "events": [],
        "coverage": [
            {"order_id": "PO-1", "sku": "A", "month": "2026-08", "complete": True},
            {"order_id": "PO-2", "sku": "B", "month": "2026-08", "complete": True},
            {"order_id": "PO-3", "sku": "C", "month": "2026-08", "complete": False},
        ],
        "responsibilities": {
            "purchasing_coordinator": "Mina",
            "warehouse_lead": "Ren",
            "data_steward": "Sora",
        },
    }


class ReceivingReviewTests(unittest.TestCase):
    def by_key(self, result):
        return {(line["order_id"], line["sku"]): line for line in result["lines"]}

    def test_signed_totals_positions_and_incomplete_subtotal(self):
        data = base_input()
        data["events"] = [
            {"event_id": "E1", "order_id": "PO-1", "sku": "A", "event_month": "2026-08", "quantity": 12},
            {"event_id": "E2", "order_id": "PO-1", "sku": "A", "event_month": "2026-08", "quantity": -2},
            {"event_id": "E3", "order_id": "PO-2", "sku": "B", "event_month": "2026-08", "quantity": 7},
            {"event_id": "E4", "order_id": "PO-3", "sku": "C", "event_month": "2026-08", "quantity": 4},
        ]
        lines = self.by_key(MODULE.analyze(data))
        self.assertEqual(lines[("PO-1", "A")]["position"], "received_as_ordered")
        self.assertEqual(lines[("PO-1", "A")]["observed_net_received_quantity"], 10)
        self.assertEqual(lines[("PO-2", "B")]["position"], "excess")
        self.assertEqual(lines[("PO-2", "B")]["difference_quantity"], 2)
        self.assertEqual(lines[("PO-2", "B")]["follow_up"]["owners"][0]["recipient"], "Ren")
        self.assertEqual(lines[("PO-3", "C")]["position"], "undetermined")
        self.assertEqual(lines[("PO-3", "C")]["observed_net_received_quantity"], 4)
        self.assertIn("incomplete_coverage", lines[("PO-3", "C")]["evidence"]["blockers"])

    def test_shortfall_exact_duplicate_and_exclusions(self):
        data = base_input()
        event = {"event_id": "E1", "order_id": "PO-1", "sku": "A", "event_month": "2026-08", "quantity": 6}
        data["events"] = [
            event,
            dict(event),
            {"event_id": "OLD", "order_id": "PO-1", "sku": "A", "event_month": "2026-07", "quantity": 50},
            {"event_id": "OTHER", "order_id": "PO-X", "sku": "Z", "event_month": "2026-08", "quantity": 50},
        ]
        result = MODULE.analyze(data)
        line = self.by_key(result)[("PO-1", "A")]
        self.assertEqual(line["observed_net_received_quantity"], 6)
        self.assertEqual(line["position"], "shortfall")
        self.assertEqual(line["difference_quantity"], 4)
        self.assertEqual(line["evidence"]["exact_duplicate_event_rows_ignored"], 1)
        self.assertEqual(line["follow_up"]["external_recipient"], "Aya at Supply Co")
        self.assertEqual(result["excluded_events"]["outside_requested_month"]["event_ids"], ["OLD"])
        self.assertEqual(result["excluded_events"]["outside_supplied_order_set"]["event_ids"], ["OTHER"])

    def test_unknown_sku_blocks_all_lines_on_order(self):
        data = base_input()
        data["orders"].append({"order_id": "PO-1", "sku": "D", "ordered": 2, "supplier_contact": "Aya at Supply Co"})
        data["coverage"].append({"order_id": "PO-1", "sku": "D", "month": "2026-08", "complete": True})
        data["events"] = [
            {"event_id": "BAD", "order_id": "PO-1", "sku": "UNKNOWN", "event_month": "2026-08", "quantity": 1}
        ]
        lines = self.by_key(MODULE.analyze(data))
        for key in (("PO-1", "A"), ("PO-1", "D")):
            self.assertEqual(lines[key]["position"], "undetermined")
            self.assertIn("unknown_sku_for_in_scope_order", lines[key]["evidence"]["blockers"])
            roles = [owner["role"] for owner in lines[key]["follow_up"]["owners"]]
            self.assertEqual(roles, ["purchasing_coordinator", "data_steward"])

    def test_conflicting_event_id_is_excluded_and_limited(self):
        data = base_input()
        data["events"] = [
            {"event_id": "E-X", "order_id": "PO-1", "sku": "A", "event_month": "2026-08", "quantity": 10},
            {"event_id": "E-X", "order_id": "PO-1", "sku": "A", "event_month": "2026-08", "quantity": 9},
            {"event_id": "E2", "order_id": "PO-2", "sku": "B", "event_month": "2026-08", "quantity": 5},
        ]
        result = MODULE.analyze(data)
        lines = self.by_key(result)
        self.assertEqual(lines[("PO-1", "A")]["observed_net_received_quantity"], 0)
        self.assertEqual(lines[("PO-1", "A")]["position"], "undetermined")
        self.assertIn("conflicting_event_id", lines[("PO-1", "A")]["evidence"]["blockers"])
        self.assertEqual(lines[("PO-2", "B")]["position"], "received_as_ordered")
        self.assertEqual(result["excluded_events"]["conflicting_event_ids"]["event_ids"], ["E-X"])

    def test_coverage_conflict_and_missing_recipients_stay_explicit(self):
        data = base_input()
        data["coverage"].append({"order_id": "PO-2", "sku": "B", "month": "2026-08", "complete": False})
        data["responsibilities"]["data_steward"] = ""
        result = MODULE.analyze(data)
        line = self.by_key(result)[("PO-2", "B")]
        self.assertEqual(line["coverage_state"], "conflicting")
        self.assertEqual(line["position"], "undetermined")
        self.assertIn("data_steward", line["follow_up"]["recipient_gaps"])

    def test_conflicting_order_does_not_block_unrelated_line(self):
        data = base_input()
        data["orders"].append({"order_id": "PO-1", "sku": "A", "ordered": 11, "supplier_contact": "Aya at Supply Co"})
        data["events"] = [
            {"event_id": "E2", "order_id": "PO-2", "sku": "B", "event_month": "2026-08", "quantity": 5}
        ]
        lines = self.by_key(MODULE.analyze(data))
        self.assertEqual(lines[("PO-1", "A")]["position"], "undetermined")
        self.assertEqual(lines[("PO-2", "B")]["position"], "received_as_ordered")

    def test_invalid_event_month_blocks_only_identifiable_line(self):
        data = base_input()
        data["events"] = [
            {"event_id": "NO-MONTH", "order_id": "PO-1", "sku": "A", "quantity": 10},
            {"event_id": "E2", "order_id": "PO-2", "sku": "B", "event_month": "2026-08", "quantity": 5},
        ]
        lines = self.by_key(MODULE.analyze(data))
        self.assertEqual(lines[("PO-1", "A")]["position"], "undetermined")
        self.assertIn("invalid_event_month", lines[("PO-1", "A")]["evidence"]["blockers"])
        self.assertEqual(lines[("PO-2", "B")]["position"], "received_as_ordered")

    def test_missing_event_id_blocks_identifiable_current_line(self):
        data = base_input()
        data["events"] = [
            {"order_id": "PO-1", "sku": "A", "event_month": "2026-08", "quantity": 10}
        ]
        line = self.by_key(MODULE.analyze(data))[("PO-1", "A")]
        self.assertEqual(line["position"], "undetermined")
        self.assertIn("invalid_event_id", line["evidence"]["blockers"])


if __name__ == "__main__":
    unittest.main()
