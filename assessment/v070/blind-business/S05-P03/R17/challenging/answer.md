# July 2026 receiving review

**Prepared for:** Rowan Ames, purchasing coordinator  
**Scope:** 13 supplied purchase-order lines; all 13 reviewed  
**Status:** Draft only. No messages were sent and no receiving records were changed.

## Source checks

- The packet contains 30 event rows. Two exact duplicate rows were ignored: the repeated copies of `RCV-K7110` and `RCV-K7114`.
- `RCV-K7107` is reused with conflicting content: one version records 18 `PACK-RACK` units on `PO-S2607-821`, while another records 12 `SHIELD-CLR` units on `PO-S2607-822`. Neither version was counted. Both affected line comparisons are withheld pending identity reconciliation.
- July event `RCV-K7105` names in-scope order `PO-S2607-820` but the absent-from-order SKU `NUT-M8`. Under the review rule, both supplied lines on that order remain undetermined pending reconciliation.
- Prior-month events `RCV-K6990`, `RCV-K6991`, and `RCV-K6992` were excluded from July quantities.
- `RCV-K7124` belongs to `PO-S2607-899`, outside the supplied order set, and was excluded from in-scope totals.
- Signed July quantities include returns and correcting reversals algebraically. “Provisional” means the subtotal can be reported, but the evidence does not support a final comparison.

## Line-by-line results

| Order / SKU | Ordered | Observed signed July quantity | Evidence condition | Supported position | Effect of gap / remaining work |
|---|---:|---:|---|---|---|
| `PO-S2607-820` / `BOLT-M8` | 100 | **90 provisional** | Conflicting order/event identity | **Undetermined** | The unexpected July `NUT-M8` event on this order prevents a final comparison; Rowan Ames and Beck Lin must reconcile the order/event identity and rerun the comparison. |
| `PO-S2607-820` / `WASHER-M8` | 200 | **200 provisional** | Conflicting order/event identity | **Undetermined** | The same unexpected-SKU event affects the order, so equality to ordered cannot yet be treated as final; Rowan and Beck must reconcile and rerun. |
| `PO-S2607-821` / `PACK-RACK` | 48 | **20 provisional** | Conflicting event ID | **Undetermined** | The conflicting 18-unit `RCV-K7107` variant was excluded. Rowan and Beck must establish the valid identity/content and rerun. |
| `PO-S2607-821` / `STRAP-20` | 60 | **60 final net** | Complete and valid | **Received as ordered** | No follow-up required. |
| `PO-S2607-822` / `SHIELD-CLR` | 40 | **28 provisional** | Conflicting event ID | **Undetermined** | The conflicting 12-unit `RCV-K7107` variant was excluded. Rowan and Beck must establish the valid identity/content and rerun. |
| `PO-S2607-823` / `POUCH-12` | 30 | **34 provisional** | Export declared incomplete | **Undetermined** | The 34-unit signed subtotal cannot support an excess judgment. Beck Lin must provide or confirm the complete July export, then the line must be rerun. |
| `PO-S2607-824` / `TRAY-L` | 18 | **9 provisional** | July coverage missing | **Undetermined** | The only coverage declaration is for June. Beck must provide or confirm July completeness, then rerun the line. |
| `PO-S2607-825` / `BINDER-B` | 25 | **0 provisional** | Export declared incomplete | **Undetermined** | Zero is only the observed subtotal, not a supported shortfall. Beck must provide or confirm the complete July export, then rerun the line. |
| `PO-S2607-826` / `INSERT-G` | 70 | **75 final net** | Complete and valid | **Excess: 5** | Inez Cole should reconcile the five-unit surplus against the order and receiving evidence. The exact duplicate receipt was counted once; the June return was excluded. |
| `PO-S2607-827` / `WRAP-500` | 40 | **18 final net** | Complete and valid | **Shortfall: 22** | Rowan should follow up with Felix Arun on the remaining 22 units and confirm the expected receipt disposition. |
| `PO-S2607-828` / `CLIP-R` | 10 | **10 final net** | Complete and valid | **Received as ordered** | No follow-up required. |
| `PO-S2607-829` / `PAD-FOAM` | 12 | **−4 final net** | Complete and valid | **Shortfall: 16** | July activity is +5 and −9, for a signed net of −4; the June +9 is excluded. Rowan should follow up with Rafael Brooks on the resulting 16-unit gap. |
| `PO-S2607-830` / `CRATE-S` | 16 | **0 final net** | Complete and valid | **Shortfall: 16** | The complete July evidence contains no receipt event. Rowan should follow up with Elena Duarte on all 16 units. |

## Recipient-specific follow-up drafts

All drafts below are **unsent**.

### 1. `PO-S2607-820` / `BOLT-M8` — identity reconciliation

**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** July 2026 receiving review — `PO-S2607-820` / `BOLT-M8`  
**Action requested:** Reconcile July event `RCV-K7105`, which assigns `NUT-M8` to this order even though that SKU is absent from the supplied order lines. Correct or confirm the source identity, then rerun the `BOLT-M8` comparison; its current observed 90 units are provisional.

### 2. `PO-S2607-820` / `WASHER-M8` — identity reconciliation

**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** July 2026 receiving review — `PO-S2607-820` / `WASHER-M8`  
**Action requested:** Reconcile July event `RCV-K7105`, which assigns `NUT-M8` to this order even though that SKU is absent from the supplied order lines. Correct or confirm the source identity, then rerun the `WASHER-M8` comparison; its current observed 200 units remain provisional.

### 3. `PO-S2607-821` / `PACK-RACK` — identity reconciliation

**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** July 2026 receiving review — `PO-S2607-821` / `PACK-RACK`  
**Action requested:** Resolve the two different records using event ID `RCV-K7107`, correct or confirm the authoritative source record, and rerun the comparison. The 18-unit conflicting variant was excluded, leaving a provisional observed subtotal of 20 units.

### 4. `PO-S2607-822` / `SHIELD-CLR` — identity reconciliation

**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** July 2026 receiving review — `PO-S2607-822` / `SHIELD-CLR`  
**Action requested:** Resolve the two different records using event ID `RCV-K7107`, correct or confirm the authoritative source record, and rerun the comparison. The 12-unit conflicting variant was excluded, leaving a provisional observed subtotal of 28 units.

### 5. `PO-S2607-823` / `POUCH-12` — complete export

**To:** Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** July 2026 receiving review — `PO-S2607-823` / `POUCH-12`  
**Action requested:** Provide or confirm the complete July event export for this line, then rerun the final comparison. The signed subtotal is 34 units after counting the exact duplicate once and applying the two-unit return, but the export is declared incomplete.

### 6. `PO-S2607-824` / `TRAY-L` — July coverage

**To:** Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** July 2026 receiving review — `PO-S2607-824` / `TRAY-L`  
**Action requested:** Provide or confirm a July completeness declaration and the complete July event export, then rerun the final comparison. The supplied coverage declaration is for June; the July signed subtotal of nine units is provisional.

### 7. `PO-S2607-825` / `BINDER-B` — complete export

**To:** Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** July 2026 receiving review — `PO-S2607-825` / `BINDER-B`  
**Action requested:** Provide or confirm the complete July event export, then rerun the final comparison. No July event is currently present, but the export is declared incomplete, so the observed zero cannot support a final shortfall judgment.

### 8. `PO-S2607-826` / `INSERT-G` — surplus reconciliation

**To:** Inez Cole <inez.cole@northquayassembly.example>  
**Subject:** July 2026 receiving review — `PO-S2607-826` / `INSERT-G`  
**Action requested:** Reconcile the supported five-unit surplus against the order and receiving evidence. July net receipt is 75 against 70 ordered, after ignoring the exact duplicate `RCV-K7114`, applying the ten-unit July reversal, and excluding the June record.

### 9. `PO-S2607-827` / `WRAP-500` — remaining receipt

**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Felix Arun <felix.arun@wrapline.example>  
**Subject:** July 2026 receiving review — `PO-S2607-827` / `WRAP-500`  
**Action requested:** Follow up on the remaining 22 units and confirm the expected receipt disposition. Complete July evidence shows a signed net of 18 units against 40 ordered.

### 10. `PO-S2607-829` / `PAD-FOAM` — remaining receipt

**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Rafael Brooks <rafael.brooks@cushionstock.example>  
**Subject:** July 2026 receiving review — `PO-S2607-829` / `PAD-FOAM`  
**Action requested:** Follow up on the remaining 16 units and confirm the expected receipt disposition. Complete July evidence nets to −4 units against 12 ordered after the nine-unit July reversal; the nine-unit June receipt is outside the review month.

### 11. `PO-S2607-830` / `CRATE-S` — remaining receipt

**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Elena Duarte <elena.duarte@crateforge.example>  
**Subject:** July 2026 receiving review — `PO-S2607-830` / `CRATE-S`  
**Action requested:** Follow up on all 16 remaining units and confirm the expected receipt disposition. The evidence is declared complete and contains no July receipt event for this line.
