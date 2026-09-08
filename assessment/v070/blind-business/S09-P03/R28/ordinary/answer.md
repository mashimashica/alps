# Cedar Quay packing-check decision

## Decision

**Continue the tested scope: check every Harbor order for the next twenty full shifts. Keep Ridge on its usual process for this period; do not expand or narrow the check yet.**

This is the only scope directly supported by the packet. At the planned 800 orders per shift and 75% standard / 25% complex mix, Harbor's mature downstream mispack rate improved enough to cover the observed recurring labor increase. Its pilot full shifts used 65 recurring productive hours per shift, below the 68-hour ceiling, and its observed late-dispatch rate stayed below the 1% promise. A complex-only check has not been measured, and checked operations have not been measured on Ridge, so neither selective-check savings nor Ridge capacity should be claimed now.

Iona retains the operating decision. This analysis does not change staffing, spending, or live operations.

## Comparable quality evidence

Rates below use only mature orders. Pilot shipped counts include the immature July 31 cohorts, but those cohorts contribute zero to both the mature denominator and confirmed outcome numerator.

| Period | Line | Band | Shipped | Mature | Confirmed mispacks | Mature-order rate |
|---|---|---:|---:|---:|---:|---:|
| Baseline | Harbor | Standard | 1,800 | 1,800 | 27 | 1.500% |
| Baseline | Harbor | Complex | 600 | 600 | 36 | 6.000% |
| Pilot | Harbor | Standard | 2,040 | 1,800 | 12 | 0.667% |
| Pilot | Harbor | Complex | 680 | 600 | 18 | 3.000% |
| Baseline | Ridge | Standard | 1,800 | 1,800 | 27 | 1.500% |
| Baseline | Ridge | Complex | 600 | 600 | 36 | 6.000% |
| Pilot | Ridge | Standard | 2,040 | 1,800 | 27 | 1.500% |
| Pilot | Ridge | Complex | 680 | 600 | 33 | 5.500% |

The next-period mix matches the observed full-shift mix, but the band calculation makes the comparison explicit:

- Standard incremental reduction: `(1.500% - 0.667%) - (1.500% - 1.500%) = 0.833 percentage points`.
- Complex incremental reduction: `(6.000% - 3.000%) - (6.000% - 5.500%) = 2.500 percentage points`.
- Next-mix estimate: `75% × 0.833 pp + 25% × 2.500 pp = 1.250 percentage points`.

This difference-in-differences estimate is consistent with a checker benefit, but it is not proof of causality. Harbor volunteered, assignment was not randomized, and only three Harbor pilot full shifts have mature outcomes. The unchanged definitions, crews, workload mix, reporting, and other operating conditions make the comparison useful, while the short follow-up and small complex cells leave it unstable.

Station catches support the process story but are not downstream errors and were not added to them. Across the three comparable full shifts, Harbor catches rose from 13 at baseline to 38 in the pilot; Ridge moved from 12 to 14.

## Workload, hours, and dispatch

Operations are aggregated once per date and line. July 31 is reported separately because it was a deliberately short 320-order shift and is not a full-shift capacity test.

| Period | Line | Full shifts | Orders | Productive hours | Training hours | Recurring hours/shift | Overtime hours | Late orders | Late rate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | Harbor | 3 | 2,400 | 186 | 0 | 62.0 | 6 | 14 | 0.583% |
| Pilot | Harbor | 3 | 2,400 | 198 | 3 | 65.0 | 15 | 13 | 0.542% |
| Baseline | Ridge | 3 | 2,400 | 186 | 0 | 62.0 | 6 | 14 | 0.583% |
| Pilot | Ridge | 3 | 2,400 | 186 | 0 | 62.0 | 6 | 13 | 0.542% |

Harbor's three July 20 training hours are one-off and are removed from recurring hours. The planning basis is therefore 65 recurring productive hours per checked Harbor full shift, leaving 3 hours under the 68-hour limit. Overtime is already a subset of productive hours; Harbor overtime rose from 2 to 5 hours per full shift on average, so staffing resilience should remain part of the review even though total hours met the ceiling.

On July 31, Harbor dispatched 2 of 320 orders late (0.625%) using 27 productive hours, and Ridge dispatched 1 of 320 late (0.313%) using 26 hours. These immediate observations are below 1%, but the shift does not establish full-shift capacity.

If the mature-pilot full-shift dispatch rate of 13/2,400 repeated, each line would have about 87 late orders over 16,000 planned orders, below the 160-order equivalent of the 1% commitment. That is a planning estimate, not a guarantee, and no dollar value is assigned to late dispatches.

## Twenty-shift cost projection for Harbor

The planned Harbor workload is `20 × 800 = 16,000` orders. Applying the 1.250-point mix-weighted incremental reduction gives:

- Expected avoidable downstream mispacks: `16,000 × 0.01250 = 200`.
- Expected gross avoided error cost: `200 × $48 = $9,600`.
- Expected incremental recurring labor: `20 × (65 - 62) = 60 hours`.
- Expected incremental labor cost: `60 × $32 = $1,920`.
- **Expected net cost reduction: `$9,600 - $1,920 = $7,680`**, or $384 per full shift.

At three extra hours per shift, the labor-cost break-even quality reduction is `($96 / (800 × $48)) = 0.250 percentage points`, compared with the estimated 1.250 points. The $7,680 is an expected net cost reduction under the packet's assumptions, not realized savings. It excludes any unpriced service consequence and makes no savings or capacity claim for Ridge or a selective check.

## Bounded follow-up and operating guardrails

During the follow-up, keep the current-period decision unchanged: Harbor checks every order with no more than 68 productive hours per full shift, and Ridge remains the comparison line under its usual process. Continue recording date/line/band shipment cohorts, seven-day mature outcomes and catches, plus one line-level labor and dispatch row per shift.

Review after the first ten Harbor shifts in this period have each completed their seven-calendar-day outcome window; the packet does not provide a period start date, so that is the earliest precise review point available. Ask whether the mix-weighted Harbor-versus-Ridge incremental reduction remains above the 0.250-point labor-cost break-even level while Harbor stays at or below 68 productive hours per full shift and at or below 1% late dispatches. Report standard and complex cells separately and include all ten mature cohorts.

If either hard operating limit is breached, Iona should reassess the all-order check immediately and narrow or stop it as needed to restore the limit; the packet cannot identify which alternative would preserve quality because selective checking has not been tested. If the ten-shift evidence remains favorable, it supports continuing Harbor and designing a separately bounded Ridge trial that measures Ridge's own checked labor and dispatch before any full expansion.

## Reproduction

Run from the trial directory:

```bash
python3 deliverables/reproduce_decision.py
```

The script validates required files, columns, and numeric values; exposes mature-only denominators; aggregates line operations once; separates the partial shift and one-off training; and prints the formulas used above. Its captured output is in `deliverables/calculation-output.txt`.
