# Reproducible operational intervention arithmetic

## Validation

- Shipment rows: 28; operations rows: 14.
- Passed nonnegative-count, maturity, subset, uniqueness, and join-grain checks.
- Delayed quality rates exclude cohorts with zero mature orders.
- Full-shift operations use only: 2026-07-06, 2026-07-07, 2026-07-08, 2026-07-20, 2026-07-21, 2026-07-22.

## Mature downstream quality

| Period | Line | Band | Mature | Errors | Rate |
|---|---|---:|---:|---:|---:|
| baseline | Harbor | standard | 1,800 | 27 | 1.500% |
| baseline | Harbor | complex | 600 | 36 | 6.000% |
| baseline | Ridge | standard | 1,800 | 27 | 1.500% |
| baseline | Ridge | complex | 600 | 36 | 6.000% |
| pilot | Harbor | standard | 1,800 | 12 | 0.667% |
| pilot | Harbor | complex | 600 | 18 | 3.000% |
| pilot | Ridge | standard | 1,800 | 27 | 1.500% |
| pilot | Ridge | complex | 600 | 33 | 5.500% |

Planned-mix weights: standard=75.0%, complex=25.0%.

| Period | Line | Planned-mix standardized rate |
|---|---|---:|
| baseline | Harbor | 2.625% |
| baseline | Ridge | 2.625% |
| pilot | Harbor | 1.250% |
| pilot | Ridge | 2.500% |

## Planning quality and cost scenarios

Planned volume per line: 16,000 orders (800 x 20).

| Scenario | Counterfactual rate | Pilot rate | Expected errors avoided | Gross avoidable cost |
|---|---:|---:|---:|---:|
| Treated own baseline | 2.625% | 1.250% | 220.00 | $10,560.00 |
| Treated baseline plus comparison-line change | 2.500% | 1.250% | 200.00 | $9,600.00 |

Comparison-line standardized change used in the second scenario: -0.125 percentage points (2.625% to 2.500%).

## Full-shift operations

| Period | Line | Shifts | Shipped | Routine hours/shift | Training hours | Late orders | Late rate |
|---|---|---:|---:|---:|---:|---:|---:|
| baseline | Harbor | 3 | 2,400 | 62.00 | 0.00 | 14 | 0.583% |
| baseline | Ridge | 3 | 2,400 | 62.00 | 0.00 | 14 | 0.583% |
| pilot | Harbor | 3 | 2,400 | 65.00 | 3.00 | 13 | 0.542% |
| pilot | Ridge | 3 | 2,400 | 62.00 | 0.00 | 13 | 0.542% |

## Proportional labor projection

- Treated baseline routine hours scaled to 800 orders: 62.00 per shift.
- Treated all-order pilot hours scaled to that volume: 65.00 per shift.
- Productive-hour cap: 68.00; projected all-order overage: 0.00 hours per shift.
- Projected incremental period hours and cost: 60.00 and $1,920.00.
- Gross avoidable cost less projected incremental labor: $8,640.00 using own baseline; $7,680.00 using the comparison-change scenario.
- Baseline projection leaves 6.00 hours; at the observed 0.0037 incremental hours per checked order, that is about 1600 checks per shift.

These projections assume labor scales in direct proportion to throughput. The common-change scenario is descriptive, not causal, and a selective check's workload and effect are unmeasured until tested.
