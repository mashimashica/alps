---
name: monthly-receiving-review
description: Review a month's purchase-order receipt evidence from supplied JSON, determine supportable line positions, expose evidence gaps, and draft recipient-specific follow-ups without sending them.
---

# Monthly receiving review

Use this skill when a coordinator needs a defensible review of supplied purchase-order lines and receiving evidence for one month. The reusable processor is `scripts/review_receipts.py`; invoke it with `python3 scripts/review_receipts.py input.json`, or `--help` for details. It emits a JSON report to stdout and errors to stderr with a nonzero exit status.

The agent remains responsible for checking scope and source validity, interpreting the report, and presenting a clear review. Treat the supplied order lines as the scope even when a coverage declaration is incomplete. Use only events in the requested month. Signed quantities are algebraic: returns and reversals reduce the subtotal. Exact repeated copies of an event count once; the same event ID with different content is conflicting evidence. An event for an in-scope order but an absent SKU requires identity reconciliation; an out-of-scope order event is excluded.

Do not infer completeness from row counts or replace missing data with zero. A complete, valid line can be classified as `received_as_ordered`, `shortfall`, or `excess`. A partial export supports an observed subtotal but not a final position. Every unresolved line needs a concrete drafted follow-up and the supplied recipient: supplier contact for a complete shortfall, warehouse lead for excess, data steward for incomplete export, and purchasing coordinator plus data steward for identity conflicts. Do not invent recipients or send drafts.

Report, for each line, order/SKU, ordered quantity, observed net quantity where supportable, evidence status, final position or why it is unavailable, evidence gaps and their effects, and follow-up recipient/action. Preserve the distinction between observed facts and judgments. Mention that component/script checks do not establish that every future agent will use the skill effectively.

