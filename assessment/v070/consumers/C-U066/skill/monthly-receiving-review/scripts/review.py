"""Local monthly receiving evidence review; no external effects."""
import argparse
import json
import re
import sys
from pathlib import Path


def string(x):
    return isinstance(x, str) and bool(x.strip())


def month(x):
    return isinstance(x, str) and re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', x) is not None


def integer(x):
    return type(x) is int


def review(data):
    if not isinstance(data, dict) or not month(data.get('month')):
        raise ValueError('month must be YYYY-MM')
    for key in ('orders', 'events', 'coverage'):
        if not isinstance(data.get(key), list):
            raise ValueError(key + ' must be an array')
    if not isinstance(data.get('responsibilities', {}), dict):
        raise ValueError('responsibilities must be an object')
    target = data['month']
    roles = data.get('responsibilities', {})
    diagnostics, lines = [], []
    for i, raw in enumerate(data['orders']):
        row = raw if isinstance(raw, dict) else {}
        line = dict(order_row=i, source=raw, order_id=row.get('order_id'),
                    sku=row.get('sku'), ordered=row.get('ordered'),
                    observed_subtotal=0, event_ids=[], coverage_rows=[], blockers=[], actions=[])
        if not string(row.get('order_id')) or not string(row.get('sku')):
            line['blockers'].append('Invalid order identity')
        if not integer(row.get('ordered')) or row['ordered'] <= 0:
            line['blockers'].append('Invalid ordered quantity')
        lines.append(line)
    def matches(oid, sku=None):
        return [l for l in lines if l['order_id'] == oid and (sku is None or l['sku'] == sku)]
    def block(affected, reason):
        for line in affected:
            if reason not in line['blockers']:
                line['blockers'].append(reason)
    for line in lines:
        if len(matches(line['order_id'], line['sku'])) > 1:
            block([line], 'Duplicate/conflicting order identity')
    groups = {}
    for i, raw in enumerate(data['events']):
        row = raw if isinstance(raw, dict) else {}
        eid = row.get('event_id')
        key = eid if string(eid) else ('invalid', i)
        groups.setdefault(key, []).append((i, row))
    for group in groups.values():
        variants = {json.dumps(row, sort_keys=True) for _, row in group}
        conflict = len(variants) > 1
        for i, row in (group if conflict else group[:1]):
            oid, sku, em = row.get('order_id'), row.get('sku'), row.get('event_month')
            order_lines = matches(oid) if string(oid) else lines
            if string(oid) and not order_lines:
                diagnostics.append(f'events[{i}]: outside supplied order set')
                continue
            if month(em) and em != target:
                diagnostics.append(f'events[{i}]: outside requested month')
                continue
            affected = matches(oid, sku) if string(oid) and string(sku) else order_lines
            if not affected:
                affected = order_lines
                block(affected, f'events[{i}]: unknown SKU for in-scope order')
            if conflict:
                block(affected, f'Conflicting event_id {row.get("event_id")}: rows {[n for n, _ in group]}')
                continue
            if not all(string(row.get(k)) for k in ('event_id', 'order_id', 'sku')) or not month(em) or not integer(row.get('quantity')):
                block(affected, f'events[{i}]: invalid or missing event fields')
                continue
            if not matches(oid, sku):
                continue
            for line in affected:
                line['observed_subtotal'] += row['quantity']
                line['event_ids'].append(row['event_id'])
    for line in lines:
        declarations = []
        for i, raw in enumerate(data['coverage']):
            row = raw if isinstance(raw, dict) else {}
            if row.get('order_id') == line['order_id'] and row.get('sku') == line['sku']:
                if row.get('month') == target:
                    line['coverage_rows'].append(i)
                    declarations.append(row.get('complete'))
                elif not month(row.get('month')):
                    block([line], f'coverage[{i}]: invalid month')
        complete = bool(declarations) and all(v is True for v in declarations)
        if any(type(v) is not bool for v in declarations) or (True in declarations and False in declarations):
            block([line], 'Invalid/conflicting coverage declarations')
        def action(kind, keys, instruction, supplier=False):
            values = [(k, roles.get(k)) for k in keys]
            if supplier:
                values.append(('supplier_contact', line['source'].get('supplier_contact')))
            recipients = [v for _, v in values if string(v)]
            missing = [k for k, v in values if not string(v)]
            line['actions'].append(dict(kind=kind, owner=roles.get('purchasing_coordinator'),
                recipients=recipients, missing_recipients=missing,
                draft=f'{target} / {line["order_id"]} / {line["sku"]}: {instruction}' +
                      (f' Obtain supplied contacts for: {", ".join(missing)}.' if missing else '')))
        if line['blockers']:
            action('reconcile_sources', ['purchasing_coordinator', 'data_steward'],
                   'Reconcile source records before final comparison: ' + '; '.join(line['blockers']))
        if not complete:
            action('complete_export', ['data_steward'], 'Provide or confirm the full event export and completeness declaration for this line and month before final comparison.')
        line['coverage_complete'] = complete
        line['final_net_received'] = None
        line['remaining_quantity'] = None
        line['excess_quantity'] = None
        if line['blockers'] or not complete:
            line['status'] = 'unresolved_evidence'
        else:
            net = line['observed_subtotal']
            line['final_net_received'] = net
            difference = line['ordered'] - net
            line['status'] = 'received_as_ordered' if difference == 0 else 'shortfall' if difference > 0 else 'excess'
            if difference > 0:
                line['remaining_quantity'] = difference
                action('supplier_follow_up', ['purchasing_coordinator'], f'Confirm the remaining receipt of {difference} units and provide the next receiving date/action.', supplier=True)
            elif difference < 0:
                line['excess_quantity'] = -difference
                action('surplus_reconciliation', ['warehouse_lead'], f'Reconcile the surplus of {-difference} units against the order and receiving evidence and report the required correction.')
        if not string(roles.get('purchasing_coordinator')) and line['actions']:
            diagnostics.append(f'orders[{line["order_row"]}]: purchasing coordinator owner is missing')
    return dict(month=target, scope='All supplied order rows for requested month', lines=lines, diagnostics=diagnostics, drafts_only=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, help='New UTF-8 JSON file; defaults to stdout')
    args = parser.parse_args()
    try:
        result = review(json.loads(args.input.read_text(encoding='utf-8')))
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        if args.output:
            with args.output.open('x', encoding='utf-8') as handle:
                handle.write(rendered)
        else:
            print(rendered, end='')
    except (ValueError, OSError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
