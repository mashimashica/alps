#!/usr/bin/env python3
"""Reproduce Northbank's supplied snapshot; Python standard library only.

Read-only inputs, deterministic JSON to stdout. Redirect to replace a prior output.
This packet-specific calculation is separate from the reusable Skill.
"""
import argparse
import csv
import json
from pathlib import Path


def read_table(path, key_columns, numeric_columns):
    with path.open(newline='', encoding='utf-8') as source:
        reader = csv.DictReader(source)
        required = set(key_columns) | set(numeric_columns)
        if not required <= set(reader.fieldnames or []):
            raise ValueError(f'{path}: missing columns {required - set(reader.fieldnames or [])}')
        rows = list(reader)
    keys = set()
    for row in rows:
        key = tuple(row[k] for k in key_columns)
        if key in keys:
            raise ValueError(f'{path}: duplicate key {key}')
        keys.add(key)
        for col in numeric_columns:
            row[col] = int(row[col])
            if row[col] < 0:
                raise ValueError(f'{path}: negative {col} at {key}')
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, default=Path(__file__).resolve().parent.parent / 'input/sources', help='Northbank source directory; defaults to sibling input/sources')
    args = parser.parse_args()
    cohorts = read_table(args.sources / 'shipment_cohorts.csv', ['shipment_date', 'line', 'order_band'], ['shipped_orders', 'mature_orders', 'confirmed_mispack_7d', 'station_catches'])
    operations = read_table(args.sources / 'shift_operations.csv', ['shipment_date', 'line'], ['productive_labor_hours', 'overtime_hours', 'training_hours', 'late_dispatch_orders'])
    expected_dates = {'baseline': ['2026-06-01', '2026-06-02', '2026-06-03'], 'pilot': ['2026-06-15', '2026-06-16', '2026-06-17', '2026-06-26']}
    expected_ops = {(d, line) for dates in expected_dates.values() for d in dates for line in ['East', 'West']}
    if {(r['shipment_date'], r['line']) for r in operations} != expected_ops:
        raise ValueError('Unexpected or missing operation keys for this snapshot')
    expected_cohorts = {(d, line, band) for d, line in expected_ops for band in ['standard', 'complex']}
    if {(r['shipment_date'], r['line'], r['order_band']) for r in cohorts} != expected_cohorts:
        raise ValueError('Unexpected or missing cohort keys for this snapshot')
    for row in cohorts + operations:
        if row['shipment_date'] not in expected_dates.get(row['period'], []):
            raise ValueError('Unexpected date/period mapping')
    for row in cohorts:
        if not row['confirmed_mispack_7d'] <= row['mature_orders'] <= row['shipped_orders']:
            raise ValueError('Inconsistent outcome denominator')
        expected_maturity = 0 if row['shipment_date'] == '2026-06-26' else row['shipped_orders']
        if row['mature_orders'] != expected_maturity:
            raise ValueError('Maturity differs from this snapshot; reconsider analysis windows')
    for row in operations:
        shipped = sum(c['shipped_orders'] for c in cohorts if (c['shipment_date'], c['line']) == (row['shipment_date'], row['line']))
        if row['late_dispatch_orders'] > shipped or max(row['overtime_hours'], row['training_hours']) > row['productive_labor_hours']:
            raise ValueError('Inconsistent operational count or labor subset')

    result = {'assumptions': {'snapshot': '2026-06-29', 'full_shift_dates': 'June 1–3 and 15–17', 'planned_shifts': 20, 'orders_per_line_per_shift': 1200, 'standard_weight': 0.8, 'complex_weight': 0.2, 'hours_limit': 84, 'mispack_usd': 65, 'incremental_hour_usd': 28, 'capacity_model': 'linear orders/hours at observed full-shift intensity; target mix workload effect unknown', 'counterfactual': 'East baseline plus West concurrent change, standardized to 80/20; not a causal identification claim'}, 'observed': {}}
    rates = {}
    for period in ['baseline', 'pilot']:
        for line in ['East', 'West']:
            cs = [r for r in cohorts if r['period'] == period and r['line'] == line and r['mature_orders'] > 0]
            dates = {r['shipment_date'] for r in cs}
            ops = [r for r in operations if r['line'] == line and r['shipment_date'] in dates]
            total = lambda rows, col: sum(r[col] for r in rows)
            bands = {}
            for band in ['standard', 'complex']:
                rs = [r for r in cs if r['order_band'] == band]
                n, e = total(rs, 'mature_orders'), total(rs, 'confirmed_mispack_7d')
                bands[band] = {'mature': n, 'errors': e, 'rate': e / n}
            n, e = total(cs, 'mature_orders'), total(cs, 'confirmed_mispack_7d')
            hours = total(ops, 'productive_labor_hours')
            ongoing = hours - total(ops, 'training_hours')
            late = total(ops, 'late_dispatch_orders')
            std80 = 0.8 * bands['standard']['rate'] + 0.2 * bands['complex']['rate']
            std60 = 0.6 * bands['standard']['rate'] + 0.4 * bands['complex']['rate']
            record = {'mature_orders': n, 'errors': e, 'pooled_rate': e/n, 'bands': bands, 'standardized_80_20': std80, 'standardized_60_40': std60, 'productive_hours': hours, 'training_hours': total(ops, 'training_hours'), 'ongoing_hours': ongoing, 'overtime_hours_subset': total(ops, 'overtime_hours'), 'late_orders': late, 'late_rate': late/n, 'actual_orders_per_hour': n/hours, 'ongoing_orders_per_hour': n/ongoing, 'ongoing_hours_per_order': ongoing/n, 'hours_for_1200': 1200*ongoing/n, 'orders_at_84_hours': 84*n/ongoing}
            result['observed'][f'{line}_{period}'] = record
            rates[line, period] = record
    result['latest_short_shift'] = {}
    for line in ['East', 'West']:
        cs = [r for r in cohorts if r['line'] == line and r['shipment_date'] == '2026-06-26']
        op = next(r for r in operations if r['line'] == line and r['shipment_date'] == '2026-06-26')
        shipped = sum(r['shipped_orders'] for r in cs)
        pilot = rates[line, 'pilot']
        result['latest_short_shift'][line] = {'shipped': shipped, 'mature': sum(r['mature_orders'] for r in cs), 'hours': op['productive_labor_hours'], 'late': op['late_dispatch_orders'], 'late_rate': op['late_dispatch_orders']/shipped, 'incorrect_pilot_rate_if_immature_denominator_used': pilot['errors']/(pilot['mature_orders']+shipped)}
    eb, ep, wb, wp = [rates[k] for k in [('East','baseline'), ('East','pilot'), ('West','baseline'), ('West','pilot')]]
    q = 'standardized_80_20'
    counterfactual = eb[q] + wp[q] - wb[q]
    effect = counterfactual - ep[q]
    hours_delta = (ep['ongoing_hours_per_order']-eb['ongoing_hours_per_order'])-(wp['ongoing_hours_per_order']-wb['ongoing_hours_per_order'])
    volume = 24000
    projected_late_east = volume * ep['late_rate']
    projected_late_west = volume * wp['late_rate']
    result['planning'] = {'orders_per_line': volume, 'east_checker_expected_errors': volume*ep[q], 'east_no_checker_adjusted_rate': counterfactual, 'east_no_checker_adjusted_errors': volume*counterfactual, 'west_expected_errors': volume*wp[q], 'adjusted_avoided_errors': volume*effect, 'adjusted_reduction_percentage_points': effect*100, 'adjusted_quality_value_usd': volume*effect*65, 'raw_east_standardized_avoided_errors': volume*(eb[q]-ep[q]), 'adjusted_incremental_hours': volume*hours_delta, 'adjusted_incremental_labor_usd': volume*hours_delta*28, 'adjusted_net_usd': volume*(effect*65-hours_delta*28), 'break_even_reduction_percentage_points': hours_delta*28/65*100, 'zero_checker_effect_net_usd': -volume*hours_delta*28, 'east_own_baseline_incremental_hours': volume*(ep['ongoing_hours_per_order']-eb['ongoing_hours_per_order']), 'concurrent_west_incremental_hours': volume*(ep['ongoing_hours_per_order']-wp['ongoing_hours_per_order']), 'east_hours_total': volume*ep['ongoing_hours_per_order'], 'west_hours_total': volume*wp['ongoing_hours_per_order'], 'authorized_hours_per_line': 20*84, 'east_projected_late': projected_late_east, 'west_projected_late': projected_late_west, 'site_projected_late_rate': (projected_late_east+projected_late_west)/(2*volume), 'site_late_allowance': 2*volume*0.01, 'east_adjusted_no_checker_hours_per_shift': 1200*(eb['ongoing_hours_per_order']+wp['ongoing_hours_per_order']-wb['ongoing_hours_per_order'])}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, ZeroDivisionError) as error:
        raise SystemExit(f'Input/analysis error: {error}')
