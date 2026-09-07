# Complete vendor reimbursement rollup

- **Snapshot:** `snap_c22e71aa06b43ab25395e0ce`
- **Posting-date interval:** `2026-04-03` through `2026-04-09`, inclusive
- **Currency:** USD
- **Coverage:** 6 of 6 source records examined across two successful `page` calls
- **Completion evidence:** the final page returned `next_cursor: null`, and the checkpoint verified that all 6 records were covered

| vendor_id | Settled charges (cents) | Settled credits (cents) | Net (charge - credit, cents) | Qualifying entries |
|---|---:|---:|---:|---:|
| `apricot` | 1,234 | 1,234 | 0 | 2 |
| `juniper` | 2,501 | 0 | 2,501 | 1 |
| `willow` | 0 | 407 | -407 | 1 |

The complete checkpoint and fetched-page evidence are preserved at `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U091/work/reimbursement-2026-04-03_2026-04-09.json`, with its lock sidecar at the same path plus `.lock`. The checkpoint records `done: true`, `cursor: null`, the snapshot and interval, both processed page cursors, and all six examined records. The post-run unmetered `describe` response reported tranche 1 with 0 calls remaining. No further tranche is required because exhaustion and full record coverage were established.
