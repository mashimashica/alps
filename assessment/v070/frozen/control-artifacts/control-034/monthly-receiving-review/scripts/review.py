#!/usr/bin/env python3
"""Deterministic local evidence processing; no external actions."""
import argparse
import json
import re
import sys


def string(v):
    return isinstance(v, str) and bool(v.strip())


def month(v):
    return isinstance(v, str) and bool(re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])", v)) and not v.startswith('0000')


def integer(v):
    return type(v) is int


def review(data):
    if not isinstance(data, dict) or not month(data.get('month')):
        raise ValueError('month must be YYYY-MM')
    for field in ('orders', 'events', 'coverage'):
        if not isinstance(data.get(field), list):
            raise ValueError(field + ' must be an array')
    if not isinstance(data.get('responsibilities'), dict):
        raise ValueError('responsibilities must be an object')
    m = data['month']
    issues, states, rows = [], {}, []
    for i, order in enumerate(data['orders']):
        if not isinstance(order, dict) or not all(string(order.get(k)) for k in ('order_id', 'sku')):
            raise ValueError(f'orders[{i}] lacks usable order_id/sku; scope must be corrected')
        key = (order['order_id'], order['sku'])
        rows.append((i, order, key))
        st = states.setdefault(key, {'orders': [], 'blockers': [], 'events': [], 'sum': 0})
        st['orders'].append(order)
        if not integer(order.get('ordered')) or order['ordered'] <= 0:
            st['blockers'].append(f'orders[{i}]: invalid ordered quantity')
    order_ids = {key[0] for key in states}
    for st in states.values():
        if len({json.dumps(o, sort_keys=True) for o in st['orders']}) > 1:
            st['blockers'].append('conflicting order rows')

    def affected(e):
        if not isinstance(e, dict):
            return list(states)
        if month(e.get('event_month')) and e['event_month'] != m:
            return []
        oid, sku = e.get('order_id'), e.get('sku')
        if string(oid) and oid not in order_ids:
            return []
        if not string(oid):
            return list(states)
        if string(sku) and (oid, sku) in states:
            return [(oid, sku)]
        return [key for key in states if key[0] == oid]

    groups = {}
    for i, event in enumerate(data['events']):
        eid = event.get('event_id') if isinstance(event, dict) else None
        token = ('id', eid) if string(eid) else ('row', i)
        group = groups.setdefault(token, [])
        # JSON serialization distinguishes booleans from integers.
        canonical = json.dumps(event, sort_keys=True, ensure_ascii=False)
        if not any(canonical == old[2] for old in group):
            group.append((i, event, canonical))
    for group in groups.values():
        if len(group) > 1:
            keys = set(k for _, e, _ in group for k in affected(e))
            reason = f'conflicting event_id {group[0][1]["event_id"]}; source rows {[i for i, _, _ in group]}'
            issues.append(reason)
            for key in keys:
                states[key]['blockers'].append(reason)
            continue
        i, e, _ = group[0]
        keys = affected(e)
        if not keys:
            issues.append(f'events[{i}] excluded: other month or outside order scope')
            continue
        valid = isinstance(e, dict) and all(string(e.get(k)) for k in ('event_id', 'order_id', 'sku')) and month(e.get('event_month')) and integer(e.get('quantity'))
        key = (e.get('order_id'), e.get('sku')) if isinstance(e, dict) and string(e.get('order_id')) and string(e.get('sku')) else None
        if not valid or key not in states:
            reason = f'events[{i}]: invalid event or order/SKU identity; reconcile source record'
            issues.append(reason)
            for k in keys:
                states[k]['blockers'].append(reason)
        else:
            states[key]['sum'] += e['quantity']
            states[key]['events'].append(e['event_id'])

    lines = []
    for i, order, key in rows:
        st = states[key]
        declarations = [c for c in data['coverage'] if isinstance(c, dict) and c.get('order_id') == key[0] and c.get('sku') == key[1] and c.get('month') == m]
        complete = bool(declarations) and all(c.get('complete') is True for c in declarations)
        coverage = 'complete' if complete else ('missing' if not declarations else 'incomplete or conflicting')
        blockers = list(dict.fromkeys(st['blockers']))
        net = st['sum'] if complete and not blockers else None
        diff = net - order['ordered'] if net is not None else None
        status = 'undetermined' if diff is None else ('received as ordered' if diff == 0 else ('short' if diff < 0 else 'excess'))
        actions = []

        def action(role, recipient, next_action):
            recipient = recipient if string(recipient) else None
            actions.append({'responsible_role': role, 'recipient': recipient,
                            'next_action': next_action, 'routing': 'ready' if recipient else 'unresolved: request supplied recipient',
                            'draft': f'To: {recipient or "[recipient needed]"}\nSubject: {m} receiving review {key[0]} / {key[1]}\n{next_action}\nDraft only; not sent.'})

        resp = data['responsibilities']
        if blockers:
            for role in ('purchasing_coordinator', 'data_steward'):
                action(role, resp.get(role), 'Reconcile the identified order/event source records before a final comparison: ' + '; '.join(blockers))
        if not complete:
            action('data_steward', resp.get('data_steward'), f'Provide or confirm the full {m} export and a consistent completeness declaration for {key[0]} / {key[1]} before final comparison.')
        if status == 'short':
            action('purchasing_coordinator', resp.get('purchasing_coordinator'), f'Follow up with the supplied supplier contact about the remaining {-diff} units; ordered {order["ordered"]}, net received {net}.')
            action('supplier_contact', order.get('supplier_contact'), f'Please confirm the remaining receipt of {-diff} units for {key[0]} / {key[1]} and the expected receipt date. Ordered {order["ordered"]}; net received in {m}: {net}.')
        elif status == 'excess':
            action('warehouse_lead', resp.get('warehouse_lead'), f'Reconcile the surplus of {diff} units against the order and receiving evidence; ordered {order["ordered"]}, net received {net}.')
        lines.append({'source_order_row': i, 'order_id': key[0], 'sku': key[1], 'ordered': order.get('ordered'),
                      'coverage': coverage, 'coverage_records': declarations, 'blockers': blockers,
                      'event_ids': st['events'], 'observed_subtotal': st['sum'] if not blockers else None,
                      'net_received': net, 'difference': diff, 'status': status, 'actions': actions})
    for i, c in enumerate(data['coverage']):
        if not isinstance(c, dict) or not all(string(c.get(k)) for k in ('order_id', 'sku')) or not month(c.get('month')) or type(c.get('complete')) is not bool:
            issues.append(f'coverage[{i}]: malformed declaration; cannot establish completeness')
    return {'month': m, 'issues': issues, 'lines': lines}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='UTF-8 monthly review JSON input')
    parser.add_argument('--output', help='New JSON report path; default stdout; refuses overwrite')
    args = parser.parse_args()
    try:
        with open(args.input, encoding='utf-8') as source:
            data = json.load(source)
        report = json.dumps(review(data), ensure_ascii=False, indent=2, allow_nan=False) + '\n'
        if args.output:
            with open(args.output, 'x', encoding='utf-8') as target:
                target.write(report)
        else:
            sys.stdout.write(report)
    except (ValueError, OSError) as exc:
        print(f'review: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
