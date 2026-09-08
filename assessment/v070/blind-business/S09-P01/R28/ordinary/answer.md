# Cedar Quay packing-check decision

## Decision

Continue Harbor's second-person check on **every order for all 20 full shifts**. Iona should also **propose the same all-order process for Ridge**, beginning with the first shift and subject to a formal gate after 10 full shifts plus the seven-day outcome window. Do not narrow to complex orders: a selective process has not been measured, so its labor, capacity, and savings are unknown.

This is a guarded expansion, not a proven causal claim. Harbor's improvement was large, Ridge's untreated results were nearly flat, the workload and crews were comparable, and the observed recurring staffing fits the hard limit. Allocation was voluntary rather than randomized and only three mature checked shifts exist, so transfer to Ridge and persistence over time still need confirmation.

## Observed evidence

Only mature 800-order full shifts are used for downstream quality. July 31 was a deliberately short 320-order shift and its seven-day outcomes were unavailable; its zeroes are not treated as error-free orders.

| Period | Line | Confirmed mispacks / mature orders | Rate | Station catches / shipped orders | Recurring productive hours / shift | Overtime hours / shift | Late dispatches / shipped orders |
|---|---|---:|---:|---:|---:|---:|---:|
| Baseline | Harbor | 63 / 2,400 | 2.625% | 13 / 2,400 (0.542%) | 62 | 2 | 14 / 2,400 (0.583%) |
| Pilot | Harbor | 30 / 2,400 | 1.250% | 38 / 2,400 (1.583%) | 65 | 5 | 13 / 2,400 (0.542%) |
| Baseline | Ridge | 63 / 2,400 | 2.625% | 12 / 2,400 (0.500%) | 62 | 2 | 14 / 2,400 (0.583%) |
| Pilot | Ridge | 60 / 2,400 | 2.500% | 14 / 2,400 (0.583%) | 62 | 2 | 13 / 2,400 (0.542%) |

Harbor's raw before/after change was **-1.375 percentage points** (33 fewer mispacks per 2,400 orders). Ridge changed by **-0.125 points** over the same periods. The difference-in-differences estimate is therefore **-1.250 points**, or 10 fewer mispacks per 800-order shift. The comparison helps account for common period movement but does not establish causality.

The result appears in both material segments:

| Order band | Harbor baseline | Harbor pilot | Ridge baseline | Ridge pilot | Difference-in-differences |
|---|---:|---:|---:|---:|---:|
| Standard | 27/1,800 (1.500%) | 12/1,800 (0.667%) | 27/1,800 (1.500%) | 27/1,800 (1.500%) | -0.833 points |
| Complex | 36/600 (6.000%) | 18/600 (3.000%) | 36/600 (6.000%) | 33/600 (5.500%) | -2.500 points |

Harbor's catches also rose while Ridge's were nearly flat. Because catches are pre-dispatch process observations, they support the mechanism but are not added to downstream mispacks.

The Harbor pilot used 198 productive hours over three shifts, including three one-off training hours. Removing that training leaves **65 recurring hours per full shift**, versus 62 at baseline. Hours are taken from the whole-line operations rows once; band rows do not duplicate them. Harbor's overtime rose from two to five hours per shift, but overtime is already a subset of productive hours and is not costed again.

## Twenty-shift planning case

Each line is planned for 16,000 orders: 12,000 standard and 4,000 complex. Applying the comparison-adjusted band effects gives an estimate of **100 fewer standard and 100 fewer complex mispacks per checked line**, 200 total. One transparent comparison is the Ridge pilot no-check rate: 2.5% implies 400 mispacks in 16,000 orders; applying the 1.25-point estimate implies 200.

Per checked line:

- Expected avoidable quality cost: 200 × $48 = **$9,600**.
- Incremental recurring labor: 3 hours/shift × 20 × $32 = **$1,920**.
- Estimated net avoidable cost: **$7,680** over the period.
- Recurring staffing assumption: **65 hours/shift**, leaving three hours below the 68-hour ceiling.

For both checked lines, the planning estimate is 400 avoided mispacks, $19,200 of avoidable quality cost, 120 incremental recurring hours costing $3,840, and **$15,360 net**. Ridge may need three separately funded pre-period training hours; valuing them at the supplied hourly rate is another $96, reducing the combined estimate to **$15,264**. Harbor's training is already complete. These are extrapolations, not realized savings; they assume the Harbor effect and three-hour recurring increment persist and transfer to Ridge.

Dispatch has no authorized dollar value and is kept separate. Harbor recorded 13/2,400 late orders during the pilot, 0.542%, and Ridge had the same untreated pilot rate. Holding that rate would imply about **87 late orders per line**, below the 160-order (1%) limit. Ridge's dispatch response to checking remains unobserved.

## Operating and review gates

- Staff each checked line at a planned 65 recurring productive hours per full shift; never schedule above 68, use another line's staff, or assume another station. Schedule up to three Ridge training hours before the period under the separate funding allowance.
- Preserve the measured all-order scope and the existing definitions. Record shipped and mature orders, seven-day confirmed mispacks by band, station catches, productive/training/overtime hours, and late dispatches.
- Review at the first date when Ridge's first 10 full-shift cohorts have all completed their seven-day windows. The review asks whether the Harbor effect transfers and whether it persists without breaching hours or dispatch. While those outcomes mature, continue Ridge provisionally only while the hours and dispatch gates remain satisfied.
- At that review, continue Ridge for the remainder of the 20-shift period only if every completed shift stayed within 68 productive hours, cumulative late dispatches are at most 1%, and its mature checked mispack rate is below the economic break-even rate of **2.25%**. That break-even is the 2.50% untreated pilot benchmark less 0.25 points, because a 0.25-point reduction over 8,000 orders yields 20 avoided mispacks × $48 = $960, equal to 30 added hours × $32.
- If Ridge breaches the hours or dispatch limit, suspend its new check and return it to the usual process while Iona reviews staffing. If it misses the mature quality/economic gate, stop Ridge after the checkpoint. Harbor continues unless its own hours or dispatch breach a hard limit; reassess Harbor at the same maturity date for persistence.

Iona can approve Harbor's continuation and can propose Ridge's expansion within these limits; this memo does not authorize a live change, spending, staffing transfer, or contact with anyone.

## Reproduce the arithmetic

From the task directory, run:

```bash
python3 deliverables/analyze.py
```

The script reads only the two supplied CSV files, validates their grains and maturity, excludes the July 31 short shift from full-shift calculations, and prints the observed denominators, weighted rates, hours, dispatch, band effects, and forward-cost arithmetic.
