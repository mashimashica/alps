# Execution note

## Artifacts

- Skill: `deliverables/skills/receiving-review/`
- Entrypoint: `deliverables/skills/receiving-review/SKILL.md`
- Processor: `deliverables/skills/receiving-review/scripts/review_receipts.py`
- Interface reference: `deliverables/skills/receiving-review/references/interface.md`

## Checks performed

All commands below were run from the trial directory with Python 3 and the supplied frozen authoring helper.

1. `python3 ../../frozen/skill-creator/scripts/quick_validate.py deliverables/skills/receiving-review`
   - Exit `0`; output: `Skill is valid!`
2. `python3 -m py_compile deliverables/skills/receiving-review/scripts/review_receipts.py`
   - Exit `0`.
3. `python3 deliverables/skills/receiving-review/scripts/review_receipts.py --help`
   - Exit `0`; displayed the positional JSON input, `--output`, and `--pretty` options.
4. A disposable synthetic JSON input exercised complete shortfall and excess, incomplete and missing coverage, conflicting coverage, exact duplicate events, conflicting event IDs, a current-month event for an absent SKU, an out-of-scope order event, and an out-of-month event. The processor wrote a report and exited `0`. The observed status counts were:
   `conflicting_evidence=1`, `coverage_conflict=1`, `coverage_missing=2`, `excess=2`, `identity_reconciliation_required=1`, `incomplete_export=1`, `shortfall=1`.
   The out-of-scope event ID was reported in `ignored_out_of_scope_event_ids`; the exact duplicate was counted once.
5. A disposable signed-quantity input with `12` and `-2` events for an ordered quantity of `10` exited `0` and reported `received_as_ordered` with `final_received=10`.
6. A disposable malformed input with a missing event quantity exited `2` and printed `events[0].quantity must be an integer` to stderr.
7. After the final processor adjustment, the quick validator, `py_compile`, and `--help` checks were rerun; each exited `0` (the validator again printed `Skill is valid!`).

The synthetic inputs and generated reports were removed after the checks. Supplied inputs were not modified.

## Design choices and limits

The processor emits one result for every supplied `(order_id, sku)` line, keeps observed subtotals separate from final positions, deduplicates exact event copies, excludes all variants of conflicting event IDs from arithmetic, and records recipient-specific drafts without sending them. Missing responsibility values remain `null` in drafts. The agent using the skill must still inspect issues, explain evidence effects, and decide how to present the review; successful script validation does not demonstrate effective use by every future agent or validate external receiving records.
