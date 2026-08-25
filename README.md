# ALPS — Agent Lifecycle Process Skills

<p align="right">
  <strong>English</strong> | <a href="docs/locales/ja/README.md">Japanese</a>
</p>

<p align="center">
  <img src="assets/icon.svg" alt="ALPS icon" width="160">
</p>

<p align="center">
  <strong>Version 0.4.0</strong><br>
  Initial development
</p>

ALPS applies a Process Framework to Agent Skills so that people and Agents can define, select, invoke, and improve reusable work using the same semantics.

A Process Skill makes its Purpose, Outcomes, work content, Inputs, Outputs, and applicable conditions explicit without prescribing a particular performer or implementation.

## Quick Start

### 1. Install the plugin

ALPS is distributed as an [Agent Plugins](https://agent-plugins.org/) v1 package. With Node.js 18 or later available, install it through the [`plugins` CLI](https://www.npmjs.com/package/plugins):

```console
npx plugins add mashimashica/alps
```

Restart affected clients after installation so they reload the Agent Skills.

### 2. Choose what you need

| Agent Skill | Representation | Use it when |
| --- | --- | --- |
| [`alps-reference-model`](skills/alps-reference-model/SKILL.md) | Process Reference Model | The ALPS reference Processes and their relationships must guide selection, assessment, or improvement. |
| [`define-alps`](skills/define-alps/SKILL.md) | Process | An ALPS representation must be created, redefined, or verified. |
| [`apply-alps`](skills/apply-alps/SKILL.md) | Process | Existing representations must guide Process selection, Invocation, composition, or handoffs. |
| [`manage-alps`](skills/manage-alps/SKILL.md) | Process | Representations must be adopted, tailored, assessed, changed, improved, or retired. |

In most cases, start with `alps-reference-model` and use it to select the applicable reference Processes.

A Process Model or Process View supplied by another plugin can guide selection in the same way. `apply-alps` resolves the Processes referenced by the selected Model or View.

### 3. Ask the Agent

```text
Activate `alps-reference-model` and use it to decide which ALPS reference Processes apply.

Use `define-alps` to define and verify an ALPS Process View for this cross-cutting concern.

Use `apply-alps` to activate the applicable Model or View, resolve the required Processes, and make every Output/Input handoff explicit.

Use `manage-alps` to assess these representations and execution records and propose controlled improvements.
```

## How ALPS Works

### Process knowledge

The starting point is a Process Description:

- a **Process** is the work being performed;
- a **Process Description** explains that work; and
- by default, an **Agent Skill** represents a Process through an authoritative Process Description.

A useful Process Description lets a reader answer the following questions.

| Plain-language question | ALPS term |
| --- | --- |
| Why does the work exist? | **Purpose** |
| What condition counts as success? | **Outcome** |
| What is produced? | **Output** |
| What is transformed? | **Input** |
| What work belongs to the Process? | **Activities and Tasks** |
| What directs, limits, or supports it? | **Controls, Constraints, and Enablers** |
| When can the work begin or be considered complete? | **Entry Criteria and Exit Criteria** |
| Where does the Process apply? | Its **boundary and application context** |
| Who performs it? | A general Process leaves this open. |
| How is it implemented? | A general Process Description does not prescribe this. |

The [Process Framework](spec/process-framework.md) defines these concepts and their semantics. `Name`, `Purpose`, and `Outcomes` are required in a Process Description. Activities and Tasks describe work content rather than implementation steps. Inputs are transformed into Outputs. People, Agents, tools, and execution environments are resources or Enablers rather than Inputs.

### Representation kinds

An Agent Skill represents a Process by default. It can also represent another Process Framework construct.

| Representation | Role |
| --- | --- |
| Process | Defines independent work through its Purpose and Outcomes. |
| Process Model | Organizes related Processes and their relationships. |
| Process Reference Model | Defines Processes by Name, Purpose, and Outcomes and relates them explicitly. |
| Process View | Organizes Activities and Tasks across Processes around a Concern or Purpose and explains their application. |

Only a Process representation may be selected for direct Process Invocation. Process Models, Process Reference Models, and Process Views provide selection or composition context.

Non-Process representations declare their kind in `SKILL.md` metadata:

```yaml
metadata:
  alps.kind: process-view
```

Supported explicit kinds are `process-model`, `process-reference-model`, and `process-view`. A Process View can reference source Activities and Tasks or describe View-local Activities and Tasks. Referenced source elements retain their provenance and Traceability, and View-local descriptions do not by themselves change a source Process.

### ALPS Reference Model

ALPS defines its own lifecycle through three reference Processes. They are not fixed phases and may be applied concurrently, iteratively, or recursively.

```mermaid
flowchart LR
    DEFINE["Define ALPS<br/>Defines and verifies ALPS representations"]
    MANAGE["Manage ALPS<br/>Governs representations and their application"]
    APPLY["Apply ALPS<br/>Activates representations and invokes Processes"]

    DEFINE -->|"Verified representation"| MANAGE
    MANAGE -->|"Managed representations and conditions"| APPLY
    APPLY -->|"Selection and execution evidence"| MANAGE
    MANAGE -->|"Redefinition or reverification request"| DEFINE
```

The authoritative Process Reference Model is packaged as [`skills/alps-reference-model/SKILL.md`](skills/alps-reference-model/SKILL.md). It repeats the Name, Purpose, and Outcomes of the three reference Processes and is mechanically checkable against their authoritative Process Descriptions.

## Creating and Reviewing ALPS Representations

Use the following resources according to the question being answered.

| Need | Start with | Role |
| --- | --- | --- |
| Understand Process concepts and semantics | [Process Framework](spec/process-framework.md) | Higher-order normative source for Process constructs. |
| Understand how Agent Skills represent and govern those constructs | [ALPS Specification](spec/ALPS-SPEC.md) | Normative requirements for ALPS representations, lifecycle, and Conformance. |
| Define, redefine, or verify a representation | [`define-alps`](skills/define-alps/SKILL.md) | Reference Process for establishing an assessable and usable ALPS representation. |
| Draft a Process Description | [`SKILL-template.md`](skills/define-alps/references/SKILL-template.md) | Informative drafting example; it does not define an ALPS requirement. |
| Use this repository's bounded Markdown form | [`alps-markdown/v1`](spec/alps-markdown.md) | Optional Environment Binding for Markdown and frontmatter. |

The `SKILL-template.md` example is compatible with `alps-markdown/v1` after its placeholders are replaced, but its physical form, headings, and order are not ALPS requirements.

The profile checker at `.agents/skills/review-alps/scripts/validate_alps_markdown.py` mechanically validates only `alps-markdown/v1`. It is an Application Enabler of the repository-development [`review-alps`](.agents/skills/review-alps/SKILL.md) Process, which reviews repository changes across the Process Framework, ALPS Specification, reference representations, bindings, locales, and distribution boundaries. The repository-development [`sync-locales`](.agents/skills/sync-locales/SKILL.md) Process checks semantic equivalence between authoritative English assets and their supported Japanese counterparts. Neither Process is distributed as a Plugin Skill.

Neither the template nor a successful profile check establishes ALPS Conformance, Outcome achievability, Outcome achievement, or Process execution Conformance.

## Using ALPS in a Repository

For a repository that uses ALPS regularly, add a short policy to [AGENTS.md](https://agents.md/). A minimal policy is:

```md
## ALPS

This repository uses ALPS.

- Activate `alps-reference-model` when the ALPS Reference Model is needed for Process selection or assessment.
- Treat Agent Skills as Process representations by default. Use `metadata.alps.kind` to distinguish `process-model`, `process-reference-model`, and `process-view` representations.
- Read the complete `SKILL.md` for every selected representation.
- Use `define-alps` to define or verify ALPS representations, `apply-alps` to resolve and invoke Processes, and `manage-alps` for adoption, Tailoring, assessment, change, or retirement.
- For a Process View, preserve provenance and Traceability for referenced source elements and keep View-local descriptions distinct from changes to source Processes.
- When combining Processes, make required Output/Input handoffs explicit.
```

## Find the Right Resource

| Goal | English | Japanese |
| --- | --- | --- |
| Understand Process semantics | [Process Framework](spec/process-framework.md) | [Process Framework](spec/locales/ja/process-framework.md) |
| Read the normative ALPS requirements | [ALPS Specification](spec/ALPS-SPEC.md) | [ALPS Specification](spec/locales/ja/ALPS-SPEC.md) |
| Draft a Process Description | [`SKILL-template.md`](skills/define-alps/references/SKILL-template.md) | [`SKILL-template.md`](skills/define-alps/references/locales/ja/SKILL-template.md) |
| Contribute to the repository | [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md) | [CONTRIBUTING.md](docs/locales/ja/CONTRIBUTING.md) and [AGENTS.md](docs/locales/ja/AGENTS.md) |
| Review release history and version policy | [CHANGELOG.md](CHANGELOG.md) and [Versioning](docs/versioning.md) | [CHANGELOG.md](CHANGELOG.md) and [Versioning](docs/locales/ja/versioning.md) |

## Version and License

ALPS versions the repository as one release unit. The current version is **0.4.0** and remains in initial development. Git tags and the commits they identify define exact release contents.

Except for identified third-party material, this repository is licensed under the [Apache License 2.0](LICENSE). See also [NOTICE](NOTICE).
