# Measurement notes — snapshot 2026-06-29, 09:00 UTC

All dates below are UTC shipment dates. Each shipment belongs to one line and one order band. A standard order has one unit and one accessory set. A complex order has either multiple units or a customer-specific accessory configuration. The definitions did not change during the observation period.

## Shipment cohort extract

`shipment_cohorts.csv` has one row per shipment date, line, and order band. Counts are integers, and rows are mutually exclusive within each date and line.

- `shipped_orders`: all orders dispatched in that cohort, including orders whose downstream observation period is still open.
- `mature_orders`: orders for which the complete seven-calendar-day customer error observation window has elapsed at extraction. Every mature order had a deliverable customer contact address. In this extract cohorts mature together; no selective removal of orders occurred.
- `confirmed_mispack_7d`: distinct mature orders with a customer-confirmed wrong or missing packed item reported within seven calendar days of dispatch. Multiple issues on an order count once. This is the consistently recorded downstream quality outcome in both periods and lines. It does not include defects in the repaired equipment itself.
- `station_catches`: package-content issues caught before dispatch. Until June 12, staff recorded these only when a supervisor was called; from June 12, both lines' scanners require every catch to be entered. The column is useful process context but is not a consistently captured before/after outcome.

A zero in `mature_orders` means the complete observation window is unavailable, not that dispatched orders are error-free. `confirmed_mispack_7d` is zero in those rows because no orders yet qualify for that outcome, not because early customer reports were searched and none found. Do not add station catches to downstream errors: catches can be resolved before dispatch, and their recording changed.

## Shift operations extract

`shift_operations.csv` has one row for the whole packing line on a shipment date. It is not broken out by order band. Joining its hours to both band rows and summing them would double-count labor.

- `productive_labor_hours`: all paid line hours assigned to these shipments, including overtime and the separately identified training hours. Lunch and unrelated maintenance are excluded. The definition and clock source are unchanged across the packet.
- `overtime_hours`: a subset of productive labor hours, not additional hours to add to the total.
- `training_hours`: a subset of productive labor hours spent on one-off trial training. Routine verification work is already in productive hours and is not training.
- `late_dispatch_orders`: distinct orders that missed the site's promised carrier loading cutoff. All such orders are included in `shipped_orders` for the same date. This measure is immediately observable and does not need the seven-day maturity window.

The same crews worked the baseline and mature pilot dates, with no absences. June 26 was a shorter low-volume shift and is included because the manager asked for the latest available data, not because it is a matched full-shift capacity observation. There are no missing rows in this extract. Money and rate assumptions are in `decision_context.md`, not inferred from these counts.
