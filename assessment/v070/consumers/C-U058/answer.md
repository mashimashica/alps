# July 2026 receiving review

The July evidence supports final receipt judgments for 6 of the 13 supplied purchase-order lines. Two were received as ordered, three have confirmed shortfalls, and one has a confirmed excess. The other seven lines are indeterminate: their July event subtotals remain useful, but they are not final receipt positions until the identified evidence issues are resolved. Eleven lines require follow-up in total.

| Purchase order / SKU | Ordered | July net | Judgment | Rowan's next step |
|---|---:|---:|---|---|
| PO-S2607-820 / BOLT-M8 | 100 | 90 observed | **Indeterminate** | Rowan Ames and Beck Lin reconcile July event `RCV-K7105`, which uses unknown SKU `NUT-M8` on this order. This order-level identity issue blocks the final comparison. |
| PO-S2607-820 / WASHER-M8 | 200 | 200 observed | **Indeterminate** | Same `RCV-K7105` order identity reconciliation. The observed 200 cannot yet be treated as received as ordered. |
| PO-S2607-821 / PACK-RACK | 48 | 20 observed | **Indeterminate** | Rowan Ames and Beck Lin reconcile conflicting event ID `RCV-K7107`. |
| PO-S2607-821 / STRAP-20 | 60 | 60 confirmed | **Received as ordered** (variance 0) | No follow-up. |
| PO-S2607-822 / SHIELD-CLR | 40 | 28 observed | **Indeterminate** | Rowan Ames and Beck Lin reconcile conflicting event ID `RCV-K7107`. |
| PO-S2607-823 / POUCH-12 | 30 | 34 observed | **Indeterminate** | Beck Lin provides or confirms the complete July export, then reruns the comparison. |
| PO-S2607-824 / TRAY-L | 18 | 9 observed | **Indeterminate** | Beck Lin provides or confirms July coverage and the complete July export, then reruns the comparison. The supplied coverage declaration is for June, not July. |
| PO-S2607-825 / BINDER-B | 25 | 0 observed | **Indeterminate** | Beck Lin provides or confirms the complete July export, then reruns the comparison. Zero is only the observed subtotal from incomplete evidence. |
| PO-S2607-826 / INSERT-G | 70 | 75 confirmed | **Excess by 5** | Inez Cole reconciles the five-unit surplus against the order and receiving evidence. |
| PO-S2607-827 / WRAP-500 | 40 | 18 confirmed | **Shortfall of 22** | Rowan Ames asks Felix Arun for the plan for the remaining 22 units. |
| PO-S2607-828 / CLIP-R | 10 | 10 confirmed | **Received as ordered** (variance 0) | No follow-up. |
| PO-S2607-829 / PAD-FOAM | 12 | -4 confirmed | **Shortfall of 16** | Rowan Ames asks Rafael Brooks for the plan to resolve the 16-unit July shortfall. |
| PO-S2607-830 / CRATE-S | 16 | 0 confirmed | **Shortfall of 16** | Rowan Ames asks Elena Duarte for the plan for the remaining 16 units. |

The calculations use July events only and include negative returns or reversals algebraically. Exact duplicates `RCV-K7110` and `RCV-K7114` were counted once. The differing records that share `RCV-K7107` were treated as conflicting evidence, so they block the affected PACK-RACK and SHIELD-CLR comparisons. June events were excluded, including the June receipt of 9 PAD-FOAM units; the July PAD-FOAM events are +5 and -9, producing the confirmed July net of -4. Event `RCV-K7124` belongs to outside-scope order `PO-S2607-899` and did not affect any supplied line. The processor reported no review-level scope issues.

## Draft follow-ups

These are drafts only; none has been sent.

**To:** Rowan Ames `<rowan.ames@northquayassembly.example>`; Beck Lin `<beck.lin@northquayassembly.example>`  
**Subject:** Reconcile PO-S2607-820 July event identity

Please reconcile July event `RCV-K7105`, which is recorded against PO-S2607-820 with SKU `NUT-M8`, a SKU not present among the supplied lines for that order. Please confirm the correct order/SKU or the required source-record correction, then rerun the July comparison. Until this is resolved, the final positions for BOLT-M8 and WASHER-M8 are blocked; their observed July subtotals are 90 and 200 respectively.

---

**To:** Rowan Ames `<rowan.ames@northquayassembly.example>`; Beck Lin `<beck.lin@northquayassembly.example>`  
**Subject:** Reconcile conflicting July event RCV-K7107

Please reconcile the two different July records sharing event ID `RCV-K7107`: one records 18 units for PO-S2607-821/PACK-RACK and the other records 12 units for PO-S2607-822/SHIELD-CLR. Please confirm the valid source record or required correction, then rerun both comparisons. Until then, the observed subtotals of 20 for PACK-RACK and 28 for SHIELD-CLR are not final receipt positions.

---

**To:** Beck Lin `<beck.lin@northquayassembly.example>`  
**Subject:** Complete July export for PO-S2607-823/POUCH-12

Please provide or confirm the complete receiving-event export for PO-S2607-823/POUCH-12 for July 2026, then rerun the comparison. The exact duplicate `RCV-K7110` was counted once, giving an observed subtotal of 34 after the two-unit return, but the supplied coverage is incomplete and no final receipt position can yet be determined.

---

**To:** Beck Lin `<beck.lin@northquayassembly.example>`  
**Subject:** Confirm July coverage for PO-S2607-824/TRAY-L

Please provide or confirm the complete receiving-event export and coverage declaration for PO-S2607-824/TRAY-L for July 2026, then rerun the comparison. The supplied coverage declaration is for June. July events currently produce an observed subtotal of 9, but no final receipt position can yet be determined.

---

**To:** Beck Lin `<beck.lin@northquayassembly.example>`  
**Subject:** Complete July export for PO-S2607-825/BINDER-B

Please provide or confirm the complete receiving-event export for PO-S2607-825/BINDER-B for July 2026, then rerun the comparison. The observed subtotal is 0, but the supplied coverage is incomplete, so zero must not be treated as the final receipt position.

---

**To:** Inez Cole `<inez.cole@northquayassembly.example>`  
**Subject:** Reconcile five-unit surplus for PO-S2607-826/INSERT-G

Please reconcile the five-unit July surplus for PO-S2607-826/INSERT-G against the purchase order and receiving evidence. Ordered quantity is 70 and confirmed July net received is 75. The exact duplicate `RCV-K7114` was counted once, and the June event was excluded.

---

**Owner:** Rowan Ames `<rowan.ames@northquayassembly.example>`  
**To:** Felix Arun `<felix.arun@wrapline.example>`  
**Subject:** Remaining 22 units for PO-S2607-827/WRAP-500

Please confirm the plan for the remaining 22 units of PO-S2607-827/WRAP-500 for July 2026. The order quantity is 40 and confirmed July net received is 18 after the recorded return.

---

**Owner:** Rowan Ames `<rowan.ames@northquayassembly.example>`  
**To:** Rafael Brooks `<rafael.brooks@cushionstock.example>`  
**Subject:** Resolve July shortfall for PO-S2607-829/PAD-FOAM

Please confirm the delivery or credit plan to resolve the 16-unit July shortfall for PO-S2607-829/PAD-FOAM. The order quantity is 12; the July events are +5 and -9, giving confirmed July net received of -4. The separate nine-unit receipt is dated June and is outside this review month.

---

**Owner:** Rowan Ames `<rowan.ames@northquayassembly.example>`  
**To:** Elena Duarte `<elena.duarte@crateforge.example>`  
**Subject:** Remaining 16 units for PO-S2607-830/CRATE-S

Please confirm the plan for the remaining 16 units of PO-S2607-830/CRATE-S for July 2026. The order quantity is 16 and confirmed July net received is 0.

