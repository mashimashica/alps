import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "input" / "sources"
FULL_DATES = {
    "2026-07-06", "2026-07-07", "2026-07-08",
    "2026-07-20", "2026-07-21", "2026-07-22",
}

with (SOURCE / "shipment_cohorts.csv").open(newline="") as f:
    cohorts = list(csv.DictReader(f))
with (SOURCE / "shift_operations.csv").open(newline="") as f:
    operations = list(csv.DictReader(f))

cohort_columns = {
    "shipment_date", "period", "line", "order_band", "shipped_orders",
    "mature_orders", "confirmed_mispack_7d", "station_catches",
}
operation_columns = {
    "shipment_date", "period", "line", "productive_labor_hours",
    "overtime_hours", "training_hours", "late_dispatch_orders",
}
assert set(cohorts[0]) == cohort_columns
assert set(operations[0]) == operation_columns

cohort_keys = [(r["shipment_date"], r["line"], r["order_band"]) for r in cohorts]
operation_keys = [(r["shipment_date"], r["line"]) for r in operations]
assert len(cohort_keys) == len(set(cohort_keys))
assert len(operation_keys) == len(set(operation_keys))
assert set(operation_keys) == {(r["shipment_date"], r["line"]) for r in cohorts}

for row in cohorts:
    values = [int(row[c]) for c in ["shipped_orders", "mature_orders", "confirmed_mispack_7d", "station_catches"]]
    assert all(v >= 0 for v in values)
    assert int(row["mature_orders"]) <= int(row["shipped_orders"])
    assert int(row["confirmed_mispack_7d"]) <= int(row["mature_orders"])
for row in operations:
    productive = int(row["productive_labor_hours"])
    overtime = int(row["overtime_hours"])
    training = int(row["training_hours"])
    late = int(row["late_dispatch_orders"])
    assert min(productive, overtime, training, late) >= 0
    assert overtime <= productive and training <= productive

full_cohorts = [r for r in cohorts if r["shipment_date"] in FULL_DATES]
full_ops = [r for r in operations if r["shipment_date"] in FULL_DATES]

outcomes = defaultdict(lambda: [0, 0, 0, 0])
for row in full_cohorts:
    key = (row["period"], row["line"])
    outcomes[key][0] += int(row["shipped_orders"])
    outcomes[key][1] += int(row["mature_orders"])
    outcomes[key][2] += int(row["confirmed_mispack_7d"])
    outcomes[key][3] += int(row["station_catches"])

ops = defaultdict(lambda: [0, 0, 0, 0, 0])
for row in full_ops:
    key = (row["period"], row["line"])
    ops[key][0] += 1
    ops[key][1] += int(row["productive_labor_hours"])
    ops[key][2] += int(row["training_hours"])
    ops[key][3] += int(row["overtime_hours"])
    ops[key][4] += int(row["late_dispatch_orders"])

print(f"VALIDATION PASS: {len(cohorts)} cohort rows; {len(operations)} operation rows; no duplicate keys; all date/line pairs matched; count relationships valid")
for key in [("baseline", "Harbor"), ("pilot", "Harbor"), ("baseline", "Ridge"), ("pilot", "Ridge")]:
    shipped, mature, errors, catches = outcomes[key]
    shifts, productive, training, overtime, late = ops[key]
    print(
        f"{key[0]} {key[1]}: shipped={shipped}, mature={mature}, errors={errors} "
        f"({errors / mature:.3%}), catches={catches} ({catches / shipped:.3%}), "
        f"productive_h={productive}, training_h={training}, ongoing_h_per_shift={(productive-training)/shifts:.2f}, "
        f"overtime_h_per_shift={overtime/shifts:.2f}, late={late} ({late/shipped:.3%})"
    )

short = [r for r in operations if r["shipment_date"] == "2026-07-31"]
for row in short:
    shipped = sum(int(c["shipped_orders"]) for c in cohorts if c["shipment_date"] == row["shipment_date"] and c["line"] == row["line"])
    print(f"short_shift {row['line']}: shipped={shipped}, late={row['late_dispatch_orders']} ({int(row['late_dispatch_orders'])/shipped:.3%}), mature=0")

orders = 20 * 800
did = 0.0125
avoided = orders * did
quality_value = avoided * 48
extra_hours = 20 * 3
labor_cost = extra_hours * 32
print(f"planning: orders={orders}, descriptive_effect={did:.3%}, fewer_mispacks={avoided:.0f}, quality_value=${quality_value:,.0f}, extra_hours={extra_hours}, labor_cost=${labor_cost:,.0f}, net=${quality_value-labor_cost:,.0f}")
print(f"break_even: $96 incremental labor/shift / $48 per mispack = 2 mispacks/shift = {2/800:.3%} rate reduction")
