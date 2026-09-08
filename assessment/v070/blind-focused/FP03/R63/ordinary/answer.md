# Reimbursement rollup

The rollup is complete for the inclusive interval **2026-04-03 through 2026-04-09**.

- Snapshot: `snap_c22e71aa06b43ab25395e0ce`
- Currency: USD
- Source coverage: **6 of 6 records examined**

| vendor_id | settled charges | settled credits | net (charges − credits) | qualifying entries |
|---|---:|---:|---:|---:|
| `apricot` | $12.34 | $12.34 | $0.00 | 2 |
| `juniper` | $25.01 | $0.00 | $25.01 | 1 |
| `willow` | $0.00 | $4.07 | -$4.07 | 1 |

The complete workflow result was returned with exit code 0 after source exhaustion. The checkpoint and supporting continuation record is at `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/F-U009/work/reimbursement-2026-04-03_to_2026-04-09.json`.

No limitation prevented completion. The result depends on the supplied API honoring its documented immutable-snapshot, cursor, and metadata contract.
