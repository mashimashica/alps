---
name: receiving-review
description: Review a month's purchase-order receipt evidence, calculate supported line positions, expose evidence gaps, and draft recipient-specific follow-up for unresolved lines. Use when supplied orders, receipt events, coverage, and responsibility information need a receiving review; it does not send messages or alter receiving records.
---

# Monthly receiving review

Use this skill when a coordinator needs an evidence-based review of the supplied purchase-order lines for one month. The supplied order lines define scope even when a coverage manifest omits a line. Interpret the evidence and decide the follow-up; a calculation alone is incomplete.

## Process

1. Keep the caller's input JSON unchanged and run the bundled processor from this skill directory:

   ```bash
   python3 scripts/receiving_review.py INPUT.json --output review.json
   ```

   Use `-` for standard input. The processor uses only Python's standard library and emits a structured JSON report. A nonzero exit means the report is not trustworthy; read the diagnostic on stderr.

2. Inspect `review.json`, including `anomalies`, `validation_warnings`, and every line under `lines`. Confirm that the requested month and each supplied order line are in scope. Use the processor's arithmetic as an aid, then apply the evidence rules below when explaining the result.

3. For a line whose requested-month coverage is explicitly complete and whose evidence has no blocking anomaly, compare net received (current-month signed quantities, after removing exact repeated copies) with ordered quantity:

   - equal: received as ordered;
   - below: complete shortfall, with the remaining quantity;
   - above: complete excess, with the surplus to reconcile.

   Negative quantities are returns or correcting reversals and remain algebraic. Events from other months do not contribute. Never turn an absent or invalid quantity into zero.

4. Treat a false or missing coverage declaration as incomplete export. You may report the observed subtotal, but do not claim a final receipt position. A current-month event for an in-scope order with a SKU not supplied for that order blocks final comparisons for the affected order and requires identity reconciliation. Events for orders outside the supplied order set are outside this review. If one `event_id` has differing content, treat affected in-scope lines as conflicting evidence; exact repeated copies count once.

5. Use the generated `follow_up` on each unresolved line as a draft only. Preserve the supplied responsibility names and supplier contact text; do not invent recipients, send messages, or alter source records. Shortfalls go to the supplier contact through the purchasing coordinator, excesses to the warehouse lead, incomplete exports to the data steward, and identity or conflicting evidence to the purchasing coordinator and data steward. Combine conditions in the explanation when more than one blocks a line.

6. Present the report with the line judgment, supporting event IDs and subtotal where available, evidence limitation, recipient, and concrete next action. State that local script checks validate the processor, not every future interpretation by an agent.

## Input and output

The input is a JSON object with `month` (`YYYY-MM`), `orders` (unique `order_id`/`sku` lines with positive integer `ordered` and `supplier_contact`), `events` (event ID, order, SKU, event month, signed integer quantity), `coverage` (line/month completeness declarations), and `responsibilities` containing `purchasing_coordinator`, `warehouse_lead`, and `data_steward`. The processor rejects malformed top-level/order data and preserves row-level evidence problems as warnings or line blockers where they can be assigned.

The output is JSON with `scope`, `lines`, `anomalies`, `out_of_scope_events`, `validation_warnings`, and `follow_up_drafts`. A line's `status` is one of `received_as_ordered`, `complete_shortfall`, `complete_excess`, `incomplete_export`, `identity_reconciliation_required`, or `conflicting_evidence`; inspect `blocking_conditions` when multiple evidence problems coexist. `observed_subtotal` is an observed sum only; `final_position` is present only when a final comparison is supported.

