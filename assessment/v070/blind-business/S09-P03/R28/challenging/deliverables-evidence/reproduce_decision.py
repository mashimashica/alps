#!/usr/bin/env python3
"""Reproduce the Fenwick packing-check decision from the supplied CSV files."""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COHORT_PATH = ROOT / "input" / "sources" / "shipment_cohorts.csv"
OPS_PATH = ROOT / "input" / "sources" / "shift_operations.csv"

COHORT_COLUMNS = {
    "shipment_date",
    "period",
    "line",
    "order_band",
    "shipped_orders",
    "mature_orders",
    "confirmed_mispack_7d",
    "station_catches",
}
OPS_COLUMNS = {
    "shipment_date",
    "period",
    "line",
    "productive_labor_hours",
    "overtime_hours",
    "training_hours",
    "late_dispatch_orders",
}


def read_csv(path: Path, required: set[str]) -> list[dict[str, str]]:
    if not path.is_file():
        raise SystemExit(f"Missing required file: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = sorted(required - columns)
        if missing:
            raise SystemExit(f"Missing required columns in {path.name}: {', '.join(missing)}")
        return list(reader)


def number(row: dict[str, str], column: str, source: str) -> float:
    try:
        value = float(row[column])
    except (KeyError, TypeError, ValueError) as exc:
        raise SystemExit(f"Invalid number in {source}, column {column}: {row.get(column)!r}") from exc
    if not math.isfinite(value) or value < 0:
        raise SystemExit(f"Invalid nonnegative number in {source}, column {column}: {value}")
    return value


def pct(numerator: float, denominator: float) -> str:
    return "open" if denominator == 0 else f"{100 * numerator / denominator:.3f}%"


cohorts = read_csv(COHORT_PATH, COHORT_COLUMNS)
ops = read_csv(OPS_PATH, OPS_COLUMNS)

# Validate cohort rows and aggregate mature-only quality denominators.
quality: dict[tuple[str, str, str], dict[str, float]] = defaultdict(
    lambda: {"shipped": 0, "mature": 0, "errors": 0}
)
shipments_by_shift: dict[tuple[str, str], float] = defaultdict(float)
for row in cohorts:
    shipped = number(row, "shipped_orders", COHORT_PATH.name)
    mature = number(row, "mature_orders", COHORT_PATH.name)
    errors = number(row, "confirmed_mispack_7d", COHORT_PATH.name)
    if mature > shipped or errors > mature:
        raise SystemExit(f"Invalid cohort counts: {row}")
    key = (row["period"], row["line"], row["order_band"])
    quality[key]["shipped"] += shipped
    quality[key]["mature"] += mature
    quality[key]["errors"] += errors
    shipments_by_shift[(row["shipment_date"], row["line"])] += shipped

if sum(v["mature"] for v in quality.values()) == 0:
    raise SystemExit("No mature shipment rows are available; quality rates cannot be calculated")

# Validate that operations are one row per date and line, then aggregate each row once.
seen_ops: set[tuple[str, str]] = set()
operations: dict[tuple[str, str], dict[str, float]] = defaultdict(
    lambda: {"shipped": 0, "hours": 0, "training": 0, "late": 0}
)
full_shift_ops: dict[tuple[str, str], dict[str, float]] = defaultdict(
    lambda: {"shipped": 0, "hours": 0, "training": 0, "late": 0, "shifts": 0}
)
for row in ops:
    shift_key = (row["shipment_date"], row["line"])
    if shift_key in seen_ops:
        raise SystemExit(f"Duplicate operations row for date and line: {shift_key}")
    seen_ops.add(shift_key)
    if shift_key not in shipments_by_shift:
        raise SystemExit(f"Operations row has no matching shipment cohorts: {shift_key}")
    shipped = shipments_by_shift[shift_key]
    hours = number(row, "productive_labor_hours", OPS_PATH.name)
    training = number(row, "training_hours", OPS_PATH.name)
    late = number(row, "late_dispatch_orders", OPS_PATH.name)
    if training > hours or late > shipped:
        raise SystemExit(f"Invalid operations counts: {row}")
    period_key = (row["period"], row["line"])
    for target in (operations[period_key],):
        target["shipped"] += shipped
        target["hours"] += hours
        target["training"] += training
        target["late"] += late
    # The notes identify August 3-5 and 17-19 as comparable full shifts.
    if row["shipment_date"] != "2026-08-28":
        target = full_shift_ops[period_key]
        target["shipped"] += shipped
        target["hours"] += hours
        target["training"] += training
        target["late"] += late
        target["shifts"] += 1

if seen_ops != set(shipments_by_shift):
    missing = sorted(set(shipments_by_shift) - seen_ops)
    raise SystemExit(f"Shipment cohorts have no matching operations row: {missing}")

print("QUALITY COHORTS — downstream rate uses mature orders only")
print("period,line,band,shipped,mature,errors,error_rate")
for key in sorted(quality):
    values = quality[key]
    print(
        f"{','.join(key)},{values['shipped']:.0f},{values['mature']:.0f},"
        f"{values['errors']:.0f},{pct(values['errors'], values['mature'])}"
    )

print("\nOPERATIONS — all recorded shifts; line rows counted once")
print("period,line,shipped,productive_hours,training_hours,late,late_rate")
for key in sorted(operations):
    values = operations[key]
    print(
        f"{','.join(key)},{values['shipped']:.0f},{values['hours']:.1f},"
        f"{values['training']:.1f},{values['late']:.0f},"
        f"{pct(values['late'], values['shipped'])}"
    )

print("\nCOMPARABLE FULL-SHIFT OPERATIONS — excludes the 600-order August 28 shift")
print("period,line,shifts,shipped,productive_hours,training_hours,recurring_hours,late,late_rate")
for key in sorted(full_shift_ops):
    values = full_shift_ops[key]
    recurring = values["hours"] - values["training"]
    print(
        f"{','.join(key)},{values['shifts']:.0f},{values['shipped']:.0f},"
        f"{values['hours']:.1f},{values['training']:.1f},{recurring:.1f},"
        f"{values['late']:.0f},{pct(values['late'], values['shipped'])}"
    )

# Band-level difference-in-differences: positive is an incremental reduction.
def rate(period: str, line: str, band: str) -> float:
    cell = quality[(period, line, band)]
    if cell["mature"] == 0:
        raise SystemExit(f"No mature orders for {period}/{line}/{band}")
    return cell["errors"] / cell["mature"]


next_mix = {"standard": 0.70, "complex": 0.30}
incremental_reductions: dict[str, float] = {}
print("\nQUALITY DIFFERENCE-IN-DIFFERENCES")
for band in ("standard", "complex"):
    reduction = (
        rate("baseline", "Alder", band)
        - rate("pilot", "Alder", band)
        - (rate("baseline", "Birch", band) - rate("pilot", "Birch", band))
    )
    incremental_reductions[band] = reduction
    print(
        f"{band}: ({rate('baseline', 'Alder', band):.3%} - "
        f"{rate('pilot', 'Alder', band):.3%}) - "
        f"({rate('baseline', 'Birch', band):.3%} - "
        f"{rate('pilot', 'Birch', band):.3%}) = {reduction:.3%} reduction"
    )

weighted_reduction = sum(next_mix[b] * incremental_reductions[b] for b in next_mix)
checked_rate = sum(next_mix[b] * rate("pilot", "Alder", b) for b in next_mix)
modeled_no_check_rate = checked_rate + weighted_reduction

shifts = 20
orders_per_shift = 1440
orders = shifts * orders_per_shift
checked_errors = orders * checked_rate
no_check_errors = orders * modeled_no_check_rate
incremental_errors = checked_errors - no_check_errors

# Recurring hours exclude Alder's five one-off training hours.
def recurring_hours_per_shift(period: str, line: str) -> float:
    values = full_shift_ops[(period, line)]
    return (values["hours"] - values["training"]) / values["shifts"]


base_alder_h = recurring_hours_per_shift("baseline", "Alder")
base_birch_h = recurring_hours_per_shift("baseline", "Birch")
pilot_alder_h = recurring_hours_per_shift("pilot", "Alder")
pilot_birch_h = recurring_hours_per_shift("pilot", "Birch")
incremental_check_h_1200 = (pilot_alder_h - base_alder_h) - (pilot_birch_h - base_birch_h)
modeled_no_check_h_1200 = pilot_birch_h + (base_alder_h - base_birch_h)
scale = orders_per_shift / 1200
modeled_no_check_h = modeled_no_check_h_1200 * scale
checked_h = (modeled_no_check_h_1200 + incremental_check_h_1200) * scale
incremental_check_h = checked_h - modeled_no_check_h

error_cost = 55
labor_cost = 34
no_check_error_cost = no_check_errors * error_cost
checked_error_cost = checked_errors * error_cost
incremental_labor_cost = incremental_check_h * shifts * labor_cost

pilot_alder = full_shift_ops[("pilot", "Alder")]
pilot_birch = full_shift_ops[("pilot", "Birch")]
alder_late_rate = pilot_alder["late"] / pilot_alder["shipped"]
birch_late_rate = pilot_birch["late"] / pilot_birch["shipped"]

print("\nNEXT-PERIOD PLANNING SCENARIO")
print(f"workload = {shifts} shifts * {orders_per_shift} orders = {orders} Alder orders")
print(f"mix = 70% standard / 30% complex")
print(f"weighted incremental reduction = 70%*{incremental_reductions['standard']:.3%} + 30%*{incremental_reductions['complex']:.3%} = {weighted_reduction:.3%}")
print(f"modeled no-check quality rate = {modeled_no_check_rate:.3%}; expected errors = {no_check_errors:.1f}")
print(f"observed-check mix-weighted quality rate = {checked_rate:.3%}; expected errors = {checked_errors:.1f}")
print(f"incremental checked errors = {incremental_errors:.1f}; error-cost difference = ${incremental_errors * error_cost:,.0f}")
print(f"labor DiD at 1,200 orders = ({pilot_alder_h:.1f} - {base_alder_h:.1f}) - ({pilot_birch_h:.1f} - {base_birch_h:.1f}) = {incremental_check_h_1200:.1f} hours")
print(f"modeled no-check hours at 1,440 = {modeled_no_check_h:.1f}; checked hours = {checked_h:.1f}; cap = 102.0")
print(f"incremental checker hours = {incremental_check_h:.1f}/shift * {shifts} shifts = {incremental_check_h * shifts:.1f}; labor cost = ${incremental_labor_cost:,.0f}")
print(f"modeled no-check error cost = ${no_check_error_cost:,.0f}")
print(f"modeled checked error cost = ${checked_error_cost:,.0f}; plus incremental labor = ${incremental_labor_cost:,.0f}")
print(f"modeled relevant-cost difference (check minus no check) = ${(checked_error_cost + incremental_labor_cost) - no_check_error_cost:,.0f}")
print(f"pilot full-shift late rate: Alder checked = {alder_late_rate:.3%}; Birch no-check = {birch_late_rate:.3%}; promise <= 1.000%")

print("\nINTERPRETATION LIMITS")
print("- Assignment was voluntary, not randomized; the template and catch-recording rules changed concurrently.")
print("- The complex pilot cells contain only 300 mature orders per line, and the future mix is 30% complex versus 8.3% in mature pilot orders.")
print("- Capacity uses constant hours per order; no time-by-band data or validated capacity curve exists.")
print("- August 28 has zero mature orders and is excluded from quality rates; its short shift is excluded from full-shift capacity and dispatch comparisons.")
print("- Station catches are not added to downstream errors because their recording rule changed.")
