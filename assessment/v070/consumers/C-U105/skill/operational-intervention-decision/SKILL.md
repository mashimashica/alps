---
name: operational-intervention-decision
description: Evaluate whether to continue, narrow, expand, or stop an operational intervention using a local measurement packet, operating constraints, and decision-owner context. Use for bounded trials where cohort maturity, changing mix, concurrent changes, capacity, cost, or service outcomes affect the decision.
---

# Operational Intervention Decision

Turn the supplied packet into an action the named decision owner can take for the stated horizon. Treat the packet as authoritative; do not replace missing local assumptions with web research or generic benchmarks.

## Establish the decision frame

Read the measurement definitions and decision context before calculating. Identify:

- the choices the owner can authorize, planning horizon, objectives, hard limits, and commitments;
- the intervention unit, start date, comparison groups, assignment method, and concurrent changes;
- numerator, denominator, maturity window, exclusions, unit of each measure, and any recording change;
- planned workload and mix versus the workload actually observed.

State material missing information. Do not turn an absent threshold, dollar value, or causal estimate into an invented one. Keep recommendations within the user's authority; analysis is not authorization to change operations.

## Build a reviewable measurement basis

Validate column presence, integer/count relationships, duplicate keys, missing rows, and denominator eligibility. Never treat an immature cohort as an observed zero. Do not combine upstream catches with downstream failures when they describe different outcomes. Do not duplicate line-level labor by joining it to multiple cohort rows.

Calculate, as applicable:

1. Raw mature outcome rates by period, line, and meaningful stratum.
2. Mix-adjusted rates using the decision period's planned mix, with the weights shown.
3. Concurrent-control changes when a comparison line exists: intervention change minus control change. Label this as a quasi-experimental estimate when assignment was not randomized.
4. Immediate service outcomes, labor, overtime, and training separately. Remove one-off training from an ongoing run-rate only when definitions support that treatment.
5. Planning scenarios that translate rates and incremental workload to the stated horizon. Show formulas and distinguish observed inputs from scaling assumptions.

Use `scripts/analyze_packet.py` when the packet follows the two-CSV schema shown in its `--help`. It produces a deterministic Markdown basis and performs structural checks. The calling agent must still interpret the context, choose defensible ordinary-shift dates, and assess causal limits.

## Make the decision

Compare continuation, narrowing, expansion, and stopping against all decision-relevant objectives. A quality improvement does not override a hard capacity or service constraint. Separate:

- **Establishes:** direct counts, rates, hours, and constraint performance supported by comparable observations.
- **Suggests:** causal effects, subgroup differences, and projected economics that depend on nonrandom comparisons, small samples, or scaling.
- **Unknown:** unmeasured variants, incomplete outcome windows, and costs or effects the packet does not authorize.

Give one primary recommendation and explain why the alternatives are weaker. For a bounded follow-up, specify its scope, interim operating choice, staffing ceiling, assignment or comparison method, immediate guardrails, outcome maturity date, review point, and the exact question that will be resolved. Do not describe savings, capacity, or effectiveness of an untested narrowed variant as observed fact.

Present a compact decision memo plus the numerical basis or a locally reproducible artifact. Report cost and service consequences separately when the packet supplies no common dollar value. Make the arithmetic traceable from source rows to recommendation.

