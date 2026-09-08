#!/usr/bin/env python3
"""Reproduce the Fenwick packing-check decision arithmetic with stdlib only."""

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COHORTS = ROOT / "input" / "sources" / "shipment_cohorts.csv"
OPERATIONS = ROOT / "input" / "sources" / "shift_operations.csv"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


cohorts = read_csv(COHORTS)
operations = read_csv(OPERATIONS)

# Downstream outcomes: mature cohorts only. Group by period, line, and band.
outcomes = defaultdict(lambda: {"shipped": 0, "mature": 0, "mispack": 0, "catches": 0})
for row in cohorts:
    key = (row["period"], row["line"], row["order_band"])
    outcomes[key]["shipped"] += int(row["shipped_orders"])
    outcomes[key]["mature"] += int(row["mature_orders"])
    outcomes[key]["mispack"] += int(row["confirmed_mispack_7d"])
    outcomes[key]["catches"] += int(row["station_catches"])

print("MATURE OUTCOMES BY PERIOD / LINE / BAND")
print("period,line,band,shipped,mature,mispack,mispack_rate")
for key in sorted(outcomes):
    values = outcomes[key]
    rate = values["mispack"] / values["mature"] if values["mature"] else None
    rate_text = "unavailable" if rate is None else f"{rate:.4%}"
    print(",".join(map(str, (*key, values["shipped"], values["mature"], values["mispack"], rate_text))))

# Operations are already one row per date and line, so hours are never joined to band rows.
full_dates = {"2026-08-03", "2026-08-04", "2026-08-05", "2026-08-17", "2026-08-18", "2026-08-19"}
ops = defaultdict(lambda: {"hours": 0, "training": 0, "late": 0, "orders": 0})
orders_by_date_line = defaultdict(int)
for row in cohorts:
    orders_by_date_line[(row["shipment_date"], row["line"])] += int(row["shipped_orders"])
for row in operations:
    if row["shipment_date"] not in full_dates:
        continue
    key = (row["period"], row["line"])
    ops[key]["hours"] += int(row["productive_labor_hours"])
    ops[key]["training"] += int(row["training_hours"])
    ops[key]["late"] += int(row["late_dispatch_orders"])
    ops[key]["orders"] += orders_by_date_line[(row["shipment_date"], row["line"])]

print("\nFULL-SHIFT OPERATIONS (LINE-LEVEL ROWS COUNTED ONCE)")
print("period,line,orders,productive_hours,training_hours,ongoing_hours,late,late_rate")
for key in sorted(ops):
    values = ops[key]
    ongoing = values["hours"] - values["training"]
    late_rate = values["late"] / values["orders"]
    print(",".join(map(str, (*key, values["orders"], values["hours"], values["training"], ongoing, values["late"], f"{late_rate:.4%}"))))

# Twenty-shift planning scenarios. These are projections, not causal estimates.
shifts = 20
orders_per_shift = 1440
planned_orders = shifts * orders_per_shift
planned = {"standard": int(planned_orders * 0.70), "complex": int(planned_orders * 0.30)}
alder_baseline_rates = {"standard": 42 / 2100, "complex": 90 / 1500}
alder_checked_rates = {"standard": 33 / 3300, "complex": 30 / 300}

def projected_mispacks(rates):
    return sum(planned[band] * rates[band] for band in planned)

no_check_mispacks = projected_mispacks(alder_baseline_rates)
checked_mispacks = projected_mispacks(alder_checked_rates)
baseline_hours_per_order = (246 / 3600)
checked_hours_per_order = (270 / 3600)  # Excludes five one-off training hours.
no_check_hours = planned_orders * baseline_hours_per_order
checked_hours = planned_orders * checked_hours_per_order
cap_hours = shifts * 102
incremental_hours = checked_hours - no_check_hours

print("\nTWENTY-SHIFT PLANNING SCENARIOS (NOT CAUSAL FORECASTS)")
print(f"planned_orders={planned_orders}; standard={planned['standard']}; complex={planned['complex']}")
print(f"no_check_mispacks_from_alder_baseline_band_rates={no_check_mispacks:.1f}")
print(f"checked_mispacks_from_alder_pilot_band_rates={checked_mispacks:.1f}")
print(f"no_check_error_cost_at_55={no_check_mispacks * 55:.2f}")
print(f"checked_error_cost_at_55={checked_mispacks * 55:.2f}")
print(f"no_check_hours_constant_hours_per_order={no_check_hours:.1f}")
print(f"checked_hours_constant_hours_per_order={checked_hours:.1f}")
print(f"twenty_shift_hours_cap={cap_hours}")
print(f"checked_hours_over_cap={checked_hours - cap_hours:.1f}")
print(f"additional_checked_hours_vs_baseline={incremental_hours:.1f}")
print(f"additional_hour_cost_at_34={incremental_hours * 34:.2f}")
print(f"checked_full_shift_late_projection_at_observed_rate={planned_orders * (42 / 3600):.1f}")
print(f"late_dispatch_limit_at_1_percent={planned_orders * 0.01:.1f}")

immature = [row for row in cohorts if int(row["mature_orders"]) == 0]
print("\nIMMATURE COHORTS")
print(f"rows={len(immature)}; shipped={sum(int(row['shipped_orders']) for row in immature)}; mature=0")
print("Their zero confirmed outcomes are unavailable outcomes and are excluded above.")
