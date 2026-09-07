---
name: receiving-review
description: Review a month's supplied purchase-order lines and receiving evidence, calculate supported receipt positions, expose evidence gaps, and draft recipient-specific follow-ups without sending them.
---

# Monthly receiving review

Use this skill when a coordinator needs a defensible review of supplied purchase-order lines for one `YYYY-MM` month. The supplied lines define scope; a coverage declaration never removes a line from scope. Do not contact suppliers, change receiving records, or treat a calculation as a completed follow-up.

## Workflow

1. Validate the input contract and scope. Require a valid month, positive integer `ordered` values, unique order-line keys, and responsibilities. Report invalid records rather than silently repairing them.
2. Run `scripts/review.py` on the JSON input. It deterministically deduplicates exact repeated event copies, includes only events whose `event_month` equals the requested month, and returns per-line evidence and follow-up drafts.
3. Interpret the returned evidence. A line is final only when its applicable coverage is explicitly complete and there are no invalid, identity, or event-content conflicts affecting it. Missing coverage is incomplete. Never substitute zero for missing information.
4. For complete evidence, compare net signed quantity with ordered quantity: equal = received as ordered; below = shortfall; above = excess. For incomplete evidence, state only the observed subtotal and that the final position is undetermined.
5. Review flags for current-month events naming an in-scope order with a SKU absent from that order, conflicting content for an event ID, and events for out-of-scope orders. The latter is out of scope and must not change in-scope totals; the former two limit affected judgments.
6. Draft (do not send) each needed follow-up using the supplied responsibility value: complete shortfall to the supplier contact; complete excess to the warehouse lead; incomplete export to the data steward; identity conflicts to the purchasing coordinator and data steward. Do not invent recipient names or addresses. If a required responsibility/contact is absent, mark the draft blocked.

## Interface

Invoke:

```bash
python3 scripts/review.py input.json [--pretty]
```

The JSON result has `ok`, `errors`, `warnings`, `scope`, `lines`, and `out_of_scope_events`. Each line contains `order_id`, `sku`, ordered quantity, evidence (`coverage_complete`, `observed_subtotal`, contributing event IDs), a `status`, `evidence_gaps`, and `follow_ups`. A nonzero exit means the input could not be safely reviewed; its stderr explains the issue. stdout remains machine-readable JSON.

The agent remains responsible for checking source provenance, deciding whether supplied evidence is applicable, interpreting flags, and ensuring every unresolved line has a concrete recipient-specific draft. Script success or format validation alone does not demonstrate effective use on a future review.

## Limits and verification

The script performs deterministic arithmetic and structural checks only; it cannot establish that an export is genuinely complete or that records are authentic. Preserve its warnings and gaps in the review output. Test with representative complete, shortfall, excess, incomplete, return, duplicate, identity-conflict, event-conflict, and out-of-scope cases when changing the script.
