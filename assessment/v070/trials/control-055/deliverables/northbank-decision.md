# Northbank dispatch verification decision

**Recommendation for the next four-week period:** narrow the East verification process to a bounded, randomized check of **up to 100 orders per full shift**, stratified as **50 standard and 50 complex orders when volume permits**. Do not continue the all-order East check and do not expand it to West. Keep the narrowed process only while East remains within 84 productive hours per shift and the cumulative late-dispatch rate is no more than 1%.

This is a recommendation to site manager Mara Venn, who retains the operating decision. It does not change production, staffing, records, or spending.

## Why this is the usable choice

The all-order trial has a promising quality association, but it is not feasible at the planned throughput on the evidence available. East's mature pilot mispack rate was 1.50% (45/3,000), down from 4.40% (132/3,000). Much of that crude decline reflects the shift from 40% complex orders in baseline to 10% in the mature pilot. At the planned 80% standard / 20% complex mix, East falls from 3.20% to 2.00%.

That improvement cannot all be assigned to the checker. The packing-list template changed on both lines, the large complex account paused, East volunteered, and there was no randomization. West's planned-mix rate also fell, from 3.00% to 2.452%. Applying West's 0.548 percentage-point improvement to East's baseline gives a descriptive no-check counterfactual of 2.652%; East's 2.00% pilot rate is 0.652 percentage points lower. This suggests an incremental checker benefit, but three mature pilot shifts and nonrandom assignment do not establish causation.

The immediate operating measures argue against an all-order continuation. Across the ordinary full pilot shifts, East missed cutoff on 59/3,000 orders (1.967%), above the 1% commercial promise and above West's 22/3,000 (0.733%). The June 26 partial shift was 4/400 late (1.00%), but it is not evidence of ordinary full-shift capacity.

East used 78 routine productive hours per 1,000-order pilot shift after removing four one-off training hours, versus 69 hours per 1,000-order baseline shift. If both base work and verification scale in proportion to the planned 1,200 orders, the all-order process needs 93.6 hours per shift, 9.6 hours above the 84-hour limit. Even the projected baseline workload is 82.8 hours, leaving only 1.2 hours. At the observed incremental rate of 0.009 hours per checked order, that headroom corresponds to about 133 checks; a 100-order ceiling leaves a small planning margin. This is a proportional planning estimate, not observed performance of a selective process.

## Four-week operating proposal

- Before each full shift, select up to 50 standard and 50 complex East orders by a reproducible random rule. Record assignment before packing outcome is known. Orders not selected receive the normal process. If either band has fewer than 50 eligible orders, do not backfill from the other band; preserving the strata makes the result interpretable.
- Use existing East staffing and stations. The separately funded allowance permits up to four one-off training hours before the period, but ongoing productive work must stay within 84 hours per shift. Do not borrow West staff.
- Stop assigning additional checks for a shift if the line forecast reaches 84 productive hours. Pause new verification assignments for later shifts if cumulative late dispatch exceeds 1% after the first five full shifts. Continue collecting already-defined downstream outcomes while paused.
- At the end of shift 5, review productive hours, overtime, checks completed, and late dispatch. If the hour and dispatch guardrails both hold, continue the same bounded scope; do not raise the ceiling during this period.
- After shift 10 plus seven calendar days, review mature checked versus randomly unselected orders within each band. This interim review can stop the narrowed process for clear harm or failed feasibility, but should not trigger expansion from a small favorable swing.
- Make the final continue, stop, or redesign decision after shift 20 plus seven calendar days, when every cohort has its complete outcome window. Compare checked and unselected orders within shipment date and band, then standardize to the planned 80/20 mix. Report station catches separately because their recording changed on June 12.

The follow-up resolves whether the second-person check itself reduces downstream errors at the intended mix, how its workload differs by band, and whether any benefit can coexist with the dispatch and labor limits. During the follow-up, East gets limited exposure to the promising intervention without committing to the infeasible all-order process.

## Planning economics

At 24,000 East orders over the period, using East's own mix-adjusted baseline implies 288 fewer downstream mispacks and USD 18,720 in gross avoidable cost if the 2.00% pilot rate held. Using the more conservative common-change counterfactual implies 156.44 fewer and USD 10,168.89 gross. A full all-order process would add a projected 216 labor hours, costing USD 6,048. Its net planning value would therefore range from USD 4,120.89 to USD 12,672, before any unpriced effect of late dispatch.

Those full-check economics do not override the 84-hour cap or the 1% dispatch promise. They also should not be attributed entirely to the checker. No savings estimate is claimed for the proposed selective process because its band-specific effect and actual workload have not been measured.

## Reproduction

From this trial directory, the following command reproduces the validation tables and planning arithmetic:

```bash
python3 deliverables/skills/operational-intervention-decision/scripts/analyze_packet.py \
  --shipments input/sources/shipment_cohorts.csv \
  --operations input/sources/shift_operations.csv \
  --baseline-label baseline \
  --pilot-label pilot \
  --treated-line East \
  --comparison-line West \
  --full-shift-dates 2026-06-01,2026-06-02,2026-06-03,2026-06-15,2026-06-16,2026-06-17 \
  --planned-mix standard=0.8,complex=0.2 \
  --planned-orders-per-shift 1200 \
  --planned-shifts 20 \
  --productive-hour-cap 84 \
  --hourly-cost 28 \
  --avoidable-event-cost 65
```

The command uses only Python's standard library and reads the supplied CSVs without modifying them.
