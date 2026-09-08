#!/usr/bin/env python3
"""Reproduce the numerical basis for the Cedar Quay decision memo."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COHORTS = ROOT / "input" / "sources" / "shipment_cohorts.csv"
OPERATIONS = ROOT / "input" / "sources" / "shift_operations.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def rate(numerator: int | float, denominator: int | float) -> float:
    return 100 * numerator / denominator


cohorts = read_csv(COHORTS)
operations = read_csv(OPERATIONS)

# Validate the stated grains before aggregating.
cohort_keys = [(r["shipment_date"], r["line"], r["order_band"]) for r in cohorts]
operation_keys = [(r["shipment_date"], r["line"]) for r in operations]
assert len(cohort_keys) == len(set(cohort_keys)), "duplicate cohort grain"
assert len(operation_keys) == len(set(operation_keys)), "duplicate operations grain"
for row in cohorts:
    shipped = int(row["shipped_orders"])
    mature = int(row["mature_orders"])
    mispacks = int(row["confirmed_mispack_7d"])
    assert mature in (0, shipped), "partially mature cohort not expected"
    assert mispacks <= mature

# Derive shift volumes at the line/date grain; 800 identifies the stated full shifts.
shift_volume: dict[tuple[str, str], int] = defaultdict(int)
for row in cohorts:
    shift_volume[(row["shipment_date"], row["line"])] += int(row["shipped_orders"])
full_shift_keys = {key for key, volume in shift_volume.items() if volume == 800}
assert all(shift_volume[key] == 320 for key in shift_volume.keys() - full_shift_keys)

# Mature quality and catches from full shifts. July 31 is neither mature nor full.
quality = defaultdict(lambda: {"shipped": 0, "mature": 0, "mispack": 0, "catch": 0})
quality_band = defaultdict(lambda: {"mature": 0, "mispack": 0})
for row in cohorts:
    key = (row["shipment_date"], row["line"])
    if key not in full_shift_keys:
        continue
    group = (row["period"], row["line"])
    quality[group]["shipped"] += int(row["shipped_orders"])
    quality[group]["mature"] += int(row["mature_orders"])
    quality[group]["mispack"] += int(row["confirmed_mispack_7d"])
    quality[group]["catch"] += int(row["station_catches"])
    band_group = (row["period"], row["line"], row["order_band"])
    quality_band[band_group]["mature"] += int(row["mature_orders"])
    quality_band[band_group]["mispack"] += int(row["confirmed_mispack_7d"])

# Operations remain at whole-line grain, so hours are never joined to band rows.
ops = defaultdict(lambda: {"shifts": 0, "hours": 0, "overtime": 0, "training": 0, "late": 0})
for row in operations:
    key = (row["shipment_date"], row["line"])
    if key not in full_shift_keys:
        continue
    group = (row["period"], row["line"])
    ops[group]["shifts"] += 1
    ops[group]["hours"] += int(row["productive_labor_hours"])
    ops[group]["overtime"] += int(row["overtime_hours"])
    ops[group]["training"] += int(row["training_hours"])
    ops[group]["late"] += int(row["late_dispatch_orders"])

print("QUALITY — MATURE FULL SHIFTS")
print("period,line,mispack/mature,mispack_rate,catch/shipped,catch_rate")
for key in sorted(quality):
    q = quality[key]
    print(
        f"{key[0]},{key[1]},{q['mispack']}/{q['mature']},"
        f"{rate(q['mispack'], q['mature']):.3f}%,"
        f"{q['catch']}/{q['shipped']},{rate(q['catch'], q['shipped']):.3f}%"
    )

print("\nQUALITY BY ORDER BAND — MATURE FULL SHIFTS")
print("period,line,band,mispack/mature,mispack_rate")
for key in sorted(quality_band):
    q = quality_band[key]
    print(f"{key[0]},{key[1]},{key[2]},{q['mispack']}/{q['mature']},{rate(q['mispack'], q['mature']):.3f}%")

print("\nOPERATIONS — FULL SHIFTS")
print("period,line,shifts,hours,training,recurring_hours_per_shift,overtime_per_shift,late/shipped,late_rate")
for key in sorted(ops):
    o = ops[key]
    shipped = quality[key]["shipped"]
    recurring = (o["hours"] - o["training"]) / o["shifts"]
    overtime = o["overtime"] / o["shifts"]
    print(
        f"{key[0]},{key[1]},{o['shifts']},{o['hours']},{o['training']},"
        f"{recurring:.1f},{overtime:.1f},{o['late']}/{shipped},{rate(o['late'], shipped):.3f}%"
    )

# Difference-in-differences: Harbor change minus Ridge change.
def qrate(period: str, line: str, band: str | None = None) -> float:
    if band is None:
        q = quality[(period, line)]
    else:
        q = quality_band[(period, line, band)]
    return q["mispack"] / q["mature"]


did = (
    qrate("pilot", "Harbor")
    - qrate("baseline", "Harbor")
    - qrate("pilot", "Ridge")
    + qrate("baseline", "Ridge")
)
std_did = (
    qrate("pilot", "Harbor", "standard")
    - qrate("baseline", "Harbor", "standard")
    - qrate("pilot", "Ridge", "standard")
    + qrate("baseline", "Ridge", "standard")
)
complex_did = (
    qrate("pilot", "Harbor", "complex")
    - qrate("baseline", "Harbor", "complex")
    - qrate("pilot", "Ridge", "complex")
    + qrate("baseline", "Ridge", "complex")
)

next_orders = 20 * 800
next_standard = int(next_orders * 0.75)
next_complex = next_orders - next_standard
avoided_standard = -std_did * next_standard
avoided_complex = -complex_did * next_complex
avoided_total = avoided_standard + avoided_complex
incremental_hours = 20 * (
    (ops[("pilot", "Harbor")]["hours"] - ops[("pilot", "Harbor")]["training"])
    / ops[("pilot", "Harbor")]["shifts"]
    - ops[("baseline", "Harbor")]["hours"] / ops[("baseline", "Harbor")]["shifts"]
)
quality_value = avoided_total * 48
labor_cost = incremental_hours * 32
training_cost = 3 * 32

print("\nFORWARD PLAN — PER CHECKED LINE, 20 FULL SHIFTS")
print(f"orders={next_orders} (standard={next_standard}, complex={next_complex})")
print(f"difference_in_differences={did * 100:.3f} percentage points")
print(f"band effects: standard={std_did * 100:.3f} pp, complex={complex_did * 100:.3f} pp")
print(f"estimated_avoided_mispacks={avoided_total:.0f} (standard={avoided_standard:.0f}, complex={avoided_complex:.0f})")
print(f"estimated_avoidable_cost={quality_value:.0f} USD")
print(f"additional_recurring_hours={incremental_hours:.0f}; labor_cost={labor_cost:.0f} USD")
print(f"estimated_net_before_one_off_training={quality_value - labor_cost:.0f} USD")
print(f"new_line_training=3 hours; at_given_rate={training_cost:.0f} USD; separately funded")
print(f"estimated_net_after_new_line_training={quality_value - labor_cost - training_cost:.0f} USD")

harbor_pilot = quality[("pilot", "Harbor")]
forecast_late = ops[("pilot", "Harbor")]["late"] / harbor_pilot["shipped"] * next_orders
print(f"dispatch_at_Harbor_pilot_rate={forecast_late:.1f} late orders; commitment_limit={next_orders * 0.01:.0f}")
