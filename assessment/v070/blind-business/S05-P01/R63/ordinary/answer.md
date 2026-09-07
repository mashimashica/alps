# June 2026 receiving review

The review covers all six supplied purchase-order lines for `2026-06`. Signed June receipt events were summed after exact-event deduplication; a negative quantity is a return or reversal. A final receipt position is stated only where the supplied coverage declaration is complete.

## Receipt positions

| Order / SKU | Ordered | June evidence | Observed received | Final position | Evidence and issues |
|---|---:|---|---:|---|---|
| `PO-R2606-410` / `LABEL-60` | 120 | `RCV-H1801` +75, `RCV-H1802` +50, `RCV-H1803` -5 | 120 | **120 final — received as ordered** | Coverage: `2026-06`, complete. The exact duplicate copy of `RCV-H1801` was counted once. No follow-up needed. |
| `PO-R2606-410` / `CARTON-M` | 80 | `RCV-H1804` +50, `RCV-H1805` -8 | 42 | **42 final — shortfall of 38** | Coverage: `2026-06`, complete. `RCV-H1720` (+20) is a May event and does not contribute to June. Supplier follow-up required. |
| `PO-R2606-411` / `GLOVE-N` | 60 | `RCV-H1806` +66, `RCV-H1807` -2 | 64 | **64 final — excess of 4** | Coverage: `2026-06`, complete. Warehouse reconciliation required. |
| `PO-R2606-412` / `FILM-300` | 24 | `RCV-H1808` +24 | 24 | **24 final — received as ordered** | Coverage: `2026-06`, complete. `RCV-H1901` (-4) is a July event and does not contribute to June. No follow-up needed. |
| `PO-R2606-413` / `SEAL-BLUE` | 40 | `RCV-H1809` +35, `RCV-H1810` -5 | 30 | **Final quantity unknown** | Coverage: `2026-06`, **incomplete**. The 30 units are an observed subtotal only; the evidence does not support calling this a 10-unit shortfall. Data-steward follow-up required. |
| `PO-R2606-414` / `TAPE-48` | 30 | No June receipt events | 0 | **0 final — shortfall of 30** | Coverage: `2026-06`, complete. Supplier follow-up required. |

Summary: 2 lines received as ordered, 2 complete shortfalls, 1 complete excess, and 1 line with an incomplete export. The report found no global issues, conflicting event IDs, or order/SKU identity conflicts.

## Excluded evidence

- `RCV-H1811` (`PO-R2606-499` / `PALLET-STD`, +90) is outside the supplied order set and was ignored.
- `RCV-H1720` is dated `2026-05`, and `RCV-H1901` is dated `2026-07`; neither contributes to the requested June review.
- The second copy of `RCV-H1801` is an exact duplicate, so its +75 quantity was counted once rather than twice.

## Draft follow-up — shortfall

**To:** Mara Quinn <mara.quinn@harborpack.example>  
**Subject:** PO-R2606-410 / CARTON-M — 38 units remaining for June

Hello Mara,

Our complete June 2026 receiving evidence for PO-R2606-410, SKU CARTON-M, shows a net 42 units received against 80 ordered (`RCV-H1804` +50 and `RCV-H1805` -8). Please confirm and arrange receipt of the remaining 38 units, or provide details of any shipment or adjustment that should resolve the shortfall.

Thank you,  
Dana Ivers

## Draft follow-up — excess

**To:** Noel Price <noel.price@juniperworks.example>  
**Subject:** PO-R2606-411 / GLOVE-N — reconcile 4-unit June excess

Hello Noel,

Our complete June 2026 receiving evidence for PO-R2606-411, SKU GLOVE-N, shows a net 64 units received against 60 ordered (`RCV-H1806` +66 and `RCV-H1807` -2). Please reconcile the 4 surplus units against the purchase order and receiving evidence and advise what correction or disposition is needed.

Thank you,  
Dana Ivers

## Draft follow-up — incomplete evidence

**To:** Simone Bell <simone.bell@juniperworks.example>  
**Subject:** PO-R2606-413 / SEAL-BLUE — complete June receiving evidence needed

Hello Simone,

The June coverage declaration for PO-R2606-413, SKU SEAL-BLUE, is incomplete. The available events support an observed net subtotal of 30 units (`RCV-H1809` +35 and `RCV-H1810` -5) against 40 ordered, but they do not support a final receipt position. Please provide or confirm the full June receiving export and coverage evidence so the line can be finalized.

Thank you,  
Dana Ivers

## Draft follow-up — shortfall

**To:** Owen Malik <owen.malik@bindwell.example>  
**Subject:** PO-R2606-414 / TAPE-48 — 30 units remaining for June

Hello Owen,

Our complete June 2026 receiving evidence for PO-R2606-414, SKU TAPE-48, contains no June receipt events, leaving a final received quantity of 0 against 30 ordered. Please confirm and arrange receipt of the remaining 30 units, or provide details of any shipment or adjustment that should resolve the shortfall.

Thank you,  
Dana Ivers

These drafts are prepared only. No messages were sent and no receiving records were changed.

## Limitation

The final June receipt position for `PO-R2606-413` / `SEAL-BLUE` cannot be determined from the supplied evidence because its coverage declaration is explicitly incomplete. The other five lines have complete coverage and support the final quantities shown above.
