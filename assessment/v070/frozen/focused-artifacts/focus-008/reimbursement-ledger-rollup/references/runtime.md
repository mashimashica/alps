# Runtime, continuation, and design evidence

## Source contract

The host supplies an existing `ledger_api.py` implementation with the following CLI. The target runner invokes it using the same Python interpreter as the helper. No network or nonstandard packages are needed.

```sh
python3.12 /path/ledger_api.py --state /path/source.sqlite describe
python3.12 /path/ledger_api.py --state /path/source.sqlite page --snapshot SNAPSHOT_ID
python3.12 /path/ledger_api.py --state /path/source.sqlite page --snapshot SNAPSHOT_ID --cursor OPAQUE_RETURNED_CURSOR
```

`describe` is unmetered and returns `snapshot_id`, `total_records`, `page_size: 3`, `calls_per_tranche: 2`, positive `tranche`, and `remaining_calls` between zero and two. A successful page returns `snapshot_id`, `items`, `next_cursor`, `total_records`, and `tranche`. Only `next_cursor: null` marks exhaustion. Empty source: one empty first page with a null cursor. The metadata count covers every entry, including nonqualifying entries.

Each item contains exactly:

| Field | Contract |
| --- | --- |
| `entry_id` | Nonempty string, unique within snapshot |
| `vendor_id` | Nonempty string |
| `posted_on` | Valid ISO calendar date, `YYYY-MM-DD` |
| `kind` | `charge` or `credit` |
| `status` | `settled`, `pending`, or `void` |
| `amount_cents` | Nonnegative integer, no floating point |
| `currency` | `USD` |

Pages are stable, disjoint, and not chronological. Cursors must be passed unchanged and are tied to the snapshot. Repeating a cursor consumes a successful page call and returns the same page. API budget exhaustion exits 75 without entries. Invalid cursor exits 2; snapshot mismatch exits 4; neither consumes a call. Successful calls can consume quota even when their response is lost.

## Public operation

`python3.12 scripts/rollup.py --help` describes all required flags. One invocation consumes at most two successful page calls in the specified approved tranche and stops when the source's allowance is exhausted. It never crosses into a different tranche automatically. A requested tranche number records the caller's claimed approval; the helper cannot authenticate an operator or create approval.

| Exit | Meaning and response |
| --- | --- |
| 0 | Complete; assess current report and deliver full result. Repeating a completed invocation refreshes the report with no page calls. |
| 75 | Incomplete; stdout and report give progress and a reason. Keep checkpoint. Resume only with available approved quota. |
| 2 | Invalid input, paths or local state; fix the stated condition. Invalid date intervals are rejected before any API call or checkpoint creation. |
| 3 | Source, malformed response, lock, or recovery error; do not accept an old report. Inspect metadata and preserve the checkpoint. |
| 4 | Snapshot/source mismatch; stop and resolve source identity. Do not combine snapshots. |

Argparse usage errors print help diagnostics to stderr. Other errors are JSON on stdout. A failed invocation may leave the prior report untouched, so its existence is not evidence of current success.

The result includes snapshot, inclusive `start`/`end`, USD currency, examined and total counts, committed page count, next cursor, last incorporated tranche, and status. A complete report uses `vendors`; an incomplete report uses `partial_vendors`. Each row has vendor ID, charge cents, credit cents, net cents, and qualifying entry count. Vendors are sorted by Python string order of `vendor_id`. Counts and sums use Python integers, including sums beyond signed 64-bit range. Final totals are not calculated by SQLite or floating point.

## Checkpoint and recovery

The version-1 JSON checkpoint binds the resolved API and source paths, snapshot ID, total count, interval, next unincorporated cursor, completion flag, committed page count, every examined entry ID, consumed cursors, vendor accumulators and last tranche. Its sibling `.lock` uses nonblocking Unix `flock` and is safe to leave in place after a run; the OS releases the held lock when the process exits. Do not delete a lock file during a running invocation.

Each page is validated and aggregated in an independent in-memory copy. The runner writes and fsyncs a temporary checkpoint, atomically replaces the old checkpoint, and fsyncs the containing directory. All changes for that page and its next cursor therefore advance together. It does not retain a partially validated page. It stops on duplicate IDs or cursor cycles because those violate the supplied disjoint-page contract. Final source exhaustion must also match the metadata count.

If the process stops before committing a page, the durable cursor still points to that page. The next invocation reads the checkpoint and calls unmetered `describe` before any retry. If quota remains in the approved tranche, it may refetch the same cursor; otherwise it pauses for an operator-approved tranche. Because the prior aggregation and cursor were not committed, replay contributes that page once. If the checkpoint commit succeeded but output was lost, the resumed cursor is already advanced and the page is not requested again. If a final report write failed, rerunning recreates it from the complete checkpoint without page calls.

A timeout or unreadable response returns an error immediately; the script does not assume whether the source counted it. Describe establishes current remaining quota, while the checkpoint establishes incorporation. Neither substitutes for the other. Do not copy page payloads into the accumulator, change checkpoint cursors, reset the source, or grant quota to recover.

For malformed source data, snapshot mismatch, or a damaged checkpoint, stop and resolve the underlying condition. Do not silently skip a page. The implementation assumes its checkpoint has not been manually modified and that atomic rename/fsync semantics are supported on the chosen local filesystem. Uncommitted temporary files may remain after abrupt termination; they are not recovery inputs.

## Responsibility and boundary rationale

The operations request and source contract are the design basis, originally supplied as “S06 — Complete reimbursement ledger rollup.” The packaged instructions carry the operational requirements so using the Skill does not require access to the original authoring brief.

| Element | Responsibility and role |
| --- | --- |
| Analyst request | Input: interval and source identification; the agent resolves ambiguity and checks report applicability. |
| Ledger pages | Inputs transformed into the vendor result; metadata also supplies coverage evidence. |
| Business qualification and arithmetic rules | Controls applied by the helper and criteria for final result assessment. |
| Two-call tranche and operator grants | Constraints on permitted traversal, not limits on required coverage. |
| Agent | Enabler for contextual input selection, approval interpretation, failure response and truthful presentation. |
| Existing source CLI | Enabler for authoritative metadata, traversal and quota enforcement. |
| Bundled helper and local Python/filesystem | Enablers for exact aggregation, contract checks, atomic continuation and bounded progress reporting. |
| Checkpoint | Intermediate Output reused as continuation Input; only the helper updates it. |
| Report | Output and evidence for assessing coverage and calculations; existence alone is insufficient. |

Existing CLI operations are reused for source access; none supplies aggregation or durable exactly-once incorporation. A cohesive wrapper therefore combines the stable fetch/validate/aggregate/checkpoint sequence while leaving meaningful choices—request scope, authority to continue, error resolution, and presentation—with the agent/operator. No extra agent, database adapter, network service, or source modification is justified. Full examined-ID retention simplifies coverage and duplicate validation at the cost of O(entries + vendors) memory/storage and repeatedly rewriting the checkpoint. Very large snapshots require a separately tested storage implementation; no scale threshold was established here.

## Verification evidence

Local Python 3.12 checks use the supplied simulator and isolated synthetic source states. The original 17-entry fixture traverses six pages over three test-controlled tranches: 6 examined after the first, 12 after the second, 17 after the third. The final totals were checked against these independent expectations:

| Vendor | Charge cents | Credit cents | Net cents | Qualifying count |
| --- | ---: | ---: | ---: | ---: |
| alder | 14000 | 1500 | 12500 | 4 |
| birch | 7000 | 200 | 6800 | 2 |
| cedar | 3250 | 3250 | 0 | 2 |
| dune | 400 | 1200 | -800 | 2 |
| elm | 2345 | 0 | 2345 | 1 |

Nine automated checks passed: full fixture and repeated invocation; invalid intervals without traversal; empty ledger; no matches with full traversal; single-day interval and integer amounts of 10^30 cents; lost successful response with metered replay; simulated checkpoint-write failure with replay; request/tranche identity checks; and page-contract failure checks (premature exhaustion, snapshot mismatch, duplicate ID, and floating-point amount). Test code and the public command record accompany the authoring handoff outside this reusable Skill.

These are implementation and integration checks, with the authoring agent inspecting the supplied contract and expected output. They are not an independent deployed-agent evaluation. No live business source, concurrent operator/consumer stress, OS power-loss injection, corrupted-filesystem recovery, or large-volume performance test was performed. Tests simulate a lost response and a failure before checkpoint replacement; they do not prove every physical interruption boundary. The source API and operator authority remain external prerequisites. Further tranches are never guaranteed.
