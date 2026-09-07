#!/usr/bin/env python3
"""Produce a transparent numerical trace for a two-line intervention packet."""
import argparse
import csv
import math
import pathlib
import sys
from collections import defaultdict


SHIP_COLS = {"shipment_date", "period", "line", "order_band", "shipped_orders", "mature_orders", "confirmed_mispack_7d", "station_catches"}
OPS_COLS = {"shipment_date", "period", "line", "productive_labor_hours", "overtime_hours", "training_hours", "late_dispatch_orders"}


def read_csv(path, required, label):
    try:
        with path.open(newline="") as f:
            rows = list(csv.DictReader(f))
    except OSError as exc:
        raise ValueError(f"cannot read {label} at {path}: {exc}") from exc
    if not rows:
        raise ValueError(f"{label} is empty: {path}")
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"{label} is missing columns: {', '.join(sorted(missing))}")
    for row_no, row in enumerate(rows, 2):
        for key in required - {"shipment_date", "period", "line", "order_band"}:
            if key in row:
                try:
                    value = int(row[key])
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"{label} row {row_no}: {key} is not an integer") from exc
                if value < 0:
                    raise ValueError(f"{label} row {row_no}: {key} is negative")
                row[key] = value
    return rows


def pct(n, d):
    return "n/a" if d == 0 else f"{100 * n / d:.3f}%"


def rate(n, d):
    return math.nan if d == 0 else n / d


def fmt(x):
    return f"{x:.6f}" if isinstance(x, float) else str(x)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Write mature-outcome and operations aggregates for an intervention packet.")
    ap.add_argument("--sources", type=pathlib.Path, required=True, help="directory containing shipment_cohorts.csv and shift_operations.csv")
    ap.add_argument("--output", type=pathlib.Path, required=True, help="Markdown file to write")
    ap.add_argument("--next-shifts", type=float, default=None)
    ap.add_argument("--orders-per-shift", type=float, default=None)
    ap.add_argument("--standard-share", type=float, default=None)
    ap.add_argument("--complex-share", type=float, default=None)
    ap.add_argument("--avoidable-cost", type=float, default=None)
    ap.add_argument("--hour-cost", type=float, default=None)
    ap.add_argument("--full-shift-min-orders", type=int, default=None, help="if set, summarize full-shift labor using dates at or above this line volume")
    ap.add_argument("--intervention-line", default="East")
    ap.add_argument("--comparison-line", default="West")
    ap.add_argument("--baseline-period", default="baseline")
    ap.add_argument("--pilot-period", default="pilot")
    args = ap.parse_args(argv)
    try:
        ship = read_csv(args.sources / "shipment_cohorts.csv", SHIP_COLS, "shipment cohorts")
        ops = read_csv(args.sources / "shift_operations.csv", OPS_COLS, "shift operations")
        if (args.standard_share is None) != (args.complex_share is None):
            raise ValueError("provide both --standard-share and --complex-share")
        if args.standard_share is not None and abs(args.standard_share + args.complex_share - 1) > 1e-9:
            raise ValueError("standard and complex shares must sum to 1")
        for name in ("next_shifts", "orders_per_shift", "standard_share", "complex_share", "avoidable_cost", "hour_cost"):
            value = getattr(args, name)
            if value is not None and value < 0:
                raise ValueError(f"{name} cannot be negative")

        cohort = defaultdict(lambda: [0, 0, 0, 0])
        line_period_ship = defaultdict(int)
        for row in ship:
            key = (row["period"], row["line"], row["order_band"])
            cohort[key][0] += row["shipped_orders"]
            cohort[key][1] += row["mature_orders"]
            cohort[key][2] += row["confirmed_mispack_7d"]
            cohort[key][3] += row["station_catches"]
            line_period_ship[(row["shipment_date"], row["period"], row["line"])] += row["shipped_orders"]

        operations = defaultdict(lambda: [0, 0, 0, 0, 0])
        for row in ops:
            key = (row["period"], row["line"])
            operations[key][0] += row["productive_labor_hours"]
            operations[key][1] += row["training_hours"]
            operations[key][2] += row["late_dispatch_orders"]
            operations[key][3] += line_period_ship.get((row["shipment_date"], row["period"], row["line"]), 0)
            operations[key][4] += 1

        out = ["# Numerical trace", "", "All outcome rates use mature orders only. Operations are aggregated once per line/date.", "", "## Mature cohorts", "", "| Period | Line | Band | Shipped | Mature | Errors | Rate | Station catches |", "|---|---|---:|---:|---:|---:|---:|---:|"]
        for key in sorted(cohort):
            shipped, mature, errors, catches = cohort[key]
            out.append(f"| {key[0]} | {key[1]} | {key[2]} | {shipped} | {mature} | {errors} | {pct(errors, mature)} | {catches} |")
        out += ["", "## Operations", "", "| Period | Line | Shipped | Productive hours | Training hours | Late dispatches | Late rate | Dates |", "|---|---|---:|---:|---:|---:|---:|---:|"]
        for key in sorted(operations):
            hours, training, late, shipped, dates = operations[key]
            out.append(f"| {key[0]} | {key[1]} | {shipped} | {hours} | {training} | {late} | {pct(late, shipped)} | {dates} |")

        if args.full_shift_min_orders is not None:
            full = defaultdict(lambda: [0, 0, 0, 0])
            for row in ops:
                shipped = line_period_ship.get((row["shipment_date"], row["period"], row["line"]), 0)
                if shipped >= args.full_shift_min_orders:
                    key = (row["period"], row["line"])
                    full[key][0] += row["productive_labor_hours"]
                    full[key][1] += row["training_hours"]
                    full[key][2] += 1
                    full[key][3] += shipped
            out += ["", f"## Full-shift labor (daily line shipments >= {args.full_shift_min_orders})", "", "| Period | Line | Full-shift dates | Avg productive hours | Avg ongoing hours (training removed) | Avg orders |", "|---|---|---:|---:|---:|---:|"]
            for key in sorted(full):
                hours, training, dates, shipped = full[key]
                out.append(f"| {key[0]} | {key[1]} | {dates} | {hours / dates:.3f} | {(hours - training) / dates:.3f} | {shipped / dates:.1f} |")

        if all(getattr(args, n) is not None for n in ("next_shifts", "orders_per_shift", "standard_share", "complex_share")):
            # Use explicitly named intervention and comparator cells; otherwise
            # report the formulas without silently choosing a line.
            intervention = args.intervention_line
            comparison = args.comparison_line
            baseline = args.baseline_period
            pilot = args.pilot_period
            bands = ("standard", "complex")
            have = {(p, l, b) for p, l, b in cohort}
            if all((baseline, intervention, b) in have and (pilot, intervention, b) in have and (baseline, comparison, b) in have and (pilot, comparison, b) in have for b in bands):
                effects = {}
                out += ["", "## Planning projection", "", f"| Band | Baseline {intervention} | Pilot {intervention} | Baseline {comparison} | Pilot {comparison} | Estimated incremental reduction |", "|---|---:|---:|---:|---:|---:|"]
                for band in bands:
                    be = rate(cohort[(baseline, intervention, band)][2], cohort[(baseline, intervention, band)][1])
                    pe = rate(cohort[(pilot, intervention, band)][2], cohort[(pilot, intervention, band)][1])
                    bw = rate(cohort[(baseline, comparison, band)][2], cohort[(baseline, comparison, band)][1])
                    pw = rate(cohort[(pilot, comparison, band)][2], cohort[(pilot, comparison, band)][1])
                    effects[band] = (be - pe) - (bw - pw)
                    be_text = pct(cohort[(baseline, intervention, band)][2], cohort[(baseline, intervention, band)][1])
                    pe_text = pct(cohort[(pilot, intervention, band)][2], cohort[(pilot, intervention, band)][1])
                    bw_text = pct(cohort[(baseline, comparison, band)][2], cohort[(baseline, comparison, band)][1])
                    pw_text = pct(cohort[(pilot, comparison, band)][2], cohort[(pilot, comparison, band)][1])
                    out.append(f"| {band} | {be_text} | {pe_text} | {bw_text} | {pw_text} | {100 * effects[band]:.6f} pp |")
                weighted = args.standard_share * effects["standard"] + args.complex_share * effects["complex"]
                planned_orders = args.next_shifts * args.orders_per_shift
                avoidable = planned_orders * weighted
                out += ["", f"- Formula: weighted reduction = {args.standard_share:g} * standard effect + {args.complex_share:g} * complex effect = {100 * weighted:.6f} percentage points.", f"- Planned orders = {args.next_shifts:g} shifts * {args.orders_per_shift:g} orders = {planned_orders:g}.", f"- Implied avoidable orders = planned orders * weighted reduction = {avoidable:.3f}."]
                if args.avoidable_cost is not None:
                    out.append(f"- Implied avoidable cost = {avoidable:.3f} * USD {args.avoidable_cost:g} = USD {avoidable * args.avoidable_cost:,.2f}.")
                if args.hour_cost is not None:
                    out.append(f"- Labor cost conversion (if an hour delta is supplied separately) = hour delta * USD {args.hour_cost:g}; this trace does not infer causality from hours.")
            else:
                out += ["", "## Planning projection", "", "The standard East/West baseline/pilot cells were not all present; no difference-in-differences projection was produced."]
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text("\n".join(out) + "\n", encoding="utf-8")
        print(f"wrote {args.output}")
        return 0
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
