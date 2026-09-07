---
name: review-monthly-receiving
description: Review a requested month's purchase-order receipt evidence, classify each supplied order line, expose evidence gaps, and draft the required receiving follow-up. Use for local JSON receiving reviews; do not use to send messages or alter receiving records.
---

# Review monthly receiving

Use this Skill when the user supplies the monthly receiving JSON contract described in [references/input-output.md](references/input-output.md). The supplied order lines define scope. Coverage declarations only describe evidence completeness; they never remove a line.

## Process the evidence

1. Preserve the user's source JSON and run:

   ```bash
   python3 scripts/review_receiving.py INPUT.json --output REVIEW.json
   ```

   Python 3.12 standard library is the only dependency. A nonzero exit means the review was not produced; report the validation messages and ask for corrected data rather than filling missing values with zero.

2. Inspect the resulting `scope_issues`, `outside_scope_events`, and every item in `lines`. Treat the script's arithmetic, deduplication, and blocking flags as deterministic evidence processing. Explain material issues and their effect in the user-facing review.

3. Apply judgment to the full output. Make sure each supplied line has a disposition, and each unresolved line has a concrete next action, responsible owner, and named recipient drawn from the source. Improve draft wording for context if useful, but do not invent names, addresses, dates, event facts, or quantities.

4. Return the review and the draft follow-ups. State observed subtotals for incomplete evidence only as observed values, never final receipt positions. Keep unaffected lines usable when another line has an evidence problem.

Do not contact suppliers, send drafts, or change live order or receiving records unless the user separately authorizes that action. A calculation without the follow-up decision is incomplete.

## Decision rules

- Count current-month events algebraically, including negative returns and reversals. Ignore other months. Count exact duplicate event records once.
- For complete, valid evidence: net equal to ordered is `received_as_ordered`; below is `shortfall`; above is `excess`.
- Missing, partial, or contradictory coverage blocks a final comparison for that line, while retaining its observed subtotal.
- Different records sharing an `event_id` are conflicting evidence and block affected in-scope lines.
- A current-month event for an in-scope order but an unknown SKU creates an order identity issue and blocks every supplied line for that order until reconciled.
- Events for orders outside the supplied order set are reported outside scope and do not affect totals.

Read [references/input-output.md](references/input-output.md) when preparing inputs or interpreting the response fields.
