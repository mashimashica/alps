# Brief: implement a receiving-review Skill

Create a self-contained Agent Skill and any needed working processing for the following established work description. Preserve the work's meaning and conditions. Design its supporting configuration and include implementation, connections and verification that can be done locally. This is design/implementation work, not permission to contact suppliers or alter real receiving records.

## Monthly Receiving Review

### Purpose

Make the month's purchase-order receipt position clear enough for the purchasing coordinator to direct the remaining receiving follow-up.

### Outcomes

- The receipt position of each in-scope order line is supported by the applicable order and receiving evidence.
- The follow-up needed for each unresolved line is identified with a responsible recipient and a concrete next action.
- Evidence gaps and their effects on affected line judgments are explicit.

### Work and conditions

The requested month, supplied purchase-order lines and declared receiving scope identify the review. The coordinator checks the scope and source data, calculates the signed received quantity, interprets the receipt position, and directs each necessary follow-up using the supplied responsibilities. Returning a calculation without deciding the follow-up does not finish this work.

An order line is identified by order_id and sku. Order quantities are positive integers. Receipt events have an event_id, order_id, sku, event_month and signed quantity. Negative quantities represent returns or correcting reversals and contribute algebraically. Events outside the requested month do not contribute. A manifest states whether the event export is complete for each order line and the requested month. Completeness is evidence, not something inferred from the number of rows. Missing information limits the affected judgment; unrelated sound evidence remains usable.

For a line with confirmed complete and valid evidence, compare net received with ordered quantity: equal means received as ordered; below means the remaining quantity needs follow-up; above means the excess quantity needs reconciliation. A partial export permits stating an observed subtotal, but not claiming the final receipt position. Do not replace missing values with zero. If supplied records contradict the order line's identity, or the same event_id has different content, identify the affected evidence conflict. Exact repeated copies of the same event count once.

For a complete shortfall the purchasing coordinator follows up with the order's supplier contact about the remaining receipt. For a complete excess the warehouse lead reconciles the surplus against the order and receiving evidence. For an incomplete export the data steward provides or confirms the full export before the affected final comparison. For conflicting order/event identity the purchasing coordinator and data steward reconcile the identified source records. Recipient names/addresses come from supplied responsibility information; do not invent them. Draft the follow-up; do not send it.

### Available information and environment

Python 3.12 and its standard library, a shell, and UTF-8 local files are available. No third-party package or external service is required. The target Skill can bundle scripts where needed. Local business inputs are supplied per use, not embedded in the Skill as permanent outcomes.

The input contract is ordinary JSON:

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

The identifiers and quantities illustrate the contract, not a review instance to complete. Choose and document a useful processing interface and response format. Make the agent's responsibility for interpreting the evidence and drafting the recipient-specific follow-up clear. Verify the components you implement; do not claim that component checks alone demonstrate every future agent's effective use.
