# Decision for Nessa Vale

**Stop Alder's all-order second-person packing check for the next twenty full shifts, and do not expand it to Birch.** Operate both lines without this added check for the 20-shift period. This is the only measured version, and it both fails the next-period capacity test under the supplied proportional planning assumption and lacks evidence of a quality benefit. Nessa retains authority to make the operating change.

## Why this is the decision

### Mature downstream quality

The raw totals improved during the pilot, but the mix changed sharply toward standard orders on both lines, so the raw comparison is not decision-safe on its own.

| Period | Line | Confirmed mispacks / mature orders | Raw 7-day rate | Exclusions |
|---|---|---:|---:|---|
| Baseline, Aug 3-5 | Alder | 132 / 3,600 | 3.67% | None; all cohorts mature |
| Pilot, Aug 17-19 | Alder | 63 / 3,600 | 1.75% | Aug 28 excluded as immature |
| Baseline, Aug 3-5 | Birch | 102 / 3,600 | 2.83% | None; all cohorts mature |
| Pilot, Aug 17-19 | Birch | 51 / 3,600 | 1.42% | Aug 28 excluded as immature |

At the planned 70% standard / 30% complex mix, the comparable band-specific rates produce:

| Period | Line | Standard rate | Complex rate | Planned-mix standardized rate |
|---|---|---:|---:|---:|
| Baseline | Alder | 42 / 2,100 = 2.00% | 90 / 1,500 = 6.00% | 3.20% |
| Pilot | Alder | 33 / 3,300 = 1.00% | 30 / 300 = 10.00% | 3.70% |
| Baseline | Birch | 42 / 2,100 = 2.00% | 60 / 1,500 = 4.00% | 2.60% |
| Pilot | Birch | 33 / 3,300 = 1.00% | 18 / 300 = 6.00% | 2.50% |

This **establishes** that Alder's standardized descriptive rate rose 0.50 percentage points, while Birch's fell 0.10 points. The nonrandomized difference-in-differences contrast is therefore **+0.60 percentage points for Alder relative to Birch**, in the unfavorable direction. It only **suggests** that the check did not improve quality: allocation was voluntary, Alder began with worse complex-order performance, the mix shifted, and the common packing-list template changed at the same time. It does not establish a causal effect.

The Aug 28 cohorts shipped 600 orders on each line but had zero mature orders at the snapshot. They are reported separately and excluded from all downstream quality rates; their recorded zeros do not mean zero errors. Station catches are also excluded from downstream quality because catch recording changed on Aug 14 and catches are upstream events.

### Capacity, workload, and dispatch

The next period requires each line to process 28,800 orders: 1,440 orders per shift for 20 shifts, comprising an estimated 20,160 standard and 8,640 complex orders.

| Comparable full shifts | Shipped | Productive hours | Training subset | Ongoing hours/shift | Throughput | Late dispatches / shipped | Late rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| Alder baseline, Aug 3-5 | 3,600 | 246 | 0 | 82.0 | 14.63 orders/hour | 21 / 3,600 | 0.58% |
| Alder pilot, Aug 17-19 | 3,600 | 275 | 5 one-off | 90.0 | 13.33 orders/hour | 42 / 3,600 | 1.17% |
| Birch pilot, Aug 17-19 | 3,600 | 246 | 0 | 82.0 | 14.63 orders/hour | 18 / 3,600 | 0.50% |

Aug 28 is excluded from this operations comparison because it was a short 600-order shift with unusually simple mix. Labor hours are counted once per date and line. Alder's five training hours are included in productive totals and removed only from the ongoing-hours calculation.

The required next-period throughput is **1,440 / 102 = 14.12 orders per hour**. Scaling Alder's observed pilot rate of 1,200 orders in 90 ongoing hours gives **108.0 hours per planned shift**, six hours above the hard cap. This is a sensitivity, not a validated capacity curve; the observed shifts had only 1,200 orders and a much simpler mix than the planned period. It nevertheless cannot support authorizing all-order checking within the cap. The observed pilot dispatch rate also exceeded the commercial limit: 42 / 3,600 = 1.17%, versus no more than 1%. At the same rate, 28,800 orders would yield an estimated 336 late dispatches, above the 288-order maximum. No dollar value is assigned to lateness.

### Planning cost consequences

These are scenarios rather than realized or causal savings:

| Scenario at 28,800 Alder orders | Estimated mispacks | Avoidable downstream cost at $55/order | Interpretation |
|---|---:|---:|---|
| Alder baseline standardized rate, 3.20% | 921.6 | $50,688 | Reference without the observed pilot-period change |
| Alder pilot standardized rate, 3.70% | 1,065.6 | $58,608 | If the pilot-period association repeated at planned mix |
| Difference | 144.0 more | $7,920 more | Association, not attributable errors caused by the check |
| Baseline plus Birch's -0.10-point shared-period change, 3.10% | 892.8 | $49,104 | Noncausal comparison scenario |
| Pilot versus that comparison scenario | 172.8 more | $9,504 more | Difference-in-differences association, not causal attribution |

Using the same proportional labor assumption, baseline Alder scales from 82 hours at 1,200 orders to 98.4 hours at 1,440, while the pilot scales from 90 to 108.0 hours. The implied increment is 9.6 hours per shift, or 192 hours over twenty shifts, costing **$6,528 at $34/hour**. This is a planning sensitivity because labor by order band and checker time were not recorded. Alder's five training hours are a one-off cost already observed; no new training is proposed for the next period.

## Evidence boundary and review

The records establish the descriptive rates, hours, throughput, and dispatch outcomes above. They suggest that stopping the measured check is preferable under the stated constraints. They do not establish why quality or dispatch changed, future performance at 1,440 orders, or whether a selective check would work. Selective checking has no measured time, quality, or dispatch effect, so it cannot be approved as a proven narrower version within the 102-hour cap.

No further evidence is needed to reject all-order checking for this 20-shift period. Keep it stopped throughout the period. Review the decision after all twenty shift cohorts have completed their seven-calendar-day outcome windows, using the same band-level 7-day mispack definition, line-level hours counted once, and late dispatches over shipped orders. Any later proposal to test a selective check must first specify the selected orders, demonstrate a schedule at or below 102 productive hours per shift, and define a near-term maturity review; the current packet does not support activating such a test now.

## Reproduce the arithmetic

The retained output is at `deliverables/reproducible-analysis.md`. From the C-U108 task directory, run:

```bash
python skill/operational-intervention-decision/scripts/analyze_packet.py \
  input/sources/shipment_cohorts.csv \
  input/sources/shift_operations.csv \
  --intervention-line Alder \
  --control-line Birch \
  --baseline-period baseline \
  --trial-period pilot \
  --planned-mix standard=0.7,complex=0.3 \
  --planned-orders-per-shift 1440 \
  --shifts 20 \
  --hour-cap 102 \
  --exclude-operations-date 2026-08-28 \
  --avoidable-cost 55 \
  --hour-cost 34
```

The supplied script phrases negative changes as negative “fewer errors.” For clarity, this recommendation states those results as **144 more** errors in the Alder before/after scenario and **172.8 more** in the difference-in-differences scenario, preserving the script's arithmetic and direction.
