# July 2026 receiving review

Rowan can close two lines as received as ordered. Four lines have supported, complete-evidence variances requiring follow-up: three shortfalls and one excess. Seven more lines remain undetermined because their evidence is incomplete or conflicted. No messages were sent and no receiving records were changed.

## Line-by-line review

Only July 2026 events contribute to the quantities below. “Complete” means the supplied July coverage declaration says `complete: true` and no identity/content conflict limits the line. An observed subtotal on an incomplete or conflicted line is not a final receipt position.

| Order / SKU | Ordered | Evidence and July quantity | Coverage / issue | Supported position | Next action |
|---|---:|---|---|---|---|
| PO-S2607-820 / BOLT-M8 | 100 | RCV-K7101 +70, K7102 +30, K7103 -10; observed net **90** | July coverage says complete, but RCV-K7105 reports NUT-M8 on this order even though that SKU is absent from its supplied order lines | **Undetermined**; do not call a 10-unit shortfall while order/event identity is unresolved | Rowan + Beck reconcile the source identity |
| PO-S2607-820 / WASHER-M8 | 200 | RCV-K7104 +200; observed net **200** | July coverage says complete, but the same RCV-K7105 NUT-M8 mismatch affects confidence in this order's line identity | **Undetermined**; equality is not final while identity is unresolved | Rowan + Beck reconcile the source identity |
| PO-S2607-821 / PACK-RACK | 48 | RCV-K7106 +20; observed unconflicted subtotal **20**. Conflicted RCV-K7107 is excluded | July coverage says complete, but RCV-K7107 appears with different content: PACK-RACK +18 and SHIELD-CLR +12 | **Undetermined** | Rowan + Beck reconcile RCV-K7107 at source |
| PO-S2607-821 / STRAP-20 | 60 | RCV-K7109 +60; net **60** | Complete July coverage; no issue | **Received as ordered** | None |
| PO-S2607-822 / SHIELD-CLR | 40 | RCV-K7108 +28; observed unconflicted subtotal **28**. Conflicted RCV-K7107 is excluded | July coverage says complete, but this line is the other content variant of RCV-K7107 | **Undetermined**; the unconflicted 28 alone does not support a final shortfall | Rowan + Beck reconcile RCV-K7107 at source |
| PO-S2607-823 / POUCH-12 | 30 | RCV-K7110 +36 counted once despite its exact duplicate; RCV-K7111 -2; observed net **34** | July coverage explicitly incomplete | **Undetermined**; do not call a 4-unit excess | Beck provides/confirms the complete July export |
| PO-S2607-824 / TRAY-L | 18 | RCV-K7112 +12, K7113 -3; observed net **9** | Only June coverage is supplied; no July coverage declaration | **Undetermined**; do not call a 9-unit shortfall | Beck supplies July coverage and the complete export |
| PO-S2607-825 / BINDER-B | 25 | No July event in the supplied packet; **no supported subtotal** | July coverage explicitly incomplete | **Undetermined**; absence of an event is not treated as zero | Beck provides/confirms the complete July export |
| PO-S2607-826 / INSERT-G | 70 | RCV-K7114 +45 counted once despite its exact duplicate, K7115 +40, K7116 -10; net **75** | Complete July coverage; June RCV-K6990 and K6991 excluded | **Complete excess: 5** | Inez reconciles the surplus against the order and receiving evidence |
| PO-S2607-827 / WRAP-500 | 40 | RCV-K7117 +20, K7118 +6, K7119 -8; net **18** | Complete July coverage; no issue | **Complete shortfall: 22** | Felix confirms the remaining 22 units |
| PO-S2607-828 / CLIP-R | 10 | RCV-K7120 +6, K7121 +4; net **10** | Complete July coverage; no issue | **Received as ordered** | None |
| PO-S2607-829 / PAD-FOAM | 12 | RCV-K7122 +5, K7123 -9; net **-4** | Complete July coverage; June RCV-K6992 +9 excluded | **Complete shortfall: 16** relative to ordered quantity | Rafael confirms the remaining 16 units and the July return position |
| PO-S2607-830 / CRATE-S | 16 | No July events; complete coverage supports net **0** | Complete July coverage; no issue | **Complete shortfall: 16** | Elena confirms the remaining 16 units |

### Packet-level filtering and reconciliation notes

- Excluded as out of month: RCV-K6990 (INSERT-G -10), RCV-K6991 (INSERT-OLD +7), and RCV-K6992 (PAD-FOAM +9), all dated June 2026.
- Excluded as outside the supplied order set: RCV-K7124 for PO-S2607-899 / WRAP-500 +500.
- Did not allocate RCV-K7105 (PO-S2607-820 / NUT-M8 +12) to any supplied line; it creates an identity-reconciliation issue for that order.
- Counted exact duplicate copies of RCV-K7110 and RCV-K7114 once each.
- Excluded both content variants of RCV-K7107 from final comparisons. The processor flagged PACK-RACK but did not propagate the same conflict to SHIELD-CLR; this review applies the skill rule to both affected lines.
- The input passed structural validation, including positive-integer ordered quantities.

## Draft follow-ups

These are drafts only.

1. **To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
   **For:** PO-S2607-820 / BOLT-M8  
   **Draft:** Please reconcile July event RCV-K7105, which records NUT-M8 against PO-S2607-820 although NUT-M8 is absent from the supplied order lines. BOLT-M8 has an observed July net of 90 against 100 ordered, but its final receipt position must remain undetermined until the order/event identity is resolved. Please confirm the corrected source record and whether the July evidence is complete for this line.

2. **To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
   **For:** PO-S2607-820 / WASHER-M8  
   **Draft:** Please reconcile July event RCV-K7105, which records NUT-M8 against PO-S2607-820 although that SKU is absent from the supplied order lines. WASHER-M8 has an observed July net of 200 against 200 ordered, but its final position remains undetermined until the order/event identity is resolved. Please confirm the corrected source record and completeness for this line.

3. **To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
   **For:** PO-S2607-821 / PACK-RACK  
   **Draft:** Please reconcile event ID RCV-K7107 at source. It appears once as PO-S2607-821 / PACK-RACK +18 and once as PO-S2607-822 / SHIELD-CLR +12. Excluding that conflicted event leaves an observed PACK-RACK subtotal of 20 against 48 ordered, so no final comparison is supported. Please confirm the authoritative event content and complete July evidence.

4. **To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
   **For:** PO-S2607-822 / SHIELD-CLR  
   **Draft:** Please reconcile event ID RCV-K7107 at source. It appears once as PO-S2607-821 / PACK-RACK +18 and once as PO-S2607-822 / SHIELD-CLR +12. Excluding that conflicted event leaves an observed SHIELD-CLR subtotal of 28 against 40 ordered, so no final comparison is supported. Please confirm the authoritative event content and complete July evidence.

5. **To:** Beck Lin <beck.lin@northquayassembly.example>  
   **For:** PO-S2607-823 / POUCH-12  
   **Draft:** Please provide or confirm the full July 2026 receiving export for PO-S2607-823 / POUCH-12. The supplied coverage is incomplete; after counting duplicate RCV-K7110 once and applying return RCV-K7111, the observed subtotal is 34 against 30 ordered, but the final receipt position is undetermined.

6. **To:** Beck Lin <beck.lin@northquayassembly.example>  
   **For:** PO-S2607-824 / TRAY-L  
   **Draft:** Please provide the July 2026 coverage declaration and full receiving export for PO-S2607-824 / TRAY-L. The packet contains only a June coverage declaration. July events currently show an observed subtotal of 9 against 18 ordered, but no final receipt comparison is supported without July completeness evidence.

7. **To:** Beck Lin <beck.lin@northquayassembly.example>  
   **For:** PO-S2607-825 / BINDER-B  
   **Draft:** Please provide or confirm the full July 2026 receiving export for PO-S2607-825 / BINDER-B. Coverage is marked incomplete and no July event is present in the packet, so the line cannot be treated as zero received or assigned a final receipt position.

8. **To:** Inez Cole <inez.cole@northquayassembly.example>  
   **For:** PO-S2607-826 / INSERT-G  
   **Draft:** Please reconcile the supported 5-unit July surplus for PO-S2607-826 / INSERT-G. Complete July evidence nets to 75 against 70 ordered after counting duplicate RCV-K7114 once, including the -10 correcting reversal, and excluding June records. Please confirm the disposition and any required receiving correction; do not change the record without the normal approval process.

9. **To:** Felix Arun <felix.arun@wrapline.example>  
   **For:** PO-S2607-827 / WRAP-500  
   **Draft:** Complete July receiving evidence nets to 18 units against 40 ordered for PO-S2607-827 / WRAP-500, a 22-unit shortfall after the -8 return. Please confirm the status and expected receipt date of the remaining 22 units.

10. **To:** Rafael Brooks <rafael.brooks@cushionstock.example>  
    **For:** PO-S2607-829 / PAD-FOAM  
    **Draft:** Complete July receiving evidence nets to -4 units against 12 ordered for PO-S2607-829 / PAD-FOAM, a 16-unit shortfall relative to the order after the July -9 return; the June +9 receipt is outside this review. Please confirm the July return status and the plan/date for the remaining 16 units.

11. **To:** Elena Duarte <elena.duarte@crateforge.example>  
    **For:** PO-S2607-830 / CRATE-S  
    **Draft:** Complete July coverage contains no receipt events for PO-S2607-830 / CRATE-S, supporting a July net of 0 against 16 ordered and a 16-unit shortfall. Please confirm the status and expected receipt date of the remaining 16 units.

The successful processor run and representative component checks establish the implemented behavior on this supplied packet only. They do not establish that every future review will be interpreted effectively by an agent; business judgments still require review of scope, completeness, conflicts, and source evidence.
