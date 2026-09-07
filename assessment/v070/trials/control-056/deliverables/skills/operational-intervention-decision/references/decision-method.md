# Decision method

Use this reference when the packet contains stratified cohorts, an intervention and comparison operation, or planned-volume capacity and cost questions.

## Cohorts and mix adjustment

Use only observations whose full outcome window has elapsed. For stratum \(s\), period \(t\), and line \(l\):

\[
r_{tls}=\frac{y_{tls}}{n_{tls}}
\]

where \(y\) is the stated matured outcome count and \(n\) is its matured eligible denominator. Standardize to the decision-period mix \(w_s\), with weights summing to 1:

\[
R_{tl}=\sum_s w_s r_{tls}
\]

Show the raw rate too when useful, but use the standardized rate for planning when observed mix differs from the decision mix. Do not use shipped orders as the denominator for a maturity-gated outcome.

With intervention line \(I\), comparison line \(C\), baseline \(0\), and intervention period \(1\), report:

\[
\text{contemporaneous benefit}=R_{1C}-R_{1I}
\]

\[
\text{difference-in-differences benefit}=(R_{1C}-R_{0C})-(R_{1I}-R_{0I})
\]

Positive values indicate fewer adverse outcomes on the intervention line. These are descriptive if assignment was not randomized or concurrent changes were not isolated. Report both when they bracket plausible planning effects; explain why neither is a causal guarantee.

For an approximate sampling interval, estimate each standardized rate variance as

\[
\operatorname{Var}(R_{tl})=\sum_s w_s^2\frac{r_{tls}(1-r_{tls})}{n_{tls}}
\]

and add variances for independent contrasts. Label the resulting normal interval approximate. Its purpose is to expose imprecision, not to convert an observational design into a randomized one.

## Operations and capacity

Summarize line-level labor once per line-date. Treat overtime and training as subsets when the packet says they are included in productive hours. For ongoing workload, subtract one-off training only when definitions authorize that treatment.

Prefer ordinary, comparable full shifts for next-period capacity. Show anomalous or short shifts separately or use them only as a sensitivity check. When projecting labor to a different volume, state the model. A proportional model is:

\[
H_{plan}=\frac{H_{observed}}{Q_{observed}}Q_{plan}
\]

It is a planning estimate, not observed capacity. Compare it with the hard labor cap and show headroom. If base work is already near the cap, do not assume a narrowed intervention fits without a timed observation or explicit staffing design. Scaling an all-order intervention by the share of targeted orders assumes equal effort per order; label it as a sensitivity, especially when complex work may take longer.

Dispatch rates use shipped orders for the same line-dates when every shipped order is eligible. Compare the observed rate and the implied maximum late-order count for the planning horizon. Keep unpriced dispatch consequences outside dollar totals.

## Economics

For planned volume \(Q\), effect \(e\) in adverse outcomes per order, avoidable cost \(c_y\), incremental hours \(h\), and hourly cost \(c_h\):

\[
\text{avoided outcomes}=Qe
\]

\[
\text{quality value}=Qe c_y
\]

\[
\text{incremental labor cost}=h c_h
\]

Show effect and labor scenarios separately rather than blending them into an unjustified precise return. Do not monetize outcomes without an authorized value. A positive point estimate does not override a hard capacity or dispatch constraint.

## Script input contract

`scripts/analyze_packet.py` expects:

- a cohort CSV with `shipment_date`, `period`, `line`, `order_band`, `shipped_orders`, `mature_orders`, and `confirmed_mispack_7d`;
- an operations CSV with `shipment_date`, `period`, `line`, `productive_labor_hours`, `training_hours`, and `late_dispatch_orders`;
- every line-date in operations to have cohort rows whose shipped counts can be summed once; and
- decision-mix entries matching all analyzed order bands.

The script validates nonnegative counts, errors no greater than mature orders, mature orders no greater than shipped orders, unique source grains, mix coverage, and cross-file periods. It excludes zero-maturity strata from outcome rates and reports their shipped volume as open-window volume. Its intervals address binomial sampling variation only; source bias, confounding, extrapolation, and operational dependence remain judgment issues.
