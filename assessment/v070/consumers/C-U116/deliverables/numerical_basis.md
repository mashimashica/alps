# Numerical basis — Fenwick Audio Renewal

Run from the consumer directory with `python3 deliverables/analysis.py`. 
Python 3 standard library only. Inputs: `shipment_cohorts.csv` and `shift_operations.csv`.

## Integrity and eligibility

- 28 cohort rows and 14 operation rows read.
- Duplicate keys: 0. Missing expected date/line/band rows: 0. Impossible denominator/count checks: 0.
- Quality uses mature cohorts on the six ordinary full shifts only. August 28 is immature and is not treated as zero-error.
- Labor and dispatch use each whole-line operation row once. The five Alder training hours on August 17 are removed only from recurring labor.
- Station catches are excluded from downstream errors because recording changed on August 14.

## Mature quality

| Period | Line | Band | Mature orders | Errors | Rate | Cohort share |
|---|---|---:|---:|---:|---:|---:|
| baseline | Alder | standard | 2,100 | 42 | 2.00% | 58.33% |
| baseline | Alder | complex | 1,500 | 90 | 6.00% | 41.67% |
| baseline | Alder | **actual total** | **3,600** | **132** | **3.67%** | **100.00%** |
| baseline | Birch | standard | 2,100 | 42 | 2.00% | 58.33% |
| baseline | Birch | complex | 1,500 | 60 | 4.00% | 41.67% |
| baseline | Birch | **actual total** | **3,600** | **102** | **2.83%** | **100.00%** |
| pilot | Alder | standard | 3,300 | 33 | 1.00% | 91.67% |
| pilot | Alder | complex | 300 | 30 | 10.00% | 8.33% |
| pilot | Alder | **actual total** | **3,600** | **63** | **1.75%** | **100.00%** |
| pilot | Birch | standard | 3,300 | 33 | 1.00% | 91.67% |
| pilot | Birch | complex | 300 | 18 | 6.00% | 8.33% |
| pilot | Birch | **actual total** | **3,600** | **51** | **1.42%** | **100.00%** |

Formula: next-mix standardized rate = `0.70 × standard rate + 0.30 × complex rate`.

| Period | Alder standardized | Birch standardized | Alder − Birch |
|---|---:|---:|---:|
| baseline | 3.20% | 2.60% | +0.60% |
| pilot | 3.70% | 2.50% | +1.20% |

- Alder standardized before/after: 3.20% → 3.70%, change +0.50%.
- Birch standardized before/after: 2.60% → 2.50%, change -0.10%.
- Difference-in-differences sensitivity: (+0.50%) − (-0.10%) = +0.60%. This is not a causal estimate.

## Labor and dispatch on ordinary full shifts

| Period | Line | Orders | Productive hours | Training | Recurring hours/order | Projected hours at 1,440 | Feasible volume at 102 h | Late orders | Late rate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | Alder | 3,600 | 246.0 | 0.0 | 0.06833 | 98.4 | 1,493 | 21 | 0.58% |
| baseline | Birch | 3,600 | 240.0 | 0.0 | 0.06667 | 96.0 | 1,530 | 18 | 0.50% |
| pilot | Alder | 3,600 | 275.0 | 5.0 | 0.07500 | 108.0 | 1,360 | 42 | 1.17% |
| pilot | Birch | 3,600 | 246.0 | 0.0 | 0.06833 | 98.4 | 1,493 | 18 | 0.50% |

Checked Alder recurring projection: `(275 − 5) / 3,600 × 1,440 = 108.0 h/shift`, which is 6.0 h over the cap; cap-feasible volume is 1,360 orders.
Alder baseline no-check projection: `246 / 3,600 × 1,440 = 98.4 h/shift`; cap headroom 3.6 h and cap-feasible volume 1,493 orders.
Birch contemporaneous no-check projection: `246 / 3,600 × 1,440 = 98.4 h/shift`; cap headroom 3.6 h and cap-feasible volume 1,493 orders.
At the ordinary full-shift pilot rate, Alder projects 336 late orders in 28,800 (1.17%), versus the 288-order maximum at 1.00%. Birch projects 144 (0.50%).

## Cost scenarios for Alder all-order checking

Incremental recurring labor vs Alder baseline: `108.0 − 98.4 = 9.6 h/shift`; cost $326.40/shift or $6,528.00 over 20 shifts. Startup training is separate and excluded.

| Scenario | Rate reduction vs counterfactual | Avoided errors/shift | Gross avoided cost/shift | Net after labor/shift | Net over 20 shifts |
|---|---:|---:|---:|---:|---:|
| Conservative: contemporaneous Birch pilot rates | -1.20% | -17.28 | $-950.40 | $-1,276.80 | $-25,536.00 |
| Favorable: standard-band gain fully attributed; no complex effect | +0.70% | +10.08 | $554.40 | $228.00 | $4,560.00 |

Break-even benefit: `9.6 × $34 / $55 = 5.93` avoided errors/shift, or 0.412% of 1,440 orders. Service failures are not monetized.

## Projection boundaries

All capacity figures assume labor scales linearly with orders and that the observed hours/order applies at the planned 70/30 mix. Because labor is not recorded by band, mix-specific capacity and selective-check labor cannot be identified. Allocation was nonrandom; Alder began worse on complex orders; the account pause and August 14 template change confound before/after comparisons. The complex pilot denominator is only 300 per line. These are planning scenarios, not proof of checker impact or future delivery.
