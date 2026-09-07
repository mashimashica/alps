# Incomplete reimbursement rollup

The rollup is **incomplete**. The authorized first tranche was fully consumed after two successful `page` calls, and the source reports zero calls remaining in tranche 1. No further tranche is authorized, so source exhaustion has not been established and the values below must not be treated as final.

- Source snapshot: `snap_fb322d1120ca406ad668bc26`
- Inclusive posting-date interval: `2026-06-10` through `2026-06-18`
- Source coverage: 2 pages incorporated; 6 of 15 source entries examined
- Incorporated entry IDs: `chg-001`, `chg-002`, `chg-003`, `chg-004`, `chg-005`, `chg-006`
- Exact next cursor: `p_b62d3333e930f1830dd2d61eb80d3bbc`
- Observed quota: tranche 1; 2 calls per tranche; 0 calls remaining
- Incorporation uncertainty: none observed; both fetched pages are recorded as incorporated in the checkpoint

## Partial, non-final vendor totals

These totals cover only the two incorporated pages and are sorted by `vendor_id`.

| vendor_id | settled charges (cents) | settled credits (cents) | net charges minus credits (cents) | qualifying entry count |
|---|---:|---:|---:|---:|
| `azure` | 5000 | 0 | 5000 | 1 |
| `glacier` | 700 | 700 | 0 | 2 |
| `saffron` | 0 | 900 | -900 | 1 |

Continuation evidence is saved at `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U088/work/reimbursement-2026-06-10-through-2026-06-18.checkpoint.json`. It binds the API path, source-state path, snapshot, interval, incorporated entry IDs, aggregates, page count, and exact next cursor.

If an operator later grants another tranche, continue by rerunning this exact command with the same checkpoint:

```sh
python3.12 skill/reimbursement-ledger-rollup/scripts/reimbursement_rollup.py \
  --api /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U088/input/ledger_api.py \
  --source-state /workspace/scratch/a75c3a6d9076/C-U088-ledger-state-yi5gom8w/ledger.sqlite \
  --checkpoint /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U088/work/reimbursement-2026-06-10-through-2026-06-18.checkpoint.json \
  --start 2026-06-10 \
  --end 2026-06-18
```

