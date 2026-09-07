# June 2026 receiving review

All six supplied purchase-order lines are in scope. The supported results are: two received as ordered, two complete shortfalls, one complete excess, and one line whose final position is undetermined because the June export is not confirmed complete.

| Order / SKU | Ordered | June evidence and coverage | Supported receipt position | Evidence issue | Next action |
|---|---:|---|---|---|---|
| PO-R2606-410 / LABEL-60 | 120 | RCV-H1801 `+75`, RCV-H1802 `+50`, RCV-H1803 `-5`; net **120**. The exact repeated copy of RCV-H1801 was counted once. June coverage: complete. | **Received as ordered** (120 = 120). | None. | None. |
| PO-R2606-410 / CARTON-M | 80 | RCV-H1804 `+50`, RCV-H1805 `-8`; net **42**. RCV-H1720 (`+20`) is dated May and was excluded. June coverage: complete. | **Complete shortfall of 38** (42 vs. 80). | None; the shortfall is supported by complete June evidence. | Mara Quinn should confirm the remaining 38 units. Draft 1 below. |
| PO-R2606-411 / GLOVE-N | 60 | RCV-H1806 `+66`, RCV-H1807 `-2`; net **64**. June coverage: complete. | **Complete excess of 4** (64 vs. 60). | None; the excess is supported by complete June evidence. | Noel Price should reconcile the four-unit surplus. Draft 2 below. |
| PO-R2606-412 / FILM-300 | 24 | RCV-H1808 `+24`; net **24**. RCV-H1901 (`-4`) is dated July and was excluded. June coverage: complete. | **Received as ordered** (24 = 24). | None. | None. |
| PO-R2606-413 / SEAL-BLUE | 40 | RCV-H1809 `+35`, RCV-H1810 `-5`; observed June subtotal **30**. June coverage: **incomplete**. | **Undetermined.** The observed subtotal is not a final shortfall because the export is not confirmed complete. | Full June evidence is missing or unconfirmed. | Simone Bell should provide or confirm the full June export before comparison. Draft 3 below. |
| PO-R2606-414 / TAPE-48 | 30 | No June receipt events; with complete June coverage, supported net is **0**. June coverage: complete. | **Complete shortfall of 30** (0 vs. 30). | None; zero is used here only because coverage explicitly says the export is complete. | Owen Malik should confirm the remaining 30 units. Draft 4 below. |

RCV-H1811 belongs to PO-R2606-499, which is outside the supplied order set, so it does not contribute to this review. No current-month SKU mismatch or conflicting event content appears in the supplied June evidence. Processor validation errors: none.

## Follow-up drafts

### Draft 1 — complete shortfall

**To:** Mara Quinn <mara.quinn@harborpack.example>  
**Subject:** PO-R2606-410 / CARTON-M — 38-unit June receiving shortfall

Our complete June receiving evidence shows 42 net units received against 80 CARTON-M units ordered on PO-R2606-410: RCV-H1804 recorded 50 and RCV-H1805 recorded a return/correction of 8. Please confirm the status of the remaining 38 units and provide the expected delivery date or any source correction needed to reconcile the order.

### Draft 2 — complete excess

**To:** Noel Price <noel.price@juniperworks.example>  
**Subject:** PO-R2606-411 / GLOVE-N — reconcile four-unit June surplus

The complete June evidence shows 64 net GLOVE-N units received against 60 ordered on PO-R2606-411: RCV-H1806 recorded 66 and RCV-H1807 recorded `-2`. Please reconcile the four-unit surplus against the purchase order and source receiving records and advise whether a receiving correction or order update is required.

### Draft 3 — incomplete export

**To:** Simone Bell <simone.bell@juniperworks.example>  
**Subject:** PO-R2606-413 / SEAL-BLUE — full June receiving export needed

The available June events show an observed subtotal of 30 SEAL-BLUE units against 40 ordered on PO-R2606-413 (RCV-H1809 `+35`; RCV-H1810 `-5`), but coverage is marked incomplete. Please provide or confirm the full June export for this order/SKU, including all receipts and returns or corrections, and confirm when coverage is complete so the final receipt comparison can be made.

### Draft 4 — complete shortfall with no June events

**To:** Owen Malik <owen.malik@bindwell.example>  
**Subject:** PO-R2606-414 / TAPE-48 — confirm 30 units outstanding

The complete June export contains no receipt events for the 30 TAPE-48 units ordered on PO-R2606-414, supporting a June net receipt of zero and a 30-unit shortfall. Please confirm whether all 30 units remain outstanding, provide the expected delivery date, or identify any source record that should be reconciled.

These are drafts only. No messages were sent and no receiving records were changed. The supplied processor run and representative component checks establish the observed behavior for these inputs; they do not establish that every future review will be interpreted effectively by an agent.
