# July 2026 receiving review

Prepared for Rowan Ames. This review is draft-only; no message was sent and no receiving record was changed.

Only July 2026 events for the supplied order lines contribute to the judgments. Exact duplicate event copies are counted once, and negative quantities reduce the net algebraically. An observed subtotal is not a final receipt position when coverage is incomplete or missing, or when identity or event evidence is conflicting.

## Line review

| Order / SKU | Ordered | Observed July net and event evidence | Coverage / flags | Supported position | Follow-up |
|---|---:|---|---|---|---|
| PO-S2607-820 / BOLT-M8 | 100 | **90**: RCV-K7101 +70, RCV-K7102 +30, RCV-K7103 -10 | Complete; order-level identity issue RCV-K7105 | **Undetermined.** The 90 is an observed subtotal only. | Draft A: Rowan Ames + Beck Lin |
| PO-S2607-820 / WASHER-M8 | 200 | **200**: RCV-K7104 +200 | Complete; order-level identity issue RCV-K7105 | **Undetermined.** The 200 is an observed subtotal only. | Draft A: Rowan Ames + Beck Lin |
| PO-S2607-821 / PACK-RACK | 48 | **20 undisputed**: RCV-K7106 +20; **38 if** the PACK-RACK version of conflicting RCV-K7107 (+18) is authoritative | Complete; conflicting event ID RCV-K7107 | **Undetermined.** | Draft B: Rowan Ames + Beck Lin |
| PO-S2607-821 / STRAP-20 | 60 | **60**: RCV-K7109 +60 | Complete; no flag | **Received as ordered.** | None needed |
| PO-S2607-822 / SHIELD-CLR | 40 | **28 undisputed**: RCV-K7108 +28; **40 if** the SHIELD-CLR version of conflicting RCV-K7107 (+12) is authoritative | Complete; conflicting event ID RCV-K7107 affects this line as the alternate event identity | **Undetermined.** Although the verifier's canonical copy produces a 28-unit shortfall, the other supplied version would make the line equal to ordered; the conflict prevents a supported final judgment. | Draft B: Rowan Ames + Beck Lin |
| PO-S2607-823 / POUCH-12 | 30 | **34 observed**: RCV-K7110 +36, RCV-K7111 -2. The exact duplicate copy of RCV-K7110 is counted once. | Incomplete | **Undetermined.** Do not treat the apparent +4 as final excess. | Draft C: Beck Lin |
| PO-S2607-824 / TRAY-L | 18 | **9 observed**: RCV-K7112 +12, RCV-K7113 -3 | July coverage missing; the supplied declaration is for June | **Undetermined.** | Draft D: Beck Lin |
| PO-S2607-825 / BINDER-B | 25 | No July event observed; the verifier's subtotal is 0, but incomplete coverage means this is not evidence of zero receipts | Incomplete | **Undetermined.** | Draft E: Beck Lin |
| PO-S2607-826 / INSERT-G | 70 | **75**: RCV-K7114 +45, RCV-K7115 +40, RCV-K7116 -10. The exact duplicate copy of RCV-K7114 is counted once. | Complete; no flag | **Excess of 5.** | Draft F: Inez Cole |
| PO-S2607-827 / WRAP-500 | 40 | **18**: RCV-K7117 +20, RCV-K7118 +6, RCV-K7119 -8 | Complete; no flag | **Shortfall of 22.** | Draft G: Felix Arun, through Rowan Ames |
| PO-S2607-828 / CLIP-R | 10 | **10**: RCV-K7120 +6, RCV-K7121 +4 | Complete; no flag | **Received as ordered.** | None needed |
| PO-S2607-829 / PAD-FOAM | 12 | **-4**: RCV-K7122 +5, RCV-K7123 -9 | Complete; no flag | **Shortfall of 16** relative to the ordered quantity. | Draft H: Rafael Brooks, through Rowan Ames |
| PO-S2607-830 / CRATE-S | 16 | No July events; with complete coverage, supported net is **0** | Complete; no flag | **Shortfall of 16.** | Draft I: Elena Duarte, through Rowan Ames |

## Follow-up drafts

### Draft A — reconcile PO-S2607-820 identity

**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** Reconcile July receipt identity for PO-S2607-820

The July evidence shows BOLT-M8 ordered 100 with an observed net of 90 (RCV-K7101 +70, RCV-K7102 +30, RCV-K7103 -10) and WASHER-M8 ordered 200 with an observed net of 200 (RCV-K7104 +200). It also contains RCV-K7105 for 12 units of NUT-M8, a SKU that is not a supplied line on this order. Please determine the correct order and SKU for RCV-K7105, correct or confirm its mapping, and provide the reconciled July event set. Until that is resolved, neither supplied line has a final supported receipt position.

### Draft B — resolve conflicting event RCV-K7107

**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** Resolve conflicting July event RCV-K7107

RCV-K7107 appears twice with different content: PO-S2607-821 / PACK-RACK +18 and PO-S2607-822 / SHIELD-CLR +12. PACK-RACK is ordered 48 with an undisputed subtotal of 20 from RCV-K7106; SHIELD-CLR is ordered 40 with an undisputed subtotal of 28 from RCV-K7108. Please identify the authoritative order, SKU, and quantity for RCV-K7107 using the source or audit record, correct the export if needed, and return the reconciled evidence. The conflict leaves both line judgments undetermined.

### Draft C — complete POUCH-12 export

**To:** Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** Complete July export for PO-S2607-823 / POUCH-12

PO-S2607-823 / POUCH-12 is ordered 30. The incomplete July export has an observed net of 34: RCV-K7110 +36 and RCV-K7111 -2, with the exact duplicate RCV-K7110 counted once. Please provide or confirm the full July export for this line and confirm whether 34 is the complete net. The line remains undetermined until coverage is complete.

### Draft D — establish July TRAY-L coverage

**To:** Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** Provide July coverage for PO-S2607-824 / TRAY-L

PO-S2607-824 / TRAY-L is ordered 18 and has a July observed subtotal of 9 from RCV-K7112 +12 and RCV-K7113 -3. The only supplied coverage declaration is for June, so July coverage is absent. Please provide or confirm the complete July export and its coverage declaration, including any missing events. Do not treat the observed 9 as the final net until then.

### Draft E — complete BINDER-B export

**To:** Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** Complete July export for PO-S2607-825 / BINDER-B

PO-S2607-825 / BINDER-B is ordered 25. No July event is present in the supplied evidence, and coverage is explicitly incomplete. Please provide or confirm the full July export for this line and state whether any receipt, return, or correcting reversal events are missing. The absence of observed events must not be treated as a confirmed zero receipt.

### Draft F — reconcile INSERT-G surplus

**To:** Inez Cole <inez.cole@northquayassembly.example>  
**Subject:** Reconcile 5-unit excess for PO-S2607-826 / INSERT-G

PO-S2607-826 / INSERT-G is ordered 70, while complete July evidence nets to 75: RCV-K7114 +45, RCV-K7115 +40, and RCV-K7116 -10; the exact duplicate copy of RCV-K7114 was counted once. Please reconcile the 5-unit surplus against physical stock and the receiving evidence, and report the required receipt correction or surplus disposition.

### Draft G — supplier follow-up for WRAP-500 shortfall

**To:** Felix Arun <felix.arun@wrapline.example>  
**Via:** Rowan Ames <rowan.ames@northquayassembly.example>  
**Subject:** Remaining 22 units on PO-S2607-827 / WRAP-500

Complete July evidence for PO-S2607-827 / WRAP-500 shows 18 net received against 40 ordered: RCV-K7117 +20, RCV-K7118 +6, and RCV-K7119 -8. Please confirm when the remaining 22 units will be delivered, or identify any receiving evidence that should change this balance.

### Draft H — supplier follow-up for PAD-FOAM shortfall

**To:** Rafael Brooks <rafael.brooks@cushionstock.example>  
**Via:** Rowan Ames <rowan.ames@northquayassembly.example>  
**Subject:** Reconcile remaining 16 units on PO-S2607-829 / PAD-FOAM

Complete July evidence for PO-S2607-829 / PAD-FOAM shows a net of -4 against 12 ordered: RCV-K7122 +5 and RCV-K7123 -9. Please confirm delivery of the 16 net units needed to reach the ordered quantity, or provide evidence that the receipt or return quantities should be corrected.

### Draft I — supplier follow-up for CRATE-S shortfall

**To:** Elena Duarte <elena.duarte@crateforge.example>  
**Via:** Rowan Ames <rowan.ames@northquayassembly.example>  
**Subject:** Remaining 16 units on PO-S2607-830 / CRATE-S

PO-S2607-830 / CRATE-S is ordered 16. Complete July coverage contains no receipt events, supporting a July net of 0 and a shortfall of 16. Please confirm when the 16 units will be delivered, or identify any missing or incorrectly attributed receiving event.

## Exclusions and unresolved global conflicts

- **Prior-month events excluded:** RCV-K6990 (PO-S2607-826 / INSERT-G, -10), RCV-K6991 (PO-S2607-826 / INSERT-OLD, +7), and RCV-K6992 (PO-S2607-829 / PAD-FOAM, +9) are dated June 2026 and do not contribute to July totals.
- **Out-of-scope order excluded:** RCV-K7124 (PO-S2607-899 / WRAP-500, +500) is for an order outside the supplied order set.
- **Unmatched line identity:** RCV-K7105 (PO-S2607-820 / NUT-M8, +12) is a July event for an in-scope order but not a supplied order line. It is excluded from line subtotals and blocks final judgment on that order pending reconciliation.
- **Conflicting event ID:** RCV-K7107 has two different supplied records—PO-S2607-821 / PACK-RACK +18 and PO-S2607-822 / SHIELD-CLR +12. Neither variant can be selected as authoritative from the packet.

