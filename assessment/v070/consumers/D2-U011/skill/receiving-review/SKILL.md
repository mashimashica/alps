---
name: receiving-review
description: Review a supplied month's purchase-order receipt evidence, determine supported line positions, expose evidence gaps, and draft (without sending) recipient-specific receiving follow-up. Use for monthly receiving review work; do not use to alter receiving records or contact parties.
---

# Monthly Receiving Review

## Purpose

Make the month's purchase-order receipt position clear enough for the purchasing coordinator to direct remaining receiving follow-up, while preserving the supplied scope and making evidence limits explicit.

## Outcomes

- Each supplied in-scope order line has a receipt position supported by applicable order, event, and coverage evidence, or is explicitly marked undetermined with the reason and affected evidence gap.
- Each unresolved line has a concrete, recipient-specific follow-up draft grounded in supplied responsibility information.
- Evidence conflicts, identity issues, exclusions, and their effects on line judgments are explicit.

## Inputs and boundaries

Accept one JSON object containing `month`, `orders`, `events`, `coverage`, and `responsibilities` as specified by the user. The supplied order lines define scope; coverage declarations do not remove lines from scope. Do not invent contacts, quantities, events, or zero values. Draft messages only; never send them or modify source records.

## Activities & Tasks

### Prepare evidence

1. Run `python3 scripts/review_receipts.py INPUT.json` (or pipe JSON on stdin). Treat exit code 2 as invalid input and stop for correction.
2. Check the returned `lines`, `identity_issues`, and `conflicting_event_ids`. Exact repeated event copies are counted once; differing content under one event ID is conflicting evidence.
3. Explain that only events in the requested month and supplied order set contribute. Negative quantities contribute algebraically. Events for out-of-scope orders are excluded, not errors.

### Interpret and direct follow-up

1. For a line with complete, valid, unflagged evidence, compare net received with ordered: equal is `received_as_ordered`, below is `shortfall`, and above is `excess`.
2. For incomplete coverage, report the observed subtotal only and do not claim a final position. For absent coverage, identity reconciliation, or conflicting evidence, mark the affected judgment undetermined and describe the limitation; unrelated sound lines remain usable.
3. For a complete shortfall, draft follow-up to the supplied supplier contact through the purchasing coordinator about the remaining quantity. For a complete excess, draft follow-up to the supplied warehouse lead to reconcile surplus against order and receiving evidence. For incomplete export, draft follow-up to the supplied data steward to provide or confirm the full export. For conflicting order/event identity, draft joint reconciliation to the supplied purchasing coordinator and data steward.
4. Include order ID, SKU, relevant quantities/event IDs, evidence limitation, recipient, and concrete requested action in each draft. If a required recipient or supplier contact is absent, state that the draft is blocked; do not guess.

## Output contract

Return a review table or equivalent per-line record containing `order_id`, `sku`, `ordered`, observed net (if any), event IDs, coverage status, evidence flags, supported position, and follow-up status/draft. Include a separate section for out-of-scope events and unresolved global conflicts. A calculation without a follow-up decision is incomplete.

## Verification limits

The bundled script verifies input shape, deterministic deduplication, month/scope filtering, algebraic totals, coverage gating, identity flags, and conflicting event IDs. These checks do not establish that a future agent correctly interprets evidence, writes an appropriate draft, or achieves the review Outcomes. Recheck representative outputs and supplied evidence in each application.
