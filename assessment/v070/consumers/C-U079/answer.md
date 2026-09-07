# Complete reimbursement rollup

The ledger was exhausted within the authorized tranche. Two successful `page` calls incorporated all 6 source records, and the second page returned `next_cursor: null`.

- **Snapshot:** `snap_c22e71aa06b43ab25395e0ce`
- **Inclusive posting-date interval:** `2026-04-03` through `2026-04-09`
- **Currency and arithmetic:** USD, exact integer cents

| vendor_id | settled charges | settled credits | net (charges − credits) | qualifying entries |
|---|---:|---:|---:|---:|
| `apricot` | 1,234 cents ($12.34) | 1,234 cents ($12.34) | 0 cents ($0.00) | 2 |
| `juniper` | 2,501 cents ($25.01) | 0 cents ($0.00) | 2,501 cents ($25.01) | 1 |
| `willow` | 0 cents ($0.00) | 407 cents ($4.07) | -407 cents (-$4.07) | 1 |

Only settled entries posted within the inclusive interval were aggregated. Vendors are sorted by `vendor_id`; zero and negative net vendors are retained.

The saved evidence is at `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U079/work/rollup-progress.json`. It records `complete: true`, `pages_applied: 2`, `next_cursor: null`, and `recovery_required: false`.
