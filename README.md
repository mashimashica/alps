# ALPS — Reusable Work Design

<p align="right">
  <strong>English</strong> | <a href="docs/locales/ja/README.md">Japanese</a>
</p>

<p align="center">
  <img src="assets/icon.svg" alt="ALPS icon" width="160">
</p>

ALPS is a thin profile that applies the [Process Framework](spec/process-framework.md)
to [Agent Skills](https://agentskills.io/specification). It helps establish
recurring or shared agent work as a reusable and assessable Process Skill with
an explicit Purpose, observable Outcomes, and only the guidance needed to apply
it.

The Plugin and repository brand is `alps`. The distributed Skill identifier is
`reusable-work-design`. The Process Name is `Reusable Work Design Process`
([`再利用可能な作業設計プロセス`](skills/reusable-work-design/references/locales/ja/SKILL.md)
in Japanese).

## The Problem ALPS Addresses

| Recurring-work failure | ALPS response |
| --- | --- |
| A recurring prompt works, but its intent and definition of done remain in people's heads. | State one Process Purpose and observable Outcomes. |
| Producing a document is treated as proof that the work succeeded. | Separate Outputs from the successful states expressed as Outcomes. |
| A Skill boundary combines unrelated reasons for doing work. | Establish one coherent Process boundary and separate independent Purposes. |
| A general Skill fixes a performer, tool, method, metric, or sequence without need. | Leave implementation choices open unless a genuine Control or Constraint requires them. |
| Skills exchange information through hidden context. | Make every described provider Output to recipient Input handoff explicit. |
| Completing a template or passing a form check is treated as proof of quality. | Keep form validation, semantic review, and execution assessment distinct. |

ALPS does not wrap the Host's Skill discovery, selection, activation, or
execution. It also does not govern adoption, versioning, controlled change, or
retirement for a repository or organization.

## Distributed Skill

ALPS distributes one Agent Skill:

| Skill ID | Process Name | Purpose |
| --- | --- | --- |
| [`reusable-work-design`](skills/reusable-work-design/SKILL.md) | Reusable Work Design Process | Establish recurring or shared agent work as a reusable and assessable Process Skill. |

Use it for:

- recurring work that needs a stable intent and definition of success;
- shared work that must be understood by more than one user or Agent;
- composed work whose Process handoffs need to be explicit; and
- an existing Process Skill that needs review or revision.

Do not use it merely for:

- a one-off task with no concrete reuse, sharing, composition, review, or
  assessment need;
- ordinary execution of an already-defined Skill;
- general Skill discovery or selection that the Host already provides; or
- repository or organizational governance of an adopted Skill.

## Start with the Semantic Core

Every Process Description begins with three elements:

| Element | Question answered |
| --- | --- |
| **Name** | What central concern identifies this Process? |
| **Purpose** | Why is this Process performed? |
| **Outcomes** | What observable result conditions constitute success? |

Add optional detail only when its absence would materially reduce correct
discovery, application, composition, or assessment. Optional detail can include
Activities, Tasks, Inputs, Outputs, Entry Criteria, Exit Criteria, Controls,
Constraints, Enablers, handoffs, and evidence needed for assessment.

The [Reusable Work Design Process](skills/reusable-work-design/SKILL.md) is the
primary example. ALPS intentionally provides no all-sections template: an empty
or unnecessary section is not evidence of completeness.

## Key Distinctions

| Distinction | Meaning |
| --- | --- |
| **Outcome / Output** | An Outcome is a successful state; an Output is an item, result, or service produced or transferred. |
| **Input / Enabler** | An Input is transformed; an Agent, person, model, tool, or execution environment enables performance. |
| **Description order / execution order** | The order of Activities or Tasks in a document does not prescribe execution order. A genuine temporal relationship is a Constraint. |
| **Brand / Process Name** | `alps` names the project and Plugin; a Process Name states the work's central concern. |
| **Self-application / self-certification** | A Process Skill can be reviewed using its own design rules, but that review is not independent proof of Conformance. |

## Responsibilities

| Participant | Responsibility |
| --- | --- |
| Agent Plugins | Distribute the Plugin and provide a portable discovery surface. |
| Agent Skills Host | Discover, select, activate, and execute Skills. |
| Reusable Work Design Process | Create, review, and revise reusable Process Skills. |
| Each resulting Process Skill | Provide the Process Description needed to perform its represented Process. |
| Repository or organization | Decide adoption, versioning, controlled change, retirement, and governance. |

## Install and Use

ALPS is distributed as an [Agent Plugins](https://agent-plugins.org/) v1 package.
With Node.js 18 or later available, install it through the `plugins` CLI:

```console
npx plugins add mashimashica/alps
```

Restart affected clients after installation so they reload the Agent Skill.
Then ask the Agent in plain language, naming the Skill when the Host requires
explicit activation:

```text
Use reusable-work-design to turn this recurring release-review work into a
reusable Process Skill. Establish one boundary, an explicit Purpose, observable
Outcomes, and only the detail needed to apply and assess it.
```

## Specification Boundary

The [Process Framework](spec/process-framework.md) is the authoritative source
for general Process semantics. The [ALPS Specification](spec/ALPS-SPEC.md) is a
thin Agent Skill application profile. The Agent Skills specification governs
the physical Skill form.

Form validation, parsing, loading, activation, template completion, or a textual
self-claim does not by itself establish semantic Conformance, Outcome
achievement, or Conformance of Process execution.

## Resources

| Goal | English | Japanese |
| --- | --- | --- |
| Understand general Process semantics | [Process Framework](spec/process-framework.md) | [プロセスフレームワーク](spec/locales/ja/process-framework.md) |
| Read the Agent Skill profile | [ALPS Specification](spec/ALPS-SPEC.md) | [ALPS仕様](spec/locales/ja/ALPS-SPEC.md) |
| Design or review a reusable Process Skill | [Reusable Work Design Process](skills/reusable-work-design/SKILL.md) | [再利用可能な作業設計プロセス](skills/reusable-work-design/references/locales/ja/SKILL.md) |
| Contribute to the repository | [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md) | [CONTRIBUTING.md](docs/locales/ja/CONTRIBUTING.md) and [AGENTS.md](docs/locales/ja/AGENTS.md) |
| Review release history and version policy | [CHANGELOG.md](CHANGELOG.md) and [Versioning](docs/versioning.md) | [CHANGELOG.md](CHANGELOG.md) and [Versioning](docs/locales/ja/versioning.md) |

## Version and License

ALPS versions the repository as one release unit. The current version is
**0.5.0** and remains in initial development. Unreleased changes are recorded in
[CHANGELOG.md](CHANGELOG.md); Git tags and the commits they identify define exact
release contents.

Except for identified third-party material, this repository is licensed under
the [Apache License 2.0](LICENSE). See also [NOTICE](NOTICE).
