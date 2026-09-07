---
name: monthly-receiving-review
description: Review a requested month's purchase-order receipt evidence, determine supported line positions, expose evidence gaps, and draft recipient-specific receiving follow-ups from supplied responsibilities. Use when given the JSON contract of month, orders, events, coverage, and responsibilities; never send messages or alter source records.
---

# Monthly receiving review

Use `scripts/review.py` to process the supplied JSON input. Invoke it with `python3 scripts/review.py INPUT.json` (or `-` for stdin); it writes a JSON report to stdout and diagnostics to stderr. The script uses only Python's standard library.

Interpret the report before acting. `scope` contains every supplied order line. `lines` contains one judgment per order line, including `status`, signed `observed_received` where computable, evidence issues, and `follow_up` with the supplied recipient and a draft action. `out_of_scope_events` records events for orders outside the supplied order set. `warnings` records contract problems that limit confidence.

The processor counts an exact duplicate event once. Events in other months do not contribute. Negative quantities are algebraic returns. A complete export permits comparison with ordered quantity: equal is `received_as_ordered`, below is `complete_shortfall`, and above is `complete_excess`. An incomplete export yields `incomplete_export` and an observed subtotal without claiming a final position. An event SKU absent from its order creates `identity_reconciliation` for the affected order's lines. Conflicting content under one event ID creates `conflicting_event_evidence` for affected lines. Missing values are surfaced as errors or evidence gaps, never converted to zero.

The agent remains responsible for checking the scope and supplied source data, explaining how evidence affects each judgment, and deciding whether the drafted action is sufficient. Drafts are not sent. Do not invent recipient names or contact details. Component checks of the script do not demonstrate effective use on future business inputs.
