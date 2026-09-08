# Reproducible calculation output

Command: `python3 deliverables/analyze.py` (run from the consumer directory)

Inputs: `input/sources/shipment_cohorts.csv`, `input/sources/shift_operations.csv`.
Definitions and assumptions come from the supplied measurement notes and decision context.

## Validation

- Unique keys: 28 cohort rows; 14 operations rows
- Nonnegative counts and numerator/denominator/labor-subset consistency: passed
- Cohort and operations date/line coverage and late-dispatch denominators: passed
- Immature cohorts excluded from quality rates: 4 rows

## Mature seven-day quality

Rates pool counts within each band. Standardized rate = 70% × standard rate + 30% × complex rate.

| Period | Line | Standard | Complex | Pooled observed mix | Planned-mix standardized |
|---|---|---:|---:|---:|---:|
| baseline | Alder | 42/2100 (2.000%) | 90/1500 (6.000%) | 132/3600 (3.667%) | 3.200% |
| baseline | Birch | 42/2100 (2.000%) | 60/1500 (4.000%) | 102/3600 (2.833%) | 2.600% |
| pilot | Alder | 33/3300 (1.000%) | 30/300 (10.000%) | 63/3600 (1.750%) | 3.700% |
| pilot | Birch | 33/3300 (1.000%) | 18/300 (6.000%) | 51/3600 (1.417%) | 2.500% |

Alder planned-mix change: 0.500%. Birch concurrent change: -0.100%. 
Illustrative difference in changes: 0.600%. Positive means a higher mispack rate for Alder relative to Birch's change.

## Full-shift operations

August 28 is excluded here because it was a short, unusually simple 600-order shift.
Productive hours count once per date/line; overtime and training are subsets, not additions.

| Period | Line | Orders | Productive hours | Training subset | Orders/hour | Late dispatch |
|---|---|---:|---:|---:|---:|---:|
| baseline | Alder | 3600 | 246.0 | 0.0 | 14.63 | 21/3600 (0.583%) |
| baseline | Birch | 3600 | 240.0 | 0.0 | 15.00 | 18/3600 (0.500%) |
| pilot | Alder | 3600 | 275.0 | 5.0 | 13.09 | 42/3600 (1.167%) |
| pilot | Birch | 3600 | 246.0 | 0.0 | 14.63 | 18/3600 (0.500%) |

## Twenty-shift planning scenarios

Linear hours/order scaling is an assumption; the records do not identify band-specific labor.
The stop scenario uses Alder baseline planned-mix quality and baseline hours/order. The all-order scenario uses Alder pilot planned-mix quality and pilot ongoing hours/order, excluding the five one-off training hours.

| Item | Stop all-order check | Continue all-order check |
|---|---:|---:|
| Quality rate assumption | 3.200% | 3.700% |
| Expected mispacked orders / 28,800 | 921.6 | 1,065.6 |
| Expected mispack cost | $50,688.0 | $58,608.0 |
| Productive hours / line / shift | 98.4 | 108.0 |
| Margin to 102-hour cap | 3.6 | -6.0 |
| Output possible at 102 hours | 1,493 orders | 1,360 orders |
| Late-dispatch rate assumption | 0.583% | 1.167% |
| Expected late dispatches / 28,800 | 168.0 | 336.0 |

All-order checking adds 9.6 ongoing hours/shift (192.0 over 20 shifts), costing $6,528.0 at $34/hour. It is 6.0 hours/shift above the hard cap and its projected output is 80 orders/shift short.
Against the primary stop baseline, continuing produces 144.0 more expected mispacks and costs $14,448.0 more including incremental labor.
Using Birch's concurrent planned-mix change as context gives a 3.100% stop counterfactual, 892.8 expected mispacks, and $16,032.0 higher total cost for continuing. This is not a causal estimate.
Even if capacity were available, the added labor requires at least 118.7 avoided mispacks, or a 0.412% absolute rate reduction, to break even. The observed planned-mix direction did not meet that condition.
At the measured full-shift late rate, checking projects 336.0 late orders (1.167%), above the 1% maximum of 288; stopping projects 168.0 (0.583%).

## Scope sensitivity (unmeasured)

The baseline-hours scenario leaves 3.6 hours/shift. If Alder's observed incremental checker time (0.006667 hours per checked order) scaled linearly to a selective scope, the cap would allow about 540 checked orders/shift. A complex-only scope is 432 orders and would project 101.3 hours. This is only a sensitivity: selective checking time, quality, and dispatch were not measured, and band-specific labor is unavailable.

## Attribution limits

Participation was not randomized; Alder and Birch differed at baseline; the complex mix changed sharply; and both lines simultaneously received the packing-list template and mandatory catch recording. The comparator assumes Alder would otherwise have changed like Birch. Station catches are excluded because recording changed and they are not downstream harm. Forecast counts are expectations, not observed next-period results.
