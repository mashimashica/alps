---
name: operational-intervention-decision
description: Evaluate whether to continue, narrow, expand, or stop an operational intervention using a local measurement packet, workload forecasts, and binding staffing and service commitments. Produce a manager-ready decision and reproducible numerical basis.
---

# Operational intervention decision

Use the supplied packet as the authority for definitions and operating assumptions. Read its measurement notes and decision context before calculating. Identify the decision owner, available choices, planning horizon, demand and mix, resource limits, service commitments, and authorized costs. Ask about missing information only when it blocks a material decision; otherwise label assumptions and give a conditional decision. Do not operate production systems, contact people, change records, or commit spending.

## Establish comparable evidence

1. Inventory sources and state each table's grain, keys, units, denominators, recording changes, and outcome window. Check missing/duplicate keys, impossible counts and coverage. Keep supplied files unchanged.
2. Separate mature outcome cohorts from still-open cohorts. Use eligible exposure for delayed outcomes; keep immediately observable service measures on their appropriate shipped denominator. Never treat unavailable outcomes as zero-risk observations.
3. Aggregate counts before dividing. Show headline outcomes alongside relevant strata and composition. Standardize to a common, decision-relevant mix using weighted stratum rates. Identify sparse strata and explain how composition changes affect aggregate comparisons.
4. Compare intervention change with a contemporaneous comparator where available. Show both changes and their difference; do not turn a nonrandomized comparison into proof of causality. Discuss shared process changes, selection, baseline imbalance, regression to the mean, short observation periods and plausible comparator contamination. Distinguish process catches from downstream failures, especially when recording changed.
5. Aggregate operations at their native grain before combining with outcome summaries. Never multiply shift labor by joining it to multiple product rows. Separate total, recurring and one-off labor; overtime or training that is already included must not be added again. Separate matched full shifts from short or otherwise atypical observations.

## Translate evidence into a decision

Project outcomes at the expected next-period volume and mix; label transport assumptions. Calculate recurring labor per unit, needed hours and implied capacity under the actual labor cap. When labor is not stratified by mix, explicitly state that linear projections cannot establish capacity at a different mix. Evaluate service commitments independently; do not monetize late dispatches without an authorized value.

Make the economic comparison's counterfactual explicit. Report gross avoidable-error value, incremental recurring labor cost and net value at the same workload and horizon. Where causality is uncertain, offer transparent scenarios (for example, own before/after, current comparator and comparator-adjusted change) and identify which assumptions they require. Calculate a break-even benefit when useful. Avoid invented precision or treating one favorable scenario as established savings. Include funded training separately from recurring limits.

Choose an actual next-period action among feasible options. Explain why alternatives lose on material dimensions. An unmeasured selective variant is a hypothesis, not demonstrated capacity or savings. If proposing bounded learning, specify scope, permitted staffing, exposure or time limit, service protections, mature-outcome review timing, question resolved and fallback action. A follow-up must not defer the whole operating decision or rely on unavailable resources. State what would change the recommendation.

## Deliver and verify

Write a concise manager-facing decision with evidence, numerical comparisons, constraints, assumptions and uncertainty. Provide a local reproducible basis using available commands, a spreadsheet with formulas, or a script; no new software dependency is required. Document invocation, source paths, cohort rules and formulas. Keep packet-specific calculations and conclusions outside this reusable Skill. Validate reported totals against source counts and check denominators, units, joins and reconciliation. Report checks actually run and limits; distinguish recommendations from actions taken.
