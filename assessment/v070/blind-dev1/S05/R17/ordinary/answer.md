# June 2026 receiving review

## Scope and basis

The review covers all six supplied purchase-order lines for **2026-06**. Only June events were included in net receipt totals; negative quantities were treated as returns/corrections, and the exact duplicate of `RCV-H1801` was counted once. Coverage declarations were used as evidence of completeness and did not remove any supplied line from scope.

## Line-by-line receipt position

| Order ID | SKU | Ordered | Evidence summary | Status / judgment | Evidence gaps | Follow-up |
|---|---|---:|---|---|---|---|
| `PO-R2606-410` | `LABEL-60` | 120 | Complete June evidence. `RCV-H1801` 75 + `RCV-H1802` 50 + `RCV-H1803` -5 = **120 net**. The repeated exact copy of `RCV-H1801` was excluded. | **Received as ordered**: net 120 equals 120 ordered. | None identified in the supplied evidence. | None needed. |
| `PO-R2606-410` | `CARTON-M` | 80 | Complete June evidence. `RCV-H1804` 50 + `RCV-H1805` -8 = **42 net**. May event `RCV-H1720` (20) is outside the review month and was excluded. | **Complete shortfall**: 42 received against 80 ordered; **38 remain**. | None identified in the supplied June evidence. | Draft to supplier contact **Mara Quinn <mara.quinn@harborpack.example>** about the remaining 38. |
| `PO-R2606-411` | `GLOVE-N` | 60 | Complete June evidence. `RCV-H1806` 66 + `RCV-H1807` -2 = **64 net**. | **Complete excess**: 64 received against 60 ordered; **4 surplus**. | None identified in the supplied evidence. | Draft to warehouse lead **Noel Price <noel.price@juniperworks.example>** to reconcile the 4-unit surplus. |
| `PO-R2606-412` | `FILM-300` | 24 | Complete June evidence. `RCV-H1808` = **24 net**. July event `RCV-H1901` (-4) is outside the review month and was excluded. | **Received as ordered**: net 24 equals 24 ordered. | None identified in the supplied June evidence. | None needed. |
| `PO-R2606-413` | `SEAL-BLUE` | 40 | Incomplete June evidence. `RCV-H1809` 35 + `RCV-H1810` -5 = **30 observed net**. | **Final position not established**. The observed subtotal is 30, but it is not evidence of a final 10-unit shortfall because coverage is incomplete. | The full June export has not been provided or confirmed. Additional receipts, returns, or corrections may be absent. | Draft to data steward **Simone Bell <simone.bell@juniperworks.example>** to provide or confirm the complete June export. |
| `PO-R2606-414` | `TAPE-48` | 30 | Complete June evidence with no qualifying receipt events; **0 net**. | **Complete shortfall**: 0 received against 30 ordered; **30 remain**. | None identified in the supplied evidence; the complete-coverage declaration supports the zero net position. | Draft to supplier contact **Owen Malik <owen.malik@bindwell.example>** about the remaining 30. |

## Other findings

- **Out of scope:** `RCV-H1811` (`PO-R2606-499`, `PALLET-STD`, quantity 90) belongs to an order outside the supplied order set. It was not folded into any reviewed line.
- **Identity reconciliation:** No event used an unexpected SKU for an in-scope order.
- **Conflicting event IDs:** None found. The two copies of `RCV-H1801` were identical, so they were treated as one event rather than a conflict.

## Draft follow-ups — not sent

### Mara Quinn <mara.quinn@harborpack.example>

**Subject:** PO-R2606-410 CARTON-M — 38 units remaining after June receipts

Hi Mara,

Our complete June 2026 receiving evidence for `PO-R2606-410`, `CARTON-M`, shows 42 units net received against 80 ordered: receipt `RCV-H1804` for 50 and correction/return `RCV-H1805` for -8. That leaves 38 units outstanding.

Please confirm whether the remaining 38 units will be shipped and the expected timing, or advise if the order or receipt documentation needs to be reconciled.

Thank you,

Dana Ivers

### Owen Malik <owen.malik@bindwell.example>

**Subject:** PO-R2606-414 TAPE-48 — 30 units remaining after June receipts

Hi Owen,

Our complete June 2026 receiving evidence for `PO-R2606-414`, `TAPE-48`, shows no qualifying receipt events against 30 units ordered. The full 30 units therefore remain outstanding for the June review.

Please confirm whether the 30 units will be shipped and the expected timing, or advise if the order or receipt documentation needs to be reconciled.

Thank you,

Dana Ivers

### Noel Price <noel.price@juniperworks.example>

**Subject:** Reconcile 4-unit receipt excess — PO-R2606-411 GLOVE-N

Hi Noel,

The complete June 2026 evidence for `PO-R2606-411`, `GLOVE-N`, shows 64 units net received against 60 ordered: `RCV-H1806` for 66 and `RCV-H1807` for -2. This leaves a 4-unit excess.

Please reconcile the 4-unit surplus against the purchase order and receiving evidence, confirm the correct receipt position, and identify any receiving-record correction or other disposition needed.

Thank you,

Dana Ivers

### Simone Bell <simone.bell@juniperworks.example>

**Subject:** Complete June export needed — PO-R2606-413 SEAL-BLUE

Hi Simone,

For `PO-R2606-413`, `SEAL-BLUE`, the supplied June evidence is marked incomplete. The events currently provided show 30 units net (`RCV-H1809` for 35 and `RCV-H1810` for -5) against 40 ordered, but the final receipt position cannot be established from an incomplete export.

Please provide the complete June 2026 export for this order line, including all receipts, returns, and corrections, or confirm that the supplied events are the full June export so the line can be finalized.

Thank you,

Dana Ivers

No messages were sent and no source records were changed.
