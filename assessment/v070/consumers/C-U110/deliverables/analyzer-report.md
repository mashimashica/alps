# Reproducible operational intervention arithmetic

## Validation

- Shipment rows: 28; operations rows: 14.
- Passed nonnegative-count, maturity, subset, uniqueness, and join-grain checks.
- Delayed quality rates exclude cohorts with zero mature orders.
- Full-shift operations use only: 2026-08-03, 2026-08-04, 2026-08-05, 2026-08-17, 2026-08-18, 2026-08-19.

## Mature downstream quality

| Period | Line | Band | Mature | Errors | Rate |
|---|---|---:|---:|---:|---:|
| baseline | Alder | standard | 2,100 | 42 | 2.000% |
| baseline | Alder | complex | 1,500 | 90 | 6.000% |
| baseline | Birch | standard | 2,100 | 42 | 2.000% |
| baseline | Birch | complex | 1,500 | 60 | 4.000% |
| pilot | Alder | standard | 3,300 | 33 | 1.000% |
| pilot | Alder | complex | 300 | 30 | 10.000% |
| pilot | Birch | standard | 3,300 | 33 | 1.000% |
| pilot | Birch | complex | 300 | 18 | 6.000% |

Planned-mix weights: standard=70.0%, complex=30.0%.

| Period | Line | Planned-mix standardized rate |
|---|---|---:|
| baseline | Alder | 3.200% |
| baseline | Birch | 2.600% |
| pilot | Alder | 3.700% |
| pilot | Birch | 2.500% |

## Planning quality and cost scenarios

Planned volume per line: 28,800 orders (1,440 x 20).

| Scenario | Counterfactual rate | Pilot rate | Expected errors avoided | Gross avoidable cost |
|---|---:|---:|---:|---:|
| Treated own baseline | 3.200% | 3.700% | -144.00 | $-7,920.00 |
| Treated baseline plus comparison-line change | 3.100% | 3.700% | -172.80 | $-9,504.00 |

Comparison-line standardized change used in the second scenario: -0.100 percentage points (2.600% to 2.500%).

## Full-shift operations

| Period | Line | Shifts | Shipped | Routine hours/shift | Training hours | Late orders | Late rate |
|---|---|---:|---:|---:|---:|---:|---:|
| baseline | Alder | 3 | 3,600 | 82.00 | 0.00 | 21 | 0.583% |
| baseline | Birch | 3 | 3,600 | 80.00 | 0.00 | 18 | 0.500% |
| pilot | Alder | 3 | 3,600 | 90.00 | 5.00 | 42 | 1.167% |
| pilot | Birch | 3 | 3,600 | 82.00 | 0.00 | 18 | 0.500% |

## Proportional labor projection

- Treated baseline routine hours scaled to 1,440 orders: 98.40 per shift.
- Treated all-order pilot hours scaled to that volume: 108.00 per shift.
- Productive-hour cap: 102.00; projected all-order overage: 6.00 hours per shift.
- Projected incremental period hours and cost: 192.00 and $6,528.00.
- Gross avoidable cost less projected incremental labor: $-14,448.00 using own baseline; $-16,032.00 using the comparison-change scenario.
- Baseline projection leaves 3.60 hours; at the observed 0.0067 incremental hours per checked order, that is about 540 checks per shift.

These projections assume labor scales in direct proportion to throughput. The common-change scenario is descriptive, not causal, and a selective check's workload and effect are unmeasured until tested.
