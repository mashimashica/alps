# Execution note

Created `output/receiving-review` with a self-contained `SKILL.md` and the deterministic helper `scripts/review_receipts.py`.

## Resources used

- The task-local `input/brief.md`.
- `common/agent-skills-format.md`.
- The frozen `skill-creator/SKILL.md` and its `quick_validate.py` helper.
- Frozen candidate-B2 `design-agent-work-system/SKILL.md`, its design principles reference, and the linked `design-process-description` Skill, Process Framework, and minimal template.

## Commands/checks performed

- Ran the bundled script with a representative complete-coverage shortfall JSON input through stdin; confirmed algebraic total, event ID, coverage, and `shortfall` position in JSON output.
- Ran `python3 .../skill-creator/scripts/quick_validate.py output/receiving-review`; result: `Skill is valid!`.

## Design choices

The helper owns repeatable validation, exact event deduplication, month/scope filtering, algebraic totals, coverage gating, identity-issue detection, and conflicting-event detection. The Skill leaves evidence interpretation and recipient-specific drafting to the agent because those require contextual judgment and supplied responsibility/contact information. The output explicitly distinguishes observed subtotals from final positions and keeps follow-up drafting separate from sending.

## Remaining limits

No live receiving records, suppliers, external services, or future business instance were accessed. The component check does not prove an agent will correctly interpret every evidence pattern or produce effective follow-up; representative end-to-end agent use remains to be evaluated by the parent workflow.
