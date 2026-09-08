# Complete vendor reimbursement rollup

The rollup is complete for immutable snapshot `snap_c22e71aa06b43ab25395e0ce` and the inclusive posting-date interval **2026-04-03 through 2026-04-09**. The workflow examined **6 of 6 entries** across **2 committed pages** and observed a null next cursor, establishing source exhaustion within the authorized two successful page calls. Currency is **USD**; all amounts below are exact integer cents.

| vendor_id | settled charges (cents) | settled credits (cents) | net charges minus credits (cents) | qualifying entry count |
|---|---:|---:|---:|---:|
| apricot | 1,234 | 1,234 | 0 | 2 |
| juniper | 2,501 | 0 | 2,501 | 1 |
| willow | 0 | 407 | -407 | 1 |

The resumable checkpoint is `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/F-U013/work/request.json`, and the machine-readable completed result is `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/F-U013/work/result.json`. There is no incomplete-work limitation or need for another execution tranche.
