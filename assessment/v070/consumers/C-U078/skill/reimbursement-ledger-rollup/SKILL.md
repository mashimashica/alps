---
name: reimbursement-ledger-rollup
description: Produce a complete vendor-level reimbursement rollup from an immutable paginated ledger snapshot. Use when an analyst supplies an inclusive posting-date interval and a local ledger_api.py state path. The bundled runner uses exact integer US cents, scans every page across operator-granted tranches, checkpoints after each successful page, and reports incomplete work without presenting it as final.
---

# Reimbursement ledger rollup

Use the bundled `scripts/rollup.py` runner to read the source API. The runner is the operational interface: do not read the source SQLite tables or fixture as a substitute for paging through the API.

## Inputs

- `--state`: absolute path to the initialized `ledger_api.py` SQLite state.
- `--api`: path to the supplied `ledger_api.py` stand-in.
- `--from` and `--to`: inclusive ISO dates (`YYYY-MM-DD`).
- `--checkpoint`: a durable JSON checkpoint path in a writable working directory.

The source snapshot is selected from `describe` on the first run. A checkpoint pins the snapshot, interval, and source path; later runs must use the same values. Create a new checkpoint for a different interval or snapshot. The runner validates the interval before any source call, so an invalid interval is reported without traversal.

Example:

```sh
python3.12 scripts/rollup.py \
  --state /absolute/disposable/source.sqlite \
  --api /absolute/path/ledger_api.py \
  --from 2026-02-01 --to 2026-02-15 \
  --checkpoint /absolute/disposable/rollup.json
```

Run the same command again to continue a checkpoint after the operator grants another tranche with the source simulator. The runner never invokes `grant-tranche`.

## Output and continuation

The runner emits one JSON document to stdout and returns:

- `0` with `status: "complete"` only after `next_cursor` is null and all source records reported by `describe` have been observed. `result.rows` is sorted by `vendor_id` and contains `settled_charge_cents`, `settled_credit_cents`, `net_cents` (charge minus credit), and `qualifying_entry_count`. Only vendors with qualifying entries appear, including vendors whose net is zero or negative. The document identifies the inclusive interval and snapshot.
- `75` with `status: "incomplete"` when the current two-call tranche is exhausted. `partial_rows` is explicitly provisional; it is not a final result. The checkpoint contains the last incorporated page and its returned cursor. Grant a tranche externally, then rerun the same command.
- `75` with `status: "recovery_required"` when a successful page call produced no usable JSON response. The call may have been counted, so do not retry within the same tranche unless the operator understands that risk; keep the checkpoint and rerun after a new tranche. A valid response can be repeated safely because already-seen `entry_id` values are ignored.
- `2` for invalid arguments, mismatched checkpoint metadata, malformed source data, or an API error other than budget exhaustion. The JSON error explains the problem and the checkpoint remains intact.

Pending and void entries, entries outside the interval, and all non-USD or malformed records are rejected or excluded according to the source contract. Arithmetic stays in integer cents. An empty source or an interval with no qualifying entries completes with an empty `result.rows` array.

The runner persists the checkpoint atomically after each successful page. It validates snapshot identity, page metadata, item fields, cursor progression, and total-record coverage. A repeated page is not counted twice. It does not infer a missing page after a lost response and cannot make a completion promise without a later operator-granted tranche.
