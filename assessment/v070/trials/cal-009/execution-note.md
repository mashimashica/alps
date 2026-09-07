# Execution note

Created `output/checkout-release/SKILL.md` as a self-contained Agent Skill for the synthetic checkout release workflow.

## Commands and checks performed

- Read the task brief, common Agent Skills format orientation, frozen `design-agent-work-system` guidance, linked frozen `design-process-description` guidance, and frozen `skill-creator` guidance.
- Listed and read the supplied `input` files.
- Read the supplied `input/release_tool.py` to document its operations, exact candidate/digest gates, idempotent request IDs, and timeout behavior.
- Authored the Skill with `apply_patch`.
- No release-tool operation was run because no business application state file or authorized release request was supplied; no external or state-changing action was performed.

## Design decisions and limits

The Skill requires exact candidate, digest, qualification, subsequent service-owner approval, and stable request-ID handling. It explicitly reconciles uncertain promotion effects before retrying and requires both production probe and checkout evidence. The output is unverified against a live or simulated state because none was supplied. The frozen format validator was not run because its location was not part of the supplied resources inspected for this task.
