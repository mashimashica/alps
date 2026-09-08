---
name: operational-intervention-decision
description: Decide whether to continue, narrow, expand, or stop an operational intervention from a local measurement packet and operating context. Applies when quality outcomes, workload, capacity, cost, comparison limits, and near-term commitments must be weighed together.
---

# Operational intervention decision

Turn a local measurement packet into an actionable operating decision. The output must be a recommendation the decision owner can use for the stated next period, with reviewable arithmetic and explicit evidence limits.

## Establish the packet

- Treat the supplied context and measurement notes as the authority for definitions, prices, limits, dates, and launch conditions. Do not replace missing assumptions with web research or generic benchmarks.
- Inspect every supplied table before calculating. State the unit of observation and the join key. If an operations row is at line-date level, join it once to the line-date total; never repeat it for each segment.
- Separate the intervention from other changes in timing, mix, tooling, recording, staffing, or customer population. Mark which comparisons are descriptive and which are a plausible counterfactual.
- Identify the decision owner, next-period volume and mix, hard constraints, outcome thresholds or promises, and any authorized training or one-off capacity.

## Make outcomes comparable

- Use the packet’s declared outcome as the primary quality measure. Keep process observations (for example, catches) separate when their recording changed or they can be resolved before the outcome.
- Calculate each rate as qualifying outcome events divided by qualifying observations. Exclude immature observations from the denominator; a zero paired with no mature observations is unavailable data, not a zero rate.
- Reconcile shipment and operations totals by date and line. Report both counts and rates, and retain segment or order-band detail whenever mix can move the aggregate.
- Standardize to the next-period mix when useful. Show the formula, inputs, and whether the result is observed, a planning estimate, or a scenario.
- Use a concurrent comparison or difference-in-differences only as an adjustment, not proof of causality, when allocation was not randomized. Discuss pre-existing differences, common changes, small cells, and follow-up maturity.

## Test operational feasibility

- Compare ordinary full-shift observations with short or exceptional shifts. Do not use a low-volume or incomplete shift as evidence of full-shift capacity or mature quality.
- Calculate intervention labor separately from training and overtime. Remember that overtime is a subset of productive hours unless the packet says otherwise.
- Test the planned volume and mix against the authorized per-shift hours, stations, and staffing. If scaling observed hours is only a planning scenario, label it as such; do not present it as measured capacity.
- Evaluate the dispatch or service commitment separately from quality. Show the observed late or missed count and rate and do not invent a dollar value for an unpriced operational failure.

## Make the decision

Choose among continue, narrow, expand, and stop. A lower quality rate alone does not justify expansion when a hard capacity or service constraint fails. A recommendation may be conditional, but the condition must be testable and the interim action must be clear.

For each plausible option, state:

1. expected next-period workload and mix;
2. quality and operational effect supported by the packet;
3. labor, capacity, cost, and service implications;
4. what is uncertain or confounded; and
5. the decision and why it satisfies the owner’s constraints.

When evidence is insufficient, define a bounded follow-up rather than deferring the decision. Specify the exact scope and dates or number of ordinary shifts, participating line(s), staffing and training budget, unchanged controls, primary quality outcome, process measures, maturity requirement, review date, and stop/rollback triggers. Do not claim savings or capacity for an unmeasured selective variant. State what runs in the meantime.

## Show the arithmetic

Include enough detail for another operator to reproduce the result locally:

- event rate = qualifying events / qualifying observations;
- mix-standardized rate = sum of (planned segment share × segment rate);
- incremental comparison, when justified = intervention change minus concurrent comparison change;
- quality workload = planned orders × rate change;
- avoidable quality cost = workload × authorized cost per event;
- added labor cost = added productive hours × authorized hourly cost.

Label every projection and scenario, keep costs separate from unpriced service effects, and round only for presentation. Prefer a small local script when repeated aggregation or joins would otherwise be easy to misread.

Do not change live staffing, production systems, records, or customer communications. Produce an analysis and recommendation for the authorized decision owner; execution requires that owner’s separate decision.
