---
name: monthly-receiving-review
description: Review a requested month's purchase-order receipt position from JSON order, receipt-event, coverage, and responsibility data. Use when line-level net receipts, evidence gaps, and recipient-specific receiving follow-up drafts are needed; do not use it to send messages or alter receiving records.
---

# Monthly Receiving Review

## Purpose

Make the requested month's purchase-order receipt position clear enough for the purchasing coordinator to direct the remaining receiving follow-up.

## Outcomes

- The receipt position of each supplied in-scope order line is supported by the applicable order, receipt-event, and coverage evidence.
- Each unresolved line has a concrete next action and a recipient grounded in the supplied supplier or responsibility information.
- Evidence gaps and their effects on affected line judgments are explicit.

## Activities & Tasks

The following Tasks are required. Evidence reconciliation and acquisition must precede any final comparison that depends on that evidence; otherwise, use the order that best fits the request.

### Establishing scope and evidence

1. Identify the requested month and every supplied order line. A line is identified by `order_id` and `sku`; a coverage declaration does not remove a supplied line from scope.
2. Inspect source provenance or freshness information supplied with the input and state any unconfirmed applicability. Do not infer export completeness from event count or from an apparently plausible total.
3. Run the bundled processor as described in [tool use](references/tool-use.md). Treat exit `0` as completed validation and calculation, not as proof that every line has a final position. On exit `2`, correct or obtain a usable input before relying on a result.
4. Check `scope_issues`, `evidence_issues`, each line's `evidence_findings`, and `recipient_gaps`. Preserve sound line evidence when a gap is limited to another line.

### Interpreting receipt positions

1. Use `observed_uncontested_net_received` as an observed subtotal. Negative receipt quantities are returns or correcting reversals and contribute algebraically. Exact duplicate copies of an event count once.
2. Claim a final line position only when the processor returns `position_is_final: true`. For that line, compare net received with ordered quantity: equality is **received as ordered**, a lower amount is a **shortfall**, and a higher amount is an **excess**.
3. Keep a position **unconfirmed** when coverage is missing, false, invalid, or conflicting; when order or event evidence conflicts; or when a current-month event for the order has a SKU absent from that order. State the observed subtotal when available, but do not replace missing values with zero or present the subtotal as final.
4. Ignore events outside the requested month in the month's total. An event for an order outside the supplied order set is outside this review and does not change in-scope totals; report the processor's exclusion summary without creating a new order line.

### Directing follow-up

1. Review every object in each line's `follow_ups`. Convert its `next_action`, quantities, evidence identifiers, and parties into a concise recipient-specific draft. Consolidate drafts only when doing so keeps every affected line, evidence gap, and requested action explicit.
2. For a confirmed shortfall, draft the purchasing coordinator's request to the supplied `supplier_contact` for the stated remaining quantity. For a confirmed excess, draft a request to the supplied warehouse lead to reconcile the stated surplus against the order and receiving evidence.
3. For incomplete or invalid export evidence, draft a request to the supplied data steward to provide or confirm the full export before final comparison. For conflicting order/event identity, draft reconciliation for both the supplied purchasing coordinator and data steward, naming the affected records.
4. If a required party is absent, do not invent a name or address. Identify the recipient gap and the supplied responsibility field needed before the follow-up can be directed.
5. Return the line-by-line judgment, supporting event identifiers and subtotal, evidence limits, and labeled follow-up drafts. Explicitly state which lines are final and which remain unconfirmed. Draft only; do not send messages or change purchase orders, events, coverage declarations, or receiving records.

## Inputs

A UTF-8 JSON document containing the requested `month`, supplied `orders`, `events`, `coverage`, and `responsibilities` described in [tool use](references/tool-use.md), plus any available source-provenance or freshness context.

## Outputs

A review for the requested month containing every usable supplied order line, its traceable receipt evidence and final or unconfirmed position, explicit evidence gaps, and recipient-specific draft follow-up for every unresolved line.

## Controls

The requested month, supplied order lines, event records, line-and-month coverage declarations, and supplied responsibilities govern the review. The calculation and evidence rules in this description govern final-position claims and follow-up routing.

## Constraints

- Order quantities must be positive integers. Receipt quantities are signed integers; never coerce missing or invalid quantities to zero.
- Final comparison requires confirmed complete and valid evidence for the affected line. Missing or conflicting evidence limits only judgments that depend on it, except an unlocalizable scope issue, which limits completeness of the overall review.
- A calculation is evidence used in the review, not the review judgment itself. Returning processor output without interpreting it and drafting required follow-up does not complete this work.
- This work does not authorize contacting suppliers or staff, changing operational records, or inferring recipient identities.

## Enablers

An agent able to inspect supplied context, run a local command, interpret structured results, and draft text; Python 3.12 or later; and the bundled [receipt processor](scripts/review_receipts.py). The processor reads local JSON and has no network or third-party dependencies.

## Resources

- [Tool use and JSON contracts](references/tool-use.md) describes invocation, validation, output meanings, failures, and reproducibility conditions.
