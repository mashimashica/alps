# Representative Process Template for an ALPS-Conformant `SKILL.md`

This material is an informative example for drafting a readable Process Description in an Agent Skills `SKILL.md`. Its Markdown form, headings, and order are not ALPS requirements. This template does not require a physical split between the discovery layer and execution layer. Give precedence to the Process Framework, ALPS, the Agent Skills specification, and the rules of the applicable execution environment.

## Template

```markdown
---
name: <lowercase-hyphen-name>
description: <Briefly state what the represented Process does, when to use this Skill, and, if needed, when not to use it> ALPS-conformant.
---

# <Short Noun-Phrase Process Name>

## Purpose

<State concisely the related high-level objective or objectives for performing this Process.>
<If needed, add reference information about scope, subject domain, or degree of rigor without changing the meaning of the Purpose.>

## Outcomes

- a) <One positive, observable, and assessable result is established.>
- b) <One independent result is established.>
- c) <A result necessary to achieve the Purpose is established.>

## Activities & Tasks

The following headings, Activities, Tasks, and numbers present the content for readability; they do not prescribe a procedure or execution sequence. Entry Criteria are conditions evaluated before invocation, and Exit Criteria are conditions evaluated before declaring completion. Controls and Constraints apply regardless of where they appear.

### <Short Activity Name>

1. <Required action> must be performed.
2. <Recommended action> should be performed.
3. <Permissible action> may be performed.
4. <Typical action> is typically performed.

## Inputs

- <An information item or artifact transformed by the Process>
- <An item received from another Process or external source>

## Outputs

- <An artifact or information item; do not confuse it with an Outcome.>
- <An item usable as a recipient's Input.>

## Entry Criteria

- <A condition under which the Process can be invoked.>

## Exit Criteria

- <A condition under which achievement of the Outcomes can be determined.>
- <A condition under which the Output can be transferred.>

## Controls

- <A law, policy, standard, agreement, or other matter that directs execution.>

## Constraints

- <A limitation arising from the external environment or conditions of application.>

## Enablers

- <A required capability, Agent, tool, technology, or execution resource.>

## Conformance

- <The subject, scope, and criteria of a Conformance claim.>
- <Conditions for satisfaction when Outcome Conformance, Task Conformance, or both are selected.>

## Interfaces & Traceability

- <Mappings among Outcomes, Activities, Tasks, and evidence should be identified.>
- <Every provider Output to recipient Input mapping is explicit.>
- <The names, meanings, and scopes of Outputs and recipient Inputs should be aligned.>

## Bundled Resources

- [<Reference material>](references/<reference>.md): <Its role and when to read it.>
- `scripts/<script>.*`: <Its role, conditions of use, and limitations.>
- `assets/<asset>.*`: <Its role in discovery, presentation, or Output creation.>

## Common Approach

This section is reference information and has no normative force.

- <An example manner of application or practical tip.>
```

## Notes on Use

- Use this example for a Process Description. Apply the kind-specific ALPS requirements and Environment Binding profile when representing a Process Model, Process Reference Model, or Process View.
- Retain Name, Purpose, and Outcomes as mandatory elements. Other sections should be included according to the Purpose and required level of detail.
- Distinguish the first sentence of the Purpose from subsequent reference explanation. Do not add to or change the Purpose through the reference explanation.
- Write each Outcome as a condition in which a result is established, not as the creation of an Output.
- Write a Task whose primary function is to express an individual action that supports achievement of one or more Outcomes, so that the object and operation of that action are distinguishable.
- When a Constraint, decision criterion, or quality condition is included in a Task, treat it as the object of the action or as a condition directing the action, and preserve the Task's primary function as an individual action.
- Place a statement whose primary function is not an individual action in another element corresponding to that function.
- For each Task, make one of requirement, prohibition, recommendation, permission, or typical action distinguishable through normative wording. The template does not require every kind.
- Do not include an Agent, tool, or execution environment among the Inputs; treat it as an Enabler.
- Mandatory references must be resolvable. A Package should include only accompanying resources that directly support understanding or applying the represented Process or creating an Output.
- Do not make a Decision Gate a component of the Skill Description; treat it as a separate decision mechanism that controls application of the represented Process.
