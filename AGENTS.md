# Repository Instructions

[Japanese translation](docs/locales/ja/AGENTS.md)

These instructions apply to the entire repository. `localization.yaml` defines English as authoritative and Japanese as supported. Keep each changed English/Japanese pair semantically equivalent without changing canonical identifiers, paths, metadata keys, code literals, or normative force.

Read the complete `SKILL.md` for every ALPS representation or repository-development Skill selected for a task before applying it.

## Authoritative Sources

Determine authority by subject rather than treating every repository asset as an equal source.

| Subject | Authoritative source | Boundary |
| --- | --- | --- |
| Process constructs and semantics | [`spec/process-framework.md`](spec/process-framework.md) | Higher-order normative source. If it conflicts with the ALPS Specification, the Process Framework takes precedence. |
| Agent Skill representation, lifecycle, and Conformance | [`spec/ALPS-SPEC.md`](spec/ALPS-SPEC.md) | Governs ALPS without requiring one physical file format. |
| A distributed ALPS representation | Its root [`skills/*/SKILL.md`](skills/) | Authoritative Process Description or non-Process representation for that Skill. |
| Repository layout, distribution boundaries, and agent workflow | This `AGENTS.md` | Governs work in this repository. |
| A drafting example | [`skills/define-alps/references/SKILL-template.md`](skills/define-alps/references/SKILL-template.md) | Informative output-creation resource; it does not define a normative ALPS structure. |

Do not infer an ALPS requirement from a template, record, Environment Binding, repository test, Host adapter, or presentation resource.

## Repository and Distribution Layout

| Path | Role | Distribution status |
| --- | --- | --- |
| `skills/` | Single source of truth for the four Agent Skill representations exposed by the ALPS Plugin. | Distributed. |
| `.agents/skills/alps-reference-model`, `.agents/skills/define-alps`, `.agents/skills/apply-alps`, `.agents/skills/manage-alps` | Relative symbolic links providing an integrated discovery view for repository-development Agents that inspect `.agents/skills/`. | The linked representations are distributed from `skills/`; do not duplicate them here. |
| `.agents/skills/review-alps/` | Proposition-level and cross-layer review of ALPS repository changes. | Repository-development only; not registered or exposed as a Plugin Skill. |
| `.agents/skills/sync-locales/` | English/Japanese semantic-equivalence and update-coverage review. | Repository-development only; not registered or exposed as a Plugin Skill. |
| `spec/` | Authoritative Process Framework and ALPS Specification. | Repository specification assets. |
| `spec/locales/ja/` and `docs/locales/ja/` | Supported Japanese counterparts. | Localized assets; English remains authoritative. |
| `.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/` | Host-specific discovery or presentation metadata. | Adapters; they must not redefine ALPS semantics. |

`.agents/skills/` is not assumed to be a universal Host convention. Plugin Hosts discover distributed Skills through `skills/` and their applicable Host adapters.

Repository-development Skills may remain as ordinary files in a repository checkout or package archive without being registered, exposed, or discovered as distributed Plugin Skills.

Add another repository-development Skill only after a repeated task has emerged that does not fit clearly within `review-alps` or `sync-locales`.

## Change Routing

| Change affects | Required Process or review perspective |
| --- | --- |
| Process Framework or ALPS Specification semantics | Use `review-alps`; use `sync-locales` for every affected English/Japanese pair. |
| ALPS Reference Model, a reference Process, or another ALPS representation | Use `define-alps` to verify the representation and `review-alps` to assess the repository change; use `sync-locales` for paired assets. |
| README, AGENTS, CONTRIBUTING, or other paired guidance | Use `sync-locales`; check terminology, links, canonical paths, and any affected semantic or distribution boundary with `review-alps`. |
| Agent Skill form, Plugin manifests, Host adapters, symlinks, or repository layout | Apply the relevant official standard validation and use `review-alps` to assess source-of-truth and distributed/repository-only boundaries. |

## Semantic Invariants

- An Agent Skill represents a Process by default; a non-Process representation declares `metadata.alps.kind`.
- A Process View preserves provenance and Traceability for referenced source elements. View-local or modified content does not change a source Process or establish source Process Conformance.
- Change an applicable source Process through managed Tailoring, or change its authoritative Process Description through controlled redefinition with `define-alps`.
- `skills/` remains the only source of truth for distributed Agent Skill representations.
- Repository-development Skills remain real directories under `.agents/skills/` and are not distributed Plugin Skills.
- Mechanical validation results do not determine ALPS Conformance, Outcome achievability, Outcome achievement, or Process execution Conformance.
- A Process Skill owns only its Process-specific work, boundary, and Outputs; link to higher-order PF or ALPS requirements instead of restating them in each Process Skill.
- Informative summaries must not duplicate normative modal wording from an authoritative source.
- Include an optional Process element only when a declared need, risk, handoff, decision, or claim justifies it.
- Do not add an ALPS semantic checker or a new physical profile; keep official form validation, repository integrity, and semantic review separate.

## Repository Workflow

### Before editing

- Inspect repository state, the requested scope, and the complete task-owned diff.
- Identify the authoritative source, affected semantic layers, paired locale assets, canonical references, and distribution boundary before changing content.
- Preserve unrelated and user-authored changes.
- Keep one source of truth for each information item and use relative links from consumers.

### Validation and review

- Apply every Process or repository-development Skill selected through the routing table above.
- Keep validation in three separate layers:
  1. validate Agent Skill and Plugin form against the applicable official standards;
  2. validate repository-controlled file, version, path, link, symlink, and distribution integrity without interpreting Process meaning; and
  3. review propositions across the Process Framework, ALPS Specification, Reference Model, reference Processes, records, and English/Japanese counterparts.
- At minimum, check whitespace, changed relative links, canonical references, English/Japanese counterpart coverage, repository distribution boundaries, and the complete task-owned diff.
- Report standard-validation and repository-integrity results separately from cross-layer semantic review and from any Conformance judgment.

### Delivery

- Inspect the final diff and record checks that were run, checks that failed, and checks that could not be performed.
- Do not commit, push, publish, open or update a pull request, or make another external change unless the user requests it.
