# Cedar Quay packing-check decision

## Recommendation

Iona Bell should **continue Harbor’s second-person check on every standard and complex order for the next 20 full shifts**, using Harbor’s existing line resources and a hard ceiling of 68 productive labor hours per shift. Keep Ridge on its usual process during this evidence period. Do not narrow Harbor to selected orders or expand to Ridge yet.

This is the best bounded decision because Harbor’s check was operationally feasible on all three comparable pilot shifts, dispatch remained within the 1% commitment, and mature downstream mispacks fell within both order bands. The packet supports continuation as an evidence period; it does not prove that the check caused the reduction.

The alternatives lose for specific reasons:

- **Stopping** gives up a favorable quality and cost signal even though the tested Harbor process fit the stated constraints.
- **Narrowing** would create an unmeasured process. The packet has no labor by order band, so neither its capacity nor its savings can be calculated.
- **Expanding to Ridge now** assumes that Harbor’s labor effect transfers and that Ridge can perform the check without another station or staff transfer. Neither has been demonstrated. Preserve Ridge as a comparison and reconsider a separately bounded Ridge trial only after a within-line staffing and station plan shows it can fit the 68-hour cap.

Iona retains the operating decision; this analysis changes no staffing, spending, systems, or live operations.

## Numerical basis

The planned 75% standard / 25% complex mix exactly matches every observed full shift, so the raw full-shift aggregate rates also equal the common-mix standardized rates. July 31 is excluded from mature quality and capacity comparisons because its cohorts were immature and it was a deliberately short 320-order shift.

| Mature 7-day outcome | Harbor baseline | Harbor pilot | Ridge baseline | Ridge pilot | Comparison-adjusted Harbor decrease |
|---|---:|---:|---:|---:|---:|
| Standard | 27/1,800 (1.50%) | 12/1,800 (0.67%) | 27/1,800 (1.50%) | 27/1,800 (1.50%) | 0.83 pp |
| Complex | 36/600 (6.00%) | 18/600 (3.00%) | 36/600 (6.00%) | 33/600 (5.50%) | 2.50 pp |
| 75% / 25% standardized | 63/2,400 (2.625%) | 30/2,400 (1.250%) | 63/2,400 (2.625%) | 60/2,400 (2.500%) | **1.250 pp** |

The adjusted planning contrast is:

`(2.625% - 1.250%) - (2.625% - 2.500%) = 1.250 percentage points`.

Station catches are a separate process measure: on the three full shifts they rose from 13 to 38 at Harbor and from 12 to 14 at Ridge. They are not added to customer-confirmed mispacks.

| Full-shift operating measure | Harbor baseline | Harbor pilot | Ridge baseline | Ridge pilot |
|---|---:|---:|---:|---:|
| Shifts / orders | 3 / 2,400 | 3 / 2,400 | 3 / 2,400 | 3 / 2,400 |
| Recurring productive hours, total (average/shift) | 186 (62) | 195 (65) | 186 (62) | 186 (62) |
| Observed recurring-hour range per shift | 61–63 | **65–65** | 61–63 | 62–62 |
| Overtime hours, total (average/shift) | 6 (2) | 15 (5) | 6 (2) | 6 (2) |
| Late dispatches | 14 (0.583%) | 13 (0.542%) | 14 (0.583%) | 13 (0.542%) |

Harbor’s July 20 total was 68 productive hours, but 3 were one-off introductory training, leaving 65 recurring hours. Training and overtime are already included in productive hours; neither is added again. The recurring pilot level leaves 3 hours under the per-shift cap. July 31’s immediate dispatch result was 2/320 (0.625%) at Harbor and 1/320 (0.313%) at Ridge; it is reported separately and is not a full-shift capacity test.

## Twenty-shift planning case

The capacity and economic estimates use Harbor’s own baseline as the stopping alternative and the comparison-adjusted quality change as the effect scenario.

| Item | Calculation | Planning result |
|---|---:|---:|
| Harbor volume | 20 × 800 | 16,000 orders |
| Recurring hours with check | 16,000 × (195 / 2,400) | 1,300 hours, or 65/shift |
| Available hours | 20 × 68 | 1,360 hours |
| Headroom | 1,360 − 1,300 | 60 hours |
| Proportional capacity at 68 hours | 68 ÷ (65 / 800) | about 837 orders/shift |
| Incremental hours vs Harbor baseline | 20 × (65 − 62) | 60 hours |
| Expected avoided mispacks | 16,000 × 1.250% | 200 |
| Gross avoidable cost | 200 × $48 | $9,600 |
| Recurring incremental labor cost | 60 × $32 | $1,920 |
| **Net avoided cost scenario** | $9,600 − $1,920 | **$7,680** |

The break-even quality reduction is 0.25 percentage points: 40 avoided errors × $48 equals the $1,920 recurring labor cost. Harbor’s raw before/after reduction is 1.375 percentage points, but the decision case uses the more conservative 1.250-point comparison-adjusted scenario. The three already-used training hours would equal $96 at the labor rate if counted economically, but they were one-off, separately funded, and are excluded from recurring cost.

The 837-order capacity figure is a proportional scenario, not a capacity guarantee. The supported decision is for the planned 800 orders at the observed mix. No subgroup labor data exists, so a different-mix labor forecast is not identified. There is also no authorized dollar value for late dispatch, so dispatch is kept outside the net-cost estimate.

## Operating boundary and reviews

For the 20 shifts, Harbor should check all orders and Ridge should remain unchanged. Harbor gets no added station, no transferred staff, and no authority to exceed 68 productive hours in a shift. If the check cannot be staffed within that cap, or Iona determines that continuing it cannot sustain the line’s at-most-1% dispatch commitment, the affected shift should use the usual process and record the exposure change rather than exceed the constraint.

Iona should conduct:

1. **An early operating review after three full shifts.** Reconcile 800 orders per line per shift and the actual band mix; review Harbor’s productive hours, overtime, late dispatches, completed-check exposure, and station catches. Continue only while the check fits within 68 hours and the service commitment remains supportable. The packet provides no separate universal mispack or return threshold, so none is invented here.
2. **A quality review once the complete seven-day window has elapsed for the first 10 shifts, followed by a final review after all 20 shifts mature.** For Harbor and Ridge, calculate confirmed mispacks over mature orders by band and standardize both lines to the planned 75% / 25% mix. Recalculate Harbor’s before/after change, Ridge’s contemporaneous change, the adjusted contrast, labor, and dispatch. Pending cohorts remain pending.

The later review should answer whether the favorable within-band Harbor association persists at the planned workload and whether a separate Ridge feasibility trial is justified. Any Ridge trial still needs a demonstrated staffing allocation and station arrangement within 68 hours, its own scope and stop rule, and up to three separately funded training hours. If Harbor cannot sustain the hard labor or service constraints, stop the check pending redesign; if it can, use the mature quality and cost evidence to decide whether continuation beyond 20 shifts is warranted.

## Reproduction, lineage, and limits

Run `python3 deliverables/reproduce.py` from this task directory. The [calculation script](deliverables/reproduce.py) reads the two supplied CSVs, validates unique source keys and population bounds before aggregating, keeps operations at whole-line/date grain, and writes the [captured calculation results](deliverables/calculation_results.json).

The authority is `input/sources/shipment_cohorts.csv`, `input/sources/shift_operations.csv`, `input/sources/measurement_notes.md`, and `input/sources/decision_context.md`. The script confirmed 28 unique cohort rows and 14 unique line/date operations rows, with no duplicate keys; all outcome counts were within mature counts and all mature counts within shipped counts. Whole-shift labor was aggregated once and was not joined onto order-band rows.

Harbor volunteered and allocation was not randomized. The adjusted contrast assumes comparable underlying trends, stable measurement, no differential selection, and equal exposure to other changes. The packet says measurement and crews were stable and identifies no concurrent operational change, but three baseline and three mature pilot shifts are too few to establish parallel trends or remove clustering concerns. Outcome counts are small, no significance claim is made, and the observed results do not guarantee the forecast. July 31 quality remains pending.
