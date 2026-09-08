#!/usr/bin/env python3
"""Reproduce the Fenwick packing-check decision arithmetic.

Inputs are the supplied synthetic CSV files. The script uses only Python's
standard library and writes a Markdown calculation record beside itself.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COHORTS = ROOT / "input/sources/shipment_cohorts.csv"
OPERATIONS = ROOT / "input/sources/shift_operations.csv"
OUTPUT = Path(__file__).resolve().parent / "calculation_output.md"

PLANNED_SHIFTS = Decimal("20")
ORDERS_PER_SHIFT = Decimal("1440")
PLANNED_ORDERS = PLANNED_SHIFTS * ORDERS_PER_SHIFT
WEIGHTS = {"standard": Decimal("0.70"), "complex": Decimal("0.30")}
HOURS_CAP = Decimal("102")
MISPACK_COST = Decimal("55")
LABOR_COST = Decimal("34")


def D(value: str | int) -> Decimal:
    return Decimal(str(value))


def pct(value: Decimal) -> str:
    return f"{value * 100:.3f}%"


def num(value: Decimal, places: str = "0.1") -> str:
    return f"{value.quantize(Decimal(places), rounding=ROUND_HALF_UP):,}"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def validate(cohorts: list[dict[str, str]], ops: list[dict[str, str]]) -> list[str]:
    checks: list[str] = []
    cohort_keys = [(r["shipment_date"], r["line"], r["order_band"]) for r in cohorts]
    op_keys = [(r["shipment_date"], r["line"]) for r in ops]
    assert len(cohort_keys) == len(set(cohort_keys)), "duplicate cohort key"
    assert len(op_keys) == len(set(op_keys)), "duplicate operations key"
    checks.append(f"Unique keys: {len(cohort_keys)} cohort rows; {len(op_keys)} operations rows")

    for row in cohorts:
        vals = [D(row[c]) for c in ("shipped_orders", "mature_orders", "confirmed_mispack_7d", "station_catches")]
        assert all(v >= 0 for v in vals), "negative cohort count"
        shipped, mature, mispacks, _ = vals
        assert mature <= shipped, "mature orders exceed shipped orders"
        assert mispacks <= mature, "mispacks exceed mature orders"
    for row in ops:
        vals = [D(row[c]) for c in ("productive_labor_hours", "overtime_hours", "training_hours", "late_dispatch_orders")]
        assert all(v >= 0 for v in vals), "negative operations count"
        productive, overtime, training, _ = vals
        assert overtime <= productive and training <= productive, "labor subset exceeds productive total"
    checks.append("Nonnegative counts and numerator/denominator/labor-subset consistency: passed")

    cohort_orders: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
    for row in cohorts:
        cohort_orders[(row["shipment_date"], row["line"])] += D(row["shipped_orders"])
    assert set(cohort_orders) == set(op_keys), "date/line keys do not reconcile"
    for row in ops:
        key = (row["shipment_date"], row["line"])
        assert D(row["late_dispatch_orders"]) <= cohort_orders[key], "late dispatch exceeds shipments"
    checks.append("Cohort and operations date/line coverage and late-dispatch denominators: passed")

    immature = [r for r in cohorts if D(r["mature_orders"]) == 0]
    assert all(D(r["confirmed_mispack_7d"]) == 0 for r in immature), "immature cohort has outcome count"
    checks.append(f"Immature cohorts excluded from quality rates: {len(immature)} rows")
    return checks


def main() -> None:
    cohorts = read_csv(COHORTS)
    ops = read_csv(OPERATIONS)
    checks = validate(cohorts, ops)

    # Quality uses mature cohorts only and pools counts within band/period/line.
    q: dict[tuple[str, str, str], dict[str, Decimal]] = defaultdict(lambda: defaultdict(Decimal))
    for r in cohorts:
        if D(r["mature_orders"]) == 0:
            continue
        k = (r["period"], r["line"], r["order_band"])
        q[k]["mature"] += D(r["mature_orders"])
        q[k]["mispack"] += D(r["confirmed_mispack_7d"])

    band_rate: dict[tuple[str, str, str], Decimal] = {}
    for k, v in q.items():
        band_rate[k] = v["mispack"] / v["mature"]

    standardized: dict[tuple[str, str], Decimal] = {}
    pooled: dict[tuple[str, str], tuple[Decimal, Decimal, Decimal]] = {}
    for period in ("baseline", "pilot"):
        for line in ("Alder", "Birch"):
            standardized[(period, line)] = sum(
                WEIGHTS[b] * band_rate[(period, line, b)] for b in WEIGHTS
            )
            mature = sum(q[(period, line, b)]["mature"] for b in WEIGHTS)
            mispack = sum(q[(period, line, b)]["mispack"] for b in WEIGHTS)
            pooled[(period, line)] = (mispack, mature, mispack / mature)

    # Full shifts are explicitly August 3-5 and 17-19; exclude short August 28.
    full_dates = {
        "baseline": {"2026-08-03", "2026-08-04", "2026-08-05"},
        "pilot": {"2026-08-17", "2026-08-18", "2026-08-19"},
    }
    operational: dict[tuple[str, str], dict[str, Decimal]] = defaultdict(lambda: defaultdict(Decimal))
    shipments: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
    for r in cohorts:
        if r["shipment_date"] in full_dates[r["period"]]:
            shipments[(r["period"], r["line"])] += D(r["shipped_orders"])
    for r in ops:
        if r["shipment_date"] in full_dates[r["period"]]:
            k = (r["period"], r["line"])
            operational[k]["hours"] += D(r["productive_labor_hours"])
            operational[k]["training"] += D(r["training_hours"])
            operational[k]["late"] += D(r["late_dispatch_orders"])

    op_metrics: dict[tuple[str, str], dict[str, Decimal]] = {}
    for k, totals in operational.items():
        orders = shipments[k]
        hours_per_order = totals["hours"] / orders
        ongoing_hours = totals["hours"] - totals["training"]
        ongoing_hpo = ongoing_hours / orders
        op_metrics[k] = {
            "orders": orders,
            "hours": totals["hours"],
            "training": totals["training"],
            "hours_per_order": hours_per_order,
            "ongoing_hpo": ongoing_hpo,
            "orders_per_hour": orders / totals["hours"],
            "late": totals["late"],
            "late_rate": totals["late"] / orders,
        }

    baseline_hpo = op_metrics[("baseline", "Alder")]["ongoing_hpo"]
    checked_hpo = op_metrics[("pilot", "Alder")]["ongoing_hpo"]
    stop_hours_shift = baseline_hpo * ORDERS_PER_SHIFT
    check_hours_shift = checked_hpo * ORDERS_PER_SHIFT
    check_capacity = HOURS_CAP / checked_hpo
    incremental_hours_shift = check_hours_shift - stop_hours_shift
    incremental_hours_period = incremental_hours_shift * PLANNED_SHIFTS

    stop_rate = standardized[("baseline", "Alder")]
    checked_rate = standardized[("pilot", "Alder")]
    birch_change = standardized[("pilot", "Birch")] - standardized[("baseline", "Birch")]
    comparison_stop_rate = standardized[("baseline", "Alder")] + birch_change
    did = (checked_rate - stop_rate) - birch_change

    stop_mispacks = PLANNED_ORDERS * stop_rate
    checked_mispacks = PLANNED_ORDERS * checked_rate
    comparison_stop_mispacks = PLANNED_ORDERS * comparison_stop_rate
    labor_delta_cost = incremental_hours_period * LABOR_COST
    primary_total_delta = (checked_mispacks - stop_mispacks) * MISPACK_COST + labor_delta_cost
    comparison_total_delta = (checked_mispacks - comparison_stop_mispacks) * MISPACK_COST + labor_delta_cost
    break_even_count = labor_delta_cost / MISPACK_COST
    break_even_rate = break_even_count / PLANNED_ORDERS

    baseline_late_rate = op_metrics[("baseline", "Alder")]["late_rate"]
    checked_late_rate = op_metrics[("pilot", "Alder")]["late_rate"]
    baseline_late_forecast = PLANNED_ORDERS * baseline_late_rate
    checked_late_forecast = PLANNED_ORDERS * checked_late_rate

    lines: list[str] = []
    lines += [
        "# Reproducible calculation output",
        "",
        "Command: `python3 deliverables/analyze.py` (run from the consumer directory)",
        "",
        "Inputs: `input/sources/shipment_cohorts.csv`, `input/sources/shift_operations.csv`.",
        "Definitions and assumptions come from the supplied measurement notes and decision context.",
        "",
        "## Validation",
        "",
    ]
    lines += [f"- {c}" for c in checks]
    lines += [
        "",
        "## Mature seven-day quality",
        "",
        "Rates pool counts within each band. Standardized rate = 70% × standard rate + 30% × complex rate.",
        "",
        "| Period | Line | Standard | Complex | Pooled observed mix | Planned-mix standardized |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for period in ("baseline", "pilot"):
        for line in ("Alder", "Birch"):
            s = q[(period, line, "standard")]
            c = q[(period, line, "complex")]
            pm, pn, pr = pooled[(period, line)]
            lines.append(
                f"| {period} | {line} | {int(s['mispack'])}/{int(s['mature'])} ({pct(band_rate[(period,line,'standard')])}) "
                f"| {int(c['mispack'])}/{int(c['mature'])} ({pct(band_rate[(period,line,'complex')])}) "
                f"| {int(pm)}/{int(pn)} ({pct(pr)}) | {pct(standardized[(period,line)])} |"
            )
    lines += [
        "",
        f"Alder planned-mix change: {pct(checked_rate - stop_rate)}. Birch concurrent change: {pct(birch_change)}. ",
        f"Illustrative difference in changes: {pct(did)}. Positive means a higher mispack rate for Alder relative to Birch's change.",
        "",
        "## Full-shift operations",
        "",
        "August 28 is excluded here because it was a short, unusually simple 600-order shift.",
        "Productive hours count once per date/line; overtime and training are subsets, not additions.",
        "",
        "| Period | Line | Orders | Productive hours | Training subset | Orders/hour | Late dispatch |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for period in ("baseline", "pilot"):
        for line in ("Alder", "Birch"):
            m = op_metrics[(period, line)]
            lines.append(
                f"| {period} | {line} | {int(m['orders'])} | {num(m['hours'])} | {num(m['training'])} "
                f"| {num(m['orders_per_hour'], '0.01')} | {int(m['late'])}/{int(m['orders'])} ({pct(m['late_rate'])}) |"
            )
    lines += [
        "",
        "## Twenty-shift planning scenarios",
        "",
        "Linear hours/order scaling is an assumption; the records do not identify band-specific labor.",
        "The stop scenario uses Alder baseline planned-mix quality and baseline hours/order. The all-order scenario uses Alder pilot planned-mix quality and pilot ongoing hours/order, excluding the five one-off training hours.",
        "",
        "| Item | Stop all-order check | Continue all-order check |",
        "|---|---:|---:|",
        f"| Quality rate assumption | {pct(stop_rate)} | {pct(checked_rate)} |",
        f"| Expected mispacked orders / {int(PLANNED_ORDERS):,} | {num(stop_mispacks)} | {num(checked_mispacks)} |",
        f"| Expected mispack cost | ${num(stop_mispacks * MISPACK_COST)} | ${num(checked_mispacks * MISPACK_COST)} |",
        f"| Productive hours / line / shift | {num(stop_hours_shift)} | {num(check_hours_shift)} |",
        f"| Margin to 102-hour cap | {num(HOURS_CAP - stop_hours_shift)} | {num(HOURS_CAP - check_hours_shift)} |",
        f"| Output possible at 102 hours | {num(HOURS_CAP / baseline_hpo, '0')} orders | {num(check_capacity, '0')} orders |",
        f"| Late-dispatch rate assumption | {pct(baseline_late_rate)} | {pct(checked_late_rate)} |",
        f"| Expected late dispatches / {int(PLANNED_ORDERS):,} | {num(baseline_late_forecast)} | {num(checked_late_forecast)} |",
        "",
        f"All-order checking adds {num(incremental_hours_shift)} ongoing hours/shift ({num(incremental_hours_period)} over 20 shifts), costing ${num(labor_delta_cost)} at $34/hour. It is {num(check_hours_shift - HOURS_CAP)} hours/shift above the hard cap and its projected output is {num(ORDERS_PER_SHIFT - check_capacity, '0')} orders/shift short.",
        f"Against the primary stop baseline, continuing produces {num(checked_mispacks - stop_mispacks)} more expected mispacks and costs ${num(primary_total_delta)} more including incremental labor.",
        f"Using Birch's concurrent planned-mix change as context gives a {pct(comparison_stop_rate)} stop counterfactual, {num(comparison_stop_mispacks)} expected mispacks, and ${num(comparison_total_delta)} higher total cost for continuing. This is not a causal estimate.",
        f"Even if capacity were available, the added labor requires at least {num(break_even_count)} avoided mispacks, or a {pct(break_even_rate)} absolute rate reduction, to break even. The observed planned-mix direction did not meet that condition.",
        f"At the measured full-shift late rate, checking projects {num(checked_late_forecast)} late orders ({pct(checked_late_rate)}), above the 1% maximum of {num(PLANNED_ORDERS * Decimal('0.01'), '0')}; stopping projects {num(baseline_late_forecast)} ({pct(baseline_late_rate)}).",
        "",
        "## Scope sensitivity (unmeasured)",
        "",
        f"The baseline-hours scenario leaves {num(HOURS_CAP - stop_hours_shift)} hours/shift. If Alder's observed incremental checker time ({num(checked_hpo - baseline_hpo, '0.000000')} hours per checked order) scaled linearly to a selective scope, the cap would allow about {num((HOURS_CAP - stop_hours_shift) / (checked_hpo - baseline_hpo), '0')} checked orders/shift. A complex-only scope is 432 orders and would project {num(stop_hours_shift + D('432') * (checked_hpo - baseline_hpo))} hours. This is only a sensitivity: selective checking time, quality, and dispatch were not measured, and band-specific labor is unavailable.",
        "",
        "## Attribution limits",
        "",
        "Participation was not randomized; Alder and Birch differed at baseline; the complex mix changed sharply; and both lines simultaneously received the packing-list template and mandatory catch recording. The comparator assumes Alder would otherwise have changed like Birch. Station catches are excluded because recording changed and they are not downstream harm. Forecast counts are expectations, not observed next-period results.",
    ]

    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"validated cohort_rows={len(cohorts)} operations_rows={len(ops)}")
    print(f"alder_standardized baseline={pct(stop_rate)} pilot={pct(checked_rate)} did={pct(did)}")
    print(f"planned_hours_per_shift stop={num(stop_hours_shift)} all_order={num(check_hours_shift)} cap={num(HOURS_CAP)}")
    print(f"planned_late_rate stop={pct(baseline_late_rate)} all_order={pct(checked_late_rate)}")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
