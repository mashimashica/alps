# Reimbursement rollup — incomplete after authorized tranche

The authorized first execution tranche was completed, but the immutable source was **not exhausted**. The workflow examined **6 of 15 entries** across **2 committed pages** and returned a non-null continuation cursor. Therefore, the figures below are **provisional**, not a final rollup.

- Snapshot: `snap_fb322d1120ca406ad668bc26`
- Inclusive posting-date interval: `2026-06-10` through `2026-06-18`
- Currency: `USD`
- Status: **incomplete** (`awaiting_operator_tranche`)
- Coverage: **6 / 15 entries examined**
- Observed source tranche: **1**
- Observed remaining page-call quota: **0 of 2**

## Provisional vendor totals from the 6 incorporated entries

| vendor_id | settled charges (cents) | settled credits (cents) | net charges − credits (cents) | qualifying entry count |
|---|---:|---:|---:|---:|
| `azure` | 5000 | 0 | 5000 | 1 |
| `glacier` | 700 | 700 | 0 | 2 |
| `saffron` | 0 | 900 | -900 | 1 |

These rows retain the observed zero and negative nets. Entries on later pages may add vendors or change any provisional vendor total. In particular, no conclusion can yet be made about every vendor requested, including a possible vendor whose only qualifying entry is zero, until a null `next_cursor` is observed.

## Exact continuation evidence

- Source state: `/workspace/scratch/a75c3a6d9076/F-U014-ledger-state-nh3496m8/ledger.sqlite`
- Snapshot: `snap_fb322d1120ca406ad668bc26`
- Interval: `2026-06-10` through `2026-06-18`, inclusive
- Page 1 request cursor: `null`; incorporated records: `chg-001`, `chg-002`, `chg-003`
- Page 2 request cursor: `p_824dd208571a05a7d57ff5bd0e4889c0`; incorporated records: `chg-004`, `chg-005`, `chg-006`
- Exact next cursor: `p_b62d3333e930f1830dd2d61eb80d3bbc`
- Committed pages: `2`
- Incorporated records: `6`
- Exhaustion marker: `false`
- Observed tranche / remaining quota after the run: `1` / `0`
- Checkpoint: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/F-U014/work/request.json`
- Partial result: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/F-U014/work/result.json`

A later operator can continue this exact request by granting another tranche and rerunning the same command with the same checkpoint, source, snapshot-bound state, and interval. No further tranche was authorized here, so no additional page call was attempted.
