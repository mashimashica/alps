# July 2026 receiving review

Scope is the 13 supplied purchase-order lines for `2026-07`. July signed quantities are netted; exact repeated copies of an event count once; June events do not contribute to July subtotals. A complete export with no July events supports a zero subtotal, while an incomplete or missing July coverage declaration does not.

## Line judgments

| Purchase order / SKU | July evidence | Judgment |
|---|---:|---|
| `PO-S2607-820` / `BOLT-M8` | 70 + 30 − 10 = **90** of 100 | **Unresolved — identity reconciliation.** `RCV-K7105` records 12 units as `NUT-M8`, a SKU absent from this order. The apparent 10-unit shortfall is not final until the order’s event identities are reconciled. |
| `PO-S2607-820` / `WASHER-M8` | **200** of 200 | **Unresolved — identity reconciliation.** The same order-level `NUT-M8` mismatch prevents a final line comparison, even though the observed subtotal equals the order. |
| `PO-S2607-821` / `PACK-RACK` | 20 + disputed 18 = **38** of 48 | **Unresolved — conflicting evidence.** `RCV-K7107` is also attached to `PO-S2607-822 / SHIELD-CLR` with different contents. Do not treat the apparent 10-unit shortfall as final. |
| `PO-S2607-821` / `STRAP-20` | **60** of 60 | **Received as ordered.** No follow-up needed. |
| `PO-S2607-822` / `SHIELD-CLR` | 28 + disputed 12 = **40** of 40 | **Unresolved — conflicting evidence.** `RCV-K7107` conflicts with the `PACK-RACK` record, so the apparent match is not final. |
| `PO-S2607-823` / `POUCH-12` | 36 − 2 = **34** of 30; exact duplicate `RCV-K7110` counted once | **Unresolved — incomplete export.** The observed net is 4 over, but coverage is explicitly incomplete, so no excess judgment is supported yet. |
| `PO-S2607-824` / `TRAY-L` | 12 − 3 = **9** of 18 | **Unresolved — incomplete July export.** Coverage was supplied for June, not July. The apparent 9-unit shortfall is not final. |
| `PO-S2607-825` / `BINDER-B` | No July events observed | **Unresolved — incomplete export.** Coverage is explicitly incomplete; absence of events is not evidence of zero receipts. |
| `PO-S2607-826` / `INSERT-G` | 45 + 40 − 10 = **75** of 70; exact duplicate `RCV-K7114` counted once | **Unresolved — identity reconciliation.** The packet contains `INSERT-OLD` under the same order (`RCV-K6991`, June). The observed July net is 5 over, but no excess judgment is final until the source identity is reconciled. The June −10 event is also excluded from July. |
| `PO-S2607-827` / `WRAP-500` | 20 + 6 − 8 = **18** of 40 | **Shortfall: 22 units.** Complete July evidence supports supplier follow-up. |
| `PO-S2607-828` / `CLIP-R` | 6 + 4 = **10** of 10 | **Received as ordered.** No follow-up needed. |
| `PO-S2607-829` / `PAD-FOAM` | 5 − 9 = **−4** of 12 | **Shortfall: 16 units.** Complete July evidence supports supplier follow-up. The June receipt of 9 is outside the review month. |
| `PO-S2607-830` / `CRATE-S` | No July events; July coverage complete = **0** of 16 | **Shortfall: 16 units.** Complete July evidence supports supplier follow-up. |

`RCV-K7124` for `PO-S2607-899 / WRAP-500` (500 units) is outside the supplied order scope and is excluded from every subtotal and judgment.

## Follow-up drafts

**To Rowan Ames <rowan.ames@northquayassembly.example> and Beck Lin <beck.lin@northquayassembly.example> — `PO-S2607-820`, both supplied lines**

> Please reconcile `RCV-K7105`, which records 12 July units as `NUT-M8` under `PO-S2607-820` although that SKU is absent from the supplied order. Confirm the correct order/SKU assignment and provide the corrected source evidence before we finalize `BOLT-M8` or `WASHER-M8`. Current observed subtotals are 90/100 and 200/200, respectively, but neither is a final receipt judgment while this identity issue remains.

**To Rowan Ames <rowan.ames@northquayassembly.example> and Beck Lin <beck.lin@northquayassembly.example> — `RCV-K7107`**

> Please reconcile the conflicting copies of `RCV-K7107`: one identifies `PO-S2607-821 / PACK-RACK`, 18 units, and the other identifies `PO-S2607-822 / SHIELD-CLR`, 12 units. Confirm the authoritative event contents before either line is finalized. The current observed subtotals are 38/48 for `PACK-RACK` and 40/40 for `SHIELD-CLR`; both remain unresolved.

**To Beck Lin <beck.lin@northquayassembly.example> — `PO-S2607-823 / POUCH-12`**

> Please provide or confirm the complete July receipt export for this line. The current deduplicated net is 34 against 30 ordered, but the supplied coverage is incomplete, so we cannot finalize an excess judgment.

**To Beck Lin <beck.lin@northquayassembly.example> — `PO-S2607-824 / TRAY-L`**

> Please provide or confirm the complete July receipt export for this line. The packet declares coverage for June only; the current July net is 9 against 18 ordered and cannot support a final shortfall judgment without July coverage.

**To Beck Lin <beck.lin@northquayassembly.example> — `PO-S2607-825 / BINDER-B`**

> Please provide or confirm the complete July receipt export for this line. No July events are present and coverage is explicitly incomplete, so receipt quantity remains undetermined rather than zero.

**To Rowan Ames <rowan.ames@northquayassembly.example> and Beck Lin <beck.lin@northquayassembly.example> — `PO-S2607-826 / INSERT-G`**

> Please reconcile `RCV-K6991`, which uses `INSERT-OLD` under this order, and confirm the authoritative order/SKU identity before final comparison. The deduplicated July net for `INSERT-G` is 75 against 70 ordered, but the apparent 5-unit excess remains unresolved until the source identity issue is cleared.

**To Rowan Ames <rowan.ames@northquayassembly.example> — `PO-S2607-827 / WRAP-500`**

> Complete July evidence shows a net receipt of 18 against 40 ordered, a 22-unit shortfall. Please ask Felix Arun <felix.arun@wrapline.example> to confirm the disposition and expected receipt timing for the remaining 22 units.

**To Rowan Ames <rowan.ames@northquayassembly.example> — `PO-S2607-829 / PAD-FOAM`**

> Complete July evidence shows a net of −4 against 12 ordered after the July correcting reversal, a 16-unit shortfall. The June receipt is outside this review month. Please ask Rafael Brooks <rafael.brooks@cushionstock.example> to reconcile the July activity and confirm the disposition of the remaining 16 units.

**To Rowan Ames <rowan.ames@northquayassembly.example> — `PO-S2607-830 / CRATE-S`**

> Complete July coverage contains no receipt events, leaving 0 received against 16 ordered. Please ask Elena Duarte <elena.duarte@crateforge.example> to confirm the status and expected receipt timing for all 16 units.

**To Rowan Ames <rowan.ames@northquayassembly.example> and Beck Lin <beck.lin@northquayassembly.example> — excluded event**

> Please verify whether `RCV-K7124` for `PO-S2607-899 / WRAP-500`, 500 units, belongs in another order packet or reflects a source-key error. It was excluded because `PO-S2607-899` is not among the supplied purchase orders.

These are drafts only; no messages were sent and no receiving records were changed.
