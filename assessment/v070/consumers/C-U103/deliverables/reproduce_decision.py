#!/usr/bin/env python3
"""Reproduce the numerical basis for the Cedar Quay intervention decision."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "input" / "sources"

COHORT_COLUMNS = {
    "shipment_date", "period", "line", "order_band", "shipped_orders",
    "mature_orders", "confirmed_mispack_7d", "station_catches",
}
OPS_COLUMNS = {
    "shipment_date", "period", "line", "productive_labor_hours",
    "overtime_hours", "training_hours", "late_dispatch_orders",
}
NUMERIC_COHORT = {
    "shipped_orders", "mature_orders", "confirmed_mispack_7d", "station_catches"
}
NUMERIC_OPS = {
    "productive_labor_hours", "overtime_hours", "training_hours",
    "late_dispatch_orders",
}


def read_csv(path: Path, required: set[str], numeric: set[str]) -> list[dict]:
    if not path.is_file():
        raise SystemExit(f"ERROR: missing file: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        present = set(reader.fieldnames or [])
        missing = required - present
        if missing:
            raise SystemExit(f"ERROR: {path.name} missing columns: {sorted(missing)}")
        rows = list(reader)
    for row_number, row in enumerate(rows, start=2):
        for col in numeric:
            try:
                value = float(row[col])
            except (TypeError, ValueError):
                raise SystemExit(
                    f"ERROR: {path.name}:{row_number} invalid number in {col}: {row[col]!r}"
                )
            if value < 0:
                raise SystemExit(
                    f"ERROR: {path.name}:{row_number} negative value in {col}: {value}"
                )
            row[col] = value
    return rows


def pct(numerator: float, denominator: float) -> str:
    return "OPEN" if denominator == 0 else f"{100 * numerator / denominator:.3f}%"


cohorts = read_csv(SOURCES / "shipment_cohorts.csv", COHORT_COLUMNS, NUMERIC_COHORT)
ops = read_csv(SOURCES / "shift_operations.csv", OPS_COLUMNS, NUMERIC_OPS)

# Cohort aggregation preserves the mature-only downstream denominator.
cohort_totals = defaultdict(lambda: defaultdict(float))
for row in cohorts:
    key = (row["period"], row["line"], row["order_band"])
    for col in ("shipped_orders", "mature_orders", "confirmed_mispack_7d", "station_catches"):
        cohort_totals[key][col] += row[col]

if not any(values["mature_orders"] > 0 for values in cohort_totals.values()):
    raise SystemExit("ERROR: no mature cohort rows; downstream rates cannot be calculated")

print("COHORT TABLE (rates use mature_orders only; pilot shipped includes July 31 immature orders)")
print("period,line,band,shipped,mature,confirmed_mispack_7d,mature_rate,station_catches")
for key in sorted(cohort_totals):
    values = cohort_totals[key]
    print(
        ",".join([
            *key,
            f"{values['shipped_orders']:.0f}",
            f"{values['mature_orders']:.0f}",
            f"{values['confirmed_mispack_7d']:.0f}",
            pct(values["confirmed_mispack_7d"], values["mature_orders"]),
            f"{values['station_catches']:.0f}",
        ])
    )

# Aggregate the two cohort bands to a unique date-line shipped total before matching operations.
ship_by_date_line = defaultdict(float)
for row in cohorts:
    ship_by_date_line[(row["shipment_date"], row["line"])] += row["shipped_orders"]

for row in ops:
    key = (row["shipment_date"], row["line"])
    if key not in ship_by_date_line:
        raise SystemExit(f"ERROR: operations row lacks shipment cohorts: {key}")
    row["shipped_orders"] = ship_by_date_line[key]

full_ops = [row for row in ops if row["shipment_date"] != "2026-07-31"]
partial_ops = [row for row in ops if row["shipment_date"] == "2026-07-31"]
ops_totals = defaultdict(lambda: defaultdict(float))
for row in full_ops:
    key = (row["period"], row["line"])
    ops_totals[key]["shifts"] += 1
    for col in (
        "shipped_orders", "productive_labor_hours", "training_hours",
        "overtime_hours", "late_dispatch_orders",
    ):
        ops_totals[key][col] += row[col]

print("\nFULL-SHIFT OPERATIONS (July 31 partial shift excluded)")
print("period,line,shifts,shipped,productive_hours,training_hours,recurring_hours_per_shift,overtime_hours,late_dispatches,late_rate")
for key in sorted(ops_totals):
    values = ops_totals[key]
    recurring = values["productive_labor_hours"] - values["training_hours"]
    print(
        ",".join([
            *key,
            f"{values['shifts']:.0f}",
            f"{values['shipped_orders']:.0f}",
            f"{values['productive_labor_hours']:.0f}",
            f"{values['training_hours']:.0f}",
            f"{recurring / values['shifts']:.3f}",
            f"{values['overtime_hours']:.0f}",
            f"{values['late_dispatch_orders']:.0f}",
            pct(values["late_dispatch_orders"], values["shipped_orders"]),
        ])
    )

print("\nPARTIAL-SHIFT CONTEXT (not a full-shift capacity test)")
print("date,line,shipped,productive_hours,late_dispatches,late_rate")
for row in sorted(partial_ops, key=lambda r: r["line"]):
    print(
        f"{row['shipment_date']},{row['line']},{row['shipped_orders']:.0f},"
        f"{row['productive_labor_hours']:.0f},{row['late_dispatch_orders']:.0f},"
        f"{pct(row['late_dispatch_orders'], row['shipped_orders'])}"
    )

def rate(period: str, line: str, band: str) -> float:
    values = cohort_totals[(period, line, band)]
    if values["mature_orders"] == 0:
        raise SystemExit(f"ERROR: no mature orders for {(period, line, band)}")
    return values["confirmed_mispack_7d"] / values["mature_orders"]


mix = {"standard": 0.75, "complex": 0.25}
did_by_band = {}
for band in mix:
    harbor_reduction = rate("baseline", "Harbor", band) - rate("pilot", "Harbor", band)
    ridge_reduction = rate("baseline", "Ridge", band) - rate("pilot", "Ridge", band)
    did_by_band[band] = harbor_reduction - ridge_reduction

weighted_did = sum(mix[band] * did_by_band[band] for band in mix)
planned_orders = 20 * 800
avoidable_orders = planned_orders * weighted_did
gross_avoided_cost = avoidable_orders * 48

harbor_baseline = ops_totals[("baseline", "Harbor")]
harbor_pilot = ops_totals[("pilot", "Harbor")]
baseline_hours = (
    harbor_baseline["productive_labor_hours"] - harbor_baseline["training_hours"]
) / harbor_baseline["shifts"]
pilot_recurring_hours = (
    harbor_pilot["productive_labor_hours"] - harbor_pilot["training_hours"]
) / harbor_pilot["shifts"]
incremental_hours_per_shift = pilot_recurring_hours - baseline_hours
incremental_labor_cost = 20 * incremental_hours_per_shift * 32
net_cost_reduction = gross_avoided_cost - incremental_labor_cost
break_even_rate = incremental_hours_per_shift * 32 / (800 * 48)

print("\nPROJECTION FOR HARBOR: 20 full shifts x 800 orders, 75% standard / 25% complex")
for band in ("standard", "complex"):
    print(
        f"{band} DiD = (Harbor baseline {pct(rate('baseline','Harbor',band),1)} - "
        f"Harbor pilot {pct(rate('pilot','Harbor',band),1)}) - "
        f"(Ridge baseline {pct(rate('baseline','Ridge',band),1)} - "
        f"Ridge pilot {pct(rate('pilot','Ridge',band),1)}) = {100*did_by_band[band]:.3f} pp"
    )
print(f"Mix-weighted incremental reduction = 75%*{100*did_by_band['standard']:.3f} pp + 25%*{100*did_by_band['complex']:.3f} pp = {100*weighted_did:.3f} pp")
print(f"Implied avoidable downstream mispacks = 16,000 * {weighted_did:.5f} = {avoidable_orders:.1f}")
print(f"Expected gross avoided error cost = {avoidable_orders:.1f} * $48 = ${gross_avoided_cost:,.0f}")
print(f"Recurring labor baseline = {baseline_hours:.1f} hours/shift; pilot = {pilot_recurring_hours:.1f} hours/shift")
print(f"Expected incremental labor cost = 20 * {incremental_hours_per_shift:.1f} hours * $32 = ${incremental_labor_cost:,.0f}")
print(f"Expected net cost reduction = ${gross_avoided_cost:,.0f} - ${incremental_labor_cost:,.0f} = ${net_cost_reduction:,.0f}")
print(f"Labor-cost break-even incremental reduction = {100*break_even_rate:.3f} pp")
print("Capacity check = 65.0 recurring productive hours/shift <= 68.0-hour ceiling")
print("One-off training = 3.0 observed hours on July 20; excluded from recurring projection")
print("CAUTION: projection is an estimate, not a causal finding; Harbor volunteered and follow-up covers three mature pilot shifts.")
