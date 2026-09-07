# Northbank: stop universal verification for the next four-week period

**Recommendation to Mara Venn:** stop the all-order second-person check on East for the coming twenty full shifts; retain the centrally supplied packing-list template and existing catch recording on both lines. Keep West on its current process. Do not expand or assume that a selective check is ready to replace the current trial. Schedule an early review of ordinary packing at the planned workload, within the existing 84 productive hours per line per shift. This is a recommendation for approval, not an instruction that has been executed.

The checker appears promising for quality and may pay for its labor. However, the measured recurring East pace implies **93.6 hours for 1,200 orders**, exceeding the cap by **9.6 hours per shift**. East also missed the dispatch cutoff on **1.97%** of comparable pilot shipments. Neither separate training funding nor a positive estimated financial return solves these ongoing constraints. Stopping is the most defensible available operating choice; the packet does not prove any process can meet the higher planned volume and changed mix, so the fallback needs immediate monitoring.

## What the outcome measurements show

Use June 1–3 and June 15–17 as the matched ordinary full-shift windows. Each line shipped 3,000 orders in each window, all mature. Quality is distinct customer-confirmed mispacked orders within seven days divided by mature orders.

| Line and period | Mature mispacks/orders | Raw rate | Complex share | Standard errors/orders | Complex errors/orders | Rate at next-period 80/20 mix |
|---|---:|---:|---:|---:|---:|---:|
| East baseline | 132/3,000 | 4.40% | 40% | 36/1,800 = 2.00% | 96/1,200 = 8.00% | 3.20% |
| East pilot | 45/3,000 | 1.50% | 10% | 27/2,700 = 1.00% | 18/300 = 6.00% | 2.00% |
| West baseline | 120/3,000 | 4.00% | 40% | 36/1,800 = 2.00% | 84/1,200 = 7.00% | 3.00% |
| West pilot | 59/3,000 | 1.97% | 10% | 40/2,700 = 1.48% | 19/300 = 6.33% | 2.45% |

The shared pause in complex-account shipments materially improved both lines' aggregate mix. East's raw improvement is 2.90 percentage points, but its improvement at a common 80/20 mix is only **1.20 points**. Both East strata improved, so mix does not explain everything. West improved by **0.548 points** at the same mix without a checker. Subtracting West's change gives a **0.652-point comparison-adjusted East improvement**: `(3.20 − 2.00) − (3.00 − 2.45185)`.

This contrast is suggestive, not a causal estimate established by the design. East volunteered, had worse baseline complex quality, and was not randomized. Both lines received a clearer template on June 12, whose independent effect is unknown. A before/after comparison credits the checker with that shared improvement; the adjusted comparison assumes the shared change would have affected East similarly to West. Three observed baseline shifts cannot establish parallel trends, and regression toward the mean or different template benefits remain plausible. Pilot complex outcomes are only 18 and 19 errors in 300 orders per line; the apparent advantage within complex orders is especially uncertain. The adjusted complex improvement is 1.33 points, versus 0.48 for standard orders, but that is not proof that complex-only verification is the best deployment.

June 26 contributes **400 pending orders per line, zero mature orders**. It supplies no seven-day quality estimate. Dividing East's 45 errors by 3,400 would incorrectly report 1.32%. The 400-order shorter shift must also remain separate from full-shift capacity evidence. Its immediate dispatch data are usable: East 4/400 late (1.00%), West 2/400 (0.50%); paid hours were 31 and 28. Including it gives pilot dispatch rates of 63/3,400 = 1.85% and 24/3,400 = 0.71%, respectively, but does not remove East's full-shift service problem. Station catches cannot repair this uncertainty: compulsory recording started June 12 on both lines, and caught issues can be fixed before shipping. They are neither comparable before/after outcomes nor extra customer errors.

## Labor and dispatch constrain the choice

Labor below is summed once per line-date from `shift_operations.csv`, not duplicated across order bands. Overtime and training are already included in productive hours.

| Line and period, three full shifts | Paid hours | Training subset | Recurring hours | Overtime subset | Late orders / shipped |
|---|---:|---:|---:|---:|---:|
| East baseline | 207 | 0 | 207 | 9 | 15/3,000 = 0.50% |
| East pilot | 238 | 4 | 234 | 26 | 59/3,000 = 1.97% |
| West baseline | 205 | 0 | 205 | 7 | 17/3,000 = 0.57% |
| West pilot | 209 | 0 | 209 | 11 | 22/3,000 = 0.73% |

East used 78 recurring hours per 1,000 pilot orders even after training is removed. All three pilot dates had the same recurring total; lateness remained 21 and 20 orders on the two nontraining dates. The concern therefore cannot be dismissed as the first training shift. East overtime also rose substantially, a workload signal even though it must not be added to paid hours again.

| Proportional planning scenario | Hours for 1,200 orders | Margin below 84-hour cap |
|---|---:|---:|
| East, continuing pilot pace | 93.6 | −9.6 |
| West, current pace | 83.6 | 0.4 |
| East, historical ordinary-packing pace | 82.8 | 1.2 |

At the pilot pace, East's 84 hours support about **1,077 orders per shift**, or **21,538 over twenty shifts**, about 2,462 short of plan. Continuing at 1,200 would require 1,872 period hours against 1,680 allowed. It would need about a **10.3% reduction in hours per order**, or **11.4% increase in orders per hour**, simply to fit the cap. No measured redesign delivers that gain. West's current plan already nearly consumes its allowance; staff transfers are prohibited, as is an extra station. Up to four separately funded training hours for a new line do not increase ongoing capacity.

These are proportional scenarios, not validated capacity curves. Labor is not recorded by order band, and the planned complex share is 20%, double the pilot's 10%. Subgroup quality can be standardized, but subgroup labor cannot be identified from these whole-line totals. The historical East fallback had 40% complex work and a different template, so its 82.8-hour projection is evidence of plausibility, not a guarantee at 1,200. West's 0.4-hour margin is also too small to treat as resilience to variation.

At unchanged observed full-shift late rates, East would have about **472** late orders and West **176** over the plan. Combined that is **648/48,000 = 1.35%**, above the site's 1% promise (480 orders). This is a workload extrapolation, not a forecast model; it shows that even the observed rates fail the site commitment. Report lateness separately: no monetary value was authorized.

## Quality economics are favorable scenarios, not permission to exceed capacity

The comparison is for **24,000 East orders at 80/20 mix**. Benefits value an avoided downstream error at $65, and incremental recurring hours at $28. Every row pairs its quality and labor baseline consistently. All assume the estimated rate changes and average labor intensity transfer to that workload.

| Baseline for East trial | Estimated fewer errors | Avoidable-cost benefit | Extra recurring hours | Labor cost | Benefit less labor |
|---|---:|---:|---:|---:|---:|
| East before/after, descriptive | 288.0 | $18,720 | 216 | $6,048 | $12,672 |
| East change minus West change | 156.4 | $10,169 | 184 | $5,152 | $5,017 |
| Current East versus current West | 108.4 | $7,049 | 200 | $5,600 | $1,449 |

For example, adjusted incremental labor is `[(234 − 207) − (209 − 205)] / 3,000 × 24,000 = 184 hours`. The adjusted quality benefit is `0.00651852 × 24,000 × $65`. The raw before/after scenario includes shared changes; the current-line scenario ignores East's worse baseline. Neither is a proven counterfactual. Even the adjusted labor estimate may reflect mix-sensitive line differences, since the packet supplies no band-specific labor rates.

The adjusted case breaks even at about **79.3 avoided errors**, a **0.330-point** reduction, roughly half its estimated 0.652-point benefit. If there is no incremental quality effect, it instead costs $5,152 in that scenario. There is no universal ROI hurdle here. East's four past training hours cost $112 at the supplied hourly rate but are one-off and sunk for the next-period decision; adding them would reduce the historical net, not recurring capacity. A new line's possible four-hour training would be separately funded and still would not establish feasible routine staffing.

At pilot stratum rates, East's planned 80/20 workload would produce about **480 downstream mispacks** and West's about **588**; neither should be projected using the lower pilot complex share. Stopping may forgo quality benefit: under the comparison-adjusted scenario, East without the check would have about **636** mispacks, around **156 more** than with it. This is an explicit quality tradeoff, not a measured prediction of rollback. Retaining the shared template may retain some improvement, but its effect is unknown.

## What happens next

Continue ordinary packing on both lines for the period, with East's universal trial stopped subject to Mara's approval. Use the existing funded crews, at most 84 hours each full shift, without borrowing West labor. Monitor the first **three full shifts** at the actual planned workload. The question is whether ordinary packing with the current template can sustain the volume and dispatch promise, and what quality is lost when universal verification ends.

Have Mara review actual volume, order mix, productive and overtime hours, and late orders after each of these shifts, with a formal operational review after shift three. Record those measures at line-date grain; retain quality counts by line, band, and shipment date. If 1,200 orders cannot be dispatched within the allowance, or late orders exceed 1% cumulatively, escalate the operational plan to Mara that day for a decision on commitments or workflow within her authority. Do not silently add labor, move work to West, or relaunch the infeasible universal check. No observed option in this packet guarantees both commitments if the fallback fails.

Review the first three shifts' downstream quality only after the third shift's complete seven-calendar-day window has elapsed (next extraction thereafter). Review June 26 at the first extract after its seven-day window closes, separately from full shifts. Continue rolling mature-cohort reviews through week four and close the final outcome review seven days after the last planned shipment. Compare mature rates by band and at common mix with contemporaneous West and the mature pilot; retain causal caution because stopping also is not randomized. Early dispatch results should guide operations while customer outcomes are pending; small early samples should not trigger a confident effectiveness conclusion.

A **complex-only check is a candidate for redesign, not the selected next-period default**. Its workload cannot be assumed to be 20% of the all-order check: fixed setup, interruptions, and harder orders may dominate. Before Mara considers a later bounded trial, require a schedule or observed time study showing the selective work fits the existing 84 hours at 1,200 orders and the planned mix without delaying dispatch. Measurement work must fit ordinary funded time; if no slack exists, do not launch it. Any approved future trial should specify selected orders, checker minutes including interruptions, an immediate stop on threatened cutoff/cap, and a three-full-shift operational review followed by the seven-day mature-outcome review. Until that feasibility condition is met, ordinary packing remains the recommendation. Expansion loses for the same capacity reason and because transferability to West is unmeasured; continuation as-is loses on service and labor despite its quality signal.

## Reproduce and inspect

From the task directory, run:

```sh
python3 deliverables/northbank/reproduce.py --sources input/sources > deliverables/northbank/calculations.json
```

The standard-library script reads the two original CSVs without modifying them. It validates keys, count bounds, table alignment, labor subsets, and the complete comparison windows, then emits [calculation aggregates and scenarios](calculations.json). Re-running replaces only the redirected output. `--help` describes invocation; invalid input raises an error and exits unsuccessfully. A relocated copy can use an absolute `--sources` path and an appropriate output path.

All facts and assumptions come from the two CSVs, `measurement_notes.md` (snapshot June 29, 2026, 09:00 UTC), and `decision_context.md`. No outside operational assumptions were used. The calculations verify descriptive arithmetic, not causal attribution, mix-specific labor, an untested selective variant, future capacity, or statistical significance.
