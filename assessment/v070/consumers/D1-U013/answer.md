# June 2026 receiving review

## Scope and evidence basis

- Review month: **2026-06**.
- Scope: all **6 supplied purchase-order lines** across PO-R2606-410 through PO-R2606-414.
- Only events whose `event_month` is `2026-06` were used. Signed quantities were netted within each line.
- The exact second copy of RCV-H1801 was counted once. No conflicting event IDs or in-scope-order/SKU identity anomalies were found.
- A complete coverage declaration supports a final comparison, including a zero subtotal when no June events exist. An incomplete declaration supports only an observed subtotal, not a final shortage or excess.
- The deterministic processor supplied normalized event sets, subtotals, coverage, and machine-detectable anomalies. The judgments and follow-up drafts below are the review interpretation.

## Line review

| Order / SKU | Ordered | Supported June evidence | Coverage | Judgment and gap | Follow-up |
|---|---:|---|---|---|---|
| PO-R2606-410 / LABEL-60 | 120 | RCV-H1801 `+75`, RCV-H1802 `+50`, RCV-H1803 `-5` = **120**. The exact duplicate of RCV-H1801 was ignored. | Complete | **Received as ordered.** No evidence gap. | None. |
| PO-R2606-410 / CARTON-M | 80 | RCV-H1804 `+50`, RCV-H1805 `-8` = **42** | Complete | **Shortfall: 38 units.** | Mara Quinn (supplier), with Dana Ivers as purchasing coordinator: reconcile the missing 38 units and provide shipment, backorder, cancellation, or credit evidence. |
| PO-R2606-411 / GLOVE-N | 60 | RCV-H1806 `+66`, RCV-H1807 `-2` = **64** | Complete | **Excess: 4 units.** | Noel Price (warehouse lead): verify the physical count and the `-2` adjustment, then provide the evidence needed to confirm or correct the 4-unit excess. |
| PO-R2606-412 / FILM-300 | 24 | RCV-H1808 `+24` = **24** | Complete | **Received as ordered.** No evidence gap. | None. |
| PO-R2606-413 / SEAL-BLUE | 40 | RCV-H1809 `+35`, RCV-H1810 `-5` = **observed subtotal 30** | Incomplete | **Final position unconfirmed.** The apparent 10-unit difference is not a final shortfall because the June receiving export is not declared complete. | Simone Bell (data steward): produce or validate a complete June export for this line, including any omitted receipts or adjustments, and confirm coverage before comparison with the ordered quantity. |
| PO-R2606-414 / TAPE-48 | 30 | No June events; complete coverage supports a **0** subtotal | Complete | **Shortfall: 30 units.** | Owen Malik (supplier), with Dana Ivers as purchasing coordinator: confirm whether all 30 units are unshipped, backordered, cancelled, or received under missing documentation, and provide the corresponding evidence. |

## Excluded and duplicate evidence

- **RCV-H1720** — PO-R2606-410 / CARTON-M, `+20`, event month 2026-05: excluded because it is outside June.
- **RCV-H1901** — PO-R2606-412 / FILM-300, `-4`, event month 2026-07: excluded because it is outside June.
- **RCV-H1811** — PO-R2606-499 / PALLET-STD, `+90`, event month 2026-06: excluded because the order is outside the supplied order set.
- The repeated copy of **RCV-H1801** was an exact duplicate and therefore counted once, not twice.

## Follow-up drafts

### Mara Quinn — CARTON-M shortfall

**To:** Mara Quinn <mara.quinn@harborpack.example>  
**Cc:** Dana Ivers <dana.ivers@juniperworks.example>  
**Subject:** PO-R2606-410 CARTON-M — 38-unit June receipt shortfall

June's complete receiving evidence shows 42 CARTON-M units received net against 80 ordered on PO-R2606-410, leaving a 38-unit shortfall. Please reconcile the remaining 38 units and provide the relevant shipment, backorder, cancellation, or credit evidence so Dana can finish the receiving review.

### Noel Price — GLOVE-N excess

**To:** Noel Price <noel.price@juniperworks.example>  
**Subject:** PO-R2606-411 GLOVE-N — verify 4-unit June excess

June's complete receiving evidence nets to 64 GLOVE-N units against 60 ordered on PO-R2606-411, an excess of 4. Please verify the physical count and the `-2` adjustment and provide the supporting evidence needed to confirm the excess or support a receiving correction.

### Simone Bell — incomplete SEAL-BLUE evidence

**To:** Simone Bell <simone.bell@juniperworks.example>  
**Subject:** PO-R2606-413 SEAL-BLUE — complete June receiving export needed

The current June evidence shows an observed net subtotal of 30 SEAL-BLUE units against 40 ordered, but the export is marked incomplete, so the final receipt position cannot be confirmed. Please produce or validate a complete June export for this line, including any omitted receipts or adjustments, and confirm coverage so the line can be compared with the order.

### Owen Malik — TAPE-48 shortfall

**To:** Owen Malik <owen.malik@bindwell.example>  
**Cc:** Dana Ivers <dana.ivers@juniperworks.example>  
**Subject:** PO-R2606-414 TAPE-48 — 30-unit June receipt shortfall

The complete June receiving evidence contains no events for TAPE-48 on PO-R2606-414, producing a supported subtotal of 0 against 30 ordered. Please confirm whether the 30 units are unshipped, backordered, cancelled, or received under missing documentation and provide the corresponding evidence so Dana can finish the receiving work.

## Limitations

This review is limited to the supplied contract and its coverage declarations; it does not independently verify physical stock, supplier systems, or source-system completeness. No messages were sent and no source records were changed.
