---
name: monthly-receiving-review
description: Review monthly purchase-order receipts from local JSON, reconcile signed receipt evidence and completeness, and draft recipient-specific receiving follow-up for a purchasing coordinator.
---

# Monthly receiving review

Use this Skill when a coordinator needs the receipt position and remaining follow-up for a requested month. Operate only on supplied local files. Never send drafts, contact suppliers, or change receiving records.

1. Obtain the requested month, all supplied order lines, events, coverage declarations and responsibilities using the [input and output contract](references/contract.md). Ask for missing inputs rather than inventing contacts, quantities or completeness. Every supplied order line remains in scope even if its coverage is missing or partial.
2. Run `python3 <skill-dir>/scripts/review.py INPUT.json --output REPORT.json`. Python 3.12 standard library only; `--help` describes the interface. Choose a new output path. Exit 0 means processing succeeded, not that all evidence is sound. Exit 2 means a structural/input/file error; correct it before relying on a report.
3. Inspect `issues`, every line's `blockers`, observed quantities and proposed actions. Resolve ambiguity with the supplied source records. The script is a deterministic evidence aid: the agent is responsible for interpreting evidence, checking scope and judging whether its proposed follow-up is sufficient. Do not silently override a blocker or declare completeness from row counts.
4. For complete valid evidence, explain whether the line is received as ordered, short or excess. A short line needs the purchasing coordinator to draft a supplier follow-up for the remaining quantity. An excess needs the warehouse lead to reconcile the excess. Incomplete evidence needs the data steward to provide or confirm a full export before final comparison. Conflicting order/event identity needs the purchasing coordinator and data steward to reconcile identified records. Preserve sound evidence on unrelated lines.
5. Produce a concise review with the requested month, all supplied lines, ordered quantity, trustworthy net or observed subtotal, coverage, receipt judgment, supporting event IDs, gaps and their effect. Include every unresolved line's responsible recipient and concrete next action. Adapt the script's drafts to the actual evidence; retain source identifiers and quantities. Where a recipient is missing, mark routing unresolved and request the supplied responsibility/contact; do not invent a name or address. Do not treat an incomplete line's observed subtotal as its final receipt position.
6. Deliver the reviewed report and unsent recipient-specific drafts. State outstanding information and which decisions it prevents. Calculation alone does not complete the review.

Local component checks: `python3 <skill-dir>/scripts/test_review.py`. These check implemented logic; they do not demonstrate every future agent's effective interpretation or use.
