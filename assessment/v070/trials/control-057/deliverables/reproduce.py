"""Reproduce Northbank tables with Python 3 standard library; prints JSON, writes nothing.
Run from the task directory: python deliverables/reproduce.py
Optional: python deliverables/reproduce.py --sources input/sources
"""
import argparse
import csv
import json
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--sources', type=Path, default=Path(__file__).resolve().parent.parent / 'input/sources')
a = p.parse_args()
def read(name, keys, nums):
    with (a.sources / name).open() as f:
        rows = list(csv.DictReader(f))
    seen = set()
    for r in rows:
        key = tuple(r[k] for k in keys)
        assert key not in seen, ('duplicate', key)
        seen.add(key)
        for k in nums:
            r[k] = int(r[k])
            assert r[k] >= 0
    return rows
c = read('shipment_cohorts.csv', ['shipment_date','line','order_band'], ['shipped_orders','mature_orders','confirmed_mispack_7d','station_catches'])
s = read('shift_operations.csv', ['shipment_date','line'], ['productive_labor_hours','overtime_hours','training_hours','late_dispatch_orders'])
assert {(r['shipment_date'],r['line']) for r in c} == {(r['shipment_date'],r['line']) for r in s}
for r in c:
    assert r['confirmed_mispack_7d'] <= r['mature_orders'] <= r['shipped_orders']
for r in s:
    assert r['overtime_hours'] <= r['productive_labor_hours'] and r['training_hours'] <= r['productive_labor_hours']
result = {}
rates = {}
for line in ['East','West']:
    for period in ['baseline','pilot']:
        rows = [r for r in c if r['line']==line and r['period']==period and r['mature_orders']>0]
        dates = {r['shipment_date'] for r in rows}
        ops = [r for r in s if r['line']==line and r['shipment_date'] in dates]
        total = lambda field: sum(r[field] for r in rows)
        bands = {}
        for band in ['standard','complex']:
            b = [r for r in rows if r['order_band']==band]
            n = sum(r['mature_orders'] for r in b)
            e = sum(r['confirmed_mispack_7d'] for r in b)
            bands[band] = {'orders':n,'errors':e,'rate':e/n}
        weighted = .8*bands['standard']['rate'] + .2*bands['complex']['rate']
        rates[line,period] = weighted
        hours = sum(r['productive_labor_hours'] for r in ops)
        recurring = hours-sum(r['training_hours'] for r in ops)
        late = sum(r['late_dispatch_orders'] for r in ops)
        result[line+' '+period] = dict(bands=bands, mature_orders=total('mature_orders'),errors=total('confirmed_mispack_7d'),raw_rate=total('confirmed_mispack_7d')/total('mature_orders'),planned_mix_rate=weighted,productive_hours=hours,recurring_hours=recurring,overtime_hours=sum(r['overtime_hours'] for r in ops),late=late,late_rate=late/total('shipped_orders'),hours_per_1200=recurring/total('shipped_orders')*1200,capacity_at_84=84/(recurring/total('shipped_orders')))
    latest = [r for r in c if r['line']==line and r['shipment_date']=='2026-06-26']
    op = next(r for r in s if r['line']==line and r['shipment_date']=='2026-06-26')
    result[line+' latest'] = dict(shipped=sum(r['shipped_orders'] for r in latest),mature=sum(r['mature_orders'] for r in latest),hours=op['productive_labor_hours'],late=op['late_dispatch_orders'])
volume = 24000
benefits = {'own_before_after':rates['East','baseline']-rates['East','pilot'],'current_comparator':rates['West','pilot']-rates['East','pilot'],'comparator_adjusted_change':(rates['East','baseline']-rates['East','pilot'])-(rates['West','baseline']-rates['West','pilot'])}
costs = {'own_before_after':(234-207)/3000*volume*28,'current_comparator':(234-209)/3000*volume*28,'comparator_adjusted_change':((234-207)-(209-205))/3000*volume*28}
result['economics_24000_East_orders'] = {k:dict(rate_benefit=v,avoided_errors=v*volume,gross_value=v*volume*65,incremental_labor_cost=costs[k],net_value=v*volume*65-costs[k],break_even_avoided_errors=costs[k]/65) for k,v in benefits.items()}
print(json.dumps(result, indent=2))
