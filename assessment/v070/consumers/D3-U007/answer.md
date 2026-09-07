# June 2026 receiving review

The review covers all six supplied purchase-order lines for `2026-06`. Signed June receipt quantities were netted by line. The exact duplicate of event `RCV-H1801` was counted once; the May event `RCV-H1720` and July event `RCV-H1901` were excluded from June. Event `RCV-H1811` belongs to unknown order `PO-R2606-499` and was reported as out of scope rather than applied to a supplied line.

| Purchase order | SKU | Ordered | June evidence | Position | Required action |
|---|---|---:|---:|---|---|
| PO-R2606-410 | LABEL-60 | 120 | 120 | Received as ordered | None |
| PO-R2606-410 | CARTON-M | 80 | 42 | Shortfall of 38 | Dana Ivers to contact supplier Mara Quinn |
| PO-R2606-411 | GLOVE-N | 60 | 64 | Excess of 4 | Noel Price to reconcile the surplus |
| PO-R2606-412 | FILM-300 | 24 | 24 | Received as ordered | None |
| PO-R2606-413 | SEAL-BLUE | 40 | 30 observed | **Undetermined — incomplete export** | Simone Bell to provide or confirm the full June export |
| PO-R2606-414 | TAPE-48 | 30 | 0 | Shortfall of 30 | Dana Ivers to contact supplier Owen Malik |

For `SEAL-BLUE`, the observed events net to 30, but the coverage declaration says the June export is incomplete. The line therefore remains undetermined; the apparent difference of 10 is not a confirmed shortfall. For `TAPE-48`, the coverage declaration says the June export is complete and contains no receipt events, so the observed subtotal is zero and the supported position is a 30-unit shortfall.

## Follow-up drafts

**To:** Dana Ivers <dana.ivers@juniperworks.example>  
**Subject:** June receiving follow-up — PO-R2606-410 / CARTON-M

The complete June receipt evidence for PO-R2606-410 / CARTON-M nets to 42 units against 80 ordered: receipt `RCV-H1804` adds 50 and `RCV-H1805` subtracts 8. The May event was excluded from the June review. Please ask Mara Quinn <mara.quinn@harborpack.example> about the remaining 38 units and confirm whether they are still due or whether the receiving evidence needs correction.

---

**To:** Noel Price <noel.price@juniperworks.example>  
**Subject:** June receiving reconciliation — PO-R2606-411 / GLOVE-N

The complete June receipt evidence for PO-R2606-411 / GLOVE-N nets to 64 units against 60 ordered: `RCV-H1806` adds 66 and `RCV-H1807` subtracts 2. Please reconcile the 4-unit surplus against the purchase order and receiving records and confirm the corrected receiving position.

---

**To:** Simone Bell <simone.bell@juniperworks.example>  
**Subject:** Full June export needed — PO-R2606-413 / SEAL-BLUE

The supplied June events for PO-R2606-413 / SEAL-BLUE net to 30 units against 40 ordered, but the coverage declaration marks the export incomplete. Please provide the full June receipt export or confirm that the supplied export is complete. The final receiving position must remain undetermined until that evidence gap is resolved.

---

**To:** Dana Ivers <dana.ivers@juniperworks.example>  
**Subject:** June receiving follow-up — PO-R2606-414 / TAPE-48

The complete June export contains no receipt events for PO-R2606-414 / TAPE-48, leaving an observed subtotal of 0 against 30 ordered. Please ask Owen Malik <owen.malik@bindwell.example> about the remaining 30 units and confirm whether they are still due or whether a receipt record is missing from the source.

## Review limits

No malformed or missing required fields were reported by the review tool. The review relies on the supplied order, event, coverage, and responsibility records; it did not compare the evidence with a live receiving system, physical inventory, delivery documents, or supplier confirmations. These are drafts only: no messages were sent and no receiving records were changed.
