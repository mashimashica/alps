"""Reproduce Northbank calculations: python deliverables/reproduce.py.
Standard library only; reads unchanged local CSVs, writes results to stdout.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def read(name, keys):
    with (ROOT / 'input/sources' / name).open() as f:
        rows = list(csv.DictReader(f))
    assert len({tuple(r[k] for k in keys) for r in rows}) == len(rows), 'Duplicate keys'
    for r in rows:
        for k in r.keys() - {'shipment_date', 'period', 'line', 'order_band'}:
            r[k] = int(r[k])
            assert r[k] >= 0
    return rows

c = read('shipment_cohorts.csv', ['shipment_date', 'line', 'order_band'])
o = read('shift_operations.csv', ['shipment_date', 'line'])
assert {(r['shipment_date'], r['line']) for r in c} == {(r['shipment_date'], r['line']) for r in o}
assert all(r['confirmed_mispack_7d'] <= r['mature_orders'] <= r['shipped_orders'] for r in c)
assert all(r['training_hours'] <= r['productive_labor_hours'] and r['overtime_hours'] <= r['productive_labor_hours'] for r in o)
rates, hours = {}, {}
for line in ['East', 'West']:
    for period in ['baseline', 'pilot']:
        rs = [r for r in c if r['line'] == line and r['period'] == period and r['mature_orders']]
        dates = {r['shipment_date'] for r in rs}
        ops = [r for r in o if r['line'] == line and r['shipment_date'] in dates]
        n = sum(r['mature_orders'] for r in rs)
        errors = sum(r['confirmed_mispack_7d'] for r in rs)
        bandrates = []
        print(line, period, 'mature/errors', n, errors, 'aggregate %', 100*errors/n)
        for band in ['standard', 'complex']:
            br = [r for r in rs if r['order_band'] == band]
            bn = sum(r['mature_orders'] for r in br)
            be = sum(r['confirmed_mispack_7d'] for r in br)
            bandrates.append(be/bn)
            print(' ', band, 'orders/errors/share/rate', bn, be, bn/n, be/bn)
        rates[line, period] = .8*bandrates[0] + .2*bandrates[1]
        paid = sum(r['productive_labor_hours'] for r in ops)
        recurring = paid - sum(r['training_hours'] for r in ops)
        hours[line, period] = recurring/n
        late = sum(r['late_dispatch_orders'] for r in ops)
        print('  standardised %', 100*rates[line, period], 'paid/recurring/OT hours', paid, recurring, sum(r['overtime_hours'] for r in ops), 'late/orders', late, n)
        print('  projected hours/shift', recurring/n*1200, 'orders at 84h', 84/(recurring/n))
    latest = [r for r in o if r['line'] == line and r['shipment_date'] == '2026-06-26'][0]
    print(' latest short shift: hours/late/orders', latest['productive_labor_hours'], latest['late_dispatch_orders'], 400)
    allpilot = [r for r in o if r['line'] == line and r['period'] == 'pilot']
    print(' all pilot late/orders', sum(r['late_dispatch_orders'] for r in allpilot), 3400)

beforeafter = rates['East', 'baseline'] - rates['East', 'pilot']
adjusted = beforeafter - (rates['West', 'baseline'] - rates['West', 'pilot'])
contemporary = rates['West', 'pilot'] - rates['East', 'pilot']
volume = 24000
print('Economics: 24,000 East orders, $65/error, $28/hour; training excluded')
for label, improvement, incremental in [
    ('East before/after (favorable attribution)', beforeafter, hours['East', 'pilot']-hours['East', 'baseline']),
    ('Comparator-adjusted changes', adjusted, (hours['East', 'pilot']-hours['East', 'baseline'])-(hours['West', 'pilot']-hours['West', 'baseline'])),
    ('Contemporary West proxy', contemporary, hours['East', 'pilot']-hours['West', 'pilot'])]:
    avoided = volume*improvement
    labor = volume*incremental*28
    print(label, 'rate improvement pp', improvement*100, 'avoided errors', avoided, 'gross $', avoided*65, 'extra hours', volume*incremental, 'labor $', labor, 'net $', avoided*65-labor, 'break-even errors', labor/65)
print('Checks passed: unique keys, source date-line coverage, nonnegative and bounded counts.')
