---
name: monthly-receiving-review
description: Review monthly purchase-order receipts from local JSON evidence, identify evidence gaps and signed receipt positions, and draft recipient-specific receiving follow-up without sending messages or changing records.
---

# Monthly receiving review

Use this Skill when a purchasing coordinator needs a month's receipt position and remaining follow-up. Every supplied order line remains in scope regardless of coverage declarations. Read [the interface](references/interface.md) before processing.

1. Confirm the requested month and supplied order lines. Obtain local input using the documented JSON contract. Never invent missing quantities, completeness declarations, identities, or recipients.
2. Run `python3 <skill-path>/scripts/review.py INPUT.json --output REPORT.json`. This is local, read-only processing of the input; output must be a different path. Inspect errors and all diagnostics. Missing or invalid evidence must limit affected judgments, while unrelated evidence remains usable.
3. Interpret each reported line: `received_as_ordered` requires no receiving follow-up; `shortfall` requires the supplier contact to address the remaining quantity through the purchasing coordinator; `excess` requires warehouse reconciliation. An observed subtotal is never a final receipt position when evidence is incomplete or invalid. Signed negative receipts contribute algebraically, including a negative net.
4. Review every action and its named owner/recipient against the supplied responsibilities. Finalize the draft text with the month, order, SKU, relevant quantity, precise source problem, and concrete next action. When a recipient is missing, explicitly ask for that responsibility/contact rather than guessing. Resolve all listed blockers, not merely the first one. The processor provides draft suggestions; the agent is accountable for interpreting evidence and ensuring each unresolved line has the right follow-up.
5. Deliver the month/scope, one result per supplied line, evidence references and limitations, and recipient-specific drafts. Explain how gaps affect conclusions. Surface diagnostics for records outside scope without changing in-scope totals. Do not send drafts, contact suppliers, or change receiving records.

For local component verification run `python3 <skill-path>/scripts/test_review.py`. These checks exercise the processor, not every future agent's interpretation or effective use.
