# July 2026 receiving review

## Scope and handling

This review covers all 13 supplied purchase-order lines for **2026-07**. July receipt quantities are net of returns and correcting reversals. Exact duplicate copies were counted once, and June events were excluded from July totals. Coverage declarations were evaluated by order line and month; a declaration for another month does not establish July completeness.

No messages were sent and no receiving records were changed. All follow-ups below are drafts.

## Line review

| Order / SKU | Ordered | Evidence summary | Status and evidence gap | Needed follow-up |
|---|---:|---|---|---|
| PO-S2607-820 / BOLT-M8 | 100 | Complete July evidence. `RCV-K7101` 70 + `RCV-K7102` 30 − `RCV-K7103` 10 = **90 net**. | **Complete shortfall: 10.** No evidence gap stated. | Supplier: Tessa Holt; ask about the remaining 10. Draft 1. |
| PO-S2607-820 / WASHER-M8 | 200 | Complete July evidence. `RCV-K7104` = **200 net**. | **Received as ordered.** | None. |
| PO-S2607-821 / PACK-RACK | 48 | `RCV-K7106` records 20. A further 18 is labeled `RCV-K7107`, but that same event ID is also attached to a different order/SKU. | **Unresolved—conflicting evidence.** The undisputed subtotal is 20; the disputed 18 cannot support a final position until its identity is reconciled. | Purchasing coordinator and data steward: Rowan Ames and Beck Lin. Draft 2. |
| PO-S2607-821 / STRAP-20 | 60 | Complete July evidence. `RCV-K7109` = **60 net**. | **Received as ordered.** | None. |
| PO-S2607-822 / SHIELD-CLR | 40 | `RCV-K7108` records 28. A further 12 is labeled `RCV-K7107`, but that event ID conflicts with the PACK-RACK record above. | **Unresolved—conflicting evidence.** The undisputed subtotal is 28. If the disputed 12 belongs here, the line totals 40; if not, it is 12 short. A final judgment is not established. | Purchasing coordinator and data steward: Rowan Ames and Beck Lin. Draft 2. |
| PO-S2607-823 / POUCH-12 | 30 | Incomplete July coverage. Exact duplicate `RCV-K7110` was counted once: 36 − 2 (`RCV-K7111`) = **34 observed**. | **Incomplete evidence.** The observed subtotal is 34, but a final excess cannot be claimed until the full export is confirmed. | Data steward: Beck Lin. Draft 3. |
| PO-S2607-824 / TRAY-L | 18 | July events total 12 − 3 = **9 observed**. The only complete coverage declaration supplied is for June, not July. | **Incomplete July evidence.** The observed subtotal is 9; no final shortfall is established. | Data steward: Beck Lin. Draft 4. |
| PO-S2607-825 / BINDER-B | 25 | No qualifying July event is supplied, and July coverage is incomplete. | **Incomplete evidence.** No event was observed, but that does not establish a zero receipt or a 25-unit shortfall. | Data steward: Beck Lin. Draft 5. |
| PO-S2607-826 / INSERT-G | 70 | Complete July evidence. Exact duplicate `RCV-K7114` was counted once: 45 + 40 − 10 = **75 net**. The June −10 event was excluded. | **Complete excess: 5.** The separate June `INSERT-OLD` identity issue was not folded into this line. | Warehouse lead: Inez Cole; reconcile the 5-unit surplus. Draft 6. |
| PO-S2607-827 / WRAP-500 | 40 | Complete July evidence. 20 + 6 − 8 = **18 net**. | **Complete shortfall: 22.** | Supplier: Felix Arun; ask about the remaining 22. Draft 7. |
| PO-S2607-828 / CLIP-R | 10 | Complete July evidence. 6 + 4 = **10 net**. | **Received as ordered.** | None. |
| PO-S2607-829 / PAD-FOAM | 12 | Complete July evidence. 5 − 9 = **−4 net**. The June receipt of 9 was excluded. | **Complete shortfall: 16 relative to the ordered quantity.** The negative July net reflects the supplied return/correction evidence. | Supplier: Rafael Brooks; ask how the 16-unit gap will be resolved and reference the July correction. Draft 8. |
| PO-S2607-830 / CRATE-S | 16 | Complete July coverage and no qualifying July events: **0 net**. | **Complete shortfall: 16.** | Supplier: Elena Duarte; ask about the remaining 16. Draft 9. |

## Other evidence findings

- **Conflicting event ID:** `RCV-K7107` appears once as PO-S2607-821 / PACK-RACK / 18 and once as PO-S2607-822 / SHIELD-CLR / 12. Both affected line judgments remain open pending source reconciliation.
- **Identity reconciliation:** `RCV-K7105` records 12 units of `NUT-M8` against in-scope PO-S2607-820, but that SKU is absent from the supplied order lines. `RCV-K6991` records 7 units of `INSERT-OLD` against in-scope PO-S2607-826 in June, also absent from the supplied order lines. Neither was folded into an ordered-line comparison. Draft 10 addresses both.
- **Out of scope:** `RCV-K7124` (PO-S2607-899 / WRAP-500 / 500) belongs to an order outside the supplied order set and was excluded.
- **Prior month:** `RCV-K6990`, `RCV-K6991`, and `RCV-K6992` are June records and were excluded from July receipt totals.

## Draft follow-ups

### Draft 1 — BOLT-M8 complete shortfall

**To:** Tessa Holt <tessa.holt@ridgefast.example>  
**Subject:** PO-S2607-820 / BOLT-M8 — July receipt shortfall of 10

The complete July receiving evidence for PO-S2607-820 / BOLT-M8 shows 90 net units received against 100 ordered, including the supplied 10-unit return/correction. Please confirm the status and expected receipt timing for the remaining 10 units, or provide the source document if the order quantity or disposition has changed.

### Draft 2 — conflicting event identity affecting two lines

**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** Reconcile RCV-K7107 across PO-S2607-821 and PO-S2607-822

Event ID `RCV-K7107` has conflicting July content: 18 units for PO-S2607-821 / PACK-RACK and 12 units for PO-S2607-822 / SHIELD-CLR. Please reconcile the authoritative order, SKU, and quantity in the source records and confirm the corrected July export. Until then, PACK-RACK has an undisputed observed subtotal of 20 against 48 ordered, and SHIELD-CLR has an undisputed observed subtotal of 28 against 40 ordered; neither line has a final receipt position.

### Draft 3 — POUCH-12 incomplete export

**To:** Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** Confirm complete July export for PO-S2607-823 / POUCH-12

The supplied July rows show 34 net units for PO-S2607-823 / POUCH-12 after counting the exact duplicate `RCV-K7110` once, but coverage is marked incomplete. Please provide or confirm the full July export for this line so its final receipt position can be established.

### Draft 4 — TRAY-L missing July coverage

**To:** Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** Provide July coverage confirmation for PO-S2607-824 / TRAY-L

The supplied July events show 9 net units for PO-S2607-824 / TRAY-L against 18 ordered, but the only complete coverage declaration supplied is for June. Please provide or confirm the full July export and July coverage status before a final shortfall judgment is made.

### Draft 5 — BINDER-B incomplete export with no observed row

**To:** Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** Confirm complete July export for PO-S2607-825 / BINDER-B

No qualifying July receipt event is present for PO-S2607-825 / BINDER-B, and July coverage is incomplete. Please provide or confirm the full July export. The absence of a row in the current packet is not being treated as proof of zero received.

### Draft 6 — INSERT-G complete excess

**To:** Inez Cole <inez.cole@northquayassembly.example>  
**Subject:** Reconcile 5-unit July excess for PO-S2607-826 / INSERT-G

Complete July evidence shows 75 net INSERT-G units against 70 ordered after counting the exact duplicate `RCV-K7114` once and excluding June activity. Please reconcile the 5-unit surplus against the purchase order and receiving evidence and confirm the correct disposition.

### Draft 7 — WRAP-500 complete shortfall

**To:** Felix Arun <felix.arun@wrapline.example>  
**Subject:** PO-S2607-827 / WRAP-500 — July receipt shortfall of 22

The complete July receiving evidence shows 18 net WRAP-500 units against 40 ordered, including the supplied 8-unit return/correction. Please confirm the status and expected receipt timing for the remaining 22 units, or provide the source document if the order quantity or disposition has changed.

### Draft 8 — PAD-FOAM complete shortfall after correction

**To:** Rafael Brooks <rafael.brooks@cushionstock.example>  
**Subject:** PO-S2607-829 / PAD-FOAM — resolve July net shortfall of 16

The complete July evidence shows 5 received and a 9-unit return/correction, for a July net of −4 against 12 ordered; the separate June receipt was excluded. Please confirm how the resulting 16-unit gap will be resolved and whether any replacement receipt or corrected source document is pending.

### Draft 9 — CRATE-S complete shortfall

**To:** Elena Duarte <elena.duarte@crateforge.example>  
**Subject:** PO-S2607-830 / CRATE-S — July receipt shortfall of 16

Complete July coverage contains no qualifying receipt event for PO-S2607-830 / CRATE-S, leaving 0 net against 16 ordered. Please confirm the status and expected receipt timing for the remaining 16 units, or provide the source document if the order quantity or disposition has changed.

### Draft 10 — SKU identity reconciliation

**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** Reconcile unexpected SKUs on PO-S2607-820 and PO-S2607-826

Please reconcile two receipt identities against the authoritative purchase orders and receiving source: July event `RCV-K7105` records 12 units of NUT-M8 on PO-S2607-820, and June event `RCV-K6991` records 7 units of INSERT-OLD on PO-S2607-826. Neither SKU appears in the supplied order lines, so neither quantity has been applied to an ordered-line receipt judgment. Please confirm the correct order/SKU mapping and provide any corrected export records.
