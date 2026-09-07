# Processing contract

Read this reference when creating an input file, diagnosing validation output, or mapping processor results into the review.

## Invocation

```bash
python3 "<skill-directory>/scripts/review_receiving.py" INPUT.json [--output REVIEW.json]
```

Replace `<skill-directory>` with the path of the Skill folder. Input and output paths follow the caller's current working directory.

Without `--output`, JSON is written to standard output. Diagnostics are written to standard error. Exit code `0` means the file was processed, including reviews that contain evidence gaps. Exit code `2` means the input could not be processed because the JSON, requested month, or required top-level collections were unusable, or because a file operation failed.

## Input

The UTF-8 input is one JSON object:

```json
{
  "month": "YYYY-MM",
  "orders": [
    {"order_id": "PO-100", "sku": "PEN", "ordered": 12, "supplier_contact": "Aya at Example Supplies"}
  ],
  "events": [
    {"event_id": "E-1", "order_id": "PO-100", "sku": "PEN", "event_month": "YYYY-MM", "quantity": 8}
  ],
  "coverage": [
    {"order_id": "PO-100", "sku": "PEN", "month": "YYYY-MM", "complete": true}
  ],
  "responsibilities": {
    "purchasing_coordinator": "Mina (purchasing)",
    "warehouse_lead": "Ren (warehouse)",
    "data_steward": "Sora (receiving data)"
  }
}
```

`order_id`, `sku`, `event_id`, and supplied contact values are non-empty strings. `ordered` is a positive integer. `quantity` is a signed integer. Booleans are not accepted as integers. `complete` is a Boolean. The requested month, event months, and coverage months use `YYYY-MM`.

The processor keeps identifiable order lines in scope even when their other fields are invalid. An order record whose line identifiers are unusable is reported in `unassigned_issues` because it cannot be safely mapped. Missing or unusable required top-level collections are blocking rather than being treated as empty.

## Output

The JSON object contains:

- `review_month` and `review_summary`: supplied record, identifiable line, unidentifiable record, resolution, and follow-up counts.
- `lines`: one result for each identifiable supplied order line. `observed_subtotal` totals valid, unique, matching events for the requested month. `final_net_received` and `variance_received_minus_ordered` are numbers only when evidence supports a final comparison; otherwise they are `null`.
- `evidence_status`: `complete`, `incomplete_export`, `conflicting_evidence`, `identity_reconciliation`, or `invalid_evidence`.
- `position`: `received_as_ordered`, `shortfall`, `excess`, or `undetermined`.
- `evidence_gaps`: line-specific reasons that qualify or block a conclusion.
- `follow_up`: the responsible role or roles, the supplied recipient values, a concrete action, and a factual `draft_basis`. A missing supplied contact remains `null` and is also identified as a gap.
- `outside_scope_events`: event IDs belonging to orders outside the supplied order set. These never affect in-scope totals.
- `ignored_other_month_event_ids`: unique events for in-scope orders that have a valid event month different from the requested month.
- `unassigned_issues`: malformed evidence that cannot be safely assigned to an identifiable in-scope line.
- `processing_notes`: deduplication and interpretation details.

Exact duplicate order, event, and coverage records are processed once. If one `event_id` has different content, none of its variants contributes and each potentially affected in-scope line is flagged. Coverage records for another month do not establish requested-month completeness. A successful processor run may still contain `undetermined` lines; the calling agent must review and explain them.
