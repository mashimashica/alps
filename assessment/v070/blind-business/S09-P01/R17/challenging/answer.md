# Decision note for Nessa Vale

## Recommendation

**Stop Alder’s all-order second-person check for the next 20 full shifts. Do not expand it to Birch or replace it with selective checking during this period.** Keep the centrally issued packing-list template and mandatory catch recording in place. This is a recommendation only; Nessa retains authority to make the operating decision.

The all-order process is not feasible at the authorized workload and hours, and the mature outcome data do not show a quality benefit after accounting for the planned order mix. Stopping the checker is the only evaluated choice that has a supportable route to 1,440 orders per line per shift within 102 productive hours and the 1% late-dispatch commitment.

## Numerical basis

The apparent raw Alder improvement, from 132/3,600 mature baseline orders mispacked (3.667%) to 63/3,600 pilot orders (1.750%), is not a valid next-period comparison: the complex-order share fell from 41.7% to 8.3%, while the next period is expected to be 30% complex.

At the common planned 70% standard / 30% complex mix:

| Mature seven-day outcome | Baseline | Pilot | Change |
|---|---:|---:|---:|
| Alder standard | 42/2,100 (2.0%) | 33/3,300 (1.0%) | -1.0 percentage point |
| Alder complex | 90/1,500 (6.0%) | 30/300 (10.0%) | +4.0 points |
| **Alder standardized** | **3.2%** | **3.7%** | **+0.5 point** |
| Birch standardized, no checker | 2.6% | 2.5% | -0.1 point |

An illustrative difference in changes is **+0.6 percentage point**: Alder’s planned-mix rate moved 0.6 point higher relative to Birch’s concurrent change. This is context, not a causal estimate. Allocation was not randomized, Alder and Birch differed at baseline, the packing-list template changed on both lines, and the complex pilot sample is only 300 mature Alder orders. The evidence therefore does not establish that checking caused harm, but it does not support crediting checking with the raw aggregate improvement either.

The operational comparison uses the ordinary full shifts only. August 28 was a short, unusually simple shift and is not treated as capacity evidence.

| Twenty-shift planning scenario | Stop checker | Continue all-order checker |
|---|---:|---:|
| Quality-rate assumption | 3.2% | 3.7% |
| Expected mispacks / 28,800 Alder orders | 921.6 | 1,065.6 |
| Expected mispack cost at $55/order | $50,688 | $58,608 |
| Productive hours / shift | 98.4 | 108.0 |
| Margin to 102-hour cap | +3.6 | **-6.0** |
| Output possible at 102 hours | 1,493 orders | **1,360 orders** |
| Late-dispatch-rate assumption | 0.583% | **1.167%** |
| Expected late dispatches / 28,800 | 168 | **336** |

These forecasts scale observed hours per order and rates linearly to the planned workload. That is a planning assumption, not a validated capacity curve. The stop scenario uses Alder’s baseline hours/order, planned-mix quality rate, and late-dispatch rate. The checker scenario uses Alder’s pilot ongoing hours/order after removing the five one-off training hours, its planned-mix quality rate, and its full-shift late rate. Actual paid pilot hours were 275 across the three full shifts, including the five-hour training subset; ongoing hours were 270. Overtime is already included and is not added again.

Continuing would add an estimated **9.6 ongoing hours per shift**, or 192 hours and **$6,528** over 20 shifts. Against the primary stop baseline, it also forecasts 144 more mispacks, so its total expected quality-plus-incremental-labor cost is **$14,448 higher**. Using Birch’s concurrent change to form a comparison-adjusted no-check counterfactual produces a 3.1% rate and makes continuing $16,032 higher; that counterfactual relies on the unproven assumption that Alder would otherwise have changed like Birch.

Even if hours were available, the additional labor would require at least **118.7 avoided mispacks**, a **0.412 percentage-point absolute rate reduction**, merely to break even. The planned-mix observation moved in the opposite direction. The measured checked-shift late rate also projects 336 late orders, above the period maximum of 288. Missed cutoff outcomes remain separate from money because no dollar value was authorized.

## Why the other choices are unsuitable now

- **Continue all-order checking:** the planning scenario requires 108 productive hours per shift, six above the hard cap, and supports only about 1,360 of the required 1,440 orders. Its observed full-shift late rate also exceeds 1%.
- **Expand to Birch:** Birch checking was not tested. Transferring Alder’s observed incremental checker time to Birch would also project roughly 108 hours per shift. The permitted five training hours are one-off and cannot solve the ongoing capacity deficit.
- **Narrow to complex orders:** neither its time nor its quality or dispatch effect was measured. A sensitivity that spreads Alder’s observed checker time evenly would put complex-only checking at 101.3 hours for 432 complex orders, but the data contain no band-level labor and do not validate that estimate. Alder’s measured complex mispack rate was 30/300 (10%) during the all-order pilot versus 90/1,500 (6%) at baseline, so there is no observed quality basis to adopt this scope now.

## Operating and review conditions

For the next period, the interim and recommended operating scope is **no second-person checker on either line**, with 1,440 orders per line per full shift, the planned 70/30 mix, and no more than 102 productive hours per line. The existing packing-list template and catch scans continue; catch counts should remain separate from customer-confirmed seven-day mispacks.

Nessa should review both lines after **shift 3** using immediately available actual hours, shipped orders, order mix, and late dispatches. The guardrails are 102 productive hours per line per shift and no more than 1% cumulative late dispatches on each line. If either fails, Nessa should address the underlying in-cap packing flow; all-order checking remains unavailable because it worsens the measured capacity margin.

The first mature quality readout occurs when each of the first three shift cohorts completes its seven-calendar-day window; the final period readout is seven days after shift 20. The decision-relevant question is whether Alder’s post-template, no-check planned-mix quality is consistent with the 3.2% planning baseline (or the 3.1% comparison-adjusted context) and remains below the observed 3.7% checked scenario. Report standard and complex counts and rates separately, then standardize them to 70/30. If the result is inconclusive or worse, keep all-order checking stopped because it remains infeasible, do not expand, and have Nessa consider a separately designed, timed, in-cap alternative rather than treating selective checking as proven.

## Reproduction

Run from the consumer directory:

```bash
python3 deliverables/analyze.py
```

The script reads the two supplied CSVs, validates keys and denominators, excludes immature cohorts from seven-day quality rates, keeps line-level labor at its own grain, and writes the inspectable result to `deliverables/calculation_output.md`. It uses only the Python standard library.
