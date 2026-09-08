# Interface and recovery

## Operational contract

The caller supplies a trusted local `ledger_api.py` and an initialized state file. Python 3.12 runs that CLI as a subprocess with no shell interpolation. It is an external runtime dependency supplied with the ledger; this Skill has no production credentials or live endpoint. Never initialize or grant tranches from the target work.

Unmetered metadata command:

```sh
python3.12 /absolute/ledger_api.py --state /absolute/source.sqlite describe
```

It returns `snapshot_id`, `total_records`, `page_size: 3`, `calls_per_tranche: 2`, positive integer `tranche`, and `remaining_calls` (0–2). First page:

```sh
python3.12 /absolute/ledger_api.py --state /absolute/source.sqlite page --snapshot SNAPSHOT_ID
```

Following pages add `--cursor RETURNED_CURSOR`, passing the non-null cursor unchanged. Each page returns `snapshot_id`, `items`, `next_cursor`, `total_records`, and `tranche`. Only a null next cursor ends traversal. Pages are stable, disjoint, and nonchronological. Empty ledgers return an empty first page and null cursor. Every successful page call consumes one allowance, even on replay or if its response is lost. Exit 75 means budget exhaustion with no entries; 2 means invalid cursor/input and 4 means snapshot mismatch. Invalid cursors and snapshot mismatches do not consume allowance.

Each item has exactly:

| Field | Required value |
| --- | --- |
| `entry_id` | Unique nonempty string within snapshot |
| `vendor_id` | Nonempty string |
| `posted_on` | Valid ISO calendar date `YYYY-MM-DD` |
| `kind` | `charge` or `credit` |
| `status` | `settled`, `pending`, or `void` |
| `amount_cents` | Nonnegative integer; not floating point or boolean |
| `currency` | `USD` |

## Public runner operations

`run` requires `--api`, `--state`, `--start`, `--end`, `--checkpoint`, and `--output`. It validates dates before source access, binds the checkpoint to resolved paths, snapshot and interval, then processes at most the initial tranche's remaining allowance. It never grants or advances a tranche. A new operator grant is reflected in `describe`; the same run command can then continue.

`status` requires only `--checkpoint` and `--output`. It reads committed progress without contacting the source. Completed status reflects the recorded immutable snapshot, not a claim that a replacement state at the old path still matches it.

Both write the full result JSON to `--output` and emit a bounded coverage/status summary to stdout. Errors go to stderr as JSON. The output contains `status`, `complete`, `snapshot_id`, `start`, `end`, `currency`, `examined_entries`, `total_records`, `committed_pages`, `next_cursor`, `reason`, and sorted `vendors`. Vendor rows contain `vendor_id`, `settled_charge_cents`, `settled_credit_cents`, `net_cents`, and `qualifying_entry_count`. A partial result uses these same fields with `complete: false`.

| Exit | Meaning and next action |
| --- | --- |
| 0 | Complete; present the result after confirming identity and coverage |
| 10 | Incomplete; keep checkpoint, coordinate further operator tranche |
| 2 | Invalid arguments, identity, protocol or local state; inspect detail, correct cause |
| 3 | Uncertain source failure/response; inspect quota, preserve checkpoint and resume safely |
| 4 | Source snapshot mismatch; confirm original source, never merge snapshots |
| 75 | Source allowance exhausted; incomplete, wait for operator grant |

Errors do not make an existing output file current. `status` regenerates the committed view. CLI argument syntax errors use argparse's text stderr and exit 2.

## Recovery and effects

The runner writes a JSON checkpoint, a persistent `.lock` file, same-directory temporary files, and the requested output. The source CLI changes only its explicitly supplied state and SQLite journal. Use distinct work-product paths that do not alias source files; do not point paths at hard links to protected files. Checkpoint files include all fetched records and need the same handling as the source ledger.

A page's records, cursor history, next cursor, and exhaustion marker are committed together using temporary-file write, file fsync, atomic replace, and parent-directory fsync. Duplicate entry IDs and cursor loops are rejected. The checkpoint keeps raw records and recalculates totals using Python integers, avoiding binary floats and SQLite integer overflow. This requires O(number of records) memory and disk; rewriting the growing checkpoint on each page is intended for modest snapshots. Large snapshots require a tested storage adaptation.

If a call response is lost or the process stops before checkpoint replacement, its cursor is not advanced. Inspect `describe` for remaining quota, then resume the same command: it fetches the same page only if allowance remains. The page's entries are then committed once. If replacement succeeded before interruption, continuation uses the next cursor and does not re-add the committed page. No claim of exactly-once API calls is made: retries can consume more calls and require more tranches. Repeating a completed command performs only metadata validation and output regeneration.

Do not manually edit, roll back, delete, or merge checkpoints. Preserve the original source state. If a checkpoint is lost, report progress as unrecoverable from that checkpoint; any full restart must traverse the source again under available approvals, with no completeness claim until exhaustion. Filesystem corruption, untrusted checkpoint edits, hard-link aliases, concurrent source use, and simultaneous operator grants are outside the supported conditions. The runner locks a checkpoint against concurrent writers but does not lock the separately implemented source for the entire run.
