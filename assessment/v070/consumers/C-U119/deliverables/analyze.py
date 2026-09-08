#!/usr/bin/env python3
"""Reproduce the Cedar Quay packing-check decision basis.

Inputs are read-only CSVs in ../input/sources. Outputs are written beside this
script. Only ordinary full shifts (July 6-8 and July 20-22) are used for the
matched baseline/pilot comparison. Delayed outcomes use mature_orders only;
July 31 is retained solely as separate immediate-operations context.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCES = HERE.parent / "input" / "sources"
COHORTS = SOURCES / "shipment_cohorts.csv"
OPERATIONS = SOURCES / "shift_operations.csv"
FULL_DATES = {
    "baseline": {"2026-07-06", "2026-07-07", "2026-07-08"},
    "pilot": {"2026-07-20", "2026-07-21", "2026-07-22"},
}
PLANNED_SHIFTS = 20
ORDERS_PER_SHIFT = 800
PLANNED_ORDERS = PLANNED_SHIFTS * ORDERS_PER_SHIFT
ORDER_WEIGHTS = {"standard": 0.75, "complex": 0.25}
MISPACK_COST = 48.0
LABOR_COST = 32.0
HOUR_LIMIT = 68.0


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def validate(cohorts: list[dict[str, str]], operations: list[dict[str, str]]) -> None:
    ckeys = [(r["shipment_date"], r["line"], r["order_band"]) for r in cohorts]
    okeys = [(r["shipment_date"], r["line"]) for r in operations]
    assert len(ckeys) == len(set(ckeys)), "duplicate shipment cohort key"
    assert len(okeys) == len(set(okeys)), "duplicate operations key"
    assert {k[:2] for k in ckeys} == set(okeys), "cohort/operations dates or lines do not reconcile"
    assert len(cohorts) == len(operations) * 2, "expected two order bands per line-date"
    for r in cohorts:
        shipped = int(r["shipped_orders"])
        mature = int(r["mature_orders"])
        mispack = int(r["confirmed_mispack_7d"])
        catches = int(r["station_catches"])
        assert min(shipped, mature, mispack, catches) >= 0, "negative cohort count"
        assert mature <= shipped and mispack <= mature, "invalid cohort denominator"
    for r in operations:
        productive = float(r["productive_labor_hours"])
        overtime = float(r["overtime_hours"])
        training = float(r["training_hours"])
        late = int(r["late_dispatch_orders"])
        assert min(productive, overtime, training, late) >= 0, "negative operations value"
        assert overtime <= productive and training <= productive, "labor subset exceeds productive hours"
        shipped = sum(int(c["shipped_orders"]) for c in cohorts if c["shipment_date"] == r["shipment_date"] and c["line"] == r["line"])
        assert late <= shipped, "late dispatch exceeds shipped orders"


def main() -> None:
    cohorts = read_csv(COHORTS)
    operations = read_csv(OPERATIONS)
    validate(cohorts, operations)

    category = defaultdict(lambda: {"shipped": 0, "mature": 0, "mispack": 0, "catches": 0})
    for r in cohorts:
        period, line, band, date = r["period"], r["line"], r["order_band"], r["shipment_date"]
        if date in FULL_DATES[period]:
            cell = category[(period, line, band)]
            for out, field in (("shipped", "shipped_orders"), ("mature", "mature_orders"), ("mispack", "confirmed_mispack_7d"), ("catches", "station_catches")):
                cell[out] += int(r[field])

    cat_rows = []
    for (period, line, band), v in sorted(category.items()):
        cat_rows.append({
            "period": period,
            "line": line,
            "band": band,
            **v,
            "mispack_rate": v["mispack"] / v["mature"],
            "catch_rate_per_shipped": v["catches"] / v["shipped"],
        })

    totals = defaultdict(lambda: {"shipped": 0, "mature": 0, "mispack": 0, "catches": 0})
    for row in cat_rows:
        cell = totals[(row["period"], row["line"])]
        for field in ("shipped", "mature", "mispack", "catches"):
            cell[field] += row[field]

    labor = defaultdict(lambda: {"hours": 0.0, "overtime": 0.0, "training": 0.0, "late": 0})
    for r in operations:
        key = (r["period"], r["line"])
        if r["shipment_date"] in FULL_DATES[r["period"]]:
            labor[key]["hours"] += float(r["productive_labor_hours"])
            labor[key]["overtime"] += float(r["overtime_hours"])
            labor[key]["training"] += float(r["training_hours"])
            labor[key]["late"] += int(r["late_dispatch_orders"])

    period_rows = []
    for key in sorted(totals):
        period, line = key
        v, l = totals[key], labor[key]
        ongoing_hours = l["hours"] - l["training"]
        period_rows.append({
            "period": period,
            "line": line,
            **v,
            **l,
            "mispack_rate": v["mispack"] / v["mature"],
            "dispatch_rate": l["late"] / v["shipped"],
            "orders_per_paid_hour": v["shipped"] / l["hours"],
            "paid_hours_per_order": l["hours"] / v["shipped"],
            "ongoing_hours_ex_training": ongoing_hours,
            "orders_per_ongoing_hour": v["shipped"] / ongoing_hours,
            "ongoing_hours_per_order": ongoing_hours / v["shipped"],
        })

    rates = {(r["period"], r["line"], r["band"]): r["mispack_rate"] for r in cat_rows}
    standardized = {
        (period, line): sum(ORDER_WEIGHTS[band] * rates[(period, line, band)] for band in ORDER_WEIGHTS)
        for period in ("baseline", "pilot") for line in ("Harbor", "Ridge")
    }
    harbor_change = standardized[("pilot", "Harbor")] - standardized[("baseline", "Harbor")]
    ridge_change = standardized[("pilot", "Ridge")] - standardized[("baseline", "Ridge")]
    did = harbor_change - ridge_change

    baseline_h = labor[("baseline", "Harbor")]["hours"] / 3
    pilot_h_ongoing = (labor[("pilot", "Harbor")]["hours"] - labor[("pilot", "Harbor")]["training"]) / 3
    incremental_hours_per_shift = pilot_h_ongoing - baseline_h
    projected_incremental_hours = incremental_hours_per_shift * PLANNED_SHIFTS
    projected_labor_cost = projected_incremental_hours * LABOR_COST
    projected_avoided = -did * PLANNED_ORDERS
    projected_avoided_cost = projected_avoided * MISPACK_COST
    projected_net = projected_avoided_cost - projected_labor_cost
    break_even_rate = projected_labor_cost / (PLANNED_ORDERS * MISPACK_COST)

    short = {}
    for line in ("Harbor", "Ridge"):
        shipped = sum(int(r["shipped_orders"]) for r in cohorts if r["shipment_date"] == "2026-07-31" and r["line"] == line)
        catches = sum(int(r["station_catches"]) for r in cohorts if r["shipment_date"] == "2026-07-31" and r["line"] == line)
        op = next(r for r in operations if r["shipment_date"] == "2026-07-31" and r["line"] == line)
        short[line] = {"shipped": shipped, "mature": 0, "catches": catches, "hours": float(op["productive_labor_hours"]), "late": int(op["late_dispatch_orders"]), "dispatch_rate": int(op["late_dispatch_orders"]) / shipped}

    analysis = {
        "inputs": [str(COHORTS), str(OPERATIONS)],
        "inclusion": "Matched comparison uses ordinary full shifts 2026-07-06..08 and 2026-07-20..22. Delayed outcomes require mature_orders. 2026-07-31 is separate immediate context.",
        "validation": "PASS: unique keys, two bands per line-date, cohort/operations reconciliation, nonnegative values, valid denominators, and labor-subset constraints.",
        "category_full_shift": cat_rows,
        "line_period_full_shift": period_rows,
        "standardized_rates_75_25": {f"{p}_{l}": v for (p, l), v in standardized.items()},
        "harbor_change": harbor_change,
        "ridge_change": ridge_change,
        "difference_in_changes": did,
        "planning": {
            "orders": PLANNED_ORDERS,
            "counterfactual": "Harbor would have followed Ridge's concurrent standardized change from its own baseline.",
            "projected_avoided_mispacks": projected_avoided,
            "projected_avoided_cost": projected_avoided_cost,
            "baseline_hours_per_shift": baseline_h,
            "pilot_ongoing_hours_per_shift": pilot_h_ongoing,
            "incremental_hours_per_shift": incremental_hours_per_shift,
            "projected_incremental_hours": projected_incremental_hours,
            "projected_incremental_labor_cost": projected_labor_cost,
            "illustrative_net_cost_reduction": projected_net,
            "break_even_effect_rate": break_even_rate,
            "hour_limit_per_shift": HOUR_LIMIT,
            "projected_hour_buffer": HOUR_LIMIT - pilot_h_ongoing,
        },
        "short_shift_2026_07_31": short,
    }
    (HERE / "analysis.json").write_text(json.dumps(analysis, indent=2) + "\n", encoding="utf-8")

    def pct(x: float) -> str:
        return f"{100*x:.3f}%"

    md = [
        "# Reproducible numerical basis",
        "",
        "Run from the consumer directory:",
        "",
        "```bash",
        "python3 deliverables/analyze.py",
        "```",
        "",
        "The script uses only Python's standard library and writes `deliverables/analysis.json`. Inputs and inclusion rules are recorded in the script and JSON output.",
        "",
        "## Full-shift line totals",
        "",
        "| Period | Line | Mature mispacks | Mispack rate | Paid hours | Ongoing hours excluding training | Orders/hour (paid) | Paid hours/order | Late dispatches | Dispatch rate |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in period_rows:
        md.append(f"| {r['period']} | {r['line']} | {r['mispack']}/{r['mature']} | {pct(r['mispack_rate'])} | {r['hours']:.0f} | {r['ongoing_hours_ex_training']:.0f} | {r['orders_per_paid_hour']:.2f} | {r['paid_hours_per_order']:.4f} | {r['late']}/{r['shipped']} | {pct(r['dispatch_rate'])} |")
    md += [
        "",
        "## Common-mix quality comparison",
        "",
        "The planned 75% standard / 25% complex mix equals the observed mix. Pooled and standardized rates therefore coincide.",
        "",
        f"- Harbor: {pct(standardized[('baseline','Harbor')])} to {pct(standardized[('pilot','Harbor')])}, change {pct(harbor_change)}.",
        f"- Ridge: {pct(standardized[('baseline','Ridge')])} to {pct(standardized[('pilot','Ridge')])}, change {pct(ridge_change)}.",
        f"- Illustrative difference in changes: {pct(did)}, or {projected_avoided:.0f} fewer mispacks over {PLANNED_ORDERS:,} Harbor orders if the comparison assumption holds.",
        "",
        "Category rates and all raw aggregate counts are in `analysis.json`.",
        "",
        "## Planning arithmetic",
        "",
        f"- Harbor baseline labor: {baseline_h:.0f} hours/shift. Pilot ongoing labor after removing the three one-off training hours: {pilot_h_ongoing:.0f} hours/shift.",
        f"- Linear projection: {incremental_hours_per_shift:.0f} additional hours/shift × {PLANNED_SHIFTS} = {projected_incremental_hours:.0f} hours; at ${LABOR_COST:.0f}/hour = ${projected_labor_cost:,.0f}.",
        f"- Comparison-adjusted outcome value: {projected_avoided:.0f} × ${MISPACK_COST:.0f} = ${projected_avoided_cost:,.0f}.",
        f"- Illustrative net cost reduction: ${projected_avoided_cost:,.0f} − ${projected_labor_cost:,.0f} = ${projected_net:,.0f}.",
        f"- Break-even quality effect: {pct(break_even_rate)} ({break_even_rate*ORDERS_PER_SHIFT:.1f} mispacks per 800-order shift; {break_even_rate*PLANNED_ORDERS:.0f} over the period).",
        f"- Projected ongoing labor is {pilot_h_ongoing:.0f} hours/shift, leaving {HOUR_LIMIT-pilot_h_ongoing:.0f} hours under the 68-hour limit. This is linear scaling from aggregate observed labor, not a category workload estimate.",
        "",
        "July 31 was an immature 320-order short shift and is excluded from mature quality and matched full-shift capacity evidence. Its immediate Harbor dispatch result was 2/320 (0.625%); this is context only.",
    ]
    (HERE / "numerical-basis.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("validation: PASS")
    print(f"Harbor mature mispack: {totals[('baseline','Harbor')]['mispack']}/{totals[('baseline','Harbor')]['mature']} -> {totals[('pilot','Harbor')]['mispack']}/{totals[('pilot','Harbor')]['mature']}")
    print(f"Ridge mature mispack: {totals[('baseline','Ridge')]['mispack']}/{totals[('baseline','Ridge')]['mature']} -> {totals[('pilot','Ridge')]['mispack']}/{totals[('pilot','Ridge')]['mature']}")
    print(f"difference_in_changes={pct(did)}")
    print(f"planning: avoided_mispacks={projected_avoided:.0f}, incremental_hours={projected_incremental_hours:.0f}, net=${projected_net:,.0f}, break_even={pct(break_even_rate)}")
    print("wrote deliverables/analysis.json and deliverables/numerical-basis.md")


if __name__ == "__main__":
    main()
