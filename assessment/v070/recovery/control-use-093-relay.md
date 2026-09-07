# Control-use-093 recovery relay

## Preservation status

This relay preserves evidence from the already-ended `control-use-093` trial using only retained successful tool-call text and output from the original conversation. The original workspace was reported disconnected (`409 environment_offline`) during recovery, so no filesystem or business tool was used, no workflow was rerun, and no current-byte or hash claim is made for any original local artifact.

## Recovered artifact: `answer.md`

- Original path: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U093/answer.md`
- Provenance: full text retained in the successful `apply_patch` payload from the original trial. The patch tool returned `{}` without an error. This is a textual recovery from the retained call record, not a read of the disconnected filesystem.

```markdown
# Complete vendor reimbursement rollup

- **Snapshot:** `snap_c22e71aa06b43ab25395e0ce`
- **Interval:** 2026-04-03 through 2026-04-09, inclusive
- **Currency:** USD
- **Coverage:** Complete — 6 of 6 source records examined across 2 committed pages

| Vendor ID | Settled charges (cents) | Settled credits (cents) | Net charges − credits (cents) | Qualifying entries |
|---|---:|---:|---:|---:|
| `apricot` | 1,234 | 1,234 | 0 | 2 |
| `juniper` | 2,501 | 0 | 2,501 | 1 |
| `willow` | 0 | 407 | -407 | 1 |

The complete checkpoint and continuation evidence is at `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U093/work/reimbursement-rollup-2026-04-03_2026-04-09.sqlite`. The terminal page was committed, so there is no next cursor and no continuation tranche is required.
```

## Recovered artifact: `execution-note.md`

- Original path: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U093/execution-note.md`
- Provenance: full text retained in the same successful `apply_patch` payload from the original trial. This is a textual recovery from the retained call record, not a read of the disconnected filesystem.

````markdown
# Public execution note

## Outcome

The supplied runner completed the request in the authorized tranche. Its exact captured result reported `complete: true`, 2 committed pages, 6 examined records, and 6 total records. No continuation or additional tranche was required.

## Commands and observations

1. `cat prompt.md`
   - Working directory: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U093`
   - Exit code: `0`
   - Captured observation (summary): directed use of the supplied skill and request, required `answer.md` via `apply_patch`, allowed temporary outputs under `work`, and required this execution note.

2. Concurrent read commands:
   - `cat skill/reimbursement-ledger-rollup/SKILL.md` — exit code `0`.
   - `cat input/request.md` — exit code `0`.
   - `rg --files input skill/reimbursement-ledger-rollup` — exit code `0`.
   - Relevant exact file-list stdout:

     ```text
     skill/reimbursement-ledger-rollup/references/verification.md
     skill/reimbursement-ledger-rollup/scripts/rollup.py
     skill/reimbursement-ledger-rollup/SKILL.md
     input/ledger_api.py
     input/request.md
     ```

   - Captured observation (summary): the skill requires the bundled runner, exact integer cents, exhaustive cursor traversal, and accepts only exit code 0 with `complete: true` as final. The request authorized at most two successful page calls and supplied the interval, API, and source paths.

3. `mkdir -p work`
   - Working directory: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U093`
   - Exit code: `0`
   - Stdout/stderr: empty.

4. `python3.12 /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U093/skill/reimbursement-ledger-rollup/scripts/rollup.py --api /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U093/input/ledger_api.py --source /workspace/scratch/a75c3a6d9076/C-U093-ledger-state-7b_kk2bk/ledger.sqlite --checkpoint /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U093/work/reimbursement-rollup-2026-04-03_2026-04-09.sqlite --start 2026-04-03 --end 2026-04-09`
   - Working directory: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U093`
   - Exit code: `0`
   - Exact stdout:

     ```json
     {"checkpoint": "/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U093/work/reimbursement-rollup-2026-04-03_2026-04-09.sqlite", "committed_pages": 2, "complete": true, "currency": "USD", "examined_records": 6, "interval": {"end": "2026-04-09", "inclusive": true, "start": "2026-04-03"}, "snapshot_id": "snap_c22e71aa06b43ab25395e0ce", "total_records": 6, "vendors": [{"net_cents": 0, "qualifying_entry_count": 2, "settled_charge_cents": 1234, "settled_credit_cents": 1234, "vendor_id": "apricot"}, {"net_cents": 2501, "qualifying_entry_count": 1, "settled_charge_cents": 2501, "settled_credit_cents": 0, "vendor_id": "juniper"}, {"net_cents": -407, "qualifying_entry_count": 1, "settled_charge_cents": 0, "settled_credit_cents": 407, "vendor_id": "willow"}]}
     ```

   - Stderr: empty.

## Files used or created

- Read: `prompt.md`
- Read: `skill/reimbursement-ledger-rollup/SKILL.md`
- Executed without modification: `skill/reimbursement-ledger-rollup/scripts/rollup.py`
- Used through the runner without reading its contents: `input/ledger_api.py`
- Read: `input/request.md`
- Supplied source passed only to the trusted API: `/workspace/scratch/a75c3a6d9076/C-U093-ledger-state-7b_kk2bk/ledger.sqlite`
- Created/modified by the runner: `work/reimbursement-rollup-2026-04-03_2026-04-09.sqlite` and any transient SQLite journal used during execution
- Created via `apply_patch`: `answer.md` and `execution-note.md`

## Checks not performed

The source database and its sidecars were not inspected directly. The API source was not read, no page was fetched manually, `grant-tranche` was not invoked, and the optional verification reference was not consulted. Completion is based on the runner's exit code 0 and exact `complete: true` output.
````

## Retained work evidence and unavailable scope

- The exact runner stdout is retained inside the recovered execution note above. It identifies snapshot `snap_c22e71aa06b43ab25395e0ce`, interval 2026-04-03 through 2026-04-09 inclusive, checkpoint path, two committed pages, six examined of six total records, and the complete vendor totals.
- The original checkpoint path was `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U093/work/reimbursement-rollup-2026-04-03_2026-04-09.sqlite`.
- The checkpoint was a SQLite binary. Its bytes or SQL dump were not retained in the conversation, so no checkpoint file content, hash, size, or current filesystem state is recovered or claimed here.
- No transient SQLite journal bytes or text were retained.
- No other work-file text was captured in the original conversation.
- The supplied source database, API, request, skill, and runner are not recovery outputs and are not reproduced in this relay.
