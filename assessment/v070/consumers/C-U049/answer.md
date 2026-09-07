# June 2026 receiving review

Prepared for Dana Ivers from the supplied purchase-order lines, June 2026 receipt events, coverage declarations, and contacts. Quantities below use signed receipt events in June only. Exact duplicate events count once.

| Purchase-order line | Ordered | Observed net received | Evidence status | Position | Evidence gap and effect | Follow-up |
|---|---:|---:|---|---|---|---|
| PO-R2606-410 / LABEL-60 | 120 | 120 | Complete; 3 distinct June events | **Received as ordered** | None. Event `RCV-H1801` was supplied twice with identical content and counted once; the supported net is 75 + 50 - 5 = 120. | None |
| PO-R2606-410 / CARTON-M | 80 | 42 | Complete; 2 June events | **Shortfall of 38** | None for June. The May receipt of 20 is outside the requested month and does not affect the June position; the supported net is 50 - 8 = 42. | Supplier: Mara Quinn |
| PO-R2606-411 / GLOVE-N | 60 | 64 | Complete; 2 June events | **Excess of 4** | None; the supported net is 66 - 2 = 64. | Warehouse lead: Noel Price |
| PO-R2606-412 / FILM-300 | 24 | 24 | Complete; 1 June event | **Received as ordered** | None for June. The July return of 4 is outside the requested month and does not affect the June position. | None |
| PO-R2606-413 / SEAL-BLUE | 40 | 30 observed so far | **Incomplete export**; 2 observed June events | **Final position unavailable** | The coverage declaration says the June export is incomplete. The events support an observed subtotal of 35 - 5 = 30, but missing events could change it, so a final shortfall or other position cannot be asserted. | Data steward: Simone Bell |
| PO-R2606-414 / TAPE-48 | 30 | 0 | Complete; no June events | **Shortfall of 30** | None. Complete coverage with no events supports a June net of zero. | Supplier: Owen Malik |

The supplied June event for out-of-scope order `PO-R2606-499` / `PALLET-STD` was excluded. No conflicting event IDs or in-scope absent-SKU identity conflicts were reported.

## Draft follow-ups

### Mara Quinn — CARTON-M shortfall

**To:** Mara Quinn <mara.quinn@harborpack.example>  
**Subject:** PO-R2606-410 / CARTON-M — confirm remaining 38 units

Hello Mara,

Our complete June 2026 receiving evidence for PO-R2606-410, CARTON-M, shows a net 42 units received against 80 ordered, leaving a shortfall of 38 units. The June subtotal includes a receipt of 50 and a return/reversal of 8; the separate May receipt is outside this review period.

Please confirm the status of the remaining 38 units and arrange receipt, or provide shipment details and the expected delivery date.

Thank you,  
Dana Ivers

### Noel Price — GLOVE-N excess

**To:** Noel Price <noel.price@juniperworks.example>  
**Subject:** PO-R2606-411 / GLOVE-N — reconcile 4-unit excess

Hello Noel,

The complete June 2026 receiving evidence for PO-R2606-411, GLOVE-N, shows a net 64 units received against 60 ordered, an excess of 4 units. The supported subtotal is 66 received less a return/reversal of 2.

Please reconcile the 4-unit surplus against the order and warehouse receiving evidence and advise what correction or disposition is needed.

Thank you,  
Dana Ivers

### Simone Bell — incomplete SEAL-BLUE export

**To:** Simone Bell <simone.bell@juniperworks.example>  
**Subject:** PO-R2606-413 / SEAL-BLUE — complete June receiving evidence needed

Hello Simone,

The supplied June 2026 export for PO-R2606-413, SEAL-BLUE, is marked incomplete. The available events show an observed net subtotal of 30 units against 40 ordered, but the missing evidence prevents a final receipt position.

Please provide or confirm the full June receiving export for this order line, including any omitted receipts, returns, or reversals. Once coverage is complete, we can determine the final position.

Thank you,  
Dana Ivers

### Owen Malik — TAPE-48 shortfall

**To:** Owen Malik <owen.malik@bindwell.example>  
**Subject:** PO-R2606-414 / TAPE-48 — confirm remaining 30 units

Hello Owen,

Our complete June 2026 receiving evidence for PO-R2606-414, TAPE-48, shows no receipt events against 30 units ordered, leaving a shortfall of 30 units.

Please confirm the status of all 30 units and arrange receipt, or provide shipment details and the expected delivery date.

Thank you,  
Dana Ivers

These are drafts only; no messages were sent and no source records were changed. The deterministic processor supports this review, but component and script checks do not establish that every future agent will use the skill effectively.
