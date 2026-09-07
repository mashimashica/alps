#!/usr/bin/env python3
"""Create a reviewable basis from shipment cohort and line-operation CSVs."""

import argparse
import csv
from collections import defaultdict
from pathlib import Path


COHORT_REQUIRED = {
    "shipment_date", "period", "line", "order_band", "shipped_orders",
    "mature_orders", "confirmed_mispack_7d", "station_catches",
}
OPS_REQUIRED = {
    "shipment_date", "period", "line", "productive_labor_hours",
    "overtime_hours", "training_hours", "late_dispatch_orders",
}


def read_rows(path, required):
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path}: missing columns: {', '.join(sorted(missing))}")
        rows = list(reader)
    return rows


def as_nonnegative(row, fields, source):
    result = {}
    for field in fields:
        try:
            value = float(row[field])
        except ValueError as exc:
            raise ValueError(f"{source}: non-numeric {field}={row[field]!r}") from exc
        if value < 0:
            raise ValueError(f"{source}: negative {field}")
        result[field] = value
    return result


def parse_mix(text):
    mix = {}
    for item in text.split(","):
        band, value = item.split("=", 1)
        mix[band.strip()] = float(value)
    if abs(sum(mix.values()) - 1.0) > 1e-9 or any(v < 0 for v in mix.values()):
        raise ValueError("planned mix weights must be nonnegative and sum to 1")
    return mix


def pct(value):
    return f"{100 * value:.3f}%"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path, help="directory containing shipment_cohorts.csv and shift_operations.csv")
    parser.add_argument("--planned-mix", required=True, help="comma-separated weights, e.g. standard=0.8,complex=0.2")
    parser.add_argument("--intervention-line", required=True)
    parser.add_argument("--control-line", required=True)
    parser.add_argument("--baseline-period", default="baseline")
    parser.add_argument("--trial-period", default="pilot")
    parser.add_argument("--ordinary-dates", help="comma-separated dates used for shift capacity/labor summaries")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    mix = parse_mix(args.planned_mix)
    cohorts = read_rows(args.packet / "shipment_cohorts.csv", COHORT_REQUIRED)
    ops = read_rows(args.packet / "shift_operations.csv", OPS_REQUIRED)
    cohort_keys = set()
    band_counts = defaultdict(lambda: [0.0, 0.0])
    total_ship = defaultdict(float)
    for index, row in enumerate(cohorts, 2):
        key = (row["shipment_date"], row["period"], row["line"], row["order_band"])
        if key in cohort_keys:
            raise ValueError(f"shipment_cohorts.csv:{index}: duplicate key {key}")
        cohort_keys.add(key)
        nums = as_nonnegative(row, ["shipped_orders", "mature_orders", "confirmed_mispack_7d"], f"shipment_cohorts.csv:{index}")
        if nums["mature_orders"] > nums["shipped_orders"] or nums["confirmed_mispack_7d"] > nums["mature_orders"]:
            raise ValueError(f"shipment_cohorts.csv:{index}: invalid count relationship")
        total_ship[(row["period"], row["line"])] += nums["shipped_orders"]
        if nums["mature_orders"] > 0:
            agg = band_counts[(row["period"], row["line"], row["order_band"])]
            agg[0] += nums["mature_orders"]
            agg[1] += nums["confirmed_mispack_7d"]

    op_keys = set()
    op_summary = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0, 0])
    ordinary = set(args.ordinary_dates.split(",")) if args.ordinary_dates else None
    for index, row in enumerate(ops, 2):
        key = (row["shipment_date"], row["period"], row["line"])
        if key in op_keys:
            raise ValueError(f"shift_operations.csv:{index}: duplicate key {key}")
        op_keys.add(key)
        nums = as_nonnegative(row, ["productive_labor_hours", "overtime_hours", "training_hours", "late_dispatch_orders"], f"shift_operations.csv:{index}")
        if nums["overtime_hours"] > nums["productive_labor_hours"] or nums["training_hours"] > nums["productive_labor_hours"]:
            raise ValueError(f"shift_operations.csv:{index}: subset hours exceed productive hours")
        shipped = sum(float(c["shipped_orders"]) for c in cohorts if c["shipment_date"] == row["shipment_date"] and c["period"] == row["period"] and c["line"] == row["line"])
        if nums["late_dispatch_orders"] > shipped:
            raise ValueError(f"shift_operations.csv:{index}: late orders exceed shipped orders")
        if ordinary is None or row["shipment_date"] in ordinary:
            agg = op_summary[(row["period"], row["line"])]
            agg[0] += shipped
            agg[1] += nums["late_dispatch_orders"]
            agg[2] += nums["productive_labor_hours"]
            agg[3] += nums["training_hours"]
            agg[4] += 1

    periods = [args.baseline_period, args.trial_period]
    lines = [args.intervention_line, args.control_line]
    adjusted = {}
    output = ["# Reproducible measurement basis", "", "## Mature downstream outcome", "", "| Period | Line | Band | Mature | Confirmed | Rate |", "|---|---|---:|---:|---:|---:|"]
    for period in periods:
        for line in lines:
            weighted = 0.0
            for band, weight in mix.items():
                mature, confirmed = band_counts[(period, line, band)]
                if not mature:
                    raise ValueError(f"no mature denominator for {period}/{line}/{band}")
                rate = confirmed / mature
                weighted += weight * rate
                output.append(f"| {period} | {line} | {band} | {mature:.0f} | {confirmed:.0f} | {pct(rate)} |")
            adjusted[(period, line)] = weighted
    output += ["", "## Planned-mix adjusted rates", "", f"Weights: {', '.join(f'{k}={v:.3f}' for k, v in mix.items())}.", "", "| Period | Line | Adjusted rate |", "|---|---|---:|"]
    for period in periods:
        for line in lines:
            output.append(f"| {period} | {line} | {pct(adjusted[(period, line)])} |")
    i_change = adjusted[(args.trial_period, args.intervention_line)] - adjusted[(args.baseline_period, args.intervention_line)]
    c_change = adjusted[(args.trial_period, args.control_line)] - adjusted[(args.baseline_period, args.control_line)]
    did = i_change - c_change
    output += ["", f"Intervention-line change: {pct(i_change)}; control-line change: {pct(c_change)}; change-in-changes: {pct(did)}.", "", "This change-in-changes is descriptive unless assignment and identifying assumptions justify a causal claim.", "", "## Ordinary-shift operations", "", "| Period | Line | Orders | Late | Late rate | Shifts | Productive h/shift | Ongoing h/shift excluding training |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    for period in periods:
        for line in lines:
            shipped, late, hours, training, shifts = op_summary[(period, line)]
            if not shifts or not shipped:
                raise ValueError(f"no operation rows selected for {period}/{line}")
            output.append(f"| {period} | {line} | {shipped:.0f} | {late:.0f} | {pct(late / shipped)} | {shifts} | {hours / shifts:.2f} | {(hours - training) / shifts:.2f} |")
    output += ["", "Productive hours include overtime and training; those subsets are not added again. Cohort-level rows are aggregated before line-level operations are summarized.", ""]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(output), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        raise SystemExit(f"error: {exc}")
