#!/usr/bin/env python3
"""Reproduce the figures used in the Fenwick packing-check recommendation.

Uses only Python's standard library and the two supplied CSV files. Shipment
cohorts are aggregated by line/date before operations data are joined, so each
line/date operations row is counted exactly once.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "input" / "sources"
PLANNED_MIX = {"standard": 0.70, "complex": 0.30}
SHIFTS = 20
ORDERS_PER_SHIFT = 1_440
HOUR_CAP = 102.0
ERROR_COST = 55.0
HOUR_COST = 34.0


def read_csv(name: str) -> list[dict[str, str]]:
    with (SOURCES / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


shipments = read_csv("shipment_cohorts.csv")
operations = read_csv("shift_operations.csv")

# Unit of observation: shipment row = date/line/order-band cohort.
# Join key to operations: (shipment_date, line), after cohort aggregation.
by_line_date = defaultdict(lambda: {"shipped": 0, "mature": 0, "errors": 0})
segment = defaultdict(lambda: {"mature": 0, "errors": 0})
for row in shipments:
    key = (row["shipment_date"], row["line"])
    by_line_date[key]["shipped"] += int(row["shipped_orders"])
    by_line_date[key]["mature"] += int(row["mature_orders"])
    by_line_date[key]["errors"] += int(row["confirmed_mispack_7d"])
    if int(row["mature_orders"]):
        skey = (row["period"], row["line"], row["order_band"])
        segment[skey]["mature"] += int(row["mature_orders"])
        segment[skey]["errors"] += int(row["confirmed_mispack_7d"])

ops_by_key = {(row["shipment_date"], row["line"]): row for row in operations}
assert len(ops_by_key) == len(operations), "operations join key is not unique"
assert set(ops_by_key) == set(by_line_date), "shipment/operations keys do not reconcile"

# The supplied notes identify the 1,200-order dates as ordinary full shifts and
# the 600-order August 28 date as short. This data check makes that split visible.
full_keys = {key for key, value in by_line_date.items() if value["shipped"] == 1_200}
short_keys = {key for key, value in by_line_date.items() if value["shipped"] == 600}
assert len(full_keys) == 12 and len(short_keys) == 2


def rate(events: float, observations: float) -> float:
    return events / observations


def segment_rate(period: str, line: str, band: str) -> float:
    values = segment[(period, line, band)]
    return rate(values["errors"], values["mature"])


def standardized(period: str, line: str) -> float:
    return sum(PLANNED_MIX[band] * segment_rate(period, line, band) for band in PLANNED_MIX)


print("UNITS AND JOIN")
print("shipment unit=date/line/order-band cohort")
print("operations unit=date/line; join once on shipment_date+line after cohort aggregation")

print("\nMATURE QUALITY")
for period in ("baseline", "pilot"):
    for line in ("Alder", "Birch"):
        std = segment[(period, line, "standard")]
        comp = segment[(period, line, "complex")]
        total_mature = std["mature"] + comp["mature"]
        total_errors = std["errors"] + comp["errors"]
        print(
            f"{period} {line}: total={total_errors}/{total_mature}={rate(total_errors, total_mature):.4%}; "
            f"standard={std['errors']}/{std['mature']}={segment_rate(period, line, 'standard'):.4%}; "
            f"complex={comp['errors']}/{comp['mature']}={segment_rate(period, line, 'complex'):.4%}; "
            f"70/30 standardized={standardized(period, line):.4%}"
        )

alder_change = standardized("pilot", "Alder") - standardized("baseline", "Alder")
birch_change = standardized("pilot", "Birch") - standardized("baseline", "Birch")
did = alder_change - birch_change
adjusted_no_check = standardized("pilot", "Birch") + (
    standardized("baseline", "Alder") - standardized("baseline", "Birch")
)
print(f"Alder standardized change={alder_change:+.4%}")
print(f"Birch standardized change={birch_change:+.4%}")
print(f"difference-in-differences adjustment={did:+.4%}")
print(f"adjusted no-check planning rate={adjusted_no_check:.4%}")

next_orders = SHIFTS * ORDERS_PER_SHIFT
print("\nNEXT-PERIOD QUALITY SCENARIOS (not causal forecasts)")
print(f"orders per line={next_orders}; standard={next_orders * 0.70:.0f}; complex={next_orders * 0.30:.0f}")
for label, planning_rate in (
    ("Alder all-check at Alder pilot segment rates", standardized("pilot", "Alder")),
    ("Alder no-check at adjusted concurrent rate", adjusted_no_check),
    ("Alder no-check at Alder baseline segment rates", standardized("baseline", "Alder")),
    ("Birch no-check at Birch pilot segment rates", standardized("pilot", "Birch")),
):
    workload = next_orders * planning_rate
    print(f"{label}: rate={planning_rate:.4%}; mispacks={workload:.1f}; error cost=${workload * ERROR_COST:,.0f}")
quality_delta = next_orders * did
print(f"unsupported full-attribution DiD contrast: mispacks={quality_delta:+.1f}; error cost=${quality_delta * ERROR_COST:+,.0f}")

print("\nFULL-SHIFT LABOR AND DISPATCH")
for period in ("baseline", "pilot"):
    for line in ("Alder", "Birch"):
        rows = [row for row in operations if row["period"] == period and row["line"] == line and (row["shipment_date"], line) in full_keys]
        productive = sum(float(row["productive_labor_hours"]) for row in rows)
        training = sum(float(row["training_hours"]) for row in rows)
        overtime = sum(float(row["overtime_hours"]) for row in rows)
        routine_productive = productive - training
        shipped = sum(by_line_date[(row["shipment_date"], line)]["shipped"] for row in rows)
        late = sum(int(row["late_dispatch_orders"]) for row in rows)
        print(
            f"{period} {line}: shifts={len(rows)}; routine productive={routine_productive:.0f}/{len(rows)}={routine_productive/len(rows):.2f} h/shift; "
            f"training={training:.0f} h; overtime={overtime:.0f} h (subset of productive); late={late}/{shipped}={rate(late, shipped):.4%}"
        )

alder_check_1200 = 90.0
alder_baseline_1200 = 82.0
scale = ORDERS_PER_SHIFT / 1_200
check_hours = alder_check_1200 * scale
baseline_hours = alder_baseline_1200 * scale
added_hours = check_hours - baseline_hours
print("\nLABOR PLANNING SCENARIO (constant hours/order; not validated capacity)")
print(f"all-check={alder_check_1200:.1f}*{scale:.1f}={check_hours:.1f} h/shift; cap={HOUR_CAP:.1f}; over cap={check_hours-HOUR_CAP:.1f}")
print(f"baseline no-check={alder_baseline_1200:.1f}*{scale:.1f}={baseline_hours:.1f} h/shift")
print(f"added checking labor={added_hours:.1f} h/shift; cost=${added_hours * HOUR_COST:,.2f}/shift; 20-shift cost=${added_hours * HOUR_COST * SHIFTS:,.2f}")

alder_pilot_late = 42 / 3_600
print("\nDISPATCH PLANNING SCENARIO")
print(f"Alder pilot ordinary full shifts=42/3600={alder_pilot_late:.4%}; projected late={next_orders * alder_pilot_late:.0f}; 1% ceiling={next_orders * 0.01:.0f}")
for line in ("Alder", "Birch"):
    row = ops_by_key[("2026-08-28", line)]
    shipped = by_line_date[("2026-08-28", line)]["shipped"]
    print(f"short shift {line}: late={row['late_dispatch_orders']}/{shipped}; excluded from full-shift capacity evidence")
