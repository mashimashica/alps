# Execution note

Created `output/checkout-service-release/` with a self-contained `SKILL.md` and bundled `references/release-tool-interface.md`.

## Resources used

- `input/brief.md`
- `input/release_tool.py` (read to document operations, mutation, exit codes, and timeout behavior)
- `../../common/agent-skills-format.md`
- Frozen candidate-B3 `design-agent-work-system/SKILL.md` and its required `design-process-description/SKILL.md`, Process Framework, and Agent Work System Design principles.

## Checks performed

- Inspected the authored files and confirmed the Skill folder contains `SKILL.md` plus its referenced bundled interface.
- Checked the frontmatter manually against the common format: folder/name match, lowercase hyphenated name, and non-empty description.
- Reviewed each documented operation against the supplied tool implementation, including qualification sequencing, approval matching, idempotent request IDs, timeout-after-mutation behavior, and independent probe/checkout results.

No business-instance simulation was run: no state file was supplied in the input, and the brief did not authorize performing a release instance. No external or state-changing action was performed. Consequently, end-to-end behavior across success, missing approval, timeout recovery, and checkout failure remains unconfirmed.
