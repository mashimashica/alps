# Northbank next-period decision

## Decision

End East’s current second-person check of every order at the start of the next four-week period. Do not expand it to West. The all-order version is associated with better mature downstream quality, but its ordinary pilot shifts missed the dispatch commitment and leave no demonstrated capacity at the planned volume.

If Mara Venn wants to preserve evidence, replace it with a gated five-full-shift East test that checks complex orders only. This is a new, unmeasured variant: its savings and capacity are hypotheses, not observed results. Schedule up to four one-off training hours, keep ongoing productive labor at or below 84 hours per East full shift, use no West staff or additional station, and pause the test if either the hours limit or a 1% same-shift late-dispatch guardrail is breached. If the staged test is not approved, run the baseline process for the four weeks.

Review operations after the five shifts. Review mature downstream quality seven calendar days after the last test shipment, then decide whether to continue the narrow variant for the remaining shifts. Until that review, the baseline process is the fallback. Continue only if the test shows a quality improvement at the planned 80% standard / 20% complex mix while meeting the hours and dispatch guardrails; otherwise stop it. This review answers whether concentrating verification on the higher-risk complex band can retain useful quality signal without repeating the full-scope workload and cutoff failure.

## What the packet establishes

The baseline consists of three ordinary full shifts (June 1–3), and the mature pilot comparison consists of three ordinary full shifts (June 15–17). Each has 3,000 mature orders per line. June 26 has 400 orders per line with zero mature orders, so its downstream error count is unavailable; it is useful only as a separate low-volume operations observation.

| line / period | standard errors / mature | complex errors / mature | all mature errors / mature |
| --- | ---: | ---: | ---: |
| East baseline | 36 / 1,800 (2.000%) | 96 / 1,200 (8.000%) | 132 / 3,000 (4.400%) |
| East pilot | 27 / 2,700 (1.000%) | 18 / 300 (6.000%) | 45 / 3,000 (1.500%) |
| West baseline | 36 / 1,800 (2.000%) | 84 / 1,200 (7.000%) | 120 / 3,000 (4.000%) |
| West pilot | 40 / 2,700 (1.481%) | 19 / 300 (6.333%) | 59 / 3,000 (1.967%) |

East’s aggregate rate fell by 2.9 percentage points, but the order mix also moved from 60% standard / 40% complex in baseline to 90% / 10% in the pilot. Both lines also received a packing-list template on June 12, and East volunteered rather than being randomized. Station catches cannot be used as a before/after outcome because all catches became mandatory to record on June 12 and catches can be resolved before dispatch.

The ordinary-shift operations comparison is:

| line / period | productive hours | training hours | late dispatch orders / shipped |
| --- | ---: | ---: | ---: |
| East baseline | 207 | 0 | 15 / 3,000 (0.500%) |
| East pilot | 238 | 4 | 59 / 3,000 (1.967%) |
| West baseline | 205 | 0 | 17 / 3,000 (0.567%) |
| West pilot | 209 | 0 | 22 / 3,000 (0.733%) |

The East baseline productive-hour total is 68 + 69 + 70 = **207**; the reproduction script prints this exact total. East pilot total includes the four training hours. Routine East pilot hours are 78, 78, and 78, versus baseline 68, 69, and 70. East therefore used about nine more ongoing productive hours per 1,000-order full shift. The June 26 East row (31 hours, 4 late orders, 400 shipped) is not treated as a full-shift capacity benchmark.

East’s 1.967% ordinary-pilot late rate is above the site’s no-more-than-1% next-period promise. Combining both lines’ ordinary pilot shifts gives 81 late orders out of 6,000 (1.350%). There is no authorized dollar value for a missed cutoff, so this is reported as an operational constraint rather than folded into the cost estimate.

## Planned-mix interpretation and cost scenario

At the planned mix, standardizing each line’s within-band rates to 80% standard / 20% complex gives:

- East baseline: `0.80 × 2.000% + 0.20 × 8.000% = 3.200%`.
- East pilot: `0.80 × 1.000% + 0.20 × 6.000% = 2.000%`.
- West baseline: `0.80 × 2.000% + 0.20 × 7.000% = 3.000%`.
- West pilot: `0.80 × 1.481% + 0.20 × 6.333% = 2.452%`.

The East change is −1.200 percentage points and the concurrent West change is −0.548 points. Their difference is a **suggestive −0.652-point incremental contrast**, not a causal estimate: the template, account pause, volunteer assignment, and small pilot complex cell can all matter. A naïve East-only before/after projection would credit the checker with 1.2 points and is therefore too strong.

For visibility, if that adjusted contrast were used only as a planning scenario for 24,000 orders (20 shifts × 1,200), it implies 156.4 fewer mispacked orders × USD 65 = **USD 10,169** of avoidable quality cost. The observed routine-hour difference (9 hours × 20 shifts × USD 28) is **USD 5,040**. These figures leave an apparent USD 5,129 before any unpriced dispatch impact, and they do not establish that the all-order checker caused the contrast or that the complex-only variant will deliver it.

Capacity is the binding concern. The current East pilot used 78 routine hours for 1,000 orders. A simple linear planning scenario for 1,200 orders is 93.6 hours, above the 84-hour limit; this is a scenario rather than measured 1,200-order capacity, but the current data provide no feasible full-scope margin. Baseline East scales to 82.8 hours under the same simple scenario. The narrow variant must therefore prove its hours and cutoff behavior before any continuation.

## Reproduction

From the task directory, run:

```bash
python deliverables/northbank-decision/reproduce.py
```

The script reads the two supplied CSVs by default, excludes immature quality rows, aggregates operations once per line-date, prints within-band and planned-mix rates, and prints the scenario cost and capacity arithmetic. Alternate CSV paths can be supplied with `--shipment` and `--operations`. It does not write or alter source records.
