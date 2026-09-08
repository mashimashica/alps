#!/usr/bin/env python3
"""Reproduce the Fenwick packing-check decision arithmetic from the supplied CSVs."""

import csv
import sys
from collections import defaultdict
from pathlib import Path


def pct(numerator, denominator):
    return 100 * numerator / denominator


def main():
    source_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "input/sources")

    with (source_dir / "shipment_cohorts.csv").open(newline="") as handle:
        cohorts = list(csv.DictReader(handle))
    with (source_dir / "shift_operations.csv").open(newline="") as handle:
        operations = list(csv.DictReader(handle))

    # Customer outcomes: mature orders only. Aggregate cohort rows by period/line/band.
    quality = defaultdict(lambda: [0, 0])
    for row in cohorts:
        mature = int(row["mature_orders"])
        errors = int(row["confirmed_mispack_7d"])
        if mature == 0:
            assert errors == 0, "immature cohort unexpectedly has an outcome count"
            continue
        key = (row["period"], row["line"], row["order_band"])
        quality[key][0] += mature
        quality[key][1] += errors

    print("MATURE QUALITY BY PERIOD / LINE / BAND")
    for key in sorted(quality):
        mature, errors = quality[key]
        print(f"{key[0]},{key[1]},{key[2]}: {errors}/{mature} = {pct(errors, mature):.3f}%")

    print("\nMATURE QUALITY BY PERIOD / LINE (raw observed mix)")
    for period in ("baseline", "pilot"):
        for line in ("Alder", "Birch"):
            mature = sum(quality[(period, line, band)][0] for band in ("standard", "complex"))
            errors = sum(quality[(period, line, band)][1] for band in ("standard", "complex"))
            print(f"{period},{line}: {errors}/{mature} = {pct(errors, mature):.3f}%")

    # Standardize each period/line to the planned next-period 70%/30% mix.
    standardized = {}
    print("\nQUALITY STANDARDIZED TO PLANNED 70% STANDARD / 30% COMPLEX MIX")
    for period in ("baseline", "pilot"):
        for line in ("Alder", "Birch"):
            standard = quality[(period, line, "standard")]
            complex_ = quality[(period, line, "complex")]
            rate = 0.7 * standard[1] / standard[0] + 0.3 * complex_[1] / complex_[0]
            standardized[(period, line)] = rate
            print(f"{period},{line}: {100 * rate:.3f}%")

    alder_change = standardized[("pilot", "Alder")] - standardized[("baseline", "Alder")]
    birch_change = standardized[("pilot", "Birch")] - standardized[("baseline", "Birch")]
    did = alder_change - birch_change
    print(f"mix-adjusted change Alder: {100 * alder_change:+.3f} percentage points")
    print(f"mix-adjusted change Birch: {100 * birch_change:+.3f} percentage points")
    print(f"difference in changes (Alder minus Birch): {100 * did:+.3f} percentage points")

    # Full shifts are the three baseline and the three Aug 17-19 pilot dates.
    # Aug 28 is explicitly a short shift and excluded from full-shift capacity evidence.
    full = [row for row in operations if row["shipment_date"] != "2026-08-28"]
    ops = defaultdict(lambda: [0, 0, 0, 0])  # shifts, productive, training, late
    for row in full:
        key = (row["period"], row["line"])
        ops[key][0] += 1
        ops[key][1] += float(row["productive_labor_hours"])
        ops[key][2] += float(row["training_hours"])
        ops[key][3] += int(row["late_dispatch_orders"])

    print("\nFULL-SHIFT OPERATIONS")
    for period in ("baseline", "pilot"):
        for line in ("Alder", "Birch"):
            shifts, productive, training, late = ops[(period, line)]
            routine_productive = productive - training
            shipped = shifts * 1200
            print(
                f"{period},{line}: productive={productive:g} h; training={training:g} h; "
                f"routine={routine_productive:g} h; routine_avg={routine_productive / shifts:.3f} h/shift; "
                f"late={late}/{shipped} = {pct(late, shipped):.3f}%"
            )

    planned_orders_per_shift = 1440
    planned_shifts = 20
    planned_orders = planned_orders_per_shift * planned_shifts
    hour_cap = 102
    avoidable_cost = 55
    labor_cost = 34

    alder_check_hours_per_order = (ops[("pilot", "Alder")][1] - ops[("pilot", "Alder")][2]) / (3 * 1200)
    alder_no_check_hours_per_order = ops[("baseline", "Alder")][1] / (3 * 1200)
    projected_check_hours = alder_check_hours_per_order * planned_orders_per_shift
    projected_no_check_hours = alder_no_check_hours_per_order * planned_orders_per_shift
    # A second no-check scenario carries Birch's +2 h/1,200 common period change onto
    # Alder's baseline. The remaining 6 h/1,200 difference-in-changes is the rough
    # incremental-labor scenario for the check; neither component is causal proof.
    birch_hour_change_per_shift = (
        ops[("pilot", "Birch")][1] / ops[("pilot", "Birch")][0]
        - ops[("baseline", "Birch")][1] / ops[("baseline", "Birch")][0]
    )
    adjusted_no_check_1200 = ops[("baseline", "Alder")][1] / 3 + birch_hour_change_per_shift
    adjusted_no_check_hours = adjusted_no_check_1200 / 1200 * planned_orders_per_shift
    incremental_check_hours = projected_check_hours - adjusted_no_check_hours
    birch_projected_hours = (ops[("pilot", "Birch")][1] / 3600) * planned_orders_per_shift
    projected_check_late = ops[("pilot", "Alder")][3] / 3600 * planned_orders
    projected_no_check_late = ops[("baseline", "Alder")][3] / 3600 * planned_orders
    projected_birch_late = ops[("pilot", "Birch")][3] / 3600 * planned_orders
    allowed_late = 0.01 * planned_orders

    print("\nNEXT-PERIOD PLANNING SCENARIOS (constant observed rates; not causal proof)")
    print(f"Alder all-order check labor: {alder_check_hours_per_order:.6f} h/order x 1,440 = {projected_check_hours:.1f} h/shift; cap={hour_cap} h")
    print(f"Alder baseline no-check labor: {alder_no_check_hours_per_order:.6f} h/order x 1,440 = {projected_no_check_hours:.1f} h/shift")
    print(f"Alder no-check plus Birch's common +2 h/1,200 period change: {adjusted_no_check_hours:.1f} h/shift")
    print(f"Birch pilot no-check labor: {birch_projected_hours:.1f} h/shift")
    print(f"Alder all-order check late dispatch: {ops[('pilot', 'Alder')][3]}/3600 x {planned_orders} = {projected_check_late:.0f}; commitment maximum={allowed_late:.0f}")
    print(f"Alder baseline no-check late dispatch: {ops[('baseline', 'Alder')][3]}/3600 x {planned_orders} = {projected_no_check_late:.0f}")
    print(f"Birch pilot no-check late dispatch: {ops[('pilot', 'Birch')][3]}/3600 x {planned_orders} = {projected_birch_late:.0f}")
    print(f"Difference-in-changes labor scenario for check: {incremental_check_hours:.1f} h/shift")
    print(f"Planning value of that incremental labor over 20 shifts: ${incremental_check_hours * planned_shifts * labor_cost:,.0f}")

    # Transparent quality/cost scenarios. They are not attributed savings.
    future_baseline_errors = standardized[("baseline", "Alder")] * planned_orders
    future_pilot_errors = standardized[("pilot", "Alder")] * planned_orders
    did_errors = did * planned_orders
    print("\nQUALITY / COST SCENARIOS FOR ALDER (70/30 mix, 28,800 orders)")
    print(f"Alder baseline mix-adjusted rate: {100 * standardized[('baseline', 'Alder')]:.3f}% -> {future_baseline_errors:.1f} errors -> ${future_baseline_errors * avoidable_cost:,.0f}")
    print(f"Alder pilot mix-adjusted rate: {100 * standardized[('pilot', 'Alder')]:.3f}% -> {future_pilot_errors:.1f} errors -> ${future_pilot_errors * avoidable_cost:,.0f}")
    print(f"Difference-in-changes scenario: {100 * did:+.3f} pp -> {did_errors:+.1f} errors -> ${did_errors * avoidable_cost:+,.0f}; not an attributed causal effect")


if __name__ == "__main__":
    main()
