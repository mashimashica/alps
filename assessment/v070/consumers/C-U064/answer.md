# July 2026 receiving review

The review covers **2026-07** and all **13 supplied purchase-order lines**. Six lines have final receipt positions; **seven remain unresolved** because their evidence does not support a final comparison. Eleven lines require follow-up, including the four lines with final shortfall or excess positions.

For unresolved lines, the observed subtotal below is only the sum of valid, unique, matching July events currently visible. It is **not** the final July net receipt.

| Order | SKU | Ordered | Observed subtotal | Final July net | Position | Evidence status | Evidence gaps |
|---|---|---:|---:|---:|---|---|---|
| PO-S2607-820 | BOLT-M8 | 100 | 90 | — | Undetermined | Identity reconciliation | July event RCV-K7105 uses SKU `NUT-M8`, which is absent from supplied order PO-S2607-820. This blocks final comparison for the order's lines. |
| PO-S2607-820 | WASHER-M8 | 200 | 200 | — | Undetermined | Identity reconciliation | July event RCV-K7105 uses SKU `NUT-M8`, which is absent from supplied order PO-S2607-820. This blocks final comparison for the order's lines. |
| PO-S2607-821 | PACK-RACK | 48 | 20 | — | Undetermined | Conflicting evidence | Event ID RCV-K7107 has conflicting content and was not counted. |
| PO-S2607-821 | STRAP-20 | 60 | 60 | 60 | Received as ordered | Complete | None. |
| PO-S2607-822 | SHIELD-CLR | 40 | 28 | — | Undetermined | Conflicting evidence | Event ID RCV-K7107 has conflicting content and was not counted. |
| PO-S2607-823 | POUCH-12 | 30 | 34 | — | Undetermined | Incomplete export | July event export is declared incomplete. The exact duplicate RCV-K7110 was counted once. |
| PO-S2607-824 | TRAY-L | 18 | 9 | — | Undetermined | Incomplete export | No July coverage declaration is supplied; the supplied declaration is for June. |
| PO-S2607-825 | BINDER-B | 25 | 0 | — | Undetermined | Incomplete export | July event export is declared incomplete; zero is only the observed subtotal, not a final receipt total. |
| PO-S2607-826 | INSERT-G | 70 | 75 | 75 | Excess by 5 | Complete | None. The exact duplicate RCV-K7114 was counted once. |
| PO-S2607-827 | WRAP-500 | 40 | 18 | 18 | Shortfall of 22 | Complete | None. |
| PO-S2607-828 | CLIP-R | 10 | 10 | 10 | Received as ordered | Complete | None. |
| PO-S2607-829 | PAD-FOAM | 12 | -4 | -4 | Shortfall of 16 | Complete | None; the July return/correction makes the signed July net negative. |
| PO-S2607-830 | CRATE-S | 16 | 0 | 0 | Shortfall of 16 | Complete | None. |

## Required follow-up drafts

1. **PO-S2607-820 / BOLT-M8 — source-record reconciliation**  
   **Owners/recipients:** Rowan Ames <rowan.ames@northquayassembly.example>, purchasing coordinator; Beck Lin <beck.lin@northquayassembly.example>, data steward.  
   **Next action:** Reconcile RCV-K7105's `NUT-M8` SKU against the supplied PO-S2607-820 lines, then rerun the July comparison.  
   **Draft:** “Rowan and Beck — PO-S2607-820 / BOLT-M8 cannot be finalized for July. Event RCV-K7105 is recorded against PO-S2607-820 with SKU NUT-M8, which is not among the supplied order lines. Please reconcile the order and event source records, confirm the correct line assignment, and rerun the July comparison. The current BOLT-M8 subtotal is 90 units and is non-final.”

2. **PO-S2607-820 / WASHER-M8 — source-record reconciliation**  
   **Owners/recipients:** Rowan Ames <rowan.ames@northquayassembly.example>, purchasing coordinator; Beck Lin <beck.lin@northquayassembly.example>, data steward.  
   **Next action:** Reconcile RCV-K7105's `NUT-M8` SKU against the supplied PO-S2607-820 lines, then rerun the July comparison.  
   **Draft:** “Rowan and Beck — PO-S2607-820 / WASHER-M8 cannot be finalized for July. Event RCV-K7105 is recorded against PO-S2607-820 with SKU NUT-M8, which is not among the supplied order lines. Please reconcile the order and event source records, confirm the correct line assignment, and rerun the July comparison. The current WASHER-M8 subtotal is 200 units and is non-final.”

3. **PO-S2607-821 / PACK-RACK — conflicting event reconciliation**  
   **Owners/recipients:** Rowan Ames <rowan.ames@northquayassembly.example>, purchasing coordinator; Beck Lin <beck.lin@northquayassembly.example>, data steward.  
   **Next action:** Reconcile the conflicting variants of RCV-K7107 and rerun the line comparison.  
   **Draft:** “Rowan and Beck — PO-S2607-821 / PACK-RACK cannot be finalized for July because event ID RCV-K7107 also appears with different order, SKU, and quantity content. It was excluded from the subtotal. Please identify the valid source record, correct or confirm it, and rerun the comparison. The current PACK-RACK subtotal is 20 units and is non-final.”

4. **PO-S2607-822 / SHIELD-CLR — conflicting event reconciliation**  
   **Owners/recipients:** Rowan Ames <rowan.ames@northquayassembly.example>, purchasing coordinator; Beck Lin <beck.lin@northquayassembly.example>, data steward.  
   **Next action:** Reconcile the conflicting variants of RCV-K7107 and rerun the line comparison.  
   **Draft:** “Rowan and Beck — PO-S2607-822 / SHIELD-CLR cannot be finalized for July because event ID RCV-K7107 also appears with different order, SKU, and quantity content. It was excluded from the subtotal. Please identify the valid source record, correct or confirm it, and rerun the comparison. The current SHIELD-CLR subtotal is 28 units and is non-final.”

5. **PO-S2607-823 / POUCH-12 — complete or confirm export**  
   **Owner/recipient:** Beck Lin <beck.lin@northquayassembly.example>, data steward.  
   **Next action:** Supply, correct, or confirm the complete July event export, then rerun the final comparison.  
   **Draft:** “Beck — PO-S2607-823 / POUCH-12 cannot be finalized because its July event export is declared incomplete. Please provide, correct, or confirm the complete July export and rerun the comparison. The current signed subtotal is 34 units and is non-final.”

6. **PO-S2607-824 / TRAY-L — obtain July coverage evidence**  
   **Owner/recipient:** Beck Lin <beck.lin@northquayassembly.example>, data steward.  
   **Next action:** Supply or confirm July coverage and the complete July event export, then rerun the final comparison.  
   **Draft:** “Beck — PO-S2607-824 / TRAY-L cannot be finalized because no July coverage declaration was supplied; the available declaration is for June. Please supply or confirm the complete July export and July coverage, then rerun the comparison. The current signed subtotal is 9 units and is non-final.”

7. **PO-S2607-825 / BINDER-B — complete or confirm export**  
   **Owner/recipient:** Beck Lin <beck.lin@northquayassembly.example>, data steward.  
   **Next action:** Supply, correct, or confirm the complete July event export, then rerun the final comparison.  
   **Draft:** “Beck — PO-S2607-825 / BINDER-B cannot be finalized because its July event export is declared incomplete. Please provide, correct, or confirm the complete July export and rerun the comparison. No valid July events are currently visible, so the observed subtotal of zero is non-final.”

8. **PO-S2607-826 / INSERT-G — reconcile 5-unit excess**  
   **Owner/recipient:** Inez Cole <inez.cole@northquayassembly.example>, warehouse lead.  
   **Next action:** Reconcile the five-unit surplus against the order and receiving evidence.  
   **Draft:** “Inez — PO-S2607-826 / INSERT-G has a final July net receipt of 75 units against 70 ordered, an excess of five. Please reconcile the surplus against the purchase order and receiving evidence and document the disposition.”

9. **PO-S2607-827 / WRAP-500 — confirm remaining 22 units**  
   **Owner:** Rowan Ames <rowan.ames@northquayassembly.example>, purchasing coordinator.  
   **Supplier recipient:** Felix Arun <felix.arun@wrapline.example>.  
   **Next action:** Rowan contacts Felix to confirm the receipt plan and timing for the remaining 22 units.  
   **Draft to Felix:** “Felix — for PO-S2607-827 / WRAP-500, our final July net receipt is 18 units against 40 ordered, leaving 22 units outstanding. Please confirm the plan and expected timing for the remaining 22 units.”

10. **PO-S2607-829 / PAD-FOAM — confirm remaining 16 units**  
    **Owner:** Rowan Ames <rowan.ames@northquayassembly.example>, purchasing coordinator.  
    **Supplier recipient:** Rafael Brooks <rafael.brooks@cushionstock.example>.  
    **Next action:** Rowan contacts Rafael to confirm the receipt plan and timing for the remaining 16 units.  
    **Draft to Rafael:** “Rafael — for PO-S2607-829 / PAD-FOAM, July activity produced a final signed net receipt of -4 units against 12 ordered, leaving a 16-unit shortfall for July. Please confirm the plan and expected timing for the remaining 16 units.”

11. **PO-S2607-830 / CRATE-S — confirm remaining 16 units**  
    **Owner:** Rowan Ames <rowan.ames@northquayassembly.example>, purchasing coordinator.  
    **Supplier recipient:** Elena Duarte <elena.duarte@crateforge.example>.  
    **Next action:** Rowan contacts Elena to confirm the receipt plan and timing for the remaining 16 units.  
    **Draft to Elena:** “Elena — for PO-S2607-830 / CRATE-S, our final July net receipt is zero units against 16 ordered, leaving 16 units outstanding. Please confirm the plan and expected timing for the remaining 16 units.”

## Events kept separate from the line judgments

- **Outside scope:** RCV-K7124 belongs to PO-S2607-899, which is outside the supplied order set, so it did not affect any in-scope total.
- **Other month, ignored for July:** RCV-K6990, RCV-K6991, and RCV-K6992 are June events and did not contribute to July subtotals.
- **Unassigned issues:** None.
- **Deduplication:** Two exact duplicate event records were ignored; each event was counted once.

This is a receiving review with draft follow-ups only. No message was sent, no one was contacted, and no order or receiving record was changed.
