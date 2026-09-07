# Northbank dispatch verification decision

**Recommendation:** Do not expand or continue the all-order East check as it stands. Narrow the next-period intervention on East to a bounded, measured complex-order check. Remove standard orders from the check, use a preassigned comparison among complex orders for the first five full shifts, and make continuation through the rest of the four-week period conditional on labor and dispatch guardrails plus the matured quality review.

This is a recommendation to site manager Mara Venn, not an instruction to alter production. The current all-order process has a favorable but uncertain quality signal. It has also coincided with an East dispatch miss rate above the 1% commitment and has not demonstrated capacity for the planned volume.

## Why this choice

At the next-period 80% standard / 20% complex mix, East's adjusted seven-day confirmed-mispack rate fell from 3.200% in baseline to 2.000% in the mature pilot dates. West, which received the common packing-list template but no checker, fell from 3.000% to 2.452%. The descriptive change-in-changes is therefore **-0.652 percentage points** in East's favor. Because East volunteered, began worse, and was not randomized, that difference suggests an incremental checker effect; it does not establish one.

The subgroup pattern supports narrowing, but weakly. The East-versus-West change-in-changes is -0.481 points for standard orders and -1.333 points for complex orders. Both normal-approximation 95% intervals include no difference (standard about -1.570 to +0.607 points; complex about -5.722 to +3.055 points). The small 300-order mature pilot denominator per line for complex orders makes its apparent advantage especially uncertain. A selective check has not been measured.

Capacity and dispatch make unchanged continuation unsuitable:

- On the three ordinary pilot shifts, East missed cutoff on 59 of 3,000 orders (1.967%), versus 0.500% at East baseline and 0.733% for West pilot. The June 26 low-volume shift is not used as a full-shift capacity observation; including its immediate dispatch result still leaves East pilot at 63/3,400, or 1.853%.
- East used 78.0 productive hours per ordinary pilot shift after removing the four one-off training hours, at 1,000 orders. This leaves only 6 hours under the 84-hour limit. A transparent proportional scaling gives 93.6 hours at 1,200 orders, above the limit. That is a planning stress case rather than a forecast because fixed and variable time are not separated.
- Expansion to West would expose a second line to an unresolved capacity and dispatch risk. The packet supplies no measured result for West with a checker.

Stopping immediately would protect dispatch capacity but abandon a plausible quality benefit concentrated in costly complex errors. A bounded complex-order comparison resolves whether a narrower scope retains benefit while fitting the hard operating limits.

## Next-period operating proposal

For the first five ordinary full shifts, make only East complex orders eligible. Before packing, assign eligible orders by a reproducible rule to checker or no-checker groups, such as a seeded random assignment or an alternating sequence fixed before outcomes are known. Record assignment without changing the outcome definitions. Keep ordinary staffing within **84 productive hours per shift** and do not borrow West staff. The separately funded training allowance may be used only within the manager's stated authorization.

Monitor productive hours and missed cutoff orders daily. If a shift would exceed 84 hours, do not add hours to preserve the trial. If cumulative East late dispatch exceeds 1%, pause the selective checker for subsequent orders and preserve the observations already collected for review. These guardrails prioritize feasibility and the commercial commitment; they are not claims that the checker caused every pilot delay.

The downstream review occurs seven calendar days after the fifth shift, once every enrolled order has a complete observation window. During that lag, continue the same bounded assignment only while both immediate guardrails hold. At review:

- continue the narrowed approach for the remaining shifts only if it stayed within 84 hours, cumulative late dispatch is at most 1%, and checked complex orders show a decision-relevant reduction in confirmed seven-day mispacks against their concurrent un-checked East comparison;
- otherwise stop the checker for the remaining shifts;
- do not expand to West during this four-week period without separate evidence that the same process fits West's capacity and dispatch commitment.

The owner should set the smallest quality effect worth the operating burden before assignment. The packet gives no universal mispack threshold, so this memo does not invent one. The five-shift stage is primarily a feasibility and direction check; it may remain underpowered for a precise quality estimate.

## Planning economics, kept separate from feasibility

Twenty East shifts at 1,200 orders imply 24,000 orders. Applying the descriptive adjusted estimates gives the following scenarios:

| Quality basis | Rate reduction | Avoided downstream mispacks | Avoidable cost at $65 each |
|---|---:|---:|---:|
| East raw before/after | 1.200 points | 288.0 | $18,720 |
| Concurrent-control change-in-changes | 0.652 points | 156.4 | about $10,169 |
| No incremental checker effect | 0 | 0 | $0 |

These are scenario values, not causal savings forecasts. The template change, mix change, nonrandom line selection, and sampling uncertainty prevent attributing the full before/after improvement to the checker.

For an all-order workload stress case, East's observed ongoing increase was 9.0 hours per 1,000-order shift; adjusting by West's 1.33-hour concurrent increase gives 7.67 incremental hours. If incremental hours scale directly to 1,200 orders, the respective 20-shift labor costs are **$6,048** (`9.0 × 1.2 × 20 × $28`) and about **$5,152** (`7.67 × 1.2 × 20 × $28`). The narrower variant has no observed labor requirement, so no savings or net return is claimed for it. Missed cutoff orders remain a separate operational effect because the manager supplied no authorized dollar value.

## Evidence boundaries

The mature cohort counts, adjusted rates, ordinary-shift labor, and dispatch rates are established by the packet. The checker’s incremental quality effect, causal role in delays, proportional hour scaling, and superiority for complex orders are suggestions. Capacity and effectiveness of a selective complex-only process are unknown and are the purpose of the bounded comparison.

June 26 shipments have zero mature orders because their seven-day windows were open at extraction; they are excluded from downstream quality rates. Station catches are not combined with confirmed mispacks and are not used as a before/after outcome because required capture began June 12. The detailed arithmetic is in [measurement-basis.md](measurement-basis.md) and can be regenerated with the bundled skill script.
