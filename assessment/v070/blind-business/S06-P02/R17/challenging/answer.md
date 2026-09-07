# Incomplete reimbursement rollup

**Status: INCOMPLETE — paused after the authorized first tranche.** The workflow successfully incorporated two pages (6 of 15 source records), and the source now reports zero calls remaining in tranche 1. A null next cursor has not been observed, so this is a partial rollup and must not be treated as final.

- Source state: `/workspace/scratch/a75c3a6d9076/C-U074-ledger-state-b0_9cwyq/ledger.sqlite`
- Snapshot: `snap_fb322d1120ca406ad668bc26`
- Inclusive interval: `2026-06-10` through `2026-06-18`
- Filter: settled entries only

## Partial rollup after the two incorporated pages

| vendor_id | settled charges (USD cents) | settled credits (USD cents) | net charges − credits (USD cents) | qualifying entry count |
|---|---:|---:|---:|---:|
| azure | 5,000 | 0 | 5,000 | 1 |
| glacier | 700 | 700 | 0 | 2 |
| saffron | 0 | 900 | -900 | 1 |

These totals include 4 qualifying entries among the first 6 source records. Vendors and entries on later pages are not yet represented.

## Exact continuation state

Checkpoint: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U074/work/reimbursement-rollup-checkpoint.json`

```json
{"cursor":"p_b62d3333e930f1830dd2d61eb80d3bbc","end":"2026-06-18","seen_cursors":[null,"p_824dd208571a05a7d57ff5bd0e4889c0"],"snapshot_id":"snap_fb322d1120ca406ad668bc26","start":"2026-06-10","totals":{"azure":{"charge_cents":5000,"credit_cents":0,"entry_count":1},"glacier":{"charge_cents":700,"credit_cents":700,"entry_count":2},"saffron":{"charge_cents":0,"credit_cents":900,"entry_count":1}}}
```

Pages incorporated, in order:

1. Initial page requested without a cursor (`null` checkpoint cursor).
2. Page requested with returned cursor `p_824dd208571a05a7d57ff5bd0e4889c0`.

The exact next returned cursor is `p_b62d3333e930f1830dd2d61eb80d3bbc`. After a later operator grants another tranche, continuation must reuse the same API, source state, snapshot, interval, and checkpoint. The workflow will resume with that cursor. Current observed API state is tranche `1`, `remaining_calls: 0`, page size `3`, total source records `15`.

The checkpoint records aggregate qualifying-entry evidence rather than individual entry IDs. There is no uncertainty about response incorporation: each of the two successful page responses was incorporated before its cursor and totals were persisted. Completion requires further operator approval and a new tranche, which was not granted for this task.
