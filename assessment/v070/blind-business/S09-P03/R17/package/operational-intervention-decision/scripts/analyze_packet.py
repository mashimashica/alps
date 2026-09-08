#!/usr/bin/env python3
"""Produce a reviewable Markdown basis from shipment-cohort and shift CSVs."""

import argparse
import csv
from collections import defaultdict
from pathlib import Path


SHIP_REQUIRED = {"shipment_date", "period", "line", "order_band", "shipped_orders", "mature_orders", "confirmed_mispack_7d"}
OPS_REQUIRED = {"shipment_date", "period", "line", "productive_labor_hours", "overtime_hours", "training_hours", "late_dispatch_orders"}


def parse_mix(value):
    result = {}
    for item in value.split(","):
        band, share = item.split("=", 1)
        result[band.strip()] = float(share)
    if not result or abs(sum(result.values()) - 1) > 1e-9 or any(v < 0 for v in result.values()):
        raise argparse.ArgumentTypeError("mix shares must be nonnegative and sum to 1")
    return result


def read_rows(path, required):
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path}: missing columns: {', '.join(sorted(missing))}")
        return list(reader)


def pct(n, d):
    return "n/a" if not d else f"{100*n/d:.2f}%"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("shipment_csv", type=Path)
    parser.add_argument("operations_csv", type=Path)
    parser.add_argument("--intervention-line", required=True)
    parser.add_argument("--control-line", required=True)
    parser.add_argument("--baseline-period", default="baseline")
    parser.add_argument("--trial-period", default="pilot")
    parser.add_argument("--planned-mix", required=True, type=parse_mix, help="e.g. standard=0.8,complex=0.2")
    parser.add_argument("--planned-orders-per-shift", required=True, type=float)
    parser.add_argument("--shifts", required=True, type=int)
    parser.add_argument("--hour-cap", required=True, type=float)
    parser.add_argument("--exclude-operations-date", action="append", default=[], help="exclude a non-comparable date from operations only; repeatable")
    parser.add_argument("--avoidable-cost", type=float)
    parser.add_argument("--hour-cost", type=float)
    args = parser.parse_args()

    ship = read_rows(args.shipment_csv, SHIP_REQUIRED)
    ops = read_rows(args.operations_csv, OPS_REQUIRED)
    periods = (args.baseline_period, args.trial_period)
    lines = (args.intervention_line, args.control_line)
    cohort = defaultdict(lambda: [0, 0, 0])
    immature = defaultdict(int)
    for row in ship:
        if row["period"] not in periods or row["line"] not in lines:
            continue
        key = (row["period"], row["line"], row["order_band"])
        shipped, mature, errors = map(int, (row["shipped_orders"], row["mature_orders"], row["confirmed_mispack_7d"]))
        if errors > mature or mature > shipped:
            raise ValueError(f"invalid cohort counts for {key} on {row['shipment_date']}")
        cohort[key][0] += shipped; cohort[key][1] += mature; cohort[key][2] += errors
        immature[(row["period"], row["line"])] += shipped - mature

    missing_bands = [b for b in args.planned_mix if any((p, l, b) not in cohort for p in periods for l in lines)]
    if missing_bands:
        raise ValueError(f"planned mix bands absent from one or more comparisons: {', '.join(missing_bands)}")

    print("# Reproducible decision basis\n")
    print("## Mature downstream quality\n")
    print("| Period | Line | Band | Errors | Mature orders | Rate |")
    print("|---|---|---:|---:|---:|---:|")
    for p in periods:
        for l in lines:
            for b in args.planned_mix:
                _, mature, errors = cohort[(p, l, b)]
                print(f"| {p} | {l} | {b} | {errors} | {mature} | {pct(errors, mature)} |")

    standardized = {}
    print("\n## Planned-mix-standardized quality\n")
    print("| Period | Line | Standardized rate | Immature shipped orders excluded |")
    print("|---|---:|---:|---:|")
    for p in periods:
        for l in lines:
            rate = sum(share * cohort[(p, l, b)][2] / cohort[(p, l, b)][1] for b, share in args.planned_mix.items())
            standardized[(p, l)] = rate
            print(f"| {p} | {l} | {100*rate:.2f}% | {immature[(p,l)]} |")
    intervention_change = standardized[(args.trial_period, args.intervention_line)] - standardized[(args.baseline_period, args.intervention_line)]
    control_change = standardized[(args.trial_period, args.control_line)] - standardized[(args.baseline_period, args.control_line)]
    did = intervention_change - control_change
    print(f"\nIntervention-line change: {100*intervention_change:.2f} percentage points. Control-line change: {100*control_change:.2f} points. Difference-in-differences: {100*did:.2f} points (descriptive contrast, not a causal estimate).")

    by_shift = defaultdict(lambda: [0.0, 0.0, 0, 0, 0])
    for row in ops:
        if row["period"] not in periods or row["line"] not in lines:
            continue
        if row["shipment_date"] in args.exclude_operations_date:
            continue
        k = (row["period"], row["line"])
        by_shift[k][0] += float(row["productive_labor_hours"])
        by_shift[k][1] += float(row["training_hours"])
        by_shift[k][2] += int(row["late_dispatch_orders"])
        by_shift[k][3] += 1
    for p in periods:
        for l in lines:
            included_dates = {r["shipment_date"] for r in ops if r["period"] == p and r["line"] == l and r["shipment_date"] not in args.exclude_operations_date}
            by_shift[(p,l)][4] = sum(int(r["shipped_orders"]) for r in ship if r["period"] == p and r["line"] == l and r["shipment_date"] in included_dates)

    print("\n## Operations (selected comparable shifts)\n")
    print("| Period | Line | Shipped | Shifts | Productive hours | Training subset | Ongoing hours/shift | Late orders | Late rate |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for p in periods:
        for l in lines:
            hours, training, late, shifts, shipped = by_shift[(p,l)]
            print(f"| {p} | {l} | {shipped} | {shifts} | {hours:.1f} | {training:.1f} | {(hours-training)/shifts:.2f} | {late} | {pct(late, shipped)} |")
    if args.exclude_operations_date:
        print(f"\nOperations-only excluded dates: {', '.join(args.exclude_operations_date)}.")

    trial = by_shift[(args.trial_period, args.intervention_line)]
    observed_orders_per_shift = trial[4] / trial[3]
    ongoing_hours = (trial[0] - trial[1]) / trial[3]
    required_throughput = args.planned_orders_per_shift / args.hour_cap
    observed_throughput = observed_orders_per_shift / ongoing_hours
    proportional_hours = ongoing_hours * args.planned_orders_per_shift / observed_orders_per_shift
    print("\n## Planning sensitivities\n")
    print(f"Required throughput: {required_throughput:.2f} orders/hour ({args.planned_orders_per_shift:g} orders / {args.hour_cap:g} hours).")
    print(f"Observed intervention-line trial throughput: {observed_throughput:.2f} orders/hour using ongoing hours across all supplied trial shifts.")
    print(f"Proportional scaling sensitivity: {proportional_hours:.1f} hours/shift at planned volume; this assumes labor scales proportionally and is not a capacity forecast.")
    planned_orders = args.planned_orders_per_shift * args.shifts
    if args.avoidable_cost is not None:
        gross_errors = -intervention_change * planned_orders
        did_errors = -did * planned_orders
        print(f"Quality scenario at {planned_orders:,.0f} orders: intervention-line before/after change corresponds to {gross_errors:.1f} fewer errors and ${gross_errors*args.avoidable_cost:,.0f}; the difference-in-differences contrast corresponds to {did_errors:.1f} fewer and ${did_errors*args.avoidable_cost:,.0f}. Both are planning scenarios, not causally established savings.")
    if args.hour_cost is not None:
        print(f"Labor price supplied: ${args.hour_cost:,.2f} per additional productive hour; no future incremental-hour claim is calculated because the packet does not establish labor scaling at planned volume.")


if __name__ == "__main__":
    main()
