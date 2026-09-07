---
name: intervention-decision
description: Turn a local operational measurement packet into a reviewable intervention decision, including comparability checks, next-period workload and cost implications, and a bounded follow-up when evidence is incomplete.
---

# Operational intervention decisions

Use this skill when an owner must decide whether to continue, stop, narrow, or expand a process change from local operational records. Produce a recommendation the owner can act on within the stated staffing, service, and budget limits. Treat the supplied packet and its definitions as authoritative; do not fill gaps with external benchmarks unless the user asks for them.

## Establish what the packet can answer

Read the measurement notes and decision context before calculating rates. Record the intervention, comparison period or line, decision horizon, planned volume and mix, staffing ceiling, service promise, and any authorized cost assumptions. Check that each input's unit of observation matches its intended use.

Keep these distinctions visible in the analysis:

- Calculate downstream outcome rates from mature orders only. A zero mature count means the observation window is open, not that the error rate is zero.
- Treat process catches as context when their recording rules changed or when they are not the same outcome. Do not add catches to downstream errors.
- Aggregate line-level labor and dispatch rows once per date and line. Do not join line hours to order-band rows and sum them.
- Separate one-off training hours from ongoing productive hours. Keep overtime as a subset of productive hours.
- Identify mix shifts, concurrent changes, volunteer or non-random assignment, partial shifts, missing rows, and outcome lag before interpreting a before/after difference.

## Build the evidence

Create a cohort table grouped by period, line, and order band with shipped orders, mature orders, confirmed downstream errors, and the resulting mature-order rate. Show the underlying numerators and denominators. Also create a line-and-period operations table with shipped orders, productive hours, training hours, late dispatches, and late-dispatch rate.

Compare like with like. Use order-band rates when the mix changed. A comparator line or period can support a difference-in-differences style estimate:

`incremental reduction = (baseline intervention rate - pilot intervention rate) - (baseline comparator rate - pilot comparator rate)`.

Weight band-level estimates by the next-period mix only when that mix is explicitly supplied. Label the result as an estimate, not proof of causality, when assignment was voluntary or other changes occurred at the same time. State where small cells, short follow-up, or immature cohorts make the estimate unstable. Do not treat a lower aggregate rate caused by a changed mix as intervention impact.

Assess dispatch and capacity independently of quality. Compare observed late-dispatch rates with the owner's service promise, and compare full-shift productive hours with the next-period limit at the planned volume. Keep any unpriced service consequence as an operational constraint rather than inventing a dollar value. Report the effect of training separately from recurring work.

## Convert evidence into a decision

Project the next period from the supplied shifts, orders per shift, mix, and rates. If using an incremental quality estimate, show the formula and the implied avoidable orders. Apply only authorized cost assumptions, such as avoidable cost per downstream error and marginal labor cost; show baseline and workload assumptions. Do not claim savings or capacity for an unmeasured variant.

Choose one actionable disposition: continue the tested scope, stop it, narrow it, or expand it. The recommendation must satisfy the hard service and staffing limits or explicitly state the condition under which the owner should choose a different disposition. A bounded follow-up may support a future change, but specify its scope, line staffing, measurement window, review date, and decision question. State what happens during the follow-up so it does not defer the current-period decision.

## Make arithmetic reproducible

Keep a local calculation trace or script beside the decision. It should read the supplied files, validate required columns, expose mature-only denominators, aggregate line-level operations once, and print or write the formulas and assumptions used for projections. Make failures clear for missing files, columns, invalid numbers, or no mature rows. The trace supports review; it does not replace the narrative decision or the limitations section.

When handing off, include the generated skill, the decision artifact, the reproducibility command and output, checks actually run, and any checks that remain unperformed. Do not perform production changes, contact staff or customers, or infer authorization to spend or change staffing from the analysis.
