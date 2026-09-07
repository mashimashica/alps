"""Synthetic component verification, not a demonstration review or agent evaluation."""

import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("receiving_review", ROOT / "scripts" / "review.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def order(oid="PO-A", sku="ITEM", quantity=10):
    return {"order_id": oid, "sku": sku, "ordered": quantity, "supplier_contact": "Supplier A"}


def event(eid="E1", quantity=10, oid="PO-A", sku="ITEM", period="2026-04"):
    return {"event_id": eid, "order_id": oid, "sku": sku, "quantity": quantity, "event_month": period}


def fixture():
    return {"month": "2026-04", "orders": [order()], "events": [event()],
            "coverage": [{"order_id": "PO-A", "sku": "ITEM", "month": "2026-04", "complete": True}],
            "responsibilities": {"purchasing_coordinator": "Coordinator C", "warehouse_lead": "Warehouse W",
                                 "data_steward": "Steward D"}}


def add_line(data, oid, sku):
    data["orders"].append(order(oid, sku))
    data["events"].append(event(f"{oid}-{sku}", 10, oid, sku))
    data["coverage"].append({"order_id": oid, "sku": sku, "month": data["month"], "complete": True})


class EvidenceTests(unittest.TestCase):
    def test_equal_and_input_preserved(self):
        data = fixture()
        original = copy.deepcopy(data)
        line = MODULE.review(data)["lines"][0]
        self.assertEqual(line["status"], "received_as_ordered")
        self.assertEqual(line["final_net"], 10)
        self.assertEqual(line["actions"], [])
        self.assertEqual(data, original)

    def test_signed_return_and_supplier_routing(self):
        data = fixture()
        data["events"].append(event("RETURN", -3))
        line = MODULE.review(data)["lines"][0]
        self.assertEqual((line["final_net"], line["remaining"]), (7, 3))
        action = line["actions"][0]
        self.assertEqual(action["responsible"][0]["name"], "Coordinator C")
        self.assertEqual(action["recipients"][0]["name"], "Supplier A")
        self.assertIn("remaining 3 units", action["draft_seed"])

    def test_negative_net(self):
        data = fixture()
        data["events"] = [event(quantity=-4)]
        line = MODULE.review(data)["lines"][0]
        self.assertEqual((line["final_net"], line["remaining"]), (-4, 14))

    def test_excess_warehouse_action(self):
        data = fixture()
        data["events"][0]["quantity"] = 14
        line = MODULE.review(data)["lines"][0]
        self.assertEqual(line["excess"], 4)
        self.assertEqual(line["actions"][0]["recipients"][0]["name"], "Warehouse W")
        self.assertIn("surplus of 4 units", line["actions"][0]["draft_seed"])

    def test_partial_subtotal_never_final(self):
        data = fixture()
        data["coverage"][0]["complete"] = False
        line = MODULE.review(data)["lines"][0]
        self.assertEqual(line["observed_net"], 10)
        self.assertIsNone(line["final_net"])
        self.assertEqual(line["status"], "incomplete_evidence")
        self.assertEqual([a["kind"] for a in line["actions"]], ["confirm_export"])
        self.assertEqual(line["actions"][0]["recipients"][0]["name"], "Steward D")

    def test_missing_coverage_keeps_scope(self):
        data = fixture()
        add_line(data, "PO-B", "B")
        data["coverage"] = data["coverage"][:1]
        result = MODULE.review(data)
        self.assertEqual(result["scope"]["unique_identifiable_lines"], 2)
        self.assertEqual(result["lines"][0]["status"], "received_as_ordered")
        self.assertEqual(result["lines"][1]["coverage"], "missing")
        self.assertIsNone(result["lines"][1]["final_net"])

    def test_zero_only_with_usable_empty_export(self):
        data = fixture()
        data["events"] = []
        self.assertEqual(MODULE.review(data)["lines"][0]["remaining"], 10)
        del data["events"]
        line = MODULE.review(data)["lines"][0]
        self.assertIsNone(line["observed_net"])
        self.assertIsNone(line["valid_event_subtotal"])
        self.assertIsNone(line["final_net"])

    def test_exact_event_copies_count_once(self):
        data = fixture()
        data["events"].append(copy.deepcopy(data["events"][0]))
        result = MODULE.review(data)
        self.assertEqual(result["lines"][0]["final_net"], 10)
        self.assertEqual(result["excluded_events"][0]["reason"], "exact_duplicate")

    def test_conflicting_event_id_blocks_both_affected_lines(self):
        data = fixture()
        add_line(data, "PO-B", "B")
        add_line(data, "PO-C", "C")
        data["events"][1]["event_id"] = "E1"
        result = MODULE.review(data)
        self.assertEqual([l["status"] for l in result["lines"]],
                         ["blocked_evidence", "blocked_evidence", "received_as_ordered"])
        self.assertEqual([p["name"] for p in result["lines"][0]["actions"][0]["recipients"]],
                         ["Coordinator C", "Steward D"])

    def test_conflict_with_outside_month_variant(self):
        data = fixture()
        data["events"].append(event(period="2026-03"))
        self.assertEqual(MODULE.review(data)["lines"][0]["status"], "blocked_evidence")

    def test_unknown_sku_blocks_order_not_other_order(self):
        data = fixture()
        add_line(data, "PO-A", "SECOND")
        add_line(data, "PO-B", "B")
        data["events"].append(event("UNKNOWN", sku="UNKNOWN"))
        self.assertEqual([l["status"] for l in MODULE.review(data)["lines"]],
                         ["blocked_evidence", "blocked_evidence", "received_as_ordered"])

    def test_outside_month_and_order_do_not_contribute(self):
        data = fixture()
        data["events"].extend([event("OLD", 99, sku="UNKNOWN", period="2026-03"),
                               event("OUTSIDE", 99, oid="PO-OTHER")])
        result = MODULE.review(data)
        self.assertEqual(result["lines"][0]["final_net"], 10)
        self.assertEqual(len(result["excluded_events"]), 2)

    def test_malformed_quantity_is_local_and_not_zero(self):
        for quantity in [None, True, 3.5, "10"]:
            with self.subTest(quantity=quantity):
                data = fixture()
                add_line(data, "PO-B", "B")
                data["events"][0]["quantity"] = quantity
                lines = MODULE.review(data)["lines"]
                self.assertIsNone(lines[0]["observed_net"])
                self.assertIsNone(lines[0]["final_net"])
                self.assertEqual(lines[1]["final_net"], 10)

    def test_unknown_event_month_prevents_final(self):
        data = fixture()
        del data["events"][0]["event_month"]
        self.assertEqual(MODULE.review(data)["lines"][0]["status"], "blocked_evidence")

    def test_unattributable_event_blocks_all_identifiable_lines(self):
        data = fixture()
        add_line(data, "PO-B", "B")
        data["events"].append(None)
        self.assertTrue(all(l["status"] == "blocked_evidence" for l in MODULE.review(data)["lines"]))

    def test_bad_orders_visible_duplicates_consolidated(self):
        data = fixture()
        data["orders"].extend([copy.deepcopy(data["orders"][0]), None, order("PO-B", "B", True)])
        result = MODULE.review(data)
        self.assertEqual(result["scope"]["supplied_order_records"], 4)
        self.assertEqual(result["lines"][0]["order_record_indexes"], [0, 1])
        self.assertEqual(result["lines"][1]["status"], "invalid_order")
        self.assertIsNone(result["lines"][2]["ordered"])

    def test_conflicting_order_keeps_other_lines_sound(self):
        data = fixture()
        data["orders"].append(order(quantity=12))
        add_line(data, "PO-B", "B")
        result = MODULE.review(data)
        self.assertEqual(result["lines"][0]["status"], "blocked_evidence")
        self.assertIsNone(result["lines"][0]["ordered"])
        self.assertEqual(result["lines"][1]["final_net"], 10)

    def test_coverage_conflict_and_nonboolean(self):
        for value in [False, "true", 1, None]:
            with self.subTest(value=value):
                data = fixture()
                extra = dict(data["coverage"][0], complete=value)
                data["coverage"].append(extra)
                line = MODULE.review(data)["lines"][0]
                self.assertEqual(line["coverage"], "invalid")
                self.assertIsNone(line["final_net"])

    def test_duplicate_and_irrelevant_coverage(self):
        data = fixture()
        data["coverage"].extend([copy.deepcopy(data["coverage"][0]),
                                  dict(data["coverage"][0], sku="EXTRA", complete=False),
                                  dict(data["coverage"][0], month="2026-03", complete=False)])
        self.assertEqual(MODULE.review(data)["lines"][0]["final_net"], 10)

    def test_missing_recipients_do_not_invent_or_change_position(self):
        data = fixture()
        data["events"] = []
        data["responsibilities"] = {}
        del data["orders"][0]["supplier_contact"]
        line = MODULE.review(data)["lines"][0]
        self.assertEqual(line["status"], "shortfall")
        self.assertEqual(line["actions"][0]["missing_routing"],
                         ["purchasing_coordinator", "supplier_contact"])
        self.assertIn("[recipient required: supplier_contact]", line["actions"][0]["draft_seed"])

    def test_combined_gaps_get_both_actions(self):
        data = fixture()
        data["events"][0]["quantity"] = None
        data["coverage"] = []
        actions = MODULE.review(data)["lines"][0]["actions"]
        self.assertEqual([a["kind"] for a in actions], ["reconcile_sources", "confirm_export"])

    def test_root_and_scope_validation(self):
        for data in [[], {}, dict(fixture(), month="2026-13"), dict(fixture(), month="0000-01"),
                     dict(fixture(), orders=None)]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                MODULE.review(data)


class InterfaceTests(unittest.TestCase):
    def test_cli_write_no_overwrite_no_input_mutation(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as temporary:
            source = Path(temporary) / "input.json"
            target = Path(temporary) / "report.json"
            original = json.dumps(fixture())
            source.write_text(original, encoding="utf-8")
            self.assertEqual(MODULE.main(["--input", str(source), "--output", str(target)]), 0)
            report = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(report["lines"][0]["status"], "received_as_ordered")
            with contextlib.redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(MODULE.main(["--input", str(source), "--output", str(target)]), 2)
                self.assertIn("File exists", errors.getvalue())
            self.assertEqual(source.read_text(encoding="utf-8"), original)

    def test_cli_rejects_ambiguous_json_and_reports_unresolved_successfully(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as temporary:
            source = Path(temporary) / "input.json"
            for raw in ['{"month":"2026-04","month":"2026-05"}', '{"quantity":NaN}', '{']:
                source.write_text(raw, encoding="utf-8")
                with contextlib.redirect_stderr(io.StringIO()) as errors:
                    self.assertEqual(MODULE.main(["--input", str(source)]), 2)
                    self.assertIn("receiving-review:", errors.getvalue())
            data = fixture()
            data["coverage"] = []
            source.write_text(json.dumps(data), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(MODULE.main(["--input", str(source)]), 0)
            self.assertEqual(json.loads(output.getvalue())["lines"][0]["status"], "incomplete_evidence")


if __name__ == "__main__":
    unittest.main()
