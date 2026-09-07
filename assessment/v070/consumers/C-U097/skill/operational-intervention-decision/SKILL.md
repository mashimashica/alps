---
name: operational-intervention-decision
description: Decide whether to continue, narrow, expand, or stop an operational intervention from a local measurement packet and operating context, connecting outcome evidence to capacity, cost, comparability, timing, and a feasible next-period action.
---

# Operational intervention decision

Turn a measurement packet into an auditable operating decision. Treat packet notes and decision context as authoritative.

1. Inventory units, grain, maturity rules, recording changes, cohorts, and horizon. Keep downstream outcomes separate from process observations; immature zeroes are unavailable outcomes.
2. Aggregate shipment cohorts by period, line, and band. Join line-level operations once per date; never duplicate hours across band rows. Show numerator, denominator, and rate.
3. Describe baseline and intervention timing, mix, volume, and concurrent changes. Separate established facts from suggestions and avoid unsupported attribution.
4. Test planned volume and mix against labor caps and dispatch promises. Keep training separate from ongoing hours; report unpriced operational effects without inventing dollars.
5. Recommend continue, narrow, expand, or stop for the horizon, with conditions that would change it. Never present an unmeasured variant as observed.
6. If needed, define bounded follow-up with scope, staffing, measures, review point, and question; state interim operation.

Use `confirmed_mispack_7d / mature_orders` and `late_dispatch_orders / shipped_orders`. Expose supplied cost assumptions and workload; label projections. Provide a local reproduction script or executable commands, preserve inputs, and make missing maturity visible. Deliver a concise memo covering recommendation, evidence, feasibility, costs, limitations, and follow-up.
