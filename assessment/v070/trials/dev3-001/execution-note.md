# Execution note

Created `output/checkout-service-release` containing the self-contained Agent Skill.

Commands and checks performed:

- Read the task brief, common Agent Skills format orientation, frozen `design-agent-work-system` skill, its required design/process references, and frozen `skill-creator` guidance.
- Read the supplied `input/release_tool.py` to document its operations, state effects, approval matching, idempotent request behavior, and timeout behavior.
- Authored `SKILL.md` and `agents/openai.yaml` with `apply_patch`.
- No business release operation was run; no state file was supplied for an authorized instance.

Key choices: use the existing CLI directly; require exact candidate/digest qualification followed by matching owner approval; query request status before retrying an uncertain promotion; and require both production probe and checkout evidence for a successful release assessment.

Remaining limits: the skill was reviewed against the supplied interface and format requirements, but no end-to-end promotion or checkout simulation was performed because the brief did not authorize a business instance. The frozen validator was not run because its location was not part of the task-local supplied resources.
