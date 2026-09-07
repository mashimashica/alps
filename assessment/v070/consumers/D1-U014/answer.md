# July 2026 receiving review

## Outcome

The review covers all 13 supplied purchase-order lines for `2026-07`. Two lines are supported as received as ordered, three have supported shortfalls, one has a supported excess, and seven remain unconfirmed because of identity, conflicting-event, or coverage gaps. No messages were sent and no receiving records were changed.

The supplied contract was valid and the deterministic processor completed with exit code 0. Its output is processing evidence, not the final judgment. In particular, the processor retained the first occurrence of conflicted event ID `RCV-K7107`; the review below does not choose either conflicting row and therefore leaves both affected lines unconfirmed.

## Scope and source assumptions

- Only events whose `event_month` is `2026-07` are included. Quantities retain their supplied signs, so returns and correcting reversals reduce the observed net.
- Exact duplicate copies count once: the second identical `RCV-K7110` and `RCV-K7114` rows were ignored.
- A complete July coverage declaration supports a final comparison only when there is no identity or event conflict. Incomplete or missing July coverage supports an observed subtotal, not a final receipt position.
- A line with incomplete coverage and no supplied event is described as having no observed July event; zero is not inferred as a receipt quantity. By contrast, complete coverage with no events supports a net receipt of 0 for the month.

## Line-by-line review

| Order / SKU | Ordered | Supported July event evidence | July coverage | Judgment | Evidence gap and follow-up |
|---|---:|---|---|---|---|
| `PO-S2607-820` / `BOLT-M8` | 100 | `RCV-K7101` +70; `RCV-K7102` +30; `RCV-K7103` -10; observed net **90** | Complete | **Final position unconfirmed** | `RCV-K7105` records +12 of unlisted `NUT-M8` against this order. Rowan Ames and Beck Lin must reconcile the order/SKU identity before any 10-unit shortfall is treated as final. |
| `PO-S2607-820` / `WASHER-M8` | 200 | `RCV-K7104` +200; observed net **200** | Complete | **Final position unconfirmed** | The same `RCV-K7105` identity anomaly affects the order. Rowan Ames and Beck Lin must reconcile it before accepting the apparent match as final. |
| `PO-S2607-821` / `PACK-RACK` | 48 | Uncontested: `RCV-K7106` +20. Disputed `RCV-K7107` is also represented as +18 for this line; uncontested subtotal **20**, potential total **38** if that row is validated. | Complete | **Final position unconfirmed** | `RCV-K7107` has conflicting content and cannot be chosen. Rowan Ames and Beck Lin must establish the canonical event. |
| `PO-S2607-821` / `STRAP-20` | 60 | `RCV-K7109` +60; net **60** | Complete | **Received as ordered** | None; no follow-up required. |
| `PO-S2607-822` / `SHIELD-CLR` | 40 | Uncontested: `RCV-K7108` +28. Disputed `RCV-K7107` is also represented as +12 for this line; uncontested subtotal **28**, potential total **40** if that row is validated. | Complete | **Final position unconfirmed** | `RCV-K7107` has conflicting content and cannot be chosen. Rowan Ames and Beck Lin must establish the canonical event. |
| `PO-S2607-823` / `POUCH-12` | 30 | `RCV-K7110` +36 counted once; `RCV-K7111` -2; observed net **34** | Incomplete | **Final position unconfirmed** | The export is not declared complete; Beck Lin must provide or certify a complete July extract before an excess can be concluded. |
| `PO-S2607-824` / `TRAY-L` | 18 | `RCV-K7112` +12; `RCV-K7113` -3; observed net **9** | No July declaration; only a June declaration was supplied | **Final position unconfirmed** | Beck Lin must provide the missing July coverage declaration and any omitted July events. |
| `PO-S2607-825` / `BINDER-B` | 25 | No July events supplied; **no receipt quantity inferred** | Incomplete | **Final position unconfirmed** | Beck Lin must provide or certify the complete July extract. |
| `PO-S2607-826` / `INSERT-G` | 70 | `RCV-K7114` +45 counted once; `RCV-K7115` +40; `RCV-K7116` -10; net **75** | Complete | **Excess: 5** | Inez Cole should reconcile the five-unit overage and determine disposition. |
| `PO-S2607-827` / `WRAP-500` | 40 | `RCV-K7117` +20; `RCV-K7118` +6; `RCV-K7119` -8; net **18** | Complete | **Shortfall: 22** | Felix Arun, with Rowan Ames coordinating, should confirm the remaining 22 units or supply corrected receipt/return evidence and a resolution date. |
| `PO-S2607-828` / `CLIP-R` | 10 | `RCV-K7120` +6; `RCV-K7121` +4; net **10** | Complete | **Received as ordered** | None; no follow-up required. |
| `PO-S2607-829` / `PAD-FOAM` | 12 | `RCV-K7122` +5; `RCV-K7123` -9; net **-4** | Complete | **Shortfall: 16** | Rafael Brooks, with Rowan Ames coordinating, should reconcile the negative July net and confirm replacement or corrected reversal evidence for the 16-unit gap. |
| `PO-S2607-830` / `CRATE-S` | 16 | No July receipt events; complete coverage supports net **0** | Complete | **Shortfall: 16** | Elena Duarte, with Rowan Ames coordinating, should confirm delivery of all 16 units or provide corrected receipt evidence and a resolution date. |

## Draft follow-ups

These are drafts only.

### 1. PO-S2607-820 identity reconciliation

**To:** Rowan Ames `<rowan.ames@northquayassembly.example>`; Beck Lin `<beck.lin@northquayassembly.example>`  
**Subject:** Reconcile unlisted SKU event on PO-S2607-820 for July

Please reconcile `RCV-K7105`, which records +12 of `NUT-M8` against PO-S2607-820 although that SKU is absent from the supplied order lines. Please confirm whether the event is mis-keyed or the order extract is missing a line, correct the mapping or packet as needed, and provide corrected July evidence. Until resolved, the observed BOLT-M8 net of 90/100 and WASHER-M8 net of 200/200 are not final positions.

### 2. Conflicting RCV-K7107 evidence

**To:** Rowan Ames `<rowan.ames@northquayassembly.example>`; Beck Lin `<beck.lin@northquayassembly.example>`  
**Subject:** Resolve conflicting July event RCV-K7107

`RCV-K7107` appears with different content: +18 PACK-RACK on PO-S2607-821 and +12 SHIELD-CLR on PO-S2607-822. Please establish the canonical event, assign distinct IDs if both transactions are real, and issue corrected July evidence. PACK-RACK and SHIELD-CLR must remain unconfirmed until then.

### 3. Incomplete POUCH-12 export

**To:** Beck Lin `<beck.lin@northquayassembly.example>`  
**Subject:** Complete July evidence for PO-S2607-823 / POUCH-12

The current extract is not declared complete. It shows a duplicate-adjusted observed net of 34 against 30 ordered (`RCV-K7110` +36 counted once and `RCV-K7111` -2). Please provide the missing July records or certify a corrected complete export so the final position can be determined.

### 4. Missing July TRAY-L coverage

**To:** Beck Lin `<beck.lin@northquayassembly.example>`  
**Subject:** Provide July coverage for PO-S2607-824 / TRAY-L

The packet contains only a June coverage declaration for this line. July events show an observed net of 9 against 18 ordered (`RCV-K7112` +12 and `RCV-K7113` -3). Please provide the July coverage declaration and any omitted July events before a final position is assigned.

### 5. Incomplete BINDER-B export

**To:** Beck Lin `<beck.lin@northquayassembly.example>`  
**Subject:** Complete July evidence for PO-S2607-825 / BINDER-B

The July export is marked incomplete and contains no event for BINDER-B. Please provide the missing July records or certify a corrected complete export. No receipt quantity can be inferred from the current absence of events.

### 6. INSERT-G excess

**To:** Inez Cole `<inez.cole@northquayassembly.example>`  
**Subject:** Reconcile five-unit July excess for PO-S2607-826 / INSERT-G

Complete July evidence supports a net receipt of 75 against 70 ordered after counting duplicate `RCV-K7114` once. Please verify the five-unit overage and record the appropriate warehouse disposition, such as acceptance, segregation, or return, through the normal process.

### 7. WRAP-500 shortfall

**To:** Felix Arun `<felix.arun@wrapline.example>`  
**Cc:** Rowan Ames `<rowan.ames@northquayassembly.example>`  
**Subject:** Resolve 22-unit July shortfall for PO-S2607-827 / WRAP-500

Complete July evidence supports a net receipt of 18 against 40 ordered. Please confirm whether the remaining 22 units will be delivered; otherwise provide corrected receipt/return evidence and the expected resolution date.

### 8. PAD-FOAM shortfall

**To:** Rafael Brooks `<rafael.brooks@cushionstock.example>`  
**Cc:** Rowan Ames `<rowan.ames@northquayassembly.example>`  
**Subject:** Resolve 16-unit July shortfall for PO-S2607-829 / PAD-FOAM

Complete July evidence shows +5 and -9, for a net of -4 against 12 ordered and therefore a 16-unit gap. Please reconcile the negative net and confirm replacement delivery or provide corrected reversal evidence and the expected resolution date.

### 9. CRATE-S shortfall

**To:** Elena Duarte `<elena.duarte@crateforge.example>`  
**Cc:** Rowan Ames `<rowan.ames@northquayassembly.example>`  
**Subject:** Resolve 16-unit July shortfall for PO-S2607-830 / CRATE-S

The complete July export contains no receipt events, supporting a net of 0 against 16 ordered. Please confirm delivery of all 16 units or provide corrected receipt evidence and the expected resolution date.

## Excluded events and unresolved limitations

- Prior-month events excluded from July totals: `RCV-K6990` (-10 INSERT-G), `RCV-K6991` (+7 INSERT-OLD), and `RCV-K6992` (+9 PAD-FOAM), all dated `2026-06`.
- `RCV-K7124` (+500 WRAP-500 on PO-S2607-899) is outside the supplied order set and does not affect any reviewed line.
- Final positions cannot be assigned to the two PO-S2607-820 lines until `RCV-K7105` is reconciled; to PACK-RACK or SHIELD-CLR until `RCV-K7107` is reconciled; or to POUCH-12, TRAY-L, or BINDER-B until complete July coverage is supplied.

