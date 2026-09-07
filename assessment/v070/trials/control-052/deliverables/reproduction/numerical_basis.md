# Numerical trace

All outcome rates use mature orders only. Operations are aggregated once per line/date.

## Mature cohorts

| Period | Line | Band | Shipped | Mature | Errors | Rate | Station catches |
|---|---|---:|---:|---:|---:|---:|---:|
| baseline | East | complex | 1200 | 1200 | 96 | 8.000% | 9 |
| baseline | East | standard | 1800 | 1800 | 36 | 2.000% | 7 |
| baseline | West | complex | 1200 | 1200 | 84 | 7.000% | 9 |
| baseline | West | standard | 1800 | 1800 | 36 | 2.000% | 6 |
| pilot | East | complex | 320 | 300 | 18 | 6.000% | 30 |
| pilot | East | standard | 3080 | 2700 | 27 | 1.000% | 72 |
| pilot | West | complex | 320 | 300 | 19 | 6.333% | 19 |
| pilot | West | standard | 3080 | 2700 | 40 | 1.481% | 48 |

## Operations

| Period | Line | Shipped | Productive hours | Training hours | Late dispatches | Late rate | Dates |
|---|---|---:|---:|---:|---:|---:|---:|
| baseline | East | 3000 | 207 | 0 | 15 | 0.500% | 3 |
| baseline | West | 3000 | 205 | 0 | 17 | 0.567% | 3 |
| pilot | East | 3400 | 269 | 4 | 63 | 1.853% | 4 |
| pilot | West | 3400 | 237 | 0 | 24 | 0.706% | 4 |

## Full-shift labor (daily line shipments >= 1000)

| Period | Line | Full-shift dates | Avg productive hours | Avg ongoing hours (training removed) | Avg orders |
|---|---|---:|---:|---:|---:|
| baseline | East | 3 | 69.000 | 69.000 | 1000.0 |
| baseline | West | 3 | 68.333 | 68.333 | 1000.0 |
| pilot | East | 3 | 79.333 | 78.000 | 1000.0 |
| pilot | West | 3 | 69.667 | 69.667 | 1000.0 |

## Planning projection

| Band | Baseline East | Pilot East | Baseline West | Pilot West | Estimated incremental reduction |
|---|---:|---:|---:|---:|---:|
| standard | 2.000% | 1.000% | 2.000% | 1.481% | 0.481481 pp |
| complex | 8.000% | 6.000% | 7.000% | 6.333% | 1.333333 pp |

- Formula: weighted reduction = 0.8 * standard effect + 0.2 * complex effect = 0.651852 percentage points.
- Planned orders = 20 shifts * 1200 orders = 24000.
- Implied avoidable orders = planned orders * weighted reduction = 156.444.
- Implied avoidable cost = 156.444 * USD 65 = USD 10,168.89.
- Labor cost conversion (if an hour delta is supplied separately) = hour delta * USD 28; this trace does not infer causality from hours.
