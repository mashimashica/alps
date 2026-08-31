# ALPS — Agent Lifecycle Process Skills

<p align="right">
  <strong>English</strong> | <a href="docs/locales/ja/README.md">Japanese</a>
</p>

<p align="center">
  <img src="assets/icon.svg" alt="ALPS icon" width="160">
</p>

Recurring agent work often begins as a one-off prompt or a case-specific procedure: its reason for existing is implicit, success is hard to assess, and details for one project become tangled with knowledge meant to be reused. ALPS helps turn that work into a clear, reusable Process Skill by designing its authoritative Process Description.

ALPS is for Agent Skill authors, teams standardizing recurring work, and maintainers simplifying Skills after real use. Its single distributed Skill, [`design-process-description`](skills/design-process-description/SKILL.md), clarifies one Purpose, observable Outcomes, a coherent reusable boundary, and the minimum detail needed for correct, safe, meaningful, composable, and assessable use.

## Who It Is For

Use ALPS when you need to:

- turn recurring work into a Process Description that can guide more than one application;
- make the reason for the work and its observable definition of success explicit;
- separate reusable Process knowledge from case-specific people, tools, files, repositories, values, and execution order; or
- revise an existing Process Skill using results, failures, repeated clarification, unresolved assumptions, and known limitations.

## What Changes with ALPS

| Before | With ALPS |
| --- | --- |
| A one-off prompt or procedure is tied to one case. | A reusable Process Description establishes one coherent Process boundary. |
| Success conditions remain implicit. | One Purpose explains why the work exists, and observable Outcomes show when it has succeeded. |
| People, tools, files, repositories, or a fixed sequence are treated as the Process itself. | Reusable Process knowledge stays independent of implementation and one application's context. |
| New instructions accumulate without evidence that they are needed. | The description keeps only detail needed for correctness, safety, meaning, composability, or assessment, and is simplified using evidence from use. |

## Quick Start

### 1. Install the Plugin

ALPS is distributed as an [Agent Plugins](https://agent-plugins.org/) v1 package. With Node.js 18 or later:

```console
npx plugins add mashimashica/alps
```

Restart clients that need to reload installed Skills.

### 2. Design or Redesign a Process Description

Use [`design-process-description`](skills/design-process-description/SKILL.md) when creating, revising, or simplifying the Process Description behind recurring work. Usually, the root `SKILL.md` is all you need; it points to one focused reference only when a specific design question requires more detail.

To perform the recurring work itself, apply its target Process Skill directly.

### 3. Ask the Agent

```text
Turn this recurring incident-summary work into a reusable Process Description with one Purpose, observable Outcomes, and a coherent boundary.

Simplify this Process Skill by separating reusable knowledge from case-specific people, tools, files, repositories, and fixed ordering. Keep only details needed for correct and assessable use.

Revise this Process Description using the attached results, failures, repeated clarifications, unresolved assumptions, and known limitations.
```

The Skill presents the created or revised Process Description together with unresolved questions, explicit assumptions, and known limitations rather than filling gaps by guessing.

## How It Works

A Process Description starts with a clear Name, one Purpose, and observable Outcomes. It then defines one coherent boundary for the recurring work and separates durable Process knowledge from information supplied by a particular application.

Activities, Tasks, Inputs, Outputs, conditions, and Handoffs are added only when the Process would otherwise be ambiguous, unsafe, difficult to compose, or impossible to assess. Unnecessary performers, tools, methods, metrics, file paths, repository details, fixed sequences, and special-case branches are removed.

The root Skill links to three independent references only when needed:

| Design question | Reference |
| --- | --- |
| Why does the Process exist, and what state shows success? | [Purpose and outcomes](skills/design-process-description/references/purpose-and-outcomes.md) |
| What belongs in the reusable Process rather than one application? | [Boundary and detail](skills/design-process-description/references/boundary-and-detail.md) |
| What function does each surrounding item or condition serve? | [Inputs, outputs, and conditions](skills/design-process-description/references/inputs-outputs-and-conditions.md) |

## Scope

“Lifecycle” in the project name reflects repeated use and redesign from what is learned; it does not introduce a lifecycle state machine. ALPS designs the target Skill's Process Description. It does not execute that target Process, act as a standing Skill selector or orchestrator, manage Git or releases, or provide formal conformance claims or certification.

## Repository

The English Skill is authoritative, with a maintained [Japanese counterpart](skills/design-process-description/references/locales/ja/SKILL.md). Host adapters expose the same single Skill without adding behavior.

ALPS is currently version **0.6.0**. See [Versioning](docs/versioning.md), [Changelog](CHANGELOG.md), [Contributing](CONTRIBUTING.md), and [Repository instructions](AGENTS.md).

Except for identified third-party material, this repository is licensed under the [Apache License 2.0](LICENSE). See [NOTICE](NOTICE).
