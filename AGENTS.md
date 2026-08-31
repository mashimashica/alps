# Repository Instructions

[Japanese translation](docs/locales/ja/AGENTS.md)

These instructions apply to the whole repository.

## Sources of Truth

- [`skills/design-process-description/SKILL.md`](skills/design-process-description/SKILL.md) is the authoritative English description of the only distributed Skill.
- Its three English files under `references/` are conditional design guidance linked from the root Skill.
- `skills/design-process-description/references/locales/ja/` contains the supported Japanese counterparts. English is authoritative; keep changed pairs semantically equivalent while preserving canonical names, paths, metadata keys, code literals, and normative force.
- [`skills/`](skills/) is the distribution source. `.agents/skills/design-process-description` is only a relative discovery symlink to that source.
- `.claude-plugin/`, `.codex-plugin/`, and `.cursor-plugin/` are non-authoritative Host adapters. They expose the single distributed Skill without adding behavior.

Do not add another distributed Skill, a second source of Process meaning, generated copies, or compatibility aliases unless a future repository requirement explicitly changes this boundary.

## Working in the Repository

- Inspect the current committed state and the complete task-owned diff before editing.
- Preserve unrelated and user-authored changes.
- Keep normally required instructions in the root Skill and move detail to one of the three existing references only when its reading condition is concrete.
- Keep reusable Process knowledge separate from one application, repository operation, and Host presentation metadata.
- Update the Japanese counterpart when an English user-facing source changes, and review the pair as ordinary documentation.
- Use relative Markdown links for repository content and keep one authoritative source for each information item.

## Validation

For a repository change, run the applicable ordinary checks:

- official Agent Skill validation for `skills/design-process-description`;
- root Agent Plugin and Host adapter validation;
- `python3 -m unittest discover -s tests -p 'test_*.py'`;
- relative Markdown link checking; and
- whitespace and final-diff checks.

Mechanical validation verifies form and repository integrity. It does not add Process meaning.

## Delivery

Inspect the final diff and report checks that passed, failed, or could not be run. Do not publish a release or tag unless the user explicitly requests it.
