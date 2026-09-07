# Cedar Quay packing-check decision

**Recommendation to Iona Bell: controlled expansion.** Continue the second-person check on every Harbor order for all twenty full shifts. Add the same all-order check at Ridge for the first six full shifts, then pause it there until all six cohorts have completed the seven-calendar-day observation window. Continue Ridge for the balance of the period only if the review gates below pass. Harbor should keep checking during the Ridge review interval; Ridge should run its usual process during that interval.

This uses the measured all-order process. A standard-only, complex-only, or other selective check has not been measured and should not be adopted on the assumption that it preserves the measured labor or quality effect.

## Data basis and comparability

The quality observation is one **mature order**. Shipment rows are mutually exclusive date/line/order-band cohorts, keyed by `shipment_date + line + order_band`. Operations rows are whole line-dates, keyed by `shipment_date + line`; each operations row is used once and is not repeated for both bands.

The July 31 cohorts have no mature orders, so their zero outcomes are unavailable quality data rather than a zero error rate. July 31 was also a 320-order short shift, so it is excluded from full-shift labor and capacity evidence. Its immediately observable dispatch results are reported separately.

| Period and line | Mature orders | Confirmed 7-day mispacks | Mispack rate | Station catches (separate process measure) |
|---|---:|---:|---:|---:|
| Harbor baseline | 2,400 | 63 | 2.625% | 13 |
| Harbor pilot | 2,400 | 30 | 1.250% | 38 |
| Ridge baseline | 2,400 | 63 | 2.625% | 12 |
| Ridge pilot | 2,400 | 60 | 2.500% | 14 |

Harbor's observed change was `1.250% - 2.625% = -1.375 percentage points`. Ridge's concurrent change was `2.500% - 2.625% = -0.125 percentage points`. The descriptive difference-in-differences adjustment is therefore:

`-1.375 pp - (-0.125 pp) = -1.250 pp`.

The band results point in the same direction:

| Band | Harbor baseline | Harbor pilot | Ridge baseline | Ridge pilot | Adjusted change |
|---|---:|---:|---:|---:|---:|
| Standard | 27/1,800 = 1.500% | 12/1,800 = 0.667% | 27/1,800 = 1.500% | 27/1,800 = 1.500% | -0.833 pp |
| Complex | 36/600 = 6.000% | 18/600 = 3.000% | 36/600 = 6.000% | 33/600 = 5.500% | -2.500 pp |

At the planned 75% standard / 25% complex mix, the adjusted change remains:

`0.75 × (-0.833 pp) + 0.25 × (-2.500 pp) = -1.250 pp`.

Station catches increased at Harbor while downstream mispacks fell, which is consistent with the check finding issues before dispatch. Catches are not added to mispacks and do not establish causation.

## Twenty-shift workload, cost, capacity, and dispatch

Each line is planned for `20 × 800 = 16,000` orders: 12,000 standard and 4,000 complex. Applying Harbor's observed pilot band rates gives a **planning estimate** of `12,000 × 0.667% + 4,000 × 3.000% = 200` downstream mispacks. A comparison-adjusted counterfactual is 400 (`16,000 × 2.500%`), so the planning workload difference is 200 fewer mispacked orders per checked line.

At $48 per event, that is `$9,600` of expected avoidable quality cost per line. It is not proven realized savings. The unadjusted Harbor before/after comparison would imply 220 fewer events; the more conservative 200-event adjustment is used for the decision.

On ordinary Harbor shifts, baseline productive labor averaged `186 / 3 = 62` hours. Pilot productive labor was 198 hours, including three one-off introductory training hours; recurring pilot labor was therefore `(198 - 3) / 3 = 65` hours per shift. This is three added productive hours per shift and fits the 68-hour cap with three hours of headroom. Overtime, already included in productive hours, averaged two hours at baseline and five during the Harbor pilot. Over twenty shifts, the recurring addition is 60 hours costing `$1,920`. Harbor's comparison-adjusted planning net is therefore `$9,600 - $1,920 = $7,680`.

Ridge averaged 62 productive hours per ordinary pilot shift. Applying Harbor's measured three-hour increment is a **planning scenario**, not measured Ridge capacity: 65 hours per shift, still below the cap. Over twenty shifts, Ridge would add 60 recurring hours ($1,920) plus up to three separately funded training hours ($96). If Ridge reproduced the adjusted quality effect, its planning net after training would be `$9,600 - $1,920 - $96 = $7,584`.

Harbor had 13 late dispatches in 2,400 ordinary pilot-shift orders (0.542%), compared with 14/2,400 (0.583%) at baseline. Ridge was also 13/2,400 (0.542%) during the ordinary pilot dates. These observed rates are below the 1% commitment. On the short July 31 shift, Harbor had 2/320 late (0.625%) and Ridge 1/320 (0.313%); these observations are valid for dispatch but not for full-shift capacity. No dollar value is assigned to late dispatch.

## Options considered

| Option | Workload and mix | Supported effect | Labor, cost, and service | Decision |
|---|---|---|---|---|
| Stop Harbor | Harbor 16,000 orders at 75/25 under usual process | Gives up the observed Harbor improvement | Avoids $1,920 recurring labor, but the adjusted scenario adds about 200 mispacks and $9,600 quality cost; dispatch had not worsened | Reject |
| Continue Harbor only | Harbor checks all 16,000; Ridge processes its 16,000 as usual | Harbor observed 1.250%; adjusted planning reduction 200 events | Harbor plans at 65 hours/shift; $7,680 planning net; observed dispatch below 1% | Feasible fallback, but does not test portability to Ridge |
| Narrow by order band | Any selective share of the 75/25 mix | Complex orders have the higher rate, but no selective process was observed | Selective labor, capacity, quality, and savings are unknown | Reject without measurement |
| Expand both lines for all twenty shifts immediately | 32,000 checked orders at 75/25 | Harbor effect on Ridge is a projection | Both lines project to 65 hours/shift; combined planning net $15,264 after Ridge training; Ridge service and quality are unmeasured under checking | Too broad for the evidence |
| Controlled expansion | Harbor checks all twenty shifts; Ridge checks six full shifts before a maturity-gated decision | Preserves the measured Harbor process and tests Ridge directly | First Ridge stage adds 18 recurring hours plus three training hours ($672); constraints and outcomes are reviewable | **Recommend** |

## Ridge evidence stage and decision gates

1. **Scope:** On Ridge's first six ordinary full shifts, check every order at the same point and with the same all-order method used at Harbor. Expected trial workload is 4,800 orders: 3,600 standard and 1,200 complex.
2. **Staffing and training:** Schedule three one-off training hours before the period from the separately authorized training allowance. Plan 65 total productive hours on each treated Ridge shift and never exceed 68. Use no extra station and do not borrow Harbor staff.
3. **Controls:** Keep packing lists, equipment, suppliers, incentives, crews, catch logging, customer reporting, and outcome definitions unchanged. Record productive, overtime, and training hours at line-date grain; record shipped, mature, mispack, and catch counts by band.
4. **Primary outcome:** Confirmed customer mispacks within seven calendar days divided by mature orders, standardized to the 75/25 planned mix. Station catches remain a separate process measure. Dispatch is assessed immediately and separately.
5. **Review point:** After shift six, Ridge returns to its usual process while the last treated cohort matures. Iona reviews at 09:00 UTC on the first day after all six cohorts have completed their seven-calendar-day windows.
6. **Immediate rollback triggers:** Stop Ridge checking if a treated full shift cannot be staffed within 68 productive hours, would require an extra station or borrowed staff, or if cumulative late dispatch exceeds 1% after any two or more treated shifts. A definition or recording change invalidates the evidence stage and returns Ridge to its usual process pending a clean restart.
7. **Continuation gates:** Resume the check at Ridge for the remaining period only if all 4,800 trial orders are mature; total late dispatch is at most 48/4,800; every treated shift stayed within 68 hours; and the 75/25 mature mispack rate is at most 2.2375% (with the planned exact mix, at most 107 confirmed mispacks), with neither band worse than Ridge's recent no-check pilot rate of 1.5% standard and 5.5% complex. The 2.2375% threshold represents the 2.5% recent Ridge rate less the 0.2625 percentage-point improvement needed to cover 60 recurring hours plus three training hours over twenty shifts at the supplied prices. If any gate fails, Ridge uses its usual process for the rest of the period; Harbor continues its measured process unless Harbor itself breaches the labor or dispatch limits.

This follow-up resolves whether Harbor's quality effect and labor pattern transfer to Ridge. It still will not prove causation because participation was not randomized and the evidence cells remain modest. The same-crews, unchanged-controls, concurrent-comparison design makes the result useful for an operating decision, but the projections are not guarantees.

## Reproduction

Run from the C-U101 task directory:

```bash
python3 deliverables/reproduce_decision.py
```

The script validates the declared grains and join keys, excludes immature quality cohorts and the short shift from full-shift capacity calculations, and writes the inspectable metric table to `deliverables/derived_metrics.csv`.
