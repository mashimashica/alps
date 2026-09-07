# Complete vendor reimbursement rollup

Source snapshot: `snap_c22e71aa06b43ab25395e0ce`  
Posting-date interval: `2026-04-03` through `2026-04-09`, inclusive  
Currency and arithmetic: USD, exact integer cents

| vendor_id | settled_charge_cents | settled_credit_cents | net_cents | qualifying_entry_count |
| --- | ---: | ---: | ---: | ---: |
| `apricot` | 1234 | 1234 | 0 | 2 |
| `juniper` | 2501 | 0 | 2501 | 1 |
| `willow` | 0 | 407 | -407 | 1 |

Completion was established: the workflow returned `complete: true` with reason `source_exhausted`, and examined all 6 of 6 source records. Only settled entries posted within the inclusive interval were included. The result retains both the zero-net vendor (`apricot`) and negative-net vendor (`willow`) and is sorted lexicographically by `vendor_id`.
