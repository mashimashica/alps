# Complete vendor reimbursement rollup

- **Snapshot:** `snap_c22e71aa06b43ab25395e0ce`
- **Inclusive interval:** `2026-04-03` through `2026-04-09`
- **Status:** Complete. Two successful `page` calls fetched all 6 source records; the second page returned a null next cursor.

| vendor_id | Settled charges | Settled credits | Net (charges − credits) | Qualifying entries |
|---|---:|---:|---:|---:|
| `apricot` | $12.34 (1,234 cents) | $12.34 (1,234 cents) | $0.00 (0 cents) | 2 |
| `juniper` | $25.01 (2,501 cents) | $0.00 (0 cents) | $25.01 (2,501 cents) | 1 |
| `willow` | $0.00 (0 cents) | $4.07 (407 cents) | −$4.07 (−407 cents) | 1 |

Pending, void, and out-of-interval entries were excluded. The exhausted checkpoint is at `work/rollup.json`; its cursor is null, so no continuation is needed. The post-run source description reported tranche 1 with 0 remaining calls.

The supplied helper has a concrete output limitation: although it accumulates all qualifying vendors, its final output loop appends only vendors whose net is zero or negative. Its direct output therefore omitted positive-net vendor `juniper`. The table above corrects that omission by applying the requested settled/date filters and exact-cent aggregation to the helper's complete six-record checkpoint.
