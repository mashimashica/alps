# Input and output contract

## Input

The processor accepts one JSON object:

```json
{
  "month": "2026-08",
  "orders": [
    {
      "order_id": "PO-100",
      "sku": "PEN",
      "ordered": 12,
      "supplier_contact": "Aya at Example Supplies"
    }
  ],
  "events": [
    {
      "event_id": "E-1",
      "order_id": "PO-100",
      "sku": "PEN",
      "event_month": "2026-08",
      "quantity": 8
    }
  ],
  "coverage": [
    {
      "order_id": "PO-100",
      "sku": "PEN",
      "month": "2026-08",
      "complete": true
    }
  ],
  "responsibilities": {
    "purchasing_coordinator": "Mina (purchasing)",
    "warehouse_lead": "Ren (warehouse)",
    "data_steward": "Sora (receiving data)"
  }
}
```

`month` and event/coverage month values use `YYYY-MM`. Each valid order is keyed by `(order_id, sku)` and has a positive integer `ordered` quantity. Each event has a nonempty `event_id` and a signed integer `quantity`; negative values contribute algebraically. Boolean values are not accepted as integers.

The root object, `month`, and the four collection fields must have the shown JSON types. Unusable root structure is a fatal contract error. Invalid individual records become diagnostics so valid, unrelated order lines can still be reviewed. An order row without a usable `(order_id, sku)` cannot define a line and appears only as a diagnostic.

## Output

The output is a JSON object with these major fields:

- `review_month`: requested month.
- `summary`: counts of supplied/usable order rows, in-scope lines, final positions, undetermined lines, follow-ups, and evidence gaps.
- `lines`: one result per usable in-scope `(order_id, sku)`.
- `excluded_events`: counts and identifiers for valid unique events excluded because they are outside the requested month or supplied order set.
- `diagnostics`: structured input and evidence issues. Each diagnostic has a code, severity, message, and when possible an order/line or source-row reference.

Each line result contains:

- `ordered_quantity`: the agreed positive order quantity, or `null` for conflicting duplicate order rows.
- `observed_net_received_quantity`: algebraic total of valid, unique, non-conflicting requested-month events attributed to the exact line. This is an observed subtotal when evidence is incomplete.
- `position`: `received_as_ordered`, `shortfall`, `excess`, or `undetermined`.
- `difference_quantity`: `ordered_quantity - observed_net_received_quantity` for final shortfalls, `observed_net_received_quantity - ordered_quantity` for final excesses, `0` for received as ordered, and `null` when undetermined.
- `coverage_state`: `complete`, `incomplete`, `missing`, or `conflicting`.
- `evidence`: counted event IDs, exact-repeat count, blockers, and relevant diagnostic codes.
- `follow_up`: `null` only for `received_as_ordered`; otherwise it contains a reason, owners, recipient gaps, next action, and draft text.

An `owners` entry contains a role and the supplied recipient string, or `null` when missing. A shortfall also uses `supplier_contact` as the external recipient. Missing responsibility or supplier information is reported rather than replaced.

## Duplicate and conflict rules

- Exact duplicate order rows collapse to one line. Different rows for the same line key make that line's order evidence conflicting.
- Exact duplicate coverage rows collapse. Different `complete` values for the same line and requested month make coverage conflicting.
- Exact duplicate event rows count once. Any different content under one `event_id` makes that ID conflicting; no variant contributes to a total.
- A conflicting event ID affects requested-month in-scope line variants. If such a variant names an in-scope order but an unknown SKU, every line on that order is affected.
- A valid requested-month event on an in-scope order with an unknown SKU blocks every line on that order. Events on an order absent from the supplied order set remain outside scope.

## Reruns and effects

The script only reads the input and writes JSON to standard output or the explicitly supplied `--output` path. Re-running with the same input deterministically replaces that output file. It has no network or business-system side effects.
