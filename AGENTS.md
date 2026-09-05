# Repository Instructions

[Japanese translation](docs/locales/ja/AGENTS.md)

These instructions apply to the repository. Follow the user's authorized scope and preserve unrelated work and user-authored data. `localization.yaml` defines English as authoritative and Japanese as supported.

## Authority

| Subject | Source |
| --- | --- |
| Process meaning, boundaries, references, change, and evaluation | [Process Framework](spec/process-framework.md) |
| Mapping a Process Description to an Agent Skill | [ALPS Specification](spec/ALPS-SPEC.md), subordinate to the Framework |
| The distributed design Process | [design-process-description](skills/design-process-description/SKILL.md) |
| Repository work and distribution | This file |
| Drafting aids | [Template](skills/design-process-description/references/SKILL-template.md) and [examples](skills/design-process-description/references/examples.md), both informative |

Do not infer Process requirements from tests, templates, Host manifests, icons, or other presentation resources. Read the complete `SKILL.md` for each Skill selected before applying it.

## Layout and distribution

| Path | Role |
| --- | --- |
| `skills/design-process-description/` | The only distributed Skill; its root English `SKILL.md` is authoritative. |
| `.agents/skills/design-process-description` | Relative symlink to `../../skills/design-process-description` for repository discovery. |
| `.agents/skills/review-alps/` | Real directory for repository semantic and distribution review; not a Plugin Skill. |
| `.agents/skills/sync-locales/` | Real directory for English/Japanese review; not a Plugin Skill. |
| `spec/` | Shared normative sources included in the Plugin root. |
| `spec/locales/ja/`, `docs/locales/ja/`, and the distributed Skill's `references/locales/ja/` | Supported translations; no second authority. |
| `plugin.json`, `.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/` | Root Plugin format and distinct Host adapters. |
| `assets/` and the Skill's `agents/` and `assets/` | Presentation resources. |

`skills/` is the sole distribution source. Hosts discover it through their applicable conventions and manifests. `.agents/skills/` is an integrated repository view, not a universal Host convention. A checkout can contain development Skills without exposing them as Plugin Skills. Preserve the Plugin root layout so required links to `spec/` remain usable. Do not copy development Skills into `skills/`.

## Change and review

- Inspect current files, ownership, and the complete task-owned diff before editing. Use the current source and requested target to judge changes; inspect history only when authorized and relevant.
- Use `review-alps` for changes to specifications, Skill content, repository guidance, tests, distribution, or presentation that affect their meaning or boundaries.
- Use `sync-locales` for each affected English/Japanese pair. Repository-development Skills have no Japanese Plugin counterparts.
- Use `design-process-description` when authoring or reviewing a Process Description; it does not authorize executing the described work or publishing it.
- Keep Purpose, Outcome, and Output distinct. Preserve necessary contextual constraints, source authority, shared-information relationships, and explicit uncertainty without recreating a management or certification system.
- Preserve one source for each meaning. Models and views link to it; translations and summaries do not redefine it.
- Follow the existing Host formats. Do not introduce a common replacement manifest schema or an execution/record subsystem.

## Verification and delivery

Keep three kinds of evidence separate:

1. Agent Skill and Plugin form validation against their applicable formats.
2. Repository integrity: required files, versions, relative links, symlinks, Host resources, and distribution boundaries.
3. Semantic review: purpose and Outcome sufficiency, required details and obligations, references, evaluation limits, and English/Japanese meaning and normative force.

Run the checks in `.github/workflows/validate.yml` that the environment permits. At minimum run `python3 -m unittest discover -s tests -v`, `git diff --check`, changed-link checks, and review the complete task-owned diff, including new files. Passing mechanical checks does not prove semantic validity or successful Process execution.

For locale review, compare subject, modality, action or state, object, condition, quantifier, polarity, exceptions, and scope. Preserve canonical paths, identifiers, and code literals. Report unverified pairs rather than assuming equivalence.

Retirement checks apply to active specifications, distribution, guidance, configuration, and tests. Preserve release documents and changelog history; do not rewrite them to match the current specification. State intentional incompatibilities in current unreleased documentation.

Report findings, completed checks, failed or unperformed checks, and limits. Do not commit, push, publish, create or update a pull request, merge, tag, release, or make another external change without the user's authorization.
