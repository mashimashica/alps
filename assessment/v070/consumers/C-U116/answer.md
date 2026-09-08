# Decision memo: Fenwick Audio Renewal packing check

**To:** Nessa Vale, site manager  
**Horizon:** Next 20 full shifts, 1,440 orders per line per shift, planned 70% standard / 30% complex mix

## Recommendation

**Stop Alder’s all-order second-person packing check for the next 20 full shifts and do not expand it to Birch.** Plan both lines without a second checker, subject to Nessa’s final approval. The measured all-order process is infeasible under the 102-hour hard cap, missed the dispatch commitment on comparable full shifts, and did not show a quality advantage after accounting for the planned order mix and the untreated line.

This recommendation does not claim that checking can never work. A selective variant has not been measured, and the packet cannot establish its labor, quality, or dispatch effects. It should not be put into the 20-shift plan until a bounded trial passes the feasibility gate below.

## What the measurements support

The raw mature mispack rate on Alder fell from 132/3,600 (3.67%) before the pilot to 63/3,600 (1.75%) during it. That raw comparison is misleading for the next period because complex orders fell from 41.67% to 8.33% of the mature cohort. Birch, which had no checker, also fell from 102/3,600 (2.83%) to 51/3,600 (1.42%).

At the next-period 70/30 mix, the band-specific rates give:

| Mature quality measure | Alder baseline | Alder checked pilot | Birch baseline | Birch untreated pilot |
|---|---:|---:|---:|---:|
| Standard | 42/2,100 = 2.00% | 33/3,300 = 1.00% | 42/2,100 = 2.00% | 33/3,300 = 1.00% |
| Complex | 90/1,500 = 6.00% | 30/300 = 10.00% | 60/1,500 = 4.00% | 18/300 = 6.00% |
| **Rate standardized to 70/30** | **3.20%** | **3.70%** | **2.60%** | **2.50%** |

Alder therefore worsened by 0.50 percentage points on a standardized before/after basis, while Birch improved by 0.10 points. The difference-in-differences sensitivity is an adverse 0.60 points. Contemporaneously, checked Alder was 1.20 points worse than untreated Birch at the planned mix. These are comparisons, not causal estimates: assignment was not random, Alder started worse on complex orders, the complex pilot denominator was only 300 orders per line, the complex-account pause changed mix, and the August 14 template change affected both lines.

August 28 has no mature orders, so its zero outcome counts are excluded from quality. Station catches are also excluded: recording changed on August 14, and catches are a process proxy rather than downstream failures.

## Workload, staffing, and dispatch

All calculations use whole-line operations once per date. The five Alder training hours on August 17 are removed from recurring labor; all other productive hours remain.

| Operating case | Observed basis | Linear projection at 1,440 | Position vs 102-hour cap | Volume feasible at cap |
|---|---:|---:|---:|---:|
| Alder, checked pilot | (275 − 5) / 3,600 = 0.07500 h/order | **108.0 h/shift** | **6.0 h over** | 1,360 |
| Alder, baseline no-check | 246 / 3,600 = 0.06833 h/order | **98.4 h/shift** | 3.6 h headroom | 1,493 |
| Birch, contemporaneous no-check | 246 / 3,600 = 0.06833 h/order | **98.4 h/shift** | 3.6 h headroom | 1,493 |

All-order checking would require 9.6 recurring hours per shift above the Alder no-check baseline and cannot process the required 1,440 orders within the cap. Staffing cannot be added or borrowed, and orders cannot be moved, deferred, or cancelled under Nessa’s authority. The no-check projection fits, but its 3.6-hour margin is small. Before shift 1, Nessa should verify that each line’s scheduled productive hours and expected work fit within 102 hours; a forecast above 102 is a capacity exception requiring escalation before launch.

On the three comparable full pilot shifts, checked Alder recorded 42/3,600 late dispatches (1.17%), above the 1% commitment; untreated Birch recorded 18/3,600 (0.50%). At those rates, the 20-shift totals would be 336 versus 144 late orders, while the commitment allows at most 288 per line. August 28 was a short, unusually simple shift and is not evidence of full-shift capacity. The service figures are not monetized because no authorized value was supplied.

## Economics

At $34 per incremental recurring hour, all-order checking costs `9.6 × $34 = $326.40` per shift, or **$6,528** over 20 shifts. The separate one-off training allowance is excluded.

| Scenario for all-order checking | Assumed quality benefit at 70/30 | Gross avoided cost/shift | Net after labor/shift | Net over 20 shifts |
|---|---:|---:|---:|---:|
| Conservative: untreated Birch pilot rates are the counterfactual | −1.20 points = −17.28 avoided errors | −$950.40 | **−$1,276.80** | **−$25,536** |
| Favorable: fully attribute Alder’s 1-point standard improvement to checking and assume no complex effect | +0.70 points = 10.08 avoided errors | $554.40 | **+$228.00** | **+$4,560** |

The labor cost breaks even at 5.93 avoided mispacks per shift, a 0.412-point reduction across 1,440 orders. The favorable scenario is deliberately optimistic because observed complex performance did not improve. Even that scenario cannot override the staffing infeasibility or dispatch result.

## Twenty-shift operating scope and review

- **Scope:** No second-person all-order check on either line for all 20 shifts. No selective check is represented as proven or included in the operating plan.
- **Workload and staffing:** 1,440 orders per line per shift at 70/30, with productive labor at or below 102 hours on each line. Nessa verifies the shift-1 plan; the planning scenario is 98.4 hours per line.
- **Service response:** Track cumulative late dispatches per line after every shift against 1.00%. If a line exceeds the limit or its 20-shift projection crosses 288, Nessa reviews the capacity cause immediately while keeping any response within 102 hours and the fixed workload.
- **Quality measurement:** Continue the same mutually exclusive band cohorts and seven-day outcome definition. Review mature standard and complex rates separately; do not combine catches with confirmed mispacks.
- **Owner and review point:** Nessa owns the operating decision and reviews workload and dispatch after shift 5. She reviews the first ten shifts’ mature quality seven calendar days after shift 10, then makes the final period review seven calendar days after shift 20.

The mid-period quality question is whether no-check performance at the planned mix confirms an economically material problem, especially in complex orders, that warrants designing a selective trial. Any selective complex-order trial must first demonstrate a recurring labor requirement no greater than the available 3.6 hours per shift—about 30 seconds across each of the planned 432 complex orders if labor scales per order—and a credible path to no more than 1% late dispatches. It then needs a randomized or crossover comparison with fully matured seven-day outcomes. Until those conditions are met, the interim and full-period decision remains no checking.

## Reproduction

Run `python3 deliverables/analysis.py` from this consumer directory. It uses only the Python 3 standard library, reads the supplied CSV files unchanged, checks keys and counts, and writes `deliverables/numerical_basis.md` with formulas, intermediate totals, denominators, and scenarios.
