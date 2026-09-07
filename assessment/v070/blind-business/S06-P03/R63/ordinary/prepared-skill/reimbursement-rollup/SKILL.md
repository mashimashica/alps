---
name: reimbursement-rollup
description: Compute complete vendor reimbursement totals from an immutable paginated ledger, with exact cents and durable continuation across operator-approved call tranches. Use for inclusive posting-date rollups of settled charges and credits.
---

# Reimbursement rollup

Obtain the inclusive start/end dates, the explicit existing source state, and the supplied `ledger_api.py` path. Use Python 3.12 and the standard-library [helper](scripts/rollup.py); no installation is needed. The API is an operational dependency supplied by the caller, not bundled data. Never read its fixture or database to obtain operational entries.

Run (replace paths and dates):

```sh
python3.12 /path/to/reimbursement-rollup/scripts/rollup.py --api /path/to/ledger_api.py --state /path/to/source.sqlite --checkpoint /path/to/request.json --start 2026-02-01 --end 2026-02-15
```

Choose a new checkpoint per request. Preserve it and its `.lock` sidecar across continuations; use the identical command to resume. The helper binds dates, source path, API path and snapshot, holds a process lock, and atomically commits each page's entries and next cursor together. It stores all examined entries to support exact reconstruction and duplicate detection. Budget requirements apply to successful calls, including retries. A lost response leaves the previous checkpoint intact: resumption describes remaining quota before retrying the same cursor. Never delete a checkpoint to bypass quota or guess a cursor.

Exit 0 with `status: complete` is final; only source `next_cursor: null` plus verified record-count coverage permits this. Output identifies snapshot and interval, sorted vendors, charge/credit/net integer USD cents and qualifying entry count. Zero and negative net vendors remain. Empty results are valid. Never stop early based on dates or source order.

Exit 75 with `status: incomplete` is a checkpointed pause, not a final rollup. Report examined/total counts and that further operator-approved work is required. Ask the operator for another tranche; do not invoke `grant-tranche`, initialize replacement states, or promise eventual completion. Once the operator grants a tranche, resume the same command. If approval never arrives, leave the request incomplete. Partial output deliberately omits vendor totals.

Exit 2 reports an input, source, checkpoint or integrity error. Correct the issue without changing request identity; retain checkpoint files. Invalid intervals fail before any API command. Source errors (including invalid cursor and snapshot mismatch) are surfaced, never interpreted as exhaustion. If a page was counted but not committed, retry may need another tranche. Do not run another helper with a different checkpoint against the same source concurrently; do not grant a tranche while this helper is running.

The helper rechecks API quota before every page and makes at most two successful calls per invocation. It never grants quota. Completion can require arbitrarily many operator approvals after lost responses. Local atomic replacement and `fcntl` locking require a Unix-like filesystem; checkpoint disk must be durable and sufficiently large for the full snapshot. Protect checkpoints as ledger data. Filesystem/device corruption and manual checkpoint edits are outside recovery guarantees.
