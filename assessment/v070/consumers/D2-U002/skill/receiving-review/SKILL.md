---
name: receiving-review
description: Review a month's purchase-order receipt evidence, classify each supplied order line, expose evidence limitations, and draft recipient-specific receiving follow-up. Use when the user supplies the JSON receiving-review contract; do not send messages or alter receiving records.
---

# Monthly Receiving Review

## Purpose and outcomes

Make the requested month's purchase-order receipt position clear enough for the purchasing coordinator to direct remaining follow-up. For every supplied order line, support the judgment with order, event, and coverage evidence; identify evidence gaps and their effect; and draft the concrete next action with the supplied responsible recipient. A draft is not a sent message.

## Inputs and processing

Accept one UTF-8 JSON object with `month`, `orders`, `events`, `coverage`, and `responsibilities` as described in the user's contract. Treat the supplied order lines as the complete review scope, even if a coverage declaration says incomplete. Use the bundled deterministic helper for arithmetic and anomaly detection:

```sh
python3 scripts/review_receipts.py input.json [output.json]
```

The helper produces JSON containing `month`, `lines`, `out_of_scope_events`, and `validation_errors`. Read its output, then interpret evidence and write the final review in a human-readable form (or preserve JSON when requested). Do not silently continue when `validation_errors` is non-empty.

For each line, apply these rules:

- Order identity is `(order_id, sku)`. Ordered quantities must be positive integers. Event quantities are signed; exact duplicate copies of an event count once. If one `event_id` has different content, mark every affected in-scope line as conflicting evidence.
- Only events whose `event_month` equals the requested month contribute. An event for an order outside the supplied orders is out of scope. A current-month event for an in-scope order but an absent SKU requires identity reconciliation for that order before final comparisons.
- Coverage is evidence, not an inference from row counts. If the matching declaration is absent or not complete, report the observed subtotal only and do not claim a final position; do not replace missing values with zero.
- With complete, valid evidence, compare net received with ordered: equal = `received_as_ordered`; below = `complete_shortfall`; above = `complete_excess`.

## Follow-up and response

Use only supplied responsibility values; never invent a name or address. Draft one follow-up per unresolved line (or one clearly grouped draft when lines share the same cause):

- complete shortfall: purchasing coordinator asks the supplier contact about the remaining quantity;
- complete excess: warehouse lead reconciles surplus against order and receiving evidence;
- incomplete export: data steward provides or confirms the full export before final comparison;
- conflicting order/event identity: purchasing coordinator and data steward reconcile the identified source records.

If multiple conditions apply, explain the blocking identity/conflict or completeness issue before proposing a final position. Include line identity, evidence summary (including signed subtotal where applicable), status, recipient, and concrete next action. Explicitly list excluded events and unresolved gaps. Do not claim that running the helper proves the agent interpreted evidence correctly; agent interpretation remains a required part of the review.

## Failure handling

Malformed JSON, missing required top-level fields, invalid month strings, duplicate order identities, or invalid quantities are validation failures. Correct the input or report the failure rather than guessing. The helper is read-only and has no external effects; retrying it is safe. Verify the output's line count matches the supplied order-line count before drafting.

