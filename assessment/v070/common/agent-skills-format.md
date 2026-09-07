# Common format information

Checked against the official [Agent Skills specification](https://agentskills.io/specification) on 2026-09-07.

A Skill is a folder with `SKILL.md`: YAML frontmatter followed by Markdown instructions. Required fields are `name` (1–64 lowercase ASCII letters, digits and hyphens, no leading/trailing or consecutive hyphens, matching the folder name) and a non-empty `description` of at most 1,024 characters describing capability and applicability. Optional supporting files can live in scripts/, references/ or assets/ when useful. The base format does not prescribe Markdown headings. Link necessary resources from the Skill; disclose detail when needed. The reference validator checks physical form, not successful business decisions.

The official [script guide](https://agentskills.io/skill-creation/using-scripts), checked on the same date, permits directly using existing commands. Bundle processing when it is useful, document dependencies and invocation, provide discoverable help and meaningful results/errors, and account for input ambiguity and effects of retries. Choose output and failure behavior that let the calling agent interpret what happened. A scripts/ directory is not itself a required deliverable.

This common orientation is not a replacement for either official source. It is the same in all comparison arms.
