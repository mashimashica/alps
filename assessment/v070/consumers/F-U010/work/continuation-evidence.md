# Reimbursement rollup continuation evidence

This state is **incomplete**. It reflects only the first authorized execution tranche and must not be presented as the final reimbursement rollup.

## Request and source identity

- API: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/F-U010/input/ledger_api.py`
- Source state: `/workspace/scratch/a75c3a6d9076/F-U010-ledger-state-li1q88xs/ledger.sqlite`
- Snapshot: `snap_fb322d1120ca406ad668bc26`
- Inclusive interval: `2026-06-10` through `2026-06-18`
- Currency: USD

## Incorporation status

- Status: incomplete (`tranche_call_limit_reached`)
- Snapshot records incorporated/examined: 6 of 15
- Pages incorporated: 2
- Page cursors already incorporated, in order: initial page (`null`), then `p_824dd208571a05a7d57ff5bd0e4889c0`
- Entry IDs incorporated: `chg-001`, `chg-002`, `chg-003`, `chg-004`, `chg-005`, `chg-006`
- Exact next cursor: `p_b62d3333e930f1830dd2d61eb80d3bbc`
- Observed tranche: 1
- Remaining calls observed after the run: 0
- Successful page calls in this run: 2
- Uncertain response or incorporation status: none observed

## Partial qualifying totals

These totals cover only the six incorporated source records and are recovery evidence, not a final rollup.

| vendor_id | settled_charge_cents | settled_credit_cents | net_cents | qualifying_entry_count |
|---|---:|---:|---:|---:|
| azure | 5000 | 0 | 5000 | 1 |
| glacier | 700 | 700 | 0 | 2 |
| saffron | 0 | 900 | -900 | 1 |

## Continuation

The machine-readable checkpoint is:

`/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/F-U010/work/reimbursement-2026-06-10_2026-06-18.checkpoint.json`

After an operator grants another tranche, rerun the same bundled command with the same API path, source-state path, checkpoint path, and interval. The workflow will call unmetered `describe`, validate the source identity, and resume at the stored exact next cursor. Do not invoke `grant-tranche` as part of this workflow.
