# Decision memo — Alder packing check, next 20 full shifts

**Recommendation: stop Alder's all-order second-person check for the next 20 full shifts, and do not expand it to Birch.** Run both lines without a dedicated checker. This is an interim operating decision for the stated horizon; Nessa retains the actual decision.

The quality records do not show that the measured check improves downstream mispacks, and its observed workload does not fit the hard 102-hour-per-line-per-shift cap at the planned volume. Narrowing to selective checking is not an implementable substitute because its time, quality, and dispatch effects have not been measured.

## What the measurements support

Only cohorts with a complete seven-day window are in the downstream outcome rates. The four August 28 band rows represent 1,200 shipped orders but zero mature orders; their zero outcome counts are unavailable, not error-free results.

| Period | Line | Standard mispacks | Complex mispacks | All mature mispacks |
|---|---:|---:|---:|---:|
| Baseline | Alder | 42 / 2,100 = 2.00% | 90 / 1,500 = 6.00% | 132 / 3,600 = 3.67% |
| Baseline | Birch | 42 / 2,100 = 2.00% | 60 / 1,500 = 4.00% | 102 / 3,600 = 2.83% |
| Pilot | Alder, all-order check | 33 / 3,300 = 1.00% | 30 / 300 = 10.00% | 63 / 3,600 = 1.75% |
| Pilot | Birch, no checker | 33 / 3,300 = 1.00% | 18 / 300 = 6.00% | 51 / 3,600 = 1.42% |

Alder improved in the aggregate from 3.67% to 1.75%, but Birch also improved from 2.83% to 1.42% without a checker. Within the pilot, Alder was no better on standard orders and worse on complex orders. These observations do not identify a checker effect: allocation was not randomized, Alder began with worse complex performance, the complex-account pause sharply changed mix, and the August 14 packing-list and catch-recording changes affected both lines before the pilot. The 119 Alder station catches during the three full pilot shifts are process observations; they cannot be added to downstream mispacks or compared consistently with the pre-August-14 counts.

## Workload, dispatch, and cost

On the three 1,200-order pilot shifts, Alder used 275 productive hours, including five one-off training hours. Ongoing work was therefore 270 hours, or **90 hours per shift and 0.075 hour per order**. Holding that rate constant at 1,440 orders projects **108 hours per shift**, six hours above the hard cap. Across 20 shifts, that is 2,160 hours versus 2,040 allowed, an infeasible 120-hour excess.

For comparison, Alder's baseline was 246 hours for 3,600 orders. A constant-hours-per-order scenario projects 98.4 hours per 1,440-order shift, leaving 3.6 hours of headroom. The checked process would require 9.6 additional hours per shift at the planned volume, or 192 additional hours over the period. At the supplied **$34 per additional productive hour**, that is **$6,528**, but the hours cannot be authorized under the hard cap. Separate training funding does not solve the ongoing-hour excess.

Alder's late-dispatch rate on the three comparable full pilot shifts was **42 / 3,600 = 1.17%**, above the 1% commitment. At a constant rate, the next period would have 336 late orders against a maximum of 288. Including the unusually short, simple August 28 shift makes the full pilot record 42 / 4,200 = 1.00%, but that shift is not evidence of full-shift capacity. Alder's baseline full-shift rate was 21 / 3,600 = 0.58%.

The following quality figures are **planning scenarios, not causal forecasts**. Applying Alder's own baseline band rates to 28,800 planned orders at the stated 70% standard / 30% complex mix yields 921.6 expected mispacks and **$50,688** in avoidable error cost at $55 each. Applying Alder's checked-pilot band rates yields 1,065.6 mispacks and **$58,608**. The latter is $7,920 higher before the $6,528 additional-hour cost. The periods differ in template, account mix, and allocation, so this comparison supports no claim that checking causes harm; it does show that the supplied evidence cannot justify paying for or operationally accommodating the check.

## Follow-up and review point

For the first five full shifts, keep the interim decision above: no dedicated checker on either line, no added station, no transferred staff, and no more than 102 productive hours per line per shift. Record shipped orders, productive hours, and late dispatches by line as usual; after the five cohorts complete their seven-day windows, calculate mature mispacks by line and order band. Review then whether current-template, no-check operation actually stays within 102 hours and 1% late dispatch at the planned 1,440-order volume and 70/30 mix, and establish a current quality benchmark.

Revisit the stop decision only if a separately designed checking scope has measured ongoing time that fits the cap, measured downstream quality results after maturity, and dispatch performance at full planned volume. The current packet cannot establish those properties for selective checking or guarantee future no-check delivery.

## Reproduction

From the assigned task directory, run:

```bash
python3 work/reproduce.py
```

The script uses only the supplied CSV files, aggregates outcomes by period, line, and band, counts each line-level operations row once, excludes immature outcomes, and prints the stated planning scenarios.
