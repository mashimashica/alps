# Reimbursement rollup — incomplete

The rollup for **2026-06-10 through 2026-06-18, inclusive** is **incomplete**. The authorized first tranche was exhausted after its maximum of two successful `page` calls. The source returned a non-null next cursor, so source exhaustion has not been established and these figures must not be treated as final.

- Snapshot: `snap_fb322d1120ca406ad668bc26`
- Source records described: 15
- Pages incorporated: 2
- Source records incorporated: 6 (`chg-001` through `chg-006`)
- Tranche: 1
- Calls allowed per tranche: 2
- Remaining calls observed after the run: 0
- Exact next cursor: `p_b62d3333e930f1830dd2d61eb80d3bbc`

## Provisional vendor rollup

| vendor_id | settled charges (cents) | settled credits (cents) | net, charges − credits (cents) | qualifying entry count |
|---|---:|---:|---:|---:|
| `azure` | 5000 | 0 | 5000 | 1 |
| `glacier` | 700 | 700 | 0 | 2 |
| `saffron` | 0 | 900 | -900 | 1 |

Only settled USD entries in the requested inclusive interval are included in these provisional totals. Four of the six incorporated source records qualified. No page response or incorporation status is uncertain.

## Continuation evidence

The durable checkpoint is at:

`/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U078/work/rollup-checkpoint.json`

Its full contents are:

```json
{"from_date":"2026-06-10","next_cursor":"p_b62d3333e930f1830dd2d61eb80d3bbc","pages_fetched":2,"seen_entry_ids":["chg-001","chg-002","chg-003","chg-004","chg-005","chg-006"],"snapshot_id":"snap_fb322d1120ca406ad668bc26","source_state":"/workspace/scratch/a75c3a6d9076/C-U078-ledger-state-sonui0_n/ledger.sqlite","to_date":"2026-06-18","total_records":15,"totals":{"azure":{"charge_cents":5000,"credit_cents":0,"qualifying_entry_count":1},"glacier":{"charge_cents":700,"credit_cents":700,"qualifying_entry_count":2},"saffron":{"charge_cents":0,"credit_cents":900,"qualifying_entry_count":1}},"version":1}
```

A later operator can continue this exact request after granting another tranche by rerunning the same rollup command with this checkpoint. The checkpoint pins the state path, snapshot, interval, incorporated entry IDs, totals, and exact returned cursor so incorporated pages are not counted twice. No additional tranche was granted or used here.
