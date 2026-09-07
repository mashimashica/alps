# July 2026 receiving review

Source: `input/receiving.json`  
Scope: 13 supplied order records, 13 unique identifiable lines, no invalid or unresolved order records.

Of the 13 lines, the evidence supports six final positions: two received as ordered, one excess, and three shortfalls. Three lines have partial or missing July coverage, and four are blocked by event identity problems. Those seven lines do not support a final receipt comparison.

## Line review

| Order / SKU | Ordered | July receipt evidence | Coverage | Judgment | Evidence references | Responsible actor / recipient | Next action |
| --- | ---: | --- | --- | --- | --- | --- | --- |
| PO-S2607-820 / BOLT-M8 | 100 | Usable-event subtotal **90**: 70 + 30 - 10. This cannot be described as the full observed net while the order-level identity issue remains. | Complete | **Withheld — blocked evidence.** The current-month NUT-M8 event on this order has no supplied line, so identity reconciliation blocks every line on PO-S2607-820. | `orders[0]`; `events[0]`, `[1]`, `[2]`; `coverage[0]`; issue I-1 at `events[4]` | Rowan Ames and Beck Lin / Rowan Ames and Beck Lin | Reconcile `events[4]` and provide corrected identity/export evidence before comparison. |
| PO-S2607-820 / WASHER-M8 | 200 | Usable-event subtotal **200**. This cannot be described as the full observed net while the order-level identity issue remains. | Complete | **Withheld — blocked evidence.** The same unknown-SKU event blocks all lines on this order. | `orders[1]`; `events[3]`; `coverage[1]`; issue I-1 at `events[4]` | Rowan Ames and Beck Lin / Rowan Ames and Beck Lin | Reconcile `events[4]` and provide corrected identity/export evidence before comparison. |
| PO-S2607-821 / PACK-RACK | 48 | Usable-event subtotal **20**. Neither RCV-K7107 variant contributes. | Complete | **Withheld — blocked evidence.** RCV-K7107 has conflicting contents. | `orders[2]`; accepted `events[5]`; `coverage[2]`; issue I-2 at `events[6]`, `[8]` | Rowan Ames and Beck Lin / Rowan Ames and Beck Lin | Reconcile both RCV-K7107 source records and provide corrected evidence. |
| PO-S2607-821 / STRAP-20 | 60 | Final net **60**. | Complete | **Received as ordered.** No receipt follow-up is needed. | `orders[3]`; `events[9]`; `coverage[3]` | None / none | No receipt follow-up. |
| PO-S2607-822 / SHIELD-CLR | 40 | Usable-event subtotal **28**. Neither RCV-K7107 variant contributes. | Complete | **Withheld — blocked evidence.** RCV-K7107 has conflicting contents. | `orders[4]`; accepted `events[7]`; `coverage[4]`; issue I-3 at `events[6]`, `[8]` | Rowan Ames and Beck Lin / Rowan Ames and Beck Lin | Reconcile both RCV-K7107 source records and provide corrected evidence. |
| PO-S2607-823 / POUCH-12 | 30 | Observed net **34**: 36 - 2. Exact duplicate `events[12]` counted once. | Partial | **Withheld — incomplete evidence.** The subtotal is not a supported excess judgment. | `orders[5]`; `events[10]`, `[11]`; `coverage[5]`; duplicate `events[12]` excluded | Beck Lin / Beck Lin | Supply or confirm the full July export and an explicit coverage declaration before comparison. |
| PO-S2607-824 / TRAY-L | 18 | Observed net **9**: 12 - 3. | Missing | **Withheld — incomplete evidence.** The only coverage declaration is for June. | `orders[6]`; `events[13]`, `[14]`; issue I-4; June-only `coverage[6]` excluded | Beck Lin / Beck Lin | Supply or confirm the full July export and an explicit July coverage declaration. |
| PO-S2607-825 / BINDER-B | 25 | Observed subtotal **0** from the supplied partial export; this does not establish that nothing was received. | Partial | **Withheld — incomplete evidence.** | `orders[7]`; no accepted events; `coverage[7]` | Beck Lin / Beck Lin | Supply or confirm the full July export and an explicit coverage declaration before comparison. |
| PO-S2607-826 / INSERT-G | 70 | Final net **75**: 45 + 40 - 10. Exact duplicate `events[16]` counted once. | Complete | **Excess of 5.** | `orders[8]`; `events[15]`, `[17]`, `[18]`; `coverage[8]`; duplicate `events[16]` excluded | Inez Cole / Inez Cole | Reconcile the 5-unit surplus against the order and receiving evidence. |
| PO-S2607-827 / WRAP-500 | 40 | Final net **18**: 20 + 6 - 8. | Complete | **Shortfall of 22.** | `orders[9]`; `events[21]`, `[22]`, `[23]`; `coverage[9]` | Rowan Ames / Felix Arun | Confirm the receipt plan for the remaining 22 units. |
| PO-S2607-828 / CLIP-R | 10 | Final net **10**: 6 + 4. | Complete | **Received as ordered.** No receipt follow-up is needed. | `orders[10]`; `events[24]`, `[25]`; `coverage[10]` | None / none | No receipt follow-up. |
| PO-S2607-829 / PAD-FOAM | 12 | Final net **-4**: 5 - 9. | Complete | **Shortfall of 16.** The negative net means July returns/corrections exceed July receipts by four units. | `orders[11]`; `events[27]`, `[28]`; `coverage[11]` | Rowan Ames / Rafael Brooks | Confirm the receipt plan for the remaining 16 units. |
| PO-S2607-830 / CRATE-S | 16 | Final net **0** from a valid empty event list. | Complete | **Shortfall of 16.** | `orders[12]`; no accepted events; `coverage[12]` | Rowan Ames / Elena Duarte | Confirm the receipt plan for the remaining 16 units. |

## Source issues and exclusions

- `events[4]` records 12 units of NUT-M8 against PO-S2607-820, but NUT-M8 is not a supplied line for that order. Because it is a current-month unknown SKU, it blocks the final comparison for both BOLT-M8 and WASHER-M8.
- Event ID RCV-K7107 is reused with different contents in `events[6]` and `events[8]`. Neither variant contributes. This blocks PACK-RACK on PO-S2607-821 and SHIELD-CLR on PO-S2607-822. It does not affect STRAP-20 on PO-S2607-821.
- POUCH-12 and BINDER-B have partial July coverage. TRAY-L has no July coverage declaration; its `coverage[6]` declaration is for June and is excluded.
- Exact duplicate events `events[12]` and `events[16]` were excluded, so they were not double-counted.
- Prior-month events `events[19]`, `[20]`, and `[26]` were excluded. The outside-order event `events[29]` for PO-S2607-899 was also excluded. These records do not block any in-scope line.

## Follow-up drafts

### Evidence identity reconciliation

**Draft — not sent**  
**To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** July 2026 receiving review — event identity reconciliation

Please reconcile the following source records and provide corrected identities or corrected export evidence before final receipt comparisons:

- PO-S2607-820 / BOLT-M8, ordered 100: usable-event subtotal 90 from `events[0]`–`[2]`, but `events[4]` records 12 units for unknown SKU NUT-M8 on the same order. No final net or remaining quantity is established.
- PO-S2607-820 / WASHER-M8, ordered 200: usable-event subtotal 200 from `events[3]`, but the same `events[4]` order-level identity issue blocks the line. No final position is established.
- PO-S2607-821 / PACK-RACK, ordered 48: usable-event subtotal 20 from `events[5]`; RCV-K7107 conflicts between `events[6]` and `[8]`, so neither variant contributes. No final net or remaining quantity is established.
- PO-S2607-822 / SHIELD-CLR, ordered 40: usable-event subtotal 28 from `events[7]`; the same RCV-K7107 conflict blocks the line. No final net or remaining quantity is established.

Please identify the correct order/SKU for `events[4]`, resolve which RCV-K7107 record is valid, and return corrected evidence for the July review.

### Coverage completion

**Draft — not sent**  
**To:** Beck Lin <beck.lin@northquayassembly.example>  
**Subject:** July 2026 receiving review — coverage needed for three lines

Please supply or confirm the full July 2026 receiving export and an explicit coverage declaration for each of these lines before final comparison:

- PO-S2607-823 / POUCH-12, ordered 30: the partial export shows observed net 34 (36 - 2). This is not yet an excess judgment.
- PO-S2607-824 / TRAY-L, ordered 18: the supplied events show observed net 9 (12 - 3), but July coverage is missing; the supplied declaration is for June.
- PO-S2607-825 / BINDER-B, ordered 25: the partial export shows an observed subtotal of 0. This does not establish a 25-unit shortfall.

Please provide the complete export and line-specific July coverage confirmations so the final positions can be calculated.

### Surplus reconciliation

**Draft — not sent**  
**To:** Inez Cole <inez.cole@northquayassembly.example>  
**Subject:** July 2026 receiving review — PO-S2607-826 / INSERT-G surplus

For July 2026, PO-S2607-826 / INSERT-G was ordered for 70 units. Complete evidence shows a net 75 received (45 + 40 - 10), after counting the exact duplicate only once, for an excess of 5 units. Please reconcile the 5-unit surplus against the purchase order and receiving evidence and report the disposition.

### Supplier receipt plans

**Draft — not sent**  
**To:** Felix Arun <felix.arun@wrapline.example>  
**Subject:** July 2026 receiving review — PO-S2607-827 / WRAP-500

For July 2026, complete evidence for PO-S2607-827 / WRAP-500 shows net received of 18 units against 40 ordered, including the 8-unit return/correction, leaving a shortfall of 22 units. Please confirm the receipt plan for the remaining 22 units.

**Draft — not sent**  
**To:** Rafael Brooks <rafael.brooks@cushionstock.example>  
**Subject:** July 2026 receiving review — PO-S2607-829 / PAD-FOAM

For July 2026, complete evidence for PO-S2607-829 / PAD-FOAM shows net received of -4 units against 12 ordered (5 received and a 9-unit return/correction), leaving 16 units remaining. Please confirm the receipt plan for the remaining 16 units.

**Draft — not sent**  
**To:** Elena Duarte <elena.duarte@crateforge.example>  
**Subject:** July 2026 receiving review — PO-S2607-830 / CRATE-S

For July 2026, complete evidence for PO-S2607-830 / CRATE-S shows net received of 0 units against 16 ordered, leaving a shortfall of 16 units. Please confirm the receipt plan for the remaining 16 units.

## Inputs needed to finish

Final judgments require corrected identity evidence for `events[4]`, corrected evidence for the two RCV-K7107 variants in `events[6]` and `[8]`, and complete July exports with explicit coverage declarations for POUCH-12, TRAY-L, and BINDER-B. All responsibility names and contacts needed to route the drafts were supplied. The messages above are drafts only; none was sent and no receiving record was changed.

Machine-readable report: `work/receipt-review.json`.
