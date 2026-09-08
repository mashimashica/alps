# Reimbursement rollup — incomplete

The authorized first execution tranche was fully used. The workflow successfully fetched and committed two pages, examining **6 of 15 source records**. Because the returned next cursor is non-null and tranche 1 has no remaining page calls, this is **not a final rollup**. No further page call was attempted.

- **Snapshot:** `snap_fb322d1120ca406ad668bc26`
- **Inclusive interval:** `2026-06-10` through `2026-06-18`
- **Currency:** USD
- **Coverage:** 2 pages committed; 6/15 records examined
- **Current tranche:** 1
- **Observed remaining page calls:** 0 of 2

## Partial vendor rollup

These amounts include only settled entries in the requested interval among the six records examined so far. They are partial and may change when the remaining pages are incorporated.

| vendor_id | settled charges (cents) | settled credits (cents) | net charges − credits (cents) | qualifying entry count |
| --- | ---: | ---: | ---: | ---: |
| `azure` | 5000 | 0 | 5000 | 1 |
| `glacier` | 700 | 700 | 0 | 2 |
| `saffron` | 0 | 900 | -900 | 1 |

## Continuation evidence

- **Checkpoint:** `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/F-U016/work/checkpoints/job.json`
- **Partial report:** `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/F-U016/work/reports/report.json`
- **Source:** `/workspace/scratch/a75c3a6d9076/F-U016-ledger-state-0hc339br/ledger.sqlite`
- **API:** `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/F-U016/input/ledger_api.py`
- **Committed page cursors:** first-page cursor `null`, then `p_824dd208571a05a7d57ff5bd0e4889c0`
- **Incorporated entry IDs:** `chg-001`, `chg-002`, `chg-003`, `chg-004`, `chg-005`, `chg-006`
- **Exact next unincorporated cursor:** `p_b62d3333e930f1830dd2d61eb80d3bbc`

The checkpoint binds this source, snapshot, interval, examined-entry set, aggregates, and next cursor. A later continuation must retain the same source, API, checkpoint, output, start date, and end date, and may change only `--tranche` to a newly operator-approved tranche. No additional tranche was authorized here, so completion is limited by the remaining 9 unexamined records and the lack of approved quota.
