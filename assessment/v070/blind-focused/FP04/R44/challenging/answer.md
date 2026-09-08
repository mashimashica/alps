# Reimbursement rollup — incomplete

The requested rollup for **2026-06-10 through 2026-06-18, inclusive** is **incomplete**. The source snapshot is `snap_fb322d1120ca406ad668bc26`, in USD integer cents.

The authorized first execution tranche was exhausted after exactly two successful `page` calls. The workflow examined and durably incorporated **6 of 15** source records. Because source order is nonchronological and 9 records remain unexamined, no vendor totals are presented as final or partial rollup results.

Continuation evidence is saved at:

`/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U096/work/request.json`

Exact saved continuation state:

- Snapshot: `snap_fb322d1120ca406ad668bc26`
- Interval: `2026-06-10` through `2026-06-18`, inclusive
- Total source records: 15
- Incorporated pages: initial cursor `null`, then cursor `p_824dd208571a05a7d57ff5bd0e4889c0`
- Incorporated record IDs: `chg-001`, `chg-002`, `chg-003`, `chg-004`, `chg-005`, `chg-006`
- Exact next cursor: `p_b62d3333e930f1830dd2d61eb80d3bbc`
- Observed source tranche: 1
- Observed remaining calls: 0 of 2
- Incorporation uncertainty: none; the checkpoint contains both incorporated cursors and all six fetched records, and points to the next returned cursor

No further tranche was granted, so execution is paused. A later operator-approved continuation must reuse the same checkpoint, restored source state, adapter, snapshot binding, interval, and exact next cursor. The original request's obsolete state-path literal was replaced, as directed during recovery, with `/workspace/scratch/a75c3a6d9076/C-U096-ledger-recovery-initial-001/ledger.sqlite`.
