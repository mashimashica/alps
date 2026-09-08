# Northbank dispatch verification decision

## Recommendation

**Narrow East verification to complex orders for a bounded five-full-shift measurement period; do not continue the all-order check and do not expand to West.** Start the narrowed period only if the shift plan fits within 84 productive hours without West support. If that cannot be shown before the first shift, stop the checker for this operating period. Suspend the narrowed check on any shift forecast to exceed 84 hours; if cumulative cutoff misses exceed 1% during the five shifts, stop after the current safely packable work and return to the packing-list process alone.

After the fifth full shift, stop the checker while its final seven-day customer outcome window matures. Review within one working day after maturity. Until that review, both lines retain the shared packing-list template and normal recording; this recommendation itself does not change production.

## Why this is the usable choice

The quality result is promising but does not support all-order continuation under the next-period commitments. At the planned 80% standard / 20% complex mix, East's mature downstream mispack rate fell from 3.20% to 2.00%. West, which received the new packing-list template but no checker, fell from 3.00% to 2.45%. The resulting difference-in-differences is a 0.65 percentage-point improvement for East. This suggests an incremental checker benefit, but does not establish it: assignment was voluntary, East started worse, the template changed concurrently, and only 300 mature complex orders per line are available in the pilot period.

The current all-order check conflicts with the dispatch promise and has no demonstrated capacity at next-period volume. On the three comparable ordinary pilot shifts, East missed cutoff on 59 of 3,000 orders (1.97%), versus 22 of 3,000 (0.73%) on West and 15 of 3,000 (0.50%) in East's baseline. Excluding four one-off training hours, East used 78 productive hours per 1,000-order shift. Its observed throughput was 12.82 orders/hour; delivering 1,200 orders within 84 hours requires 14.29. A proportional sensitivity produces 93.6 hours, above the cap. That sensitivity is not a forecast, but there is no observed basis for claiming the all-order check fits.

Complex orders are the bounded scope because they carry the highest observed downstream risk: East's mature rates were 8.00% at baseline and 6.00% in the pilot, compared with 2.00% and 1.00% for standard orders. Selective checking is untested, so its labor use, dispatch effect, and quality benefit remain unknown. The proposed five shifts measure those unknowns rather than treating savings or capacity as observed.

## Five-shift measurement and decision rule

Use the planned mix as the operating expectation: about 240 complex orders and 960 standard orders per 1,200-order shift, or about 1,200 checked complex orders across five shifts. Record checker hours separately within the unchanged productive-hours definition. Preserve shipment-date, line, and order-band cohort records. Compare East with concurrent West by band; do not use station catches as the quality outcome because their recording changed. Include every shipped order in dispatch performance, and include only mature orders in seven-day quality.

At review, continue complex-only checking for the remaining 15 shifts only if all five shifts stayed at or below 84 productive hours, cumulative cutoff misses stayed at or below 1%, and the mature complex-order comparison still suggests a worthwhile quality advantage after considering concurrent West. Otherwise stop it. Do not expand from this test: expansion would need its own capacity case and evidence.

This rule makes capacity and the commercial promise hard gates. The manager must judge whether the size and uncertainty of the mature quality contrast justify the measured checker hours; the packet supplies no universal quality threshold or dollar value for late dispatch.

## Planning economics and limits

Across 24,000 planned East orders, applying the full 1.20-point East before/after change gives a scenario of 288 fewer mispacks, worth $18,720 at the authorized $65 each. Applying the 0.65-point difference-in-differences gives about 156 fewer and $10,169. These are transparent scenarios, not causally established savings. They use the planned mix and volume; actual volume and mix may differ.

Current all-order labor cannot be priced credibly for the next period because fixed versus volume-dependent work is unknown. Selective-check labor is wholly unmeasured. Price its measured additional hours at $28 during the review; keep the four already observed training hours separate and do not value missed cutoffs in dollars.

The full arithmetic and exclusions are in `decision-basis.md`; the included skill script reproduces them from the unchanged source files.
