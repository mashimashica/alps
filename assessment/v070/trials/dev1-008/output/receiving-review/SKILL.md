---
name: receiving-review
description: Review a month's supplied purchase-order lines, receipt events, coverage declarations, and responsibilities; establish evidence-qualified receipt positions and draft recipient-specific follow-ups without sending messages or changing records.
---

# Monthly Receiving Review

Use the bundled deterministic processor for arithmetic, identity checks, duplicate handling, and evidence status. Then interpret its results as an agent: check scope and source plausibility, preserve uncertainty, and draft the needed follow-up for each unresolved line. A calculation alone is not completion.

## Inputs and invocation

The input is one JSON object with `month`, `orders`, `events`, `coverage`, and `responsibilities` as described in the work brief. Save it locally and run:

```sh
python3 scripts/review_receipts.py input.json > review.json
```

The script emits JSON to stdout and diagnostics/errors to stderr. It never sends messages or edits receiving records. A non-zero exit means the input contract or validation could not support a review; report the error rather than guessing.

## Agent procedure

1. Confirm the requested month and supplied order lines are the review scope; coverage declarations do not remove a supplied line.
2. Read the processor's per-line evidence and status. Use only events in the requested month for totals. Negative quantities are algebraic returns/corrections. Exact repeated copies of an event count once.
3. Treat `complete` coverage as evidence, not as an inference from row counts. For complete, valid evidence compare net received with ordered quantity. Classify equal as received as ordered, below as complete shortfall, and above as complete excess. For incomplete evidence, state the observed subtotal and do not claim a final position.
4. Treat an event SKU absent from its in-scope order as identity-reconciliation evidence; do not fold it into a line comparison. Events for orders outside the supplied order set are out of scope. If one event ID has differing content, mark affected evidence conflicting.
5. For every unresolved line, draft (do not send) a concrete follow-up with the supplied recipient: complete shortfall → supplier contact about remaining receipt; complete excess → warehouse lead to reconcile surplus against order/receiving evidence; incomplete export → data steward to provide or confirm the full export; identity conflict → purchasing coordinator and data steward to reconcile source records. Never invent a recipient name or address.
6. State evidence gaps and their effect on the judgment, and distinguish observed facts, interpretation, and the proposed next action. A line with no qualifying event is not automatically zero when evidence is incomplete.

## Response format

Return a review containing: scope, one record per supplied order line (order_id, sku, ordered, evidence summary, status/judgment, evidence gaps, and follow-up if needed), out-of-scope/identity/conflict findings, and a draft follow-up section. Keep recipients exactly as supplied in `responsibilities` or the order's `supplier_contact`.

The processor is a support tool, not proof that an agent achieved the review outcomes. Verify representative results and exercise judgment over source validity and wording before relying on the review.
