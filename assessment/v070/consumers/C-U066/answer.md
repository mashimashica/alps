# July 2026 receiving review

**Scope:** all 13 supplied purchase-order lines for `2026-07`. This is a draft review for Rowan Ames; no messages were sent and no receiving records were changed.

Signed quantities are added algebraically. A line has a final receipt judgment only when its July coverage is complete and no source blocker affects it. Otherwise, the quantity shown is an **observed subtotal**, not a final net receipt.

| Order / SKU | Ordered | July evidence | Coverage / source position | Supported judgment |
|---|---:|---|---|---|
| `PO-S2607-820` / `BOLT-M8` | 100 | Observed subtotal **90**: `RCV-K7101` +70, `RCV-K7102` +30, `RCV-K7103` -10 | Coverage row 0 says complete, but `RCV-K7105` (events row 4) records +12 against unknown SKU `NUT-M8` on this in-scope order. That unknown SKU blocks every line on the order. | **Unresolved evidence.** Do not treat 90 as a final net or infer a 10-unit shortfall yet. Rowan and Beck must reconcile the unknown-SKU record. |
| `PO-S2607-820` / `WASHER-M8` | 200 | Observed subtotal **200**: `RCV-K7104` +200 | Coverage row 1 says complete, but the same unknown-SKU event `RCV-K7105` blocks the order. | **Unresolved evidence.** Do not treat 200 as received as ordered until the unknown-SKU record is reconciled. |
| `PO-S2607-821` / `PACK-RACK` | 48 | Observed subtotal **20**: `RCV-K7106` +20 | Coverage row 2 says complete. Event ID `RCV-K7107` conflicts between events rows 6 and 8: +18 for this line versus +12 for `PO-S2607-822 / SHIELD-CLR`. The conflicting ID contributes nothing pending correction. | **Unresolved evidence.** The apparent subtotal cannot establish a shortfall. Rowan and Beck must resolve which record, if either, is valid. |
| `PO-S2607-821` / `STRAP-20` | 60 | Final net **60**: `RCV-K7109` +60 | Complete, unblocked July coverage row 3 | **Received as ordered.** No receiving follow-up. |
| `PO-S2607-822` / `SHIELD-CLR` | 40 | Observed subtotal **28**: `RCV-K7108` +28 | Coverage row 4 says complete, but the conflicting `RCV-K7107` at events rows 6 and 8 could affect this line. | **Unresolved evidence.** The apparent subtotal cannot establish a shortfall. Rowan and Beck must resolve the conflicting ID. |
| `PO-S2607-823` / `POUCH-12` | 30 | Observed subtotal **34**: exact duplicate `RCV-K7110` counted once at +36, plus `RCV-K7111` -2 | Coverage row 5 is explicitly false | **Unresolved evidence.** The 34-unit subtotal does not support a final excess judgment until Beck supplies or confirms complete July evidence. |
| `PO-S2607-824` / `TRAY-L` | 18 | Observed subtotal **9**: `RCV-K7112` +12, `RCV-K7113` -3 | No July coverage declaration. Coverage row 6 is for June and does not establish July completeness. | **Unresolved evidence.** The 9-unit subtotal does not support a final shortfall judgment. Beck must provide or confirm the complete July export and declaration. |
| `PO-S2607-825` / `BINDER-B` | 25 | Observed subtotal **0** from no supplied July events | Coverage row 7 is explicitly false | **Unresolved evidence.** Zero is only the known subtotal, not a final net and not evidence of a 25-unit shortfall. Beck must provide or confirm the complete July export and declaration. |
| `PO-S2607-826` / `INSERT-G` | 70 | Final net **75**: exact duplicate `RCV-K7114` counted once at +45, `RCV-K7115` +40, `RCV-K7116` -10 | Complete, unblocked July coverage row 8 | **Excess of 5.** Inez should reconcile the surplus against the order and receiving evidence and report the required correction to Rowan. |
| `PO-S2607-827` / `WRAP-500` | 40 | Final net **18**: `RCV-K7117` +20, `RCV-K7118` +6, `RCV-K7119` -8 | Complete, unblocked July coverage row 9 | **Shortfall of 22.** Rowan should have Felix confirm the remaining receipt and next receiving date or action. |
| `PO-S2607-828` / `CLIP-R` | 10 | Final net **10**: `RCV-K7120` +6, `RCV-K7121` +4 | Complete, unblocked July coverage row 10 | **Received as ordered.** No receiving follow-up. |
| `PO-S2607-829` / `PAD-FOAM` | 12 | Final net **-4**: `RCV-K7122` +5, `RCV-K7123` -9 | Complete, unblocked July coverage row 11 | **Shortfall of 16.** The signed correction makes the July net negative; Rowan should have Rafael confirm the remaining receipt and next receiving date or action. |
| `PO-S2607-830` / `CRATE-S` | 16 | Final net **0** from a complete empty July event set | Complete, unblocked July coverage row 12 | **Shortfall of 16.** Rowan should have Elena confirm the remaining receipt and next receiving date or action. |

## Recipient-specific follow-up drafts

### Source reconciliation — Rowan Ames and Beck Lin

**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** July 2026 source reconciliation — PO-S2607-820 / BOLT-M8  
`2026-07 / PO-S2607-820 / BOLT-M8` — Ordered quantity is 100 and the usable signed events total 90 (`RCV-K7101`, `RCV-K7102`, `RCV-K7103`). Event `RCV-K7105` at events row 4 records +12 for unknown SKU `NUT-M8` on the same in-scope order, so the 90-unit subtotal is not a final receipt position. Please determine the correct SKU for `RCV-K7105` or document why it is outside this order, correct or confirm the source record, and return the reconciled July evidence so Rowan can rerun the comparison.

**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** July 2026 source reconciliation — PO-S2607-820 / WASHER-M8  
`2026-07 / PO-S2607-820 / WASHER-M8` — Ordered quantity is 200 and the usable event `RCV-K7104` gives an observed subtotal of 200. Event `RCV-K7105` at events row 4 records +12 for unknown SKU `NUT-M8` on the same in-scope order, so 200 cannot yet be accepted as the final net. Please determine the correct SKU for `RCV-K7105` or document why it is outside this order, correct or confirm the source record, and return the reconciled July evidence so Rowan can finalize this line.

**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** July 2026 conflicting receipt ID — PO-S2607-821 / PACK-RACK  
`2026-07 / PO-S2607-821 / PACK-RACK` — Ordered quantity is 48 and the unconflicted observed subtotal is 20 from `RCV-K7106`. Event ID `RCV-K7107` conflicts between events row 6 (+18 for this line) and events row 8 (+12 for `PO-S2607-822 / SHIELD-CLR`), so neither conflicting quantity was counted. Please establish which record, if either, is valid, correct the duplicate ID or source data, confirm the complete July evidence, and return it for a final comparison.

**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** July 2026 conflicting receipt ID — PO-S2607-822 / SHIELD-CLR  
`2026-07 / PO-S2607-822 / SHIELD-CLR` — Ordered quantity is 40 and the unconflicted observed subtotal is 28 from `RCV-K7108`. Event ID `RCV-K7107` conflicts between events row 8 (+12 for this line) and events row 6 (+18 for `PO-S2607-821 / PACK-RACK`), so neither conflicting quantity was counted. Please establish which record, if either, is valid, correct the duplicate ID or source data, confirm the complete July evidence, and return it for a final comparison.

### Coverage completion — Beck Lin

**To:** Beck Lin <beck.lin@northquayassembly.example>  
**Owner:** Rowan Ames <rowan.ames@northquayassembly.example>  
**Subject:** Complete July evidence — PO-S2607-823 / POUCH-12  
`2026-07 / PO-S2607-823 / POUCH-12` — Ordered quantity is 30. The known signed events total 34 after exact duplicate `RCV-K7110` is counted once (+36) and `RCV-K7111` is applied (-2), but coverage row 5 is false. Please provide or confirm the full July event export and a complete coverage declaration. Rowan will then determine whether an excess exists and direct any receiving action.

**To:** Beck Lin <beck.lin@northquayassembly.example>  
**Owner:** Rowan Ames <rowan.ames@northquayassembly.example>  
**Subject:** Complete July evidence — PO-S2607-824 / TRAY-L  
`2026-07 / PO-S2607-824 / TRAY-L` — Ordered quantity is 18 and the known signed July events total 9 (`RCV-K7112` +12 and `RCV-K7113` -3). The only supplied coverage declaration is for June, so July completeness is unconfirmed. Please provide or confirm the full July event export and July completeness declaration, then return the evidence for final comparison.

**To:** Beck Lin <beck.lin@northquayassembly.example>  
**Owner:** Rowan Ames <rowan.ames@northquayassembly.example>  
**Subject:** Complete July evidence — PO-S2607-825 / BINDER-B  
`2026-07 / PO-S2607-825 / BINDER-B` — Ordered quantity is 25. No July events were supplied, and coverage row 7 is false; the observed zero therefore is not a final receipt position. Please provide or confirm the full July event export and a complete coverage declaration, including confirmation if the complete export is empty, then return the evidence for final comparison.

### Warehouse reconciliation — Inez Cole

**To:** Inez Cole <inez.cole@northquayassembly.example>  
**Owner:** Rowan Ames <rowan.ames@northquayassembly.example>  
**Subject:** Reconcile July excess — PO-S2607-826 / INSERT-G  
`2026-07 / PO-S2607-826 / INSERT-G` — Ordered quantity is 70 and the complete signed July net is 75 (`RCV-K7114` +45 counted once despite its exact duplicate, `RCV-K7115` +40, and `RCV-K7116` -10), leaving an excess of 5. Please reconcile the five-unit surplus against the order and receiving evidence and report the required correction to Rowan.

### Supplier follow-up — Rowan Ames with supplier contacts

**To:** Felix Arun <felix.arun@wrapline.example>  
**Cc:** Rowan Ames <rowan.ames@northquayassembly.example>  
**Subject:** July receipt shortfall — PO-S2607-827 / WRAP-500  
`2026-07 / PO-S2607-827 / WRAP-500` — The order is for 40 units and the complete signed July net is 18, leaving 22 units outstanding. Please confirm the remaining 22-unit receipt and provide the next receiving date or other concrete fulfillment action to Rowan.

**To:** Rafael Brooks <rafael.brooks@cushionstock.example>  
**Cc:** Rowan Ames <rowan.ames@northquayassembly.example>  
**Subject:** July receipt shortfall — PO-S2607-829 / PAD-FOAM  
`2026-07 / PO-S2607-829 / PAD-FOAM` — The order is for 12 units and the complete signed July net is -4 (`RCV-K7122` +5 and correcting event `RCV-K7123` -9), leaving 16 units outstanding. Please confirm the remaining 16-unit receipt and provide the next receiving date or other concrete fulfillment action to Rowan.

**To:** Elena Duarte <elena.duarte@crateforge.example>  
**Cc:** Rowan Ames <rowan.ames@northquayassembly.example>  
**Subject:** July receipt shortfall — PO-S2607-830 / CRATE-S  
`2026-07 / PO-S2607-830 / CRATE-S` — The order is for 16 units and the complete July export contains no receipt events, giving a final net of 0 and leaving 16 units outstanding. Please confirm the remaining 16-unit receipt and provide the next receiving date or other concrete fulfillment action to Rowan.

## Outside-scope diagnostics

These records did not change any in-scope total:

- Events row 19, `RCV-K6990`, is for June 2026.
- Events row 20, `RCV-K6991`, is for June 2026.
- Events row 26, `RCV-K6992`, is for June 2026.
- Events row 29, `RCV-K7124`, is for order `PO-S2607-899`, which is outside the supplied order set.

Event and coverage row references above are zero-based, matching the processor report.
