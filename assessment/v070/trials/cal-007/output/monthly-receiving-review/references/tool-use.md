# Receipt review processor

`scripts/review_receipts.py` validates and normalizes the supplied JSON, deduplicates receipt events, calculates uncontested current-month net quantities, classifies lines whose evidence permits a final comparison, and returns explicit evidence and routing information. It does not write to business systems, send follow-up, or replace the agent's interpretation and drafting responsibility.

Python 3.12 or later and its standard library are the only dependencies. Run from the Skill directory, or use absolute paths.

```console
python3 scripts/review_receipts.py INPUT.json
python3 scripts/review_receipts.py INPUT.json --output result.json
python3 scripts/review_receipts.py - < INPUT.json
```

Use `--help` for the command interface. Input `-` reads bytes from standard input. Output defaults to one UTF-8 JSON object on standard output; `--output PATH` writes the object to that path after processing succeeds. The operation never modifies its input. Avoid using the same path for input and output.

## Input contract

The root object must contain:

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

Identifiers and contacts must be nonempty strings. `ordered` must be a positive integer, `quantity` a signed integer, completeness a Boolean, and month fields valid `YYYY-MM` values. Boolean values are not accepted as integers. Additional object fields are preserved only by the source file; they do not change processing.

A malformed JSON document, wrong root/container type, or invalid requested month is a fatal interface error. Record-level defects are reported where they can be localized so valid unrelated lines remain usable. An order record with no valid line identity appears in `scope_issues`; because the complete supplied scope cannot then be represented, the overall review remains incomplete even if other lines are usable.

## Output contract

The result has `schema_version: "1.0"`, the requested month, an input byte count and SHA-256 digest, normalized supplied responsibilities, top-level scope/evidence exclusions and issues, line results, and a summary.

Each line contains:

- `order_id`, `sku`, `ordered`, and the supplied `supplier_contact` when usable.
- `coverage_status`: `complete`, `incomplete`, `missing`, `invalid`, or `conflicting`.
- `included_event_ids` and `observed_uncontested_net_received`. The subtotal includes each valid, unique, nonconflicting, matching current-month event exactly once.
- `evidence_findings`, including record indexes and event identifiers where available.
- `position`: `received_as_ordered`, `shortfall`, `excess`, or `unconfirmed`, plus `position_is_final`.
- `remaining_quantity` or `excess_quantity` only for the corresponding final position.
- `follow_ups`, each with a machine-readable `type`, concrete `next_action`, relevant evidence identifiers, and supplied parties. A party value is `null` when its required source field is missing.
- `recipient_gaps` listing any missing supplier or responsibility field needed to direct that line's follow-up.

`coverage_status: complete` is necessary but not sufficient for a final position: conflicting or invalid order/event evidence also blocks the comparison. Exact repeated copies of one event are counted once and listed in the top-level duplicate summary. Different content under the same `event_id` is excluded from totals and blocks affected lines. A current-month event with an in-scope order and unknown SKU blocks every supplied line for that order until identity is reconciled. Current-month events for orders outside the supplied set are listed as outside scope and never create or change an in-scope total.

The summary counts positions and unresolved lines. `all_supplied_scope_represented` is false when a supplied order record cannot be represented as a unique valid line. `all_line_positions_final` concerns represented lines only. Neither field means the agent has completed evidence interpretation or drafted the required follow-up.

## Failures, retries, and reproducibility

Exit status `0` means processing completed, including when evidence is incomplete or a line remains unconfirmed. Exit status `2` writes a diagnostic to standard error and emits no JSON result when the document cannot be read, parsed, or used through the root interface, or when the output cannot be written.

Correct the stated input/access problem before retrying exit `2`. The script reads the input once and identifies those bytes by digest. The result is deterministic for the same bytes and Python behavior, except that an input path or output formatting location may differ. Use a stable copy if the source can change during the review.

