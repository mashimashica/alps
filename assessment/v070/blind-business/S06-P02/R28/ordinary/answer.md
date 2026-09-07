# Complete vendor reimbursement rollup

- **Snapshot:** `snap_c22e71aa06b43ab25395e0ce`
- **Inclusive posting-date interval:** `2026-04-03` through `2026-04-09`
- **Source records examined:** 6
- **Exhaustion:** Established by a valid page response with `next_cursor: null`.

All amounts are exact integer USD cents.

| vendor_id | settled charges | settled credits | net (charges − credits) | qualifying entries |
|---|---:|---:|---:|---:|
| `apricot` | 1,234 | 1,234 | 0 | 2 |
| `juniper` | 2,501 | 0 | 2,501 | 1 |
| `willow` | 0 | 407 | -407 | 1 |

The request-specific evidence and completed checkpoint are at [reimbursement-2026-04-03-through-2026-04-09.checkpoint.json](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U081/work/reimbursement-2026-04-03-through-2026-04-09.checkpoint.json). It records all six incorporated entry IDs, the exact interval and source paths, the snapshot, `exhausted: true`, and `next_cursor: null`. The post-run `describe` response reported tranche 1 with 0 of 2 page calls remaining.
