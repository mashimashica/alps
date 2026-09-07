# June 2026 receiving review

**Review month:** June 2026 (`2026-06`)  
**Scope:** 6 supplied purchase-order lines; all 6 are included below.

## Line results

| Purchase order | SKU | Ordered | Observed June subtotal | Final net received | Position | Evidence basis and action |
|---|---|---:|---:|---:|---|---|
| PO-R2606-410 | LABEL-60 | 120 | 120 | 120 | Received as ordered | Complete coverage. Accepted events: RCV-H1801 `+75`, RCV-H1802 `+50`, and RCV-H1803 `-5`. The exact repeat of RCV-H1801 was counted once. No follow-up needed. |
| PO-R2606-410 | CARTON-M | 80 | 42 | 42 | **Shortfall: 38** | Complete coverage. Accepted events: RCV-H1804 `+50` and RCV-H1805 `-8`. Dana Ivers should ask the supplied supplier contact for the remaining-unit plan. |
| PO-R2606-411 | GLOVE-N | 60 | 64 | 64 | **Excess: 4** | Complete coverage. Accepted events: RCV-H1806 `+66` and RCV-H1807 `-2`. Noel Price should reconcile the surplus against the order and receiving evidence. |
| PO-R2606-412 | FILM-300 | 24 | 24 | 24 | Received as ordered | Complete coverage. Accepted event: RCV-H1808 `+24`. The July return does not affect the June position. No follow-up needed. |
| PO-R2606-413 | SEAL-BLUE | 40 | 30 | — | **Undetermined** | Coverage is explicitly incomplete. RCV-H1809 `+35` and RCV-H1810 `-5` establish only a 30-unit observed subtotal; they do not support a final comparison with the 40 ordered. Simone Bell must provide or confirm the full June export before the position can be finalized. |
| PO-R2606-414 | TAPE-48 | 30 | 0 | 0 | **Shortfall: 30** | Complete coverage and no accepted June receipt events support a final net of 0. Dana Ivers should ask the supplied supplier contact for the remaining-unit plan. |

## Evidence limits and exclusions

- **PO-R2606-413 / SEAL-BLUE:** the incomplete coverage declaration prevents a final quantity and receipt position. The observed subtotal of 30 must not be treated as a supported 10-unit shortfall. A complete June export could change it.
- **Exact duplicate:** the repeated copy of RCV-H1801 has identical content and was collapsed, so its 75 units were counted once.
- **Outside June:** RCV-H1720 (May, PO-R2606-410 / CARTON-M) and RCV-H1901 (July, PO-R2606-412 / FILM-300) were excluded from June arithmetic.
- **Outside scope:** RCV-H1811 for PO-R2606-499 / PALLET-STD was excluded.
- No conflicting event IDs, unknown in-scope SKUs, invalid input rows, or missing recipient identities were found in the supplied evidence.

## Follow-up drafts

### 1. CARTON-M shortfall — Dana Ivers to Mara Quinn

**Next action:** Ask the supplier to confirm the receipt plan for the remaining 38 units.

> **To:** Mara Quinn <mara.quinn@harborpack.example>  
> **From/owner:** Dana Ivers <dana.ivers@juniperworks.example>  
> **Subject:** PO-R2606-410 / CARTON-M — remaining 38 units  
>  
> For PO-R2606-410, SKU CARTON-M, the complete June 2026 receiving evidence shows a final net receipt of 42 units against 80 ordered, leaving a 38-unit shortfall. Please confirm the delivery or resolution plan for the remaining 38 units.

### 2. GLOVE-N excess — Noel Price

**Next action:** Reconcile the 4-unit surplus against the order and receiving evidence, then confirm its source and disposition.

> **To:** Noel Price <noel.price@juniperworks.example>  
> **From/owner:** Noel Price <noel.price@juniperworks.example>  
> **Subject:** Reconcile PO-R2606-411 / GLOVE-N excess  
>  
> Please reconcile PO-R2606-411, SKU GLOVE-N. The complete June 2026 evidence shows a final net receipt of 64 units against 60 ordered, an excess of 4. Please confirm the source of the surplus and the corrective disposition.

### 3. SEAL-BLUE incomplete export — Simone Bell

**Next action:** Provide or confirm the full June receiving-event export and resolve the incomplete coverage declaration before the receipt position is finalized.

> **To:** Simone Bell <simone.bell@juniperworks.example>  
> **From/owner:** Simone Bell <simone.bell@juniperworks.example>  
> **Subject:** Complete June export for PO-R2606-413 / SEAL-BLUE  
>  
> Please provide or confirm the complete June 2026 receiving-event export for PO-R2606-413, SKU SEAL-BLUE, and confirm its coverage status. The currently accepted events produce an observed subtotal of 30 units, but that subtotal is not being treated as a final receipt position because coverage is incomplete.

### 4. TAPE-48 shortfall — Dana Ivers to Owen Malik

**Next action:** Ask the supplier to confirm the receipt plan for the remaining 30 units.

> **To:** Owen Malik <owen.malik@bindwell.example>  
> **From/owner:** Dana Ivers <dana.ivers@juniperworks.example>  
> **Subject:** PO-R2606-414 / TAPE-48 — remaining 30 units  
>  
> For PO-R2606-414, SKU TAPE-48, the complete June 2026 receiving evidence shows a final net receipt of 0 units against 30 ordered, leaving a 30-unit shortfall. Please confirm the delivery or resolution plan for the remaining 30 units.

All communications above are drafts only. No messages were sent and no source or receiving records were changed.
