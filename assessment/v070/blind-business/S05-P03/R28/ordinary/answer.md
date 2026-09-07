# June 2026 receiving review

All six supplied purchase-order lines were reviewed. Quantities below are signed June receipts: positive receipts less returns. Exact duplicate events were counted once; events from other months and orders outside the supplied order set were excluded.

| Purchase order | SKU | Ordered | Observed June receipt | Supported position | Evidence and action |
|---|---:|---:|---:|---|---|
| PO-R2606-410 | LABEL-60 | 120 | 120 | **Received as ordered** | 75 + 50 - 5 = 120. Exact duplicate `RCV-H1801` was counted once. No follow-up needed. |
| PO-R2606-410 | CARTON-M | 80 | 42 | **Complete shortfall: 38** | 50 - 8 = 42 against a complete June export. The May receipt of 20 is outside this review month. Ask supplier Mara Quinn to confirm the remaining 38 or provide fulfillment details. |
| PO-R2606-411 | GLOVE-N | 60 | 64 | **Complete excess: 4** | 66 - 2 = 64 against a complete June export. Ask warehouse lead Noel Price to reconcile the four-unit surplus. |
| PO-R2606-412 | FILM-300 | 24 | 24 | **Received as ordered** | The June receipt is 24. The July return of 4 is outside this review month. No June follow-up needed. |
| PO-R2606-413 | SEAL-BLUE | 40 | 30 subtotal | **Incomplete export; final position undetermined** | 35 - 5 = 30 in the available evidence, but coverage is incomplete. This is not a supported shortfall of 10. Ask data steward Simone Bell for the complete June export before making a final comparison. |
| PO-R2606-414 | TAPE-48 | 30 | Not available | **Missing received value** | Coverage is marked complete, but no June quantity-bearing receipt event was supplied. The missing value is not zero. Ask Noel Price to confirm physical receipt activity and Simone Bell to reconcile the export if receipt evidence exists. |

The June event `RCV-H1811` records 90 units of `PALLET-STD` against `PO-R2606-499`, which is outside the supplied order set. It did not affect any line position above. Simone Bell should verify whether it is correctly assigned before it is used in any other receiving review.

## Follow-up drafts

### Mara Quinn — supplier contact

**To:** Mara Quinn <mara.quinn@harborpack.example>  
**Subject:** PO-R2606-410 CARTON-M — June receipt shortfall

Hello Mara,

Our complete June receiving evidence for PO-R2606-410 shows 42 CARTON-M received net of returns against 80 ordered: a receipt of 50 and a return of 8. Please confirm the status of the remaining 38 units. If the order has been fulfilled, please send the shipment or delivery details needed to reconcile our records.

Thank you,  
Dana Ivers

### Noel Price — warehouse lead

**To:** Noel Price <noel.price@juniperworks.example>  
**Subject:** June receiving checks — GLOVE-N surplus and TAPE-48 evidence

Hello Noel,

Please check these two June receiving items:

- PO-R2606-411 / GLOVE-N shows 64 received net of returns against 60 ordered, an excess of 4. Please reconcile the surplus to the order and receiving evidence.
- PO-R2606-414 / TAPE-48 has no quantity-bearing June receipt event in the supplied evidence, although export coverage is marked complete. Please confirm whether any TAPE-48 was physically received in June and share any receipt IDs, dates, and quantities that should be present.

Please send the supporting details so we can close or route each item correctly.

Thank you,  
Dana Ivers

### Simone Bell — data steward

**To:** Simone Bell <simone.bell@juniperworks.example>  
**Subject:** June receiving export follow-up — SEAL-BLUE, TAPE-48, and RCV-H1811

Hello Simone,

Please help reconcile three evidence items in the June receiving review:

- PO-R2606-413 / SEAL-BLUE has an observed subtotal of 30, but its June export is marked incomplete. Please provide or confirm the complete June export for this line.
- PO-R2606-414 / TAPE-48 is marked as having complete coverage, but no quantity-bearing June receipt event was supplied. Please confirm whether the export correctly contains no event, or provide the missing receipt record after the warehouse check.
- Event RCV-H1811 records 90 PALLET-STD against PO-R2606-499, an order outside the supplied review set. Please verify that the order assignment is correct before the event is used elsewhere.

Thank you,  
Dana Ivers

These are drafts only; no messages were sent and no source records were changed. The final June position for SEAL-BLUE remains undetermined until complete evidence is supplied, and the observed June quantity for TAPE-48 remains unknown until its missing-value issue is resolved.
