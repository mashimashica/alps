# Execution note

Created `output/checkout-release/SKILL.md` for the synthetic checkout-service release brief.

## Resources used

- `input/brief.md`
- `input/release_tool.py`
- `common/agent-skills-format.md`
- Frozen `skill-creator/SKILL.md`
- Frozen candidate-B1 `design-agent-work-system/SKILL.md`, `design-process-description/SKILL.md`, Process Framework, and Agent Work System Design principles.

## Commands/checks performed

- Read the supplied brief, authoring guidance, required design skills, and the supplied release tool source.
- Authored the target Skill with `apply_patch`.
- No business-instance release operation was run; no state file was supplied for an authorized instance.
- No external repository, deployment service, customer state, or live production system was accessed.

## Design choices and limits

The Skill keeps judgment with the agent (exact candidate, approval basis, interpretation of uncertain effects) and uses the supplied CLI for deterministic inspection, qualification, promotion, request-status, health, and checkout operations. It explicitly separates command completion from release outcomes and requires post-promotion health and checkout evidence. The physical format and frontmatter were not validated with the frozen validator because its location was not needed to author the self-contained folder; only structural inspection was performed.
