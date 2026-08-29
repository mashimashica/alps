# Minimal Process Template for `SKILL.md`

This informative drafting aid starts with the required semantic core of a Process Description. Its Markdown form and order are not ALPS requirements. Apply the [Process Framework](../../../spec/process-framework.md), the [ALPS Specification](../../../spec/ALPS-SPEC.md), and the applicable Agent Skill and execution-environment rules.

## Minimal Template

```markdown
---
name: <lowercase-hyphen-name>
description: <State what the Process does, when to use this Skill, and any information needed to determine applicability.>
---

# <Short Noun-Phrase Process Name>

## Purpose

<State the high-level objective for performing this Process.>

## Outcomes

- a) <One positive, observable, and assessable result is established.>
- b) <One independent result needed for the Purpose is established.>
```

## Add Only When Needed

| Optional detail | Add when |
| --- | --- |
| Inputs, Outputs, Entry Criteria, and Exit Criteria | Invocation or a handoff needs explicit boundary conditions or exchanged items. |
| Activities and Tasks | The work content needs standardization or will be used as a Task Conformance basis. |
| Controls, Constraints, and Enablers | A Process-specific direction, limitation, or capability dependency is not already inherited from a higher-order source. |
| Interfaces and Traceability | A Model, View, composition, or quality risk requires mappings, provenance, change propagation, or evidence relationships. |
| Evidence and records | Risk, a Decision Gate, a handoff, Tailoring, an audit, or an explicit Conformance claim justifies durable evidence. |

Do not add a `Conformance` section by default. Add one only when making an actual claim, and identify the subject, applicable baseline, scope, basis, conclusion, evidence, and limitations without inventing a new physical format.

## Drafting Checks

- For every optional element, ask whether deleting it would lose Outcome evaluation, a boundary, a handoff, a material decision, or claim evidence. If not, omit it.
- Keep each Outcome and Task to one meaning. A Task states one distinguishable action and its normative attribute.
- Treat Agents, tools, and execution environments as Enablers rather than Inputs when they provide execution capability.
