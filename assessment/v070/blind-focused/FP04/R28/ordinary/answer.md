# Complete vendor reimbursement rollup

**Status:** Complete  
**Snapshot:** `snap_c22e71aa06b43ab25395e0ce`  
**Inclusive posting-date interval:** `2026-04-03` through `2026-04-09`  
**Currency:** USD  
**Coverage:** 6 of 6 source records examined across 2 committed pages; the final `next_cursor` is `null`.

Only settled entries posted within the inclusive interval were included. Amounts below are authoritative integer USD cents, and vendors are sorted by `vendor_id`.

| vendor_id | settled charge cents | settled credit cents | net cents | qualifying entry count |
|---|---:|---:|---:|---:|
| apricot | 1,234 | 1,234 | 0 | 2 |
| juniper | 2,501 | 0 | 2,501 | 1 |
| willow | 0 | 407 | -407 | 1 |

The complete machine-readable report is at `work/report/report.json`. The durable checkpoint is at `work/checkpoint/job.json`; it records completion, two incorporated pages, all six examined entry IDs, and no next cursor.

The authorized tranche was fully consumed: the final source description reported tranche 1 with 0 calls remaining. No further tranche is needed because source exhaustion and full record coverage were established within this tranche.

**Limitation:** No independent concurrency, filesystem-corruption, or source-implementation audit was performed. The result relies on the supplied immutable-source and stable-page API contract; the workflow's report and checkpoint passed the requested completion checks.
