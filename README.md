# ALPS — Agent Lifecycle Process Skills

[日本語](docs/locales/ja/README.md)

<p align="center">
  <img src="assets/icon.svg" alt="ALPS icon" width="160">
</p>

ALPS helps you design and review the meaning of work as a Process Description: why it is done, what observable conditions count as success, and which boundaries and details are necessary. The description remains understandable across different execution means.

Use it to clarify a one-off assignment, improve an existing Skill, or describe work shared across people and Agents. Start with **Name, Purpose, and Outcomes**; add detail when it changes how the work is understood, applied, or evaluated.

## Install

ALPS is an [Agent Plugins](https://agent-plugins.org/) package with Claude, Cursor, and Codex adapters. Install the complete Plugin through a compatible client. The [`plugins` CLI](https://www.npmjs.com/package/plugins) provides:

```console
npx plugins add mashimashica/alps
```

Reload affected clients after installation. Keep the Plugin root layout, including `spec/`: the Skill's required specification links depend on it. Copying only the Skill folder omits those sources. Check that your installed client exposes `design-process-description` and that its links to both specifications open.

## Use the Skill

[design-process-description](skills/design-process-description/SKILL.md) helps you create, revise, and review Process Descriptions. Ask in ordinary language or name the Skill explicitly as your Host requires.

```text
Use design-process-description to describe this one-off task through its purpose, observable success conditions, and necessary boundaries.

Review this Process Description. Identify unclear Outcomes, unnecessary method constraints, missing references, and limits. Return findings without rewriting it.

Revise these work descriptions so their shared information and the effects of changes are clear. Preserve the approvals that apply to this context.
```

The [minimal template](skills/design-process-description/references/SKILL-template.md) starts with ordinary Agent Skill frontmatter and the three required Process elements. The [examples](skills/design-process-description/references/examples.md) cover minimal and one-off work, work without a fixed artifact, necessary approvals and order, shared information, views, missing references, and Outputs that fail to establish an Outcome.

## What a description makes clear

| Question | Element or distinction |
| --- | --- |
| Why undertake the work? | Purpose |
| What observable condition counts as success? | Outcome |
| What work contributes to success? | Activities group related Tasks; Tasks describe individual actions |
| What is produced or updated? | Output; its existence alone is not success |
| What is examined or transformed? | Input |
| What directs, limits, or enables the work? | Control, Constraint, Enabler |
| What is the source, and what changes locally? | Authority, reference, translation, and context-limited change |
| What does a review establish? | A judgment about the description, separate from execution results and satisfaction of requirements |

Add Activities, Tasks, boundary elements, and Entry/Exit Criteria when they help explain the work. The Framework defines their meanings and relationships so that additional detail remains consistent. Necessary methods or order can be scoped to the relevant context. Multiple Processes can consult and update the same information; a Model or View can link to their descriptions without duplicating their Purposes and Outcomes.

ALPS supplies meaning and design support. Your environment supplies execution, storage, approval, and version management.

## Resources

| Resource | English | Japanese |
| --- | --- | --- |
| Meaning of Process Descriptions | [Process Framework](spec/process-framework.md) | [プロセスフレームワーク](spec/locales/ja/process-framework.md) |
| Agent Skill correspondence | [ALPS Specification](spec/ALPS-SPEC.md) | [ALPS Specification](spec/locales/ja/ALPS-SPEC.md) |
| Design Skill | [Skill](skills/design-process-description/SKILL.md) | [Skill](skills/design-process-description/references/locales/ja/SKILL.md) |
| Contribution and repository work | [CONTRIBUTING](CONTRIBUTING.md), [AGENTS](AGENTS.md) | [CONTRIBUTING](docs/locales/ja/CONTRIBUTING.md), [AGENTS](docs/locales/ja/AGENTS.md) |
| Version policy and pending compatibility changes | [Versioning](docs/versioning.md), [unreleased redesign](docs/unreleased-redesign.md) | [版管理](docs/locales/ja/versioning.md), [未リリースの再設計](docs/locales/ja/unreleased-redesign.md) |

## Version and license

The repository is versioned as one unit. See the version policy and unreleased changes linked above for release scope and compatibility information.

Except for identified third-party material, this repository is licensed under the [Apache License 2.0](LICENSE). See also [NOTICE](NOTICE).
