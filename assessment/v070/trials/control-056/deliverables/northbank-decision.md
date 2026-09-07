# Northbank dispatch verification decision

**Decision for Mara Venn:** Change the East trial's scope for the next four-week period. End the all-order second-person check and do not expand it to West. Allow one five-full-shift, complex-order-only validation on East only if a preceding five-full-shift no-check run-in demonstrates enough labor and dispatch headroom. At all other times, including while outcomes mature, operate without the second-person check.

This is a recommendation for the site manager, not an instruction that changes production.

## Why this decision

The all-order trial does not fit the next-period operating commitments. On the three comparable 1,000-order pilot shifts, East used 78.0 ongoing productive hours per shift after removing the four one-off training hours and missed the loading cutoff on 59 of 3,000 orders (1.97%). Proportional projection to the planned 1,200 orders gives 93.6 hours, 9.6 above the 84-hour cap. The dispatch rate is nearly twice the 1% promise. West's contemporaneous pattern projects to 83.6 hours at 1,200 orders, leaving only 0.4 hour of headroom before adding any check.

The quality result is favorable but not strong enough to override those hard constraints. At the planned 80% standard / 20% complex mix, East's mature seven-day mispack rate fell from 3.20% to 2.00%. West, which received the common packing-list change but no checker, fell from 3.00% to 2.45%. The resulting descriptive checker benefit is 0.45 percentage point using the pilot comparison and 0.65 point using difference-in-differences. Both approximate 95% sampling intervals include no benefit, and neither resolves non-random line selection or the other concurrent changes.

An immediate complex-only rollout is also not established as feasible. If verification effort were proportional to order count, complex-only checking would project to 85.44–85.60 hours per planned shift using West's recent workload as the base. That is already above the cap, and complex orders may take longer than standard orders. The estimate is a sensitivity, not an observation. A capacity run-in is therefore a launch condition, not a formality.

## Numerical basis

All downstream rates use mature orders only. The 800 orders shipped on June 26 across both lines have open seven-day windows and are excluded from the downstream outcome calculation. Raw rates changed partly because the complex-order mix fell; the planned-mix rates correct that compositional difference.

| Period | Line | Mature errors / orders | Raw rate | Rate at 80% standard / 20% complex |
|---|---:|---:|---:|---:|
| Baseline | East | 132 / 3,000 | 4.40% | 3.20% |
| Baseline | West | 120 / 3,000 | 4.00% | 3.00% |
| Pilot, mature dates | East | 45 / 3,000 | 1.50% | 2.00% |
| Pilot, mature dates | West | 59 / 3,000 | 1.97% | 2.45% |

| Period | Line | Standard | Complex |
|---|---:|---:|---:|
| Baseline | East | 36 / 1,800 = 2.00% | 96 / 1,200 = 8.00% |
| Baseline | West | 36 / 1,800 = 2.00% | 84 / 1,200 = 7.00% |
| Pilot, mature dates | East | 27 / 2,700 = 1.00% | 18 / 300 = 6.00% |
| Pilot, mature dates | West | 40 / 2,700 = 1.48% | 19 / 300 = 6.33% |

| Descriptive mix-adjusted contrast | Estimated benefit | Approximate 95% interval |
|---|---:|---:|
| Pilot West minus pilot East | 0.45 percentage point | −0.45 to 1.36 points |
| Difference-in-differences | 0.65 percentage point | −0.58 to 1.89 points |

Positive benefit means fewer downstream mispacks on East. The intervals reflect binomial sampling variation only; they do not include design bias or confounding.

| Ordinary full shifts | Ongoing hours / shift | Late orders / shipped | Proportional hours at 1,200 | Headroom to 84 |
|---|---:|---:|---:|---:|
| Baseline East | 69.00 | 15 / 3,000 = 0.50% | 82.80 | 1.20 |
| Baseline West | 68.33 | 17 / 3,000 = 0.57% | 82.00 | 2.00 |
| Pilot East | 78.00 | 59 / 3,000 = 1.97% | 93.60 | −9.60 |
| Pilot West | 69.67 | 22 / 3,000 = 0.73% | 83.60 | 0.40 |

The projection is observed ongoing hours per order multiplied by 1,200. It excludes East's four one-off training hours and is a planning estimate rather than a measured 1,200-order shift. June 26 is omitted because it was an atypical short shift; its per-order labor is directionally consistent but does not prove full-shift capacity.

Across 20 planned shifts, the two descriptive all-order quality effects imply 108–156 fewer mispacks and USD 7,049–10,169 of avoided cost at USD 65 each. The corresponding incremental labor estimates are 184–200 hours, costing USD 5,152–5,600 at USD 28 per hour. The point-estimate quality value exceeds labor by roughly USD 1,449–5,017 before dispatch effects. This is not a reliable return forecast: the quality-effect intervals include zero, causal attribution is unresolved, and missed dispatches have no authorized dollar value. A favorable dollar point estimate cannot cure a capacity breach.

## Four-week operating plan and gates

The following plan makes the proposed narrowing testable while keeping the existing constraints in force.

1. **Run-in, first five ordinary full shifts:** No second-person checking on either line. Use existing records to measure East productive hours, shipped volume, order mix, and late dispatches at the planned workload. Do not borrow West staff or add a station.
2. **Launch gate:** Start the complex-only validation only if all five East shifts remain at or below 84 productive hours, their average is at or below 82 hours, and cumulative late dispatches are no more than 1% of shipped orders. At exactly 6,000 shipped orders, that means no more than 60 late orders. The two-hour average reserve is the approximate effort suggested by proportional scaling of the current all-order increment to a 20% complex mix; it is not observed selective-check capacity.
3. **If the launch gate fails:** Operate without the second-person check for the rest of the four weeks. Record the failed capacity or dispatch condition. Do not replace it with a partial or informal check.
4. **Complex-only validation, next five ordinary full shifts if launched:** Check every East complex order and no standard orders. Keep productive labor at or below 84 hours on every shift, use no West staff and no extra station, and record actual check coverage and hours. If all complex orders cannot be checked within the cap, stop checking before exceeding the cap, classify the variant as infeasible, and run no checker for the remainder. Stop after any cumulative dispatch result above 1% of shipped trial orders.
5. **Maturity interval:** After the fifth validation shift, run no checker while its complete seven-calendar-day outcome window elapses. Do not interpret zero-maturity cohorts as error-free.
6. **Review point:** On the first working day after the final trial cohort matures, compare East and West complex-order mispacks, report the before/after and contemporaneous contrasts, measured incremental labor, coverage, and dispatch. The manager may consider a further complex-only period only if every shift met the 84-hour cap, coverage was complete, dispatch was at or below 1%, and the smaller of the contemporaneous and difference-in-differences point estimates produces expected avoided cost at least equal to measured incremental labor cost. Otherwise stop the check. Do not expand to West from this small non-random validation.

The launch and review rules answer two different questions: the run-in tests whether any checker time exists at the planned workload, and the validation tests whether the unmeasured selective scope is operationally feasible and economically promising. Until each gate is passed, no checker operates.

## What the packet establishes, suggests, and leaves unknown

**Establishes**

- East's mature, mix-adjusted downstream rate fell by 1.20 percentage points between the supplied periods.
- West also improved after the common template change, so the full East change cannot be assigned to the checker.
- East's ordinary all-order pilot shifts had a 1.97% late-dispatch rate, above the 1% next-period promise.
- The all-order East workload does not fit the 84-hour cap under the visible proportional projection to 1,200 orders.

**Suggests**

- The checker may have added a 0.45–0.65 percentage-point quality benefit at the planned mix.
- The all-order check may have a positive quality-minus-labor value before dispatch effects, but that result depends on observational effect and workload assumptions.
- Complex orders are the higher-rate group and therefore a reasonable constrained scope to test, not a proven better scope.

**Unknown**

- The checker's causal effect, because East volunteered, baseline risks differed, the large account paused, and the template changed concurrently.
- Whether complex-only checking fits the labor cap or preserves the quality effect; that variant has not been measured.
- The final outcome for June 26 shipments, whose seven-day windows are open.
- A comparable before/after station-catch effect, because mandatory scanner recording began June 12. Catches are not added to downstream mispacks.
- The monetary consequence of late dispatch, for which the packet authorizes no value.

## Reproduce the analysis

From the task directory, run:

```bash
python3 deliverables/skills/operational-intervention-decision/scripts/analyze_packet.py \
  --cohorts input/sources/shipment_cohorts.csv \
  --operations input/sources/shift_operations.csv \
  --intervention-line East \
  --comparison-line West \
  --planned-mix standard=0.8,complex=0.2 \
  --ordinary-dates 2026-06-01,2026-06-02,2026-06-03,2026-06-15,2026-06-16,2026-06-17 \
  --planned-shifts 20 \
  --orders-per-shift 1200 \
  --labor-cap-hours 84 \
  --error-cost 65 \
  --hour-cost 28 \
  --output deliverables/northbank-analysis.json
```

The inspectable output is `deliverables/northbank-analysis.json`.
