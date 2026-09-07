# Input and output interface

## Input

Pass one UTF-8 JSON object to `scripts/review_receiving.py`. The top-level fields are:

| Field | Required shape | Meaning |
| --- | --- | --- |
| `month` | `"YYYY-MM"` | Review month. |
| `orders` | array | In-scope lines. Each line has non-empty `order_id`, non-empty `sku`, positive integer `ordered`, and `supplier_contact`. |
| `events` | array | Receipt evidence. Each event has non-empty `event_id`, `order_id`, `sku`, valid `event_month`, and signed integer `quantity`. |
| `coverage` | array | Export declarations with `order_id`, `sku`, `month`, and Boolean `complete`. |
| `responsibilities` | object | Supplied names/addresses for `purchasing_coordinator`, `warehouse_lead`, and `data_steward`. |

The input file is read-only. Array order is not significant. JSON integers must not be Booleans.

## Invocation

```bash
python3 scripts/review_receiving.py INPUT.json
python3 scripts/review_receiving.py INPUT.json --output REVIEW.json
```

Exit code `0` means a review was produced. Review-level evidence gaps can still be present and must be handled. Exit code `2` means the file, JSON, or top-level review scope could not be processed; the diagnostic is written to standard error. `--output` is written atomically after processing succeeds.

## Output

The output is a UTF-8 JSON object:

- `review_month` and `scope` describe the requested review.
- `input_issues` reports non-fatal row or responsibility problems. Each issue identifies its source where possible.
- `ignored` reports out-of-month events, events for orders outside scope, and coverage declarations that do not apply to an in-scope line/month.
- `lines` contains one result per identifiable supplied order line.

Each line includes:

| Field | Interpretation |
| --- | --- |
| `ordered` | Supplied ordered quantity, or `null` when invalid. |
| `observed_net_received` | Sum of accepted, unique, non-conflicting current-month events. It remains only a subtotal when evidence is incomplete or blocked. |
| `final_net_received` | Final net quantity only when order, event, identity, and completeness evidence support comparison; otherwise `null`. |
| `receipt_position` | `received_as_ordered`, `shortfall`, `excess`, or `undetermined`. |
| `difference_from_order` | `final_net_received - ordered` when final, otherwise `null`. |
| `coverage_status` | `complete`, `incomplete`, `missing`, `conflicting`, or `invalid`. |
| `evidence_gaps` | Specific reasons a final judgment or follow-up recipient is limited. |
| `follow_up` | Suggested recipient-specific actions and unsent drafts. |

`observed_net_received: 0` means the accepted event subtotal is numerically zero. It does not assert that no receipts exist. Use `final_net_received` and `receipt_position` to distinguish a supported final comparison from an incomplete subtotal.

Follow-up records contain `reason`, `responsible_role`, `responsible`, `recipient`, `next_action`, and `draft`. A missing supplied identity appears as `null`, and the draft is withheld rather than populated with an invented name.
