---
name: rollup-reimbursements
description: Produce a complete vendor reimbursement rollup from an immutable paginated ledger for an inclusive posting-date interval, preserving exact USD cents and resumable progress across operator-approved execution tranches.
---

# Complete reimbursement ledger rollup

## Purpose

Give the operations analyst a complete vendor-level reimbursement rollup for the requested inclusive posting-date interval and immutable snapshot. This work aggregates ledger entries; it does not issue reimbursements or authorize additional source access.

## Outcomes

- Every entry in the identified source snapshot has been examined.
- Each vendor with a qualifying entry has exact settled charge, settled credit, net (charges minus credits), and qualifying entry count values for the requested interval.
- Results identify their snapshot and date interval and list vendors in ascending `vendor_id` order, including zero and negative nets.
- The analyst can distinguish a completed result from incomplete work and determine whether continuation is available.

## Tasks

Perform these tasks, with interval validation preceding traversal and source exhaustion preceding any final claim.

1. Establish the inclusive `start` and `end` dates, trusted API script, initialized source state, and a persistent request checkpoint and output location. Reuse the original checkpoint on continuation. Require valid calendar dates in `YYYY-MM-DD` form with start no later than end. Report invalid intervals without beginning traversal. Read [the interface and recovery reference](references/interface.md) when connecting the source or recovering an interrupted run.
2. Use [scripts/rollup.py](scripts/rollup.py) to process the available tranche. It examines all source entries, follows opaque cursors, filters settled entries in the interval, and performs integer arithmetic. Do not read the fixture or source database to obtain operational entries. Source order is not chronological; a date beyond the interval does not justify stopping.

   ```sh
   python3.12 scripts/rollup.py run --api /absolute/ledger_api.py --state /absolute/source.sqlite --start 2026-02-01 --end 2026-02-15 --checkpoint /absolute/request.json --output /absolute/result.json
   ```

   Resolve `scripts/rollup.py` relative to this Skill folder. The dates above illustrate inputs, not fixed defaults. Parent directories must exist. The script provides `--help` and `run --help`.

3. Interpret the JSON status and exit code. Exit 0 with `complete: true` establishes that a null cursor was observed and examined entries equal metadata's full record count. Read the result file for the vendor table; fields ending in `_cents` are integer USD cents. An empty vendor list is a valid completed result, including an empty source. Do not drop rows because their net is nonpositive.
4. On exit 10, tell the analyst that the request remains incomplete, quote examined versus total entries, and retain the checkpoint and original command. The current partial rows are provisional. Ask the operator for another execution tranche if continued work is desired. Only after the operator grants it, repeat the same command. Never invoke `grant-tranche`, reset source state, split the request, or create another checkpoint to evade the two-successful-call limit. If approval never arrives, keep the request incomplete; make no unconditional completion promise.
5. On other errors, report the failure and preserve the checkpoint. The output file might be stale. Use the recovery guidance before retrying; lost responses may already have consumed quota. To regenerate the committed view without source calls:

   ```sh
   python3.12 scripts/rollup.py status --checkpoint /absolute/request.json --output /absolute/result.json
   ```

6. Present final results only after completion: snapshot, inclusive interval, currency, examined/total entries, and sorted vendor charge, credit, net, and count columns. Partial status is a truthful pause, not satisfaction of the complete-coverage outcome.

## Controls and Constraints

An entry qualifies exactly when `status == settled` and `start <= posted_on <= end`. Count qualifying entries including zero amounts. Pending and void entries never contribute. Use exact integer cents; dollar formatting is optional.

The immutable paginated source contract and the operator's two-successful-page-call tranche are execution conditions. Only `next_cursor: null` establishes exhaustion. Record counts are a completeness cross-check, not an early-stop rule. A repeated successful page call also consumes quota.

Use one coordinated source consumer and one checkpoint writer; the operator must not grant a tranche during a running command. Preserve checkpoint files across sessions. The local runner cannot itself obtain operator authority or guarantee durable storage beyond its filesystem. If the source, checkpoint, or approval is unavailable, report the dependent work as incomplete.

## Enablers and Information

Requires Python 3.12 standard library, a POSIX shell and filesystem supporting `flock` and atomic rename, and a trusted `ledger_api.py` with its initialized immutable source state.

The analyst's interval and the ledger pages are Inputs. Qualification and completeness rules are Controls. Operator approvals and call limits constrain traversal. The agent interprets the request, coordinates continuation, and evaluates the reported result; the supplied source CLI fetches pages and meters quota; the bundled runner handles deterministic validation, traversal, arithmetic, and atomic checkpointing. Python and the local filesystem enable execution. The checkpoint is an intermediate Output and continuation Input; the result JSON supplies evidence of coverage and totals.

The operational dependency is the user-supplied trusted source CLI and existing state, not a bundled fixture. [Interface and recovery](references/interface.md) specifies its required contract and state effects. [Verification scope](references/verification.md) states the local evidence and limits of the implementation.
