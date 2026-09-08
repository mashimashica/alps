#!/usr/bin/env python3
"""Reproduce the Cedar Quay packing-check numerical basis.

Invocation (from the C-U115 consumer directory):
    python3 deliverables/analyze.py > deliverables/numerical_basis.md

Dependencies: Python 3 standard library only.
Inputs are read unchanged from input/sources/.
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COHORTS_PATH = ROOT / "input/sources/shipment_cohorts.csv"
OPERATIONS_PATH = ROOT / "input/sources/shift_operations.csv"
FULL_SHIFT_DATES = {"2026-07-06", "2026-07-07", "2026-07-08",
                    "2026-07-20", "2026-07-21", "2026-07-22"}
PLANNED_SHIFTS = 20
PLANNED_ORDERS_PER_LINE_SHIFT = 800
HOURS_LIMIT_PER_LINE_SHIFT = 68
ERROR_COST = 48
LABOR_COST = 32


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def rate(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else float("nan")


def pct(value: float) -> str:
    return f"{100 * value:.3f}%"


def pp(value: float) -> str:
    return f"{100 * value:.3f} pp"


cohorts = read_csv(COHORTS_PATH)
operations = read_csv(OPERATIONS_PATH)

cohort_ints = ["shipped_orders", "mature_orders", "confirmed_mispack_7d", "station_catches"]
operation_ints = ["productive_labor_hours", "overtime_hours", "training_hours", "late_dispatch_orders"]
for row in cohorts:
    for field in cohort_ints:
        row[field] = int(row[field])
for row in operations:
    for field in operation_ints:
        row[field] = int(row[field])

# Structural and range checks.
checks: list[tuple[str, bool, str]] = []
cohort_keys = [(r["shipment_date"], r["line"], r["order_band"]) for r in cohorts]
operation_keys = [(r["shipment_date"], r["line"]) for r in operations]
checks.append(("Unique cohort keys", len(cohort_keys) == len(set(cohort_keys)), f"{len(cohort_keys)} rows"))
checks.append(("Unique operation keys", len(operation_keys) == len(set(operation_keys)), f"{len(operation_keys)} rows"))
checks.append(("Cohort count bounds", all(
    0 <= r["confirmed_mispack_7d"] <= r["mature_orders"] <= r["shipped_orders"]
    and 0 <= r["station_catches"] <= r["shipped_orders"] for r in cohorts
), "0 <= errors <= mature <= shipped; 0 <= catches <= shipped"))
checks.append(("Labor subset bounds", all(
    0 <= r["overtime_hours"] <= r["productive_labor_hours"]
    and 0 <= r["training_hours"] <= r["productive_labor_hours"] for r in operations
), "overtime and training do not exceed productive hours"))

cohort_pairs = defaultdict(list)
for row in cohorts:
    cohort_pairs[(row["shipment_date"], row["line"])].append(row)
expected_bands = {"standard", "complex"}
complete_band_pairs = all({r["order_band"] for r in rows} == expected_bands for rows in cohort_pairs.values())
checks.append(("Both bands per date/line", complete_band_pairs, f"{len(cohort_pairs)} date/line pairs"))
checks.append(("Operation/cohort date-line match", set(operation_keys) == set(cohort_pairs), f"{len(operation_keys)} pairs"))

late_bounds = True
for op in operations:
    shipped = sum(r["shipped_orders"] for r in cohort_pairs[(op["shipment_date"], op["line"])])
    late_bounds &= 0 <= op["late_dispatch_orders"] <= shipped
checks.append(("Late-dispatch bounds", late_bounds, "0 <= late <= shipped at whole-line grain"))


def cohort_sum(filters: dict[str, str], field: str, *, full_only: bool = False,
               mature_only: bool = False) -> int:
    total = 0
    for row in cohorts:
        if full_only and row["shipment_date"] not in FULL_SHIFT_DATES:
            continue
        if mature_only and row["mature_orders"] == 0:
            continue
        if all(row[k] == v for k, v in filters.items()):
            total += row[field]
    return total


def operation_sum(filters: dict[str, str], field: str, *, full_only: bool = False) -> int:
    total = 0
    for row in operations:
        if full_only and row["shipment_date"] not in FULL_SHIFT_DATES:
            continue
        if all(row[k] == v for k, v in filters.items()):
            total += row[field]
    return total


# Mature downstream outcomes: only the six ordinary full shifts are eligible.
outcomes: dict[tuple[str, str, str], tuple[int, int]] = {}
for period in ("baseline", "pilot"):
    for line in ("Harbor", "Ridge"):
        for band in ("standard", "complex", "all"):
            filt = {"period": period, "line": line}
            if band != "all":
                filt["order_band"] = band
            mature = cohort_sum(filt, "mature_orders", full_only=True, mature_only=True)
            errors = cohort_sum(filt, "confirmed_mispack_7d", full_only=True, mature_only=True)
            outcomes[(period, line, band)] = (errors, mature)

harbor_baseline_rate = rate(*outcomes[("baseline", "Harbor", "all")])
harbor_pilot_rate = rate(*outcomes[("pilot", "Harbor", "all")])
ridge_baseline_rate = rate(*outcomes[("baseline", "Ridge", "all")])
ridge_pilot_rate = rate(*outcomes[("pilot", "Ridge", "all")])
harbor_change = harbor_pilot_rate - harbor_baseline_rate
ridge_change = ridge_pilot_rate - ridge_baseline_rate
did = harbor_change - ridge_change
pilot_gap = harbor_pilot_rate - ridge_pilot_rate

# Whole-line full-shift labor. Strip only Harbor's documented 3 introductory hours.
labor: dict[tuple[str, str], dict[str, float]] = {}
for period in ("baseline", "pilot"):
    for line in ("Harbor", "Ridge"):
        rows = [r for r in operations if r["period"] == period and r["line"] == line
                and r["shipment_date"] in FULL_SHIFT_DATES]
        productive = sum(r["productive_labor_hours"] for r in rows)
        overtime = sum(r["overtime_hours"] for r in rows)
        training = sum(r["training_hours"] for r in rows)
        recurring = productive - training
        shipped = cohort_sum({"period": period, "line": line}, "shipped_orders", full_only=True)
        labor[(period, line)] = {
            "shifts": len(rows), "productive": productive, "overtime": overtime,
            "training": training,
            "recurring": recurring, "avg": recurring / len(rows),
            "hours_per_order": recurring / shipped,
        }

checked_hours_per_order = labor[("pilot", "Harbor")]["hours_per_order"]
no_check_hours_per_order = labor[("pilot", "Ridge")]["hours_per_order"]
checked_projected_hours = checked_hours_per_order * PLANNED_ORDERS_PER_LINE_SHIFT
no_check_projected_hours = no_check_hours_per_order * PLANNED_ORDERS_PER_LINE_SHIFT
checked_capacity = math.floor(HOURS_LIMIT_PER_LINE_SHIFT / checked_hours_per_order)
no_check_capacity = math.floor(HOURS_LIMIT_PER_LINE_SHIFT / no_check_hours_per_order)
incremental_hours_per_line_shift = checked_projected_hours - no_check_projected_hours

# Dispatch at native whole-line grain; mature status is irrelevant.
dispatch: dict[tuple[str, str, str], tuple[int, int]] = {}
for period in ("baseline", "pilot"):
    for line in ("Harbor", "Ridge"):
        for shift_scope in ("full", "all"):
            full_only = shift_scope == "full"
            late = operation_sum({"period": period, "line": line}, "late_dispatch_orders", full_only=full_only)
            shipped = cohort_sum({"period": period, "line": line}, "shipped_orders", full_only=full_only)
            dispatch[(period, line, shift_scope)] = (late, shipped)

# Catches remain a process proxy and are never added to downstream outcomes.
catches: dict[tuple[str, str, str], tuple[int, int]] = {}
for period in ("baseline", "pilot"):
    for line in ("Harbor", "Ridge"):
        for shift_scope in ("full", "all"):
            full_only = shift_scope == "full"
            caught = cohort_sum({"period": period, "line": line}, "station_catches", full_only=full_only)
            shipped = cohort_sum({"period": period, "line": line}, "shipped_orders", full_only=full_only)
            catches[(period, line, shift_scope)] = (caught, shipped)

# Next-period economics. Rates are conditional planning assumptions, not causal estimates.
orders_per_line = PLANNED_SHIFTS * PLANNED_ORDERS_PER_LINE_SHIFT
recurring_hours_per_line = incremental_hours_per_line_shift * PLANNED_SHIFTS
recurring_cost_per_line = recurring_hours_per_line * LABOR_COST
scenarios = [
    ("Conservative comparator", ridge_pilot_rate, harbor_pilot_rate),
    ("Favorable raw pre/post", harbor_baseline_rate, harbor_pilot_rate),
]

print("# Cedar Quay numerical basis")
print()
print("Generated by `python3 deliverables/analyze.py > deliverables/numerical_basis.md` using Python 3 standard library only.")
print("Inputs: `input/sources/shipment_cohorts.csv` and `input/sources/shift_operations.csv`.")
print()
print("## Input checks")
print()
print("| Check | Result | Detail |")
print("|---|---:|---|")
for name, passed, detail in checks:
    print(f"| {name} | {'PASS' if passed else 'FAIL'} | {detail} |")
assert all(passed for _, passed, _ in checks), "Input validation failed"

print()
print("## Mature seven-day downstream outcomes — ordinary full shifts")
print()
print("July 31 is excluded because its cohorts have no elapsed outcome window. All eligible cohorts have the planned 75% standard / 25% complex mix, so direct and next-period-mix-standardized rates are identical.")
print()
print("| Period | Line | Band | Confirmed mispacks | Mature orders | Rate |")
print("|---|---|---|---:|---:|---:|")
for period in ("baseline", "pilot"):
    for line in ("Harbor", "Ridge"):
        for band in ("standard", "complex", "all"):
            errors, mature = outcomes[(period, line, band)]
            print(f"| {period} | {line} | {band} | {errors} | {mature} | {pct(rate(errors, mature))} |")
print()
print(f"- Harbor change = {pct(harbor_pilot_rate)} - {pct(harbor_baseline_rate)} = {pp(harbor_change)}.")
print(f"- Ridge change = {pct(ridge_pilot_rate)} - {pct(ridge_baseline_rate)} = {pp(ridge_change)}.")
print(f"- Comparator-adjusted change = ({pp(harbor_change)}) - ({pp(ridge_change)}) = {pp(did)}; equivalently, the pilot Harbor–Ridge gap is {pp(pilot_gap)}.")
hb_std = rate(*outcomes[("baseline", "Harbor", "standard")])
hb_complex = rate(*outcomes[("baseline", "Harbor", "complex")])
hp_std = rate(*outcomes[("pilot", "Harbor", "standard")])
hp_complex = rate(*outcomes[("pilot", "Harbor", "complex")])
print(f"- Next-mix standardization: Harbor baseline = 0.75 × {pct(hb_std)} + 0.25 × {pct(hb_complex)} = {pct(0.75 * hb_std + 0.25 * hb_complex)}; Harbor pilot = 0.75 × {pct(hp_std)} + 0.25 × {pct(hp_complex)} = {pct(0.75 * hp_std + 0.25 * hp_complex)}.")
for band in ("standard", "complex"):
    hb = rate(*outcomes[("baseline", "Harbor", band)])
    hp = rate(*outcomes[("pilot", "Harbor", band)])
    rb = rate(*outcomes[("baseline", "Ridge", band)])
    rp = rate(*outcomes[("pilot", "Ridge", band)])
    print(f"- {band.capitalize()} comparator-adjusted change = ({pp(hp - hb)}) - ({pp(rp - rb)}) = {pp((hp - hb) - (rp - rb))}.")

print()
print("## Process catches — kept separate from downstream mispacks")
print()
print("| Period | Line | Shift scope | Station catches | Shipped orders | Rate |")
print("|---|---|---|---:|---:|---:|")
for period in ("baseline", "pilot"):
    for line in ("Harbor", "Ridge"):
        for scope in (("full",) if period == "baseline" else ("full", "all")):
            caught, shipped = catches[(period, line, scope)]
            print(f"| {period} | {line} | {scope} | {caught} | {shipped} | {pct(rate(caught, shipped))} |")

print()
print("## Whole-line full-shift labor and capacity")
print()
print("| Period | Line | Full shifts | Productive h | Overtime h | Training h | Recurring h | Recurring h/shift | h/order |")
print("|---|---|---:|---:|---:|---:|---:|---:|---:|")
for period in ("baseline", "pilot"):
    for line in ("Harbor", "Ridge"):
        x = labor[(period, line)]
        print(f"| {period} | {line} | {int(x['shifts'])} | {x['productive']:.0f} | {x['overtime']:.0f} | {x['training']:.0f} | {x['recurring']:.0f} | {x['avg']:.2f} | {x['hours_per_order']:.5f} |")
print()
print(f"- Checked planning case: {checked_hours_per_order:.5f} h/order × 800 = {checked_projected_hours:.2f} h/line-shift, leaving {HOURS_LIMIT_PER_LINE_SHIFT - checked_projected_hours:.2f} h under the 68 h cap.")
print(f"- Linear same-mix checked capacity = floor(68 / {checked_hours_per_order:.5f}) = {checked_capacity} orders/line-shift.")
print(f"- Contemporary no-check case: {no_check_hours_per_order:.5f} h/order × 800 = {no_check_projected_hours:.2f} h, with floor(68 / {no_check_hours_per_order:.5f}) = {no_check_capacity} orders.")
print(f"- Assumed incremental recurring load for a checked line = {checked_projected_hours:.2f} - {no_check_projected_hours:.2f} = {incremental_hours_per_line_shift:.2f} h/shift. Band-specific labor is unavailable, so selective-scope capacity cannot be identified.")

print()
print("## Dispatch — immediately observable")
print()
print("| Period | Line | Shift scope | Late | Shipped | Rate | Next-period late at observed full-shift rate |")
print("|---|---|---|---:|---:|---:|---:|")
for period in ("baseline", "pilot"):
    for line in ("Harbor", "Ridge"):
        for scope in (("full",) if period == "baseline" else ("full", "all")):
            late, shipped = dispatch[(period, line, scope)]
            projection = "—"
            if period == "pilot" and scope == "full":
                projection = f"{rate(late, shipped) * orders_per_line:.1f} of {orders_per_line}"
            print(f"| {period} | {line} | {scope} | {late} | {shipped} | {pct(rate(late, shipped))} | {projection} |")
print(f"The commitment permits at most {int(0.01 * orders_per_line)} late orders per line across {orders_per_line} planned orders. The projection is conditional, not a guarantee.")

print()
print("## Twenty-shift cost scenarios")
print()
print(f"Each line has {orders_per_line:,} orders. Incremental recurring labor is {incremental_hours_per_line_shift:.2f} h × {PLANNED_SHIFTS} = {recurring_hours_per_line:.0f} h/line, costing ${recurring_cost_per_line:,.0f}. Ridge may also use up to 3 separately funded startup hours = ${3 * LABOR_COST:,.0f}; Harbor's startup is already observed and is not repeated.")
print()
print("| Scenario | No-check counterfactual | Checked planning rate | Avoided errors/line | Gross/line | Recurring labor/line | Net/line | Net, two lines | Net after Ridge startup |")
print("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
for name, counterfactual, checked in scenarios:
    avoided = (counterfactual - checked) * orders_per_line
    gross = avoided * ERROR_COST
    net = gross - recurring_cost_per_line
    net_two = 2 * net
    print(f"| {name} | {pct(counterfactual)} | {pct(checked)} | {avoided:.0f} | ${gross:,.0f} | ${recurring_cost_per_line:,.0f} | ${net:,.0f} | ${net_two:,.0f} | ${net_two - 3 * LABOR_COST:,.0f} |")

break_even_errors_per_shift = incremental_hours_per_line_shift * LABOR_COST / ERROR_COST
break_even_rate = break_even_errors_per_shift / PLANNED_ORDERS_PER_LINE_SHIFT
print()
print(f"Break-even benefit per checked line = ({incremental_hours_per_line_shift:.2f} h × ${LABOR_COST}) / ${ERROR_COST} = {break_even_errors_per_shift:.2f} avoided errors/shift, or {pp(break_even_rate)} at 800 orders. Dispatch failures are not priced.")
for name, counterfactual, checked in scenarios:
    avoided = (counterfactual - checked) * orders_per_line
    marginal_ridge_net = avoided * ERROR_COST - recurring_cost_per_line - 3 * LABOR_COST
    print(f"- {name} marginal Ridge expansion net after maximum startup = ${marginal_ridge_net:,.0f}.")
print()
print("## Assumptions and interpretation limits")
print()
print("- Observed figures above are descriptive. Harbor volunteered; assignment was nonrandom, there are only three mature full shifts per period, and the comparison line does not prove causality.")
print("- The conservative scenario applies Harbor's observed checked rate and the contemporaneous Ridge no-check rate to both planned lines. The favorable scenario uses Harbor's own baseline as the no-check counterfactual. Applying Harbor's effect and 3-hour recurring increment to Ridge is an unmeasured expansion assumption.")
print("- Projections scale linearly at the unchanged 75%/25% mix. No band-specific labor data exist. July 31 informs catches and dispatch only and is not a full-shift capacity test.")
