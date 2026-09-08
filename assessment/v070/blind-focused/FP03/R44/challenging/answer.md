# Reimbursement rollup — incomplete

The authorized first tranche was used in full, but it did not exhaust the source. This is **not a final rollup**.

- Snapshot: `snap_fb322d1120ca406ad668bc26`
- Interval: `2026-06-10` through `2026-06-18`, inclusive
- Currency: USD
- Coverage: 6 of 15 source records incorporated
- Source exhausted: no
- Page calls committed: 2
- Observed tranche: 1
- Observed remaining calls: 0
- Pause reason: `tranche_boundary_reached`
- Uncertain page or checkpoint effects: none observed

The qualifying aggregates from the six incorporated records are partial and may change when the remaining nine records are examined:

| vendor_id | settled charges (cents) | settled credits (cents) | net charges − credits (cents) | qualifying entry count |
|---|---:|---:|---:|---:|
| azure | 5000 | 0 | 5000 | 1 |
| glacier | 700 | 700 | 0 | 2 |
| saffron | 0 | 900 | -900 | 1 |

Continuation evidence is saved at:

- Checkpoint: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/F-U012/work/reimbursement-2026-06-10_2026-06-18.checkpoint.json`
- Human-readable handoff: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/F-U012/work/reimbursement-2026-06-10_2026-06-18.handoff.json`

The checkpoint records incorporated entry IDs `chg-001` through `chg-006` and the exact next cursor `p_b62d3333e930f1830dd2d61eb80d3bbc`. After an operator grants or confirms new call capacity, continue by rerunning this identical command:

```sh
python3.12 /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/F-U012/skill/complete-reimbursement-rollup/scripts/reimbursement_rollup.py --api /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/F-U012/input/ledger_api.py --source-state /workspace/scratch/a75c3a6d9076/F-U012-ledger-state-_tu1uu31/ledger.sqlite --checkpoint /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/F-U012/work/reimbursement-2026-06-10_2026-06-18.checkpoint.json --output /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/F-U012/work/reimbursement-2026-06-10_2026-06-18.result.json --start 2026-06-10 --end 2026-06-18
```

No additional tranche was granted or requested, and no completed result file was produced.
