#!/usr/bin/env python3
"""Synthetic component checks; no real receiving records or messages are used."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
from review import review


def fixture():
    return {"month": "2026-08", "orders": [
        {"order_id": "P1", "sku": "A", "ordered": 10, "supplier_contact": "Supplier One"},
        {"order_id": "P2", "sku": "B", "ordered": 5, "supplier_contact": "Supplier Two"}],
        "events": [], "coverage": [
            {"order_id": "P1", "sku": "A", "month": "2026-08", "complete": True},
            {"order_id": "P2", "sku": "B", "month": "2026-08", "complete": True}],
        "responsibilities": {"purchasing_coordinator": "Coordinator", "warehouse_lead": "Warehouse", "data_steward": "Steward"}}


def event(eid="E1", quantity=10, order="P1", sku="A", month="2026-08"):
    return {"event_id": eid, "quantity": quantity, "order_id": order, "sku": sku, "event_month": month}


class ReviewTests(unittest.TestCase):
    def line(self, data, index=0):
        return review(data)["lines"][index]

    def test_equal_and_signed_reversals(self):
        data = fixture()
        data["events"] = [event(quantity=14), event("E2", -4)]
        line = self.line(data)
        self.assertEqual((line["final_net"], line["receipt_position"], line["follow_ups"]), (10, "received_as_ordered", []))

    def test_shortfall_routing(self):
        data = fixture()
        data["events"] = [event(quantity=7)]
        line = self.line(data)
        task = line["follow_ups"][0]
        self.assertEqual(line["remaining"], 3)
        self.assertEqual(task["owners"], ["Coordinator"])
        self.assertEqual(task["recipients"], ["Supplier One"])
        self.assertIn("remaining 3 units", task["draft"])

    def test_excess_routing(self):
        data = fixture()
        data["events"] = [event(quantity=13)]
        line = self.line(data)
        self.assertEqual(line["excess"], 3)
        self.assertEqual(line["follow_ups"][0]["recipients"], ["Warehouse"])
        self.assertIn("surplus 3 units", line["follow_ups"][0]["action"])

    def test_negative_net(self):
        data = fixture()
        data["events"] = [event(quantity=-3)]
        self.assertEqual(self.line(data)["remaining"], 13)

    def test_complete_empty_export_supports_zero(self):
        line = self.line(fixture())
        self.assertEqual((line["final_net"], line["remaining"]), (0, 10))

    def test_partial_and_missing_coverage_never_final(self):
        for coverage in ([], [{"order_id": "P1", "sku": "A", "month": "2026-08", "complete": False}]):
            data = fixture()
            data["coverage"] = coverage
            data["events"] = [event()]
            result = review(data)
            self.assertEqual(result["scope_line_count"], 2)
            line = result["lines"][0]
            self.assertEqual(line["observed_net"], 10)
            self.assertIsNone(line["final_net"])
            self.assertEqual(line["receipt_position"], "not_final")
            self.assertEqual(line["follow_ups"][0]["recipients"], ["Steward"])

    def test_other_month_and_external_order(self):
        data = fixture()
        data["events"] = [event(quantity=900, month="2026-07"), event("E2", 900, "OUTSIDE", "X")]
        self.assertEqual(self.line(data)["final_net"], 0)

    def test_exact_event_duplicates_once(self):
        data = fixture()
        data["events"] = [event(), event()]
        self.assertEqual(self.line(data)["final_net"], 10)
        self.assertEqual(self.line(data)["accepted_event_ids"], ["E1"])

    def test_conflict_across_lines(self):
        data = fixture()
        data["events"] = [event(), event(order="P2", sku="B", quantity=5)]
        for line in review(data)["lines"]:
            self.assertEqual(line["receipt_position"], "blocked")
            self.assertEqual(line["observed_net"], 0)
            self.assertEqual(line["follow_ups"][0]["recipients"], ["Coordinator", "Steward"])
            self.assertIn("[0, 1]", line["issues"][0]["message"])

    def test_conflicting_id_across_months(self):
        data = fixture()
        data["events"] = [event(), event(month="2026-07")]
        self.assertEqual(self.line(data)["receipt_position"], "blocked")

    def test_unknown_sku_blocks_order_only(self):
        data = fixture()
        data["orders"].append({"order_id": "P1", "sku": "C", "ordered": 2})
        data["coverage"].append({"order_id": "P1", "sku": "C", "month": "2026-08", "complete": True})
        data["events"] = [event(), event("E2", 1, sku="UNKNOWN")]
        lines = review(data)["lines"]
        self.assertEqual([l["receipt_position"] for l in lines], ["blocked", "shortfall", "blocked"])
        self.assertEqual(lines[0]["observed_net"], 10)

    def test_missing_quantity_is_not_zero(self):
        data = fixture()
        bad = event()
        del bad["quantity"]
        data["events"] = [bad]
        line = self.line(data)
        self.assertIsNone(line["final_net"])
        self.assertEqual(line["follow_ups"][0]["kind"], "evidence_repair")
        self.assertEqual(self.line(data, 1)["final_net"], 0)

    def test_invalid_quantities_and_missing_id(self):
        for value in (None, True, 1.5, "10", [], {}):
            data = fixture()
            data["events"] = [event(quantity=value)]
            self.assertEqual(self.line(data)["receipt_position"], "blocked")
        data = fixture()
        data["events"] = [event(eid=None)]
        self.assertIsNone(self.line(data)["final_net"])

    def test_invalid_month_blocks_only_affected_line(self):
        data = fixture()
        data["events"] = [event(month="2026-13")]
        self.assertIsNone(self.line(data)["final_net"])
        self.assertEqual(self.line(data, 1)["final_net"], 0)

    def test_unattributable_event_blocks_all(self):
        for bad in (None, event(order=None)):
            data = fixture()
            data["events"] = [bad]
            self.assertTrue(all(l["final_net"] is None for l in review(data)["lines"]))

    def test_invalid_and_contradictory_coverage(self):
        for extra in ({"order_id": "P1", "sku": "A", "month": "2026-08", "complete": False},
                      {"order_id": "P1", "sku": "A", "month": "2026-08", "complete": "true"},
                      {"order_id": "P1", "sku": "A", "month": None, "complete": True}):
            data = fixture()
            data["coverage"].append(extra)
            line = self.line(data)
            self.assertEqual(line["coverage"], "invalid")
            self.assertIsNone(line["final_net"])
            self.assertEqual(line["follow_ups"][-1]["kind"], "full_export")

    def test_identity_and_partial_need_both_actions(self):
        data = fixture()
        data["events"] = [event(), event(quantity=9)]
        data["coverage"][0]["complete"] = False
        self.assertEqual([f["kind"] for f in self.line(data)["follow_ups"]], ["identity_reconciliation", "full_export"])

    def test_missing_contacts_explicit(self):
        data = fixture()
        del data["orders"][0]["supplier_contact"]
        data["responsibilities"] = {}
        task = self.line(data)["follow_ups"][0]
        self.assertEqual(task["missing_roles"], ["purchasing_coordinator", "supplier_contact"])
        self.assertEqual(task["recipients"], [])
        self.assertFalse(task["ready_to_address"])

    def test_conflicting_and_invalid_orders(self):
        data = fixture()
        data["orders"].append(dict(data["orders"][0], ordered=11))
        self.assertEqual(self.line(data)["receipt_position"], "blocked")
        self.assertIsNone(self.line(data)["ordered"])
        for value in (None, True, 0, -1, "10"):
            data = fixture()
            data["orders"][0]["ordered"] = value
            self.assertIsNone(self.line(data)["final_net"])
        data["orders"].append({"ordered": 3})
        result = review(data)
        self.assertEqual(len(result["invalid_orders"]), 1)
        self.assertEqual(result["invalid_orders"][0]["follow_ups"][0]["kind"], "identity_reconciliation")

    def test_identical_order_and_coverage_duplicates(self):
        data = fixture()
        data["orders"].append(copy.deepcopy(data["orders"][0]))
        data["coverage"].append(copy.deepcopy(data["coverage"][0]))
        result = review(data)
        self.assertEqual(result["scope_line_count"], 2)
        self.assertEqual(result["lines"][0]["remaining"], 10)

    def test_missing_document_fields_fail(self):
        for field in ("month", "orders", "events", "coverage", "responsibilities"):
            data = fixture()
            del data[field]
            with self.assertRaises(ValueError):
                review(data)

    def test_deterministic_and_input_unchanged(self):
        data = fixture()
        before = copy.deepcopy(data)
        self.assertEqual(review(data), review(data))
        self.assertEqual(data, before)

    def test_cli_success_error_help_and_no_input_mutation(self):
        script = str(Path(__file__).with_name("review.py"))
        with tempfile.TemporaryDirectory(prefix="receiving-check-", dir=Path.cwd()) as directory:
            path = Path(directory) / "input.json"
            payload = json.dumps(fixture())
            path.write_text(payload, encoding="utf-8")
            run = subprocess.run([sys.executable, "-B", script, str(path)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)["scope_line_count"], 2)
            self.assertEqual(path.read_text(encoding="utf-8"), payload)
            for invalid in ('{"month": "2026-08", "month": "2026-09"}', 'NaN', '{'):
                path.write_text(invalid, encoding="utf-8")
                run = subprocess.run([sys.executable, "-B", script, str(path)], capture_output=True, text=True)
                self.assertEqual(run.returncode, 2)
                self.assertEqual(run.stdout, "")
                self.assertFalse(json.loads(run.stderr)["review_produced"])
        help_run = subprocess.run([sys.executable, "-B", script, "--help"], capture_output=True, text=True)
        self.assertEqual(help_run.returncode, 0)
        self.assertIn("UTF-8 JSON input", help_run.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
