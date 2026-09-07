# Input and report interface

The processor accepts one UTF-8 JSON object:

```json
{
  "month": "YYYY-MM",
  "orders": [
    {"order_id": "PO-100", "sku": "PEN", "ordered": 12,
     "supplier_contact": "Aya at Example Supplies"}
  ],
  "events": [
    {"event_id": "E-1", "order_id": "PO-100", "sku": "PEN",
     "event_month": "YYYY-MM", "quantity": 8}
  ],
  "coverage": [
    {"order_id": "PO-100", "sku": "PEN", "month": "YYYY-MM",
     "complete": true}
  ],
  "responsibilities": {
    "purchasing_coordinator": "Mina (purchasing)",
    "warehouse_lead": "Ren (warehouse)",
    "data_steward": "Sora (receiving data)"
  }
}
```

`order_id`, `sku`, and `event_id` are non-empty strings. `ordered` is a positive integer. Event `quantity` is an integer and may be negative or zero. The script validates month shape and the required structural fields. Recipient values are allowed to be absent or empty so the report can expose an unavailable responsibility without inventing one.

The JSON report contains:

- `scope_lines`: one entry per supplied order line. Each entry includes `observed_received`, the deduplicated current-month event IDs used for that subtotal, coverage evidence, `issues`, `status`, and a `follow_up` draft when action is required.
- `status`: `received_as_ordered`, `shortfall`, `excess`, `incomplete_export`, `coverage_missing`, `coverage_conflict`, `identity_reconciliation_required`, or `conflicting_evidence`.
- `final_received` and `remaining_or_surplus` only when a complete, valid final comparison is supported. An observed subtotal is not a final position.
- `global_issues`, `ignored_out_of_scope_event_ids`, and `summary` for review-wide context.

The processor excludes all variants of a conflicting `event_id` from arithmetic and reports the affected line. It also reports current-month in-scope-order events whose SKU does not match an order line. These choices make an ambiguous event visible instead of silently choosing a value.

