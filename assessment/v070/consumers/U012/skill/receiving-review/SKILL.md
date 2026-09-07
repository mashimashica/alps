---
name: receiving-review
description: Review a month's purchase-order receiving evidence from supplied JSON, determine supported line positions, expose evidence gaps and identity conflicts, and draft recipient-specific follow-ups without sending them.
---

# Monthly receiving review

Use this skill when a purchasing coordinator needs a defensible monthly receipt position for supplied order lines. The work is an evidence review, not permission to contact suppliers or edit receiving records.

## Workflow

1. Read the supplied JSON input (contract below) and confirm the requested `month` and supplied order lines define scope. Do not remove a line because a coverage declaration is absent or says incomplete.
2. Run `scripts/review_receiving.py input.json` for deterministic normalization and arithmetic. Inspect its JSON result, then apply the interpretation and follow-up rules below. If the script reports an input error, fix or request corrected input rather than guessing.
3. Check that every in-scope line has usable order data and a coverage record for the requested month. Treat coverage `complete` as evidence; never infer completeness from row counts. Events outside the requested month or for out-of-scope orders do not affect in-scope totals.
4. Treat exact repeated copies of an event (same event_id and identical content) as one event. If an event_id has different content, mark every affected in-scope line as conflicting evidence. If a current-month event names an in-scope order but a SKU absent from that order, require identity reconciliation before final comparisons for that order's receiving evidence.
5. For a line with complete, valid evidence, compare net signed quantity (including negative returns/reversals) to ordered quantity: equal = `received_as_ordered`; below = `complete_shortfall`; above = `complete_excess`. For incomplete evidence, report the observed subtotal but do not claim a final position or invent zeroes for missing data.
6. Draft (do not send) the next action for each unresolved line: complete shortfall -> supplier contact, complete excess -> warehouse lead, incomplete export -> data steward, identity conflict -> purchasing coordinator and data steward. Use only supplied responsibility values and supplier contacts; never invent names or addresses. Where multiple issues apply, explain the evidence limitation and choose the reconciliation action before any quantity-based follow-up.

## Input and output

Input is ordinary UTF-8 JSON with `month`, `orders` (`order_id`, `sku`, positive integer `ordered`, `supplier_contact`), `events` (`event_id`, `order_id`, `sku`, `event_month`, signed integer `quantity`), `coverage` (`order_id`, `sku`, `month`, boolean `complete`), and `responsibilities` containing `purchasing_coordinator`, `warehouse_lead`, and `data_steward`.

The script emits JSON containing `scope`, `lines`, `excluded_events`, and `issues`. Each line includes evidence status, observed/net quantity when calculable, position, and a `follow_up` object with recipient and draft action. The agent remains responsible for checking source meaning, explaining limitations, and presenting the result to the coordinator.

Do not state that script execution alone proves effective future agent use. Do not send drafts or alter business records.
