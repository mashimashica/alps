# June 2026 receiving review

**Source:** `input/receiving.json`  
**Scope:** 6 supplied order records; 6 unique identifiable lines; 0 unresolved order records; 6 reported entries.

The complete evidence supports two received-as-ordered lines, two shortfalls, and one excess. The final position for `PO-R2606-413 / SEAL-BLUE` is withheld because its coverage declaration is partial.

| Order / SKU | Ordered | June observed net | Coverage | Final position | Evidence references | Responsible actor / recipient | Next action |
| --- | ---: | ---: | --- | --- | --- | --- | --- |
| `PO-R2606-410 / LABEL-60` | 120 | 120 | Complete | **Received as ordered** | `orders[0]`; `coverage[0]`; accepted `events[0]` +75, `events[1]` +50, `events[2]` −5. Exact copy `events[3]` excluded. | None required | No receipt follow-up needed. |
| `PO-R2606-410 / CARTON-M` | 80 | 42 | Complete | **Shortfall: 38** | `orders[1]`; `coverage[1]`; accepted `events[4]` +50, `events[5]` −8. May event `events[6]` excluded from June. | Dana Ivers <dana.ivers@juniperworks.example> / Mara Quinn <mara.quinn@harborpack.example> | Confirm the June receipt plan for the remaining 38 units. |
| `PO-R2606-411 / GLOVE-N` | 60 | 64 | Complete | **Excess: 4** | `orders[2]`; `coverage[2]`; accepted `events[7]` +66, `events[8]` −2. | Noel Price <noel.price@juniperworks.example> / Noel Price <noel.price@juniperworks.example> | Reconcile the 4-unit surplus against the order and receiving evidence. |
| `PO-R2606-412 / FILM-300` | 24 | 24 | Complete | **Received as ordered** | `orders[3]`; `coverage[3]`; accepted `events[9]` +24. July return `events[10]` excluded from June. | None required | No receipt follow-up needed. |
| `PO-R2606-413 / SEAL-BLUE` | 40 | 30 observed subtotal | Partial | **Withheld — incomplete evidence** | `orders[4]`; `coverage[4]`; accepted `events[11]` +35, `events[12]` −5. | Simone Bell <simone.bell@juniperworks.example> / Simone Bell <simone.bell@juniperworks.example> | Supply or confirm the full receiving export and an explicit coverage declaration for this line and month before final comparison. Do not treat the apparent 10-unit difference as a confirmed shortfall. |
| `PO-R2606-414 / TAPE-48` | 30 | 0 | Complete | **Shortfall: 30** | `orders[5]`; `coverage[5]`; no accepted June events. The affirmative complete coverage supports a final net of zero. | Dana Ivers <dana.ivers@juniperworks.example> / Owen Malik <owen.malik@bindwell.example> | Confirm the June receipt plan for the remaining 30 units. |

## Source-specific exclusions

- `events[3]` is an exact duplicate of `events[0]` and counts once.
- `events[6]` is from May 2026 and does not contribute to the June `CARTON-M` result.
- `events[10]` is from July 2026 and does not contribute to the June `FILM-300` result.
- `events[13]` belongs to outside order `PO-R2606-499` and does not contribute to this review.
- The processor reported no blocking source issues and no excluded coverage declarations. These event exclusions do not block the supported line judgments above.

## Follow-up drafts

**Draft — not sent**  
**To:** Mara Quinn <mara.quinn@harborpack.example>  
**Subject:** June 2026 receiving follow-up — PO-R2606-410 / CARTON-M

Hello Mara,

For June 2026, the complete receiving export for `PO-R2606-410 / CARTON-M` shows net received of 42 units against 80 ordered, leaving a confirmed shortfall of 38 units. Please confirm the receipt plan for the remaining 38 units.

Thank you,  
Dana Ivers

---

**Draft — not sent**  
**To:** Noel Price <noel.price@juniperworks.example>  
**Subject:** June 2026 receiving reconciliation — PO-R2606-411 / GLOVE-N

Hello Noel,

For June 2026, the complete receiving export for `PO-R2606-411 / GLOVE-N` shows net received of 64 units against 60 ordered, a surplus of 4 units. Please reconcile the 4-unit surplus against the purchase order and receiving evidence and report the outcome.

Thank you,  
Dana Ivers

---

**Draft — not sent**  
**To:** Simone Bell <simone.bell@juniperworks.example>  
**Subject:** June 2026 evidence request — PO-R2606-413 / SEAL-BLUE

Hello Simone,

For June 2026, `PO-R2606-413 / SEAL-BLUE` has 40 units ordered and a usable observed subtotal of 30 units from the supplied events, but its coverage declaration is partial. Please supply or confirm the full receiving export and provide an explicit coverage declaration for this order, SKU, and month so the final receipt position can be determined.

Thank you,  
Dana Ivers

---

**Draft — not sent**  
**To:** Owen Malik <owen.malik@bindwell.example>  
**Subject:** June 2026 receiving follow-up — PO-R2606-414 / TAPE-48

Hello Owen,

For June 2026, the complete receiving export for `PO-R2606-414 / TAPE-48` shows net received of 0 units against 30 ordered, leaving a confirmed shortfall of 30 units. Please confirm the receipt plan for the remaining 30 units.

Thank you,  
Dana Ivers

## Input needed to finish

The only unresolved line judgment is `PO-R2606-413 / SEAL-BLUE`. Finishing it requires the full June receiving export and an explicit coverage declaration for that exact order/SKU/month. All required contacts are supplied, so no routing detail is missing. The drafts above were prepared only and were not sent; no source or live receiving records were changed.

The deterministic machine report is available at [receipt-review.json](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U071/work/receipt-review.json).
