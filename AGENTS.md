# Repository Instructions

[Japanese translation](docs/locales/ja/AGENTS.md)

These instructions apply to the entire repository. `localization.yaml` defines
English as authoritative and Japanese as supported. Keep every changed
English/Japanese pair semantically equivalent without changing canonical
identifiers, paths, metadata keys, code literals, or normative force.

Read the complete `SKILL.md` for every distributed or repository-development
Skill selected for a task before applying it.

## Authoritative Sources

Determine authority by subject rather than treating every repository asset as
an equal source.

| Subject | Authoritative source | Boundary |
| --- | --- | --- |
| General Process constructs and semantics | [`spec/process-framework.md`](spec/process-framework.md) | Higher-order normative source. It takes precedence over the ALPS Specification. |
| Applying PF to Agent Skills | [`spec/ALPS-SPEC.md`](spec/ALPS-SPEC.md) | Thin profile for Process Skill representation, discovery projection, resources, handoffs, and validation boundaries. |
| Distributed Process Skill | [`skills/reusable-work-design/SKILL.md`](skills/reusable-work-design/SKILL.md) | Authoritative Process Description for the Reusable Work Design Process. |
| Repository layout, distribution boundaries, and change workflow | This `AGENTS.md` | Governs work in this repository. |

Do not infer Process semantics or ALPS requirements from a Host adapter,
manifest, test, presentation asset, or validation result.

## Repository and Distribution Layout

| Path | Role | Distribution status |
| --- | --- | --- |
| `skills/reusable-work-design/` | Single source of truth for the one Process Skill exposed by the `alps` Plugin. | Distributed. |
| `.agents/skills/reusable-work-design` | Relative symbolic link providing a repository-development discovery view. | Points to the distributed source; do not duplicate it. |
| `.agents/skills/review-alps/` | Cross-layer semantic and distribution review. | Repository-development only; never register it as a Plugin Skill. |
| `.agents/skills/sync-locales/` | English/Japanese semantic-equivalence and coverage review. | Repository-development only; never register it as a Plugin Skill. |
| `spec/` | Process Framework and ALPS Specification. | Repository specification assets. |
| `spec/locales/ja/` and `docs/locales/ja/` | Supported Japanese counterparts. | Localized assets; English remains authoritative. |
| `.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/` | Supported Host discovery or presentation metadata. | Adapters; they must not redefine ALPS semantics. |

`skills/` is the only distributed Skill source of truth. `.agents/skills/` is a
repository-development view, not a universal Host convention. Agent Plugins
provide distribution; the applicable Host performs Skill discovery, selection,
activation, and execution.

Repository or organizational policy, not the Reusable Work Design Process,
governs adoption, versioning, controlled change, retirement, and governance.

## Change Routing

| Change affects | Required Process or review perspective |
| --- | --- |
| Process Framework or ALPS Specification semantics | Apply `review-alps`; apply `sync-locales` to every affected English/Japanese pair. |
| `skills/reusable-work-design/SKILL.md` or its localization | Perform the Process's self-consistency and semantic-fixed-point review, then apply `review-alps` and `sync-locales`. |
| README, AGENTS, CONTRIBUTING, versioning, or other paired guidance | Apply `sync-locales` and the relevant `review-alps` semantic and distribution checks. |
| Plugin manifest, Host adapter, OpenAI metadata, symlink, or layout | Apply applicable official form validation, repository-integrity checks, and a `review-alps` distribution-boundary review. |

## Semantic and Product Invariants

- `alps` is the Plugin and repository brand.
- `reusable-work-design` is the Agent Skill discovery identifier.
- `Reusable Work Design Process` is the English Process Name; `再利用可能な作業設計プロセス`
  is its Japanese counterpart.
- The distributed Skill represents one Process with one Purpose: establishing
  recurring or shared agent work as a reusable and assessable Process Skill.
- Creating, reviewing, and revising the Process Skill representation are inside
  that Process boundary. Executing the represented Process and governing an
  adopted Skill are outside it.
- PF remains authoritative for Name, Purpose, Outcomes, optional Process
  elements, handoffs, Tailoring, assessment, and other general semantics.
- Optional detail is included only when needed for discovery, application,
  composition, or assessment.
- Mechanical validation does not determine semantic Conformance, Outcome
  achievement, Process execution Conformance, or self-consistency.

## Repository Workflow

### Before editing

- Inspect repository state, the requested scope, and the complete task-owned
  diff.
- Identify authoritative sources, affected semantic layers, locale pairs,
  relative references, Host projections, and the distribution boundary.
- Preserve unrelated and user-authored changes.
- Keep one authoritative source for each information item and link to it from
  consumers.
- Keep historical release documents factual. Repair links broken by removals
  with immutable tag or commit links rather than rewriting release history.

### Validation and review

Keep validation in three separate layers:

1. apply official Agent Skills, Agent Plugins, and supported Host form
   validation;
2. validate repository-controlled files, versions, paths, links, symlinks,
   locale coverage, and distribution boundaries without interpreting Process
   meaning; and
3. apply `review-alps`, including the `sync-locales` result, to review Process
   semantics, discovery projection, Process boundary, English/Japanese meaning,
   and cross-layer product promises.

At minimum, run Python unit tests, JSON and YAML parsing, relative Markdown-link
validation, symlink-target validation, `git diff --check`, active-reference
search, locale counterpart coverage, and complete task-owned diff review.

Report official form validation and repository-integrity results separately
from semantic review. Do not report any of them as automated proof of ALPS
Conformance, Outcome achievement, or self-consistency.

### Delivery

Inspect the final diff and record checks that passed, checks that failed, checks
that could not be performed, assumptions, and limitations. Do not commit,
update a branch, publish, open or update a pull request, or make another
external change unless the user requests it.
