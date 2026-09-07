---
name: reimbursement-ledger-rollup
description: Produce a complete vendor-level reimbursement rollup from an immutable paginated ledger, with exact cent arithmetic, date and status filtering, and durable continuation across two-page execution tranches.
---

# Reimbursement ledger rollup

Use this skill when an operations analyst needs vendor totals for a closed inclusive posting-date interval from the supplied paginated ledger API. The answer is complete only after the API returns a page with `next_cursor: null`; a two-page response is not evidence of completion.

## Run the supporting system

Use the bundled `scripts/reimbursement_rollup.py` with an existing source state database:

```sh
python3.12 scripts/reimbursement_rollup.py \
  --api /absolute/path/to/ledger_api.py \
  --state /absolute/path/to/source.sqlite \
  --progress /absolute/path/to/rollup-progress.json \
  --start-date YYYY-MM-DD --end-date YYYY-MM-DD
```

The progress path must be durable and dedicated to this interval and source state. If a fresh simulator state is explicitly supplied, initialize it once with the source API's `init --fixture` command before running the script. Do not read the SQLite tables to perform the rollup; all entries must come from API pages. The script calls `describe` first, validates the interval before any source traversal, and invokes at most two page calls in one execution.

The script writes progress atomically after each incorporated page. It records the snapshot, cursor, aggregate counters, and entry fingerprints. Re-running with the same progress path resumes at the saved cursor and ignores an already incorporated entry ID, so a billable retry after a lost response cannot count that entry twice. Never delete or hand-edit progress during a continuation.

When the script emits `status: "incomplete"`, inspect `reason`:

- `tranche_boundary` means two pages were incorporated and another approved tranche is needed.
- `call_budget_exhausted` means the source had no call available when the attempt was made.

The operator must grant the next tranche using the source API's `grant-tranche` control, then rerun the same command:

```sh
python3.12 /absolute/path/to/ledger_api.py --state /absolute/path/to/source.sqlite grant-tranche
```

This skill never grants a tranche itself. A response parsing or validation failure can emit `status: "error"` with `recovery_required: true`; preserve the progress file and treat retrying the saved cursor as consuming another source call. Do not present any incomplete or error response as the requested final result.

## Interpret a complete result

Only `status: "complete"` contains final `results`. Rows are sorted by `vendor_id` and include `settled_charge_cents`, `settled_credit_cents`, `net_cents` (charge minus credit), and `qualifying_entry_count`, together with the inclusive interval and snapshot ID. Keep rows whose net is zero or negative. A qualifying entry has `status: "settled"` and a `posted_on` date within both bounds; pending and void entries are ignored. Amounts are integer USD cents, so retain integer arithmetic and do not infer values from formatted dollars. An empty `results` list is valid when the source is empty or the interval has no qualifying entries.

The script's output is JSON on stdout. Exit code `0` means complete; exit code `75` means continuation is required; exit code `74` marks a consumed-call response that could not be incorporated; other nonzero codes identify input, metadata, or source errors.
