# Minimal Process Description template

```markdown
---
name: <lowercase-hyphen-name>
description: <What this Skill does and when to use it.>
---

# <Process Name>

## Purpose

<Why the work is undertaken.>

## Outcomes

- <An observable result condition. Add further Outcomes only as needed for the Purpose.>
```

The frontmatter is ordinary Agent Skill discovery information. Name, Purpose, and one or more Outcomes are the required Process content. Replace the placeholders; do not add empty optional sections.

Each Outcome describes a result state needed for the Purpose; together, the Outcomes must be sufficient to satisfy it. Use [examples](examples.md) when additional work detail, conditions, references, or evaluation context is needed. This template is informative; the [Framework](../../../spec/process-framework.md) and [Specification](../../../spec/ALPS-SPEC.md) govern meaning and representation.

The [Production Release example](examples.md#production-release) shows how to add Activity headings, numbered Tasks, and attached NOTEs while keeping obligations in the main text.

When supporting tools need to be described, use the [system design examples](../../design-agent-work-system/references/examples.md) to add the necessary responsibilities, interfaces, and conditions to the target Skill or its resources.

[Japanese translation](locales/ja/SKILL-template.md)
