---
name: operational-intervention-decision
description: Make an actionable operational intervention recommendation from a local measurement packet and operating context. Use for decisions to continue, narrow, expand, or stop a trial when outcome maturity, changing workload, comparison groups, staffing limits, cost, and service commitments matter. Produces inspectable calculations, a bounded decision, and a follow-up plan without changing live operations.
---

# Operational intervention decision

Use the supplied packet as the authority. Recommend an action for the decision owner; do not change staffing, spending, records, systems, or send messages. Ask for missing decision-critical definitions or limits where needed, but complete the supported analysis and state an interim decision. Do not invent thresholds or operating assumptions.

## Establish what is being decided

Read the brief, measurement definitions, operating context, and raw measurements before calculating. Identify the decision owner, options, next-period volume and mix, labor and equipment limits, service commitments, cost assumptions, and available authority. Separate hard constraints from preferences. Record which facts are observations, forecasts, or assumptions.

Map each table's grain, unique keys, units, eligible populations, and timing. Identify comparable periods, intervention and comparison groups, simultaneous changes, recording discontinuities, unusual shifts, and selection into treatment. Check duplicate keys, missing rows, valid counts, compatible periods, and whether subgroup totals reconcile. Keep sources unchanged.

## Build an inspectable numerical basis

Use available local tools; a script is optional. Provide a rerunnable command or transparent workbook, exact inputs, formulas, intermediate aggregates, and outputs. Keep packet-specific data and conclusions outside this reusable Skill. State dependencies and verification limits. Validate at the source grain before aggregating; never duplicate whole-shift labor by joining it to multiple subgroup records.

1. **Eligibility and outcomes.** Calculate each outcome using its proper denominator and observation window. Mature downstream errors divide by mature orders, not all recent shipments. Pending cohorts remain pending. Immediate dispatch measures can include recent cohorts, but report atypical shifts separately. Do not combine intercepted issues with customer outcomes or treat recording changes as treatment effects.
2. **Composition and comparability.** Show raw rates and workload shares, then rates within meaningful strata. For a stated target mix, standardize each group and period using the same weights: `R = sum(target_share[s] * errors[s] / eligible[s])`. Disclose absent strata and avoid unsupported extrapolation. A changing aggregate can reflect mix rather than within-stratum improvement.
3. **Attribution.** Describe before/after changes as observed associations. If there is a reasonable comparison group, show its change and an adjusted contrast: `(treatment_before - treatment_after) - (comparison_before - comparison_after)` after common-mix standardization. State assumptions: comparable trends and exposure to other changes, stable measurement, and no differential selection. Without randomization or enough pre-period evidence, use this as a planning scenario, not a proven causal effect. Note small outcome counts and clustering; avoid false precision or unsupported significance claims.
4. **Labor and service.** Aggregate labor once at its native grain. Separate one-off training from recurring work; overtime may already be included. Show observed hours, throughput, overtime, and late-dispatch rates on comparable shifts. Distinguish total program effort from incremental labor relative to a named alternative.
5. **Next-period feasibility.** Translate hours per order into required hours at planned volume, compare with the hard cap, and calculate supported volume at that cap. Explain whether observed mix supports the forecast; without subgroup labor data, a mix-adjusted labor estimate is not identified. A proportional extrapolation is a scenario, not a capacity guarantee. Test dispatch commitments separately from labor and quality. Do not assume staff transfers or extra stations are available.
6. **Economics.** For each useful named baseline, show `expected avoided errors = forecast orders * estimated rate reduction`, benefit at the supplied avoidable cost, recurring incremental labor cost, and separately funded or sunk training. Pair quality and labor comparisons consistently. Do not count all observed improvement as caused by the intervention, double-count overtime, invent the value of lateness, or let positive expected savings override infeasibility. Show break-even or sensitivity when uncertain effects could change the choice.

## Make a usable recommendation

Choose among continuation, scope change, expansion, and stopping; briefly explain why the relevant alternatives lose. Name the operating scope, duration, staffing boundary, and what happens immediately. If no tested intervention fits the cap and service promise, say so and choose a supported fallback, disclosing its quality and capacity uncertainties.

Treat selective or redesigned variants as untested. Do not obtain their savings by simply multiplying full-trial labor by the fraction of orders selected. A proposed bounded trial needs a feasible staffing allocation, scope or stop rule, measurement plan, review date, and the decision-relevant question it resolves. If capacity for a trial is unproven, condition its launch on an observed fit within the existing allowance; specify the fallback until then.

Define both an early operational review and a later review after outcomes mature. Measure planned mix and volume, actual recurring hours, lateness, and consistently defined mature outcomes by group/stratum. Specify who reviews the results, what evidence permits reconsideration, and what happens if service or staffing cannot be sustained. Do not promise a future decision from a tiny sample.

## Deliver and check

Present the recommendation first, followed by only the tables and explanation necessary to assess it. Link the reproducible calculations. Include data lineage, exclusions, causal limitations, forecast assumptions, and unanswered questions. Reconcile weighted rates and native-grain totals against the source; rerun any supplied calculation path and record actual checks. A format-valid Skill or a successful script is not evidence that the intervention works.
