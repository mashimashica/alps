---
name: reimbursement-ledger-rollup
description: Compute complete vendor reimbursement totals for an inclusive posting-date interval from an immutable paginated USD ledger, with exact cents, quota-aware pauses and crash-safe continuation. Use when an operations analyst needs settled charges, credits, net amounts and counts across every page of a supplied ledger snapshot.
---

# Complete reimbursement ledger rollup

Use the bundled [runner](scripts/rollup.py) with Python 3.12 and its standard library. The caller supplies an existing source state and its trusted `ledger_api.py` interface. The runner never reads source records from SQLite or a fixture: it invokes only `describe` and `page`. No network, packages, aggregation endpoint or personal installation is required.

## Inputs and invocation

Obtain the inclusive start/end dates, trusted API script path, existing source state path, and a durable writable checkpoint path dedicated to this request. Dates must be real calendar dates in exact `YYYY-MM-DD` form, with start no later than end. Invalid dates fail before any API call. Do not initialize, replace or modify the source to get around quotas. Do not use the checkpoint path for any other file.

```sh
python3.12 /absolute/skill/scripts/rollup.py --api /absolute/ledger_api.py --source /absolute/source.sqlite --checkpoint /absolute/request.sqlite --start 2026-02-01 --end 2026-02-15
```

Use `--help` for arguments. The first invocation binds the checkpoint to the resolved API/source paths, interval, snapshot and total source count. Repeat the **same command and checkpoint** to continue. A changed request or snapshot is rejected. Keep the checkpoint durable; it contains processed entry IDs, page cursors and aggregates. Do not edit it, copy it while running, delete it to retry, or run multiple checkpoints for the same request. SQLite serializes concurrent invocations on the same checkpoint; a busy error is safe to retry later. The runner creates/modifies only the checkpoint and its SQLite journal, while the supplied API changes its own metering state.

## Interpret output before answering

One JSON object is written to stdout. Exit 0 with `complete: true` is the only successful final result. It includes snapshot, inclusive interval, currency, examined and total source record counts, committed page count, and vendors ordered by `vendor_id`. Each vendor has `settled_charge_cents`, `settled_credit_cents`, `net_cents` (charges minus credits), and `qualifying_entry_count`. Use integer cents for all arithmetic. Vendors with qualifying entries remain even when their net is zero or negative.

Exit 75 with `complete: false` is a truthful pause, not an empty result or failure of the business request. The JSON includes the checkpoint path, reason, remaining quota, progress and explicitly nonfinal vendor totals. Tell the analyst the request remains incomplete and needs an operator-approved further tranche. Never call `grant-tranche` yourself. The operator may grant a tranche separately; then rerun the same command. If approval never arrives, leave the request incomplete; do not promise eventual completion.

Other nonzero exits indicate an error; never present their output as final totals. Exit 2 reports invalid input, source/checkpoint mismatch, unexpected API or data errors; exit 4 reports source snapshot mismatch. Preserve the checkpoint and resolve the error. `response_unavailable` means a page may have consumed quota without being committed; rerun the same command when permitted. It checks `describe` before retrying and retries the saved cursor, so a retry is not assumed free. A timeout has the same recovery behavior. An invalid cursor is an error, never exhaustion. Do not invent or modify a cursor.

## Coverage and recovery guarantees

The runner traverses every page in returned cursor order, regardless of posting-date order. It filters only `settled` records whose dates fall within both inclusive bounds. Pending/void entries are examined but never aggregated. It stops as complete only after a committed page has `next_cursor: null` **and** unique examined entries equal the snapshot's source count. Counts alone, out-of-range dates, empty nonterminal pages and quota errors never establish completion. A legitimate empty source still requires its empty terminal first page. An interval with no matches produces a complete empty vendor list after full traversal.

Each page's IDs, totals, consumed cursor and next cursor are committed in one SQLite transaction. A crash before commit leaves the old cursor and totals; a retry safely refetches the uncommitted page, subject to remaining quota. A crash after commit resumes at the next cursor; repeated final invocations make no page calls. Duplicate IDs or cycling cursors are rejected as contract violations, rather than silently hiding source inconsistency. Repeated pages caused by transport recovery cannot be counted twice. Do not manually fetch pages to feed this runner.

The runner reads quota before every call, makes at most two successful page calls per invocation, and stops if the observed tranche changes during that invocation. The API enforces the two-successful-calls-per-tranche limit across invocations and lost responses. The runner cannot grant approval or guarantee progress without further quota. The source must remain immutable and honor the supplied API contract; coordinate grants so they do not occur during an active invocation. There is no atomic transaction spanning the API and checkpoint, so a lost response can waste a call but cannot cause skipped entries. Checkpoint storage grows with examined entry IDs and pages; vendor arithmetic uses Python integers. A damaged or lost checkpoint cannot be reconstructed from quota metadata: preserve it and obtain a separately authorized restart if recovery is impossible.

Local verification and its limits are documented in [verification](references/verification.md).
