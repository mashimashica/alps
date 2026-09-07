# Interface and decision contract

Supply a JSON object with:

| Field | Required value |
| --- | --- |
| `month` | Real calendar month string `YYYY-MM`, year 0001–9999 |
| `orders` | Array of objects: nonempty string `order_id`, nonempty string `sku`, positive integer `ordered`, supplied string `supplier_contact` for supplier routing |
| `events` | Array of objects: nonempty string `event_id`, `order_id`, `sku`, valid `event_month`, signed integer `quantity` |
| `coverage` | Array of objects: nonempty string `order_id`, `sku`, valid `month`, boolean `complete` |
| `responsibilities` | Object containing supplied strings `purchasing_coordinator`, `warehouse_lead`, `data_steward` |

Whitespace-only identifiers and contacts are missing. Identifiers match exactly; do not trim or normalize them. Booleans are not integers. Missing contacts/roles affect routing, not valid receipt arithmetic. Missing/mistyped arrays, month, responsibilities, invalid JSON, duplicate JSON object keys and non-finite JSON numbers are document errors (exit 2). Empty arrays are allowed. Missing per-record fields are evidence issues, never numeric defaults. Unrecognized fields are retained in event/order duplicate comparisons and otherwise ignored.

## Scope, deduplication and evidence

- Each distinct supplied `(order_id, sku)` is a line, regardless of coverage. Exact repeated order rows are coalesced with a notice. Differing order rows with the same key block that line, including differing supplier contacts: reconcile the source records before final comparison. Unidentifiable order rows appear in `invalid_orders`; identifiable lines remain reviewable, but the scope has unresolved rows.
- Exact repeated event objects count once. Any different event objects sharing the same valid `event_id` conflict. Requested-month in-scope versions are excluded and their affected lines blocked; variants outside the month remain noncontributing but can establish that the ID is reused inconsistently. All variants' record indexes are reported. This deliberately treats extra-field differences as conflicting content rather than silently assuming they are irrelevant.
- An event for a known different month does not contribute or block that month's review. An event with an order outside the supplied identifiable order set is outside scope and does not change totals. A current-month unknown SKU on an in-scope order blocks all that order's lines for identity reconciliation. Missing/malformed SKU does likewise when the month is current or unknown. A malformed month blocks the identifiable affected line because temporal membership is unknown. An unidentifiable event order or non-object event with a current/unknown month blocks all scoped lines because attribution is unknown; do not allocate its quantity.
- Only valid, nonconflicting, requested-month events for known lines contribute to `observed_net`. Invalid quantities/IDs block affected lines and are excluded. Any observed subtotal is explicitly a subtotal of accepted events, not a replacement for the excluded quantities. Accepted events may still have a subtotal on a blocked line.
- Coverage is explicit for the key and requested month. `complete: true` confirms completeness; `false` is partial; absent is missing. Repeated identical applicable declarations agree. Contradictory true/false declarations or invalid applicable declarations produce invalid coverage. Malformed coverage months for a known key make its coverage uncertain. Other-month and out-of-scope declarations are ignored with notices. No event count implies completeness.
- If evidence is valid and coverage complete, compare algebraic net with positive ordered quantity. A negative net can create a remaining quantity larger than the original order; report it faithfully. Incomplete coverage permits an observed subtotal only. Evidence problems block final comparison even when coverage claims completeness.

## Output JSON

`schema_version` is 1. Top-level `month`, `scope_line_count`, `lines`, `invalid_orders` and `notices` describe the review. Record indexes are zero-based indexes into the original input arrays. Each line includes original order record indexes, ordered quantity or null, coverage (`complete`, `partial`, `missing`, `invalid`), `observed_net`, `accepted_event_ids`, `issues`, `receipt_position`, `final_net`, `remaining`, `excess`, and `follow_ups`.

Positions are `received_as_ordered`, `shortfall`, `excess`, `not_final` (coverage limitation), or `blocked` (invalid/conflicting evidence). Null final quantities mean no supported final comparison. `remaining` and `excess` are populated only for their corresponding final positions. Issues include source record indexes in their messages. `invalid_orders` have their own reconciliation follow-up.

Follow-ups contain `kind`, `owners`, `recipients`, `missing_roles`, `action`, `draft`, and `ready_to_address`. Supplier drafts identify both the coordinator owner and supplied supplier recipient. Identity reconciliation uses both named coordinator and steward. Invalid quantity or coverage repair uses the steward; an identity-conflicted line with incomplete coverage also gets an export request. Missing contact roles are explicit and make the draft unready. Output is a local draft, never evidence that a message was sent.

Configuration is supplied through `responsibilities` and each order's `supplier_contact`; month and evidence are runtime inputs. No external connection, credentials, service or package is required. Local integration reads the JSON file, checks the exit code, parses output, and has the agent finish the review using `SKILL.md`.
