"""Independent, standard-library arithmetic for the two synthetic S09 fixtures.

Run from any directory. This is author evidence, not a consumer test or required
analysis method. It reads only the two control input directories.
"""

import csv
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CASES = {
    "ordinary": ("Harbor", "Ridge", 800, F(3, 4), 68, 48, 32),
    "challenging": ("Alder", "Birch", 1440, F(7, 10), 102, 55, 34),
}


def rows(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def pct(value):
    return f"{float(value * 100):.6f}%"


def num(value):
    return f"{float(value):.6f}"


def check_case(name, parameters):
    treated, comparator, planned_daily, standard_share, cap, error_cost, wage = parameters
    source = ROOT / "control-consumer-cases" / "S09" / name / "input" / "sources"
    cohorts = rows(source / "shipment_cohorts.csv")
    operations = rows(source / "shift_operations.csv")
    seen = set()
    daily = defaultdict(lambda: [0, 0, 0])
    quality = defaultdict(lambda: [0, 0])
    for row in cohorts:
        key = (row["shipment_date"], row["line"], row["order_band"])
        assert key not in seen
        seen.add(key)
        shipped, mature, errors, catches = (
            int(row[column]) for column in (
                "shipped_orders", "mature_orders", "confirmed_mispack_7d", "station_catches"
            )
        )
        assert 0 <= errors <= mature <= shipped and catches >= 0
        assert mature in (0, shipped)
        if mature == 0:
            assert errors == 0
        day_key = (row["shipment_date"], row["line"], row["period"])
        for index, value in enumerate((shipped, mature, errors)):
            daily[day_key][index] += value
        for band in (row["order_band"], "all"):
            quality_key = (row["line"], row["period"], band)
            quality[quality_key][0] += mature
            quality[quality_key][1] += errors

    seen_ops = set()
    full_ops = defaultdict(lambda: [F(0)] * 7)
    all_pilot = defaultdict(lambda: [0, 0])
    for row in operations:
        key = (row["shipment_date"], row["line"], row["period"])
        assert key in daily and key not in seen_ops
        seen_ops.add(key)
        shipped, mature, _ = daily[key]
        hours, overtime, training, late = (
            F(row[column]) for column in (
                "productive_labor_hours", "overtime_hours", "training_hours", "late_dispatch_orders"
            )
        )
        assert 0 <= overtime <= hours and 0 <= training <= hours and 0 <= late <= shipped
        if row["period"] == "pilot":
            all_pilot[row["line"]][0] += shipped
            all_pilot[row["line"]][1] += late
        # Notes identify all fully mature dates as full shifts in these fixtures.
        if mature == shipped:
            values = (1, shipped, hours, training, overtime, late, hours - training)
            destination = full_ops[row["line"], row["period"]]
            for index, value in enumerate(values):
                destination[index] += value
    assert seen_ops == set(daily)

    print(f"CASE {name}")
    weighted = {}
    recurring = {}
    daily_volume = {}
    for line in (treated, comparator):
        for period in ("baseline", "pilot"):
            for band in ("standard", "complex", "all"):
                mature, errors = quality[line, period, band]
                print(f"quality {line} {period} {band}: {errors}/{mature} = {pct(F(errors, mature))}")
            std_n, std_e = quality[line, period, "standard"]
            cmp_n, cmp_e = quality[line, period, "complex"]
            weighted[line, period] = standard_share * F(std_e, std_n) + (1 - standard_share) * F(cmp_e, cmp_n)
            print(f"planned-mix quality {line} {period}: {pct(weighted[line, period])}")
            shifts, shipped, hours, training, overtime, late, routine = full_ops[line, period]
            assert shifts == 3
            recurring[line, period] = routine / shifts
            daily_volume[line, period] = shipped / shifts
            print(f"full operations {line} {period}: orders={num(shipped)} paid_hours={num(hours)} training={num(training)} overtime_subset={num(overtime)} recurring_per_shift={num(routine / shifts)} late={num(late)}/{num(shipped)}={pct(late / shipped)}")
        shipped, late = all_pilot[line]
        print(f"all-pilot dispatch {line}: {num(late)}/{shipped} = {pct(F(late, shipped))}")

    volume = planned_daily * 20
    raw_reduction = weighted[treated, "baseline"] - weighted[treated, "pilot"]
    comparator_reduction = weighted[comparator, "baseline"] - weighted[comparator, "pilot"]
    adjusted_reduction = raw_reduction - comparator_reduction
    scale = F(planned_daily) / daily_volume[treated, "pilot"]
    raw_extra_daily = (recurring[treated, "pilot"] - recurring[treated, "baseline"]) * scale
    comparator_extra_daily = (recurring[comparator, "pilot"] - recurring[comparator, "baseline"]) * scale
    adjusted_extra_daily = raw_extra_daily - comparator_extra_daily
    full_check_hours = recurring[treated, "pilot"] * scale
    adjusted_no_check_hours = full_check_hours - adjusted_extra_daily
    print(f"planning orders per line: {volume}; hours cap: {cap}")
    print(f"linear scenario treated full-check hours/shift: {num(full_check_hours)}; comparison-adjusted no-check: {num(adjusted_no_check_hours)}")
    for label, reduction, extra_daily in (
        ("raw treated change", raw_reduction, raw_extra_daily),
        ("comparison-adjusted change", adjusted_reduction, adjusted_extra_daily),
    ):
        avoided = reduction * volume
        labor_hours = extra_daily * 20
        gross = avoided * error_cost
        labor_cost = labor_hours * wage
        print(f"{label}: quality_reduction={pct(reduction)} expected_avoided_errors={num(avoided)} extra_labor_hours={num(labor_hours)} gross_avoidable_cost={num(gross)} additional_labor_cost={num(labor_cost)} net_benefit={num(gross - labor_cost)}")
    print()


if __name__ == "__main__":
    for case_name, case_parameters in CASES.items():
        check_case(case_name, case_parameters)
