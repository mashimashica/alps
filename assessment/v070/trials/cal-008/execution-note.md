# Execution note

## Result

Created the self-contained Agent Skill at `output/monthly-receiving-review/` with:

- `SKILL.md` for scope, workflow, evidence interpretation, follow-up ownership, no-send boundary, and verification guidance.
- `scripts/review_receipts.py`, a Python 3.12 standard-library JSON processor.
- `references/contract.md` for the input/output contract, duplicate/conflict behavior, and rerun effects.
- `tests/test_review_receipts.py` with eight behavioral tests.

## Supplied and official authoring resources used

- `input/brief.md`
- `common/agent-skills-format.md`
- `frozen/skill-creator/SKILL.md`
- `frozen/skill-creator/scripts/quick_validate.py`
- Official Agent Skills specification: `https://agentskills.io/specification`
- Official script guide: `https://agentskills.io/skill-creation/using-scripts`

No other trial or assessment material was inspected.

## Key design decisions

- Kept every usable supplied `(order_id, sku)` line in scope independently of coverage declarations.
- Used a deterministic script for signed in-month quantity arithmetic, exact-event deduplication, conflict localization, completeness handling, classification, and initial follow-up drafting.
- Preserved an observed subtotal while returning `undetermined` whenever coverage, order quantity, or attributable event evidence prevents a final comparison.
- Excluded all variants of a conflicting `event_id` from totals and surfaced affected lines. An in-month event with an unknown SKU blocks all lines for its in-scope order.
- Kept events from other months and orders outside the supplied order set visible in exclusion summaries without changing in-scope totals.
- Made missing recipient information explicit in `recipient_gaps`; the processor never invents names or addresses.
- Made all generated communication a draft with `sent: false`; the skill prohibits sending or changing business records without separate authorization.
- Kept record-level problems local when they can be associated with specific lines, allowing unrelated sound evidence to remain usable.

## Commands and checks performed

- Read the task prompt, supplied brief, common format guide, and frozen skill-creator instructions with `sed`.
- Listed only the permitted input and frozen authoring files with `rg --files`.
- Opened the two official Agent Skills documentation pages listed above.
- Ran `python3 -m unittest discover -s tests -p 'test_*.py' -v`: all 8 tests passed.
- Ran `python3 -m py_compile scripts/review_receipts.py tests/test_review_receipts.py`: passed.
- Ran `python3 scripts/review_receipts.py --help`: help and documented exit codes rendered successfully.
- Ran the CLI against an in-memory representative shortfall JSON through `/dev/stdin`: exit 0; it returned a 2-unit shortfall, the supplied coordinator and supplier contact, a concrete next action, and `sent: false`.
- Ran `python3 frozen/skill-creator/scripts/quick_validate.py output/monthly-receiving-review` using absolute trial paths: `Skill is valid!`.
- Listed final package files with `find` for package-hygiene review.

## Unperformed checks and missing information

- No live receiving system, supplier, warehouse, or messaging integration was available or authorized; no records were changed and no drafts were sent.
- No real review-instance JSON was supplied, so no actual month's business position was calculated.
- No delegated or end-to-end agent evaluation was performed because the task explicitly prohibited delegation. Local component checks do not prove every future agent will interpret all future evidence correctly.
- No third-party runtime or external service was needed.
