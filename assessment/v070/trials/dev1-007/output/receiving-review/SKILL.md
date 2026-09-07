---
name: receiving-review
description: Review a month's purchase-order receiving evidence, determine each supplied order line's supported receipt position, expose evidence gaps, and draft recipient-specific follow-up without sending messages or changing records.
---

# Monthly Receiving Review

Use this skill when the user supplies the JSON contract for a monthly receiving review. The requested month and every supplied order line define scope; a coverage declaration never removes a line from scope.

## Responsibility and workflow

The agent owns interpretation of evidence and the decision about follow-up. Use the bundled deterministic processor for arithmetic, normalization, duplicate handling, and machine-detectable anomalies, then inspect its result and write the human-readable review. Do not treat a successful script run as proof that the review outcomes are achieved.

1. Validate that the input is JSON with `month`, `orders`, `events`, `coverage`, and `responsibilities`; validate dates, positive integer order quantities, required identifiers, and recipient fields. Report malformed or missing information rather than inventing values.
2. Run `python3 scripts/review_receiving.py INPUT.json [OUTPUT.json]`. The script is read-only and emits structured evidence for every in-scope line.
3. For each line, use only events in the requested month. Exact repeated copies of an event count once. A same-`event_id` content conflict is conflicting evidence, not a choice between rows. An event whose SKU is absent from its in-scope order is an identity-reconciliation issue. Events for orders outside the supplied order set do not affect in-scope totals.
4. Interpret status: complete valid evidence permits `received_as_ordered`, `shortfall`, or `excess`; incomplete evidence permits only an observed subtotal and `final_position_unconfirmed`; identity or event conflicts require reconciliation and prevent a final comparison. Never substitute missing values with zero.
5. Draft (do not send) a follow-up for every unresolved line, naming only supplied responsibility information: complete shortfall to the supplier contact/order's purchasing coordinator, complete excess to the warehouse lead, incomplete export to the data steward, and conflicting identity/evidence to the purchasing coordinator and data steward. State the concrete next action and evidence gap. If a required recipient is absent, mark the follow-up recipient unresolved.

## Response format

Return the requested month, scope and source assumptions, then one entry per order line containing ordered quantity, supported event evidence (including observed subtotal where applicable), coverage, judgment/status, evidence gaps, and follow-up recipient/action. Explicitly list out-of-scope events and unresolved limitations. Distinguish script output (processing evidence) from the agent's interpretation and drafts. Do not claim that calculations alone establish the Outcomes.

## Tool contract and limits

The script reads one UTF-8 JSON file and writes JSON to the optional output path (or stdout). Exit 0 means it processed the contract and may still report line-level gaps; exit 2 means invalid input and no trustworthy review should be inferred. It does not contact suppliers, send messages, or update receiving records. Re-run only after confirming the input path/content; outputs are replaceable derived evidence.

The implementation is intentionally deterministic and standard-library-only. Local checks can exercise valid, incomplete, duplicate, conflict, identity-mismatch, and out-of-scope cases; those checks establish component behavior, not every future agent's effective judgment.
