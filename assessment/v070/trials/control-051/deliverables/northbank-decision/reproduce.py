#!/usr/bin/env python3
"""Reproduce the Northbank decision arithmetic using only the supplied CSVs."""
import argparse
import csv
from pathlib import Path


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def n(rows, field):
    return sum(int(r[field]) for r in rows)


def fmt_rate(x):
    return f"{100*x:.3f}%"


def main():
    here = Path(__file__).resolve()
    default_sources = here.parents[2] / "input" / "sources"
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--shipment", type=Path,
                    default=default_sources / "shipment_cohorts.csv")
    ap.add_argument("--operations", type=Path,
                    default=default_sources / "shift_operations.csv")
    args = ap.parse_args()
    shipments = read_csv(args.shipment)
    operations = read_csv(args.operations)

    # Mature quality: baseline and the three ordinary, mature pilot dates.
    def mature(period, line):
        return [r for r in shipments if r["period"] == period and r["line"] == line
                and int(r["mature_orders"]) > 0]

    print("MATURE QUALITY")
    rates = {}
    for period in ("baseline", "pilot"):
        for line in ("East", "West"):
            rows = mature(period, line)
            orders, errors = n(rows, "mature_orders"), n(rows, "confirmed_mispack_7d")
            rates[(period, line)] = errors / orders
            print(f"{period:8} {line:5} orders={orders:4} errors={errors:3} rate={fmt_rate(rates[(period,line)])}")
            for band in ("standard", "complex"):
                band_rows = [r for r in rows if r["order_band"] == band]
                bo, be = n(band_rows, "mature_orders"), n(band_rows, "confirmed_mispack_7d")
                print(f"  {band:8} orders={bo:4} errors={be:3} rate={fmt_rate(be/bo)}")

    # Ordinary full-shift operations are June 1-3 and June 15-17.
    print("\nORDINARY FULL-SHIFT OPERATIONS")
    for period in ("baseline", "pilot"):
        dates = {"baseline": {"2026-06-01", "2026-06-02", "2026-06-03"},
                 "pilot": {"2026-06-15", "2026-06-16", "2026-06-17"}}[period]
        for line in ("East", "West"):
            rows = [r for r in operations if r["period"] == period and r["line"] == line
                    and r["shipment_date"] in dates]
            hours = sum(float(r["productive_labor_hours"]) for r in rows)
            late = n(rows, "late_dispatch_orders")
            print(f"{period:8} {line:5} hours={hours:.1f} late={late:2} "
                  f"late_rate={fmt_rate(late/(1000*len(rows)))}")

    print("\nPLANNED-MIX QUALITY SCENARIO")
    # 80% standard / 20% complex, using mature within-band rates.
    band = {}
    for period in ("baseline", "pilot"):
        for line in ("East", "West"):
            rows = mature(period, line)
            band[(period, line)] = {}
            for b in ("standard", "complex"):
                br = [r for r in rows if r["order_band"] == b]
                band[(period, line)][b] = n(br, "confirmed_mispack_7d") / n(br, "mature_orders")
    for period, line in (("baseline", "East"), ("pilot", "East"),
                         ("baseline", "West"), ("pilot", "West")):
        s = band[(period, line)]
        print(f"{period:8} {line:5} standardized_rate={fmt_rate(.8*s['standard']+.2*s['complex'])}")
    east_change = (.8*band[("pilot", "East")]["standard"] + .2*band[("pilot", "East")]["complex"]) - (.8*band[("baseline", "East")]["standard"] + .2*band[("baseline", "East")]["complex"])
    west_change = (.8*band[("pilot", "West")]["standard"] + .2*band[("pilot", "West")]["complex"]) - (.8*band[("baseline", "West")]["standard"] + .2*band[("baseline", "West")]["complex"])
    did = east_change - west_change
    orders = 20 * 1200
    avoided = orders * (-did)
    quality_cost = avoided * 65
    labor_cost = (78 - 69) * 20 * 28
    print(f"East change={fmt_rate(east_change)} West change={fmt_rate(west_change)} "
          f"incremental contrast={fmt_rate(did)}")
    print(f"planned_orders={orders} scenario_avoided_orders={avoided:.1f} "
          f"quality_cost_at_$65=${quality_cost:,.2f} added_labor_cost_at_$28=${labor_cost:,.2f}")
    print(f"pilot_East_routine_hours_per_1000=78.0; linear_1200_order_scenario={78*1.2:.1f} "
          f"vs_limit=84.0")


if __name__ == "__main__":
    main()
