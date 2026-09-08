# Reproducible numerical basis

Run from the consumer directory:

```bash
python3 deliverables/analyze.py
```

The script uses only Python's standard library and writes `deliverables/analysis.json`. Inputs and inclusion rules are recorded in the script and JSON output.

## Full-shift line totals

| Period | Line | Mature mispacks | Mispack rate | Paid hours | Ongoing hours excluding training | Orders/hour (paid) | Paid hours/order | Late dispatches | Dispatch rate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | Harbor | 63/2400 | 2.625% | 186 | 186 | 12.90 | 0.0775 | 14/2400 | 0.583% |
| baseline | Ridge | 63/2400 | 2.625% | 186 | 186 | 12.90 | 0.0775 | 14/2400 | 0.583% |
| pilot | Harbor | 30/2400 | 1.250% | 198 | 195 | 12.12 | 0.0825 | 13/2400 | 0.542% |
| pilot | Ridge | 60/2400 | 2.500% | 186 | 186 | 12.90 | 0.0775 | 13/2400 | 0.542% |

## Common-mix quality comparison

The planned 75% standard / 25% complex mix equals the observed mix. Pooled and standardized rates therefore coincide.

- Harbor: 2.625% to 1.250%, change -1.375%.
- Ridge: 2.625% to 2.500%, change -0.125%.
- Illustrative difference in changes: -1.250%, or 200 fewer mispacks over 16,000 Harbor orders if the comparison assumption holds.

Category rates and all raw aggregate counts are in `analysis.json`.

## Planning arithmetic

- Harbor baseline labor: 62 hours/shift. Pilot ongoing labor after removing the three one-off training hours: 65 hours/shift.
- Linear projection: 3 additional hours/shift × 20 = 60 hours; at $32/hour = $1,920.
- Comparison-adjusted outcome value: 200 × $48 = $9,600.
- Illustrative net cost reduction: $9,600 − $1,920 = $7,680.
- Break-even quality effect: 0.250% (2.0 mispacks per 800-order shift; 40 over the period).
- Projected ongoing labor is 65 hours/shift, leaving 3 hours under the 68-hour limit. This is linear scaling from aggregate observed labor, not a category workload estimate.

July 31 was an immature 320-order short shift and is excluded from mature quality and matched full-shift capacity evidence. Its immediate Harbor dispatch result was 2/320 (0.625%); this is context only.
