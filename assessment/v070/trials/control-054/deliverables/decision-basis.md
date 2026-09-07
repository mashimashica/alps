# Reproducible decision basis

Generated with:

```bash
python3 deliverables/skills/operational-intervention-decision/scripts/analyze_packet.py input/sources/shipment_cohorts.csv input/sources/shift_operations.csv --intervention-line East --control-line West --planned-mix standard=0.8,complex=0.2 --planned-orders-per-shift 1200 --shifts 20 --hour-cap 84 --avoidable-cost 65 --hour-cost 28 --exclude-operations-date 2026-06-26
```

## Mature downstream quality

| Period | Line | Band | Errors | Mature orders | Rate |
|---|---|---:|---:|---:|---:|
| baseline | East | standard | 36 | 1800 | 2.00% |
| baseline | East | complex | 96 | 1200 | 8.00% |
| baseline | West | standard | 36 | 1800 | 2.00% |
| baseline | West | complex | 84 | 1200 | 7.00% |
| pilot | East | standard | 27 | 2700 | 1.00% |
| pilot | East | complex | 18 | 300 | 6.00% |
| pilot | West | standard | 40 | 2700 | 1.48% |
| pilot | West | complex | 19 | 300 | 6.33% |

## Planned-mix-standardized quality

| Period | Line | Standardized rate | Immature shipped orders excluded |
|---|---:|---:|---:|
| baseline | East | 3.20% | 0 |
| baseline | West | 3.00% | 0 |
| pilot | East | 2.00% | 400 |
| pilot | West | 2.45% | 400 |

Intervention-line change: -1.20 percentage points. Control-line change: -0.55 points. Difference-in-differences: -0.65 points (descriptive contrast, not a causal estimate).

## Operations (selected comparable shifts)

| Period | Line | Shipped | Shifts | Productive hours | Training subset | Ongoing hours/shift | Late orders | Late rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | East | 3000 | 3 | 207.0 | 0.0 | 69.00 | 15 | 0.50% |
| baseline | West | 3000 | 3 | 205.0 | 0.0 | 68.33 | 17 | 0.57% |
| pilot | East | 3000 | 3 | 238.0 | 4.0 | 78.00 | 59 | 1.97% |
| pilot | West | 3000 | 3 | 209.0 | 0.0 | 69.67 | 22 | 0.73% |

Operations-only excluded date: 2026-06-26, the packet-designated short low-volume shift. Its 400 immature orders per line remain reported in the quality exclusions above.

## Planning sensitivities

Required throughput: 14.29 orders/hour (1,200 orders / 84 hours). Observed East trial throughput was 12.82 orders/hour using ongoing hours across the three comparable trial shifts. Proportional scaling gives 93.6 hours/shift at planned volume; this assumes labor scales proportionally and is not a capacity forecast.

At 24,000 East orders, the East before/after change corresponds to 288.0 fewer errors and $18,720 at $65 each. The difference-in-differences contrast corresponds to 156.4 fewer and $10,169. Both are planning scenarios, not causally established savings. No future incremental-hour cost is calculated because labor scaling at planned volume and selective-check effort are unknown.
