# Vendor reimbursement rollup

**Status:** Complete  
**Source snapshot:** `snap_c22e71aa06b43ab25395e0ce`  
**Posting-date interval:** 2026-04-03 through 2026-04-09, inclusive  
**Currency:** USD  
**Coverage:** 6 of 6 source records examined; the final page returned a null next cursor.

| vendor_id | settled charges | settled credits | net (charges - credits) | qualifying entries |
|---|---:|---:|---:|---:|
| `apricot` | 1,234 cents ($12.34) | 1,234 cents ($12.34) | 0 cents ($0.00) | 2 |
| `juniper` | 2,501 cents ($25.01) | 0 cents ($0.00) | 2,501 cents ($25.01) | 1 |
| `willow` | 0 cents ($0.00) | 407 cents ($4.07) | -407 cents (-$4.07) | 1 |

The complete checkpoint is saved at `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U089/work/reimbursement-rollup.json`. It records both incorporated page cursors, all six examined entry IDs, the null terminal cursor, source binding, snapshot, interval, and vendor totals. No additional tranche is needed.
