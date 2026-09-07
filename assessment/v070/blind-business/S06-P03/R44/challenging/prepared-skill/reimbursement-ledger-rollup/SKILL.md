---
name: reimbursement-ledger-rollup
description: Produce a complete, exact vendor reimbursement rollup from the supplied paginated immutable ledger API for an inclusive posting-date interval, including safe continuation across operator-approved call tranches.
---

# Reimbursement ledger rollup

Use this skill when an operations analyst requests a vendor-level reimbursement rollup from a ledger snapshot that follows the supplied API contract.

## Required inputs

Obtain:

- the inclusive `YYYY-MM-DD` start and end dates;
- the path to the ledger API program;
- the path to the already initialized source-state database; and
- a durable, request-specific checkpoint path in an authorized working directory.

Do not read the fixture or SQLite database to obtain ledger entries. Do not initialize or replace an existing source state. One checkpoint belongs to exactly one API path, source-state path, snapshot, and date interval.

## Run the rollup

Invoke the bundled processor with the same arguments on every continuation:

```sh
python3.12 scripts/reimbursement_rollup.py \
  --api /absolute/path/ledger_api.py \
  --source-state /absolute/path/source.sqlite \
  --checkpoint /absolute/path/request-checkpoint.json \
  --start 2026-02-01 \
  --end 2026-02-15
```

The processor validates the interval before contacting the source. It uses the unmetered `describe` operation, follows opaque cursors unchanged, and consumes no more than the calls available in the current tranche. It never invokes `grant-tranche`.

Interpret its JSON output and exit code:

- Exit `0` with `status: "complete"` is the final business result. Report the snapshot, inclusive interval, source-entry coverage, and the ordered `vendors` array. Integer cents are authoritative.
- Exit `3` with `status: "incomplete"` is a continuation state, not a result. Report the reason and progress only. Do not present any vendor totals as final. If the operator later grants another tranche, rerun the exact command with the same checkpoint.
- Exit `2` with `status: "error"` means the request, checkpoint, source identity, response contract, or local operation failed. Report the error. Do not claim completeness.

Only the operator may run the simulator's `grant-tranche` control. Never request or imply that another tranche is guaranteed. If none is granted, leave the request incomplete and preserve the checkpoint.

## Result rules

The processor examines every entry before completing. It includes an entry only when `status` is `settled` and `posted_on` is within the inclusive interval. It sums `charge` and `credit` amounts independently as integer cents, computes `net_cents = settled_charge_cents - settled_credit_cents`, counts qualifying entries, retains zero and negative-net vendors, and orders vendors by `vendor_id`.

An exhausted empty snapshot or fully traversed interval with no matches produces a complete empty `vendors` array. A call-budget error is never treated as an empty page. The checkpoint records incorporated entry IDs and is replaced atomically, so retrying the same page cannot double-count it. After an uncertain or malformed page response, stop and preserve the checkpoint; a later retry may consume another call.

