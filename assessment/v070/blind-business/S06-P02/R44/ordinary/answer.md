# Complete vendor reimbursement rollup

- **Source snapshot:** `snap_c22e71aa06b43ab25395e0ce`
- **Inclusive posting-date interval:** `2026-04-03` through `2026-04-09`
- **Completion evidence:** 2 pages fetched, all 6 source records observed, and the second page returned a null next cursor.

| vendor_id | settled charges (USD cents) | settled credits (USD cents) | net charges − credits (USD cents) | qualifying entry count |
|---|---:|---:|---:|---:|
| `apricot` | 1,234 | 1,234 | 0 | 2 |
| `juniper` | 2,501 | 0 | 2,501 | 1 |
| `willow` | 0 | 407 | -407 | 1 |

The complete checkpoint and incorporated-entry evidence is available at `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U077/work/rollup.json`.
