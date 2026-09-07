# July 2026 receiving review

**Scope:** 13 supplied purchase-order lines; all 13 are included below. The review counts only July 2026 events for the exact in-scope order and SKU, sums returns and reversals as signed quantities, counts exact duplicate events once, and excludes conflicting event-ID variants.

## Line results

| Order / SKU | Ordered | Observed July subtotal | Final net | Position | Evidence basis and effect |
| --- | ---: | ---: | ---: | --- | --- |
| PO-S2607-820 / BOLT-M8 | 100 | 90 | — | **Undetermined** | Complete line coverage; accepted RCV-K7101 `+70`, K7102 `+30`, and K7103 `-10`. July event RCV-K7105 names this order but unknown SKU `NUT-M8`, so identity is unclear and the order's line comparison is withheld. |
| PO-S2607-820 / WASHER-M8 | 200 | 200 | — | **Undetermined** | Complete line coverage; accepted RCV-K7104 `+200`. The same unknown-SKU event RCV-K7105 makes the order identity unclear, so the apparent match is not final. |
| PO-S2607-821 / PACK-RACK | 48 | 20 | — | **Undetermined** | Complete line coverage; accepted RCV-K7106 `+20`. RCV-K7107 also appears with different content on PO-S2607-822 / SHIELD-CLR; both variants are excluded, so no final comparison is supportable. |
| PO-S2607-821 / STRAP-20 | 60 | 60 | 60 | **Received as ordered** | Complete coverage and identity-clear July event RCV-K7109 `+60`; difference 0. |
| PO-S2607-822 / SHIELD-CLR | 40 | 28 | — | **Undetermined** | Complete line coverage; accepted RCV-K7108 `+28`. The conflicting RCV-K7107 variant (`+12`) is excluded, so no final comparison is supportable. |
| PO-S2607-823 / POUCH-12 | 30 | 34 | — | **Undetermined** | Coverage is explicitly incomplete. RCV-K7110 `+36` is an exact duplicate and counts once; RCV-K7111 `-2` gives an observed subtotal of 34. That subtotal cannot establish an excess until the full export is confirmed. |
| PO-S2607-824 / TRAY-L | 18 | 9 | — | **Undetermined** | Accepted July events RCV-K7112 `+12` and K7113 `-3`. The only coverage declaration is for June, leaving July coverage missing; 9 is only an observed subtotal. |
| PO-S2607-825 / BINDER-B | 25 | 0 | — | **Undetermined** | Coverage is explicitly incomplete and no July event is supplied. The observed zero is a subtotal, not evidence that nothing was received. |
| PO-S2607-826 / INSERT-G | 70 | 75 | 75 | **Excess: 5** | Complete coverage. Exact duplicate RCV-K7114 `+45` counts once; RCV-K7115 `+40` and K7116 `-10` produce 75. The June reversal is outside the review month. |
| PO-S2607-827 / WRAP-500 | 40 | 18 | 18 | **Shortfall: 22** | Complete coverage; RCV-K7117 `+20`, K7118 `+6`, and K7119 `-8` produce 18. |
| PO-S2607-828 / CLIP-R | 10 | 10 | 10 | **Received as ordered** | Complete coverage; RCV-K7120 `+6` and K7121 `+4` produce 10; difference 0. |
| PO-S2607-829 / PAD-FOAM | 12 | -4 | -4 | **Shortfall: 16** | Complete July coverage; RCV-K7122 `+5` and K7123 `-9` produce `-4`. The June receipt is outside the review month. |
| PO-S2607-830 / CRATE-S | 16 | 0 | 0 | **Shortfall: 16** | Complete coverage and no July receipt events; the supported final net is 0. |

## Evidence gaps Rowan needs resolved

- **Unknown SKU on PO-S2607-820:** RCV-K7105 records 12 units against `NUT-M8`, which is not a supplied line for this in-scope order. This blocks final comparisons for both BOLT-M8 and WASHER-M8 until Beck confirms the event's correct identity.
- **Conflicting event ID:** RCV-K7107 appears once as PO-S2607-821 / PACK-RACK `+18` and once as PO-S2607-822 / SHIELD-CLR `+12`. Both variants were excluded, blocking final comparisons for both lines.
- **Incomplete or missing July coverage:** POUCH-12 is explicitly incomplete, BINDER-B is explicitly incomplete, and TRAY-L has no applicable July declaration. Their values of 34, 0, and 9 are observed subtotals only.
- **Ignored records:** June events RCV-K6990, RCV-K6991, and RCV-K6992, plus out-of-scope order event RCV-K7124, do not affect July in-scope totals. The June-only TRAY-L coverage row also does not establish July completeness.

## Follow-up drafts

### 1. Reconcile PO-S2607-820 event identity

**Owner:** Rowan Ames `<rowan.ames@northquayassembly.example>`  
**Recipient:** Beck Lin `<beck.lin@northquayassembly.example>`  
**Next action:** Confirm the correct order line and content of RCV-K7105, provide corrected July evidence, and then reassess both BOLT-M8 and WASHER-M8.

> **Subject:** Reconcile RCV-K7105 for PO-S2607-820  
> Beck, please reconcile July event RCV-K7105, recorded for PO-S2607-820 with SKU NUT-M8 and quantity 12. NUT-M8 is not among the supplied lines for this order. Please confirm the correct SKU and event content and provide corrected evidence. Until resolved, BOLT-M8 has an observed subtotal of 90 against 100 ordered and WASHER-M8 has an observed subtotal of 200 against 200 ordered; neither is being treated as final.

### 2. Reconcile conflicting RCV-K7107

**Owner:** Rowan Ames `<rowan.ames@northquayassembly.example>`  
**Recipient:** Beck Lin `<beck.lin@northquayassembly.example>`  
**Next action:** Determine which RCV-K7107 record is valid, correct the source/export, and refresh both affected line results.

> **Subject:** Resolve conflicting July event RCV-K7107  
> Beck, RCV-K7107 appears with conflicting content: PO-S2607-821 / PACK-RACK for 18 units and PO-S2607-822 / SHIELD-CLR for 12 units. Both variants were excluded. Please confirm the valid identity and quantity and provide corrected July evidence. Current non-conflicting subtotals are 20 for PACK-RACK against 48 ordered and 28 for SHIELD-CLR against 40 ordered; neither is final.

### 3. Complete POUCH-12 coverage

**Owner and recipient:** Beck Lin `<beck.lin@northquayassembly.example>`  
**Next action:** Supply or confirm the full July export and update the coverage declaration.

> **Subject:** Complete July coverage for PO-S2607-823 / POUCH-12  
> Please provide or confirm the complete July 2026 receiving-event export for PO-S2607-823 / POUCH-12 and confirm its coverage status. The accepted events currently total 34 against 30 ordered, after counting the exact duplicate RCV-K7110 once, but 34 is only an observed subtotal while coverage remains incomplete.

### 4. Establish TRAY-L July coverage

**Owner and recipient:** Beck Lin `<beck.lin@northquayassembly.example>`  
**Next action:** Supply or confirm the full July export and add or correct the July coverage declaration.

> **Subject:** Confirm July coverage for PO-S2607-824 / TRAY-L  
> Please provide or confirm the complete July 2026 receiving-event export for PO-S2607-824 / TRAY-L and confirm July coverage. The packet contains only a June coverage declaration. The accepted July events currently total 9 against 18 ordered, but 9 is only an observed subtotal until July completeness is established.

### 5. Complete BINDER-B coverage

**Owner and recipient:** Beck Lin `<beck.lin@northquayassembly.example>`  
**Next action:** Supply or confirm the full July export and update the coverage declaration.

> **Subject:** Complete July coverage for PO-S2607-825 / BINDER-B  
> Please provide or confirm the complete July 2026 receiving-event export for PO-S2607-825 / BINDER-B and confirm its coverage status. No July events are present in the supplied packet, so the observed subtotal is 0 against 25 ordered; that zero is not being treated as final while coverage remains incomplete.

### 6. Reconcile INSERT-G excess

**Owner and recipient:** Inez Cole `<inez.cole@northquayassembly.example>`  
**Next action:** Reconcile the five-unit excess against the order and receiving evidence and confirm its source and disposition.

> **Subject:** Reconcile 5-unit excess on PO-S2607-826 / INSERT-G  
> Inez, complete July evidence shows a final net of 75 INSERT-G units received against 70 ordered on PO-S2607-826, an excess of 5. This counts the exact duplicate RCV-K7114 once and includes the July `-10` reversal. Please confirm the source of the excess and its corrective disposition.

### 7. Ask supplier for WRAP-500 balance plan

**Owner:** Rowan Ames `<rowan.ames@northquayassembly.example>`  
**Recipient:** Felix Arun `<felix.arun@wrapline.example>`  
**Next action:** Confirm the plan for the remaining 22 units.

> **Subject:** Remaining 22 WRAP-500 units on PO-S2607-827  
> Felix, complete July 2026 evidence shows a final net of 18 WRAP-500 units received against 40 ordered on PO-S2607-827, including the July return. Please confirm the receipt plan for the remaining 22 units.

### 8. Ask supplier for PAD-FOAM balance plan

**Owner:** Rowan Ames `<rowan.ames@northquayassembly.example>`  
**Recipient:** Rafael Brooks `<rafael.brooks@cushionstock.example>`  
**Next action:** Confirm the plan for the 16-unit July shortfall.

> **Subject:** July PAD-FOAM shortfall on PO-S2607-829  
> Rafael, complete July 2026 evidence shows a final net of -4 PAD-FOAM units against 12 ordered on PO-S2607-829. The July `+5` receipt and `-9` return produce a 16-unit shortfall; the June receipt is outside this review. Please confirm the receipt plan for the remaining 16 units.

### 9. Ask supplier for CRATE-S delivery plan

**Owner:** Rowan Ames `<rowan.ames@northquayassembly.example>`  
**Recipient:** Elena Duarte `<elena.duarte@crateforge.example>`  
**Next action:** Confirm the plan for the 16 units not received in July.

> **Subject:** July CRATE-S shortfall on PO-S2607-830  
> Elena, complete July 2026 evidence shows 0 CRATE-S units received against 16 ordered on PO-S2607-830. Please confirm the receipt plan for the remaining 16 units.

All communications above are drafts only. No messages were sent and no receiving records were changed.
