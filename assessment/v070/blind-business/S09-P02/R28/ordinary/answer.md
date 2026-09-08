# Decision memo — Cedar Quay packing check

**To:** Iona Bell, site manager  
**Decision horizon:** Next 20 full shifts  
**Recommendation:** **Expand** the second-person check to every order on Ridge while continuing it on every Harbor order, as a bounded 20-shift operating period with the staffing and service gates below. Iona retains the decision and operating authority; this memo does not change operations.

## Why expand

Across the three mature ordinary full shifts in each period, Harbor's confirmed seven-day downstream mispack rate fell from **63/2,400 (2.625%)** to **30/2,400 (1.250%)**, a 1.375 percentage-point reduction. Ridge, which did not check, moved from **63/2,400 (2.625%)** to **60/2,400 (2.500%)**, a 0.125-point reduction. The comparator-adjusted change is therefore **-1.250 percentage points**, or 30 fewer mispacks per 2,400 orders. The planned 75% standard / 25% complex mix matches every eligible observed full shift, so mix standardization does not change these rates.

The direction holds in both bands. Harbor standard orders moved from 1.500% to 0.667%, versus no change at Ridge, for a comparator-adjusted reduction of 0.833 points. Harbor complex orders moved from 6.000% to 3.000%, versus Ridge's 6.000% to 5.500%, for a comparator-adjusted reduction of 2.500 points. This supports checking both bands. A complex-only version has not been measured, and the packet has no band-specific labor, so narrowing now would claim savings and capacity that cannot be identified.

Station catches are supporting process evidence, not downstream failures: Harbor recorded **38/2,400 (1.583%)** on mature pilot full shifts versus **13/2,400 (0.542%)** at baseline. Including the short July 31 shift gives 43/2,720 (1.581%). These catches are not added to confirmed mispacks or priced.

This evidence is descriptive rather than causal. Harbor volunteered, assignment was not randomized, and there are only three mature full shifts per period. The unchanged definitions, crews, workload mix, and contemporaneous Ridge comparison improve comparability but do not prove the checker caused the change.

## Workload, staffing, and dispatch

After removing only Harbor's documented three introductory training hours, Harbor used **195 recurring productive hours over three pilot full shifts: 65 hours per shift, or 0.08125 hour/order**. Ridge's contemporaneous no-check figure was **62 hours, or 0.07750 hour/order**. Harbor also recorded 15 overtime hours over those shifts, **5 per shift**, versus 2 per shift at Harbor baseline and Ridge pilot. The checked plan therefore assumes an incremental **3 productive hours per line-shift** and continued availability of the required overtime pattern.

At 800 orders, the checked projection is **65 hours per line-shift**, within the 68-hour hard limit but leaving only **3 hours** of headroom. Linear capacity at the same mix is floor(68 / 0.08125) = **836 orders**; the contemporary no-check equivalent is 877. This makes the 800-order plan feasible, but the margin is thin.

Before Ridge starts, Iona should verify that each line's roster can supply a 65-hour recurring plan, including expected overtime, without borrowing staff or exceeding 68 hours. Schedule Ridge's permitted training of up to three hours before the period with its separate funding. If that verification fails, keep Harbor checking within its cap and defer Ridge rather than launch an infeasible expansion.

Dispatch remained inside the commercial commitment in the observed data. On pilot full shifts, each line had **13 late orders out of 2,400 (0.542%)**; Harbor was 15/2,720 (0.551%) and Ridge 14/2,720 (0.515%) when the short July 31 shift is included. Applying the full-shift rate to 16,000 planned orders gives **86.7 late orders per line**, below the maximum 160, but this is a conditional projection. There is no authorized price for late dispatch, so it is not included in the cost case.

## Twenty-shift economics

For each checked line, the conservative planning counterfactual is Ridge's contemporaneous no-check rate of 2.500%, against Harbor's observed checked rate of 1.250%. Across 16,000 orders, that is **200 fewer errors**, **$9,600 gross avoided cost**, **60 incremental recurring hours costing $1,920**, and **$7,680 conditional net benefit per line**. For the expansion decision itself, Ridge's marginal conditional net is **$7,584 after its $96 maximum startup cost**. Across both lines, the conditional recurring net is **$15,360**; after pricing Ridge's startup separately, it is **$15,264**.

The favorable raw Harbor pre/post case uses 2.625% as the counterfactual. It gives 220 avoided errors per line, $10,560 gross, and $8,640 net per line; the marginal Ridge figure is **$8,544 after startup**, and across both lines the net is $17,280, or **$17,184 after Ridge startup**. These are scenarios, not proven savings: they assume Harbor's checked rate, incremental hours, and effect transfer to Ridge and persist for 20 shifts.

Break-even is low relative to the observed gap: **(3 hours × $32) / $48 = 2 avoided errors per line-shift**, equal to a **0.250 percentage-point** improvement at 800 orders. Favorable economics do not override the hours or dispatch limits.

## Operating scope and review gates

- **Scope:** Check every standard and complex order on both lines for the next 20 full shifts. Do not treat July 31 as a capacity test.
- **Staffing ceiling:** Plan 65 recurring productive hours per line-shift; 68 is a hard maximum. Do not borrow staff across lines. Keep Ridge's startup training outside the recurring period budget.
- **Daily service gate:** Record shipped orders, productive, overtime and training hours, station catches, and late dispatches at their native grains. If a line cannot complete the planned work within 68 hours, or its cumulative late-dispatch rate exceeds 1%, Iona should review before the next shift and pause the Ridge expansion first if its added check is contributing. Harbor should continue only while it independently meets the same limits.
- **Outcome measurement:** For every date, line, and band, retain shipped orders and report confirmed mispacks only after the complete seven-calendar-day window. Never count an immature cohort as zero and never add station catches to downstream mispacks.
- **Interim review:** Iona reviews after the first 10 full-shift cohorts have matured, seven calendar days after shift 10. Continue both lines through the review only while the staffing and dispatch gates hold. The review asks whether Ridge reproduces a benefit greater than the 0.250-point economic break-even against its 2.500% no-check reference, while Harbor remains directionally consistent.
- **Final review:** Seven calendar days after shift 20, Iona decides whether to make Ridge permanent. Retain both lines only if each stayed within 68 hours and 1% late dispatch and the mature quality evidence remains above break-even. If Ridge does not reproduce that benefit, stop Ridge's check and retain Harbor subject to its own service results. If a permanent causal estimate is required, the next study must prespecify randomized checked and unchecked full shifts or another defensible contemporaneous control.

The reproducible calculation is in `deliverables/analyze.py`; running `python3 deliverables/analyze.py > deliverables/numerical_basis.md` regenerates the complete numerical basis from the unchanged CSV inputs using only the Python standard library.
