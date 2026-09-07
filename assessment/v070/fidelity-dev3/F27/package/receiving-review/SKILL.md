---
name: receiving-review
description: Review a month's purchase-order receiving evidence and draft recipient-specific follow-up for each line. Use when supplied orders, receipt events, coverage declarations, and responsibilities need an evidence-aware receiving position; do not send messages or alter receiving records.
---

# Monthly receiving review

Use the supplied JSON input with `scripts/review_receiving.py` to produce a deterministic evidence summary, then interpret the result and draft the follow-up for the purchasing coordinator. The script is a calculation and evidence-checking aid; the agent owns scope confirmation, interpretation, and recipient-specific drafting.

## Interface

Run:

```bash
python3 scripts/review_receiving.py input.json > review.json
```

The input must contain `month` (`YYYY-MM`), `orders`, `events`, `coverage`, and `responsibilities` as described by the work request. Orders use positive integer `ordered`; events use `event_id`, `order_id`, `sku`, `event_month`, and signed integer `quantity`. Coverage declares `complete` for an order line and month. Responsibility values are recipient names or addresses supplied for `purchasing_coordinator`, `warehouse_lead`, and `data_steward`.

The JSON output contains `month`, `lines`, and `issues`. Each line includes its key, ordered quantity, event evidence, `observed_subtotal`, `evidence_status`, `position`, `follow_up`, and `recipient`. `position` is `received_as_ordered`, `shortfall`, `excess`, `undetermined_incomplete_export`, `undetermined_identity_reconciliation`, `undetermined_conflicting_evidence`, or `undetermined_invalid_evidence`. Exact repeated event copies count once. Events outside the requested month do not contribute. An event for an unknown order is reported in `issues` and excluded; an event for a SKU absent from an in-scope order creates an identity issue for that order. Conflicting contents for one `event_id` affect every referenced in-scope line and prevent a final comparison.

## Agent interpretation and follow-up

1. Confirm the requested month and supplied order lines define scope. Coverage claims do not remove a supplied line.
2. Inspect `issues`, event evidence, and line statuses. Do not convert missing values to zero, and do not treat a row count as proof of completeness.
3. For complete, valid lines, use the reported net subtotal against ordered quantity. Draft the required follow-up: a shortfall goes to the supplied supplier contact through the purchasing coordinator; an excess goes to the supplied warehouse lead for reconciliation. For an incomplete export, ask the supplied data steward to provide or confirm the full export. For identity or conflicting evidence, ask the purchasing coordinator and data steward to reconcile the identified source records.
4. Keep unresolved positions unresolved and explain which evidence gap limits the judgment. Include a concrete next action and supplied recipient; never invent a contact. Draft messages only; do not send them or change records.

The output is evidence for the review, not proof that an agent made every required decision. Report assumptions, malformed or missing fields, and any unperformed review checks.

