# Incomplete reimbursement rollup

The authorized first tranche is exhausted, so this result is **incomplete** and the amounts below are provisional. Two pages containing 6 of 15 source records were incorporated. Nine records remain unexamined, and source exhaustion has not been established because the saved next cursor is non-null.

- Snapshot: `snap_fb322d1120ca406ad668bc26`
- Inclusive posting-date interval: `2026-06-10` through `2026-06-18`
- Currency: USD

| vendor_id | settled charges (cents) | settled credits (cents) | net charges minus credits (cents) | qualifying entry count |
|---|---:|---:|---:|---:|
| azure | 5000 | 0 | 5000 | 1 |
| glacier | 700 | 700 | 0 | 2 |
| saffron | 0 | 900 | -900 | 1 |

These provisional totals include only qualifying entries among the six incorporated records. They must not be treated as a final rollup.

Continuation evidence is saved at `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U090/work/reimbursement-rollup-2026-06-10_2026-06-18.json`. It is bound to this source path, API path, snapshot, interval, and source record count.

- Incorporated page requests: initial cursor `null`, then cursor `p_824dd208571a05a7d57ff5bd0e4889c0`
- Incorporated record IDs: `chg-001`, `chg-002`, `chg-003`, `chg-004`, `chg-005`, `chg-006`
- Exact next cursor: `p_b62d3333e930f1830dd2d61eb80d3bbc`
- Observed source control: tranche `1`, `0` of `2` calls remaining
- Incorporation uncertainty: none observed; the checkpoint records both accepted pages atomically

Continuation requires a later operator-approved tranche. Preserve the checkpoint and rerun the identical rollup command after approval; no further tranche was granted or requested here.
