# Vendor reimbursement rollup

Status: **complete**. The workflow examined all 6 source records across 2 pages; the final returned cursor was null.

- Source state: `/workspace/scratch/a75c3a6d9076/C-U073-ledger-state-rsr_6lq0/ledger.sqlite`
- Snapshot: `snap_c22e71aa06b43ab25395e0ce`
- Inclusive interval: `2026-04-03` through `2026-04-09`
- Filter: settled entries only

| vendor_id | settled charges (USD cents) | settled credits (USD cents) | net (charges - credits, USD cents) | qualifying entry count |
|---|---:|---:|---:|---:|
| apricot | 1,234 | 1,234 | 0 | 2 |
| juniper | 2,501 | 0 | 2,501 | 1 |
| willow | 0 | 407 | -407 | 1 |

The complete checkpoint evidence is at `work/checkpoint.json`. It records both incorporated page cursors, the null exhaustion cursor, the snapshot, interval, and accumulated totals. The authorized tranche is fully used (`remaining_calls: 0`), but no continuation is needed because traversal completed.
