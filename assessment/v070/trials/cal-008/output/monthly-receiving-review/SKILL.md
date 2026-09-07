---
name: monthly-receiving-review
description: Review a requested month's purchase-order receipt position from JSON order, receipt-event, coverage, and responsibility data; calculate signed receipts, expose evidence gaps or conflicts, and draft (but do not send) recipient-specific follow-up for unresolved lines. Use for monthly receiving reconciliation and follow-up planning, not for changing receiving records or contacting suppliers.
---

# Monthly Receiving Review

Turn the supplied JSON into a line-by-line receiving decision and a usable follow-up plan. Every supplied order line remains in scope for the requested month. Coverage describes the evidence; it never removes a line from scope.

This skill is analysis and drafting only. Do not contact anyone, send a draft, or alter an order or receiving record unless the user separately authorizes that live action.

## Run the deterministic analysis

Save the use-specific input as a UTF-8 JSON file, then run:

```bash
python3 scripts/review_receipts.py INPUT.json --output REVIEW.json
```

The script uses only Python's standard library. Run `python3 scripts/review_receipts.py --help` for options. It exits `0` after producing a review, `1` for unreadable input or output files, and `2` when the root contract is unusable. Record-level evidence problems are normally represented in the review instead of aborting unrelated lines.

Read [references/contract.md](references/contract.md) when preparing input, interpreting output fields, or resolving a diagnostic.

## Interpret the evidence

Treat the script as deterministic evidence processing, not as the finished business judgment. Check that the requested month, supplied line scope, coverage, responsibilities, and diagnostics match the user's materials. Then review every entry in `lines`:

- `received_as_ordered`, `shortfall`, and `excess` are final positions only when the line has complete, valid evidence.
- `undetermined` retains an observed subtotal but does not assert a final position. Never turn a missing value or incomplete export into zero.
- Negative event quantities are returns or corrections and contribute algebraically.
- Exact repeated event rows count once. A reused `event_id` with different content is conflicting evidence; the script excludes that event ID from totals and limits the conflict to lines whose requested-month evidence may be affected.
- A requested-month event for an in-scope order but an unknown SKU blocks final comparisons for every line on that order until the identity is reconciled.
- Events outside the month or outside the supplied order set do not change in-scope totals. Inspect their counts in `excluded_events` so exclusions remain visible.

Do not overrule an `undetermined` result merely because its observed subtotal happens to equal the ordered quantity. If source material resolves a diagnostic, update the input and rerun the processor rather than editing calculated output by hand.

## Finish the follow-up plan

For each unresolved line, confirm the generated `follow_up` has the correct owner, recipient, reason, and concrete next action:

- Complete shortfall: the purchasing coordinator follows up with that line's supplied `supplier_contact` about the remaining receipt.
- Complete excess: the supplied warehouse lead reconciles the surplus against order and receiving evidence.
- Incomplete or missing coverage: the supplied data steward provides or confirms the full export before comparison.
- Conflicting order or event identity: the supplied purchasing coordinator and data steward reconcile the identified source records.

The processor supplies a concise draft when all needed names are present. Adapt it to the user's requested communication format and context, but preserve quantities, evidence limitations, and the next action. If a recipient is absent, keep it as an explicit recipient gap; do not invent a name or address. For a line with multiple blockers, preserve every blocker and all applicable owners rather than selecting a convenient single cause.

Return the review month, scope/count summary, each line's ordered quantity, observed net received quantity, final position or reason it is undetermined, evidence gaps and their effect, and the recipient-specific follow-up draft. State that drafts were not sent.

## Verify when modifying the skill

Run the behavioral tests after changing the processor:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

These checks cover the implemented mechanics. They do not prove that every future agent will interpret new business evidence correctly.
