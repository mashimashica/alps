---
name: receiving-review
description: Review a month's supplied purchase-order lines and receiving evidence, determine supported receipt positions, expose evidence gaps, and draft recipient-specific follow-ups without sending messages or changing records.
---

# Monthly Receiving Review

Use the bundled deterministic processor for arithmetic, identity checks, duplicate handling, and evidence classification; retain responsibility for interpreting the result and drafting useful follow-up.

## Inputs and invocation

Input is one UTF-8 JSON object with `month` (`YYYY-MM`), `orders`, `events`, `coverage`, and `responsibilities`, as described in the request. Run:

```sh
python3 scripts/monthly_review.py input.json > review.json
```

The script emits JSON to stdout and diagnostics/errors to stderr. Exit 0 means the input was processed (including incomplete or conflicting evidence); nonzero means the contract could not be safely processed. It never contacts recipients or mutates business records.

## Agent responsibilities

1. Confirm the requested month and supplied order lines define scope. Coverage declarations do not remove lines from scope.
2. Inspect each returned line's evidence and preserve distinctions among `received_as_ordered`, `shortfall`, `excess`, `incomplete_export`, `identity_reconciliation`, `conflicting_event`, and input errors. An observed subtotal is not a final position when export completeness is false. Never turn absent values into zero.
3. Use the supplied responsibility names exactly. Draft (do not send) a concrete follow-up for every unresolved line: supplier contact for a complete shortfall; warehouse lead for a complete excess; data steward for incomplete export; purchasing coordinator plus data steward for identity or event conflicts. Include order/sku, evidence basis, and the requested action. Do not invent contacts.
4. Treat events outside the requested month as non-contributing, out-of-scope orders as non-contributing, exact repeated event copies as one event, and differing content under the same event_id as conflicting evidence. A current-month event with an in-scope order but absent SKU requires identity reconciliation for the affected order.
5. Explain evidence gaps and how they limit judgments while leaving unrelated sound lines usable. The final review must state scope, per-line position, evidence basis, and follow-up status. A script result alone is not proof of effective review.

## Verification boundary

The script's local checks establish component behavior for the supplied contract. Before relying on a review, check that the input is authoritative, responsibilities are current, and your interpretation and drafted follow-ups satisfy the work outcomes. Do not claim that format or script checks demonstrate every future agent's effective use.
