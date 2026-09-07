---
name: receiving-review
description: Review a month's purchase-order receipt evidence line by line, calculate supported receipt positions, expose evidence gaps, and draft recipient-specific receiving follow-up. Use when a user supplies orders, receipt events, coverage declarations, and responsibilities in the documented JSON contract. This skill drafts follow-up only; it does not send messages or change receiving records.
---

# Monthly receiving review

Use this skill to make a supplied month's purchase-order receipt position actionable for the purchasing coordinator. The supplied order lines define scope for the requested month. A coverage declaration describes evidence completeness; it never removes an order line from scope.

## Processing

For a repeatable calculation, run the bundled standard-library script from the skill directory:

```bash
python3 scripts/review_receipts.py INPUT.json --output REPORT.json --pretty
```

Use `--help` for the interface. `INPUT.json` must contain `month` (`YYYY-MM`), `orders`, `events`, `coverage`, and `responsibilities` as described in [references/interface.md](references/interface.md). The script writes a JSON report and exits nonzero with a useful error on malformed input; it never writes to the input file. Review the report's issues and source details before presenting conclusions.

The agent remains responsible for interpreting the report, explaining evidence limits, and drafting the actual follow-up. Do not treat a successful script run as proof that the business decision is correct.

## Evidence rules

- Identify an order line by `(order_id, sku)`. Validate that each ordered quantity is a positive integer. Keep every supplied line in the report, including lines with no coverage declaration or no events.
- Count an event only once when exact repeated copies share an `event_id`. Sum signed quantities for the requested month; negative quantities are returns or reversals. Events from other months contribute nothing. An event for an order outside the supplied order set is outside this review.
- Use the manifest's `complete` value as evidence. Do not infer completeness from row counts. A missing or false declaration limits the affected line to an observed subtotal and prevents a final receipt-position claim. Never substitute a missing value with zero.
- If a current-month event names an in-scope order but a SKU absent from that order, hold the affected order's final comparisons for identity reconciliation. If one `event_id` has different content, hold every referenced in-scope line as conflicting evidence; exact duplicates are harmless.
- When evidence is complete and valid, compare net received with ordered: equal is `received_as_ordered`, below is `shortfall`, and above is `excess`. Report the remaining or surplus quantity.

The report's `follow_up` is a draft and must remain unsent. For a complete shortfall, address the order's supplied `supplier_contact`. For a complete excess, address the supplied `warehouse_lead`. For incomplete evidence, address the supplied `data_steward`. For order/event identity reconciliation or conflicting evidence, address both the supplied `purchasing_coordinator` and `data_steward`. If a recipient is absent from the input, state that the recipient is unavailable rather than inventing a name or address. A line can have a supported observed subtotal and still require follow-up because its final position is unknown.

## Response

Present the requested month, scope-line results, observed and final quantities, evidence sources, issues, and one draft follow-up for every unresolved line. Distinguish `observed_received` from a final position, call out ignored out-of-scope events, and state any unavailable recipient. Include enough event IDs and coverage information for the coordinator to trace each judgment. Never claim that a message was sent or that a receiving record was changed.

