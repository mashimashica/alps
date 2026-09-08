#!/usr/bin/env python3
"""Reproduce the numerical basis for the Cedar Quay operating decision."""

from collections import defaultdict
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHIPMENTS = ROOT / "input" / "sources" / "shipment_cohorts.csv"
OPERATIONS = ROOT / "input" / "sources" / "shift_operations.csv"
SHORT_SHIFT_DATE = "2026-07-31"
NEXT_SHIFTS = 20
ORDERS_PER_LINE_SHIFT = 800
LABOR_CAP = 68
ERROR_COST = 48
HOUR_COST = 32


def pct(numerator, denominator):
    return 100 * numerator / denominator if denominator else None


with SHIPMENTS.open(newline="", encoding="utf-8") as handle:
    cohorts = list(csv.DictReader(handle))
with OPERATIONS.open(newline="", encoding="utf-8") as handle:
    operations = list(csv.DictReader(handle))

for row in cohorts:
    for field in ("shipped_orders", "mature_orders", "confirmed_mispack_7d", "station_catches"):
        row[field] = int(row[field])
for row in operations:
    for field in ("productive_labor_hours", "overtime_hours", "training_hours", "late_dispatch_orders"):
        row[field] = int(row[field])

# Shipment outcomes: aggregate mutually exclusive cohorts. Immature rows remain
# visible but are excluded from mature outcome-rate denominators.
shipment_totals = defaultdict(lambda: defaultdict(int))
for row in cohorts:
    key = (row["period"], row["line"], row["order_band"])
    for field in ("shipped_orders", "mature_orders", "confirmed_mispack_7d", "station_catches"):
        shipment_totals[key][field] += row[field]

print("MATURE OUTCOMES BY PERIOD / LINE / BAND")
for key in sorted(shipment_totals):
    vals = shipment_totals[key]
    print(
        f"{key[0]:8s} {key[1]:6s} {key[2]:8s} "
        f"mispack={vals['confirmed_mispack_7d']}/{vals['mature_orders']} "
        f"({pct(vals['confirmed_mispack_7d'], vals['mature_orders']):.3f}%), "
        f"shipped={vals['shipped_orders']}, catches={vals['station_catches']}"
    )

print("\nMATURE OUTCOMES BY PERIOD / LINE")
line_totals = defaultdict(lambda: defaultdict(int))
for (period, line, _band), vals in shipment_totals.items():
    for field, value in vals.items():
        line_totals[(period, line)][field] += value
for key in sorted(line_totals):
    vals = line_totals[key]
    print(
        f"{key[0]:8s} {key[1]:6s} "
        f"mispack={vals['confirmed_mispack_7d']}/{vals['mature_orders']} "
        f"({pct(vals['confirmed_mispack_7d'], vals['mature_orders']):.3f}%), "
        f"shipped={vals['shipped_orders']}, catches={vals['station_catches']}"
    )

immature = [row for row in cohorts if row["mature_orders"] == 0]
print(
    f"\nIMMATURE: {sum(r['shipped_orders'] for r in immature)} shipped orders "
    f"across {len(immature)} cohorts; confirmed outcome unavailable"
)

# Operations are aggregated directly from their one-row-per-date-and-line grain,
# never joined to band rows. The short shift is shown separately from full shifts.
print("\nFULL-SHIFT OPERATIONS BY PERIOD / LINE")
ops_totals = defaultdict(lambda: defaultdict(int))
ops_counts = defaultdict(int)
for row in operations:
    if row["shipment_date"] == SHORT_SHIFT_DATE:
        continue
    key = (row["period"], row["line"])
    ops_counts[key] += 1
    for field in ("productive_labor_hours", "overtime_hours", "training_hours", "late_dispatch_orders"):
        ops_totals[key][field] += row[field]
for key in sorted(ops_totals):
    vals = ops_totals[key]
    shipped = sum(
        row["shipped_orders"]
        for row in cohorts
        if row["period"] == key[0]
        and row["line"] == key[1]
        and row["shipment_date"] != SHORT_SHIFT_DATE
    )
    n = ops_counts[key]
    print(
        f"{key[0]:8s} {key[1]:6s} shifts={n}, "
        f"productive={vals['productive_labor_hours']} ({vals['productive_labor_hours']/n:.3f}/shift), "
        f"training={vals['training_hours']}, overtime={vals['overtime_hours']} ({vals['overtime_hours']/n:.3f}/shift), "
        f"late={vals['late_dispatch_orders']}/{shipped} ({pct(vals['late_dispatch_orders'], shipped):.3f}%)"
    )

print("\nFULL-SHIFT PROCESS OBSERVATIONS (not downstream outcomes)")
for period in ("baseline", "pilot"):
    for line in ("Harbor", "Ridge"):
        rows = [
            row
            for row in cohorts
            if row["period"] == period
            and row["line"] == line
            and row["shipment_date"] != SHORT_SHIFT_DATE
        ]
        catches = sum(row["station_catches"] for row in rows)
        shipped = sum(row["shipped_orders"] for row in rows)
        print(f"{period:8s} {line:6s} catches={catches}/{shipped} ({pct(catches, shipped):.3f}%)")

print("\nSHORT-SHIFT DISPATCH (immediately observable)")
for row in operations:
    if row["shipment_date"] == SHORT_SHIFT_DATE:
        shipped = sum(
            c["shipped_orders"]
            for c in cohorts
            if c["shipment_date"] == SHORT_SHIFT_DATE and c["line"] == row["line"]
        )
        print(
            f"{row['line']:6s} late={row['late_dispatch_orders']}/{shipped} "
            f"({pct(row['late_dispatch_orders'], shipped):.3f}%)"
        )

# Planning arithmetic. Harbor's recurring pilot hours remove the explicitly
# one-off three training hours: (198 - 3) / 3 = 65 hours/shift.
hb = line_totals[("baseline", "Harbor")]
hp = line_totals[("pilot", "Harbor")]
rb = line_totals[("baseline", "Ridge")]
rp = line_totals[("pilot", "Ridge")]
harbor_change_pp = pct(hp["confirmed_mispack_7d"], hp["mature_orders"]) - pct(
    hb["confirmed_mispack_7d"], hb["mature_orders"]
)
ridge_change_pp = pct(rp["confirmed_mispack_7d"], rp["mature_orders"]) - pct(
    rb["confirmed_mispack_7d"], rb["mature_orders"]
)
comparison_adjusted_pp = harbor_change_pp - ridge_change_pp
planned_orders_per_line = NEXT_SHIFTS * ORDERS_PER_LINE_SHIFT
projected_avoided_per_line = -comparison_adjusted_pp / 100 * planned_orders_per_line
raw_avoided_per_line = -harbor_change_pp / 100 * planned_orders_per_line
harbor_baseline_hours = ops_totals[("baseline", "Harbor")]["productive_labor_hours"] / 3
harbor_recurring_pilot_hours = (
    ops_totals[("pilot", "Harbor")]["productive_labor_hours"]
    - ops_totals[("pilot", "Harbor")]["training_hours"]
) / 3
incremental_hours_per_shift = harbor_recurring_pilot_hours - harbor_baseline_hours
incremental_hours_per_line = incremental_hours_per_shift * NEXT_SHIFTS
labor_cost_per_line = incremental_hours_per_line * HOUR_COST
avoided_error_cost_per_line = projected_avoided_per_line * ERROR_COST
net_per_line = avoided_error_cost_per_line - labor_cost_per_line
raw_avoided_error_cost_per_line = raw_avoided_per_line * ERROR_COST
raw_net_per_line = raw_avoided_error_cost_per_line - labor_cost_per_line
harbor_pilot_late_rate = ops_totals[("pilot", "Harbor")]["late_dispatch_orders"] / 2400
projected_late_per_line = harbor_pilot_late_rate * planned_orders_per_line

print("\nPLANNING PROJECTION (assumptions, not realized results)")
print(f"Harbor raw change: {harbor_change_pp:.3f} percentage points")
print(f"Ridge contemporaneous change: {ridge_change_pp:.3f} percentage points")
print(f"Comparison-adjusted Harbor change: {comparison_adjusted_pp:.3f} percentage points")
print(f"Planned orders: {planned_orders_per_line:,} per line; {2*planned_orders_per_line:,} both lines")
print(
    f"Recurring check hours: {harbor_recurring_pilot_hours:.1f}/shift versus "
    f"{harbor_baseline_hours:.1f} baseline; +{incremental_hours_per_shift:.1f}, "
    f"cap headroom={LABOR_CAP-harbor_recurring_pilot_hours:.1f}"
)
print(
    f"Per line: projected avoided mispacks={projected_avoided_per_line:.0f}, "
    f"avoidable error cost=${avoided_error_cost_per_line:,.0f}, "
    f"added hours={incremental_hours_per_line:.0f}, labor cost=${labor_cost_per_line:,.0f}, "
    f"net=${net_per_line:,.0f}"
)
print(
    f"Per line, raw Harbor pre/post sensitivity: avoided mispacks={raw_avoided_per_line:.0f}, "
    f"avoidable error cost=${raw_avoided_error_cost_per_line:,.0f}, net=${raw_net_per_line:,.0f}"
)
print(
    f"Both lines: projected avoided mispacks={2*projected_avoided_per_line:.0f}, "
    f"avoidable error cost=${2*avoided_error_cost_per_line:,.0f}, "
    f"added hours={2*incremental_hours_per_line:.0f}, labor cost=${2*labor_cost_per_line:,.0f}, "
    f"net=${2*net_per_line:,.0f}"
)
print(f"Dispatch commitment: <= {planned_orders_per_line//100} late orders per line (1% of plan)")
print(
    f"At Harbor's pilot full-shift dispatch rate: projected late orders="
    f"{projected_late_per_line:.1f} per line ({100*harbor_pilot_late_rate:.3f}%)"
)
