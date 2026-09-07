# June 2026 receiving review

Scope: all six supplied purchase-order lines for `2026-06`. Signed receipt quantities are applied algebraically. The review is based on `input/receiving.json`; no messages were sent and no source records were changed.

| Order / SKU | Ordered | June evidence | Receipt position | Follow-up |
|---|---:|---|---|---|
| `PO-R2606-410` / `LABEL-60` | 120 | `RCV-H1801` +75, `RCV-H1802` +50, `RCV-H1803` -5; coverage row 0 is complete | **Received as ordered: final net 120.** The exact repeated `RCV-H1801` record counts once. | None |
| `PO-R2606-410` / `CARTON-M` | 80 | `RCV-H1804` +50, `RCV-H1805` -8; coverage row 1 is complete | **Shortfall: final net 42; 38 remaining.** | Dana Ivers to follow up with Mara Quinn |
| `PO-R2606-411` / `GLOVE-N` | 60 | `RCV-H1806` +66, `RCV-H1807` -2; coverage row 2 is complete | **Excess: final net 64; 4 excess.** | Warehouse reconciliation with Noel Price |
| `PO-R2606-412` / `FILM-300` | 24 | `RCV-H1808` +24; coverage row 3 is complete | **Received as ordered: final net 24.** | None |
| `PO-R2606-413` / `SEAL-BLUE` | 40 | `RCV-H1809` +35, `RCV-H1810` -5; coverage row 4 is **not complete** | **Unresolved evidence: observed subtotal 30 only.** A final net and remaining quantity cannot be stated until completeness is resolved. | Dana Ivers to request the complete export/declaration from Simone Bell |
| `PO-R2606-414` / `TAPE-48` | 30 | No June events; coverage row 5 is complete | **Shortfall: final net 0; 30 remaining.** A complete empty export supports the zero final net. | Dana Ivers to follow up with Owen Malik |

## Recipient-specific drafts

**To:** Mara Quinn `<mara.quinn@harborpack.example>`  
**From/action owner:** Dana Ivers `<dana.ivers@juniperworks.example>`  
**Subject:** June 2026 receiving follow-up — PO-R2606-410 / CARTON-M

For June 2026, PO-R2606-410 / CARTON-M was ordered for 80 units. The complete June receipt evidence nets to 42 units (`RCV-H1804` +50 and `RCV-H1805` -8), leaving 38 units outstanding. Please confirm how the remaining 38 units will be completed and provide the next receiving date or required action to Dana Ivers.

---

**To:** Noel Price `<noel.price@juniperworks.example>`  
**Action owner:** Dana Ivers `<dana.ivers@juniperworks.example>`  
**Subject:** June 2026 warehouse reconciliation — PO-R2606-411 / GLOVE-N

For June 2026, PO-R2606-411 / GLOVE-N was ordered for 60 units. The complete June evidence nets to 64 units (`RCV-H1806` +66 and `RCV-H1807` -2), an excess of 4 units. Please reconcile the 4-unit surplus against the order and receiving evidence and report the correction or other action required to Dana Ivers.

---

**To:** Simone Bell `<simone.bell@juniperworks.example>`  
**Action owner:** Dana Ivers `<dana.ivers@juniperworks.example>`  
**Subject:** June 2026 evidence completion — PO-R2606-413 / SEAL-BLUE

For June 2026, the known receipt events for PO-R2606-413 / SEAL-BLUE net to an observed subtotal of 30 units (`RCV-H1809` +35 and `RCV-H1810` -5), against 40 ordered. Coverage row 4 is marked incomplete, so 30 is not a final receipt position and a 10-unit shortfall cannot yet be confirmed. Please provide or confirm the full June event export and a complete coverage declaration so Dana Ivers can make the final comparison and determine any remaining supplier follow-up.

---

**To:** Owen Malik `<owen.malik@bindwell.example>`  
**From/action owner:** Dana Ivers `<dana.ivers@juniperworks.example>`  
**Subject:** June 2026 receiving follow-up — PO-R2606-414 / TAPE-48

For June 2026, PO-R2606-414 / TAPE-48 was ordered for 30 units. The June export is declared complete and contains no matching receipt events, so the final net is 0 and all 30 units remain outstanding. Please confirm how the remaining 30 units will be completed and provide the next receiving date or required action to Dana Ivers.

## Evidence limitations and diagnostics

- `events[6]`, `RCV-H1720` (+20 for `PO-R2606-410` / `CARTON-M`), is dated May 2026 and is excluded from June totals.
- `events[10]`, `RCV-H1901` (-4 for `PO-R2606-412` / `FILM-300`), is dated July 2026 and is excluded from June totals.
- `events[13]`, `RCV-H1811` (+90 for `PO-R2606-499` / `PALLET-STD`), is outside the supplied order set and does not change any in-scope total.
- Only `PO-R2606-413` / `SEAL-BLUE` lacks complete evidence. That gap does not limit the conclusions for the other five lines.

These are drafts only. They have not been sent.
