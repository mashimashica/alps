---
name: receiving-review
description: Review a month's supplied purchase-order lines and receiving evidence, determine supported receipt positions, expose evidence gaps, and draft recipient-specific follow-ups without sending or changing records. Use when the input contains the monthly orders, receipt events, coverage declarations, and responsibility contacts for this review.
---

# Monthly Receiving Review

Use the bundled processor for repeatable arithmetic and evidence checks, then interpret its result and complete the review. The input is one JSON object containing `month` (`YYYY-MM`), `orders`, `events`, `coverage`, and `responsibilities`. Run:

```bash
python3 scripts/review_receipts.py input.json > review.json
```

The JSON output has `lines`, `follow_ups`, `issues`, and `validation_errors`. Treat validation errors as a failed review input, not as a zero or an empty value. The processor is advisory evidence processing: the agent remains responsible for checking scope, explaining judgments, and presenting a usable review.

## Required interpretation

- The review scope is every supplied order line for the requested month. A coverage declaration does not remove a line from scope.
- Identify a line by `(order_id, sku)`. Ordered quantities must be positive integers. A current-month event for an in-scope order with a SKU absent from that order is an identity-reconciliation issue; do not use it in a final line comparison.
- Count an exact repeated copy of an event once. If one `event_id` has different content, mark the affected evidence as conflicting and do not claim a final comparison for it. Events from another month do not contribute. Events for orders outside the supplied order set are outside this review.
- Use the supplied coverage declaration for the line and month as evidence of completeness. Do not infer completeness from row counts. Missing coverage, incomplete coverage, invalid coverage, conflicting identity, or conflicting event content limits the affected judgment; never substitute zero for missing information.
- For valid, complete evidence only, compare net current-month received quantity (signed quantities algebraically) with ordered quantity: equal = received as ordered; lower = complete shortfall; higher = complete excess. For incomplete evidence, report the observed subtotal only and explicitly say that final receipt position is undetermined.
- Every unresolved line needs a concrete drafted follow-up and recipient: supplier contact for a complete shortfall; warehouse lead for a complete excess; data steward for incomplete export; purchasing coordinator plus data steward for order/event identity or event-content conflict. Use only supplied responsibility values; never invent contact details. Do not send drafts or alter receiving records.

## Review response

Present each line with order ID, SKU, ordered quantity, evidence status, observed/net quantity when supported, supported position (or why it is undetermined), evidence issues, and the next action. Include the applicable evidence (orders, event IDs/month filtering, coverage) so another reviewer can trace the judgment. Include all follow-up drafts and their recipients, including drafts requesting the full export or source reconciliation. State that the processor and component checks do not establish that every future review will be interpreted effectively by an agent.

## Verification

Before relying on a run, inspect `validation_errors` and `issues`, and test representative complete, shortfall, excess, incomplete, return, out-of-month, unknown-order, SKU-mismatch, exact-duplicate, and conflicting-event cases. A successful script run proves only the implemented processing behavior for supplied inputs; it is not evidence that a business review outcome is correct without agent interpretation.
