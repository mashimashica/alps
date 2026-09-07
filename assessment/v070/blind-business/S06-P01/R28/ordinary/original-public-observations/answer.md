# Complete reimbursement rollup

- **Snapshot:** `snap_c22e71aa06b43ab25395e0ce`
- **Inclusive posting-date interval:** `2026-04-03` through `2026-04-09`
- **Status:** Complete; source exhaustion was established by a successfully processed response with a null next cursor.
- **Coverage:** 2 pages processed, 6 of 6 source records examined.

| vendor_id | settled charges (USD cents) | settled credits (USD cents) | net cents | qualifying entry count |
|---|---:|---:|---:|---:|
| `apricot` | 1,234 | 1,234 | 0 | 2 |
| `juniper` | 2,501 | 0 | 2,501 | 1 |
| `willow` | 0 | 407 | -407 | 1 |

The rollup includes only settled entries posted within the requested inclusive interval. It retains the zero-net vendor (`apricot`) and negative-net vendor (`willow`) and is sorted by `vendor_id`.
