#!/usr/bin/env python3
"""Reproduce the Cedar Quay decision metrics from the supplied CSV sources."""

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "input" / "sources"
OUT = ROOT / "deliverables" / "calculation_results.json"


def read_csv(name):
    with (SOURCE / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


cohorts = read_csv("shipment_cohorts.csv")
operations = read_csv("shift_operations.csv")

# Validate source grain and basic population relationships before aggregation.
cohort_keys = [(r["shipment_date"], r["line"], r["order_band"]) for r in cohorts]
operation_keys = [(r["shipment_date"], r["line"]) for r in operations]
assert len(cohort_keys) == len(set(cohort_keys)), "duplicate cohort key"
assert len(operation_keys) == len(set(operation_keys)), "duplicate operations key"
assert len(cohorts) == 28 and len(operations) == 14
for r in cohorts:
    shipped = int(r["shipped_orders"])
    mature = int(r["mature_orders"])
    errors = int(r["confirmed_mispack_7d"])
    assert 0 <= errors <= mature <= shipped
for r in operations:
    assert int(r["overtime_hours"]) <= int(r["productive_labor_hours"])
    assert int(r["training_hours"]) <= int(r["productive_labor_hours"])

shipped_by_shift = defaultdict(int)
for r in cohorts:
    shipped_by_shift[(r["shipment_date"], r["line"])] += int(r["shipped_orders"])
assert set(shipped_by_shift) == set(operation_keys)

full_shift_keys = {k for k, v in shipped_by_shift.items() if v == 800}
short_shift_keys = {k for k, v in shipped_by_shift.items() if v != 800}
assert len(full_shift_keys) == 12
assert short_shift_keys == {("2026-07-31", "Harbor"), ("2026-07-31", "Ridge")}

def cohort_rollup(period, line, band=None, full_only=True, mature_only=False):
    rows = []
    for r in cohorts:
        key = (r["shipment_date"], r["line"])
        if r["period"] != period or r["line"] != line:
            continue
        if band is not None and r["order_band"] != band:
            continue
        if full_only and key not in full_shift_keys:
            continue
        if mature_only and int(r["mature_orders"]) == 0:
            continue
        rows.append(r)
    return {
        "shipped": sum(int(r["shipped_orders"]) for r in rows),
        "mature": sum(int(r["mature_orders"]) for r in rows),
        "errors": sum(int(r["confirmed_mispack_7d"]) for r in rows),
        "catches": sum(int(r["station_catches"]) for r in rows),
    }


def operation_rollup(period, line, full_only=True):
    rows = [
        r for r in operations
        if r["period"] == period
        and r["line"] == line
        and (not full_only or (r["shipment_date"], r["line"]) in full_shift_keys)
    ]
    shipped = sum(shipped_by_shift[(r["shipment_date"], r["line"])] for r in rows)
    productive = sum(int(r["productive_labor_hours"]) for r in rows)
    training = sum(int(r["training_hours"]) for r in rows)
    recurring = productive - training
    recurring_by_shift = [
        int(r["productive_labor_hours"]) - int(r["training_hours"])
        for r in rows
    ]
    return {
        "shifts": len(rows),
        "shipped": shipped,
        "productive_hours": productive,
        "training_hours": training,
        "recurring_hours": recurring,
        "overtime_hours": sum(int(r["overtime_hours"]) for r in rows),
        "late_dispatches": sum(int(r["late_dispatch_orders"]) for r in rows),
        "avg_recurring_hours_per_shift": recurring / len(rows),
        "min_recurring_hours_per_shift": min(recurring_by_shift),
        "max_recurring_hours_per_shift": max(recurring_by_shift),
        "late_dispatch_rate": sum(int(r["late_dispatch_orders"]) for r in rows) / shipped,
    }


bands = ("standard", "complex")
target_weights = {"standard": 0.75, "complex": 0.25}
quality = {}
for period in ("baseline", "pilot"):
    for line in ("Harbor", "Ridge"):
        by_band = {}
        for band in bands:
            x = cohort_rollup(period, line, band=band, mature_only=True)
            by_band[band] = {
                **x,
                "mispack_rate": x["errors"] / x["mature"],
            }
        total = cohort_rollup(period, line, mature_only=True)
        standardized = sum(target_weights[b] * by_band[b]["mispack_rate"] for b in bands)
        quality[f"{line}_{period}"] = {
            "by_band": by_band,
            "total": {
                **total,
                "mispack_rate": total["errors"] / total["mature"],
            },
            "target_mix_standardized_rate": standardized,
        }

h_before = quality["Harbor_baseline"]["target_mix_standardized_rate"]
h_after = quality["Harbor_pilot"]["target_mix_standardized_rate"]
r_before = quality["Ridge_baseline"]["target_mix_standardized_rate"]
r_after = quality["Ridge_pilot"]["target_mix_standardized_rate"]
adjusted_reduction = (h_before - h_after) - (r_before - r_after)

operations_summary = {
    f"{line}_{period}": operation_rollup(period, line)
    for period in ("baseline", "pilot")
    for line in ("Harbor", "Ridge")
}

forecast_orders = 20 * 800
harbor_pilot_hours_per_order = operations_summary["Harbor_pilot"]["recurring_hours"] / operations_summary["Harbor_pilot"]["shipped"]
harbor_baseline_hours_per_order = operations_summary["Harbor_baseline"]["recurring_hours"] / operations_summary["Harbor_baseline"]["shipped"]
forecast_hours = forecast_orders * harbor_pilot_hours_per_order
baseline_hours = forecast_orders * harbor_baseline_hours_per_order
incremental_hours = forecast_hours - baseline_hours
avoided_errors = forecast_orders * adjusted_reduction
gross_avoided_cost = avoided_errors * 48
incremental_labor_cost = incremental_hours * 32

short_shift = {}
for line in ("Harbor", "Ridge"):
    op = operation_rollup("pilot", line, full_only=False)
    full = operation_rollup("pilot", line, full_only=True)
    short_shipped = op["shipped"] - full["shipped"]
    short_late = op["late_dispatches"] - full["late_dispatches"]
    short_shift[line] = {
        "shipped": short_shipped,
        "late_dispatches": short_late,
        "late_dispatch_rate": short_late / short_shipped,
        "mature_orders": 0,
    }

result = {
    "validation": {
        "cohort_rows": len(cohorts),
        "unique_cohort_keys": len(set(cohort_keys)),
        "operations_rows": len(operations),
        "unique_operations_keys": len(set(operation_keys)),
        "full_line_shifts": len(full_shift_keys),
        "short_line_shifts": sorted([list(k) for k in short_shift_keys]),
    },
    "quality_full_shifts_mature_only": quality,
    "operations_full_shifts": operations_summary,
    "short_shift_2026_07_31": short_shift,
    "comparison": {
        "harbor_before_after_reduction": h_before - h_after,
        "ridge_before_after_reduction": r_before - r_after,
        "adjusted_reduction": adjusted_reduction,
    },
    "harbor_20_shift_planning_scenario": {
        "orders": forecast_orders,
        "hours_per_order_at_observed_pilot": harbor_pilot_hours_per_order,
        "forecast_recurring_hours": forecast_hours,
        "available_hours_at_cap": 20 * 68,
        "headroom_hours": 20 * 68 - forecast_hours,
        "proportional_supported_orders_per_shift_at_cap": 68 / harbor_pilot_hours_per_order,
        "incremental_hours_vs_harbor_baseline": incremental_hours,
        "expected_avoided_errors_adjusted": avoided_errors,
        "gross_avoided_cost_usd": gross_avoided_cost,
        "incremental_labor_cost_usd": incremental_labor_cost,
        "net_avoided_cost_usd": gross_avoided_cost - incremental_labor_cost,
        "break_even_rate_reduction": incremental_labor_cost / (forecast_orders * 48),
        "one_off_training_hours_already_observed": operations_summary["Harbor_pilot"]["training_hours"],
        "one_off_training_cost_if_economically_counted_usd": operations_summary["Harbor_pilot"]["training_hours"] * 32,
    },
}

OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, sort_keys=True))
