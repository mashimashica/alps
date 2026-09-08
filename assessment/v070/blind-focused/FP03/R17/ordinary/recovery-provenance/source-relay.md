# C-U085 recovery relay

This supplemental preservation was assembled only from retained successful tool-call text and output in the completed C-U085 conversation after the workspace became unavailable. It does not claim a fresh filesystem check or rerun. Paths below retain their original provenance.

## Recovered original `answer.md`

Original path: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U085/answer.md`

```markdown
# Complete reimbursement rollup

- **Snapshot:** `snap_c22e71aa06b43ab25395e0ce`
- **Inclusive posting-date interval:** `2026-04-03` through `2026-04-09`
- **Status:** Complete; source exhaustion was established by a successfully processed response with a null next cursor.
- **Coverage:** 2 pages processed, 6 of 6 source records examined.

| vendor_id | settled charges (USD cents) | settled credits (USD cents) | net cents | qualifying entry count |
|---|---:|---:|---:|---:|
| `apricot` | 1,234 | 1,234 | 0 | 2 |
| `juniper` | 2,501 | 0 | 2,501 | 1 |
| `willow` | 0 | 407 | -407 | 1 |

The rollup includes only settled entries posted within the requested inclusive interval. It retains the zero-net vendor (`apricot`) and negative-net vendor (`willow`) and is sorted by `vendor_id`.
```

## Recovered original `execution-note.md`

Original path: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U085/execution-note.md`

```markdown
# Public execution note

## Files used

- `prompt.md`
- `skill/complete-reimbursement-rollup/SKILL.md`
- `skill/complete-reimbursement-rollup/scripts/reimbursement_rollup.py`
- `input/request.md`
- `input/ledger_api.py`
- `/workspace/scratch/a75c3a6d9076/C-U085-ledger-state-ub66sp7k/ledger.sqlite` (passed to the supplied API through the bundled runner; not read or queried directly)
- `work/reimbursement-2026-04-03_2026-04-09.checkpoint.json` (created and managed by the bundled runner)

## Read and discovery commands

All commands below exited `0`.

```sh
cat prompt.md
find . -maxdepth 1 -type f -printf '%f\n' | sort
cat skill/complete-reimbursement-rollup/SKILL.md
cat input/request.md
find input -maxdepth 2 -type f -printf '%p\n' | sort
find skill/complete-reimbursement-rollup -maxdepth 3 -type f -printf '%p\n' | sort
```

Relevant observations: the task supplied only `input/request.md` and `input/ledger_api.py`; the supplied Skill contained `SKILL.md` and `scripts/reimbursement_rollup.py`. No fixture, database content, sidecar, creator prompt, sibling trial, evaluation material, or quota control was read.

## Rollup command

Working directory: `skill/complete-reimbursement-rollup`

```sh
mkdir -p work && python3.12 scripts/reimbursement_rollup.py \
  --api /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U085/input/ledger_api.py \
  --source-state /workspace/scratch/a75c3a6d9076/C-U085-ledger-state-ub66sp7k/ledger.sqlite \
  --checkpoint /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U085/work/reimbursement-2026-04-03_2026-04-09.checkpoint.json \
  --start 2026-04-03 \
  --end 2026-04-09; rc=$?; echo "__EXIT_CODE__=$rc"; exit 0
```

Rollup exit code: `0`

Exact stdout:

```json
{"coverage":{"pages_processed":2,"records_examined":6,"source_exhausted":true,"total_records":6},"interval":{"end":"2026-04-09","start":"2026-04-03"},"snapshot_id":"snap_c22e71aa06b43ab25395e0ce","status":"complete","vendors":[{"net_cents":0,"qualifying_entry_count":2,"settled_charge_cents":1234,"settled_credit_cents":1234,"vendor_id":"apricot"},{"net_cents":2501,"qualifying_entry_count":1,"settled_charge_cents":2501,"settled_credit_cents":0,"vendor_id":"juniper"},{"net_cents":-407,"qualifying_entry_count":1,"settled_charge_cents":0,"settled_credit_cents":407,"vendor_id":"willow"}]}
```

Stderr was empty. The run completed within the authorized tranche after exactly 2 successfully processed pages and established source exhaustion, so no continuation or additional tranche was needed. `grant-tranche` and `init` were not invoked.

## File verification

Command (working directory: consumer folder):

```sh
test -s answer.md && test -s execution-note.md && test -s work/reimbursement-2026-04-03_2026-04-09.checkpoint.json && wc -c answer.md execution-note.md work/reimbursement-2026-04-03_2026-04-09.checkpoint.json
```

Exit code: `0`

Exact stdout at verification time:

```text
 787 answer.md
2540 execution-note.md
 969 work/reimbursement-2026-04-03_2026-04-09.checkpoint.json
4296 total
```

Stderr was empty. The execution note was then updated with this verification record, so its final byte size is larger than the captured pre-update size shown above.
```

## Retained run output and unavailable scope

The runner's exact stdout is preserved inside the recovered execution note above. The conversation also retained that the runner's tool wrapper printed `__EXIT_CODE__=0`.

The checkpoint was reported at the original path `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U085/work/reimbursement-2026-04-03_2026-04-09.checkpoint.json`, and the pre-update verification reported it as 969 bytes. Its actual file text was never captured in the conversation and is therefore unavailable; no checkpoint content is reconstructed here.

The original prompt, request, Skill, runner, API, ledger state, and other workspace files are not embedded in this relay. Their paths or names appear only where they were retained in the recovered execution note. No new hashes, current byte sizes, or current filesystem observations are asserted.
