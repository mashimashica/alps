# July 2026 receiving review

To: Rowan Ames

The supplied packet contains 13 unique purchase-order lines with valid positive ordered quantities and the required responsibility contacts. July receipt positions are final for 6 lines: 2 were received as ordered, 3 have complete shortfalls, and 1 has a complete excess. The other 7 lines remain unresolved: 4 are affected by identity/event conflicts and 3 lack explicitly complete July coverage.

## Line-by-line review

| Purchase-order line | Ordered | Supported July evidence | Judgment | Required action |
|---|---:|---:|---|---|
| PO-S2607-820 / BOLT-M8 | 100 | 90 (70 + 30 - 10) | **Undetermined — identity conflict.** July coverage is marked complete, but event RCV-K7105 names the in-scope order with unexpected SKU NUT-M8. | Rowan Ames and Beck Lin to reconcile the PO/SKU identity before any supplier shortage claim. |
| PO-S2607-820 / WASHER-M8 | 200 | 200 | **Undetermined — identity conflict.** The subtotal equals the order, but RCV-K7105 makes the order's SKU identity unresolved. | Rowan Ames and Beck Lin to reconcile the PO/SKU identity. |
| PO-S2607-821 / PACK-RACK | 48 | 20 undisputed; the script subtotal of 38 also includes disputed RCV-K7107 (+18) | **Undetermined — conflicting event content.** RCV-K7107 is also supplied as PO-S2607-822 / SHIELD-CLR / +12. | Rowan Ames and Beck Lin to determine the authoritative RCV-K7107 record. Do not yet request 10 units from the supplier. |
| PO-S2607-821 / STRAP-20 | 60 | 60 | **Received as ordered.** Coverage is explicitly complete. | None. |
| PO-S2607-822 / SHIELD-CLR | 40 | 28 undisputed; a disputed RCV-K7107 variant adds 12 | **Undetermined — conflicting event content.** The duplicate event ID conflicts with the PACK-RACK record. | Rowan Ames and Beck Lin to determine the authoritative RCV-K7107 record. |
| PO-S2607-823 / POUCH-12 | 30 | Observed subtotal 34 (36 - 2); the exact repeated copy of RCV-K7110 is counted once | **Undetermined — incomplete export.** Coverage is explicitly false, so 34 is not a final excess position. | Beck Lin to provide or confirm the complete July export. |
| PO-S2607-824 / TRAY-L | 18 | Observed subtotal 9 (12 - 3) | **Undetermined — missing July coverage.** The only coverage declaration is for June. | Beck Lin to provide or confirm complete July coverage. |
| PO-S2607-825 / BINDER-B | 25 | No July events observed | **Undetermined — incomplete export.** Coverage is explicitly false; the absence of observed events is not evidence of zero receipts. | Beck Lin to provide or confirm the complete July export. |
| PO-S2607-826 / INSERT-G | 70 | 75 (45 + 40 - 10); the exact repeated copy of RCV-K7114 is counted once | **Complete excess: 5 units.** Coverage is explicitly complete. | Inez Cole to reconcile the 5-unit excess against the receiving evidence. |
| PO-S2607-827 / WRAP-500 | 40 | 18 (20 + 6 - 8) | **Complete shortfall: 22 units.** Coverage is explicitly complete. | Felix Arun to confirm the remaining 22 units. |
| PO-S2607-828 / CLIP-R | 10 | 10 (6 + 4) | **Received as ordered.** Coverage is explicitly complete. | None. |
| PO-S2607-829 / PAD-FOAM | 12 | -4 (5 - 9) | **Complete shortfall: 16 units.** Coverage is explicitly complete; the June receipt of 9 is outside the requested month. | Rafael Brooks to confirm the remaining 16-unit net position. |
| PO-S2607-830 / CRATE-S | 16 | 0; no July events observed | **Complete shortfall: 16 units.** Coverage is explicitly complete, so the zero subtotal is supported for this review. | Elena Duarte to confirm the remaining 16 units. |

## Evidence handling and exceptions

- Only events whose `event_month` is `2026-07` were included. June events RCV-K6990, RCV-K6991, and RCV-K6992 were excluded.
- Exact repeated copies of RCV-K7110 and RCV-K7114 were deduplicated.
- RCV-K7107 has conflicting content across PO-S2607-821 / PACK-RACK and PO-S2607-822 / SHIELD-CLR. Both lines are therefore unresolved. The automated result flags SHIELD-CLR but calculates PACK-RACK from the first occurrence; that first-occurrence choice is not sufficient to finalize PACK-RACK.
- RCV-K7105 is a July event for in-scope PO-S2607-820 but names SKU NUT-M8, which is absent from that order's supplied lines. It does not enter either subtotal and requires identity reconciliation affecting both supplied PO-S2607-820 lines.
- RCV-K7124 belongs to out-of-scope order PO-S2607-899 and was excluded from all in-scope totals.

## Follow-up drafts — do not send

### 1. PO-S2607-820 identity reconciliation

**To:** Rowan Ames <rowan.ames@northquayassembly.example>  
**Subject:** Reconcile July SKU identity on PO-S2607-820

Please reconcile July event RCV-K7105, which names PO-S2607-820 / NUT-M8 even though NUT-M8 is not a supplied line for that order. Until the authoritative order/SKU assignment is confirmed, the BOLT-M8 observed subtotal of 90 and WASHER-M8 observed subtotal of 200 are not final receipt positions. Please coordinate the purchasing-record correction or confirmation; no receiving record has been changed.

**To:** Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** Validate July source record RCV-K7105 for PO-S2607-820

Please validate the source mapping for RCV-K7105 (PO-S2607-820 / NUT-M8 / 12 units) and provide the authoritative order/SKU identity. The event was excluded from the supplied BOLT-M8 and WASHER-M8 subtotals, and both line judgments remain undetermined pending reconciliation.

### 2. Conflicting RCV-K7107 records

**To:** Rowan Ames <rowan.ames@northquayassembly.example>  
**Subject:** Purchasing reconciliation required for conflicting event RCV-K7107

Please reconcile the two supplied versions of RCV-K7107: PO-S2607-821 / PACK-RACK / 18 units and PO-S2607-822 / SHIELD-CLR / 12 units. PACK-RACK has 20 undisputed July units and SHIELD-CLR has 28 undisputed July units; neither line can be finalized until the authoritative event is identified. Please do not initiate a supplier shortage request from the disputed version.

**To:** Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** Source-data correction needed for duplicate event ID RCV-K7107

Please identify the authoritative RCV-K7107 source record and provide a corrected or confirmed July export. The event ID appears with different order, SKU, and quantity values, affecting PO-S2607-821 / PACK-RACK and PO-S2607-822 / SHIELD-CLR.

### 3. Incomplete or missing July coverage

**To:** Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** Complete July receiving evidence needed for three PO lines

Please provide or explicitly confirm the complete July 2026 receiving export for the following lines before final comparison:

- PO-S2607-823 / POUCH-12 — coverage is marked incomplete; observed subtotal 34.
- PO-S2607-824 / TRAY-L — no July coverage declaration is supplied; observed subtotal 9.
- PO-S2607-825 / BINDER-B — coverage is marked incomplete; no July events were observed, which must not be treated as a confirmed zero.

### 4. Complete excess

**To:** Inez Cole <inez.cole@northquayassembly.example>  
**Subject:** Reconcile 5-unit July excess for PO-S2607-826 / INSERT-G

The complete July evidence nets to 75 units against 70 ordered for PO-S2607-826 / INSERT-G. Please reconcile the 5-unit excess against events RCV-K7114 (+45, exact duplicate counted once), RCV-K7115 (+40), and RCV-K7116 (-10), and confirm the appropriate warehouse disposition. No receiving record has been changed.

### 5. Complete shortfalls

**To:** Felix Arun <felix.arun@wrapline.example>  
**Subject:** Remaining 22 units on PO-S2607-827 / WRAP-500

Our complete July evidence nets to 18 units against 40 ordered for PO-S2607-827 / WRAP-500, leaving a 22-unit shortfall after the July return. Please confirm the status and expected receipt timing for the remaining 22 units.

**To:** Rafael Brooks <rafael.brooks@cushionstock.example>  
**Subject:** Remaining 16-unit net position on PO-S2607-829 / PAD-FOAM

Our complete July evidence nets to -4 units (5 received and 9 returned) against 12 ordered for PO-S2607-829 / PAD-FOAM, leaving a 16-unit shortfall for July. The separate 9-unit receipt is dated June and was not included. Please confirm the status and expected receipt timing for the remaining 16-unit net position.

**To:** Elena Duarte <elena.duarte@crateforge.example>  
**Subject:** Remaining 16 units on PO-S2607-830 / CRATE-S

The complete July export contains no receipt events for PO-S2607-830 / CRATE-S against 16 units ordered. Please confirm the status and expected receipt timing for the remaining 16 units.

## Limitation

This review establishes what the supplied JSON supports; it does not independently authenticate the records or prove that a coverage declaration reflects a genuinely complete source export. All messages above are drafts only. No contact was made and no receiving record was edited.
