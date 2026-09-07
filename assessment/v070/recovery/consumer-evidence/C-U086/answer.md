# Reimbursement rollup — incomplete

The request is **incomplete** because the authorized first tranche ended after two successful `page` calls. No final vendor rollup can be reported until the source returns `next_cursor: null`.

- Inclusive interval: **2026-06-10 through 2026-06-18**
- Snapshot: `snap_fb322d1120ca406ad668bc26`
- Coverage: **2 pages processed; 6 of 15 source records examined**
- Source exhausted: **no**
- Source tranche: **1**
- Remaining calls in the tranche: **0**

The checkpoint's provisional accumulator currently contains the following qualifying entries. These are **partial values, not final totals**; later pages may change these vendors or add others.

| vendor_id | settled charges (cents) | settled credits (cents) | net charges − credits (cents) | qualifying entry count |
| --- | ---: | ---: | ---: | ---: |
| azure | 5,000 | 0 | 5,000 | 1 |
| glacier | 700 | 700 | 0 | 2 |
| saffron | 0 | 900 | -900 | 1 |

Continuation evidence is saved at:

`/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U086/work/reimbursement-rollup.checkpoint.json`

Its full contents are:

```json
{"calls_per_tranche":2,"inflight_cursor":null,"next_cursor":"p_b62d3333e930f1830dd2d61eb80d3bbc","page_size":3,"pages_processed":2,"records_examined":6,"request":{"api":"/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U086/input/ledger_api.py","checkpoint":"/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U086/work/reimbursement-rollup.checkpoint.json","end":"2026-06-18","source_state":"/workspace/scratch/a75c3a6d9076/C-U086-ledger-state-a619nv43/ledger.sqlite","start":"2026-06-10"},"seen_entry_ids":["chg-001","chg-002","chg-003","chg-004","chg-005","chg-006"],"snapshot_id":"snap_fb322d1120ca406ad668bc26","status":"in_progress","total_records":15,"vendors":{"azure":{"qualifying_entry_count":1,"settled_charge_cents":5000,"settled_credit_cents":0},"glacier":{"qualifying_entry_count":2,"settled_charge_cents":700,"settled_credit_cents":700},"saffron":{"qualifying_entry_count":1,"settled_charge_cents":0,"settled_credit_cents":900}},"version":1}
```

The exact next returned cursor is `p_b62d3333e930f1830dd2d61eb80d3bbc`. `inflight_cursor` is `null`, so the checkpoint records no uncertain response or page awaiting incorporation. After an operator grants another tranche, continue with the same runner command and the same checkpoint; do not start a new snapshot or alter the cursor.
