# Repository Instructions

[Japanese translation](docs/locales/ja/AGENTS.md)

These instructions apply to the repository. Follow the user's authorized scope and preserve unrelated work and user-authored data. `localization.yaml` defines English as the source locale and Japanese as supported.

## Sources

| Subject | Source |
| --- | --- |
| Process meaning, boundaries, references, change, and evaluation | [Process Framework](skills/design-process-description/references/process-framework.md) |
| Agent, tool, information, and environment design | [Design Principles for Agent Work Systems](skills/design-agent-work-system/references/agent-work-system-design.md) |
| Design work and its application to Agent Skills | [design-process-description](skills/design-process-description/SKILL.md) and [design-agent-work-system](skills/design-agent-work-system/SKILL.md) |
| Repository work and distribution | This file |
| Drafting aids | [Template](skills/design-process-description/references/SKILL-template.md) and [examples](skills/design-process-description/references/examples.md), both informative |

Do not infer Process requirements from tests, templates, Host manifests, icons, or other presentation resources. Read the complete `SKILL.md` for each Skill selected before applying it.

## Layout and distribution

| Path | Role |
| --- | --- |
| `skills/design-process-description/`, `skills/design-agent-work-system/` | Distributed Skills; each root English `SKILL.md` is the source for its Process. |
| `.agents/skills/<distributed-skill>` | Relative symlink to `../../skills/<distributed-skill>` for repository discovery. |
| `.agents/skills/review-alps/` | Real directory for repository semantic and distribution review; not a Plugin Skill. |
| `.agents/skills/sync-locales/` | Real directory for English/Japanese review; not a Plugin Skill. |
| Each Skill's `references/` | Principles and supporting material used by that Skill; each document's role determines its normative force. |
| `docs/locales/ja/` and each Skill's `references/locales/ja/` | Supported translations of the corresponding English source files. |
| `examples/` | Bundled reference material, including a working target Skill; outside Plugin Skill discovery. The guide's translation is in `examples/locales/ja/`, and the target Skill's translations are in its `references/locales/ja/`. |
| `plugin.json`, `.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/` | Root Plugin format and distinct Host adapters. |
| `assets/` and the Skill's `agents/` and `assets/` | Presentation resources. |

`skills/` is the source of Plugin Skills. Hosts discover it through their applicable conventions and manifests. `.agents/skills/` is an integrated repository view, not a universal Host convention. A checkout can contain development Skills without exposing them as Plugin Skills. Preserve the complete Plugin layout so references within and between Skills, and to `examples/`, remain usable. Keep development Skills and example Skills outside `skills/`.

## Change and review

- Inspect current files and the task-owned diff before editing. Preserve unrelated work.
- Use `review-alps` for changes to specifications, Skill content, repository guidance, tests, distribution, or presentation that affect their meaning or boundaries.
- Use `sync-locales` for each affected English/Japanese pair. Repository-development Skills have no Japanese Plugin counterparts.
- Use `design-process-description` when authoring or reviewing a Process Description.
- Use `design-agent-work-system` when designing or reviewing the supporting configuration, implementation, or effectiveness. Preserve shared work meaning and apply each foundation within its subject.
- Keep each Host adapter aligned with its native format and the distribution layout above.
- Apply [CONTRIBUTING](CONTRIBUTING.md) for contribution and licensing requirements and [Versioning](docs/versioning.md) for release policy.

## Verification and delivery

Keep the following evidence distinct:

1. Agent Skill and Plugin form validation against their applicable formats.
2. Repository integrity: required files, versions, relative links, symlinks, Host resources, and distribution boundaries.
3. Semantic review: purpose and Outcome sufficiency, required details and obligations, references, evaluation limits, and English/Japanese meaning and normative force.
4. Tool and connection verification against the specified behavior, including failures and incomplete results.
5. Work-system effectiveness through representative work with an agent, information, tools, and environment, assessed against the work's Outcomes and conditions.

Run the checks in `.github/workflows/validate.yml` that the environment permits. At minimum run `python3 -m unittest discover -s tests -v`, `git diff --check`, changed-link checks, and review the complete task-owned diff, including new files. Passing mechanical checks does not prove semantic validity or successful Process execution.

Report findings, completed checks, failed or unperformed checks, and limits.
