# July 2026 receiving review

## Review outcome

The supplied scope contains 13 purchase-order lines. July evidence supports final positions for six: two were received as ordered, three have shortfalls, and one has an excess. Seven lines do not support a final position because source identity or July-export completeness is unresolved.

Signed July quantities are netted algebraically; exact duplicate records are counted once. June records and the event for out-of-scope `PO-S2607-899` are excluded. “Observed” below describes what the supplied July records show; it is not a final receipt position where the evidence status is unresolved.

| Order / SKU | Ordered | Observed July net | Evidence status | Supported position | Gap, effect, and next action |
|---|---:|---:|---|---|---|
| `PO-S2607-820` / `BOLT-M8` | 100 | 90 | Identity conflict | Unavailable | The matched records net to 70 + 30 − 10. The same PO also has a July event for absent SKU `NUT-M8` (12), so line identity must be reconciled before comparison. Rowan Ames and Beck Lin should reconcile the PO/SKU source records. |
| `PO-S2607-820` / `WASHER-M8` | 200 | 200 | Identity conflict | Unavailable | The matched record totals 200, but the `NUT-M8` event on this PO prevents a final line judgment. Rowan Ames and Beck Lin should reconcile the PO/SKU source records. |
| `PO-S2607-821` / `PACK-RACK` | 48 | 38 recorded, including disputed 18 | Conflicting event evidence | Unavailable | `RCV-K7107` identifies both this line for 18 and `PO-S2607-822 / SHIELD-CLR` for 12. Rowan Ames and Beck Lin should establish the valid event record before either affected line is compared. |
| `PO-S2607-821` / `STRAP-20` | 60 | 60 | Complete | **Received as ordered** | No evidence gap or follow-up needed. |
| `PO-S2607-822` / `SHIELD-CLR` | 40 | 28 undisputed; a further 12 is disputed | Conflicting event evidence | Unavailable | `RCV-K7107` conflicts with the record attributed to `PACK-RACK`. Rowan Ames and Beck Lin should establish the valid event record before final comparison. |
| `PO-S2607-823` / `POUCH-12` | 30 | 34 observed subtotal | Incomplete export | Unavailable | Exact duplicate `RCV-K7110` is counted once, giving 36 − 2 = 34, but coverage is explicitly incomplete. Beck Lin should provide or confirm the full July export; apparent excess must not be treated as final. |
| `PO-S2607-824` / `TRAY-L` | 18 | 9 observed subtotal | Incomplete export | Unavailable | July events net to 12 − 3 = 9, but the only coverage declaration is for June. Beck Lin should provide or confirm complete July coverage; apparent shortfall must not be treated as final. |
| `PO-S2607-825` / `BINDER-B` | 25 | Not supportable | Incomplete export | Unavailable | Coverage is explicitly incomplete and there are no supplied July events. The absence of events is not evidence of zero receipts. Beck Lin should provide or confirm the full July export. |
| `PO-S2607-826` / `INSERT-G` | 70 | 75 | Complete | **Excess of 5** | Exact duplicate `RCV-K7114` is counted once: 45 + 40 − 10 = 75. June events are excluded. Inez Cole should reconcile the five-unit surplus against the order and receiving records. |
| `PO-S2607-827` / `WRAP-500` | 40 | 18 | Complete | **Shortfall of 22** | July net is 20 + 6 − 8 = 18. Felix Arun should confirm and arrange receipt of the remaining 22. |
| `PO-S2607-828` / `CLIP-R` | 10 | 10 | Complete | **Received as ordered** | No evidence gap or follow-up needed. |
| `PO-S2607-829` / `PAD-FOAM` | 12 | −4 | Complete | **Shortfall of 16** | The June receipt of 9 is outside this review. July nets to 5 − 9 = −4, so the algebraic gap to 12 is 16. Rafael Brooks should confirm and arrange receipt of the remaining 16 and account for the July return. |
| `PO-S2607-830` / `CRATE-S` | 16 | 0 | Complete | **Shortfall of 16** | Complete July coverage with no July events supports a zero subtotal. Elena Duarte should confirm and arrange receipt of all 16. |

## Follow-up drafts

These are drafts only; nothing has been sent and no receiving record has been changed.

**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** Reconcile July SKU identity on PO-S2607-820

Please reconcile the July source records for `PO-S2607-820`. The supplied events show `BOLT-M8` net 90 and `WASHER-M8` net 200, but event `RCV-K7105` is assigned to `NUT-M8`, a SKU absent from the supplied PO lines. Please confirm the intended order line or correct the source identity, then provide the reconciled evidence so both line positions can be finalized.

**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** Resolve conflicting July event RCV-K7107

Please establish the valid source record for `RCV-K7107`. It appears once as 18 units for `PO-S2607-821 / PACK-RACK` and again as 12 units for `PO-S2607-822 / SHIELD-CLR`. Until its correct order, SKU, and quantity are confirmed, neither affected line has a defensible final position. Please return the corrected or authoritative event evidence for both lines.

**To:** Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** Complete July receiving coverage for three PO lines

Please provide or confirm the full July 2026 receiving export for:

- `PO-S2607-823 / POUCH-12`: supplied records net to an observed 34, but coverage is marked incomplete.
- `PO-S2607-824 / TRAY-L`: supplied July records net to an observed 9, but the coverage declaration supplied is for June rather than July.
- `PO-S2607-825 / BINDER-B`: coverage is marked incomplete and no July events were supplied; this cannot be interpreted as zero received.

Please include any omitted receipts, returns, or reversals and confirm July completeness so final positions can be calculated.

**To:** Inez Cole <inez.cole@northquayassembly.example>  
**Subject:** Reconcile five-unit July excess for PO-S2607-826 / INSERT-G

Complete July evidence nets to 75 units against 70 ordered after counting duplicate `RCV-K7114` once and applying the July reversal. Please reconcile the five-unit surplus against the PO and warehouse receiving records and advise the disposition or correction needed.

**To:** Felix Arun <felix.arun@wrapline.example>  
**Subject:** Confirm 22-unit shortfall for PO-S2607-827 / WRAP-500

Complete July evidence nets to 18 units against 40 ordered, leaving a shortfall of 22 after the July return. Please confirm the balance and arrange receipt of the remaining 22 units, or provide the relevant fulfillment details.

**To:** Rafael Brooks <rafael.brooks@cushionstock.example>  
**Subject:** Confirm July balance for PO-S2607-829 / PAD-FOAM

Complete July evidence nets to −4 units against 12 ordered: a July receipt of 5 and return of 9. The June receipt is outside this monthly review. Please confirm the resulting 16-unit July balance, account for the return, and arrange the remaining receipt or provide the relevant fulfillment details.

**To:** Elena Duarte <elena.duarte@crateforge.example>  
**Subject:** Confirm 16-unit shortfall for PO-S2607-830 / CRATE-S

The packet declares complete July coverage and contains no July receiving events for the 16 units ordered. Please confirm the shortfall and arrange receipt of all 16 units, or provide the relevant fulfillment details.

This review is based only on the supplied packet and the skill processor’s output. The component/script check used here does not establish that every future agent will use the skill effectively.
