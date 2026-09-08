#!/usr/bin/env python3
"""Reproduce the Cedar Quay packing-check decision metrics.

Uses only Python's standard library and the four frozen source files. Shipment
outcomes are aggregated from date/line/order-band rows. Operations are kept at
their native date/line grain so labor and dispatch are never duplicated across
bands.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "input" / "sources"
OUTPUT = ROOT / "deliverables" / "derived_metrics.csv"

PLANNED_SHIFTS = 20
ORDERS_PER_SHIFT = 800
PLANNED_ORDERS = PLANNED_SHIFTS * ORDERS_PER_SHIFT
PLANNED_MIX = {"standard": 0.75, "complex": 0.25}
ERROR_COST = 48.0
LABOR_COST = 32.0
LABOR_CAP = 68.0


def read_csv(name: str) -> list[dict[str, str]]:
    with (SOURCE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


shipments = read_csv("shipment_cohorts.csv")
operations = read_csv("shift_operations.csv")

# Validate the declared grains and reconciliation key.
cohort_keys = [(r["shipment_date"], r["line"], r["order_band"]) for r in shipments]
operations_keys = [(r["shipment_date"], r["line"]) for r in operations]
assert len(cohort_keys) == len(set(cohort_keys)), "duplicate shipment cohort key"
assert len(operations_keys) == len(set(operations_keys)), "duplicate operations key"
assert {k[:2] for k in cohort_keys} == set(operations_keys), "shipment/operations key mismatch"

# Quality: only mature observations enter denominators.
quality = defaultdict(lambda: {"mature": 0, "mispack": 0, "catches": 0})
for row in shipments:
    if int(row["mature_orders"]) > 0:
        key = (row["period"], row["line"], row["order_band"])
        quality[key]["mature"] += int(row["mature_orders"])
        quality[key]["mispack"] += int(row["confirmed_mispack_7d"])
        quality[key]["catches"] += int(row["station_catches"])

rates = {
    key: value["mispack"] / value["mature"]
    for key, value in quality.items()
}

line_quality = defaultdict(lambda: {"mature": 0, "mispack": 0, "catches": 0})
for (period, line, _band), value in quality.items():
    key = (period, line)
    for field in value:
        line_quality[key][field] += value[field]

line_rates = {
    key: value["mispack"] / value["mature"]
    for key, value in line_quality.items()
}

harbor_change = line_rates[("pilot", "Harbor")] - line_rates[("baseline", "Harbor")]
ridge_change = line_rates[("pilot", "Ridge")] - line_rates[("baseline", "Ridge")]
adjusted_change = harbor_change - ridge_change

band_adjusted_changes = {}
for band in PLANNED_MIX:
    harbor_band_change = rates[("pilot", "Harbor", band)] - rates[("baseline", "Harbor", band)]
    ridge_band_change = rates[("pilot", "Ridge", band)] - rates[("baseline", "Ridge", band)]
    band_adjusted_changes[band] = harbor_band_change - ridge_band_change

mix_adjusted_change = sum(
    PLANNED_MIX[band] * band_adjusted_changes[band]
    for band in PLANNED_MIX
)

# Operations: full shifts are exactly the 800-order line-dates declared in the notes.
shipped_by_line_date = defaultdict(int)
for row in shipments:
    shipped_by_line_date[(row["shipment_date"], row["line"])] += int(row["shipped_orders"])

full_operations = [
    row for row in operations
    if shipped_by_line_date[(row["shipment_date"], row["line"])] == ORDERS_PER_SHIFT
]

ops_summary = defaultdict(lambda: {
    "shifts": 0,
    "productive": 0.0,
    "training": 0.0,
    "overtime": 0.0,
    "late": 0,
    "orders": 0,
})
for row in full_operations:
    key = (row["period"], row["line"])
    summary = ops_summary[key]
    summary["shifts"] += 1
    summary["productive"] += float(row["productive_labor_hours"])
    summary["training"] += float(row["training_hours"])
    summary["overtime"] += float(row["overtime_hours"])
    summary["late"] += int(row["late_dispatch_orders"])
    summary["orders"] += shipped_by_line_date[(row["shipment_date"], row["line"])]

harbor_baseline_hours = ops_summary[("baseline", "Harbor")]["productive"] / 3
harbor_pilot_recurring_hours = (
    ops_summary[("pilot", "Harbor")]["productive"]
    - ops_summary[("pilot", "Harbor")]["training"]
) / 3
incremental_hours_per_shift = harbor_pilot_recurring_hours - harbor_baseline_hours

avoided_mispacks_per_line = -PLANNED_ORDERS * mix_adjusted_change
avoidable_quality_cost_per_line = avoided_mispacks_per_line * ERROR_COST
added_hours_per_line = PLANNED_SHIFTS * incremental_hours_per_shift
added_labor_cost_per_line = added_hours_per_line * LABOR_COST
ridge_training_cost = 3 * LABOR_COST

rows: list[tuple[str, str]] = []
def add(metric: str, value: object) -> None:
    rows.append((metric, str(value)))

for period in ("baseline", "pilot"):
    for line in ("Harbor", "Ridge"):
        counts = line_quality[(period, line)]
        add(f"{period}_{line.lower()}_mature_orders", counts["mature"])
        add(f"{period}_{line.lower()}_mispack_count", counts["mispack"])
        add(f"{period}_{line.lower()}_mispack_rate", f"{line_rates[(period, line)]:.8f}")
        add(f"{period}_{line.lower()}_station_catches", counts["catches"])

for band in ("standard", "complex"):
    for period in ("baseline", "pilot"):
        for line in ("Harbor", "Ridge"):
            key = (period, line, band)
            add(f"{period}_{line.lower()}_{band}_mispack_rate", f"{rates[key]:.8f}")

add("harbor_change", f"{harbor_change:.8f}")
add("ridge_change", f"{ridge_change:.8f}")
add("difference_in_differences", f"{adjusted_change:.8f}")
add("planned_mix_adjusted_change", f"{mix_adjusted_change:.8f}")
add("planned_orders_per_line", PLANNED_ORDERS)
add("adjusted_avoided_mispacks_per_line", f"{avoided_mispacks_per_line:.2f}")
add("avoidable_quality_cost_per_line_usd", f"{avoidable_quality_cost_per_line:.2f}")
add("harbor_baseline_productive_hours_per_full_shift", f"{harbor_baseline_hours:.2f}")
add("harbor_pilot_recurring_hours_per_full_shift", f"{harbor_pilot_recurring_hours:.2f}")
add("incremental_hours_per_shift", f"{incremental_hours_per_shift:.2f}")
add("added_hours_per_line_20_shifts", f"{added_hours_per_line:.2f}")
add("added_labor_cost_per_line_usd", f"{added_labor_cost_per_line:.2f}")
add("ridge_one_off_training_cost_usd", f"{ridge_training_cost:.2f}")
add("harbor_planning_net_usd", f"{avoidable_quality_cost_per_line - added_labor_cost_per_line:.2f}")
add("ridge_expansion_planning_net_after_training_usd", f"{avoidable_quality_cost_per_line - added_labor_cost_per_line - ridge_training_cost:.2f}")
add("labor_cap_hours_per_shift", f"{LABOR_CAP:.2f}")

for period in ("baseline", "pilot"):
    for line in ("Harbor", "Ridge"):
        summary = ops_summary[(period, line)]
        add(f"{period}_{line.lower()}_full_shift_late_count", summary["late"])
        add(f"{period}_{line.lower()}_full_shift_late_rate", f"{summary['late'] / summary['orders']:.8f}")
        add(f"{period}_{line.lower()}_overtime_hours_per_full_shift", f"{summary['overtime'] / summary['shifts']:.2f}")

with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["metric", "value"])
    writer.writerows(rows)

print("unit_quality=mature order; shipment_key=shipment_date+line+order_band")
print("unit_operations=line-date; join_key=shipment_date+line")
print(f"cohort_rows={len(shipments)}; operations_rows={len(operations)}; key_reconciliation=passed")
print(f"Harbor baseline: 63/2400 = {line_rates[('baseline', 'Harbor')]:.4%}")
print(f"Harbor pilot: 30/2400 = {line_rates[('pilot', 'Harbor')]:.4%}")
print(f"Ridge baseline: 63/2400 = {line_rates[('baseline', 'Ridge')]:.4%}")
print(f"Ridge pilot: 60/2400 = {line_rates[('pilot', 'Ridge')]:.4%}")
print(f"difference_in_differences={adjusted_change:.4%}")
print(f"planned_mix_adjusted_change={mix_adjusted_change:.4%}")
print(f"adjusted_avoided_mispacks_per_line={avoided_mispacks_per_line:.0f}")
print(f"avoidable_quality_cost_per_line=${avoidable_quality_cost_per_line:,.0f}")
print(f"recurring_added_hours_per_line={added_hours_per_line:.0f}; cost=${added_labor_cost_per_line:,.0f}")
print(f"Harbor planning net=${avoidable_quality_cost_per_line - added_labor_cost_per_line:,.0f}")
print(f"Ridge planning net after 3 training hours=${avoidable_quality_cost_per_line - added_labor_cost_per_line - ridge_training_cost:,.0f}")
print(f"wrote={OUTPUT.relative_to(ROOT)}")
