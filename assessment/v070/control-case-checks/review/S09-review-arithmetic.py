"""Targeted independent review of decision-changing S09 quantities, stdlib only.

Reads the two authorized control packets. Does not import author calculations,
run an API, load a Skill, run a model, or test an operational intervention.
Parameters below transcribe each packet's decision context and snapshot date.
All reported fractions are exact, including fractional expected error counts.
"""

import csv
import hashlib
import json
from datetime import date
from fractions import Fraction as F
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PARAMETERS = {
    "ordinary": ("Harbor", "Ridge", 800, F(3, 4), 68, 48, 32, "2026-08-03"),
    "challenging": ("Alder", "Birch", 1440, F(7, 10), 102, 55, 34, "2026-08-31"),
}


def review(case, parameters):
    treated, comparison, planned, standard_share, cap, error_cost, wage, snapshot = parameters
    directory = ROOT / "control-consumer-cases" / "S09" / case / "input" / "sources"
    with (directory / "shipment_cohorts.csv").open(newline="") as stream:
        cohorts = list(csv.DictReader(stream))
    with (directory / "shift_operations.csv").open(newline="") as stream:
        operations = list(csv.DictReader(stream))
    full_dates = {row["shipment_date"] for row in cohorts if int(row["mature_orders"])}
    ages = {row["shipment_date"]: (date.fromisoformat(snapshot) - date.fromisoformat(row["shipment_date"])).days for row in cohorts}
    assert all((ages[row["shipment_date"]] >= 7) == bool(int(row["mature_orders"])) for row in cohorts)

    rates, hours = {}, {}
    for line in (treated, comparison):
        for period in ("baseline", "pilot"):
            band_rates = {}
            for band in ("standard", "complex"):
                selected = [row for row in cohorts if (row["line"], row["period"], row["order_band"]) == (line, period, band)]
                band_rates[band] = F(sum(int(row["confirmed_mispack_7d"]) for row in selected), sum(int(row["mature_orders"]) for row in selected))
            rates[line, period] = standard_share * band_rates["standard"] + (1 - standard_share) * band_rates["complex"]
            shifts = [row for row in operations if (row["line"], row["period"]) == (line, period) and row["shipment_date"] in full_dates]
            hours[line, period] = sum((F(row["productive_labor_hours"]) - F(row["training_hours"]) for row in shifts), F(0)) / len(shifts)

    pilot_full = [row for row in cohorts if row["line"] == treated and row["period"] == "pilot" and row["shipment_date"] in full_dates]
    observed_per_shift = F(sum(int(row["shipped_orders"]) for row in pilot_full), len({row["shipment_date"] for row in pilot_full}))
    scale = F(planned) / observed_per_shift
    volume = planned * 20
    raw_reduction = rates[treated, "baseline"] - rates[treated, "pilot"]
    adjusted_reduction = raw_reduction - (rates[comparison, "baseline"] - rates[comparison, "pilot"])
    raw_hours_increment = (hours[treated, "pilot"] - hours[treated, "baseline"]) * scale
    adjusted_hours_increment = raw_hours_increment - (hours[comparison, "pilot"] - hours[comparison, "baseline"]) * scale
    full_check_hours = hours[treated, "pilot"] * scale
    adjusted_no_check_hours = full_check_hours - adjusted_hours_increment
    dispatch = {}
    for population in ("full_shifts", "all_pilot"):
        relevant = lambda row: row["line"] == treated and row["period"] == "pilot" and (population == "all_pilot" or row["shipment_date"] in full_dates)
        late = sum(int(row["late_dispatch_orders"]) for row in operations if relevant(row))
        shipped = sum(int(row["shipped_orders"]) for row in cohorts if relevant(row))
        dispatch[population] = {"late": late, "shipped": shipped, "rate": str(F(late, shipped))}
    raw_net = raw_reduction * volume * error_cost - raw_hours_increment * 20 * wage
    adjusted_net = adjusted_reduction * volume * error_cost - adjusted_hours_increment * 20 * wage

    if case == "ordinary":
        assert list(rates.values()) == [F(21, 800), F(1, 80), F(21, 800), F(1, 40)]
        assert (adjusted_reduction, full_check_hours, adjusted_no_check_hours, raw_net, adjusted_net) == (F(1, 80), 65, 62, 8640, 7680)
    else:
        assert list(rates.values()) == [F(4, 125), F(37, 1000), F(13, 500), F(1, 40)]
        assert (adjusted_reduction, full_check_hours, adjusted_no_check_hours, raw_net, adjusted_net) == (F(-3, 500), 108, F(504, 5), -14448, -14400)
        assert dispatch["full_shifts"]["rate"] == "7/600" and dispatch["all_pilot"]["rate"] == "1/100"

    return {
        "source_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(directory.iterdir()) if path.is_file()},
        "parameters_from_packet": {"planned_orders_per_shift": planned, "standard_share": str(standard_share), "cap_hours": cap, "error_cost_usd": error_cost, "wage_usd": wage, "snapshot_date": snapshot},
        "shipment_age_calendar_days_at_snapshot": ages,
        "planned_mix_quality_rates": {f"{line}/{period}": str(value) for (line, period), value in rates.items()},
        "comparison_adjusted_reduction_percentage_points": str(adjusted_reduction * 100),
        "linear_full_check_hours_per_shift": str(full_check_hours),
        "comparison_adjusted_no_check_hours_per_shift": str(adjusted_no_check_hours),
        "comparison_adjusted_no_check_headroom_hours": str(cap - adjusted_no_check_hours),
        "dispatch": dispatch,
        "comparison_adjusted_expected_avoided_errors": str(adjusted_reduction * volume),
        "comparison_adjusted_extra_labor_hours": str(adjusted_hours_increment * 20),
        "raw_net_benefit_usd": str(raw_net),
        "comparison_adjusted_net_benefit_usd": str(adjusted_net),
    }


if __name__ == "__main__":
    report = {"scope": "Independent arithmetic/timing review only; projections are conditional assumptions, not demonstrated effects or capacities.", "cases": {case: review(case, parameters) for case, parameters in PARAMETERS.items()}, "all_assertions_passed": True}
    print(json.dumps(report, indent=2, sort_keys=True))
