#!/usr/bin/env python3
"""Create an inspectable numerical basis for an operational intervention decision."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cohorts", required=True, type=Path)
    p.add_argument("--operations", required=True, type=Path)
    p.add_argument("--intervention-line", required=True)
    p.add_argument("--comparison-line", required=True)
    p.add_argument("--baseline-period", default="baseline")
    p.add_argument("--intervention-period", default="pilot")
    p.add_argument(
        "--planned-mix",
        required=True,
        help="Comma-separated order_band=weight pairs; weights must sum to 1",
    )
    p.add_argument(
        "--ordinary-dates",
        required=True,
        help="Comma-separated YYYY-MM-DD dates suitable for ordinary-shift comparisons",
    )
    p.add_argument("--planned-shifts", required=True, type=int)
    p.add_argument("--orders-per-shift", required=True, type=float)
    p.add_argument("--labor-cap-hours", type=float)
    p.add_argument("--error-cost", type=float)
    p.add_argument("--hour-cost", type=float)
    p.add_argument("--output", type=Path, help="Write JSON here; otherwise print to stdout")
    return p


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def parse_mix(raw: str) -> dict[str, float]:
    result: dict[str, float] = {}
    for item in raw.split(","):
        band, sep, weight = item.partition("=")
        if not sep or not band.strip():
            raise ValueError(f"invalid planned-mix item: {item!r}")
        result[band.strip()] = float(weight)
    if any(v < 0 for v in result.values()) or not math.isclose(sum(result.values()), 1.0, abs_tol=1e-9):
        raise ValueError("planned-mix weights must be nonnegative and sum to 1")
    return result


def integer(row: dict[str, str], field: str) -> int:
    value = int(row[field])
    if value < 0:
        raise ValueError(f"{field} must be nonnegative: {row}")
    return value


def number(row: dict[str, str], field: str) -> float:
    value = float(row[field])
    if value < 0:
        raise ValueError(f"{field} must be nonnegative: {row}")
    return value


def rounded(value: float | None, digits: int = 8) -> float | None:
    return None if value is None else round(value, digits)


def interval(estimate: float, variance: float) -> dict[str, float]:
    margin = 1.96 * math.sqrt(variance)
    return {"estimate": rounded(estimate), "lower": rounded(estimate - margin), "upper": rounded(estimate + margin)}


def main() -> int:
    args = parser().parse_args()
    mix = parse_mix(args.planned_mix)
    ordinary_dates = {d.strip() for d in args.ordinary_dates.split(",") if d.strip()}
    periods = [args.baseline_period, args.intervention_period]
    lines = [args.intervention_line, args.comparison_line]
    cohorts = read_csv(args.cohorts)
    operations = read_csv(args.operations)

    cohort_required = {"shipment_date", "period", "line", "order_band", "shipped_orders", "mature_orders", "confirmed_mispack_7d"}
    operation_required = {"shipment_date", "period", "line", "productive_labor_hours", "training_hours", "late_dispatch_orders"}
    if not cohorts or not cohort_required.issubset(cohorts[0]):
        raise ValueError(f"cohort CSV must contain {sorted(cohort_required)}")
    if not operations or not operation_required.issubset(operations[0]):
        raise ValueError(f"operations CSV must contain {sorted(operation_required)}")

    cohort_seen: set[tuple[str, str, str]] = set()
    cells: dict[tuple[str, str, str], dict[str, int]] = defaultdict(lambda: {"shipped": 0, "mature": 0, "errors": 0})
    shipped_by_date_line: dict[tuple[str, str], int] = defaultdict(int)
    open_window_shipped = 0
    for row in cohorts:
        key = (row["shipment_date"], row["line"], row["order_band"])
        if key in cohort_seen:
            raise ValueError(f"duplicate cohort grain: {key}")
        cohort_seen.add(key)
        shipped = integer(row, "shipped_orders")
        mature = integer(row, "mature_orders")
        errors = integer(row, "confirmed_mispack_7d")
        if mature > shipped or errors > mature:
            raise ValueError(f"invalid cohort counts: {row}")
        shipped_by_date_line[(row["shipment_date"], row["line"])] += shipped
        if mature == 0:
            open_window_shipped += shipped
        cell = cells[(row["period"], row["line"], row["order_band"])]
        cell["shipped"] += shipped
        cell["mature"] += mature
        cell["errors"] += errors

    missing_bands = set(mix) - {k[2] for k in cells}
    if missing_bands:
        raise ValueError(f"planned-mix bands absent from cohorts: {sorted(missing_bands)}")

    outcome_cells: dict[str, dict] = {}
    standardized: dict[tuple[str, str], tuple[float, float]] = {}
    raw_rates: dict[str, dict] = {}
    for period in periods:
        for line in lines:
            total_mature = total_errors = 0
            rate = variance = 0.0
            for band, weight in mix.items():
                cell = cells.get((period, line, band))
                if not cell or cell["mature"] == 0:
                    raise ValueError(f"no mature denominator for {period}/{line}/{band}")
                band_rate = cell["errors"] / cell["mature"]
                outcome_cells[f"{period}|{line}|{band}"] = {
                    **cell,
                    "rate": rounded(band_rate),
                    "planned_mix_weight": weight,
                }
                total_mature += cell["mature"]
                total_errors += cell["errors"]
                rate += weight * band_rate
                variance += weight * weight * band_rate * (1 - band_rate) / cell["mature"]
            standardized[(period, line)] = (rate, variance)
            raw_rates[f"{period}|{line}"] = {
                "mature": total_mature,
                "errors": total_errors,
                "raw_rate": rounded(total_errors / total_mature),
                "planned_mix_rate": rounded(rate),
                "planned_mix_rate_approx_95_interval": interval(rate, variance),
            }

    base_i, var_base_i = standardized[(args.baseline_period, args.intervention_line)]
    base_c, var_base_c = standardized[(args.baseline_period, args.comparison_line)]
    post_i, var_post_i = standardized[(args.intervention_period, args.intervention_line)]
    post_c, var_post_c = standardized[(args.intervention_period, args.comparison_line)]
    contemp = post_c - post_i
    did = (post_c - base_c) - (post_i - base_i)
    effects = {
        "intervention_line_change": interval(post_i - base_i, var_post_i + var_base_i),
        "comparison_line_change": interval(post_c - base_c, var_post_c + var_base_c),
        "contemporaneous_benefit": interval(contemp, var_post_i + var_post_c),
        "difference_in_differences_benefit": interval(did, var_post_i + var_post_c + var_base_i + var_base_c),
        "interpretation": "Positive benefit means fewer downstream adverse outcomes on the intervention line; intervals cover sampling variation only.",
    }
    effects_by_band: dict[str, dict] = {}
    for band in mix:
        def band_rate(period: str, line: str) -> tuple[float, float]:
            cell = cells[(period, line, band)]
            rate = cell["errors"] / cell["mature"]
            return rate, rate * (1 - rate) / cell["mature"]

        b_i, vb_i = band_rate(args.baseline_period, args.intervention_line)
        b_c, vb_c = band_rate(args.baseline_period, args.comparison_line)
        p_i, vp_i = band_rate(args.intervention_period, args.intervention_line)
        p_c, vp_c = band_rate(args.intervention_period, args.comparison_line)
        effects_by_band[band] = {
            "contemporaneous_benefit": interval(p_c - p_i, vp_c + vp_i),
            "difference_in_differences_benefit": interval((p_c - b_c) - (p_i - b_i), vp_c + vp_i + vb_c + vb_i),
        }

    operation_seen: set[tuple[str, str]] = set()
    ordinary: dict[tuple[str, str], list[dict[str, float]]] = defaultdict(list)
    for row in operations:
        key = (row["shipment_date"], row["line"])
        if key in operation_seen:
            raise ValueError(f"duplicate operation grain: {key}")
        operation_seen.add(key)
        if key not in shipped_by_date_line:
            raise ValueError(f"operation row has no matching cohorts: {key}")
        if row["shipment_date"] not in ordinary_dates or row["line"] not in lines or row["period"] not in periods:
            continue
        productive = number(row, "productive_labor_hours")
        training = number(row, "training_hours")
        if training > productive:
            raise ValueError(f"training exceeds productive hours: {row}")
        ordinary[(row["period"], row["line"])].append({
            "orders": shipped_by_date_line[key],
            "productive": productive,
            "ongoing": productive - training,
            "training": training,
            "late": integer(row, "late_dispatch_orders"),
        })

    operation_summary: dict[str, dict] = {}
    labor_rates: dict[tuple[str, str], float] = {}
    for period in periods:
        for line in lines:
            rows = ordinary.get((period, line), [])
            if not rows:
                raise ValueError(f"no ordinary operation rows for {period}/{line}")
            orders = sum(r["orders"] for r in rows)
            late = sum(r["late"] for r in rows)
            ongoing = sum(r["ongoing"] for r in rows)
            labor_rate = ongoing / orders
            labor_rates[(period, line)] = labor_rate
            projected = labor_rate * args.orders_per_shift
            summary = {
                "shifts": len(rows),
                "orders": orders,
                "late_dispatch_orders": late,
                "late_dispatch_rate": rounded(late / orders),
                "mean_productive_hours_per_shift": rounded(mean(r["productive"] for r in rows)),
                "mean_training_hours_per_shift": rounded(mean(r["training"] for r in rows)),
                "mean_ongoing_hours_per_shift": rounded(mean(r["ongoing"] for r in rows)),
                "ongoing_hours_per_order": rounded(labor_rate),
                "proportional_projected_hours_at_planned_volume": rounded(projected),
            }
            if args.labor_cap_hours is not None:
                summary["projected_headroom_to_cap_hours"] = rounded(args.labor_cap_hours - projected)
            operation_summary[f"{period}|{line}"] = summary

    pilot_gap = labor_rates[(args.intervention_period, args.intervention_line)] - labor_rates[(args.intervention_period, args.comparison_line)]
    baseline_gap = labor_rates[(args.baseline_period, args.intervention_line)] - labor_rates[(args.baseline_period, args.comparison_line)]
    labor_effects = {
        "contemporaneous_incremental_hours_per_planned_shift": rounded(pilot_gap * args.orders_per_shift),
        "difference_in_differences_incremental_hours_per_planned_shift": rounded((pilot_gap - baseline_gap) * args.orders_per_shift),
        "projection_model": "ordinary-shift ongoing hours per observed order multiplied by planned orders; training excluded",
    }

    total_volume = args.planned_shifts * args.orders_per_shift
    planning = {
        "planned_shifts": args.planned_shifts,
        "orders_per_shift": args.orders_per_shift,
        "total_orders": total_volume,
        "planned_mix": mix,
    }
    if args.error_cost is not None:
        planning["quality_effect_scenarios"] = {}
        for label, effect in (("contemporaneous", contemp), ("difference_in_differences", did)):
            avoided = total_volume * effect
            planning["quality_effect_scenarios"][label] = {
                "avoided_outcomes_point_estimate": rounded(avoided, 2),
                "avoided_cost_point_estimate": rounded(avoided * args.error_cost, 2),
            }
        planning["error_cost_per_outcome"] = args.error_cost
        planning["quality_effect_scenarios_by_band"] = {}
        for band, weight in mix.items():
            band_volume = total_volume * weight
            planning["quality_effect_scenarios_by_band"][band] = {"planned_orders": band_volume}
            for label in ("contemporaneous_benefit", "difference_in_differences_benefit"):
                estimate = effects_by_band[band][label]["estimate"]
                avoided = band_volume * estimate
                planning["quality_effect_scenarios_by_band"][band][label] = {
                    "avoided_outcomes_point_estimate": rounded(avoided, 2),
                    "avoided_cost_point_estimate": rounded(avoided * args.error_cost, 2),
                }
    if args.hour_cost is not None:
        planning["labor_cost_scenarios"] = {}
        for label, per_shift in (
            ("contemporaneous", labor_effects["contemporaneous_incremental_hours_per_planned_shift"]),
            ("difference_in_differences", labor_effects["difference_in_differences_incremental_hours_per_planned_shift"]),
        ):
            hours = per_shift * args.planned_shifts
            planning["labor_cost_scenarios"][label] = {
                "incremental_hours": rounded(hours, 2),
                "incremental_cost": rounded(hours * args.hour_cost, 2),
            }
        planning["hour_cost"] = args.hour_cost
        comparison_projected = labor_rates[(args.intervention_period, args.comparison_line)] * args.orders_per_shift
        planning["equal_effort_scope_sensitivity"] = {}
        for band, weight in mix.items():
            planning["equal_effort_scope_sensitivity"][band] = {
                "warning": "Assumes intervention effort is proportional to order count; this scope has not been observed.",
                "projected_hours_per_shift": {},
            }
            for label, per_shift in (
                ("contemporaneous", labor_effects["contemporaneous_incremental_hours_per_planned_shift"]),
                ("difference_in_differences", labor_effects["difference_in_differences_incremental_hours_per_planned_shift"]),
            ):
                scoped_increment = per_shift * weight
                planning["equal_effort_scope_sensitivity"][band]["projected_hours_per_shift"][label] = rounded(comparison_projected + scoped_increment)

    result = {
        "metadata": {
            "cohorts": str(args.cohorts),
            "operations": str(args.operations),
            "ordinary_dates": sorted(ordinary_dates),
            "open_window_shipped_orders_excluded_from_mature_outcomes": open_window_shipped,
            "interval_note": "Approximate 95% normal intervals reflect binomial sampling variation only, not design bias or confounding.",
        },
        "outcome_cells": outcome_cells,
        "outcome_line_period": raw_rates,
        "outcome_effects": effects,
        "outcome_effects_by_band": effects_by_band,
        "ordinary_shift_operations": operation_summary,
        "labor_effects": labor_effects,
        "planning": planning,
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
