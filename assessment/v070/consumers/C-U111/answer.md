# Cedar Quay packing-check decision

**Recommendation to Iona Bell:** continue Harbor's second-person check on **every order** for the next twenty full shifts, subject to the labor and dispatch gates below. Keep Ridge on its usual process. Do not narrow Harbor's scope, expand to Ridge, or stop the Harbor check now. This is a recommendation only; Iona retains the operating decision.

## Proposed operating instruction

- Harbor checks all 800 orders on each of 20 full shifts: 16,000 orders total, planned as 12,000 standard and 4,000 complex.
- Plan Harbor at the observed 65 recurring productive hours per shift and never exceed the hard 68-hour cap. The three July 20 introductory training hours were one-off and are excluded from the recurring projection.
- Ridge continues its usual process. A Ridge expansion is not yet operationally established: Ridge checking was not observed, no extra station or borrowed staff is available, and transferring Harbor's measured three-hour increment is only an assumption.
- Track Harbor's productive hours and late dispatches at every shift boundary. A shift must not be staffed above 68 productive hours. If Harbor's cumulative late-dispatch rate exceeds 1%, Iona should review before the next shift and pause the check unless she has a feasible plan within the same labor and station limits that protects the period commitment.

## Decisive evidence

The next-period mix is the same 75% standard / 25% complex mix seen in the mature full-shift cohorts, so the raw and mix-standardized rates are identical.

| Period and line | Confirmed 7-day mispacks / mature orders | Raw and planned-mix rate | Recurring productive hours / full shift | Late dispatches / shipped orders | Late-dispatch rate |
|---|---:|---:|---:|---:|---:|
| Baseline Harbor | 63 / 2,400 | 2.625% | 62.0 h | 14 / 2,400 | 0.583% |
| Pilot Harbor, all-order check | 30 / 2,400 | 1.250% | 65.0 h | 13 / 2,400 | 0.542% |
| Baseline Ridge | 63 / 2,400 | 2.625% | 62.0 h | 14 / 2,400 | 0.583% |
| Pilot Ridge, usual process | 60 / 2,400 | 2.500% | 62.0 h | 13 / 2,400 | 0.542% |

Harbor improved by 1.375 percentage points while Ridge improved by 0.125 points. The resulting descriptive difference-in-differences benefit is **1.25 percentage points**; the contemporaneous pilot gap is also **1.25 points**. Approximate 95% sampling intervals are 0.072 to 2.428 points for the difference-in-differences estimate and 0.488 to 2.012 points for the contemporaneous estimate. These intervals cover sampling variation only.

Both order bands moved in the favorable direction at Harbor:

| Band | Harbor baseline | Harbor pilot | Ridge pilot | Pilot Harbor advantage vs Ridge |
|---|---:|---:|---:|---:|
| Standard | 27 / 1,800 = 1.500% | 12 / 1,800 = 0.667% | 27 / 1,800 = 1.500% | 0.833 points |
| Complex | 36 / 600 = 6.000% | 18 / 600 = 3.000% | 33 / 600 = 5.500% | 2.500 points |

Harbor's station catches rose from 13 / 2,400 baseline shipments to 38 / 2,400 pilot shipments, while Ridge moved from 12 to 14. Because catch recording was unchanged, this supports the proposed mechanism. Catches are upstream process observations and are not added to downstream mispacks.

The July 31 cohorts contain 640 shipped orders across both lines but zero mature orders. They are excluded from all seven-day outcome rates because their windows were still open. July 31 was also a deliberately short shift and is excluded from full-shift labor projections; its dispatch result remains observable (Harbor 2 / 320, or 0.625%).

## Capacity, dispatch, and authorized cost

Harbor's pilot full shifts averaged 66 total productive hours, including the one-off average of one training hour per shift. Removing the authorized three-hour introductory training block gives **65 recurring hours**, three hours below the cap and three hours above Harbor's baseline. At the observed 0.542% dispatch rate, 16,000 planned Harbor orders imply about 87 late orders, versus the commercial maximum of 160. This is a projection, and missed cutoffs have no authorized dollar value.

Using the descriptive 1.25-point benefit for planning:

- Expected avoided mispacks: 16,000 × 1.25% = **200**.
- Expected quality value: 200 × $48 = **$9,600**.
- Incremental labor: 3 hours × 20 shifts = **60 hours**.
- Incremental labor cost: 60 × $32 = **$1,920**.
- Point-estimate net value: **$7,680**.

At three incremental hours per shift, the quality benefit breaks even at **0.25 percentage points**, or 40 avoided mispacks. Applying the lower contemporaneous sampling bound gives about 78 avoided mispacks and **+$1,824** net. Applying the lower difference-in-differences bound gives about 12 avoided mispacks and **−$1,366** net. If recurring labor rises to the six-hour maximum that reaches the 68-hour cap, the point-estimate net remains **+$5,760**, but the lower contemporaneous case becomes approximately **−$96**. The recommendation therefore depends on the favorable effect repeating and labor remaining close to the observed 65 hours.

## What the packet establishes, suggests, and cannot establish

**Establishes:** the mature counts and rates above; a descriptive 1.25-point pilot gap; observed 65-hour recurring Harbor workload; three hours of cap headroom; and observed Harbor dispatch below 1% on the ordinary pilot shifts.

**Suggests:** the check likely contributed to fewer downstream mispacks, supported by the contemporaneous Ridge contrast, the before/after contrast, and increased Harbor catches. The 200 avoided mispacks and $7,680 net value are planning estimates, not realized savings.

**Cannot establish:** a causal checker effect, because Harbor volunteered and assignment was not randomized; performance over the next twenty shifts; the capacity or savings of a selective check; or a feasible Ridge rollout. The approximate intervals do not cover confounding, dependence, or extrapolation.

## Bounded follow-up and gates

Use the first ten recommended shifts as a defined evidence block while the all-order Harbor check continues. That block is 8,000 Harbor orders under ordinary 800-order shifts and the planned 75% / 25% mix, with at most 68 productive hours per shift. Ridge remains the contemporaneous usual-process comparison.

Review operations after every shift. Review mature quality **seven calendar days after the shipment date of shift 10**, when its full customer window has elapsed; a calendar date cannot be named because the next-period shift dates were not supplied. Recalculate the planned-mix contemporaneous and difference-in-differences benefits and measured incremental recurring hours.

The break-even benefit at review is:

`incremental hours per shift × $32 ÷ (800 orders × $48)`.

- If labor exceeds 68 hours or cumulative late dispatch exceeds 1%, Iona pauses the check before the next shift unless she approves a compliant recovery plan.
- If both quality-effect estimates meet or exceed the break-even benefit, labor remains within 68 hours, and dispatch remains at or below 1%, continue the all-order check through shift 20.
- If both estimates are below break-even, stop after shift 10 and return Harbor to its usual process for shifts 11–20.
- If the two estimates straddle break-even while operating constraints hold, continue Harbor through shift 20, keep Ridge unchanged, and make the next-horizon decision after all 20 cohorts mature. Do not substitute an unmeasured selective version.

## Reproduction

Run from the `C-U111` directory:

```bash
python3 skill/operational-intervention-decision/scripts/analyze_packet.py \
  --cohorts input/sources/shipment_cohorts.csv \
  --operations input/sources/shift_operations.csv \
  --intervention-line Harbor \
  --comparison-line Ridge \
  --baseline-period baseline \
  --intervention-period pilot \
  --planned-mix standard=0.75,complex=0.25 \
  --ordinary-dates 2026-07-06,2026-07-07,2026-07-08,2026-07-20,2026-07-21,2026-07-22 \
  --planned-shifts 20 \
  --orders-per-shift 800 \
  --labor-cap-hours 68 \
  --error-cost 48 \
  --hour-cost 32 \
  --output deliverables/numerical_basis.json
```

The inspectable outputs are `deliverables/numerical_basis.json` and `deliverables/economic_sensitivity.csv`. The latter is regenerated with `python3 work/build_sensitivity.py`.
