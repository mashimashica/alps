# July 2026 receiving review

Scope: all 13 supplied purchase-order lines. The packet passed structural validation, and the review output contained all 13 lines. No messages were sent and no receiving records were changed.

## Line judgments

| Order / SKU | Ordered | July evidence | Coverage / integrity | Supported status |
|---|---:|---|---|---|
| PO-S2607-820 / BOLT-M8 | 100 | `RCV-K7101 +70`, `RCV-K7102 +30`, `RCV-K7103 -10`; observed subtotal **90** | July coverage is complete, but `RCV-K7105` is a current-month event for the same order and an absent SKU (`NUT-M8`, +12), so order identity must be reconciled | **Identity reconciliation required; no final position.** The apparent 10-unit shortfall is not final. |
| PO-S2607-820 / WASHER-M8 | 200 | `RCV-K7104 +200`; observed subtotal **200** | Same PO-level absent-SKU conflict as above | **Identity reconciliation required; no final position.** Do not call this received as ordered yet. |
| PO-S2607-821 / PACK-RACK | 48 | `RCV-K7106 +20`, disputed `RCV-K7107 +18`; observed subtotal **38** | July coverage is complete, but event ID `RCV-K7107` also identifies a different event on PO-S2607-822 | **Conflicting evidence; no final position.** The apparent 10-unit shortfall is not final. |
| PO-S2607-821 / STRAP-20 | 60 | `RCV-K7109 +60`; observed subtotal **60** | The conflicting `RCV-K7107` affects the integrity of PO-S2607-821 as a whole | **Conflicting evidence; no final position.** Do not call this received as ordered yet. |
| PO-S2607-822 / SHIELD-CLR | 40 | `RCV-K7108 +28`, disputed `RCV-K7107 +12`; observed subtotal **40** | July coverage is complete, but `RCV-K7107` has conflicting content across PO-S2607-821 and PO-S2607-822 | **Conflicting evidence; no final position.** Do not call this received as ordered yet. |
| PO-S2607-823 / POUCH-12 | 30 | `RCV-K7110 +36`, `RCV-K7111 -2`; observed subtotal **34**. The exact duplicate copy of `RCV-K7110` counts once. | July coverage is explicitly incomplete | **Observed subtotal only; no final position.** The apparent 4-unit excess is not final. |
| PO-S2607-824 / TRAY-L | 18 | `RCV-K7112 +12`, `RCV-K7113 -3`; observed subtotal **9** | No matching July coverage declaration; the supplied declaration is for June | **Observed subtotal only; no final position.** The apparent 9-unit shortfall is not final. |
| PO-S2607-825 / BINDER-B | 25 | No supplied July events; observed subtotal **0** | July coverage is explicitly incomplete | **Observed subtotal only; no final position.** Zero must not be treated as a final received quantity. |
| PO-S2607-826 / INSERT-G | 70 | `RCV-K7114 +45`, `RCV-K7115 +40`, `RCV-K7116 -10`; net **75**. The exact duplicate copy of `RCV-K7114` counts once. | Complete, valid July evidence | **Complete excess: 5 units.** |
| PO-S2607-827 / WRAP-500 | 40 | `RCV-K7117 +20`, `RCV-K7118 +6`, `RCV-K7119 -8`; net **18** | Complete, valid July evidence | **Complete shortfall: 22 units.** |
| PO-S2607-828 / CLIP-R | 10 | `RCV-K7120 +6`, `RCV-K7121 +4`; net **10** | Complete, valid July evidence | **Received as ordered.** No follow-up needed. |
| PO-S2607-829 / PAD-FOAM | 12 | `RCV-K7122 +5`, `RCV-K7123 -9`; net **-4** | Complete, valid July evidence | **Complete shortfall: 16 units.** The negative net reflects the signed July correction evidence. |
| PO-S2607-830 / CRATE-S | 16 | No supplied July events; net **0** | Coverage declares the July evidence complete | **Complete shortfall: 16 units.** |

## Follow-up drafts

These are drafts only.

### 1. Reconcile the absent SKU on PO-S2607-820

**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** Reconcile July identity on PO-S2607-820 before receipt close

Please reconcile `RCV-K7105`, which records +12 for `NUT-M8` on PO-S2607-820 even though that SKU is absent from the supplied order lines. Until the source order/event identity is confirmed or corrected, please hold final judgments for `BOLT-M8` (ordered 100; observed July subtotal 90) and `WASHER-M8` (ordered 200; observed July subtotal 200). After reconciliation, rerun the comparison and determine whether supplier follow-up is needed.

### 2. Reconcile conflicting event ID RCV-K7107

**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** Reconcile conflicting July event RCV-K7107

Please reconcile the source record for `RCV-K7107`: it appears as +18 for PO-S2607-821 / `PACK-RACK` and as +12 for PO-S2607-822 / `SHIELD-CLR`. This blocks final judgments for both affected orders: PO-S2607-821 / `PACK-RACK` (ordered 48; observed 38), PO-S2607-821 / `STRAP-20` (ordered 60; observed 60), and PO-S2607-822 / `SHIELD-CLR` (ordered 40; observed 40). Confirm the correct event identity/content, correct the source extract if needed, and rerun all three comparisons.

### 3. Complete the July export evidence

**To:** Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** Complete or confirm July receipt export for three order lines

Please provide or confirm the complete July export for PO-S2607-823 / `POUCH-12` (ordered 30; observed subtotal 34), PO-S2607-824 / `TRAY-L` (ordered 18; observed subtotal 9; no matching July coverage declaration), and PO-S2607-825 / `BINDER-B` (ordered 25; observed subtotal 0). These are observed subtotals only and must not be treated as final. Once coverage is complete, rerun the comparisons and route any confirmed shortfall or excess.

### 4. Reconcile the INSERT-G surplus

**To:** Inez Cole <inez.cole@northquayassembly.example>  
**Subject:** Reconcile 5-unit July excess on PO-S2607-826 / INSERT-G

Complete July evidence nets to 75 units against 70 ordered for PO-S2607-826 / `INSERT-G` (`+45 +40 -10`, with the duplicate copy of `RCV-K7114` counted once). Please reconcile the 5-unit surplus against the purchase order and receiving evidence and record the appropriate correction through the normal receiving process.

### 5. Ask suppliers about confirmed shortfalls

**From/action owner:** Rowan Ames <rowan.ames@northquayassembly.example>

**To:** Felix Arun <felix.arun@wrapline.example>  
**Subject:** 22 units remaining on PO-S2607-827 / WRAP-500

Our complete July receiving evidence nets to 18 units against 40 ordered for PO-S2607-827 / `WRAP-500`, leaving 22 units outstanding. Please confirm whether and when the remaining 22 units will ship, or identify any supplier-side correction we should reconcile.

**To:** Rafael Brooks <rafael.brooks@cushionstock.example>  
**Subject:** 16-unit July gap on PO-S2607-829 / PAD-FOAM

Our complete July receiving evidence nets to -4 units against 12 ordered for PO-S2607-829 / `PAD-FOAM` after the +5 receipt and -9 correction, leaving a 16-unit gap. Please confirm fulfillment for the 16 units and whether your records agree with the July return/correction activity.

**To:** Elena Duarte <elena.duarte@crateforge.example>  
**Subject:** 16 units remaining on PO-S2607-830 / CRATE-S

Our complete July receiving evidence shows a net of 0 units against 16 ordered for PO-S2607-830 / `CRATE-S`. Please confirm whether and when all 16 units will ship, or identify any supplier-side correction we should reconcile.

## Excluded evidence and unresolved gaps

- Excluded from July totals because they are June records: `RCV-K6990` (PO-S2607-826 / `INSERT-G`, -10), `RCV-K6991` (PO-S2607-826 / `INSERT-OLD`, +7), and `RCV-K6992` (PO-S2607-829 / `PAD-FOAM`, +9).
- Excluded as outside the supplied order scope: `RCV-K7124` (PO-S2607-899 / `WRAP-500`, +500).
- Not assigned to a supplied line, and therefore not included in a line subtotal: `RCV-K7105` (PO-S2607-820 / absent SKU `NUT-M8`, +12). It creates an identity-reconciliation blocker for PO-S2607-820.
- Conflicting evidence: `RCV-K7107` has different order/SKU/quantity content in two records; final comparisons for PO-S2607-821 and PO-S2607-822 are blocked.
- Coverage gaps: PO-S2607-823 / `POUCH-12` and PO-S2607-825 / `BINDER-B` are declared incomplete; PO-S2607-824 / `TRAY-L` has no matching July declaration.
- Exact duplicate copies were deduplicated, not double-counted: `RCV-K7110` and `RCV-K7114`.
