#!/usr/bin/env python3
"""Reproduce the Fenwick Audio Renewal packing-check calculations.

Dependencies: Python 3 standard library only.
Invocation (from the C-U116 directory): python3 deliverables/analysis.py
Inputs are read without modification from input/sources/.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COHORTS = ROOT / "input/sources/shipment_cohorts.csv"
OPERATIONS = ROOT / "input/sources/shift_operations.csv"
OUT = ROOT / "deliverables/numerical_basis.md"

PLAN_ORDERS_PER_SHIFT = 1440
PLAN_SHIFTS = 20
PLAN_MIX = {"standard": 0.70, "complex": 0.30}
HOURS_CAP = 102.0
ERROR_COST = 55.0
HOUR_COST = 34.0


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


cohorts = read_csv(COHORTS)
operations = read_csv(OPERATIONS)

# Packet integrity checks.
cohort_keys = [(r["shipment_date"], r["line"], r["order_band"]) for r in cohorts]
operation_keys = [(r["shipment_date"], r["line"]) for r in operations]
assert len(cohort_keys) == len(set(cohort_keys)), "duplicate cohort key"
assert len(operation_keys) == len(set(operation_keys)), "duplicate operation key"
assert all(int(r["mature_orders"]) <= int(r["shipped_orders"]) for r in cohorts)
assert all(int(r["confirmed_mispack_7d"]) <= int(r["mature_orders"]) for r in cohorts)
assert all(int(r["late_dispatch_orders"]) >= 0 for r in operations)
expected_cohort_keys = {
    (r["shipment_date"], r["line"], band)
    for r in operations
    for band in PLAN_MIX
}
assert set(cohort_keys) == expected_cohort_keys, "missing cohort/operation rows"

# Only the three ordinary, full, mature shifts in each period support the
# outcome comparison. The short 2026-08-28 shift has zero mature orders.
full_dates = {
    "baseline": {"2026-08-03", "2026-08-04", "2026-08-05"},
    "pilot": {"2026-08-17", "2026-08-18", "2026-08-19"},
}

quality = defaultdict(lambda: {"orders": 0, "errors": 0})
for row in cohorts:
    if row["shipment_date"] not in full_dates[row["period"]]:
        continue
    key = (row["period"], row["line"], row["order_band"])
    quality[key]["orders"] += int(row["mature_orders"])
    quality[key]["errors"] += int(row["confirmed_mispack_7d"])


def band_rate(period: str, line: str, band: str) -> float:
    item = quality[(period, line, band)]
    return item["errors"] / item["orders"]


def standardized_rate(period: str, line: str) -> float:
    return sum(PLAN_MIX[b] * band_rate(period, line, b) for b in PLAN_MIX)


def actual_total(period: str, line: str) -> tuple[int, int]:
    items = [quality[(period, line, b)] for b in PLAN_MIX]
    return sum(i["orders"] for i in items), sum(i["errors"] for i in items)


std_rates = {
    (period, line): standardized_rate(period, line)
    for period in ("baseline", "pilot")
    for line in ("Alder", "Birch")
}
alder_before_after = std_rates[("pilot", "Alder")] - std_rates[("baseline", "Alder")]
birch_before_after = std_rates[("pilot", "Birch")] - std_rates[("baseline", "Birch")]
did = alder_before_after - birch_before_after
pilot_gap = std_rates[("pilot", "Alder")] - std_rates[("pilot", "Birch")]

# Operations are native whole-line rows; count each once, never once per band.
ops = defaultdict(lambda: {"orders": 0, "hours": 0.0, "training": 0.0, "late": 0})
orders_by_date_line = defaultdict(int)
for row in cohorts:
    orders_by_date_line[(row["shipment_date"], row["line"])] += int(row["shipped_orders"])
for row in operations:
    if row["shipment_date"] not in full_dates[row["period"]]:
        continue
    key = (row["period"], row["line"])
    ops[key]["orders"] += orders_by_date_line[(row["shipment_date"], row["line"])]
    ops[key]["hours"] += float(row["productive_labor_hours"])
    ops[key]["training"] += float(row["training_hours"])
    ops[key]["late"] += int(row["late_dispatch_orders"])

alder_pilot_recurring_hours = ops[("pilot", "Alder")]["hours"] - ops[("pilot", "Alder")]["training"]
checked_hpo = alder_pilot_recurring_hours / ops[("pilot", "Alder")]["orders"]
alder_baseline_hpo = ops[("baseline", "Alder")]["hours"] / ops[("baseline", "Alder")]["orders"]
birch_pilot_hpo = ops[("pilot", "Birch")]["hours"] / ops[("pilot", "Birch")]["orders"]
checked_projected_hours = checked_hpo * PLAN_ORDERS_PER_SHIFT
alder_no_check_projected_hours = alder_baseline_hpo * PLAN_ORDERS_PER_SHIFT
birch_no_check_projected_hours = birch_pilot_hpo * PLAN_ORDERS_PER_SHIFT
incremental_hours = checked_projected_hours - alder_no_check_projected_hours
checked_feasible_volume = HOURS_CAP / checked_hpo
alder_no_check_feasible_volume = HOURS_CAP / alder_baseline_hpo
birch_no_check_feasible_volume = HOURS_CAP / birch_pilot_hpo

alder_pilot_late_rate = ops[("pilot", "Alder")]["late"] / ops[("pilot", "Alder")]["orders"]
birch_pilot_late_rate = ops[("pilot", "Birch")]["late"] / ops[("pilot", "Birch")]["orders"]
next_orders = PLAN_ORDERS_PER_SHIFT * PLAN_SHIFTS

# Economics. Conservative: contemporaneous untreated Birch's pilot band rates
# are the counterfactual. Favorable: attribute Alder's 1 percentage point
# standard-band improvement fully to checking and assume zero complex-band
# benefit or harm, despite the observed complex increase.
conservative_rate_reduction = std_rates[("pilot", "Birch")] - std_rates[("pilot", "Alder")]
favorable_rate_reduction = PLAN_MIX["standard"] * (
    band_rate("baseline", "Alder", "standard") - band_rate("pilot", "Alder", "standard")
)
break_even_errors_shift = incremental_hours * HOUR_COST / ERROR_COST
break_even_rate = break_even_errors_shift / PLAN_ORDERS_PER_SHIFT


def money(x: float) -> str:
    return f"${x:,.2f}"


lines: list[str] = []
lines += [
    "# Numerical basis — Fenwick Audio Renewal",
    "",
    "Run from the consumer directory with `python3 deliverables/analysis.py`. ",
    "Python 3 standard library only. Inputs: `shipment_cohorts.csv` and `shift_operations.csv`.",
    "",
    "## Integrity and eligibility",
    "",
    f"- {len(cohorts)} cohort rows and {len(operations)} operation rows read.",
    "- Duplicate keys: 0. Missing expected date/line/band rows: 0. Impossible denominator/count checks: 0.",
    "- Quality uses mature cohorts on the six ordinary full shifts only. August 28 is immature and is not treated as zero-error.",
    "- Labor and dispatch use each whole-line operation row once. The five Alder training hours on August 17 are removed only from recurring labor.",
    "- Station catches are excluded from downstream errors because recording changed on August 14.",
    "",
    "## Mature quality",
    "",
    "| Period | Line | Band | Mature orders | Errors | Rate | Cohort share |",
    "|---|---|---:|---:|---:|---:|---:|",
]
for period in ("baseline", "pilot"):
    for line in ("Alder", "Birch"):
        total_orders, _ = actual_total(period, line)
        for band in ("standard", "complex"):
            item = quality[(period, line, band)]
            lines.append(
                f"| {period} | {line} | {band} | {item['orders']:,} | {item['errors']:,} | "
                f"{item['errors']/item['orders']:.2%} | {item['orders']/total_orders:.2%} |"
            )
        orders, errors = actual_total(period, line)
        lines.append(f"| {period} | {line} | **actual total** | **{orders:,}** | **{errors:,}** | **{errors/orders:.2%}** | **100.00%** |")

lines += [
    "",
    "Formula: next-mix standardized rate = `0.70 × standard rate + 0.30 × complex rate`.",
    "",
    "| Period | Alder standardized | Birch standardized | Alder − Birch |",
    "|---|---:|---:|---:|",
]
for period in ("baseline", "pilot"):
    lines.append(
        f"| {period} | {std_rates[(period, 'Alder')]:.2%} | {std_rates[(period, 'Birch')]:.2%} | "
        f"{std_rates[(period, 'Alder')] - std_rates[(period, 'Birch')]:+.2%} |"
    )
lines += [
    "",
    f"- Alder standardized before/after: {std_rates[('baseline','Alder')]:.2%} → {std_rates[('pilot','Alder')]:.2%}, change {alder_before_after:+.2%}.",
    f"- Birch standardized before/after: {std_rates[('baseline','Birch')]:.2%} → {std_rates[('pilot','Birch')]:.2%}, change {birch_before_after:+.2%}.",
    f"- Difference-in-differences sensitivity: ({alder_before_after:+.2%}) − ({birch_before_after:+.2%}) = {did:+.2%}. This is not a causal estimate.",
    "",
    "## Labor and dispatch on ordinary full shifts",
    "",
    "| Period | Line | Orders | Productive hours | Training | Recurring hours/order | Projected hours at 1,440 | Feasible volume at 102 h | Late orders | Late rate |",
    "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
]
for period, line in (("baseline", "Alder"), ("baseline", "Birch"), ("pilot", "Alder"), ("pilot", "Birch")):
    item = ops[(period, line)]
    recurring = item["hours"] - item["training"]
    hpo = recurring / item["orders"]
    lines.append(
        f"| {period} | {line} | {item['orders']:,} | {item['hours']:.1f} | {item['training']:.1f} | "
        f"{hpo:.5f} | {hpo*PLAN_ORDERS_PER_SHIFT:.1f} | {HOURS_CAP/hpo:,.0f} | {item['late']:,} | {item['late']/item['orders']:.2%} |"
    )
lines += [
    "",
    f"Checked Alder recurring projection: `(275 − 5) / 3,600 × 1,440 = {checked_projected_hours:.1f} h/shift`, which is {checked_projected_hours-HOURS_CAP:.1f} h over the cap; cap-feasible volume is {checked_feasible_volume:,.0f} orders.",
    f"Alder baseline no-check projection: `246 / 3,600 × 1,440 = {alder_no_check_projected_hours:.1f} h/shift`; cap headroom {HOURS_CAP-alder_no_check_projected_hours:.1f} h and cap-feasible volume {alder_no_check_feasible_volume:,.0f} orders.",
    f"Birch contemporaneous no-check projection: `246 / 3,600 × 1,440 = {birch_no_check_projected_hours:.1f} h/shift`; cap headroom {HOURS_CAP-birch_no_check_projected_hours:.1f} h and cap-feasible volume {birch_no_check_feasible_volume:,.0f} orders.",
    f"At the ordinary full-shift pilot rate, Alder projects {alder_pilot_late_rate*next_orders:.0f} late orders in {next_orders:,} ({alder_pilot_late_rate:.2%}), versus the 288-order maximum at 1.00%. Birch projects {birch_pilot_late_rate*next_orders:.0f} ({birch_pilot_late_rate:.2%}).",
    "",
    "## Cost scenarios for Alder all-order checking",
    "",
    f"Incremental recurring labor vs Alder baseline: `{checked_projected_hours:.1f} − {alder_no_check_projected_hours:.1f} = {incremental_hours:.1f} h/shift`; cost {money(incremental_hours*HOUR_COST)}/shift or {money(incremental_hours*HOUR_COST*PLAN_SHIFTS)} over 20 shifts. Startup training is separate and excluded.",
    "",
    "| Scenario | Rate reduction vs counterfactual | Avoided errors/shift | Gross avoided cost/shift | Net after labor/shift | Net over 20 shifts |",
    "|---|---:|---:|---:|---:|---:|",
]
for name, reduction in (
    ("Conservative: contemporaneous Birch pilot rates", conservative_rate_reduction),
    ("Favorable: standard-band gain fully attributed; no complex effect", favorable_rate_reduction),
):
    avoided = reduction * PLAN_ORDERS_PER_SHIFT
    gross = avoided * ERROR_COST
    net = gross - incremental_hours * HOUR_COST
    lines.append(f"| {name} | {reduction:+.2%} | {avoided:+.2f} | {money(gross)} | {money(net)} | {money(net*PLAN_SHIFTS)} |")
lines += [
    "",
    f"Break-even benefit: `{incremental_hours:.1f} × $34 / $55 = {break_even_errors_shift:.2f}` avoided errors/shift, or {break_even_rate:.3%} of 1,440 orders. Service failures are not monetized.",
    "",
    "## Projection boundaries",
    "",
    "All capacity figures assume labor scales linearly with orders and that the observed hours/order applies at the planned 70/30 mix. Because labor is not recorded by band, mix-specific capacity and selective-check labor cannot be identified. Allocation was nonrandom; Alder began worse on complex orders; the account pause and August 14 template change confound before/after comparisons. The complex pilot denominator is only 300 per line. These are planning scenarios, not proof of checker impact or future delivery.",
]

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("Integrity: duplicate_keys=0 missing_rows=0 impossible_counts=0")
print(f"Quality next-mix: baseline Alder={std_rates[('baseline','Alder')]:.4%} Birch={std_rates[('baseline','Birch')]:.4%}; pilot Alder={std_rates[('pilot','Alder')]:.4%} Birch={std_rates[('pilot','Birch')]:.4%}; DiD={did:+.4%}")
print(f"Capacity: checked_Alder={checked_projected_hours:.1f}h/shift cap_gap={HOURS_CAP-checked_projected_hours:+.1f}h feasible_volume={checked_feasible_volume:.0f}; no_check_Alder={alder_no_check_projected_hours:.1f}h headroom={HOURS_CAP-alder_no_check_projected_hours:.1f}h")
print(f"Dispatch full-shift pilot: Alder={alder_pilot_late_rate:.4%} ({ops[('pilot','Alder')]['late']}/{ops[('pilot','Alder')]['orders']}); Birch={birch_pilot_late_rate:.4%} ({ops[('pilot','Birch')]['late']}/{ops[('pilot','Birch')]['orders']})")
print(f"Economics conservative_20_shift_net={(conservative_rate_reduction*PLAN_ORDERS_PER_SHIFT*ERROR_COST-incremental_hours*HOUR_COST)*PLAN_SHIFTS:.2f}; favorable_20_shift_net={(favorable_rate_reduction*PLAN_ORDERS_PER_SHIFT*ERROR_COST-incremental_hours*HOUR_COST)*PLAN_SHIFTS:.2f}; break_even_rate={break_even_rate:.4%}")
print(f"Wrote {OUT.relative_to(ROOT)}")
