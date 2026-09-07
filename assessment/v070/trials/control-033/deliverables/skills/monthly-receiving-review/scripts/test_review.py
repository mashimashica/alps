"""Synthetic component checks; no business records or network access."""
import copy
import unittest
from review import review


def fixture():
    return dict(month='2026-08', orders=[dict(order_id='A', sku='X', ordered=10, supplier_contact='Supplier'),
                dict(order_id='B', sku='Y', ordered=5, supplier_contact='Other')],
                events=[dict(event_id='e', order_id='A', sku='X', event_month='2026-08', quantity=8)],
                coverage=[dict(order_id='A', sku='X', month='2026-08', complete=True),
                          dict(order_id='B', sku='Y', month='2026-08', complete=True)],
                responsibilities=dict(purchasing_coordinator='Buyer', warehouse_lead='Warehouse', data_steward='Data'))


class ReviewTests(unittest.TestCase):
    def test_shortfall_and_complete_empty(self):
        lines = review(fixture())['lines']
        self.assertEqual([l['remaining_quantity'] for l in lines], [2, 5])
        self.assertEqual(lines[0]['actions'][0]['recipients'], ['Buyer', 'Supplier'])

    def test_equal_excess_and_signed_return(self):
        for quantity, status in [(10, 'received_as_ordered'), (11, 'excess'), (-2, 'shortfall')]:
            d = fixture()
            d['events'][0]['quantity'] = quantity
            line = review(d)['lines'][0]
            self.assertEqual(line['status'], status)
            if quantity == -2:
                self.assertEqual(line['remaining_quantity'], 12)
            if quantity == 11:
                self.assertEqual(line['actions'][0]['recipients'], ['Warehouse'])

    def test_dedup_and_month_filter(self):
        d = fixture()
        d['events'] += [copy.deepcopy(d['events'][0]), dict(d['events'][0], event_id='old', event_month='2026-07'),
                        dict(d['events'][0], event_id='return', quantity=-3)]
        self.assertEqual(review(d)['lines'][0]['final_net_received'], 5)

    def test_partial_and_missing_coverage(self):
        for coverage in [[], [dict(order_id='A', sku='X', month='2026-08', complete=False)]]:
            d = fixture()
            d['coverage'] = coverage
            line = review(d)['lines'][0]
            self.assertEqual(line['observed_subtotal'], 8)
            self.assertIsNone(line['final_net_received'])
            self.assertEqual(line['actions'][0]['recipients'], ['Data'])
            self.assertEqual(len(review(d)['lines']), 2)

    def test_unknown_sku_localizes_to_order(self):
        d = fixture()
        d['events'].append(dict(d['events'][0], event_id='unknown', sku='Z'))
        lines = review(d)['lines']
        self.assertEqual(lines[0]['status'], 'unresolved_evidence')
        self.assertEqual(lines[1]['status'], 'shortfall')

    def test_outside_order_has_no_effect(self):
        d = fixture()
        d['events'].append(dict(d['events'][0], order_id='OUT', quantity=999))
        self.assertEqual(review(d)['lines'][1]['final_net_received'], 0)
        # The shared event ID still conflicts with its in-scope variant.
        self.assertEqual(review(d)['lines'][0]['status'], 'unresolved_evidence')
        d['events'][1]['event_id'] = 'outside'
        self.assertEqual(review(d)['lines'][0]['final_net_received'], 8)

    def test_conflict_blocks_both_lines(self):
        d = fixture()
        d['events'].append(dict(d['events'][0], order_id='B', sku='Y'))
        self.assertTrue(all(l['status'] == 'unresolved_evidence' for l in review(d)['lines']))

    def test_invalid_quantity_not_zero(self):
        for quantity in [None, True, '8', 1.5]:
            d = fixture()
            d['events'][0]['quantity'] = quantity
            self.assertIsNone(review(d)['lines'][0]['final_net_received'])
            self.assertEqual(review(d)['lines'][1]['status'], 'shortfall')

    def test_duplicate_orders_and_missing_recipients(self):
        d = fixture()
        d['orders'].append(copy.deepcopy(d['orders'][0]))
        self.assertEqual(review(d)['lines'][0]['status'], 'unresolved_evidence')
        d = fixture()
        d['responsibilities'] = {}
        del d['orders'][0]['supplier_contact']
        self.assertEqual(review(d)['lines'][0]['actions'][0]['missing_recipients'], ['purchasing_coordinator', 'supplier_contact'])

    def test_coverage_conflict(self):
        d = fixture()
        d['coverage'].append(dict(d['coverage'][0], complete=False))
        line = review(d)['lines'][0]
        self.assertEqual({a['kind'] for a in line['actions']}, {'reconcile_sources', 'complete_export'})


if __name__ == '__main__':
    unittest.main()
