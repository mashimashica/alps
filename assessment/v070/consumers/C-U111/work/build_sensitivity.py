import csv
import json
from pathlib import Path


basis_path = Path("deliverables/numerical_basis.json")
output_path = Path("deliverables/economic_sensitivity.csv")
basis = json.loads(basis_path.read_text())

orders = basis["planning"]["total_orders"]
shifts = basis["planning"]["planned_shifts"]
outcome_cost = basis["planning"]["error_cost_per_outcome"]
hour_cost = basis["planning"]["hour_cost"]
effects = {
    "difference_in_differences_lower_95": basis["outcome_effects"]["difference_in_differences_benefit"]["lower"],
    "contemporaneous_lower_95": basis["outcome_effects"]["contemporaneous_benefit"]["lower"],
    "observed_point_estimate": basis["outcome_effects"]["contemporaneous_benefit"]["estimate"],
}

with output_path.open("w", newline="") as handle:
    writer = csv.DictWriter(
        handle,
        fieldnames=[
            "effect_scenario",
            "benefit_per_order",
            "incremental_hours_per_shift",
            "avoided_outcomes",
            "quality_value_usd",
            "labor_cost_usd",
            "net_value_usd",
            "break_even_benefit_per_order",
        ],
    )
    writer.writeheader()
    for effect_name, effect in effects.items():
        for hours_per_shift in (3.0, 6.0):
            avoided = orders * effect
            quality_value = avoided * outcome_cost
            labor_cost = shifts * hours_per_shift * hour_cost
            writer.writerow(
                {
                    "effect_scenario": effect_name,
                    "benefit_per_order": round(effect, 8),
                    "incremental_hours_per_shift": hours_per_shift,
                    "avoided_outcomes": round(avoided, 2),
                    "quality_value_usd": round(quality_value, 2),
                    "labor_cost_usd": round(labor_cost, 2),
                    "net_value_usd": round(quality_value - labor_cost, 2),
                    "break_even_benefit_per_order": round(labor_cost / (orders * outcome_cost), 8),
                }
            )

print(f"wrote {output_path}")
