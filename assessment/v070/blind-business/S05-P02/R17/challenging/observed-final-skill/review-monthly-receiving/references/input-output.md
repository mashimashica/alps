# Input and output contract

The input is one UTF-8 JSON object with `month`, `orders`, `events`, `coverage`, and `responsibilities`. `month` and coverage/event months use `YYYY-MM`. Each order has `order_id`, `sku`, a positive integer `ordered`, and a non-empty `supplier_contact`. Each event has non-empty `event_id`, `order_id`, `sku`, `event_month`, and an integer signed `quantity`. Each coverage row has `order_id`, `sku`, `month`, and Boolean `complete`. Responsibilities must name `purchasing_coordinator`, `warehouse_lead`, and `data_steward`.

An order line key is the pair `(order_id, sku)`, which must be unique in `orders`. Coverage for every supplied line and requested month should be present and internally consistent. Extra coverage rows are reported but do not expand scope.

The output has:

- `month` and `summary`, including counts by disposition.
- `lines`, one per supplied order line. Each contains ordered quantity, `observed_net_received`, evidence state, disposition, variance when a final comparison is allowed, explicit issues, and zero or more follow-up drafts.
- `scope_issues`, for review-level evidence or contract concerns that do not invalidate JSON parsing.
- `outside_scope_events`, listing event IDs for orders outside the supplied order set.

Disposition values are `received_as_ordered`, `shortfall`, `excess`, or `indeterminate`. Follow-up objects contain `owner`, `recipient`, `action`, and `draft`. These are drafts only. For incomplete evidence, the data steward owns export completion. For a complete shortfall, the purchasing coordinator owns supplier follow-up. For a complete excess, the warehouse lead owns reconciliation. Identity conflicts are assigned jointly to the purchasing coordinator and data steward.

Use `python3 scripts/review_receiving.py --help` for command options. Without `--output`, JSON is written to standard output. Input/contract errors go to standard error and exit with status 2; the tool does not emit a partial review for structurally invalid input.
