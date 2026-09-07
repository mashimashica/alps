---
name: reimbursement-ledger-rollup
description: Produce a complete vendor-level reimbursement rollup from an immutable cursor-paginated ledger snapshot, including safe continuation across limited API-call tranches. Use when settled charges and credits must be aggregated exactly over an inclusive posting-date interval without skipping later pages or double counting retries.
---

# Reimbursement ledger rollup

Use `scripts/rollup.py` for the traversal and exact integer-cent aggregation. It maintains a durable checkpoint, validates every page and item, and emits JSON that distinguishes a complete result from a pause at the current tranche boundary.

## Inputs

Obtain these explicit local paths and dates:

- the source API program implementing the supplied `describe` and `page` commands;
- its existing immutable source-state database;
- a checkpoint path dedicated to this request;
- inclusive `YYYY-MM-DD` start and end dates.

Run from any directory:

```sh
python3.12 /path/to/reimbursement-ledger-rollup/scripts/rollup.py \
  --api /path/to/ledger_api.py \
  --source-state /path/to/source.sqlite \
  --checkpoint /path/to/request-checkpoint.json \
  --start 2026-02-01 \
  --end 2026-02-15
```

Use the identical command to continue after the operator grants another tranche. Keep the same source state, checkpoint, dates, and API. The script rejects request or snapshot changes. Do not initialize or replace a source state while continuing.

## Interpret the output

- `status: "complete"` is the only final business result. Report its `vendors` in the emitted order and identify `snapshot_id` and `interval`. Amount fields are exact integer US cents. Keep vendors with zero or negative `net_amount_cents`.
- `status: "incomplete"` means coverage has paused. Do not present `partial_vendors` as final. Report the progress fields and ask the operator whether to grant a further tranche. The operator, rather than this skill or script, controls `grant-tranche`. If no new tranche is authorized, leave the request incomplete and make no completion promise.

The script uses all currently available successful calls, stopping when `describe` reports no remaining calls or when the API returns `call_budget_exhausted`. A failed page response is never treated as exhaustion of the ledger. Resume using the stored cursor; never invent, decode, or alter a cursor.

The script validates the interval before calling the source. It treats a null `next_cursor` as the sole exhaustion signal, including for an empty ledger. Completion also requires the number of distinct examined entries to equal source metadata `total_records`. Pending, void, out-of-range, and otherwise nonqualifying entries still count as examined coverage but do not affect vendor totals.

## Recovery and checkpoint care

Keep the checkpoint even if a page call's response appears lost. Re-run the same command after checking or obtaining tranche capacity. The checkpoint is written atomically after each received page; replayed entries are deduplicated by `entry_id`, preventing repeated pages from changing totals.

Do not edit the checkpoint. If it is missing or damaged after traversal began, a new traversal requires a fresh checkpoint and enough newly approved API capacity to examine the entire snapshot again. Do not combine partial totals manually.

