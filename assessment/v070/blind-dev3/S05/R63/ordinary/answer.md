# June 2026 receiving review

The supplied input passed validation. All six supplied purchase-order lines are represented below. Four lines need follow-up; two are received as ordered.

| Purchase order | SKU | Ordered | June evidence | Receipt position | Follow-up |
|---|---|---:|---:|---|---|
| PO-R2606-410 | LABEL-60 | 120 | 120 net across 3 unique events | **Received as ordered** | None |
| PO-R2606-410 | CARTON-M | 80 | 42 net across 2 events | **Complete shortfall: 38** | Supplier: Mara Quinn |
| PO-R2606-411 | GLOVE-N | 60 | 64 net across 2 events | **Complete excess: 4** | Warehouse lead: Noel Price |
| PO-R2606-412 | FILM-300 | 24 | 24 net across 1 event | **Received as ordered** | None |
| PO-R2606-413 | SEAL-BLUE | 40 | Observed subtotal 30 across 2 events | **Incomplete evidence; no final receipt position** | Data steward: Simone Bell |
| PO-R2606-414 | TAPE-48 | 30 | 0; no June events | **Complete shortfall: 30** | Supplier: Owen Malik |

## Evidence notes

- The coverage manifest marks the June export complete for every line except PO-R2606-413 / SEAL-BLUE. Complete lines can therefore be compared with their ordered quantities; SEAL-BLUE cannot.
- The repeated copy of event `RCV-H1801` is exact and was counted once. The unique LABEL-60 events net to 120: 75 + 50 - 5.
- Event `RCV-H1720` is from May and event `RCV-H1901` is from July, so neither contributes to the June review.
- Event `RCV-H1811` belongs to unsupplied order PO-R2606-499 and is outside scope.
- No conflicting event IDs or current-month SKU identity mismatches were found.

## Recipient-specific drafts

### Mara Quinn <mara.quinn@harborpack.example>

**Subject:** PO-R2606-410 / CARTON-M — 38-unit June shortfall

Hi Mara,

Our complete June receipt export shows a net 42 CARTON-M units received against 80 ordered on PO-R2606-410, leaving 38 units outstanding. Please confirm the status of the remaining 38 units and the expected delivery date.

Thanks,  
Dana

### Noel Price <noel.price@juniperworks.example>

**Subject:** PO-R2606-411 / GLOVE-N — reconcile 4-unit excess

Hi Noel,

Our complete June receipt export shows a net 64 GLOVE-N units received against 60 ordered on PO-R2606-411, an excess of 4 units. Please reconcile the surplus against the order and receiving evidence and advise whether a receiving correction or other action is needed.

Thanks,  
Dana

### Simone Bell <simone.bell@juniperworks.example>

**Subject:** PO-R2606-413 / SEAL-BLUE — complete June receipt export needed

Hi Simone,

The June coverage manifest marks the receipt export incomplete for PO-R2606-413 / SEAL-BLUE. The available events total 30 units net (35 received and a 5-unit reversal) against 40 ordered, but that subtotal is not a final receipt position. Please provide or confirm the full June receipt export so we can complete the comparison.

Thanks,  
Dana

### Owen Malik <owen.malik@bindwell.example>

**Subject:** PO-R2606-414 / TAPE-48 — 30 units outstanding in June

Hi Owen,

Our complete June receipt export contains no receipt events for the 30 TAPE-48 units ordered on PO-R2606-414, leaving all 30 units outstanding. Please confirm the order status and expected delivery date.

Thanks,  
Dana

These drafts were prepared only; no messages were sent and no source records were changed.
