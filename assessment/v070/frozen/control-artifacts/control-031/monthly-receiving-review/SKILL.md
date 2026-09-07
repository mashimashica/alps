---
name: monthly-receiving-review
description: Review a requested month's purchase-order receipt position from JSON order lines, receipt events, coverage declarations, and responsibilities; identify evidence limits and draft line-specific receiving follow-up. Use for monthly receiving reviews and receipt reconciliation planning, not for sending messages or changing receiving records.
---

# Monthly Receiving Review

Turn the supplied monthly receiving JSON into a decision-ready review for the purchasing coordinator. Keep every supplied order line in scope. Use only supplied identities and contacts, and draft follow-up without sending it or changing source records.

## Process the evidence

1. Read [references/input-output.md](references/input-output.md) when preparing or interpreting the JSON interface.
2. Run the bundled processor from this Skill directory:

   ```bash
   python3 scripts/review_receiving.py INPUT.json --output REVIEW.json
   ```

   Omit `--output` to write JSON to standard output. The script uses Python 3.12 standard library only. It calculates signed in-month receipt subtotals, collapses exact duplicate events, detects conflicting event IDs, checks line/month coverage, and proposes follow-up records.
3. Inspect `input_issues`, `ignored`, and every line in `lines`. Treat the processor as a calculation and evidence-control aid. Decide and explain the review yourself; do not merely return its JSON.
4. For each supplied order line, connect the order quantity, applicable receipt evidence, coverage status, final position or explicit limit, and follow-up. Do not remove a line because coverage is missing, false, or conflicting.

## Make the judgment

- Count only events for the requested month and the exact in-scope `(order_id, sku)`. Sum signed quantities algebraically, including returns and correcting reversals.
- When evidence is complete, valid, and identity-clear, compare final net received with ordered quantity: equal is `received_as_ordered`, below is `shortfall`, and above is `excess`.
- For an incomplete or missing export, label the sum as an observed subtotal and withhold the final receipt position. Never substitute zero for missing evidence.
- If a current-month event names an in-scope order but an unknown SKU, withhold final comparisons for that order until identity reconciliation.
- If one `event_id` has different content, exclude its variants from arithmetic and identify every affected line. An exact repeated event counts once.
- Ignore events for orders outside the supplied order set and events outside the requested month; do not let them change in-scope totals.
- Keep unaffected lines usable when another line has missing or conflicting information.

The script reports conservative blocks and suggested actions. Check that each block follows from the source records and that no relevant issue was omitted. A valid calculation does not by itself complete the work.

## Deliver the review

Present:

- the requested month and a scope count;
- one line result for every supplied order line, with ordered quantity, observed subtotal, final net quantity when supportable, position, and evidence basis;
- explicit evidence gaps and the effect of each gap on the judgment;
- every needed follow-up with the supplied responsible person or recipient, a concrete next action, and a draft message.

For a supported shortfall, direct the purchasing coordinator to the order's supplied supplier contact. For a supported excess, direct the supplied warehouse lead to reconcile the surplus. For incomplete or missing coverage, direct the supplied data steward to provide or confirm the full export. For conflicting order/event identity or source evidence, direct the supplied purchasing coordinator and data steward to reconcile the named records. If a required name or address is absent, say that the recipient is unresolved; do not invent one.

Keep all communications as drafts. Sending messages, contacting suppliers, and modifying live receiving data require separate authorization.
