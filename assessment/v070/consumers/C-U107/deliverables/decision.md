# Cedar Quay packing-check decision

## Recommendation: expand conditionally as a measured 20-shift rollout

Iona should **continue Harbor's all-order second-person check for the next twenty full shifts and propose the same all-order check for Ridge as a bounded evidence rollout**. Ridge should start only if its roster can support 800 orders within the 68-productive-hour cap, without another station or borrowed staff. Until that gate is met, Harbor continues and Ridge uses its usual process.

This is a recommendation, not authorization to launch Ridge. Harbor's observed result supports continuation; the Ridge extension remains an unmeasured planning assumption.

## Evidence driving the choice

All downstream rates below use complete seven-calendar-day cohorts. The July 31 cohorts shipped 320 orders per line but had **0 mature orders**, so their downstream outcomes are unavailable and excluded rather than treated as zero. The observed full shifts and the planned mix are both 75% standard / 25% complex, so the raw and planned-mix-standardized aggregate rates are the same.

| Period and line | Confirmed mispacks / mature orders | Raw and standardized rate | Exclusion |
|---|---:|---:|---|
| Baseline Harbor, July 6–8 | 63 / 2,400 | 2.625% | None |
| Pilot Harbor, July 20–22 | 30 / 2,400 | 1.250% | July 31: 320 shipped, immature |
| Baseline Ridge, July 6–8 | 63 / 2,400 | 2.625% | None |
| Pilot Ridge, July 20–22 | 60 / 2,400 | 2.500% | July 31: 320 shipped, immature |

Harbor improved by **1.375 percentage points** while Ridge improved by **0.125 points**, yielding a **1.25-point difference-in-differences contrast**. By band, Harbor moved from 27/1,800 (1.50%) to 12/1,800 (0.67%) for standard orders and from 36/600 (6.00%) to 18/600 (3.00%) for complex orders. This establishes the observed rates and changes. It **suggests**, but does not establish, that the check caused the improvement: Harbor volunteered, assignment was not randomized, and only three comparable pilot shifts were observed.

Station catches are separate upstream process observations and are not added to customer mispacks. On the comparable full shifts, Harbor catches increased from 13/2,400 shipped orders (0.54%) to 38/2,400 (1.58%); Ridge moved from 12/2,400 (0.50%) to 14/2,400 (0.58%). Harbor also logged 5 catches among 320 July 31 shipments. This pattern is consistent with interception before dispatch, but it is not a count of errors prevented.

## Feasibility, dispatch, and workload

The next period is **20 full shifts × 800 orders = 16,000 orders per line**, or 32,000 sitewide, at the observed 75/25 mix.

| Full-shift measure | Harbor baseline | Harbor pilot | Ridge pilot | Limit or requirement |
|---|---:|---:|---:|---:|
| Productive hours | 186/3 = 62.0/shift | 198 total less 3 one-off training = 195/3 = 65.0 ongoing/shift | 186/3 = 62.0/shift | ≤68/line/shift |
| Overtime subset | 6/3 = 2.0/shift | 15/3 = 5.0/shift | 6/3 = 2.0/shift | No separate cap stated |
| Throughput on ongoing hours | 2,400/186 = 12.90 orders/hour | 2,400/195 = 12.31 orders/hour | 2,400/186 = 12.90 orders/hour | 800/68 = 11.76 orders/hour |
| Late dispatch | 14/2,400 = 0.58% | 13/2,400 = 0.54% | 13/2,400 = 0.54% | ≤1% per line over period |

Harbor therefore had three hours of headroom per comparable pilot shift and met the dispatch commitment descriptively. Its rise from 2 to 5 overtime hours per shift should be watched even though overtime is already included in productive hours. The July 31 320-order shifts are excluded from capacity comparisons because they were deliberately short, but their immediately observable dispatch results remain 2/320 late at Harbor and 1/320 at Ridge.

Using 65 hours for Ridge is only an analogy to Harbor's observed all-order process. It is not a Ridge capacity forecast. Ridge must have its own shift plan within 68 hours before the rollout starts. Up to three one-off training hours may be scheduled before the period with separate funding and do not enlarge the recurring cap.

## Cost scenarios

For Harbor's 16,000 planned orders, applying its own 1.375-point before/after change gives an estimate of **220 fewer downstream mispacks × $48 = $10,560 gross avoidable cost**. Using the more conservative 1.25-point difference-in-differences contrast gives **200 × $48 = $9,600 gross**. Neither is realized savings or a causal estimate.

If Harbor's observed ongoing labor difference persists, 3 additional hours/shift × 20 shifts × $32 = **$1,920 recurring incremental labor**, producing a planning net of **$7,680 to $8,640**. Harbor's three introductory training hours are already incurred and are not a next-period cost.

For Ridge, a same-effect and same-labor scenario would also be $9,600 gross less $1,920 recurring labor = **$7,680**, with up to **$96** of separately funded one-off training, for $7,584 after that training. Every part of the Ridge quality and labor scenario is extrapolated from Harbor and must be replaced with Ridge's actual hours and mature outcomes. Missed cutoffs are not monetized because no authorized value exists.

## Rollout and decision rules

1. **Before Ridge starts:** document a full-shift staffing plan at 800 orders and no more than 68 productive hours, plus no more than three separately funded pre-period training hours. If that cannot be done, do not start Ridge; continue Harbor and leave Ridge on its usual process.
2. **After five full rollout shifts:** review each line's actual productive hours, overtime, shipped volume, catches, and cumulative late-dispatch rate. Continue only while every shift remains at or below 68 hours and the cumulative late rate is at or below 1%. If either hard limit is breached, suspend the affected line's check for the next shift, revert that line to its usual process, and bring the exception to Iona before resuming.
3. **Seven calendar days after the fifth shift:** review the first five mature cohorts by line and order band. Use confirmed mispacks/mature orders and a 75/25 standardized rate; keep catches separate. An adverse or flat early quality result triggers review, but the small early sample alone should not be labeled causal.
4. **Seven calendar days after the twentieth shift:** make the retention decision using all mature cohorts. Report raw and standardized rates, actual incremental hours and cost, and dispatch. Retain a line's all-order check only if it stayed within both hard operating limits and the observed quality-cost comparison is favorable: estimated gross avoidable cost at $48 per downstream mispack exceeds actual incremental labor at $32 per hour. Otherwise stop that line's all-order check. Do not move to a selective version without measuring that version under its own scope and staffing plan.

The reproducible arithmetic is retained in `deliverables/numerical-basis.md`; rerun it with `deliverables/reproduce.sh`.
