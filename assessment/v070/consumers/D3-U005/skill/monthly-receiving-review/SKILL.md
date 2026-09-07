---
name: monthly-receiving-review
description: Review a supplied month's purchase-order receipt evidence, classify every supplied order line, expose evidence gaps and identity conflicts, and draft recipient-specific follow-ups. Use when the input is the documented JSON contract; do not send messages or alter receiving records.
---

# Monthly Receiving Review

## Purpose

Make the requested month's purchase-order receipt position clear enough for the purchasing coordinator to direct remaining receiving follow-up.

## Outcomes

- Each supplied order line has a receipt judgment supported by the applicable order, current-month events, and coverage evidence, with limitations explicit.
- Each unresolved line has a concrete next action and recipient drawn from supplied responsibility information.
- Evidence gaps, duplicate or conflicting events, and identity anomalies are visible with their effects on affected judgments.

## Inputs

Accept one UTF-8 JSON object with `month` (`YYYY-MM`), `orders`, `events`, `coverage`, and `responsibilities` as described by the caller. Orders are in scope because they are supplied; coverage declarations never remove a supplied line. Do not infer missing values as zero or invent contacts.

## Activities & Tasks

### Establish scope and evidence

1. Confirm the requested month and validate each order line's `order_id`, `sku`, and positive integer `ordered` quantity.
2. Treat only events whose `event_month` equals the requested month and whose order and SKU identify an in-scope line as contributing to that line. Events for outside orders are out of scope.
3. Use the manifest's `complete` value for each line and month as the completeness evidence. Report missing or ambiguous coverage rather than inferring completeness.
4. Deduplicate exact repeated copies of an `event_id` and flag an event ID with different content as conflicting evidence on all affected lines. Flag a current-month event for an in-scope order but absent SKU for identity reconciliation.

### Interpret and direct

1. For complete, valid evidence, sum signed quantities algebraically and compare net received with ordered: equal is `received_as_ordered`, below is `complete_shortfall`, and above is `complete_excess`.
2. For incomplete or invalid evidence, report the observed subtotal when computable but do not claim a final receipt position.
3. Draft follow-up for every unresolved line: supplier contact for a complete shortfall, warehouse lead for a complete excess, data steward for incomplete export, and purchasing coordinator plus data steward for conflicting order/event identity. Use only supplied responsibility values.
4. Return a review record for every supplied line and a concise evidence and follow-up record. The agent must interpret results, decide whether additional supplied evidence resolves a limitation, and draft messages without sending them.

## Enablers and constraints

Use the bundled standard-library script for deterministic arithmetic, validation, deduplication, anomaly detection, and initial follow-up routing. The agent remains responsible for contextual interpretation and final drafting. Python 3.12+ is required; no network or third-party package is used. The script has no external side effects.

## Procedure

Run from this Skill directory:

```sh
python3 scripts/review_receipts.py input.json > review.json
```

The output is JSON with `status` (`ok` or `invalid_input`), `month`, `lines`, `issues`, and `follow_ups`. On invalid input, `errors` explains all detected errors and no line judgment should be treated as complete. Review `issues` and each line's `evidence` before drafting or relying on a result.

## Exit criteria and limits

The review is ready for coordination only when every supplied line is represented, all evidence limitations are explicit, and each unresolved line has a recipient and drafted next action. Script checks demonstrate component behavior for tested inputs; they do not establish that an agent will interpret every future evidence situation correctly. This Skill drafts follow-ups only and never sends them or updates business systems.
