#!/usr/bin/env python3
"""Reproduce the Fenwick packing-check decision arithmetic using only local CSVs."""

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COHORTS = ROOT / "input" / "sources" / "shipment_cohorts.csv"
OPERATIONS = ROOT / "input" / "sources" / "shift_operations.csv"
OUTPUT = Path(__file__).with_name("analysis_results.json")
TARGET_MIX = {"standard": 0.70, "complex": 0.30}
FORECAST_ORDERS_PER_SHIFT = 1440
FORECAST_SHIFTS = 20
HOURS_CAP = 102
ERROR_COST = 55
LABOR_COST = 34


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def rate(numerator, denominator):
    return numerator / denominator


cohorts = read_csv(COHORTS)
operations = read_csv(OPERATIONS)

cohort_key = [(r["shipment_date"], r["line"], r["order_band"]) for r in cohorts]
operation_key = [(r["shipment_date"], r["line"]) for r in operations]
assert len(cohort_key) == len(set(cohort_key)), "duplicate cohort key"
assert len(operation_key) == len(set(operation_key)), "duplicate operation key"
assert {r["order_band"] for r in cohorts} == set(TARGET_MIX), "unexpected/missing band"

for row in cohorts:
    for field in ("shipped_orders", "mature_orders", "confirmed_mispack_7d", "station_catches"):
        row[field] = int(row[field])
    assert row["mature_orders"] <= row["shipped_orders"]
    assert row["confirmed_mispack_7d"] <= row["mature_orders"]
for row in operations:
    for field in ("productive_labor_hours", "overtime_hours", "training_hours", "late_dispatch_orders"):
        row[field] = int(row[field])
    assert row["overtime_hours"] <= row["productive_labor_hours"]
    assert row["training_hours"] <= row["productive_labor_hours"]

ship_totals = defaultdict(int)
period_by_shift = {}
for row in cohorts:
    key = (row["shipment_date"], row["line"])
    ship_totals[key] += row["shipped_orders"]
    period_by_shift[key] = row["period"]
assert set(ship_totals) == set(operation_key), "shipment/operation shift mismatch"
assert all(sum(1 for r in cohorts if (r["shipment_date"], r["line"]) == key) == 2 for key in ship_totals)

band_totals = defaultdict(lambda: {"mature": 0, "errors": 0, "shipped": 0})
for row in cohorts:
    key = (row["period"], row["line"], row["order_band"])
    band_totals[key]["mature"] += row["mature_orders"]
    band_totals[key]["errors"] += row["confirmed_mispack_7d"]
    band_totals[key]["shipped"] += row["shipped_orders"]

stratum_rates = {}
stratum_counts = {}
standardized_rates = {}
raw_rates = {}
workload_shares = {}
mature_workload_shares = {}
for period in ("baseline", "pilot"):
    for line in ("Alder", "Birch"):
        label = f"{period}_{line.lower()}"
        rates = {}
        counts = {}
        mature_total = 0
        error_total = 0
        shipped_total = 0
        band_shipped = {}
        for band in TARGET_MIX:
            x = band_totals[(period, line, band)]
            assert x["mature"] > 0, f"no mature observations for {label}/{band}"
            rates[band] = rate(x["errors"], x["mature"])
            counts[band] = {"mature": x["mature"], "errors": x["errors"]}
            mature_total += x["mature"]
            error_total += x["errors"]
            shipped_total += x["shipped"]
            band_shipped[band] = x["shipped"]
        stratum_rates[label] = rates
        stratum_counts[label] = counts
        standardized_rates[label] = sum(TARGET_MIX[b] * rates[b] for b in TARGET_MIX)
        raw_rates[label] = rate(error_total, mature_total)
        workload_shares[label] = {b: rate(band_shipped[b], shipped_total) for b in TARGET_MIX}
        mature_workload_shares[label] = {
            b: rate(band_totals[(period, line, b)]["mature"], mature_total) for b in TARGET_MIX
        }

did = (
    standardized_rates["baseline_alder"] - standardized_rates["pilot_alder"]
) - (
    standardized_rates["baseline_birch"] - standardized_rates["pilot_birch"]
)
alder_no_check_counterfactual = standardized_rates["baseline_alder"] + (
    standardized_rates["pilot_birch"] - standardized_rates["baseline_birch"]
)

full_ops = [r for r in operations if ship_totals[(r["shipment_date"], r["line"])] == 1200]

def ops_summary(period, line):
    rows = [r for r in full_ops if r["period"] == period and r["line"] == line]
    shipped = sum(ship_totals[(r["shipment_date"], r["line"])] for r in rows)
    labor = sum(r["productive_labor_hours"] for r in rows)
    overtime = sum(r["overtime_hours"] for r in rows)
    training = sum(r["training_hours"] for r in rows)
    late = sum(r["late_dispatch_orders"] for r in rows)
    return {
        "shifts": len(rows),
        "shipped": shipped,
        "productive_hours": labor,
        "overtime_hours": overtime,
        "training_hours": training,
        "recurring_hours": labor - training,
        "recurring_hours_per_order": rate(labor - training, shipped),
        "orders_per_recurring_hour": rate(shipped, labor - training),
        "late_orders": late,
        "late_rate": rate(late, shipped),
    }


ops = {
    "baseline_alder": ops_summary("baseline", "Alder"),
    "baseline_birch": ops_summary("baseline", "Birch"),
    "pilot_alder": ops_summary("pilot", "Alder"),
    "pilot_birch": ops_summary("pilot", "Birch"),
}
assert ops["pilot_alder"]["training_hours"] == 5

check_hours_per_order = ops["pilot_alder"]["recurring_hours_per_order"]
no_check_hours_per_order = ops["baseline_alder"]["recurring_hours_per_order"]
check_hours_forecast = check_hours_per_order * FORECAST_ORDERS_PER_SHIFT
no_check_hours_forecast = no_check_hours_per_order * FORECAST_ORDERS_PER_SHIFT
supported_check_volume = HOURS_CAP / check_hours_per_order
incremental_hours_per_shift = check_hours_forecast - no_check_hours_forecast

forecast_line_orders = FORECAST_ORDERS_PER_SHIFT * FORECAST_SHIFTS
added_errors_check_vs_counterfactual = -did * forecast_line_orders
added_error_cost = added_errors_check_vs_counterfactual * ERROR_COST
incremental_labor_cost = incremental_hours_per_shift * FORECAST_SHIFTS * LABOR_COST

results = {
    "inputs": {
        "cohort_file": str(COHORTS.relative_to(ROOT)),
        "operations_file": str(OPERATIONS.relative_to(ROOT)),
        "target_mix": TARGET_MIX,
        "forecast_orders_per_line_shift": FORECAST_ORDERS_PER_SHIFT,
        "forecast_shifts": FORECAST_SHIFTS,
        "productive_hours_cap_per_line_shift": HOURS_CAP,
        "avoidable_cost_per_mispack_usd": ERROR_COST,
        "additional_labor_hour_usd": LABOR_COST,
    },
    "validation": {
        "cohort_rows": len(cohorts),
        "operation_rows": len(operations),
        "unique_cohort_keys": len(set(cohort_key)),
        "unique_operation_keys": len(set(operation_key)),
        "shipment_operation_keys_reconciled": True,
        "two_bands_per_shift": True,
        "immature_rows": sum(r["mature_orders"] == 0 for r in cohorts),
        "full_shift_operation_rows": len(full_ops),
        "short_shift_operation_rows": len(operations) - len(full_ops),
    },
    "quality": {
        "stratum_rates": stratum_rates,
        "stratum_counts": stratum_counts,
        "raw_mature_rates": raw_rates,
        "shipped_workload_shares": workload_shares,
        "mature_workload_shares": mature_workload_shares,
        "target_mix_standardized_rates": standardized_rates,
        "adjusted_improvement_check_minus_no_check": did,
        "planning_no_check_alder_rate_parallel_change": alder_no_check_counterfactual,
    },
    "full_shift_operations": ops,
    "capacity_scenarios": {
        "checked_hours_per_order": check_hours_per_order,
        "checked_hours_at_1440": check_hours_forecast,
        "checked_orders_supported_at_102_hours": supported_check_volume,
        "no_check_hours_per_order": no_check_hours_per_order,
        "no_check_hours_at_1440": no_check_hours_forecast,
        "incremental_check_hours_at_1440": incremental_hours_per_shift,
        "checked_projected_late_orders_per_shift_at_observed_rate": ops["pilot_alder"]["late_rate"] * FORECAST_ORDERS_PER_SHIFT,
        "no_check_projected_late_orders_per_shift_at_alder_baseline_rate": ops["baseline_alder"]["late_rate"] * FORECAST_ORDERS_PER_SHIFT,
        "late_order_limit_per_shift": FORECAST_ORDERS_PER_SHIFT * 0.01,
    },
    "economics_check_vs_no_check_parallel_change_scenario": {
        "forecast_alder_orders": forecast_line_orders,
        "expected_avoided_errors_from_check": did * forecast_line_orders,
        "expected_added_errors_from_check": added_errors_check_vs_counterfactual,
        "expected_added_error_cost_usd": added_error_cost,
        "recurring_incremental_check_hours": incremental_hours_per_shift * FORECAST_SHIFTS,
        "recurring_incremental_labor_cost_usd": incremental_labor_cost,
        "total_expected_disadvantage_usd": added_error_cost + incremental_labor_cost,
        "quality_improvement_needed_to_offset_labor_cost": incremental_labor_cost / (forecast_line_orders * ERROR_COST),
        "one_off_pilot_training_hours_sunk": 5,
    },
}

OUTPUT.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
print("validation: PASS")
print(f"wrote: {OUTPUT}")
print(f"target-mix rates: {json.dumps(standardized_rates, sort_keys=True)}")
print(f"adjusted improvement from checking: {did:.6f}")
print(f"checked hours at 1,440 orders: {check_hours_forecast:.1f}; supported volume at cap: {supported_check_volume:.0f}")
print(f"Alder checked full-shift late rate: {ops['pilot_alder']['late_rate']:.6f}")
print(f"20-shift expected check disadvantage: ${added_error_cost + incremental_labor_cost:.2f}")
