---
name: complete-reimbursement-rollup
description: Produce exact vendor-level reimbursement rollups from an immutable paginated ledger, with complete coverage and safe continuation across call-limited tranches. Use when an analyst supplies an inclusive posting-date interval, a ledger_api.py-compatible source, and its existing snapshot state.
---

# Complete Reimbursement Rollup

## Purpose

Produce a trustworthy vendor-level reimbursement result for an inclusive posting-date interval without treating a page or tranche boundary as source exhaustion.

## Outcomes

- Every entry in the identified immutable snapshot has been examined exactly once in the completed computation.
- The completed result contains every vendor with a qualifying entry, including vendors with zero or negative net amount, and reports exact settled charge, settled credit, net, and count values.
- The result identifies its snapshot and inclusive interval and distinguishes completion from every paused, failed, or uncertain execution.
- Continuation after a tranche boundary resumes the same request without omitting entries or incorporating a repeated page twice.

## Inputs

Obtain these before running the processor:

- The inclusive `YYYY-MM-DD` start and end dates.
- The existing source state database for the immutable snapshot.
- The local `ledger_api.py` compatible with the interface in the request.
- A durable checkpoint path dedicated to this snapshot and interval. Reuse that exact path for every continuation.
- An unused result path for a new request's completed JSON rollup. Reuse that exact path for every continuation.

The source state and checkpoint are different files. Do not initialize or replace an existing source state as part of a continuation.

## Activities & Tasks

### Start or continue the rollup

1. Run the bundled processor with absolute paths:

   ```sh
   python3.12 scripts/reimbursement_rollup.py \
     --api /absolute/path/ledger_api.py \
     --source-state /absolute/path/source.sqlite \
     --checkpoint /absolute/path/rollup.checkpoint.json \
     --output /absolute/path/rollup.result.json \
     --start YYYY-MM-DD \
     --end YYYY-MM-DD
   ```

2. Let the processor call `describe` and make at most two page calls in the current invocation. It validates the interval before contacting the source, binds a new checkpoint to the request and snapshot, passes returned cursors unchanged, validates every page, keeps integer-cent arithmetic, and atomically commits each incorporated page.
3. Never invoke `grant-tranche` on behalf of the operator. It is an operator control, not part of this Skill's processing capability.

### Interpret the processor result

1. Treat only exit code `0` with JSON `"status": "complete"` and `"final": true` as completion. Read the business result from `result_file`, then report its `vendors` rows in their emitted `vendor_id` order. Preserve the integer-cent fields; optional dollar formatting must not replace them as the calculation basis.
2. Exit code `10` with `"status": "incomplete"` is a truthful pause. Do not present checkpoint aggregates as final. Report its coverage, snapshot, interval, and `pause_reason`. If the operator later grants a new tranche, rerun the identical command; do not promise that another tranche will be granted.
3. Exit code `20` indicates invalid input, incompatible source metadata, a source contract violation, or a checkpoint mismatch. Correct the reported condition before retrying. A checkpoint mismatch protects against combining snapshots, intervals, API paths, or state files.
4. Exit code `21` means a page call may have consumed quota but its response could not be safely incorporated. Do not infer that the call had no effect and do not immediately loop. The checkpoint remains at the last committed cursor; after confirming that another call is permitted, rerun the identical command. Re-fetching that cursor is safe for aggregation because a page is committed only after full validation.

## Interface and state

The processor writes compact status JSON to standard output and writes the completed business result atomically to `--output`. Diagnostics from the source command are summarized in error JSON. It changes only the specified checkpoint, its adjacent `.lock` file, and the specified result path; the stand-in API may update its explicitly supplied SQLite state and journal according to its own call-metering contract. `--output` may be omitted for small results, in which case the complete result is printed to standard output, but use a file when result size is not known to be small.

The final output includes `snapshot_id`, the inclusive `interval`, `currency`, complete `coverage`, and `vendors`. Each vendor row contains `settled_charge_amount_cents`, `settled_credit_amount_cents`, `net_amount_cents`, and `qualifying_entry_count`. An empty exhausted source or an exhausted interval with no qualifying entries returns a complete empty `vendors` list.

The checkpoint is an internal continuation record, not a partial business result. The processor refuses a pre-existing result path for a new request and an unexpected result file beside an incomplete checkpoint, preventing stale output from appearing to belong to partial work. Keep the checkpoint until the completed result has been retained. The immutable source contract, stable disjoint pages, opaque snapshot-bound cursors, and unique entry IDs are required conditions; stop on reported contract violations rather than improvising around them.
