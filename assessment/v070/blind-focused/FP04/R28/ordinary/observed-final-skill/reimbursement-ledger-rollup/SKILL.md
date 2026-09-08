---
name: reimbursement-ledger-rollup
description: Produce complete vendor reimbursement rollups from immutable paginated USD ledgers for inclusive posting-date intervals, with exact integer-cent arithmetic and durable continuation across operator-approved two-call tranches. Use for new rollups or resuming an incomplete ledger aggregation.
compatibility: Python 3.12 standard library on Unix with flock and atomic file replacement; supplied ledger_api.py and existing immutable source state; writable durable local checkpoint and report directories.
---

# Complete Reimbursement Ledger Rollup

## Purpose

Give an operations analyst a complete vendor-level reimbursement summary for one immutable ledger snapshot and an inclusive posting-date interval. This work aggregates entries; it does not grant execution tranches, change ledger entries, or make reimbursements.

## Outcomes

- Every source entry in the identified snapshot has been examined before the result is called complete.
- Each vendor with qualifying entries has exact settled charge cents, settled credit cents, net cents, and qualifying entry count for the requested inclusive interval.
- The result retains zero and negative nets and orders vendors by `vendor_id`.
- The analyst can identify the result's snapshot, interval, coverage, and whether work is complete.
- Incomplete work preserves sufficient durable progress to resume the same request without omission or double counting.

## Inputs and Enablers

Obtain the requested start and end calendar dates, the supplied API script path, its existing source-state path, the currently approved tranche number, and durable checkpoint/report paths. Dates must be `YYYY-MM-DD` with start on or before end. Do not assume the demonstration interval is the user's interval.

Use the bundled [rollup helper](scripts/rollup.py). It reuses the source's `describe` and `page` commands and Python's exact integer arithmetic, JSON, atomic replacement, and file locking. See [the interface and recovery reference](references/runtime.md) before first execution or handling an error. The supplied API is an operational dependency provided by the host, not bundled data to bypass traversal.

## Activities & Tasks

The following Tasks are required. Validate inputs and approval before fetching; establish completion before presenting a final rollup.

### Establish the request

1. Confirm the interval and existing immutable source, and use one checkpoint for that exact request. Retain an existing checkpoint when continuing. Resolve missing dates or source identity before dependent work.
2. Check that the approved execution tranche is available. The operator grants tranches; this Skill must never call `grant-tranche` or reinitialize source state. An initial authorized request may use its available initial tranche. A continuation must have a newly granted tranche or remaining quota in its already approved tranche.
3. Ensure checkpoint and report directories exist on reliable local storage and that the source has no concurrent consumer or operator control change during this run. Do not place output over source files. Checkpoint locking protects only runners sharing that checkpoint.

### Traverse and preserve progress

1. Run the helper with the confirmed inputs. Paths below are placeholders to replace with actual paths; the script path is relative to this Skill's root.

   ```sh
   python3.12 scripts/rollup.py --api /path/ledger_api.py --source /path/source.sqlite --checkpoint /path/job.json --output /path/report.json --start 2026-02-01 --end 2026-02-15 --tranche 1
   ```

2. Interpret its JSON stdout and exit code using the reference. Read the complete report file; stdout deliberately contains only progress metadata. The helper examines every page in source order, with no chronological early stop. Only a null returned next cursor and matching examined/total count allow completion.
3. At exit 75, present a clearly incomplete progress report with examined/total records and checkpoint location. Preserve the source and checkpoint. Ask the operator for a further tranche when none remains; do not promise completion conditional on an ungranted tranche. If approval never arrives, the request remains incomplete.
4. On continuation, invoke the same command with the same source, dates, checkpoint and output, changing only `--tranche` to the newly approved current tranche when applicable. Do not manually advance cursors or merge partial reports.
5. On an error or uncertain page effect, follow the recovery reference. Do not discard the checkpoint, assume a retry is free, or use a previous output as proof that the failed invocation completed.

### Assess and communicate the result

1. Accept a complete rollup only when the current invocation exits 0 and the report says `status: complete`, `next_cursor: null`, and `examined_records == total_records`. Confirm the snapshot and interval match the request.
2. Present the ordered `vendors` rows with `charge_cents`, `credit_cents`, `net_cents`, and `qualifying_entry_count`. Optional dollar display must be derived exactly from cents; retain the cents as the authoritative values.
3. Treat a complete empty `vendors` list as a valid result, including an empty source. Label `partial_vendors` as partial if shown during a pause; they are never a final answer.

## Controls and Constraints

The business rules apply to all supported snapshots: qualify only `status == settled` and inclusive `start <= posted_on <= end`; add charges and credits separately; net equals charges minus credits; count each qualifying entry once. Pending and void entries never contribute. Never remove a vendor because its net is zero or negative. All amounts are nonnegative integer USD cents.

The source permits two successful page calls per approved tranche, including repeated calls. This constrains a tranche, not the scope of the requested rollup. A budget-exhaustion error is not an empty final page. Entries must be obtained through the API, not the fixture, source database, inferred cursors, or an invented export endpoint.

Source immutability, disjoint stable pages, unique entry IDs, opaque snapshot-bound cursors, durable writable storage, and nonconcurrent source control are conditions of this implementation. Preserve checkpoint integrity; manual edits and storage corruption are unsupported. Resource use grows with examined entry IDs and vendor count. No production-scale capacity or power-loss fault-injection claim is made.

## Outputs and Verification

The helper produces an atomic JSON checkpoint, a checkpoint lock file, and an atomic JSON report. It consumes source page quota and may change the supplied source database/journal only through its page CLI. It neither initializes nor grants quota. Full results remain in the report file to avoid stdout truncation.

The [runtime reference](references/runtime.md#verification-evidence) records the locally tested cases and limits. These checks support the helper's behavior under examined conditions; final business success still requires the agent to assess the actual report and communicate its completeness honestly.
