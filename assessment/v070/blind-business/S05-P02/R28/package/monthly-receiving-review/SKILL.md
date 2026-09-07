---
name: monthly-receiving-review
description: Review a requested month's purchase-order receipts from order, event, coverage, and responsibility JSON; decide each line's evidence-supported receipt position and draft the required receiving follow-up. Use for monthly receiving close or purchasing follow-up preparation, not for sending messages or changing receiving records.
---

# Monthly Receiving Review

Turn supplied monthly receiving evidence into a line-complete review and draft each necessary follow-up. Keep every supplied order line in scope. Treat coverage as evidence about the export, never as a scope filter.

## Process the evidence

1. Check that the requested month and the local input file are identified. Read [references/contract.md](references/contract.md) when preparing, troubleshooting, or interpreting the JSON interface.
2. Run:

   ```bash
   python3 "<skill-directory>/scripts/review_receiving.py" INPUT.json --output REVIEW.json
   ```

   Replace `<skill-directory>` with this Skill folder's path. Resolve input and output paths relative to the current working directory. The script uses only the Python standard library. A successful exit means processing completed; it does not mean every line has complete evidence.
3. Inspect `review_summary`, every entry in `lines`, `outside_scope_events`, and `unassigned_issues`. Reconcile the output to the source input. Do not silently drop a source line or infer completeness from event counts.
4. Interpret the evidence and write the review. The script provides deterministic calculations and a follow-up basis, but the agent remains responsible for the final line judgment and recipient-specific draft.

If the processor rejects the file, report the blocking structural problem. If malformed records are isolated while other lines remain usable, retain the sound line conclusions and state exactly which judgments the malformed evidence limits.

## Decide each supplied line

For evidence that is confirmed complete, internally consistent, and valid, compare the month's signed net receipt to the positive ordered quantity:

- Equal: `received_as_ordered`; no receiving follow-up.
- Below: `shortfall`; the remaining quantity requires supplier follow-up by the purchasing coordinator.
- Above: `excess`; the surplus requires reconciliation by the warehouse lead.

Returns and correcting reversals are negative and contribute algebraically. Events from another month do not contribute. Count exact copies of one event once. Never turn an absent or invalid quantity into zero.

Do not state a final receipt position when the line has an incomplete export, conflicting event content, an invalid quantity that could affect its total, or an order/event identity problem. You may state the `observed_subtotal` as a partial subtotal when the output labels it non-final. An unexpected current-month SKU on an in-scope order blocks final comparison for that order's lines until identity is reconciled. Events for orders outside the supplied order set remain outside the review.

## Direct and draft follow-up

Use the supplied responsibility values and supplier contacts exactly; do not invent names or addresses. For every unresolved line, include a concrete next action and a draft:

- Complete shortfall: purchasing coordinator contacts that order line's supplier contact to confirm the plan and timing for the remaining quantity.
- Complete excess: warehouse lead reconciles the surplus against the order and receiving evidence.
- Incomplete or invalid export evidence: data steward supplies, corrects, or confirms the full requested-month export before final comparison.
- Conflicting event or order/event identity: purchasing coordinator and data steward reconcile the identified source records before recalculation.

The processor's `follow_up` object provides roles, supplied recipients, and a factual draft basis. Turn that basis into a concise recipient-specific message. If required contact information is absent or conflicting, identify the recipient gap and draft only what the evidence supports; do not guess. Draft messages only. Do not send them or alter order or receiving records without separate authorization.

## Deliver the review

Include:

- requested month, supplied line count, and whether any line remains unresolved;
- one row per supplied `order_id` and `sku`, with ordered quantity, observed subtotal, final net only when established, position, evidence status, and evidence gaps;
- every required follow-up with supplied owner/recipient, concrete next action, and draft text;
- outside-scope event IDs separately, plus unassigned issues that cannot safely be attached to one line;
- an explicit statement that the work is a review and draft, and that no message was sent or record changed.

Do not describe a partial subtotal as the month's final total. Do not let a sound line inherit an unrelated evidence gap.
