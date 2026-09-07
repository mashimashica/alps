---
name: reimbursement-rollup
description: Produce complete vendor reimbursement rollups from an immutable paginated USD ledger for an inclusive posting-date interval, with exact integer arithmetic and resumable two-call execution tranches. Use when all source entries must be examined and operator approval may be needed to continue.
---

# Reimbursement rollup

Use the bundled [runner](scripts/rollup.py) to traverse the ledger and maintain a durable request checkpoint. Python 3.12 with the standard library and a POSIX local filesystem supporting `flock`, atomic rename, and fsync are required. The source adapter is the supplied `ledger_api.py` command interface; provide its absolute path and an existing, explicitly authorized source state. No network, database queries, exports, or third-party packages are used by the runner.

## Start and continue

Obtain the inclusive start/end dates, adapter path, existing source state path, and a writable checkpoint path unique to this request. Checkpoint directories must already exist. Keep the checkpoint and its `.lock` sidecar available across continuations; do not put disposable checkpoints inside this Skill. The source snapshot must remain immutable and the adapter must implement the contract in [the interface notes](references/interface.md).

```sh
python3.12 /absolute/path/reimbursement-rollup/scripts/rollup.py --help
python3.12 /absolute/path/reimbursement-rollup/scripts/rollup.py \
  --api /absolute/path/ledger_api.py --state /absolute/path/source.sqlite \
  --checkpoint /absolute/path/request.json \
  --start 2026-02-01 --end 2026-02-15
```

Use the same command and checkpoint to continue. The runner binds it to the adapter path, source state path, dates, snapshot and total source record count. A different request needs its own checkpoint. Invalid or reversed dates are rejected before any API call. Never infer chronology from source order or stop because a page has no qualifying entries.

Interpret JSON stdout and process exit status together:

| Exit | Meaning | Action |
| --- | --- | --- |
| 0 | `complete: true`; null terminal cursor and examined count equals source total | Present `vendors` as final, identifying interval, snapshot, USD and integer cents. An empty list is a valid complete result. |
| 75 | `complete: false`; quota boundary or tranche changed | State that work is incomplete, report examined/total counts, retain checkpoint and wait for an operator-approved continuation. |
| 2 | `complete: false`; input, source, checkpoint, protocol or local I/O failure | Report the error; preserve checkpoint and resolve cause. Never treat an error as an empty final page. |

Incomplete output deliberately omits vendor totals. Report progress only; do not present it as the requested rollup. Each invocation makes at most two successful page calls, uses the source's reported remaining allowance, and stops at the current tranche. Re-running cannot replenish that allowance. Only the operator grants a new tranche. Do not call `grant-tranche`, initialize/reset a source, create a replacement state to obtain fresh quota, or read fixture/database entries to bypass pagination. If no further tranche is granted, the request stays incomplete indefinitely; do not promise completion.

## Recovery and result rules

The checkpoint stores validated source entries, incorporated request cursors, and the next cursor atomically under an exclusive local lock. A successfully saved page advances all of them together. A response lost before saving leaves the previous cursor in place: the next run retries that cursor only if quota permits. A repeated page consumes quota again but cannot be incorporated twice. A crash after saving resumes from the next cursor. Completed checkpoints can be reported again without page calls (metadata is revalidated).

Qualifying entries have status `settled` and `start <= posted_on <= end`. `settled_charge_cents` and `settled_credit_cents` are nonnegative sums; `net_cents` is charges minus credits. Include each vendor with at least one qualifying entry, including zero amounts and zero/negative nets. `qualifying_entry_count` counts both qualifying kinds. Vendors sort lexicographically by `vendor_id`. Arithmetic uses Python integers, never floats.

Checkpoint storage grows with source size. It contains source data, so use authorized private storage. Do not manually edit, delete, rewind or share checkpoints across requests. The runner fails closed on detected corruption; it does not reconstruct a lost checkpoint from source metadata. Source calls and checkpoint writes cannot be one transaction: a crash may waste a call, requiring a later approved tranche. `flock` only coordinates runner processes using the same checkpoint. The operator must not grant a tranche concurrently with execution, and multiple processes must not operate on the same request using different checkpoints. See [verification](references/verification.md) for tested behavior and limits.
