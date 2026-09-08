# Complete vendor reimbursement rollup

The rollup completed within the authorized tranche. The processor committed **2 page calls**, examined **all 6 of 6 source records**, and established source exhaustion.

- **Snapshot:** `snap_c22e71aa06b43ab25395e0ce`
- **Interval:** `2026-04-03` through `2026-04-09`, inclusive
- **Currency:** USD
- **Status:** complete (`final: true`)

| vendor_id | settled charges (cents) | settled credits (cents) | net charges − credits (cents) | qualifying entry count |
|---|---:|---:|---:|---:|
| `apricot` | 1,234 | 1,234 | 0 | 2 |
| `juniper` | 2,501 | 0 | 2,501 | 1 |
| `willow` | 0 | 407 | -407 | 1 |

The complete machine-readable result is at `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/F-U011/work/rollup.result.json`. Its continuation checkpoint is at `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/F-U011/work/rollup.checkpoint.json`; it records `complete: true`, `next_cursor: null`, and all six incorporated entry IDs.

There is no completion limitation or unresolved continuation uncertainty.
