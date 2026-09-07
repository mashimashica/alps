# June 2026 receiving review

Only receipt events in June 2026 for the supplied purchase-order lines contribute to the observed totals. Negative quantities are applied algebraically. Exact duplicate copies are counted once; events from other months or orders outside the supplied order set are excluded.

## Line review

| Order ID | SKU | Ordered | Observed net | Event IDs | Coverage | Evidence flags | Supported position | Follow-up |
|---|---|---:|---:|---|---|---|---|---|
| PO-R2606-410 | LABEL-60 | 120 | 120 | RCV-H1801, RCV-H1802, RCV-H1803 | Complete | None; exact duplicate of RCV-H1801 counted once | `received_as_ordered` | None required |
| PO-R2606-410 | CARTON-M | 80 | 42 | RCV-H1804, RCV-H1805 | Complete | None | `shortfall` — 38 | Draft 1: supplier follow-up through Dana Ivers |
| PO-R2606-411 | GLOVE-N | 60 | 64 | RCV-H1806, RCV-H1807 | Complete | None | `excess` — 4 | Draft 2: warehouse reconciliation |
| PO-R2606-412 | FILM-300 | 24 | 24 | RCV-H1808 | Complete | None | `received_as_ordered` | None required |
| PO-R2606-413 | SEAL-BLUE | 40 | 30 observed subtotal | RCV-H1809, RCV-H1810 | Incomplete | Incomplete June export | `undetermined` — the observed subtotal is not a final receipt position | Draft 3: full-export request |
| PO-R2606-414 | TAPE-48 | 30 | 0 | None | Complete | None | `shortfall` — 30 | Draft 4: supplier follow-up through Dana Ivers |

Calculations:

- LABEL-60: 75 + 50 - 5 = 120. The repeated copy of RCV-H1801 is not counted again.
- CARTON-M: 50 - 8 = 42; 80 - 42 = 38 short.
- GLOVE-N: 66 - 2 = 64; 64 - 60 = 4 excess.
- SEAL-BLUE: 35 - 5 = 30 observed, but incomplete coverage prevents a final comparison with the ordered 40.
- TAPE-48: complete coverage and no applicable events support a net of 0; 30 remain unreceived.

## Follow-up drafts

### Draft 1 — CARTON-M shortfall

**From:** Dana Ivers, Purchasing Coordinator (`dana.ivers@juniperworks.example`)  
**To:** Mara Quinn, HarborPack (`mara.quinn@harborpack.example`)  
**Subject:** PO-R2606-410 / CARTON-M — confirm remaining 38 units

Hi Mara,

Our complete June receiving evidence for PO-R2606-410, SKU CARTON-M, shows a net receipt of 42 units against 80 ordered, leaving a shortfall of 38. The applicable events are RCV-H1804 (+50) and RCV-H1805 (-8).

Please confirm whether the remaining 38 units will be delivered. If so, please provide the expected delivery date; if not, please explain the variance and provide any supporting shipment or credit documentation so we can finish the receiving review.

Thanks,  
Dana

### Draft 2 — GLOVE-N excess

**From:** Dana Ivers, Purchasing Coordinator (`dana.ivers@juniperworks.example`)  
**To:** Noel Price, Warehouse Lead (`noel.price@juniperworks.example`)  
**Subject:** PO-R2606-411 / GLOVE-N — reconcile 4-unit excess

Hi Noel,

The complete June evidence for PO-R2606-411, SKU GLOVE-N, shows 64 units received against 60 ordered, an excess of 4. The applicable events are RCV-H1806 (+66) and RCV-H1807 (-2).

Please reconcile the 4-unit surplus against the purchase order and receiving evidence, verify the event quantities, and confirm the correction or disposition needed to close the line.

Thanks,  
Dana

### Draft 3 — SEAL-BLUE incomplete export

**From:** Dana Ivers, Purchasing Coordinator (`dana.ivers@juniperworks.example`)  
**To:** Simone Bell, Data Steward (`simone.bell@juniperworks.example`)  
**Subject:** PO-R2606-413 / SEAL-BLUE — complete June receipt export needed

Hi Simone,

The supplied June export for PO-R2606-413, SKU SEAL-BLUE, is marked incomplete. It currently shows an observed subtotal of 30 units against 40 ordered from RCV-H1809 (+35) and RCV-H1810 (-5), so the final receipt position is undetermined.

Please provide the complete June export for this order line, or confirm that the supplied events are the full June record and correct the coverage declaration. Please also identify any missing event IDs or quantities so we can determine the final position.

Thanks,  
Dana

### Draft 4 — TAPE-48 shortfall

**From:** Dana Ivers, Purchasing Coordinator (`dana.ivers@juniperworks.example`)  
**To:** Owen Malik, Bindwell (`owen.malik@bindwell.example`)  
**Subject:** PO-R2606-414 / TAPE-48 — confirm remaining 30 units

Hi Owen,

Our complete June receiving evidence for PO-R2606-414, SKU TAPE-48, contains no applicable receipt event IDs and therefore shows 0 units received against 30 ordered, leaving a shortfall of 30.

Please confirm whether all 30 units will be delivered. If so, please provide the expected delivery date; if not, please explain the variance and provide any supporting shipment or credit documentation so we can finish the receiving review.

Thanks,  
Dana

## Excluded events

| Event ID | Reason excluded | Quantity |
|---|---|---:|
| RCV-H1720 | May 2026 event; outside the requested June 2026 month | +20 |
| RCV-H1901 | July 2026 event; outside the requested June 2026 month | -4 |
| RCV-H1811 | PO-R2606-499 / PALLET-STD is outside the supplied order set | +90 |

## Global evidence issues

There are no unresolved event-ID conflicts and no order/event identity issues. The sole evidence limitation is the line-specific incomplete coverage for PO-R2606-413 / SEAL-BLUE described above.

These are drafts only. No messages were sent and no source records were changed.
