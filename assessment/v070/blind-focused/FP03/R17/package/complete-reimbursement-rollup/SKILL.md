---
name: complete-reimbursement-rollup
description: Produce a complete vendor-level reimbursement rollup from an immutable paginated ledger snapshot for an inclusive posting-date interval. Use when settled charge and credit totals, net cents, and qualifying counts must cover every page despite per-tranche call limits and resumable execution.
---

# Complete reimbursement rollup

Use the bundled runner for the traversal and arithmetic. It validates the interval before accessing the source, saves a durable checkpoint around every metered page call, and withholds vendor totals until it has reconciled source exhaustion with the snapshot record count.

## Run or continue the request

Require four explicit inputs:

- inclusive `START_DATE` and `END_DATE` in `YYYY-MM-DD` form;
- the immutable source state database path;
- the source API Python file path;
- a checkpoint path dedicated to this request.

Then run from this Skill folder:

```sh
python3.12 scripts/reimbursement_rollup.py \
  --api /absolute/path/to/ledger_api.py \
  --source-state /absolute/path/to/source.sqlite \
  --checkpoint /absolute/path/to/request.checkpoint.json \
  --start START_DATE \
  --end END_DATE
```

Use the same command and checkpoint for every continuation. The checkpoint is bound to the resolved API path, source state, interval, snapshot ID, record count, and page size; the runner rejects incompatible reuse before making a page call. Do not edit the checkpoint.

Do not read the source database or setup fixture to obtain operational ledger entries. Do not assume source order is chronological, stop after a page lacking qualifying entries, or infer exhaustion from page length. Only a successfully processed response with `next_cursor: null` establishes exhaustion.

## Interpret the result

The runner writes one JSON object to stdout and uses these exit codes:

| Exit | Status | Action |
| --- | --- | --- |
| `0` | `complete` | Report the emitted interval, snapshot, coverage, and sorted vendor results. |
| `75` | `incomplete` | Do not report any rollup as final. Preserve the checkpoint and state paths. |
| `2` | `invalid_request` | Correct the interval, paths, or checkpoint/request mismatch before retrying. |
| `1` | `error` | Resolve the reported source, response-contract, or checkpoint error; do not claim completion. |

An incomplete result intentionally contains coverage metadata but no vendor aggregation. A two-call boundary is a pause, not reduced coverage. Tell the operator that the request remains incomplete and that they may grant another tranche through their source control. Never invoke `grant-tranche` on the operator's behalf. If a page call may have been counted without a usable response, keep the same checkpoint; a later retry of its recorded cursor is safe but may require a new tranche.

For a complete result, keep amounts as integer cents. The runner includes every vendor with at least one qualifying entry, including zero or negative net vendors, and sorts by `vendor_id`. An empty `vendors` list is final only when `status` is `complete` and coverage shows source exhaustion.

## Source setup boundary

If the user explicitly asks to create a disposable source from a fixture, create its parent directory and use the source API's `init` command once. Never reinitialize an existing state or replace a continuation with a fresh snapshot. `describe` is safe for checking metadata and quota because it is unmetered.

