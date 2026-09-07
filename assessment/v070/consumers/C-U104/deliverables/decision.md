# Fenwick Audio Renewal packing-check decision

## Decision for the next 20 full shifts

**Stop Alder’s second-person all-order packing check for the full 20-shift period. Keep Birch without a checker. Do not expand the check or substitute selective checking.**

This is the only measured checking scope, and it does not fit the hard operating limits at the planned workload. The best comparable full-shift scenario projects **108.0 productive hours per Alder shift**, above the **102-hour cap**, and Alder’s checked full shifts had a **1.167% late-dispatch rate**, above the **1% promise**. The quality evidence also provides no support for continuing: after comparing bands and using Birch to account for shared changes, the estimated quality effect is a **0.6 percentage-point increase in downstream mispacks** at the next-period mix.

Nessa retains the operating decision. This recommendation does not authorize a staffing, spending, or live-process change.

## What the records can answer

The tested intervention was a second-person check of every Alder order beginning August 17; Birch remained without the checker. The decision horizon is 20 full shifts at 1,440 orders per line per shift, with a 70% standard / 30% complex mix. Each line must remain at or below 102 productive hours per shift and 1% late dispatches. Up to five separately funded training hours are available for a newly participating line, but they do not increase the recurring cap.

The quality outcome is customer-confirmed mispacked orders within a complete seven-day window. Rates therefore use mature orders only. August 28’s 600-order cohorts have no mature orders and contribute no quality denominator. Station catches are excluded from the outcome because their recording rule changed on August 14 and they are a different event.

Assignment was voluntary, the packing-list template changed on both lines on August 14, the complex-order mix fell, and Alder began with a worse complex-order rate. The result is an estimate, not proof of causality.

## Mature-order quality cohorts

| Period | Line | Band | Shipped | Mature | Confirmed mispacks | Mature-order rate |
|---|---|---:|---:|---:|---:|---:|
| Baseline | Alder | Standard | 2,100 | 2,100 | 42 | 2.000% |
| Baseline | Alder | Complex | 1,500 | 1,500 | 90 | 6.000% |
| Baseline | Birch | Standard | 2,100 | 2,100 | 42 | 2.000% |
| Baseline | Birch | Complex | 1,500 | 1,500 | 60 | 4.000% |
| Pilot | Alder | Standard | 3,870 | 3,300 | 33 | 1.000% |
| Pilot | Alder | Complex | 330 | 300 | 30 | 10.000% |
| Pilot | Birch | Standard | 3,870 | 3,300 | 33 | 1.000% |
| Pilot | Birch | Complex | 330 | 300 | 18 | 6.000% |

The unadjusted Alder aggregate fell from 3.667% at baseline to 1.750% in the mature pilot. That comparison is not decision-grade because standard orders were 58.3% of Alder’s mature baseline volume and 91.7% of its mature pilot volume. The next period is planned at 70%.

A band-level difference-in-differences estimate gives:

- Standard: `(2% - 1%) - (2% - 1%) = 0` percentage points of incremental reduction.
- Complex: `(6% - 10%) - (4% - 6%) = -2` percentage points of incremental reduction.
- Next-period mix: `70% × 0 + 30% × (-2%) = -0.6` percentage points.

A negative reduction means the checked Alder result is worse than the modeled no-check counterfactual. The complex estimate is unstable because each line has only 300 mature pilot complex orders.

## Operations and comparability

The line-level operations rows are counted once per date and line.

| Period | Line | Shipped | Productive hours | Training hours | Late dispatches | Late rate |
|---|---|---:|---:|---:|---:|---:|
| Baseline | Alder | 3,600 | 246 | 0 | 21 | 0.583% |
| Baseline | Birch | 3,600 | 240 | 0 | 18 | 0.500% |
| Pilot, all recorded shifts | Alder | 4,200 | 311 | 5 | 42 | 1.000% |
| Pilot, all recorded shifts | Birch | 4,200 | 280 | 0 | 18 | 0.429% |

The all-recorded pilot row includes August 28, an unusually simple 600-order partial shift with no late dispatches. It is not evidence of full-shift capacity. On the comparable August 17–19 full shifts, Alder used 275 productive hours, including five one-off training hours; recurring work was therefore 270 hours, or 90 per shift at 1,200 orders. Its 42 late dispatches were **1.167%** of 3,600 orders. Birch used 82 hours per shift and had an unchanged 0.500% late rate.

## Next-period planning scenario

The estimates below are planning scenarios. They assume band rates and hours per order remain constant when volume rises from 1,200 to 1,440 orders per shift. There are no minutes by band and no validated capacity curve.

For quality, the modeled Alder no-check rate preserves the baseline Alder-versus-Birch difference within each band and applies Birch’s pilot rates: 1% standard and 8% complex, or **3.1%** at the planned mix. Alder’s observed checked pilot band rates yield **3.7%** at that mix.

For labor, the difference-in-differences estimate is `(90 - 82) - (82 - 80) = 6` incremental checker hours per 1,200-order shift. The modeled Alder no-check counterfactual is Birch’s pilot 82 hours plus Alder’s two-hour baseline line difference, or 84 hours at 1,200 orders. Scaling by `1,440 / 1,200` gives 100.8 no-check hours and 108 checked hours.

| Scenario for Alder | Quality rate | Mispacked orders over 28,800 | Productive hours/shift | Late-dispatch planning rate | Relevant modeled cost |
|---|---:|---:|---:|---:|---:|
| No checker | 3.100% | 892.8 | 100.8 | 0.583% | $49,104 |
| Check every order | 3.700% | 1,065.6 | 108.0 | 1.167% | $63,504 |
| Check minus no check | +0.600 pp | +172.8 | +7.2 | +0.583 pp | +$14,400 |

The no-check late-rate scenario is Birch’s 0.500% pilot full-shift rate plus Alder’s 0.083 percentage-point baseline line difference. The checked rate is Alder’s observed full-shift pilot rate. At 28,800 orders, those rates correspond to about 168 and 336 late orders respectively; the service ceiling is 288.

Cost uses only the authorized assumptions. The no-check outcome cost is `892.8 × $55 = $49,104`. The checked outcome cost is `1,065.6 × $55 = $58,608`. Estimated incremental checker labor is `7.2 × 20 = 144` hours, costing `144 × $34 = $4,896`. Thus checked relevant cost is $63,504, or $14,400 more than modeled no-check. No dollar value is assigned to missed carrier cutoffs.

Even if the quality estimate later moves, all-order checking remains infeasible on the current capacity scenario: 108 hours exceeds the hard cap by six hours per shift. The five training hours are one-off and separately funded; removing them does not close that recurring gap. Selective checking cannot be used as a workaround because its time, quality effect, and dispatch effect were not measured.

## Bounded follow-up

The current-period decision remains **no checker on either line for all 20 shifts**, using the existing line crews and staying within 102 productive hours per line per shift.

For a future decision, preserve the common packing template and collect the same line/date operations and line/band mature-outcome fields for shifts 1–10 at the planned 70/30 mix. Review **seven calendar days after shift 10**, when those cohorts are mature. The source packet does not supply operating dates, so that is the most specific valid review point rather than an invented calendar date.

The review question is: **Without a checker, does Alder sustain no more than 102 productive hours per shift and 1% late dispatches, and does its band-specific post-template quality gap versus Birch persist at the planned mix?** This follow-up can establish a stable counterfactual for a future controlled test. It cannot justify adding a checker during the current 20 shifts, and any later test must first demonstrate a staffing plan within the same cap.

## Reproduce the arithmetic

From this task directory, run:

```bash
python3 deliverables/reproduce_decision.py
```

The script validates required files and columns, rejects invalid counts, uses mature-only quality denominators, aggregates operations once per date and line, excludes the short August 28 shift from full-shift comparisons, and prints the formulas and assumptions. Captured output is in `deliverables/calculation_output.txt`.

## Limitations

- Voluntary assignment and concurrent template and recording changes prevent a causal claim.
- The future mix differs materially from the mature pilot, and the complex pilot cells are small.
- Hours-per-order scaling is a planning assumption; mix-specific staffing cannot be recovered.
- The packet contains only three comparable pilot full shifts and no measured selective-check variant.
- August 28 remains immature for quality and cannot establish zero errors.
