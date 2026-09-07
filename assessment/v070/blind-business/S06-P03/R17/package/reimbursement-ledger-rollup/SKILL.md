---
name: reimbursement-ledger-rollup
description: Produce complete vendor reimbursement rollups from the supplied paginated immutable ledger API, with exact cent arithmetic and resumable two-page tranches.
---

# Reimbursement ledger rollup

Use the bundled `scripts/rollup.py` helper for this task. It obtains the snapshot metadata, validates the inclusive ISO date interval before traversal, fetches at most two successful pages per invocation, and writes a durable checkpoint. Invoke it again with the same checkpoint after the operator grants another tranche. A result is final only when `complete` is true; never present a partial result as complete.

```sh
python3 scripts/rollup.py --api /path/to/ledger_api.py --state /path/to/source.sqlite \
  --start 2026-02-01 --end 2026-02-15 --checkpoint /path/to/rollup.json
```

The JSON output identifies `snapshot_id`, interval, `complete`, `calls_used`, and `vendors`. Each vendor includes settled charge cents, settled credit cents, net cents (charge minus credit), and qualifying entry count, sorted by `vendor_id`; vendors with net zero or negative are retained. Pending and void records are ignored. Empty complete ledgers and intervals with no qualifying entries are valid empty results. Checkpoint files are execution state and may be retained for continuation; do not edit supplied source files or fixture data. If the source snapshot changes, start a new checkpoint rather than combining snapshots.
