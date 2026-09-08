# Decision for Iona Bell

## Recommendation

Continue the full second-person check on every Harbor order for the next 20 full shifts, and expand that same full check to every Ridge order. Schedule Ridge's authorized three training hours before the period from the separate training allocation. Plan each line at **65 recurring productive hours per 800-order shift**, enforce the **68-hour line cap**, and do not add a station or borrow staff.

Treat the Ridge expansion as a bounded 20-shift rollout because the effect has not been observed on Ridge and Harbor volunteered rather than being randomized. Keep both lines checking while results mature, subject to labor and dispatch protections. Review the first five Ridge checked shifts once all five cohorts have had their seven-calendar-day outcome windows, and review the full decision after the twentieth cohorts mature. The first review asks whether the Harbor result transports to Ridge; the final review asks whether the process should become standard on both lines.

The operating fallback is to stop the Ridge check and retain Harbor's full check if Ridge cannot run within 68 productive hours, its cumulative late-dispatch rate exceeds the 1% commitment, or its mature, mix-standardized mispack reduction versus its 2.50% pilot-period starting rate is below the **0.25 percentage-point economic break-even**. Apply the same capacity and dispatch protections to Harbor; if its check causes either limit to fail, suspend it on Harbor as well. These are management guardrails, not claims that the packet proves a threshold response.

## Evidence behind the decision

All comparison figures use the six matched ordinary full shifts and aggregate counts before division. Their 800-order workload and 75% standard / 25% complex mix match the plan.

The shipment table has 28 unique date/line/band cohort keys; the operations table has 14 unique date/line keys. Validation found no duplicate keys, negative or impossible outcome counts, or unmatched shift keys, and reconciled 12 line-level full shifts at 800 orders plus two short shifts at 320. Mispack rates use mature orders, catch rates use shipped orders, late-dispatch rates use shipped orders, and labor is summed once at its date/line grain. The notes report no missing rows or recording-definition changes.

| Line and period | Mature mispacks | Standard | Complex | Station catches | Recurring hours/shift | Late dispatch |
|---|---:|---:|---:|---:|---:|---:|
| Harbor baseline | 63/2,400 = 2.625% | 27/1,800 = 1.500% | 36/600 = 6.000% | 13/2,400 = 0.542% | 62 | 14/2,400 = 0.583% |
| Harbor checked | 30/2,400 = 1.250% | 12/1,800 = 0.667% | 18/600 = 3.000% | 38/2,400 = 1.583% | 65 | 13/2,400 = 0.542% |
| Ridge baseline | 63/2,400 = 2.625% | 27/1,800 = 1.500% | 36/600 = 6.000% | 12/2,400 = 0.500% | 62 | 14/2,400 = 0.583% |
| Ridge unchanged | 60/2,400 = 2.500% | 27/1,800 = 1.500% | 33/600 = 5.500% | 14/2,400 = 0.583% | 62 | 13/2,400 = 0.542% |

Harbor's downstream rate fell **1.375 percentage points**; Ridge's fell **0.125 points**. The difference in changes is therefore **1.250 points**, equal to 10 fewer mispacks per 800 orders. The planned mix equals the observed mix, so the 75/25 standardized rates equal the aggregate rates. The complex result rests on 600 mature orders per line-period, one third of the standard-band denominator, but both bands improved on Harbor.

Harbor's catches rose from 13 to 38 while its confirmed downstream mispacks fell from 63 to 30. Catch recording was unchanged, which is consistent with the check finding more issues before dispatch, but catches are process events and were not added to downstream errors.

July 31 is excluded from mature mispack rates and full-shift capacity because its outcome window was still open and it was a deliberate 320-order short shift. It remains eligible for immediate service reporting: across all pilot shipments, Harbor had **15/2,720 = 0.551%** late and Ridge **14/2,720 = 0.515%** late. No unavailable outcome was treated as zero.

## Workload, capacity, and service

Harbor used 198 productive hours in its three checked full shifts, including three one-off training hours. Recurring use was therefore **195 / 3 = 65 hours per shift**, up from 62. Overtime is already a subset of productive hours and was not added again. At the same 800-order workload and mix, extending that observed linear rate requires 65 hours per line per shift, leaving a three-hour buffer below the cap. Ridge capacity is a transport assumption; the packet does not demonstrate Ridge's checked labor directly.

At Harbor's checked full-shift late rate, each line would project to about **86.7 late orders out of 16,000 (0.542%)**, below the maximum 160 (1%). This is a planning projection, not a guarantee, and there is no authorized monetary value for lateness. Track productive hours and late orders by line after every shift rather than offsetting a service miss with quality savings.

## Twenty-shift economics

The recurring increment is three hours per shift, or **60 hours and $1,920 per line** over 20 shifts. The table holds workload at 16,000 orders per line and values an avoided downstream mispack at $48.

| Benefit assumption | Avoided mispacks/line | Gross avoidable value | Net after recurring labor |
|---|---:|---:|---:|
| Harbor own before/after: 1.375-point reduction | 220 | $10,560 | $8,640 |
| Current checked-Harbor versus Ridge gap: 1.250 points | 200 | $9,600 | $7,680 |
| Comparator-adjusted change: 1.250 points | 200 | $9,600 | $7,680 |
| No true benefit | 0 | $0 | -$1,920 |

Using the comparator-adjusted planning case on both lines gives 400 avoided mispacks, $19,200 gross value, $3,840 recurring labor cost, and **$15,360 recurring net value**. Ridge's three separately funded training hours cost **$96** at the stated labor rate, leaving **$15,264** after that one-off setup. Break-even is 40 avoided errors per line, or a 0.25-point rate reduction. These are expected-value scenarios, not proven realized savings.

The nonrandomized comparison cannot establish that checking caused the change. Selection, baseline dynamics, regression to the mean, the short three-shift windows, or contamination could contribute, although the packet reports unchanged crews, definitions, equipment, suppliers, incentives, and reporting. The no-benefit scenario shows the financial downside if the apparent effect does not transport.

Stopping loses a favorable observed quality result while saving only three recurring hours per shift. Continuing Harbor alone is feasible but forgoes an economically attractive Ridge opportunity. Narrowing to selected orders is not recommended because no selective version has been measured; it also risks excluding the complex band, where Harbor's absolute decline was largest.

## Reproducible basis

Run from the application directory:

```bash
python3 deliverables/analyze.py
```

The script reads `input/sources/shipment_cohorts.csv` and `input/sources/shift_operations.csv`, validates unique keys and count bounds, reconciles shipment and operations rows at the date/line grain, separates mature cohorts and full shifts, and prints all rates, changes, capacity calculations, scenarios, and break-even figures. The captured output is in `deliverables/analysis_output.txt`.

This document is a recommendation only. No operating change, message, purchase, or external action was performed; Iona retains the decision.
