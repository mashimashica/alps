"""Synthetic component checks, not a business demonstration."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from review import review


def fixture():
    return {'month': '2026-08',
            'orders': [{'order_id': 'A', 'sku': 'X', 'ordered': 10, 'supplier_contact': 'Supplier'},
                       {'order_id': 'B', 'sku': 'Y', 'ordered': 5, 'supplier_contact': 'Other'}],
            'events': [{'event_id': '1', 'order_id': 'A', 'sku': 'X', 'event_month': '2026-08', 'quantity': 12},
                       {'event_id': '2', 'order_id': 'A', 'sku': 'X', 'event_month': '2026-08', 'quantity': -2}],
            'coverage': [{'order_id': 'A', 'sku': 'X', 'month': '2026-08', 'complete': True},
                         {'order_id': 'B', 'sku': 'Y', 'month': '2026-08', 'complete': True}],
            'responsibilities': {'purchasing_coordinator': 'Coordinator', 'warehouse_lead': 'Warehouse', 'data_steward': 'Steward'}}


class ReviewTests(unittest.TestCase):
    def test_signed_and_zero_complete(self):
        a, b = review(fixture())['lines']
        self.assertEqual((a['net_received'], a['status']), (10, 'received as ordered'))
        self.assertEqual((b['net_received'], b['status']), (0, 'short'))
        self.assertEqual(b['actions'][1]['recipient'], 'Other')

    def test_excess_routing(self):
        d = fixture(); d['events'].pop()
        a = review(d)['lines'][0]
        self.assertEqual(a['difference'], 2)
        self.assertEqual(a['actions'][0]['recipient'], 'Warehouse')

    def test_missing_partial_conflicting_coverage(self):
        for coverage in ([], [False], [True, False], [None]):
            d = fixture(); c = d['coverage'][0]
            d['coverage'] = [dict(c, complete=v) for v in coverage]
            a = review(d)['lines'][0]
            self.assertIsNone(a['net_received'])
            self.assertEqual(a['observed_subtotal'], 10)
            self.assertEqual(a['actions'][0]['recipient'], 'Steward')
            self.assertEqual(len(review(d)['lines']), 2)

    def test_duplicate_and_excluded(self):
        d = fixture(); e = d['events'][0]
        d['events'] += [copy.deepcopy(e), dict(e, event_id='old', event_month='2026-07'), dict(e, event_id='outside', order_id='C')]
        self.assertEqual(review(d)['lines'][0]['net_received'], 10)

    def test_conflict_localization(self):
        d = fixture(); d['events'].append(dict(d['events'][0], quantity=99))
        a, b = review(d)['lines']
        self.assertIsNone(a['net_received'])
        self.assertIsNone(a['observed_subtotal'])
        self.assertEqual(b['status'], 'short')
        self.assertEqual([x['recipient'] for x in a['actions']], ['Coordinator', 'Steward'])

    def test_unknown_sku_blocks_order(self):
        d = fixture(); d['events'].append(dict(d['events'][0], event_id='unknown', sku='Z'))
        a, b = review(d)['lines']
        self.assertEqual(a['status'], 'undetermined')
        self.assertEqual(b['status'], 'short')

    def test_missing_quantity_not_zero(self):
        d = fixture(); del d['events'][0]['quantity']
        self.assertIsNone(review(d)['lines'][0]['observed_subtotal'])

    def test_invalid_order_and_missing_contact(self):
        d = fixture(); d['orders'][0]['ordered'] = True
        self.assertEqual(review(d)['lines'][0]['status'], 'undetermined')
        d = fixture(); del d['orders'][1]['supplier_contact']
        b = review(d)['lines'][1]
        self.assertEqual(b['status'], 'short')
        self.assertIsNone(b['actions'][1]['recipient'])

    def test_conflict_identity_marks_both_lines(self):
        d = fixture(); d['events'].append(dict(d['events'][0], order_id='B', sku='Y'))
        self.assertTrue(all(x['status'] == 'undetermined' for x in review(d)['lines']))

    def test_cli(self):
        # Confine all disposable state to the caller's task working directory.
        with tempfile.TemporaryDirectory(dir='.') as tmp:
            source, output = Path(tmp) / 'input.json', Path(tmp) / 'output.json'
            source.write_text(json.dumps(fixture()), encoding='utf-8')
            before = source.read_bytes()
            cmd = [sys.executable, str(Path(__file__).with_name('review.py')), str(source), '--output', str(output)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text())['lines'][0]['net_received'], 10)
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 2)
            self.assertEqual(source.read_bytes(), before)
            source.write_text('{}', encoding='utf-8')
            self.assertEqual(subprocess.run(cmd[:-2], capture_output=True).returncode, 2)


if __name__ == '__main__':
    unittest.main()
