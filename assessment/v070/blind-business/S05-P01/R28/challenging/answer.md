# July 2026 receiving review

**Coordinator:** Rowan Ames <rowan.ames@northquayassembly.example>  
**Scope:** All 13 supplied purchase-order lines. The input was structurally valid; there are no invalid order rows and no missing recipient details.

## Receipt position

`Observed net` is the signed subtotal of accepted July events, so returns and reversals reduce it. A remaining or excess quantity is shown only where complete, unblocked evidence supports a final comparison.

| Order | SKU | Ordered | Accepted July events | Observed net | Coverage | Supported position | Final difference |
| --- | --- | ---: | --- | ---: | --- | --- | ---: |
| PO-S2607-820 | BOLT-M8 | 100 | RCV-K7101, RCV-K7102, RCV-K7103 | 90 | Complete | **Blocked** — unknown July SKU on this order | — |
| PO-S2607-820 | WASHER-M8 | 200 | RCV-K7104 | 200 | Complete | **Blocked** — unknown July SKU on this order | — |
| PO-S2607-821 | PACK-RACK | 48 | RCV-K7106 | 20 | Complete | **Blocked** — conflicting event ID excluded | — |
| PO-S2607-821 | STRAP-20 | 60 | RCV-K7109 | 60 | Complete | **Received as ordered** | 0 |
| PO-S2607-822 | SHIELD-CLR | 40 | RCV-K7108 | 28 | Complete | **Blocked** — conflicting event ID excluded | — |
| PO-S2607-823 | POUCH-12 | 30 | RCV-K7110, RCV-K7111 | 34 | Partial | **Not final** — observed subtotal only | — |
| PO-S2607-824 | TRAY-L | 18 | RCV-K7112, RCV-K7113 | 9 | Missing for July | **Not final** — observed subtotal only | — |
| PO-S2607-825 | BINDER-B | 25 | None | 0 | Partial | **Not final** — observed subtotal only | — |
| PO-S2607-826 | INSERT-G | 70 | RCV-K7114, RCV-K7115, RCV-K7116 | 75 | Complete | **Excess** | 5 excess |
| PO-S2607-827 | WRAP-500 | 40 | RCV-K7117, RCV-K7118, RCV-K7119 | 18 | Complete | **Shortfall** | 22 remaining |
| PO-S2607-828 | CLIP-R | 10 | RCV-K7120, RCV-K7121 | 10 | Complete | **Received as ordered** | 0 |
| PO-S2607-829 | PAD-FOAM | 12 | RCV-K7122, RCV-K7123 | -4 | Complete | **Shortfall** | 16 remaining |
| PO-S2607-830 | CRATE-S | 16 | None | 0 | Complete | **Shortfall** | 16 remaining |

## Evidence gaps and exclusions

- **PO-S2607-820, both lines:** July event record 4, `RCV-K7105`, names unknown SKU `NUT-M8` on the order. It blocks final comparison for both BOLT-M8 and WASHER-M8, even though their accepted subtotals are 90 and 200.
- **PO-S2607-821 PACK-RACK and PO-S2607-822 SHIELD-CLR:** `RCV-K7107` is reused with conflicting contents in event records 6 and 8 (18 PACK-RACK versus 12 SHIELD-CLR). Both variants are excluded, so neither line has a final comparison.
- **PO-S2607-823 POUCH-12:** coverage is explicitly partial. The subtotal is 34 after counting exact duplicate `RCV-K7110` once and applying the -2 return, but it cannot support an excess judgment yet.
- **PO-S2607-824 TRAY-L:** the only coverage declaration is for June and is ignored for this July review. The July subtotal is 9, but July coverage is missing.
- **PO-S2607-825 BINDER-B:** partial coverage and no accepted events support only a subtotal of 0. They do not establish zero final receipts or a 25-unit shortfall.
- Exact duplicate `RCV-K7114` was counted once. June events `RCV-K6990`, `RCV-K6991`, and `RCV-K6992` do not contribute to July. Out-of-scope order event `RCV-K7124` also does not contribute.

## Follow-up drafts

These are drafts only; no message was sent and no receiving record was changed.

### 1. Reconcile PO-S2607-820 receiving identity

**Owner/recipients:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
**Next action:** Identify whether `RCV-K7105` belongs to a supplied PO-S2607-820 line or whether the order scope is incomplete; correct the source identity, confirm the order quantities and event mappings, then rerun the review.

> **To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
> **Subject:** July 2026 receiving identity — PO-S2607-820  
>  
> July event RCV-K7105 identifies SKU NUT-M8 on PO-S2607-820, but that SKU is not among the supplied order lines. This blocks final comparison for BOLT-M8 (accepted subtotal 90 against 100 ordered) and WASHER-M8 (accepted subtotal 200 against 200 ordered). Please reconcile the event-to-line identity and supplied order scope, confirm the order quantities and mappings, and provide the corrected source records so the July review can be rerun.

### 2. Reconcile conflicting event RCV-K7107

**Owner/recipients:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
**Next action:** Determine the correct line and quantity for `RCV-K7107`, correct the source records, and rerun the review.

> **To:** Rowan Ames <rowan.ames@northquayassembly.example>; Beck Lin <beck.lin@northquayassembly.example>  
> **Subject:** July 2026 conflicting receiving event — RCV-K7107  
>  
> Event ID RCV-K7107 appears with conflicting July contents: 18 units for PO-S2607-821 / PACK-RACK and 12 units for PO-S2607-822 / SHIELD-CLR. Both variants were excluded. The accepted subtotals are therefore 20 for PACK-RACK against 48 ordered and 28 for SHIELD-CLR against 40 ordered, with neither comparison final. Please identify the correct event line and quantity, correct the source records, and provide them for a rerun.

### 3. Complete the POUCH-12 export

**Owner/recipient:** Beck Lin <beck.lin@northquayassembly.example>  
**Next action:** Provide the full July event export and a complete coverage declaration for this line.

> **To:** Beck Lin <beck.lin@northquayassembly.example>  
> **Subject:** July 2026 full export needed — PO-S2607-823 / POUCH-12  
>  
> Coverage is partial for PO-S2607-823 / POUCH-12. The accepted-event subtotal is 34 against 30 ordered after the exact duplicate receipt was counted once, but no final excess judgment is supported. Please provide or confirm the full July event export and an explicit complete coverage declaration, then rerun the review.

### 4. Complete the TRAY-L export

**Owner/recipient:** Beck Lin <beck.lin@northquayassembly.example>  
**Next action:** Provide the full July event export and July coverage declaration for this line.

> **To:** Beck Lin <beck.lin@northquayassembly.example>  
> **Subject:** July 2026 coverage needed — PO-S2607-824 / TRAY-L  
>  
> PO-S2607-824 / TRAY-L has an accepted July subtotal of 9 against 18 ordered, but its supplied coverage declaration applies to June. Please provide or confirm the full July event export and an explicit complete July coverage declaration, then rerun the review.

### 5. Complete the BINDER-B export

**Owner/recipient:** Beck Lin <beck.lin@northquayassembly.example>  
**Next action:** Provide the full July event export and a complete coverage declaration for this line.

> **To:** Beck Lin <beck.lin@northquayassembly.example>  
> **Subject:** July 2026 full export needed — PO-S2607-825 / BINDER-B  
>  
> Coverage is partial for PO-S2607-825 / BINDER-B, and there are no accepted July events, producing an observed subtotal of 0 against 25 ordered. This does not establish zero final receipts. Please provide or confirm the full July event export and an explicit complete coverage declaration, then rerun the review.

### 6. Reconcile the INSERT-G surplus

**Owner/recipient:** Inez Cole <inez.cole@northquayassembly.example>  
**Next action:** Reconcile the five-unit surplus and report its cause and proposed correction or disposition.

> **To:** Inez Cole <inez.cole@northquayassembly.example>  
> **Subject:** July 2026 receiving surplus — PO-S2607-826 / INSERT-G  
>  
> Complete July evidence shows 75 net units received against 70 ordered for PO-S2607-826 / INSERT-G, after the return and exact-duplicate handling, leaving a surplus of 5. Please reconcile the surplus against the order and receiving evidence and report the cause and proposed correction or disposition.

### 7. Confirm the WRAP-500 balance

**Owner:** Rowan Ames <rowan.ames@northquayassembly.example>  
**Recipient:** Felix Arun <felix.arun@wrapline.example>  
**Next action:** Ask the supplier for the status and expected receipt date of the remaining 22 units and the next receiving action.

> **To:** Felix Arun <felix.arun@wrapline.example>  
> **Subject:** July 2026 receiving balance — PO-S2607-827 / WRAP-500  
>  
> Complete July evidence shows 18 net units received against 40 ordered for PO-S2607-827 / WRAP-500. Please confirm the status and expected receipt date of the remaining 22 units and the next receiving action.

### 8. Confirm the PAD-FOAM balance

**Owner:** Rowan Ames <rowan.ames@northquayassembly.example>  
**Recipient:** Rafael Brooks <rafael.brooks@cushionstock.example>  
**Next action:** Ask the supplier for the status and expected receipt date of the remaining 16 units and the next receiving action.

> **To:** Rafael Brooks <rafael.brooks@cushionstock.example>  
> **Subject:** July 2026 receiving balance — PO-S2607-829 / PAD-FOAM  
>  
> Complete July evidence shows a net receipt of -4 against 12 ordered for PO-S2607-829 / PAD-FOAM: the July receipt of 5 less the July return of 9. The June receipt does not contribute to July. Please confirm the status and expected receipt date of the remaining 16 units and the next receiving action.

### 9. Confirm the CRATE-S balance

**Owner:** Rowan Ames <rowan.ames@northquayassembly.example>  
**Recipient:** Elena Duarte <elena.duarte@crateforge.example>  
**Next action:** Ask the supplier for the status and expected receipt date of all 16 remaining units and the next receiving action.

> **To:** Elena Duarte <elena.duarte@crateforge.example>  
> **Subject:** July 2026 receiving balance — PO-S2607-830 / CRATE-S  
>  
> Complete July coverage and no accepted July events establish 0 net units received against 16 ordered for PO-S2607-830 / CRATE-S. Please confirm the status and expected receipt date of the remaining 16 units and the next receiving action.

The review’s limitation is confined to the seven lines marked **Blocked** or **Not final**: their final receipt positions must wait for corrected identity evidence or complete July exports. The other six lines have supported final positions.
