#!/usr/bin/env python3
"""Reproduce the Fenwick packing-check decision arithmetic with the Python stdlib."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHIPMENTS = ROOT / "input" / "sources" / "shipment_cohorts.csv"
OPERATIONS = ROOT / "input" / "sources" / "shift_operations.csv"

MIX = {"standard": 0.70, "complex": 0.30}
NEXT_ORDERS_PER_SHIFT = 1_440
NEXT_SHIFTS = 20
HOURS_CAP = 102.0
ERROR_VALUE = 55.0
LABOR_COST = 34.0


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def pct(x: float) -> str:
    return f"{100 * x:.3f}%"


ship = read_csv(SHIPMENTS)
ops = read_csv(OPERATIONS)

# Structural and range checks.
ship_keys = [(r["shipment_date"], r["line"], r["order_band"]) for r in ship]
ops_keys = [(r["shipment_date"], r["line"]) for r in ops]
assert len(ship_keys) == len(set(ship_keys)), "duplicate shipment cohort key"
assert len(ops_keys) == len(set(ops_keys)), "duplicate operations key"
assert {k[:2] for k in ship_keys} == set(ops_keys), "shipment/operations coverage mismatch"
for r in ship:
    shipped = int(r["shipped_orders"])
    mature = int(r["mature_orders"])
    errors = int(r["confirmed_mispack_7d"])
    catches = int(r["station_catches"])
    assert 0 <= mature <= shipped
    assert 0 <= errors <= mature
    assert catches >= 0
for r in ops:
    productive = float(r["productive_labor_hours"])
    overtime = float(r["overtime_hours"])
    training = float(r["training_hours"])
    late = int(r["late_dispatch_orders"])
    assert productive >= overtime >= 0
    assert productive >= training >= 0
    assert late >= 0

# Outcome rates: aggregate counts first, and only use cohorts with eligible mature orders.
outcomes: dict[tuple[str, str, str], list[int]] = defaultdict(lambda: [0, 0])
for r in ship:
    mature = int(r["mature_orders"])
    if mature:
        k = (r["period"], r["line"], r["order_band"])
        outcomes[k][0] += int(r["confirmed_mispack_7d"])
        outcomes[k][1] += mature

rates = {k: errors / mature for k, (errors, mature) in outcomes.items()}
standardized = {}
for period in ("baseline", "pilot"):
    for line in ("Alder", "Birch"):
        standardized[(period, line)] = sum(
            MIX[band] * rates[(period, line, band)] for band in MIX
        )

# Full shifts have 1,200 observed shipments per line; the 600-order August 28 shift is atypical.
shipped_by_shift: dict[tuple[str, str], int] = defaultdict(int)
for r in ship:
    shipped_by_shift[(r["shipment_date"], r["line"])] += int(r["shipped_orders"])
full_ops = [r for r in ops if shipped_by_shift[(r["shipment_date"], r["line"])] == 1_200]

op_totals: dict[tuple[str, str], dict[str, float]] = defaultdict(
    lambda: {"hours": 0.0, "training": 0.0, "late": 0.0, "shipped": 0.0}
)
for r in full_ops:
    k = (r["period"], r["line"])
    op_totals[k]["hours"] += float(r["productive_labor_hours"])
    op_totals[k]["training"] += float(r["training_hours"])
    op_totals[k]["late"] += int(r["late_dispatch_orders"])
    op_totals[k]["shipped"] += shipped_by_shift[(r["shipment_date"], r["line"])]

hours_per_order = {}
late_rate = {}
for k, totals in op_totals.items():
    recurring_hours = totals["hours"] - totals["training"]
    hours_per_order[k] = recurring_hours / totals["shipped"]
    late_rate[k] = totals["late"] / totals["shipped"]

# Shared-change counterfactual: Alder baseline plus Birch's contemporaneous change.
quality_cf = standardized[("baseline", "Alder")] + (
    standardized[("pilot", "Birch")] - standardized[("baseline", "Birch")]
)
labor_cf = hours_per_order[("baseline", "Alder")] + (
    hours_per_order[("pilot", "Birch")] - hours_per_order[("baseline", "Birch")]
)
checker_quality = standardized[("pilot", "Alder")]
checker_labor = hours_per_order[("pilot", "Alder")]

period_orders = NEXT_ORDERS_PER_SHIFT * NEXT_SHIFTS


def scenario(name: str, no_check_quality: float, no_check_labor: float) -> tuple:
    errors_avoided = period_orders * (no_check_quality - checker_quality)
    gross_value = errors_avoided * ERROR_VALUE
    incremental_hours = period_orders * (checker_labor - no_check_labor)
    labor_cost = incremental_hours * LABOR_COST
    net_value = gross_value - labor_cost
    return name, no_check_quality, errors_avoided, gross_value, incremental_hours, labor_cost, net_value


scenarios = [
    scenario(
        "own baseline",
        standardized[("baseline", "Alder")],
        hours_per_order[("baseline", "Alder")],
    ),
    scenario(
        "current Birch comparator",
        standardized[("pilot", "Birch")],
        hours_per_order[("pilot", "Birch")],
    ),
    scenario("comparator-adjusted", quality_cf, labor_cf),
]

print("INPUTS")
print(f"shipments={SHIPMENTS}")
print(f"operations={OPERATIONS}")
print(f"shipment_rows={len(ship)} operations_rows={len(ops)}")
print("checks=PASS unique keys, matched coverage, count ranges, labor subset ranges")
print()
print("MATURE OUTCOMES (errors/mature, rate)")
for period in ("baseline", "pilot"):
    for line in ("Alder", "Birch"):
        parts = []
        for band in ("standard", "complex"):
            errors, mature = outcomes[(period, line, band)]
            parts.append(f"{band}={errors}/{mature} ({pct(errors/mature)})")
        raw_errors = sum(outcomes[(period, line, b)][0] for b in MIX)
        raw_mature = sum(outcomes[(period, line, b)][1] for b in MIX)
        print(
            f"{period} {line}: " + ", ".join(parts)
            + f", raw={raw_errors}/{raw_mature} ({pct(raw_errors/raw_mature)}), "
            + f"70/30 standardized={pct(standardized[(period, line)])}"
        )
print(
    "standardized changes: "
    f"Alder={pct(standardized[('pilot','Alder')] - standardized[('baseline','Alder')])}; "
    f"Birch={pct(standardized[('pilot','Birch')] - standardized[('baseline','Birch')])}; "
    f"difference-in-changes={pct((standardized[('pilot','Alder')] - standardized[('baseline','Alder')]) - (standardized[('pilot','Birch')] - standardized[('baseline','Birch')]))}"
)
print()
print("FULL-SHIFT OPERATIONS (one operations row counted once; training removed from recurring hours)")
for period in ("baseline", "pilot"):
    for line in ("Alder", "Birch"):
        t = op_totals[(period, line)]
        print(
            f"{period} {line}: recurring_hours={t['hours']-t['training']:.1f}, "
            f"orders={int(t['shipped'])}, hours/order={hours_per_order[(period,line)]:.6f}, "
            f"minutes/order={60*hours_per_order[(period,line)]:.2f}, "
            f"late={int(t['late'])}/{int(t['shipped'])} ({pct(late_rate[(period,line)])})"
        )
print()
print("NEXT-PERIOD PLANNING SCENARIOS")
print(f"orders/line={period_orders}; mix=70% standard/30% complex; shifts={NEXT_SHIFTS}")
print(
    f"Alder checker constant-rate projection: hours/shift={checker_labor*NEXT_ORDERS_PER_SHIFT:.1f} "
    f"vs cap={HOURS_CAP:.1f}; errors={checker_quality*period_orders:.1f}; "
    f"late/full-shift sample projection={late_rate[('pilot','Alder')]*period_orders:.1f} "
    f"vs 1% maximum={0.01*period_orders:.1f}"
)
print(
    f"Alder no-check comparator-adjusted projection: hours/shift={labor_cf*NEXT_ORDERS_PER_SHIFT:.1f}; "
    f"errors={quality_cf*period_orders:.1f}; "
    f"late using Alder baseline plus Birch contemporaneous change={period_orders*(late_rate[('baseline','Alder')] + late_rate[('pilot','Birch')] - late_rate[('baseline','Birch')]):.1f}"
)
print()
print("CHECKER ECONOMICS VS NO-CHECK COUNTERFACTUALS")
for row in scenarios:
    name, q, avoided, gross, incr_hours, labor_cost, net = row
    print(
        f"{name}: no-check quality={pct(q)}; errors_avoided={avoided:.1f}; "
        f"gross_avoidable_error_value=${gross:,.0f}; incremental_hours={incr_hours:.1f}; "
        f"incremental_labor_cost=${labor_cost:,.0f}; net_value=${net:,.0f}"
    )
breakeven_errors = period_orders * (checker_labor - labor_cf) * LABOR_COST / ERROR_VALUE
breakeven_pp = breakeven_errors / period_orders
print(
    f"comparator-adjusted labor break-even requires at least {breakeven_errors:.1f} avoided errors "
    f"({100*breakeven_pp:.3f} percentage points); observed standardized change vs that counterfactual "
    f"was {100*(quality_cf-checker_quality):.3f} percentage points."
)
print(f"capacity threshold={60*HOURS_CAP/NEXT_ORDERS_PER_SHIFT:.2f} minutes/order")
