#!/usr/bin/env python3
"""Reproduce core arithmetic for a two-period operational intervention packet.

Uses only Python's standard library. The shipment CSV must contain:
shipment_date, period, line, order_band, shipped_orders, mature_orders,
confirmed_mispack_7d. The operations CSV must contain: shipment_date,
period, line, productive_labor_hours, overtime_hours, training_hours,
late_dispatch_orders.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path


SHIPMENT_COUNT_FIELDS = (
    "shipped_orders",
    "mature_orders",
    "confirmed_mispack_7d",
)
OPERATION_NUMBER_FIELDS = (
    "productive_labor_hours",
    "overtime_hours",
    "training_hours",
    "late_dispatch_orders",
)


def fail(message: str) -> None:
    raise ValueError(message)


def parse_mix(value: str) -> dict[str, float]:
    result: dict[str, float] = {}
    for item in value.split(","):
        try:
            band, raw_weight = item.split("=", 1)
            band = band.strip()
            weight = float(raw_weight)
        except ValueError as exc:
            fail(f"Invalid planned mix item {item!r}; use band=weight")
        if not band or band in result or weight < 0:
            fail(f"Invalid planned mix item {item!r}")
        result[band] = weight
    if abs(sum(result.values()) - 1.0) > 1e-9:
        fail("Planned mix weights must sum to 1")
    return result


def parse_dates(value: str) -> set[str]:
    dates = {item.strip() for item in value.split(",") if item.strip()}
    if not dates:
        fail("At least one full-shift date is required")
    return dates


def read_csv(path: Path, required: set[str]) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            fields = set(reader.fieldnames or [])
            missing = required - fields
            if missing:
                fail(f"{path}: missing columns: {', '.join(sorted(missing))}")
            return list(reader)
    except OSError as exc:
        fail(f"Cannot read {path}: {exc}")


def to_nonnegative_number(row: dict[str, str], field: str, source: str) -> float:
    try:
        number = float(row[field])
    except ValueError:
        fail(f"{source}: {field} is not numeric in {row}")
    if number < 0:
        fail(f"{source}: {field} is negative in {row}")
    return number


def pct(value: float) -> str:
    return f"{100 * value:.3f}%"


def percentage_points(value: float) -> str:
    return f"{100 * value:.3f} percentage points"


def num(value: float) -> str:
    return f"{value:,.2f}"


def money(value: float) -> str:
    return f"${value:,.2f}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and summarize a local operational intervention packet as Markdown."
    )
    parser.add_argument("--shipments", required=True, type=Path)
    parser.add_argument("--operations", required=True, type=Path)
    parser.add_argument("--baseline-label", required=True)
    parser.add_argument("--pilot-label", required=True)
    parser.add_argument("--treated-line", required=True)
    parser.add_argument("--comparison-line", required=True)
    parser.add_argument(
        "--full-shift-dates",
        required=True,
        help="Comma-separated dates to use for full-shift labor and dispatch comparisons",
    )
    parser.add_argument(
        "--planned-mix",
        required=True,
        help="Comma-separated band weights, for example standard=0.8,complex=0.2",
    )
    parser.add_argument("--planned-orders-per-shift", required=True, type=float)
    parser.add_argument("--planned-shifts", required=True, type=int)
    parser.add_argument("--productive-hour-cap", required=True, type=float)
    parser.add_argument("--hourly-cost", required=True, type=float)
    parser.add_argument("--avoidable-event-cost", required=True, type=float)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    mix = parse_mix(args.planned_mix)
    full_dates = parse_dates(args.full_shift_dates)
    if args.planned_orders_per_shift <= 0 or args.planned_shifts <= 0:
        fail("Planned orders and shifts must be positive")
    if min(args.productive_hour_cap, args.hourly_cost, args.avoidable_event_cost) < 0:
        fail("Cap and cost inputs must be nonnegative")
    if args.baseline_label == args.pilot_label or args.treated_line == args.comparison_line:
        fail("Baseline/pilot labels and treated/comparison lines must differ")

    shipment_required = {
        "shipment_date", "period", "line", "order_band", *SHIPMENT_COUNT_FIELDS
    }
    operation_required = {
        "shipment_date", "period", "line", *OPERATION_NUMBER_FIELDS
    }
    shipments = read_csv(args.shipments, shipment_required)
    operations = read_csv(args.operations, operation_required)
    periods = (args.baseline_label, args.pilot_label)
    lines = (args.treated_line, args.comparison_line)

    quality: dict[tuple[str, str, str], list[float]] = defaultdict(lambda: [0.0, 0.0])
    shipped_by_shift: dict[tuple[str, str], float] = defaultdict(float)
    seen_shipment_keys: set[tuple[str, str, str]] = set()
    for row in shipments:
        source = str(args.shipments)
        shipped, mature, errors = [
            to_nonnegative_number(row, field, source) for field in SHIPMENT_COUNT_FIELDS
        ]
        if any(not value.is_integer() for value in (shipped, mature, errors)):
            fail(f"{source}: shipment counts must be integers in {row}")
        if mature > shipped or errors > mature:
            fail(f"{source}: require errors <= mature <= shipped in {row}")
        key = (row["shipment_date"], row["line"], row["order_band"])
        if key in seen_shipment_keys:
            fail(f"{source}: duplicate date/line/band row {key}")
        seen_shipment_keys.add(key)
        quality[(row["period"], row["line"], row["order_band"])][0] += mature
        quality[(row["period"], row["line"], row["order_band"])][1] += errors
        shipped_by_shift[(row["shipment_date"], row["line"])] += shipped

    operation_summary: dict[tuple[str, str], list[float]] = defaultdict(
        lambda: [0.0, 0.0, 0.0, 0.0, 0.0]
    )
    seen_operation_keys: set[tuple[str, str]] = set()
    used_full_keys: set[tuple[str, str]] = set()
    for row in operations:
        source = str(args.operations)
        productive, overtime, training, late = [
            to_nonnegative_number(row, field, source) for field in OPERATION_NUMBER_FIELDS
        ]
        if overtime > productive or training > productive:
            fail(f"{source}: overtime/training must be subsets of productive hours in {row}")
        if not late.is_integer():
            fail(f"{source}: late_dispatch_orders must be an integer in {row}")
        shift_key = (row["shipment_date"], row["line"])
        if shift_key in seen_operation_keys:
            fail(f"{source}: duplicate date/line row {shift_key}")
        seen_operation_keys.add(shift_key)
        if shift_key not in shipped_by_shift:
            fail(f"{source}: no shipment rows for {shift_key}")
        if late > shipped_by_shift[shift_key]:
            fail(f"{source}: late orders exceed shipped orders for {shift_key}")
        if row["shipment_date"] not in full_dates:
            continue
        if row["line"] in lines:
            used_full_keys.add(shift_key)
        summary = operation_summary[(row["period"], row["line"])]
        summary[0] += 1
        summary[1] += productive
        summary[2] += training
        summary[3] += late
        summary[4] += shipped_by_shift[shift_key]

    required_full_keys = {(date, line) for date in full_dates for line in lines}
    missing_full_keys = required_full_keys - used_full_keys
    if missing_full_keys:
        formatted = ", ".join(f"{date}/{line}" for date, line in sorted(missing_full_keys))
        fail(f"No operations row found for selected full shift(s): {formatted}")

    for period in periods:
        for line in lines:
            for band in mix:
                mature, _ = quality.get((period, line, band), (0.0, 0.0))
                if mature <= 0:
                    fail(f"No mature orders for period={period}, line={line}, band={band}")
            if operation_summary[(period, line)][0] <= 0:
                fail(f"No selected full shifts for period={period}, line={line}")

    standardized: dict[tuple[str, str], float] = {}
    for period in periods:
        for line in lines:
            standardized[(period, line)] = sum(
                mix[band]
                * quality[(period, line, band)][1]
                / quality[(period, line, band)][0]
                for band in mix
            )

    planned_volume = args.planned_orders_per_shift * args.planned_shifts
    treated_pre = standardized[(args.baseline_label, args.treated_line)]
    treated_post = standardized[(args.pilot_label, args.treated_line)]
    comparison_pre = standardized[(args.baseline_label, args.comparison_line)]
    comparison_post = standardized[(args.pilot_label, args.comparison_line)]
    own_reduction = treated_pre - treated_post
    common_change = comparison_post - comparison_pre
    common_change_counterfactual = treated_pre + common_change
    relative_reduction = common_change_counterfactual - treated_post

    def ops(period: str, line: str) -> dict[str, float]:
        shifts, productive, training, late, shipped = operation_summary[(period, line)]
        return {
            "shifts": shifts,
            "productive": productive,
            "training": training,
            "routine_avg": (productive - training) / shifts,
            "late": late,
            "shipped": shipped,
            "late_rate": late / shipped,
            "shipped_avg": shipped / shifts,
        }

    treated_base_ops = ops(args.baseline_label, args.treated_line)
    treated_pilot_ops = ops(args.pilot_label, args.treated_line)
    base_scale = args.planned_orders_per_shift / treated_base_ops["shipped_avg"]
    pilot_scale = args.planned_orders_per_shift / treated_pilot_ops["shipped_avg"]
    planned_base_hours = treated_base_ops["routine_avg"] * base_scale
    planned_full_check_hours = treated_pilot_ops["routine_avg"] * pilot_scale
    observed_increment_per_shift = (
        treated_pilot_ops["routine_avg"] - treated_base_ops["routine_avg"]
    )
    incremental_hours_per_order = observed_increment_per_shift / treated_pilot_ops["shipped_avg"]
    planned_increment_hours = planned_full_check_hours - planned_base_hours
    period_increment_hours = planned_increment_hours * args.planned_shifts
    period_increment_cost = period_increment_hours * args.hourly_cost
    headroom = args.productive_hour_cap - planned_base_hours
    max_checks = (
        max(0.0, headroom) / incremental_hours_per_order
        if incremental_hours_per_order > 0
        else float("inf")
    )

    own_gross = own_reduction * planned_volume * args.avoidable_event_cost
    relative_gross = relative_reduction * planned_volume * args.avoidable_event_cost

    print("# Reproducible operational intervention arithmetic")
    print()
    print("## Validation")
    print()
    print(f"- Shipment rows: {len(shipments)}; operations rows: {len(operations)}.")
    print("- Passed nonnegative-count, maturity, subset, uniqueness, and join-grain checks.")
    print(f"- Delayed quality rates exclude cohorts with zero mature orders.")
    print(f"- Full-shift operations use only: {', '.join(sorted(full_dates))}.")
    print()
    print("## Mature downstream quality")
    print()
    print("| Period | Line | Band | Mature | Errors | Rate |")
    print("|---|---|---:|---:|---:|---:|")
    for period in periods:
        for line in lines:
            for band in mix:
                mature, errors = quality[(period, line, band)]
                print(f"| {period} | {line} | {band} | {mature:,.0f} | {errors:,.0f} | {pct(errors/mature)} |")
    print()
    print(f"Planned-mix weights: {', '.join(f'{band}={weight:.1%}' for band, weight in mix.items())}.")
    print()
    print("| Period | Line | Planned-mix standardized rate |")
    print("|---|---|---:|")
    for period in periods:
        for line in lines:
            print(f"| {period} | {line} | {pct(standardized[(period, line)])} |")
    print()
    print("## Planning quality and cost scenarios")
    print()
    print(f"Planned volume per line: {planned_volume:,.0f} orders ({args.planned_orders_per_shift:,.0f} x {args.planned_shifts}).")
    print()
    print("| Scenario | Counterfactual rate | Pilot rate | Expected errors avoided | Gross avoidable cost |")
    print("|---|---:|---:|---:|---:|")
    print(f"| Treated own baseline | {pct(treated_pre)} | {pct(treated_post)} | {num(own_reduction*planned_volume)} | {money(own_gross)} |")
    print(f"| Treated baseline plus comparison-line change | {pct(common_change_counterfactual)} | {pct(treated_post)} | {num(relative_reduction*planned_volume)} | {money(relative_gross)} |")
    print()
    print(f"Comparison-line standardized change used in the second scenario: {percentage_points(common_change)} ({pct(comparison_pre)} to {pct(comparison_post)}).")
    print()
    print("## Full-shift operations")
    print()
    print("| Period | Line | Shifts | Shipped | Routine hours/shift | Training hours | Late orders | Late rate |")
    print("|---|---|---:|---:|---:|---:|---:|---:|")
    for period in periods:
        for line in lines:
            values = ops(period, line)
            print(
                f"| {period} | {line} | {values['shifts']:.0f} | {values['shipped']:,.0f} | "
                f"{values['routine_avg']:.2f} | {values['training']:.2f} | "
                f"{values['late']:.0f} | {pct(values['late_rate'])} |"
            )
    print()
    print("## Proportional labor projection")
    print()
    print(f"- Treated baseline routine hours scaled to {args.planned_orders_per_shift:,.0f} orders: {planned_base_hours:.2f} per shift.")
    print(f"- Treated all-order pilot hours scaled to that volume: {planned_full_check_hours:.2f} per shift.")
    print(f"- Productive-hour cap: {args.productive_hour_cap:.2f}; projected all-order overage: {max(0.0, planned_full_check_hours-args.productive_hour_cap):.2f} hours per shift.")
    print(f"- Projected incremental period hours and cost: {period_increment_hours:.2f} and {money(period_increment_cost)}.")
    print(f"- Gross avoidable cost less projected incremental labor: {money(own_gross-period_increment_cost)} using own baseline; {money(relative_gross-period_increment_cost)} using the comparison-change scenario.")
    if max_checks == float("inf"):
        print("- Observed routine hours did not increase, so a per-check capacity estimate is not available from this comparison.")
    else:
        print(f"- Baseline projection leaves {headroom:.2f} hours; at the observed {incremental_hours_per_order:.4f} incremental hours per checked order, that is about {max_checks:.0f} checks per shift.")
    print()
    print("These projections assume labor scales in direct proportion to throughput. The common-change scenario is descriptive, not causal, and a selective check's workload and effect are unmeasured until tested.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
