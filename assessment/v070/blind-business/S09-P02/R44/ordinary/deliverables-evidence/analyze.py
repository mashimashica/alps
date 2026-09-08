#!/usr/bin/env python3
"""Reproduce the Cedar Quay intervention calculations using only the supplied CSVs."""

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHIPMENTS = ROOT / "input" / "sources" / "shipment_cohorts.csv"
OPERATIONS = ROOT / "input" / "sources" / "shift_operations.csv"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


ship = read_csv(SHIPMENTS)
ops = read_csv(OPERATIONS)

ship_key = [(r["shipment_date"], r["line"], r["order_band"]) for r in ship]
ops_key = [(r["shipment_date"], r["line"]) for r in ops]
assert len(ship_key) == len(set(ship_key)), "duplicate shipment cohort key"
assert len(ops_key) == len(set(ops_key)), "duplicate operations key"
assert all(int(r["mature_orders"]) <= int(r["shipped_orders"]) for r in ship)
assert all(int(r["confirmed_mispack_7d"]) <= int(r["mature_orders"]) for r in ship)
assert all(int(r[f]) >= 0 for r in ship for f in ["shipped_orders", "mature_orders", "confirmed_mispack_7d", "station_catches"])
assert all(float(r[f]) >= 0 for r in ops for f in ["productive_labor_hours", "overtime_hours", "training_hours", "late_dispatch_orders"])

# Reconcile each date/line operations row to the sum of its two shipment-band rows.
shipped_by_shift = defaultdict(int)
for r in ship:
    shipped_by_shift[(r["shipment_date"], r["line"])] += int(r["shipped_orders"])
assert set(shipped_by_shift) == set(ops_key)
assert sorted(shipped_by_shift.values()).count(800) == 12
assert sorted(shipped_by_shift.values()).count(320) == 2

# Outcome evidence: only mature cohorts on the six matched full-shift dates.
outcomes = defaultdict(lambda: defaultdict(lambda: {"shipped": 0, "mature": 0, "mispack": 0, "catches": 0}))
for r in ship:
    if int(r["mature_orders"]) == int(r["shipped_orders"]):
        d = outcomes[(r["line"], r["period"])][r["order_band"]]
        d["shipped"] += int(r["shipped_orders"])
        d["mature"] += int(r["mature_orders"])
        d["mispack"] += int(r["confirmed_mispack_7d"])
        d["catches"] += int(r["station_catches"])

print("VALIDATION")
print(f"shipment_rows={len(ship)} unique_keys={len(set(ship_key))}")
print(f"operations_rows={len(ops)} unique_keys={len(set(ops_key))}")
print("reconciliation=12 full shifts x 800 orders; 2 short shifts x 320 orders")
print("cohort_checks=mature<=shipped, mispacks<=mature, and all counts nonnegative: PASS")

print("\nMATURE FULL-SHIFT OUTCOMES (75% standard / 25% complex)")
rates = {}
for line in ["Harbor", "Ridge"]:
    for period in ["baseline", "pilot"]:
        bands = outcomes[(line, period)]
        total_mature = sum(v["mature"] for v in bands.values())
        total_mispack = sum(v["mispack"] for v in bands.values())
        total_catches = sum(v["catches"] for v in bands.values())
        standard_rate = bands["standard"]["mispack"] / bands["standard"]["mature"]
        complex_rate = bands["complex"]["mispack"] / bands["complex"]["mature"]
        standardized = 0.75 * standard_rate + 0.25 * complex_rate
        rates[(line, period)] = standardized
        print(
            f"{line},{period}: mispacks={total_mispack}/{total_mature}={standardized:.4%}; "
            f"standard={bands['standard']['mispack']}/{bands['standard']['mature']}={standard_rate:.4%}; "
            f"complex={bands['complex']['mispack']}/{bands['complex']['mature']}={complex_rate:.4%}; "
            f"station_catches={total_catches}/{total_mature}={total_catches/total_mature:.4%}"
        )

harbor_change = rates[("Harbor", "pilot")] - rates[("Harbor", "baseline")]
ridge_change = rates[("Ridge", "pilot")] - rates[("Ridge", "baseline")]
did_change = harbor_change - ridge_change
print(f"Harbor change={harbor_change:.4%} ({harbor_change*100:+.3f} percentage points)")
print(f"Ridge change={ridge_change:.4%} ({ridge_change*100:+.3f} percentage points)")
print(f"difference-in-changes={did_change:.4%} ({did_change*100:+.3f} percentage points)")

# Operations are aggregated at their native one-row-per-date/line grain.
full_ops = [r for r in ops if shipped_by_shift[(r["shipment_date"], r["line"])] == 800]
op_summary = defaultdict(lambda: {"hours": 0.0, "training": 0.0, "overtime": 0.0, "late": 0, "orders": 0, "shifts": 0})
for r in full_ops:
    d = op_summary[(r["line"], r["period"])]
    d["hours"] += float(r["productive_labor_hours"])
    d["training"] += float(r["training_hours"])
    d["overtime"] += float(r["overtime_hours"])
    d["late"] += int(r["late_dispatch_orders"])
    d["orders"] += shipped_by_shift[(r["shipment_date"], r["line"])]
    d["shifts"] += 1

print("\nMATCHED FULL-SHIFT OPERATIONS")
for line in ["Harbor", "Ridge"]:
    for period in ["baseline", "pilot"]:
        d = op_summary[(line, period)]
        recurring = d["hours"] - d["training"]
        print(
            f"{line},{period}: productive_hours={d['hours']:.0f}; one_off_training={d['training']:.0f}; "
            f"overtime_subset={d['overtime']:.0f}; recurring_hours_per_shift={recurring/d['shifts']:.2f}; "
            f"late={d['late']}/{d['orders']}={d['late']/d['orders']:.4%}"
        )

# July 31 is eligible for dispatch and catches, but not downstream outcomes or full-shift capacity.
for line in ["Harbor", "Ridge"]:
    pilot_ship = [r for r in ship if r["line"] == line and r["period"] == "pilot"]
    pilot_ops = [r for r in ops if r["line"] == line and r["period"] == "pilot"]
    shipped = sum(int(r["shipped_orders"]) for r in pilot_ship)
    catches = sum(int(r["station_catches"]) for r in pilot_ship)
    late = sum(int(r["late_dispatch_orders"]) for r in pilot_ops)
    print(f"{line},all pilot dispatch incl short July 31: late={late}/{shipped}={late/shipped:.4%}; catches={catches}/{shipped}={catches/shipped:.4%}")

planned_shifts = 20
orders_per_shift = 800
planned_orders_per_line = planned_shifts * orders_per_shift
recurring_increment_per_shift = (
    (op_summary[("Harbor", "pilot")]["hours"] - op_summary[("Harbor", "pilot")]["training"])
    / op_summary[("Harbor", "pilot")]["shifts"]
    - op_summary[("Harbor", "baseline")]["hours"] / op_summary[("Harbor", "baseline")]["shifts"]
)
projected_hours_per_shift = (
    op_summary[("Harbor", "pilot")]["hours"] - op_summary[("Harbor", "pilot")]["training"]
) / op_summary[("Harbor", "pilot")]["shifts"]
incremental_hours_per_line = planned_shifts * recurring_increment_per_shift
incremental_labor_cost_per_line = incremental_hours_per_line * 32
adjusted_avoided_rate = -did_change
adjusted_avoided_per_line = planned_orders_per_line * adjusted_avoided_rate
gross_value_per_line = adjusted_avoided_per_line * 48
recurring_net_per_line = gross_value_per_line - incremental_labor_cost_per_line
ridge_training_cost = 3 * 32
late_rate = op_summary[("Harbor", "pilot")]["late"] / op_summary[("Harbor", "pilot")]["orders"]

print("\n20-SHIFT PLANNING SCENARIO")
print(f"planned_orders_per_line={planned_orders_per_line}")
print(f"projected_recurring_hours_per_shift={projected_hours_per_shift:.2f}; cap=68.00; buffer={68-projected_hours_per_shift:.2f}")
print(f"incremental_recurring_hours_per_line={incremental_hours_per_line:.0f}; cost_per_line=${incremental_labor_cost_per_line:,.0f}")
print(f"comparator_adjusted_avoided_rate={adjusted_avoided_rate:.4%}; avoided_mispacks_per_line={adjusted_avoided_per_line:.0f}")
print(f"gross_avoidable_value_per_line=${gross_value_per_line:,.0f}; recurring_net_per_line=${recurring_net_per_line:,.0f}")
print(f"Ridge_one_off_training=3 hours; training_cost_at_$32=${ridge_training_cost:,.0f}; Ridge_net_after_training=${recurring_net_per_line-ridge_training_cost:,.0f}")
print(f"two_line_net_after_Ridge_training=${2*recurring_net_per_line-ridge_training_cost:,.0f}")
print(f"break_even_avoided_mispacks_per_line={incremental_labor_cost_per_line/48:.0f}; break_even_rate={(incremental_labor_cost_per_line/48)/planned_orders_per_line:.4%}")
print(f"projected_late_per_line_at_Harbor_pilot_full_shift_rate={planned_orders_per_line*late_rate:.1f}/{planned_orders_per_line}={late_rate:.4%}; commitment<=1.0000%")

print("\nSCENARIOS PER LINE, 20 SHIFTS")
own_rate = rates[("Harbor", "baseline")] - rates[("Harbor", "pilot")]
current_gap = rates[("Ridge", "pilot")] - rates[("Harbor", "pilot")]
for name, benefit_rate in [
    ("Harbor own before/after", own_rate),
    ("current Ridge-vs-Harbor gap", current_gap),
    ("comparator-adjusted change", adjusted_avoided_rate),
    ("no true benefit", 0.0),
]:
    avoided = planned_orders_per_line * benefit_rate
    gross = avoided * 48
    net = gross - incremental_labor_cost_per_line
    print(f"{name}: assumed_rate_reduction={benefit_rate:.4%}; avoided={avoided:.0f}; gross=${gross:,.0f}; recurring_net=${net:,.0f}")
