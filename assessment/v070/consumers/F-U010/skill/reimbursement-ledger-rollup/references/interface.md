# Rollup operation interface

## Invocation

```sh
python3.12 scripts/rollup_ledger.py \
  --api /absolute/path/ledger_api.py \
  --source-state /absolute/path/source.sqlite \
  --checkpoint /absolute/path/request-checkpoint.json \
  --start-date 2026-02-01 \
  --end-date 2026-02-15
```

All four paths are resolved to absolute paths. `--api` and `--source-state` must already exist. The checkpoint parent must already exist. A checkpoint is bound to the resolved API path, source-state path, interval, snapshot ID, and source record count. Reusing it with different values returns an error before any page call.

`--command-timeout-seconds` optionally changes the per-API-command timeout from 30 seconds. It must be positive.

## Required source CLI contract

The script invokes the source with the running Python interpreter:

```text
API --state STATE describe
API --state STATE page --snapshot SNAPSHOT
API --state STATE page --snapshot SNAPSHOT --cursor CURSOR
```

`describe` must return one JSON object containing `snapshot_id`, `total_records`, `page_size`, `calls_per_tranche`, `tranche`, and `remaining_calls`. The operation requires `calls_per_tranche` to be exactly `2`.

A successful page must return one JSON object containing exactly `snapshot_id`, `items`, `next_cursor`, `total_records`, and `tranche`. Each item must contain exactly:

| Field | Accepted value |
| --- | --- |
| `entry_id` | Nonempty string, unique in the snapshot |
| `vendor_id` | Nonempty string |
| `posted_on` | Canonical ISO calendar date, `YYYY-MM-DD` |
| `kind` | `charge` or `credit` |
| `status` | `settled`, `pending`, or `void` |
| `amount_cents` | Nonnegative integer; booleans are rejected |
| `currency` | `USD` |

The script passes every non-null `next_cursor` unchanged. Only a null cursor establishes exhaustion. It checks response identity, page size, cursor progress, entry uniqueness, and the final examined count against `total_records`.

## Selection and calculations

An entry qualifies only when `status` is `settled` and `start_date <= posted_on <= end_date`. For each vendor with one or more qualifying entries:

- `settled_charge_cents` is the sum of qualifying `charge` amounts.
- `settled_credit_cents` is the sum of qualifying `credit` amounts.
- `net_cents` is charge cents minus credit cents.
- `qualifying_entry_count` counts both qualifying charges and credits.

The complete `vendors` array is sorted by `vendor_id`; no net-value filter is applied.

## Outputs and exits

Standard output contains one JSON object. Diagnostics from the source are captured rather than mixed into standard output.

Exit `0` returns:

```json
{
  "status": "complete",
  "snapshot_id": "snap_...",
  "interval": {"start": "2026-02-01", "end": "2026-02-15", "inclusive": true},
  "currency": "USD",
  "source_records_examined": 17,
  "source_records_total": 17,
  "vendors": [
    {
      "vendor_id": "example",
      "settled_charge_cents": 1000,
      "settled_credit_cents": 250,
      "net_cents": 750,
      "qualifying_entry_count": 2
    }
  ],
  "checkpoint": "/absolute/path/request-checkpoint.json"
}
```

Exit `75` returns `status: "incomplete"`. It includes identity, examined/total counts, the current tranche and remaining-call observation, the checkpoint path, a reason, and a next action. It deliberately omits vendor totals. Common reasons are `tranche_call_limit_reached`, `no_calls_remaining_in_current_tranche`, and `page_response_unusable`. After an unusable page response, the script refreshes unmetered metadata; if that refresh also fails, `remaining_calls_observed` is null and `quota_refresh_error` explains why.

Exit `2` reports invalid dates, paths, timeout values, or checkpoint/request mismatches. Exit `3` reports a source invocation or response-contract failure. Exit `4` reports an unreadable, unsupported, or internally inconsistent checkpoint. All use `status: "error"` except an unusable page response, which remains safely resumable and therefore uses the incomplete form and exit `75`.

## Continuation and retry guarantees

The checkpoint is replaced atomically only after an entire page has passed validation and its entries have been incorporated. It records the next opaque cursor, entry identifiers and content digests, exact aggregates, and request/source identity. An adjacent advisory lock serializes concurrent invocations that use the same checkpoint.

If a page call may have consumed quota but did not yield a usable response, the stored cursor is unchanged and the operation stops. A later invocation calls `describe` before retrying, so it does not assume the retry is free. If a process stops after the source returns but before checkpoint replacement, the previous checkpoint still points at that page; replaying it reconstructs the same next state. Duplicate or conflicting entry identifiers, cursor cycles, premature exhaustion, and metadata changes are errors and never yield a complete result.
