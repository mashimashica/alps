---
name: monthly-receiving-review
description: Review a requested month's purchase-order receipts from local JSON orders, signed receipt events, coverage declarations, and responsibilities. Use when a purchasing coordinator needs evidence-supported line positions, explicit evidence gaps, and recipient-specific follow-up drafts for shortages, excesses, incomplete exports, or source conflicts.
---

# Monthly receiving review

Make the month's receipt position clear enough for the purchasing coordinator to direct remaining receiving follow-up. Finish with interpreted line judgments and concrete, recipient-specific drafts. A calculation alone is insufficient.

## Inputs and local processing

Obtain the requested month and the per-use JSON described in [the input and output contract](references/contract.md). Do not embed business inputs into this Skill. Every supplied order line is in scope for that month, regardless of coverage. If no input or month is supplied, request it; do not substitute the example identifiers or assume the current month.

Use Python 3.12 and its standard library:

```sh
python3 scripts/review.py --help
python3 scripts/review.py --input /absolute/path/review-input.json --output /absolute/path/receipt-review.json
```

Resolve `scripts/review.py` relative to this Skill's directory. Choose a new output path; the processor refuses to overwrite a file. It reads local inputs and writes only the requested output. It does not send messages, update receiving records, or connect to external services. Retry with a new output path or use stdout by omitting `--output`.

Read the entire returned report, including issues, excluded events, missing recipients, and invalid supplied order records. Exit 0 means a report was produced, **not** that all lines are resolved. Exit 2 means an input/interface failure; correct the indicated problem before reviewing. Run the bundled component checks with `python3 -m unittest discover -s tests -v` from this Skill directory.

## Interpret the evidence

1. Confirm the requested month, input source, all supplied order lines, and the order-record count. Exact duplicates are represented by one line with every source index retained. Invalid order records remain visible as unresolved records; never silently omit them.
2. Use signed quantities algebraically, including returns and correcting reversals. Exact copies of an event count once. Different contents sharing an event ID are conflicting evidence. Out-of-month events and events for outside orders do not contribute.
3. Distinguish confirmed complete evidence, an incomplete/missing coverage declaration, and invalid/conflicting evidence. Coverage is explicit evidence; row count cannot establish completeness. Missing fields are never zero. A valid empty event list can have an observed subtotal of zero, but still needs affirmative coverage for a final comparison.
4. For complete, valid evidence, compare net received with ordered: equality is received as ordered; below is a shortfall; above is an excess. A negative net is possible: the remaining quantity is ordered minus that negative net. For partial coverage report only an observed subtotal, never a final position. When records are unusable, `valid_event_subtotal` counts only usable records and must not be described as the full observed net.
5. A current-month unknown SKU on an in-scope order blocks final comparisons for **all** lines of that order until identity reconciliation. Other localized errors block only affected lines. Preserve sound judgments on unrelated lines. Unattributable records may necessarily affect all lines; explain why.
6. Inspect the report's evidence references and blockers before adopting its suggested actions. Do not manually override a blocker merely because the subtotal looks plausible. If the user provides corrected evidence, rerun on the corrected input and identify the new source.

## Direct and draft follow-up

Use supplied names/addresses verbatim. Each unresolved line needs a responsible actor, recipient, concrete next action, and a draft. The processor returns action records as drafting aids; the agent owns interpretation and the final recipient-specific wording.

| Finding | Responsible actor | Draft recipient | Concrete action |
| --- | --- | --- | --- |
| Complete shortfall | Purchasing coordinator | Order's supplier contact | Confirm receipt plan for the exact remaining quantity for this month/order/SKU. |
| Complete excess | Warehouse lead | Warehouse lead | Reconcile the exact surplus against the order and receiving evidence. |
| Partial, missing, or invalid coverage | Data steward | Data steward | Supply or confirm the full export and an explicit coverage declaration before final comparison. |
| Conflicting or invalid order/event records | Purchasing coordinator and data steward | Both supplied role holders | Reconcile the cited source records/identities and provide corrected evidence. |

Multiple evidence gaps may require multiple drafts. Do not draft a shortage/excess demand from an incomplete or blocked subtotal. If an actor or recipient is missing, explicitly flag the missing responsibility key/contact and ask the coordinator to supply it. Leave the draft addressed to `[recipient required: ROLE]` until resolved; do not invent a person or claim it is ready to send.

## Deliver the review

Provide the requested month, scope counts, and a compact table containing every line (and unresolved order record): ordered quantity, observed net or qualified usable-event subtotal, coverage, final position or reason withheld, evidence references, responsible actor/recipient, and next action. Include source-specific issues and explain their effects; distinguish outside-review events from blocking errors.

Then provide actual draft messages grouped by recipient when appropriate. Each draft must name the month/order/SKU, supported quantities or the exact gap, and the next action. Label all messages **Draft — not sent**. For received-as-ordered lines state that no receipt follow-up is needed. If all lines are resolved, do not manufacture follow-up.

Conclude by identifying any inputs needed to finish unresolved judgments or route drafts. Link the machine report if useful. Creating drafts is authorized; sending them or modifying live records requires a separate user instruction. Component checks verify the bundled processor only; they do not prove every future agent's interpretation or communication will be correct.
