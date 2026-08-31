# ALPS — Agent Lifecycle Process Skills

<p align="right">
  <strong>English</strong> | <a href="docs/locales/ja/README.md">Japanese</a>
</p>

<p align="center">
  <img src="assets/icon.svg" alt="ALPS icon" width="160">
</p>

ALPS is the project and method name for turning recurring agent work into a clear, reusable Process Skill. “Lifecycle” means that a Skill is intended to be used repeatedly and redesigned from what is learned in use. It does not mean that ALPS supplies a lifecycle state machine or a governance system.

The package distributes one Skill: [`design-process-description`](skills/design-process-description/SKILL.md). It creates, revises, or simplifies the authoritative Process Description for recurring work. The description centers on one Purpose, observable Outcomes, a reusable boundary, and only the detail needed for correctness, safety, meaning, composability, or assessment.

ALPS does not execute the target Process, manage its repository or release, or provide formal conformance claims or certification. To achieve a target Process Skill's Outcomes, apply that Skill directly.

## Install

ALPS is distributed as an [Agent Plugins](https://agent-plugins.org/) v1 package. With Node.js 18 or later:

```console
npx plugins add mashimashica/alps
```

Restart clients that need to reload installed Skills.

## Use

Usually, read only the root [`SKILL.md`](skills/design-process-description/SKILL.md). It links to one of three focused references only when a specific design question requires more detail.

Example requests:

```text
Turn this recurring incident-summary work into a reusable Process Description with one Purpose and observable Outcomes.

Simplify this Process Skill by removing case-specific tools, file paths, fixed ordering, and details that are not needed for correct use.

Revise this Process Description using the attached results, failures, repeated clarifications, and unresolved assumptions.
```

The Skill presents the designed or revised Process Description and makes unknowns explicit instead of guessing.

## Repository

The English Skill is authoritative. A maintained [Japanese counterpart](skills/design-process-description/references/locales/ja/SKILL.md) is included. Host adapters expose the same single Skill and do not define additional behavior.

ALPS is currently version **0.6.0**. See [Versioning](docs/versioning.md), [Changelog](CHANGELOG.md), [Contributing](CONTRIBUTING.md), and [Repository instructions](AGENTS.md).

Except for identified third-party material, this repository is licensed under the [Apache License 2.0](LICENSE). See [NOTICE](NOTICE).
