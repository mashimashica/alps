---
name: monthly-receiving-review
description: Review monthly purchase-order receiving evidence, calculate signed net receipts, distinguish confirmed positions from incomplete or conflicting evidence, and draft recipient-specific receiving follow-ups. Use when a purchasing coordinator needs a monthly receipt review from local JSON orders, events, coverage declarations and responsibilities.
---

# Monthly receiving review

Make the requested month's receipt position clear enough for the purchasing coordinator to direct remaining follow-up. A calculation alone is not a completed review.

## Inputs and local execution

Read [the contract and decision rules](references/contract.md). Obtain a UTF-8 JSON file supplied for this use. It contains the requested month, all in-scope order lines, receipt events, explicit coverage and named responsibilities. Do not embed business inputs or outcomes permanently in this Skill. Never invent contacts or assume missing values are zero.

Run with Python 3.12 and its standard library, using the actual installed Skill path:

```sh
python3 /path/to/monthly-receiving-review/scripts/review.py /path/to/input.json > /path/to/review.json
```

Use a new output path in the user's authorized work area. The script reads the input and writes JSON to stdout; it never edits records or sends messages. `--help` describes usage. Exit 0 means a review was produced, which may contain unresolved lines and routing gaps. Exit 2 means the document could not be reviewed; read the JSON error on stderr and correct the input before continuing. Identical inputs produce identical outputs. Rerunning to the same shell redirection path replaces that output.

## Interpret and finish the work

1. Check that `month`, `scope_line_count` and every line in `lines` represent the supplied scope. Coverage cannot remove lines. Inspect document `notices`, `invalid_orders` and each line's issues; resolve unexpected scope or identity problems with the coordinator and data steward. A structurally invalid document cannot support a completed review.
2. Check the evidence basis: accepted event IDs, excluded/problem records, signed observed subtotal, and coverage. Returns and reversals subtract. Only requested-month events contribute. The `observed_net` is a subtotal of accepted events; `final_net` and a final receipt position require complete, valid evidence. Zero is justified only by explicit complete coverage and no blocking evidence issues when there are no events.
3. Interpret every line: equal is received as ordered, below requires supplier follow-up for the remaining quantity, and above requires warehouse reconciliation of the surplus. For partial, missing or invalid coverage, report only the observed subtotal and request the full export. Identity conflicts take precedence over final comparison; retain any additional export request. Keep unaffected sound evidence usable.
4. Review every proposed `follow_ups` item. Verify its cause, affected records, owner, supplied recipient, exact action and draft against the input. Refine the wording for the coordinator while preserving the evidence limits. Complete shortfalls go from the purchasing coordinator to the order's supplier contact; complete excesses go to the warehouse lead; incomplete exports go to the data steward; order/event identity conflicts go to both the coordinator and data steward. Missing routing information requires a request to the user for the named role/contact; never replace it with an invented person. A draft with missing recipients is not ready to address or send.
5. Present a concise review: month and scope; a per-line table of ordered, observed net, coverage, supported position and remaining/excess quantity where final; explicit evidence gaps and their affected judgments; and recipient-specific follow-up drafts with owner and concrete next action. Include invalid order rows and unresolved recipient gaps. Explain why any line cannot yet receive a final comparison. Ensure each unresolved line has follow-up, including negative net receipt cases.

The processor is a decision aid. The agent remains responsible for checking the scope, interpreting the evidence and delivering useful drafts. Do not contact suppliers, send messages or alter real receiving records. A later request for those actions requires separate authorization.

## Component verification

Run the bundled standard-library checks:

```sh
python3 /path/to/monthly-receiving-review/scripts/test_review.py
```

These checks cover processor behavior and draft routing on synthetic fixtures. They do not establish every future agent's successful interpretation or end-to-end operational use.
