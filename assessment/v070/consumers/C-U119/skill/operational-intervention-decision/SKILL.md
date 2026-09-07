---
name: operational-intervention-decision
description: Make a manager-usable decision to continue, narrow, expand, or stop an operational intervention from a local measurement packet and operating context. Use when quality, cost, outcome maturity, workload, staffing limits, and delivery commitments must be assessed together; produce a reproducible numerical basis and a bounded recommendation without taking live operational actions.
---

# Operational intervention decision

Use the supplied packet as the authority for definitions, objectives, costs, and permissions. Read measurement notes and decision context before calculating. Do not invent a universal success threshold, monetary value, or causal effect. Ask for missing decision-critical inputs only after completing useful analysis with what is available.

## Establish the decision and valid comparisons

1. Identify the owner, decision horizon, available choices, planned workload and mix, hard staffing or capacity limits, and customer commitments. Distinguish an actionable recommendation from authority to change operations. Do not contact people, spend money, change staffing, or alter records without separate authorization.
2. Map each table's unit of observation, unique key, denominators, inclusion rules, outcome window, and recording changes. Check duplicate keys, missing cohorts, nonnegative counts, numerator/denominator consistency, and reconciliation across tables. Aggregate each table at its own grain before joining: line-level labor must not be repeated across order categories. Identify labor subsets such as overtime and training so they are not added twice.
3. Separate fully observed outcomes from immature cohorts. Use eligible mature exposure for delayed-outcome rates; a placeholder zero is not a favorable outcome. Immediate operational outcomes can use shipped exposure. Retain recent short or unusual shifts as separate context, not matched full-shift evidence. Do not combine preventive process catches with downstream harm, especially across recording changes.
4. Establish comparable baseline and intervention windows. Describe selection, shared changes, demand shifts, and any unmatched conditions. Separate aggregate change, within-category change, and composition change. Calculate pooled rates from counts rather than averaging percentages. Show counts alongside percentages.

## Build a reviewable numerical basis

Use an existing local calculation tool or a small deterministic script as appropriate. Preserve inputs. Keep the formulas, input paths, inclusion rules, assumptions, invocation, and resulting tables together so another operator can reproduce the results. Document dependencies and fail clearly on malformed inputs. Calculations must distinguish observed quantities from forecasts and assumptions.

For each relevant group and period, compute delayed-outcome rates, operational outcome rates, output per labor hour, and labor per order. Show actual paid hours and, if justified, a separate ongoing estimate excluding explicitly one-off training. Routine intervention labor remains included.

When mix changes, compute category rates and apply common weights: `standardized_rate = sum(weight × category_rate)`. Choose weights that answer the decision (usually next-period demand); optionally also show a historical common mix. Missing category rates require an explicit gap or sensitivity, never an invented zero.

Where a credible comparison group exists, calculate its concurrent change on the same weights. An illustrative difference in changes is `(treated_after − treated_before) − (comparison_after − comparison_before)`. Explain the assumption that the treated group would otherwise have changed similarly. Nonrandom participation, baseline imbalance, small samples, and shared interventions can invalidate causal interpretation; a comparator is context, not proof. Describe the uncertainty that matters to the choice without manufacturing precision or independence assumptions.

## Convert evidence into a feasible operating choice

Project each materially different option onto the same planned volume, mix, horizon, and baseline. Show expected outcome counts, avoidable costs, incremental ongoing labor costs, and separate one-off costs. Explicitly name the counterfactual. Do not credit every before/after improvement to the intervention. Show a plausible sensitivity or break-even effect where attribution can change the economic conclusion. Keep unpriced service outcomes separate from money.

Translate observed labor intensity into hours required for planned volume and output possible at the authorized hours. Label linear scaling and unmeasured mix effects as assumptions; aggregate labor data do not identify category-specific workload. A budget or dispatch limit is a feasibility constraint even when expected monetary value is positive. Check the actual level of the service promise (site, line, or customer), and expose line-level problems that a site average can hide.

Compare continuing, narrowing, expanding, and stopping as relevant. Never label an untested selective intervention's capacity or savings as measured. Prefer a usable current decision with explicit conditions over deferring everything for more data. If no option is proven feasible, state this and recommend a conservative interim option with the unresolved obligation clearly assigned to the owner.

For bounded follow-up, specify scope, authorized resource ceiling, near-term review date or shift number, mature-outcome readout date, decision-relevant question, observations needed, service and resource guardrails, and what happens if conditions fail or results remain inconclusive. Account for outcome lag: operational monitoring can be immediate while quality evidence must wait. Choose proportional evidence collection; do not promise statistical certainty from a short test.

## Deliver and check

Deliver a concise decision note with the chosen action, why alternatives are unsuitable now, workload and economic implications, evidence limitations, and executable review conditions. Accompany it with local inspectable calculations and a documented reproduction command. Keep packet-specific results outside this reusable Skill.

Before handing off, reconcile published figures to the calculation output, verify units and signs, ensure forecasts are labeled, confirm the recommendation respects all stated constraints, and identify remaining material uncertainty. Report only checks actually run and their limits. A valid Skill format alone does not validate a business decision.
