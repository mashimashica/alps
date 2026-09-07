---
name: operational-intervention-decision
description: Evaluate whether to continue, narrow, expand, or stop a trial operational intervention using a local measurement packet, operating constraints, cohort maturity, capacity, costs, and nonrandomized comparisons. Use when a decision owner needs an actionable next-period recommendation rather than a dashboard or a single-metric pass/fail.
---

# Operational intervention decision

Turn the supplied packet into a decision the named owner can execute within stated authority. Treat the packet as authoritative for definitions and local assumptions; do not invent thresholds, prices, capacity, causal effects, or permissions.

## Establish the decision frame

Identify the available choices, decision horizon, owner priorities, hard limits, planned workload and mix, and what the owner may actually authorize. Record material missing inputs. If the packet supports only a conditional choice, make the condition observable and say what happens until it is resolved.

## Build comparable measures

Read measurement notes before calculating. Preserve units, denominators, cohort windows, subsets, and table grain.

- Exclude immature cohorts from downstream outcome rates; report their shipped volume separately.
- Never interpret unavailable outcomes as zero.
- Do not add upstream catches to downstream failures or compare a measure across a recording change as though it were stable.
- Avoid double-counting line-level measures after joining them to lower-grain rows.
- Separate one-off training from ongoing labor when the packet distinguishes them, while retaining training in any total that asks for all productive hours.

Show numerator, denominator, rate, period, unit, and exclusions for each decision metric. Use `scripts/analyze_packet.py` when the packet has the documented cohort and shift schemas; run `--help` for required arguments. Retain its output with the decision so another reviewer can reproduce the arithmetic.

## Handle nonrandomized evidence

Compare like periods, lines, and order bands. Report both raw and planned-mix-standardized quality rates when mix changed. A contemporaneous comparison or difference-in-differences can reduce some shared-period bias, but label it as suggestive when assignment was not randomized, baseline levels differed, or other changes coincided.

Use calibrated language:

- **Establishes:** directly calculated descriptive facts under stable definitions.
- **Suggests:** associations, adjusted contrasts, and extrapolations that depend on assumptions.
- **Unknown:** unmeasured variants, causal attribution, or future performance outside observed workload.

Do not convert an association into “errors prevented.” For planning scenarios, name the reference rate and workload, show the formula, and label the result as an estimate rather than realized savings.

## Test feasibility and consequences

Evaluate quality, labor, throughput, dispatch/service performance, and cost separately. Apply hard constraints before recommending expansion. Compare observed throughput with required throughput (`planned orders / hour cap`) and state when proportional scaling is only a sensitivity, especially if observed shifts differ from planned volume.

For costs, separate gross avoidable downstream cost from incremental labor cost and keep one-off costs distinct. Do not monetize an outcome without an authorized value. Make every cost scenario's baseline, workload, and causal assumption visible.

Do not treat a selective or expanded version as proven if only the original scope was observed. If recommending a bounded variant, specify its scope, staffing gate, measurement definitions, review date or maturity point, decision question, and stop/continue rules.

## Write the recommendation

Lead with one of: continue, narrow, expand, or stop. State conditions immediately. Then present:

1. the evidence that drives the choice;
2. what is descriptive versus suggestive or unknown;
3. expected next-period workload, capacity, dispatch, quality, and cost implications;
4. the bounded follow-up, if needed, including interim action and escalation triggers.

The recommendation is decision support, not authority to change live operations. Do not contact staff, modify records, commit spend, or activate an intervention unless separately authorized.
