#!/usr/bin/env python3
"""Reproduce Northbank's packet-specific arithmetic using Python's standard library."""
import argparse
import csv
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True, help="Directory containing the two supplied CSV files")
    args = parser.parse_args()
    with (args.sources / "shipment_cohorts.csv").open(newline="") as f:
        cohorts = list(csv.DictReader(f))
    with (args.sources / "shift_operations.csv").open(newline="") as f:
        shifts = list(csv.DictReader(f))
    for rows, keys, counts in [
        (cohorts, ("shipment_date", "line", "order_band"), ("shipped_orders", "mature_orders", "confirmed_mispack_7d", "station_catches")),
        (shifts, ("shipment_date", "line"), ("productive_labor_hours", "overtime_hours", "training_hours", "late_dispatch_orders")),
    ]:
        seen = set()
        for r in rows:
            key = tuple(r[k] for k in keys)
            if key in seen:
                raise ValueError(f"Duplicate key: {key}")
            seen.add(key)
            for c in counts:
                r[c] = int(r[c])
                if r[c] < 0:
                    raise ValueError(f"Negative {c}: {key}")
    for r in cohorts:
        if not r["confirmed_mispack_7d"] <= r["mature_orders"] <= r["shipped_orders"]:
            raise ValueError("Inconsistent outcome counts")
    for r in shifts:
        if max(r["training_hours"], r["overtime_hours"]) > r["productive_labor_hours"]:
            raise ValueError("Labor subset exceeds total")
        matching = [c for c in cohorts if (c["shipment_date"], c["line"]) == (r["shipment_date"], r["line"])]
        if len(matching) != 2 or {c["order_band"] for c in matching} != {"standard", "complex"}:
            raise ValueError("Missing or unexpected order bands")
        if any(c["period"] != r["period"] for c in matching):
            raise ValueError("Period mismatch")
        if r["late_dispatch_orders"] > sum(c["shipped_orders"] for c in matching):
            raise ValueError("Late orders exceed shipments")
    if {(c["shipment_date"], c["line"]) for c in cohorts} != {(r["shipment_date"], r["line"]) for r in shifts}:
        raise ValueError("Unmatched line-date keys")
    result = {"validation": {"cohort_rows": len(cohorts), "shift_rows": len(shifts), "status": "passed"}, "groups": {}}
    # These explicitly selected dates are the packet's comparable full shifts.
    dates = {"baseline": {"2026-06-01", "2026-06-02", "2026-06-03"}, "pilot": {"2026-06-15", "2026-06-16", "2026-06-17"}}
    for period in dates:
        for line in ("East", "West"):
            cs = [c for c in cohorts if c["shipment_date"] in dates[period] and c["line"] == line]
            ss = [s for s in shifts if s["shipment_date"] in dates[period] and s["line"] == line]
            if len(cs) != 6 or len(ss) != 3:
                raise ValueError("Incomplete comparison window")
            total = sum(c["shipped_orders"] for c in cs)
            mature = sum(c["mature_orders"] for c in cs)
            errors = sum(c["confirmed_mispack_7d"] for c in cs)
            bands = {}
            for band in ("standard", "complex"):
                bs = [c for c in cs if c["order_band"] == band]
                n = sum(c["mature_orders"] for c in bs)
                e = sum(c["confirmed_mispack_7d"] for c in bs)
                if n == 0:
                    raise ValueError("No mature orders in stratum")
                bands[band] = {"mature": n, "errors": e, "rate": e / n}
            hours = sum(s["productive_labor_hours"] for s in ss)
            training = sum(s["training_hours"] for s in ss)
            recurring = hours - training
            late = sum(s["late_dispatch_orders"] for s in ss)
            result["groups"][f"{line}_{period}"] = dict(shipped=total, mature=mature, errors=errors, raw_rate=errors / mature,
                complex_share=bands["complex"]["mature"] / mature, bands=bands,
                target_mix_rate=.8 * bands["standard"]["rate"] + .2 * bands["complex"]["rate"],
                hours=hours, training=training, recurring_hours=recurring,
                overtime=sum(s["overtime_hours"] for s in ss), late=late, late_rate=late / total,
                projected_hours_per_1200=recurring / total * 1200, projected_orders_at_84=84 * total / recurring)
    result["latest_shift"] = {}
    for line in ("East", "West"):
        cs = [c for c in cohorts if c["shipment_date"] == "2026-06-26" and c["line"] == line]
        s = next(s for s in shifts if s["shipment_date"] == "2026-06-26" and s["line"] == line)
        result["latest_shift"][line] = dict(shipped=sum(c["shipped_orders"] for c in cs), mature=sum(c["mature_orders"] for c in cs), **{k:s[k] for k in ("productive_labor_hours", "overtime_hours", "late_dispatch_orders")})
    g = result["groups"]
    eb, ep, wb, wp = [g[k] for k in ("East_baseline", "East_pilot", "West_baseline", "West_pilot")]
    drop_e = eb["target_mix_rate"] - ep["target_mix_rate"]
    drop_w = wb["target_mix_rate"] - wp["target_mix_rate"]
    labor_e = (ep["recurring_hours"] - eb["recurring_hours"]) / 3000
    labor_w = (wp["recurring_hours"] - wb["recurring_hours"]) / 3000
    scenarios = [("East_before_after", drop_e, labor_e), ("comparison_adjusted", drop_e - drop_w, labor_e - labor_w),
                 ("contemporaneous_East_vs_West", wp["target_mix_rate"] - ep["target_mix_rate"], (ep["recurring_hours"] - wp["recurring_hours"]) / 3000)]
    result["planning"] = {"orders_per_line": 24000, "mix": {"standard": .8, "complex": .2}, "scenarios": {}}
    for name, reduction, labor in scenarios:
        avoided = 24000 * reduction
        extra_hours = 24000 * labor
        result["planning"]["scenarios"][name] = dict(rate_reduction=reduction, avoided_errors=avoided, benefit_usd=avoided * 65,
            additional_hours=extra_hours, labor_cost_usd=extra_hours * 28, net_usd=avoided * 65 - extra_hours * 28,
            break_even_rate_reduction=extra_hours * 28 / 65 / 24000)
    result["planning"].update(east_required_period_hours=ep["projected_hours_per_1200"] * 20,
        east_hours_above_cap=(ep["projected_hours_per_1200"] - 84) * 20,
        east_orders_at_cap=ep["projected_orders_at_84"] * 20,
        east_expected_mispacks_at_pilot_target_rate=24000 * ep["target_mix_rate"],
        west_expected_mispacks_at_pilot_target_rate=24000 * wp["target_mix_rate"],
        east_late_orders_if_full_shift_rate_persists=24000 * ep["late_rate"],
        west_late_orders_if_full_shift_rate_persists=24000 * wp["late_rate"])
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
