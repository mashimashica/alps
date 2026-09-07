---
name: monthly-receiving-review
description: Review a requested month's purchase-order receipts from JSON order, event, coverage, and responsibility data; decide each line's evidence-supported position and draft the required receiving follow-up. Use for monthly receiving review or receipt reconciliation requests, not for changing records or contacting recipients.
---

# Monthly Receiving Review

Turn the supplied JSON into a decision-ready review for the purchasing coordinator. Keep every supplied order line in scope. Treat coverage declarations as evidence about those lines, never as a scope filter.

## Process the evidence

1. Save the supplied JSON locally without changing its values, then run:

   ```bash
   python3 scripts/receiving_review.py INPUT.json --output REVIEW.json
   ```

   The script uses only Python's standard library. Its exit code is `0` when it writes a review, including a review with evidence gaps, and `2` when the input contract is structurally invalid. Use `--help` for interface details.

2. Inspect the processor's `issues`, `scope`, and every object in `lines`. Do not report a final receipt position where the line has incomplete, missing, ambiguous, or conflicting evidence. An observed subtotal is still usable when explicitly labeled as provisional.

3. Present the requested month, scope count, source checks, and one result for every supplied `(order_id, sku)`. For each line state ordered quantity, observed signed current-month quantity when calculable, evidence condition, supported position, and the effect of any gap.

4. Include each required draft follow-up with its supplied recipient and concrete next action. A calculation without a follow-up decision is unfinished. Keep drafts clearly unsent. Do not invent names or addresses; if required responsibility data is unavailable, identify that recipient gap and preserve the role as the unresolved owner.

5. Distinguish events outside the supplied order set from in-scope evidence. They do not change in-scope totals. Mention them as excluded observations when useful for source review.

## Decision rules

- Count exact copies of an event once. A reused `event_id` with different content is conflicting evidence for each affected in-scope line or order; withhold affected final comparisons.
- Add current-month quantities algebraically, including negative returns and correcting reversals. Exclude other months.
- If a current-month event names an in-scope order with a SKU absent from that order, withhold final comparisons for that order pending purchasing coordinator and data steward identity reconciliation.
- Only confirmed complete and valid evidence supports a final comparison. Equal to ordered is `received_as_ordered`; below is `shortfall`; above is `excess`.
- A complete shortfall goes to the order's supplier contact through the purchasing coordinator. A complete excess goes to the warehouse lead. An incomplete or missing export goes to the data steward. Identity conflicts go jointly to the purchasing coordinator and data steward.
- Missing information limits only affected judgments. Continue using unrelated sound evidence.

## Interpret the result

The processor produces machine-readable evidence and proposed follow-ups, not the finished communication. Check that its classifications follow the supplied facts, explain material evidence gaps in plain language, and adapt the draft wording to the user's requested format without strengthening provisional conclusions. Do not send messages, contact suppliers, or alter receiving records unless the user separately authorizes that action.

