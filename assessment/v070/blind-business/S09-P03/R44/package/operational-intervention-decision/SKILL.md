---
name: operational-intervention-decision
description: Turn a local operational trial measurement packet and decision context into a reviewable continue, narrow, expand, or stop recommendation. Use when quality, cost, capacity, service commitments, cohort maturity, mix changes, or nonrandom comparison affect a near-term operating decision.
---

# Operational intervention decisions

Use the packet's measurement notes and decision context as the authority. Produce a decision the named owner can act on, with arithmetic that another reader can reproduce and with clear limits on what the evidence supports.

## Establish the decision frame

Before calculating, identify:

- the available choices, decision period, owner, objectives, hard limits, and actions outside the user's authority;
- the intervention, treated and comparison units, baseline and intervention periods, assignment method, concurrent changes, and material mix differences;
- each measure's unit, denominator, observation window, recording changes, and relationship to other tables;
- the planned volume and mix, cost assumptions, staffing or capacity limits, service commitments, and timing of mature outcomes.

Do not replace packet assumptions with outside benchmarks. Ask only when missing information blocks a useful decision; otherwise state the uncertainty and make a bounded recommendation.

## Make the numerical basis reviewable

Validate counts and joins before interpreting them. In particular:

- use only outcome-mature units in a delayed-outcome denominator;
- keep pre-dispatch catches separate from downstream errors, especially if catch recording changed;
- aggregate measures at their native grain before joining, so line- or shift-level labor is not repeated across order-band rows;
- treat overtime and training as subsets of productive hours when the notes define them that way;
- separate one-off training from ongoing workload when estimating steady-state capacity;
- distinguish ordinary full shifts from partial or exceptional shifts when planning full-shift capacity.

Show counts as well as rates. Calculate crude results, then standardize stratum-specific rates to the decision period's planned mix when composition changed. Compare the treated unit with its own baseline and with a concurrent comparison when available. A difference-in-differences calculation can describe how the treated unit changed relative to the comparison, but nonrandom assignment, small samples, concurrent changes, and clustered dates limit causal claims.

For the expected operating period, translate rates into expected event counts at planned volume. Show the chosen counterfactual rather than hiding it in a single return metric. When more than one plausible baseline materially changes the result, present a range or labeled scenarios.

Assess ongoing labor and service outcomes separately:

1. Estimate routine hours at observed throughput, excluding one-off training when justified by the notes.
2. State any throughput scaling assumption and test planned hours against the hard cap.
3. Calculate incremental labor cost from additional hours only when that is the relevant decision cost.
4. Keep service outcomes without an authorized dollar value as operational outcomes; do not invent a price.

Use `scripts/analyze_packet.py` when the packet follows its documented CSV contract. Run `python scripts/analyze_packet.py --help` for the required arguments. Its Markdown output provides validation, observed rates, mix-standardized planning scenarios, labor scaling, and dispatch results. Treat its proportional labor projection as a planning assumption and its common-change counterfactual as descriptive, then apply the packet's qualitative context.

## Make the decision

Choose continue, narrow, expand, or stop for the stated period. A conditional recommendation is acceptable, but it must define the condition and the action on each side of it. Explain:

- what the measurements establish directly;
- what they suggest but cannot attribute to the intervention;
- how quality, capacity, service, cost, and outcome timing affect the choice;
- why the rejected options are weaker under the stated limits.

If a bounded follow-up is decision-relevant, specify its eligible population, intervention assignment, staffing cap, measures, immediate guardrails, review date, and the exact question it resolves. State what happens during the follow-up and what happens if a guardrail fails. Do not present an unmeasured selective variant's savings, throughput, or effect as observed fact.

End with the concrete recommendation and a compact numerical basis. Preserve the decision owner's authority: preparing a recommendation does not authorize staffing changes, production changes, spending, communications, or record modification.
