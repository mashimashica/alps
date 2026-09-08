---
name: reimbursement-ledger-rollup
description: Produce a complete vendor-level reimbursement rollup from an immutable paginated ledger snapshot for an inclusive posting-date interval. Use when every page must be covered across operator-approved call tranches with exact integer-cent arithmetic and resumable progress.
---

# Reimbursement Ledger Rollup

## Purpose

Produce a trustworthy vendor-level summary of settled reimbursement ledger activity for a requested inclusive posting-date interval while preserving complete snapshot coverage across limited execution tranches.

## Outcomes

- Every source entry in the identified immutable snapshot has been examined before a result is presented as final.
- Each vendor with qualifying activity has exact settled charge cents, settled credit cents, net cents, and qualifying entry count; vendors with zero or negative net remain included.
- The final result identifies the snapshot and interval, and orders vendors by `vendor_id`.
- Work paused at a call boundary or after an uncertain page response remains explicitly incomplete and can resume without omitting or double-counting entries.
- Invalid requests, source-contract failures, and unperformed work remain visible and do not produce a final rollup.

## Inputs

The work uses:

- Python 3.12 and a local shell.
- Inclusive `YYYY-MM-DD` start and end dates.
- The local ledger API program and the explicitly supplied source-state database.
- A durable, request-specific checkpoint path whose parent directory exists.

## Entry Criteria

The API program, source state, canonical interval, and writable checkpoint parent must be available before traversal. The start date must not be after the end date.

## Activities & Tasks

### Establish the request

1. Confirm the inclusive start and end dates, API path, source-state path, and request-specific checkpoint path.
2. Use a new checkpoint path for each distinct interval or source state. Preserve the same checkpoint and inputs when continuing one request.
3. Do not read the API's backing database, setup fixture, or other implementation storage to obtain operational ledger entries.

### Traverse and roll up the snapshot

1. Run the bundled operation from the Skill root:

   ```sh
   python3.12 scripts/rollup_ledger.py \
     --api /absolute/path/ledger_api.py \
     --source-state /absolute/path/source.sqlite \
     --checkpoint /absolute/path/request-checkpoint.json \
     --start-date YYYY-MM-DD \
     --end-date YYYY-MM-DD
   ```

2. Let the operation traverse all pages it can within the current tranche. It validates the interval before invoking the source, calls unmetered `describe`, and then makes at most the successful page calls available in the current two-call tranche. It passes returned cursors unchanged, scans until `next_cursor` is null, validates the record contract, and stores progress atomically after each usable page. It uses only integer cents for arithmetic. Source order is not chronological; do not stop based on dates or page contents.
3. After a timeout, empty response, malformed response, or other uncertain page response, do not call the page API manually. The checkpoint remains at the unconfirmed cursor. Rerun the bundled operation when quota is available; it first checks current metadata and safely retries from that cursor. A retry can consume another page call.

### Assess and communicate the result

1. Interpret the operation's JSON and exit code together.
2. Treat `status: "complete"` with exit `0` as the only final business result. Present its `vendors` array as the rollup. A complete empty array is a valid result.
3. Treat `status: "incomplete"` with exit `75` as progress, never a final rollup. Preserve the checkpoint and report the examined/total counts, snapshot, reason, and required next action. Do not calculate or present partial vendor totals as final.
4. Treat `status: "error"` with a nonzero exit as a failed or invalid operation. Report the structured error and do not infer completion.
5. If the operator supplies another approved tranche, rerun the same command with the same checkpoint and request inputs. If no tranche is granted, leave the request incomplete without promising completion.

For the exact command contract, checkpoint guarantees, result fields, and exit meanings, read [references/interface.md](references/interface.md).

## Enablers

The agent selects the correct paths and interval, invokes the operation, preserves the request identity across continuations, and communicates whether the result is complete. The bundled script supplies deterministic pagination, validation, de-duplication checks, checkpointing, filtering, aggregation, and ordering.

## Constraints

Page calls mutate only the source's tranche allowance; the script also creates or replaces the local checkpoint and creates an adjacent lock file. It does not initialize source state, grant tranches, change ledger entries, or use a network. Its completion claim depends on the supplied API honoring the documented immutable-snapshot, stable-cursor, and metadata contract.

The operator alone controls `grant-tranche`. Never invoke that control from this Skill or the bundled script.

## Exit Criteria

The work is complete only when the bundled operation returns exit `0` with `status: "complete"` after source exhaustion and matching examined/total record counts. Every other result leaves the work incomplete or failed as its structured status states.
