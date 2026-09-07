# Main system-case quality and verification report

Prepared 2026-09-07. This work produced only original synthetic case inputs, local stand-in commands where needed, and provider-verification material. It did not create target Skills, hidden consumer cases, business-result gold answers, or grading criteria. No ALPS text, other assessments, candidates, grades, worktrees, PRs, or history were consulted. No external writes were made; the parent agent is responsible for review and persistence.

## Case quality

| Case | Work and intended distinction | Supplied support |
| --- | --- | --- |
| S06 | Exact, all-record reimbursement rollup from an immutable paginated source. Two successful page calls per approved tranche do not reduce total coverage. Partial work may continue only in an operator-granted later tranche. | `brief.md`, original 17-entry `fixture.json`, and `ledger_api.py`. Fixed three-entry pages, opaque snapshot-bound cursors, metered repeated calls, explicit exhaustion vs. completion, and separate operator quota control. |
| S07 | Read-only queue-aging handoff from a stable local SQLite export. Existing SQL and the verified Python standard-library SQLite CLI are sufficient; a new executable wrapper is not intrinsically needed. | `brief.md` and original `queue_fixture.sql` containing schema and 12 setup rows. No custom adapter or fake service. |
| S08 | Authorized local booking with truthful uncertain outcomes, durable request identity, atomic capacity changes, same-key retries, and concurrent callers. | `brief.md`, original three-session `fixture.json`, and `booking.py`. Committed receipts and capacity share a transaction; two verification faults expose the same missing-outcome symptom on either side of commit. |

Every brief begins with a sufficient business work description and then supplies the scope, inputs, outcome semantics, conditions, and available interface. Each asks for design, implementation where justified, and local verification of the target Agent Skill's supporting system. None prescribes ALPS wording, Skill headings, a runtime architecture, fixed output documents, or a mandatory added wrapper. The case inputs are not variant-specific; the parent can give these same inputs to every creator of a given case.

The synthetic data deliberately includes ordinary business boundaries without providing rollup answers: S06 includes pending/void and out-of-window entries, later-page contributions, a negative-net case, and a zero-net case; S07 includes due-date equality, missing due dates, an unassigned group, zero value, excluded states, and a future received date. S08 includes a one-place session suitable for original local concurrency checks.

## Verification performed

The local environment reports Python **3.12.13**. `python3.12 -m sqlite3 --help` and an actual SQL invocation succeeded; the underlying SQLite version reports **3.53.1**. `command -v sqlite3` found no standalone binary, and the S07 brief explicitly avoids assuming one.

Re-run the supplied provider checks with:

```sh
python3.12 /workspace/scratch/a75c3a6d9076/alps-v070-assessment/audits/verify_main_system_cases.py
```

Two complete runs passed the same **7 tests**, most recently in approximately **3.0 seconds**:

- S06: invalid cursor and snapshot rejection without quota consumption; repeated-page identity and quota consumption; explicit budget exhaustion; traversal of all 17 source rows over operator-granted tranches; empty-source completion; cursor binding; refusal to overwrite a source; and refusal to create missing operational state.
- S07: actual SQL-file initialization through the existing CLI; fixture row count; unchanged database bytes after a read-only query; and a separate in-memory capability probe exercising filtering, joins, grouping, conditional counts, integer sums, and ordering. The probe is not the queue-handoff solution.
- S08: rollback-before-commit and hidden-after-commit failures with identical observed error output; persisted receipt lookup and same-key replay; no duplicate capacity decrement; conflicts for changed payload fields; stable business rejections; invalid-input nonmutation; refusal to overwrite state or create missing operational state; six concurrent distinct keys competing for one place; six concurrent attempts of one key; and recovery after a deliberately held SQLite write lock.

All writable test state was created under fresh, automatically cleaned temporary directories from these original setup fixtures. Provider checks inspect local fixture/state internals only to verify the stand-ins; they do not implement or assess a target Skill's business result. The operational briefs explicitly prohibit bypassing the supplied API/booking commands to perform the target work by directly reading or changing stand-in state.

## Limits and review points

- These are local standard-library simulations, not claims about a production API or reservation service. They do not model networks, credentials, service deployment, payments, cancellation, clock-driven quota resets, or unbounded load.
- S06's additional tranche is an explicit operator action. An attempted supporting system must not grant its own new tranche or call an incomplete aggregation final. The stand-in has no transport-fault switch; its counted-repeat behavior supports retry reasoning, but actual response loss was not injected in its tests.
- S08 verifies controlled unknown outcomes, lock contention, and small concurrent process groups. No OS-level process-kill or power-loss experiment was performed. Atomicity and rollback behavior otherwise rely on SQLite's local transaction implementation.
- Verification establishes the supplied interfaces' behavior on original disposable fixtures, not the correctness of any future target Skill, creator implementation, or general architecture. No aggregation gold totals, target implementation, hidden tests, or comparative scores are included.
