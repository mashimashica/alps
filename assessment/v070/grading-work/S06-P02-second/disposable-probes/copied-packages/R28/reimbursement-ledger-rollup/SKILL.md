---
name: reimbursement-ledger-rollup
description: Produce complete vendor reimbursement rollups from an immutable, cursor-paginated ledger API, with exact cent arithmetic and safe continuation across approved call tranches. Use for settled charge/credit totals over an inclusive posting-date interval when every page must be covered.
---

# Reimbursement ledger rollup

Use the bundled `scripts/rollup.py` instead of manually paging or aggregating. It validates the interval before any API traversal, binds a checkpoint to the request and immutable snapshot, validates every response, deduplicates entry IDs, and writes progress atomically.

Run:

```sh
python3.12 scripts/rollup.py \
  --api /path/to/ledger_api.py \
  --state /path/to/source.sqlite \
  --checkpoint /path/to/request-checkpoint.json \
  --from-date YYYY-MM-DD \
  --through-date YYYY-MM-DD
```

Use a unique checkpoint path for each request. On later approved tranches, run the identical command with the same checkpoint. Never invoke the API's operator-only `grant-tranche` control; the operator decides whether to grant another tranche.

Interpret the one-object JSON output:

- `status: "complete"` is the only final business result. Report its ordered `vendors`, inclusive `date_interval`, and `snapshot_id`. Preserve zero and negative nets. Amounts are integer USD cents.
- `status: "incomplete"` means the source is not exhausted. State that no final rollup is available, retain the checkpoint, and wait for a later approved tranche. Do not present checkpoint progress or any partial aggregation as the answer.
- `status: "error"` means the request or source could not be safely processed. Report the error and do not claim completion.

Completion depends only on observing a valid page with `next_cursor: null`; metadata counts are consistency evidence, not an exhaustion signal. Do not edit the checkpoint. If a page response was lost or execution was interrupted, rerun the same command: repeated pages are safe because entry IDs are recorded and counted once. Do not change dates, API path, state path, or snapshot when continuing; start a new checkpoint for a new request.

The script uses Python 3.12 standard library only. `--help` documents optional output and diagnostic fields. The checkpoint can contain source entries and is operational state; store it accordingly.
