#!/usr/bin/env python3
"""Reproduce the Fenwick packing-check decision arithmetic from the supplied CSVs."""

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COHORTS = ROOT / "input" / "sources" / "shipment_cohorts.csv"
OPS = ROOT / "input" / "sources" / "shift_operations.csv"
ORDINARY = {
    "2026-08-03", "2026-08-04", "2026-08-05",
    "2026-08-17", "2026-08-18", "2026-08-19",
}
MIX = {"standard": 0.70, "complex": 0.30}
NEXT_ORDERS_PER_SHIFT = 1440
NEXT_SHIFTS = 20
HOURS_CAP = 102
MISPACK_COST = 55
LABOR_COST = 34


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def whole_nonnegative(row, field, source):
    value = float(row[field])
    assert value >= 0 and value.is_integer(), f"{source}: invalid {field}"
    return int(value)


cohorts = read_csv(COHORTS)
ops = read_csv(OPS)

cohort_required = {
    "shipment_date", "period", "line", "order_band", "shipped_orders",
    "mature_orders", "confirmed_mispack_7d", "station_catches",
}
ops_required = {
    "shipment_date", "period", "line", "productive_labor_hours",
    "overtime_hours", "training_hours", "late_dispatch_orders",
}
assert cohort_required <= set(cohorts[0]), "missing cohort columns"
assert ops_required <= set(ops[0]), "missing operations columns"

cohort_keys = set()
group_bands = defaultdict(set)
band_counts = defaultdict(lambda: [0, 0])
raw_counts = defaultdict(lambda: [0, 0])
shipped_by_group = defaultdict(int)
for line_no, row in enumerate(cohorts, 2):
    key = (row["shipment_date"], row["period"], row["line"], row["order_band"])
    assert key not in cohort_keys, f"duplicate cohort key at line {line_no}"
    cohort_keys.add(key)
    group = key[:3]
    group_bands[group].add(row["order_band"])
    shipped = whole_nonnegative(row, "shipped_orders", f"cohort line {line_no}")
    mature = whole_nonnegative(row, "mature_orders", f"cohort line {line_no}")
    confirmed = whole_nonnegative(row, "confirmed_mispack_7d", f"cohort line {line_no}")
    whole_nonnegative(row, "station_catches", f"cohort line {line_no}")
    assert confirmed <= mature <= shipped, f"invalid cohort counts at line {line_no}"
    shipped_by_group[group] += shipped
    if mature:
        band_counts[(row["period"], row["line"], row["order_band"])][0] += mature
        band_counts[(row["period"], row["line"], row["order_band"])][1] += confirmed
        raw_counts[(row["period"], row["line"])][0] += mature
        raw_counts[(row["period"], row["line"])][1] += confirmed

assert all(bands == set(MIX) for bands in group_bands.values()), "missing or unexpected band row"

op_keys = set()
op_totals = defaultdict(lambda: [0, 0, 0, 0])  # shifts, hours, training, late
for line_no, row in enumerate(ops, 2):
    key = (row["shipment_date"], row["period"], row["line"])
    assert key not in op_keys, f"duplicate operations key at line {line_no}"
    op_keys.add(key)
    productive = float(row["productive_labor_hours"])
    overtime = float(row["overtime_hours"])
    training = float(row["training_hours"])
    late = whole_nonnegative(row, "late_dispatch_orders", f"operations line {line_no}")
    assert 0 <= overtime <= productive and 0 <= training <= productive
    assert late <= shipped_by_group[key]
    if row["shipment_date"] in ORDINARY:
        values = op_totals[(row["period"], row["line"])]
        values[0] += 1
        values[1] += productive
        values[2] += training
        values[3] += late

assert op_keys == set(group_bands), "cohort/operations date-line coverage mismatch"
for date in ORDINARY:
    assert {key[2] for key in op_keys if key[0] == date} == {"Alder", "Birch"}

adjusted = {}
for period in ("baseline", "pilot"):
    for line in ("Alder", "Birch"):
        adjusted[(period, line)] = sum(
            MIX[band] * band_counts[(period, line, band)][1] /
            band_counts[(period, line, band)][0]
            for band in MIX
        )

def ops_metrics(period, line):
    shifts, hours, training, late = op_totals[(period, line)]
    orders = sum(shipped_by_group[g] for g in shipped_by_group
                 if g[1] == period and g[2] == line and g[0] in ORDINARY)
    return {
        "hours_per_shift": hours / shifts,
        "ongoing_hours_per_shift": (hours - training) / shifts,
        "late_rate": late / orders,
    }


baseline_alder = ops_metrics("baseline", "Alder")
pilot_alder = ops_metrics("pilot", "Alder")
baseline_birch = ops_metrics("baseline", "Birch")
pilot_birch = ops_metrics("pilot", "Birch")

quality_did = (
    adjusted[("pilot", "Alder")] - adjusted[("baseline", "Alder")]
    - (adjusted[("pilot", "Birch")] - adjusted[("baseline", "Birch")])
)
labor_did_1200 = (
    pilot_alder["ongoing_hours_per_shift"] - baseline_alder["ongoing_hours_per_shift"]
    - (pilot_birch["ongoing_hours_per_shift"] - baseline_birch["ongoing_hours_per_shift"])
)
scale = NEXT_ORDERS_PER_SHIFT / 1200
next_orders = NEXT_ORDERS_PER_SHIFT * NEXT_SHIFTS

continue_hours = pilot_alder["ongoing_hours_per_shift"] * scale
stop_hours_control_trend = (
    baseline_alder["ongoing_hours_per_shift"]
    + pilot_birch["ongoing_hours_per_shift"]
    - baseline_birch["ongoing_hours_per_shift"]
) * scale
stop_hours_baseline_only = baseline_alder["ongoing_hours_per_shift"] * scale
birch_hours = pilot_birch["ongoing_hours_per_shift"] * scale

continue_quality = adjusted[("pilot", "Alder")]
stop_quality_control_trend = (
    adjusted[("baseline", "Alder")]
    + adjusted[("pilot", "Birch")]
    - adjusted[("baseline", "Birch")]
)
continue_mispacks = continue_quality * next_orders
stop_mispacks = stop_quality_control_trend * next_orders
extra_mispacks = continue_mispacks - stop_mispacks
incremental_labor_hours = labor_did_1200 * scale * NEXT_SHIFTS

print("VALIDATION: PASS")
print(f"rows: {len(cohorts)} cohort, {len(ops)} operations; unique keys and coverage pass")
for period in ("baseline", "pilot"):
    for line in ("Alder", "Birch"):
        mature, confirmed = raw_counts[(period, line)]
        print(f"raw {period} {line}: {confirmed}/{mature} = {confirmed/mature:.3%}")
        print(f"70/30 adjusted {period} {line}: {adjusted[(period, line)]:.3%}")
print(f"quality change-in-changes: {quality_did:.3%}")
print(f"labor change-in-changes per 1,200-order shift: {labor_did_1200:.2f} h")
print(f"Alder continue projection: {continue_hours:.1f} h/shift vs {HOURS_CAP} h cap")
print(f"Alder stop projection (control-trend): {stop_hours_control_trend:.1f} h/shift")
print(f"Alder stop projection (baseline-only): {stop_hours_baseline_only:.1f} h/shift")
print(f"Birch no-check projection: {birch_hours:.1f} h/shift")
print(f"Alder continue late projection: {pilot_alder['late_rate'] * next_orders:.0f}/{next_orders} = {pilot_alder['late_rate']:.3%}")
print(f"Alder stop late projection: {baseline_alder['late_rate'] * next_orders:.0f}/{next_orders} = {baseline_alder['late_rate']:.3%}")
print(f"Birch no-check late projection: {pilot_birch['late_rate'] * next_orders:.0f}/{next_orders} = {pilot_birch['late_rate']:.3%}")
print(f"continue expected mispacks: {continue_mispacks:.1f}; cost ${continue_mispacks * MISPACK_COST:,.0f}")
print(f"stop expected mispacks (control-trend): {stop_mispacks:.1f}; cost ${stop_mispacks * MISPACK_COST:,.0f}")
print(f"continue-minus-stop expected mispack cost: ${extra_mispacks * MISPACK_COST:,.0f}")
print(f"continue-minus-stop incremental labor: {incremental_labor_hours:.1f} h; cost ${incremental_labor_hours * LABOR_COST:,.0f}")
print(f"continue-minus-stop combined modeled cost: ${extra_mispacks * MISPACK_COST + incremental_labor_hours * LABOR_COST:,.0f}")
