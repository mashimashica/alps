# July 2026 receiving review

**Review month:** 2026-07  
**Coordinator:** Rowan Ames `<rowan.ames@northquayassembly.example>`  
**Scope:** 13 supplied purchase-order lines

The evidence supports final receipt positions for six lines: two received as ordered, one excess, and three shortfalls. The other seven lines have supported **observed subtotals only** because identity, event-conflict, or coverage issues prevent a final comparison. Eleven lines need follow-up in total. All follow-ups below are drafts only; no message was sent and no receiving record was changed.

## Line-by-line review

| Order / SKU | Ordered | Observed received | Final received | Evidence and coverage | Supported judgment |
|---|---:|---:|---:|---|---|
| PO-S2607-820 / BOLT-M8 | 100 | 90 | — | `RCV-K7101` +70, `RCV-K7102` +30, `RCV-K7103` −10; July coverage complete | **Identity reconciliation required.** The same order has July event `RCV-K7105` for absent SKU `NUT-M8`, so the order's final comparisons are held. The observed 90 is not a final shortfall. |
| PO-S2607-820 / WASHER-M8 | 200 | 200 | — | `RCV-K7104` +200; July coverage complete | **Identity reconciliation required.** The same `RCV-K7105` / `NUT-M8` mismatch holds this order's final comparisons. The observed 200 is not a final received-as-ordered judgment. |
| PO-S2607-821 / PACK-RACK | 48 | 20 | — | `RCV-K7106` +20; July coverage complete; conflicting `RCV-K7107` excluded | **Conflicting evidence.** `RCV-K7107` appears once as 18 PACK-RACK units and once as 12 SHIELD-CLR units on PO-S2607-822. No final position is supported. |
| PO-S2607-821 / STRAP-20 | 60 | 60 | 60 | `RCV-K7109` +60; July coverage complete | **Received as ordered.** No follow-up needed. |
| PO-S2607-822 / SHIELD-CLR | 40 | 28 | — | `RCV-K7108` +28; July coverage complete; conflicting `RCV-K7107` excluded | **Conflicting evidence.** The inconsistent reuse of `RCV-K7107` prevents a final comparison. |
| PO-S2607-823 / POUCH-12 | 30 | 34 | — | `RCV-K7110` +36 counted once despite its exact duplicate, plus `RCV-K7111` −2; July coverage explicitly incomplete | **Incomplete export.** Only an observed subtotal is supported; it must not be called an excess. |
| PO-S2607-824 / TRAY-L | 18 | 9 | — | `RCV-K7112` +12, `RCV-K7113` −3; no July coverage declaration (the supplied declaration is for June) | **Coverage missing.** Only an observed subtotal is supported; it must not be called a shortfall. |
| PO-S2607-825 / BINDER-B | 25 | 0 | — | No July events; July coverage explicitly incomplete | **Incomplete export.** Zero is only the observed subtotal, not a final non-receipt or shortfall. |
| PO-S2607-826 / INSERT-G | 70 | 75 | 75 | `RCV-K7114` +45 counted once despite its exact duplicate, `RCV-K7115` +40, `RCV-K7116` −10; July coverage complete | **Excess: 5 units.** |
| PO-S2607-827 / WRAP-500 | 40 | 18 | 18 | `RCV-K7117` +20, `RCV-K7118` +6, `RCV-K7119` −8; July coverage complete | **Shortfall: 22 units remaining.** |
| PO-S2607-828 / CLIP-R | 10 | 10 | 10 | `RCV-K7120` +6, `RCV-K7121` +4; July coverage complete | **Received as ordered.** No follow-up needed. |
| PO-S2607-829 / PAD-FOAM | 12 | −4 | −4 | `RCV-K7122` +5, `RCV-K7123` −9; July coverage complete | **Shortfall: 16 units remaining.** The supported July net is negative because the July reversal exceeds the July receipt. |
| PO-S2607-830 / CRATE-S | 16 | 0 | 0 | No July events; July coverage complete | **Shortfall: 16 units remaining.** Here zero is final because the July coverage is complete. |

## Review-wide evidence notes

- `RCV-K7105` is a July event for in-scope PO-S2607-820 but names SKU `NUT-M8`, which is absent from that order's supplied lines. It therefore holds the final comparison for both supplied PO-S2607-820 lines.
- `RCV-K7107` has conflicting content across PO-S2607-821 / PACK-RACK and PO-S2607-822 / SHIELD-CLR. Both variants were excluded from arithmetic, and both referenced lines remain unresolved.
- Exact duplicates of `RCV-K7110` and `RCV-K7114` were each counted once.
- Prior-month events `RCV-K6990`, `RCV-K6991`, and `RCV-K6992` do not contribute to July quantities. The June coverage entry for PO-S2607-824 / TRAY-L does not establish July completeness.
- `RCV-K7124` for PO-S2607-899 / WRAP-500 is outside the supplied order scope and was ignored.

## Follow-up drafts

### 1. PO-S2607-820 / BOLT-M8 — identity reconciliation

**To:** Rowan Ames `<rowan.ames@northquayassembly.example>`; Beck Lin `<beck.lin@northquayassembly.example>`  
**Subject:** Draft — reconcile PO-S2607-820 identity before July close

Please reconcile July event `RCV-K7105`, which names PO-S2607-820 and SKU `NUT-M8`, against the supplied order lines. For BOLT-M8, the current trace (`RCV-K7101`, `RCV-K7102`, `RCV-K7103`) supports an observed subtotal of 90 against 100 ordered, but no final receipt position should be recorded until the SKU identity issue is resolved.

### 2. PO-S2607-820 / WASHER-M8 — identity reconciliation

**To:** Rowan Ames `<rowan.ames@northquayassembly.example>`; Beck Lin `<beck.lin@northquayassembly.example>`  
**Subject:** Draft — reconcile PO-S2607-820 identity before July close

Please reconcile July event `RCV-K7105`, which names PO-S2607-820 and SKU `NUT-M8`, against the supplied order lines. For WASHER-M8, `RCV-K7104` supports an observed subtotal of 200 against 200 ordered, but no final receipt position should be recorded until the order/SKU identity issue is resolved.

### 3. PO-S2607-821 / PACK-RACK — conflicting event

**To:** Rowan Ames `<rowan.ames@northquayassembly.example>`; Beck Lin `<beck.lin@northquayassembly.example>`  
**Subject:** Draft — resolve conflicting event RCV-K7107

Please determine the correct source record for `RCV-K7107`, which appears both as 18 PACK-RACK units on PO-S2607-821 and 12 SHIELD-CLR units on PO-S2607-822. The conflicting event was excluded; PACK-RACK currently has an observed subtotal of 20 from `RCV-K7106` against 48 ordered, with no supported final position.

### 4. PO-S2607-822 / SHIELD-CLR — conflicting event

**To:** Rowan Ames `<rowan.ames@northquayassembly.example>`; Beck Lin `<beck.lin@northquayassembly.example>`  
**Subject:** Draft — resolve conflicting event RCV-K7107

Please determine the correct source record for `RCV-K7107`, which appears both as 18 PACK-RACK units on PO-S2607-821 and 12 SHIELD-CLR units on PO-S2607-822. The conflicting event was excluded; SHIELD-CLR currently has an observed subtotal of 28 from `RCV-K7108` against 40 ordered, with no supported final position.

### 5. PO-S2607-823 / POUCH-12 — incomplete July export

**To:** Beck Lin `<beck.lin@northquayassembly.example>`  
**Subject:** Draft — complete July receiving evidence for PO-S2607-823 / POUCH-12

Please provide or confirm the full July receiving export and update the coverage evidence for PO-S2607-823 / POUCH-12. The current incomplete export supports only an observed subtotal of 34 from `RCV-K7110` (+36, exact duplicate counted once) and `RCV-K7111` (−2) against 30 ordered; it does not support a final excess judgment.

### 6. PO-S2607-824 / TRAY-L — July coverage missing

**To:** Beck Lin `<beck.lin@northquayassembly.example>`  
**Subject:** Draft — provide July coverage for PO-S2607-824 / TRAY-L

Please provide or confirm the full July receiving export and a July coverage declaration for PO-S2607-824 / TRAY-L. The supplied coverage declaration is for June. July events `RCV-K7112` (+12) and `RCV-K7113` (−3) support only an observed subtotal of 9 against 18 ordered, not a final shortfall.

### 7. PO-S2607-825 / BINDER-B — incomplete July export

**To:** Beck Lin `<beck.lin@northquayassembly.example>`  
**Subject:** Draft — complete July receiving evidence for PO-S2607-825 / BINDER-B

Please provide or confirm the full July receiving export and coverage evidence for PO-S2607-825 / BINDER-B. No July events are present and coverage is explicitly incomplete, so the observed subtotal of 0 against 25 ordered cannot be treated as a final shortfall.

### 8. PO-S2607-826 / INSERT-G — confirmed excess

**To:** Inez Cole `<inez.cole@northquayassembly.example>`  
**Subject:** Draft — reconcile 5-unit July excess for PO-S2607-826 / INSERT-G

Please reconcile the confirmed 5-unit excess for PO-S2607-826 / INSERT-G. Complete July evidence supports a final net receipt of 75 against 70 ordered: `RCV-K7114` +45 (exact duplicate counted once), `RCV-K7115` +40, and `RCV-K7116` −10.

### 9. PO-S2607-827 / WRAP-500 — confirmed shortfall

**To:** Felix Arun `<felix.arun@wrapline.example>`  
**Subject:** Draft — confirm 22 remaining units for PO-S2607-827 / WRAP-500

Please confirm and arrange receipt of the 22 remaining WRAP-500 units for PO-S2607-827. Complete July evidence supports a final net receipt of 18 against 40 ordered from `RCV-K7117` +20, `RCV-K7118` +6, and `RCV-K7119` −8.

### 10. PO-S2607-829 / PAD-FOAM — confirmed shortfall

**To:** Rafael Brooks `<rafael.brooks@cushionstock.example>`  
**Subject:** Draft — confirm 16 remaining units for PO-S2607-829 / PAD-FOAM

Please confirm and arrange receipt of the 16 remaining PAD-FOAM units for PO-S2607-829. Complete July evidence supports a final net receipt of −4 against 12 ordered from `RCV-K7122` +5 and `RCV-K7123` −9. The June receipt `RCV-K6992` is outside this review month and was not included.

### 11. PO-S2607-830 / CRATE-S — confirmed shortfall

**To:** Elena Duarte `<elena.duarte@crateforge.example>`  
**Subject:** Draft — confirm 16 remaining units for PO-S2607-830 / CRATE-S

Please confirm and arrange receipt of the 16 remaining CRATE-S units for PO-S2607-830. The July evidence is declared complete, contains no receipt events, and therefore supports a final received quantity of 0 against 16 ordered.

## Limitation

Final receipt positions cannot be stated for the seven lines marked identity reconciliation required, conflicting evidence, incomplete export, or coverage missing. Their observed subtotals remain useful for tracing, but they are not substitutes for final quantities.
