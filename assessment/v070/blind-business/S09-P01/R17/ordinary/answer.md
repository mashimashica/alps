# Cedar Quay packing-check decision

**Recommendation to Iona Bell:** approve Harbor’s second-person check for **all standard and complex orders for the next 20 full shifts**. Keep Ridge on its usual process during this period. Do not narrow Harbor or roll the check out to Ridge yet. This is a recommendation only; the packet does not authorize an operating change or spending.

## Why continue Harbor

The matched evidence covers three ordinary 800-order full shifts before and three during the pilot on each line. Harbor’s mature seven-day mispack rate fell from **63/2,400 (2.625%)** to **30/2,400 (1.250%)**. Ridge changed from **63/2,400 (2.625%)** to **60/2,400 (2.500%)**. At the planned 75% standard / 25% complex mix, which matches the observed mix, the illustrative difference in changes is therefore a **1.250 percentage-point reduction** at Harbor. The within-band results point the same way: Harbor’s standard rate fell from 1.500% to 0.667% while Ridge stayed at 1.500%; Harbor’s complex rate fell from 6.000% to 3.000% while Ridge fell from 6.000% to 5.500%.

This is useful comparison evidence, not a proven causal effect. Harbor volunteered, allocation was not random, and each period contains only three matched full shifts. The interpretation assumes Harbor would otherwise have followed Ridge’s concurrent change. Station catches increased at Harbor from 13/2,400 to 38/2,400 shipped orders, but they are preventive process observations and are neither added to mispacks nor priced.

## Planned workload, labor, and economics

Harbor will ship an estimated **16,000 orders** over 20 shifts. Applying the observed Harbor pilot rate gives **200 expected mispacks**. The analysis counterfactual—Harbor’s baseline rate adjusted by Ridge’s concurrent 0.125-point improvement—gives **400 expected mispacks**. The resulting 200-order difference is worth **$9,600** at $48 per mispack, if the comparison assumption holds. A simpler unchanged-baseline counterfactual would give 420 mispacks and $10,560 of avoided cost; it is less conservative.

Harbor used 186 hours over the three baseline shifts, or **62 hours per shift**. It used 198 hours during the three pilot shifts; removing the explicitly one-off three training hours gives an ongoing estimate of **195 hours, or 65 per shift**. That is 12.31 orders per ongoing labor hour and 0.08125 hour per order, versus 12.90 orders per paid hour and 0.07750 hour per order at baseline. Linear scaling gives **1,300 ongoing hours** for the next period, **60 more than baseline**, costing **$1,920** at $32 per additional hour. It leaves three hours per shift, or 60 hours over the period, below the 68-hour limit.

On those assumptions, continuation has an **illustrative net cost reduction of $7,680**: $9,600 avoided mispack cost less $1,920 incremental labor. The break-even quality effect is **0.250 percentage point**, equal to 40 mispacks over 16,000 orders, versus the observed comparison-adjusted 1.250-point effect. These are forecasts, not realized savings. Linear labor scaling and unchanged next-period performance are assumptions; aggregate labor does not reveal band-specific effort.

Harbor’s full-shift late-dispatch rate was **13/2,400 (0.542%)** in the pilot, compared with 14/2,400 (0.583%) at baseline. At the pilot rate, the planning projection is about **87 late orders**, below the line-level limit of 160 over 16,000 orders. July 31’s short-shift result, 2/320 (0.625%), is consistent immediate context but is not capacity evidence. Dispatch remains unpriced and must stay a separate service guardrail.

## Why the other choices are unsuitable now

- **Stop:** saves an estimated 60 recurring labor hours, but under the comparison-adjusted counterfactual gives up an estimated 200 avoided mispacks and is $7,680 worse over the period.
- **Narrow Harbor:** a selective check has no measured quality effect or labor requirement. Any claimed capacity or savings would be invented.
- **Expand to Ridge for all 20 shifts:** applying Harbor’s three-hour increment would project 65 hours per Ridge shift and a favorable net result, but both the labor transfer and quality effect are unmeasured. Ridge would also need separately funded introductory training, and Iona may propose rather than approve expansion. Keep Ridge unchanged as the concurrent comparison and revisit expansion after the mature readout.

## Operating and review conditions

Use the same all-order Harbor scope for comparability. Cap productive labor at **68 hours per shift**; the one-off Harbor training is already incurred and is not part of the next-period forecast. Track shipped orders, productive/overtime hours, late dispatches, catches, and seven-day confirmed mispacks by order band without changing definitions.

Iona should review hours and dispatch immediately after shifts 1–3. If any shift needs more than 68 productive hours, the option is infeasible and Iona should stop the added check pending a redesigned scope. If cumulative Harbor late dispatch exceeds 1% after those first three full shifts, pause before the next shift and review the check’s effect on cutoff performance. Otherwise continue while outcomes mature.

Read the first quality checkpoint no sooner than seven calendar days after the tenth full shift ships; use mature counts only, apply the planned 75/25 mix, and repeat the concurrent Ridge change comparison. The decision question is whether the Harbor point estimate still exceeds the **0.250-point economic break-even effect** while labor and dispatch remain within their guardrails. If the estimate is at or below break-even, stop the added check for the remaining shifts. If it exceeds break-even, complete the 20-shift period. If the result is too count-sensitive to support expansion but remains above break-even, continue Harbor and keep Ridge unchanged; do not infer a Ridge benefit.

The final mature readout is due seven calendar days after shift 20 ships. It should decide whether Harbor continues beyond this horizon and whether Iona should propose a separately authorized, capped Ridge trial. Twenty shifts improve the evidence but cannot guarantee statistical certainty or establish causality.

The inspectable calculation is in `deliverables/numerical-basis.md`; reproduce it with:

```bash
python3 deliverables/analyze.py
```

The script validates the input structure and writes the full aggregates, category rates, formulas, assumptions, and projections to `deliverables/analysis.json`.
