# June 2026 receiving review

The review covers all six supplied purchase-order lines. Five lines have complete evidence and a final position (including one shortfall with no June events); one line remains provisional because its June export is explicitly incomplete.

| Order / SKU | June evidence | Coverage | Receipt position | Follow-up |
|---|---|---|---|---|
| PO-R2606-410 / LABEL-60 | Ordered 120; RCV-H1801 +75, RCV-H1802 +50, RCV-H1803 -5; signed net 120. The second identical copy of RCV-H1801 was counted once. | Complete | `received_as_ordered` — net equals ordered quantity. | None. |
| PO-R2606-410 / CARTON-M | Ordered 80; RCV-H1804 +50 and RCV-H1805 -8; signed net 42. | Complete | `complete_shortfall` — 38 remain. | Dana Ivers to ask supplier contact Mara Quinn about the remaining 38. |
| PO-R2606-411 / GLOVE-N | Ordered 60; RCV-H1806 +66 and RCV-H1807 -2; signed net 64. | Complete | `complete_excess` — net is 4 over order. | Warehouse lead Noel Price to reconcile the surplus 4 against the order and receiving evidence. |
| PO-R2606-412 / FILM-300 | Ordered 24; RCV-H1808 +24; signed net 24. | Complete | `received_as_ordered` — net equals ordered quantity. | None. |
| PO-R2606-413 / SEAL-BLUE | Ordered 40; RCV-H1809 +35 and RCV-H1810 -5; observed signed subtotal 30. | Incomplete | `incomplete_export` — no final receipt position. The observed subtotal is 10 below ordered, but incomplete coverage blocks a final comparison. | Data steward Simone Bell to provide or confirm the full June export before the line is compared and any supplier follow-up is decided. |
| PO-R2606-414 / TAPE-48 | Ordered 30; no June events; signed net 0. | Complete | `complete_shortfall` — 30 remain. | Dana Ivers to ask supplier contact Owen Malik about the remaining 30. |

## Excluded evidence and unresolved gaps

- RCV-H1720 (PO-R2606-410 / CARTON-M, +20) is a May 2026 event and does not contribute to the June subtotal.
- RCV-H1901 (PO-R2606-412 / FILM-300, -4) is a July 2026 event and does not contribute to the June subtotal.
- RCV-H1811 (PO-R2606-499 / PALLET-STD, +90) is out of scope because its order is not among the supplied order lines.
- The repeated RCV-H1801 record is an exact duplicate copy, so it contributes +75 only once.
- The only unresolved evidence gap is incomplete June coverage for PO-R2606-413 / SEAL-BLUE. No event-ID conflicts or in-scope order/SKU identity conflicts were detected.

## Draft follow-ups

### To: Mara Quinn <mara.quinn@harborpack.example>
From/action owner: Dana Ivers <dana.ivers@juniperworks.example>  
Subject: PO-R2606-410 / CARTON-M — June receiving shortfall

Hi Mara,

Our complete June receiving evidence for PO-R2606-410 / CARTON-M shows +50 and -8, for a signed net of 42 against 80 ordered. Please confirm the status of the remaining 38 units and the expected delivery or resolution.

Thanks,  
Dana

### To: Noel Price <noel.price@juniperworks.example>
Subject: PO-R2606-411 / GLOVE-N — reconcile June surplus

Hi Noel,

The complete June evidence for PO-R2606-411 / GLOVE-N shows +66 and -2, for a signed net of 64 against 60 ordered. Please reconcile the surplus 4 units against the purchase order and receiving records and confirm the corrected disposition.

Thanks,  
Dana

### To: Simone Bell <simone.bell@juniperworks.example>
Subject: PO-R2606-413 / SEAL-BLUE — complete June receiving export needed

Hi Simone,

The supplied June export for PO-R2606-413 / SEAL-BLUE is marked incomplete. It currently shows +35 and -5, an observed signed subtotal of 30 against 40 ordered, but we cannot make a final receipt comparison from incomplete evidence. Please provide or confirm the full June export so the line can be finalized and any further follow-up assigned.

Thanks,  
Dana

### To: Owen Malik <owen.malik@bindwell.example>
From/action owner: Dana Ivers <dana.ivers@juniperworks.example>  
Subject: PO-R2606-414 / TAPE-48 — June receiving shortfall

Hi Owen,

Our complete June receiving evidence for PO-R2606-414 / TAPE-48 contains no receipt events, giving a signed net of 0 against 30 ordered. Please confirm the status of the remaining 30 units and the expected delivery or resolution.

Thanks,  
Dana

These are drafts only; no messages were sent and no source records were changed.
