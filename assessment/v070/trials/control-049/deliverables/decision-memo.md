# Northbank next four-week decision

## Recommendation

Stop East's current all-order second-person check for the next four-week period and do not expand it to West. It produced a useful quality signal, but the current form misses the dispatch commitment and exceeds the labor ceiling. A narrower design should be reconsidered only through the bounded measurement below; its savings and capacity are unmeasured.

## Evidence

| Line / period | Mature | Mispacked | 7-day rate | Shipped | Late | Cutoff rate | Productive hours | Training |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| East baseline | 3,000 | 132 | 4.40% | 3,000 | 15 | 0.50% | 207 (69.0/shift) | 0 |
| East pilot (mature dates) | 3,000 | 45 | 1.50% | 3,000 | 59 | 1.97% | 238 (79.3/shift) | 4 |
| West baseline | 3,000 | 120 | 4.00% | 3,000 | 17 | 0.57% | 205 (68.3/shift) | 0 |
| West pilot (mature dates) | 3,000 | 59 | 1.97% | 3,000 | 22 | 0.73% | 209 (69.7/shift) | 0 |

East's mature rate is 1.50% versus 4.40% baseline (87 fewer per 3,000), but the shared June 12 packing-list template, changed mix, and non-random volunteer line prevent causal attribution. East's pilot cutoff rate over all pilot dates is 63/3,400 = 1.85%, above the 1% promise. Its 269 hours include four one-off training hours: 89.7/shift, or 88.3 ongoing, above the 84-hour cap. June 26 is low volume. The 400 immature orders on that date are excluded from quality; zero reported errors means unavailable maturity. Station catches are incomparable after mandatory recording began June 12.

At 20 planned shifts of 1,200 orders, mechanically applying East baseline and pilot rates gives about 845 versus 288 mispacks, or USD 36,205 at USD 65 each. This is a planning illustration, not an attributed or guaranteed saving. No cutoff dollar value is authorized, and no labor saving is claimed while the current form exceeds the cap. Apply USD 28/hour only to an authorized measured design.

## Bounded follow-up

If evidence for a narrower option is desired, run five ordinary full shifts on East with a pre-specified complex-order-only check, within 84 productive hours and without West staff. Record checker hours separately, shipped orders, late cutoffs, and seven-day mature mispacks by band. Review after the fifth shift plus maturity time. The question is whether the selective check can preserve meaningful complex-order improvement while meeting the 1% cutoff and 84-hour limits. Until review, do not claim its capacity or savings.

Run `python reproduce.py` from `deliverables/`; it reads the unchanged packet sources.
