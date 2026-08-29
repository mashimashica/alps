---
name: apply-alps
description: Select and activate ALPS representations suited to an application situation, resolve the applicable Processes, and achieve intended Outcomes through single or combined application of Process Skills. Use for selection guided by a Process Model, Process Reference Model, or Process View; Invocation or composition of existing Process Skills; or establishment of selection rationale, Tailoring, handoffs, or Outcome evidence. Use define-alps for an unmet representation need and manage-alps for adoption, controlled change, Tailoring decisions, assessment, or retirement. ALPS-conformant.
---

# ALPS Application Process

## Purpose

This Process selects and activates applicable ALPS representations, resolves the Processes needed for the application situation, and achieves the intended Outcomes through the single or combined application of Process Skills.

## Outcomes

Success of this Process establishes the following conditions.

- a) The needs, conditions, and risks of the application situation are identified.
- b) Applicable Process Models, Process Reference Models, Process Views, and Process representations are selected or activated as needed.
- c) Candidate Processes are resolved from the selected or activated representations.
- d) The Process Skills to invoke and the form of application are determined with a rationale.
- e) Applicable Controls, Constraints, Tailoring decisions, and Decision Gates are identified before affected actions occur.
- f) Process Instances are executed within the declared application scope and applicable Controls, Constraints, and Tailoring decisions.
- g) The declared Outcomes of the applied Processes are achieved with observable evidence.
- h) Required handoffs are established.
- i) When multiple Processes are composed, completeness within the selected composition scope is established.
- j) Consistency across applicable Process relationships and structural levels is established.

## Activities & Tasks

The order of headings, Activities, Tasks, and numbers does not prescribe an execution sequence. Entry Criteria govern invocation of this Process; the Entry Criteria of each selected Process are assessed separately before that Process is invoked. Controls and Constraints apply irrespective of where they appear. Iteration, Concurrency, Recursion, and Integration may be used according to the application situation.

### Representation Selection and Process Resolution

This Activity uses discovery information and ALPS representations to determine the Processes that fit the application situation. It primarily contributes to Outcomes a), b), c), and d).

1. The needs, conditions, risks, and applicable Constraints of the application situation must be identified.
2. Candidate Agent Skills should be discovered from their discovery information without assuming that every discovered Skill represents an invokable Process.
3. The representation kind must be determined before treating an Agent Skill as an Invocation candidate.
4. A Process Model may be activated to identify related Processes and their relationships.
5. A Process Reference Model may be activated to compare candidate Processes by Name, Purpose, Outcomes, and relationships.
6. A Process View may be activated to apply a cross-cutting concern and identify the source Processes and the Activities and Tasks relevant to the application situation.
7. Canonical Skill references in the selected representation must be resolved before a referenced Process Skill is used.
8. Only an Agent Skill representing a Process may be selected for direct Process Invocation.
9. Candidate Process Purposes and Outcomes should be compared with the needs and target Outcomes of the application situation.
10. If no suitable representation or Process exists, the unmet need may be handed to the ALPS Definition Process.
11. The uncertainty and risks associated with the selection decision must be evaluated.
12. The rationale for the selection decision should be recorded.

### Process Invocation and Execution

This Activity invokes selected Process Skills and evaluates their execution. It primarily contributes to Outcomes d), e), f), and g).

1. The selected Agent Skill's authoritative representation must be confirmed to represent a Process before Invocation begins.
2. Satisfaction of the selected Process's Entry Criteria must be confirmed before the Process is invoked.
3. If the Process Entry Criteria are not satisfied, Invocation must be deferred or the unmet conditions must be resolved first.
4. Required Inputs and Enablers should be confirmed as available.
5. Applicable Controls, Constraints, Tailoring decisions, and required Decision Gates must be identified before the affected action that they direct, limit, or govern occurs.
6. When the Conformance claim selected for the invoked Process is Full Conformance with Task Conformance as a basis, or Tailored Conformance whose declared scope retains a requirement stated in an Activity or Task, the applicable Activities and Tasks in the authoritative Process Description must be applied according to their normative attributes.
7. An execution sequence not explicitly established by a Constraint must not be assumed.
8. A required Decision Gate must be passed before the action it governs occurs.
9. Process Exit Criteria must be assessed before completion is declared.
10. Outcome achievement should be assessed from observable evidence.
11. Significant execution decisions, assumptions, deviations, and unresolved matters should be recorded.
12. Execution evidence and lessons may be handed to the ALPS Management Process for assessment and improvement.

### Process Composition and Handoffs

This Activity combines Processes and manages interfaces, handoffs, and composition completeness and consistency. It primarily contributes to Outcomes g), h), i), and j).

1. The target set of Outcomes for the composition must be identified.
2. The identity and provenance of each Process representation used in the composition should be recorded.
3. Every provider Output to recipient Input mapping must be made explicit.
4. The names, meanings, and scopes of each exchanged item should be aligned across its provider Output and recipient Input.
5. Previously undefined handoffs may be introduced only through an applicable controlled change or Tailoring decision.
6. When Iteration or Recursion changes an Output, affected Inputs and applicable criteria should be reevaluated.
7. When a change to an Output affects an Input to another Process, the affected Process and mapping should be identified.
8. When a change to an Output affects an Input to another Process, the necessary reassessment should be performed.
9. When Processes are applied concurrently, iteratively, or recursively, shared or interdependent information items and their reference or change relationships should be identified to the extent needed for application.
10. When Output quality affects a subsequent Outcome or stakeholder acceptance, the determination conditions and necessary evidence should be related to Entry Criteria, Exit Criteria, a review, or a Decision Gate.
11. Integration must establish completeness within the selected scope.
12. Integration must establish consistency across Process relationships and structural levels.
13. Outcome achievement for the composition as a whole should be assessed.
14. When the same information item is changed by multiple Processes, its integrity, state, and change handling must be defined in proportion to quality risk.

## Inputs

Representative Inputs include application needs and conditions, target Outcomes, discovery information, Process Models, Process Reference Models, Process Views, Process Descriptions, declared Inputs, Framework-level declarations, Tailoring decisions, and execution requests.

## Outputs

Representative Outputs include activated representations, resolved Process selections and rationale, Process Outputs, composition definitions, handoff records, Outcome evidence, execution decisions, and unresolved needs or change requests.

## Entry Criteria

- Information needed to identify the application need and material risks is available or can be obtained.
- Candidate Agent Skills or the absence of candidates can be identified.
- Priority Controls and critical Constraints can be identified.
- The distinction between representation activation and Process Invocation can be maintained for the selected assets.

## Exit Criteria

- The application needs, selected representations, resolved Processes, Invocation decisions, and rationale are recorded.
- Entry/Exit Criteria, applicable Activity and Task requirements, Outcome evidence, and unresolved matters for each invoked Process have been assessed.
- For combined application, Output/Input mappings and composition completeness and consistency have been evaluated.
- Required handoffs, holds, requests to the ALPS Definition Process or ALPS Management Process, or termination are explicit.
- Any Conformance claim states its subject, scope, basis, and evidence.

## Controls

- The [Process Framework](../../spec/process-framework.md) and [ALPS Specification](../../spec/ALPS-SPEC.md) must be applied. If they conflict, the Process Framework must take precedence.
- Normative words and their meanings are those defined in the Process Framework.
- Under Outcome Conformance, Activities and Tasks are guidance rather than mandatory execution conditions.
- When no Process Conformance is claimed for an invoked Process, applicable Activity and Task statements retain their normative attributes.
- When a Process View is active, referenced source elements retain their source meaning.
- Applicable system instructions, user instructions, safety and privacy policies, laws, standards, and agreements must be applied.
- The authoritative representation and managed Tailoring decisions applicable to each selected Process must be applied.
- Execution-environment rules concerning permissions, confirmation, and external effects must be followed.

## Constraints

- Agent Skill discovery or activation must not be treated as Process Invocation unless the selected Agent Skill represents a Process and its Entry Criteria are satisfied.
- A Process Model, Process Reference Model, or Process View must not be executed as though it were a Process.
- Information used only to discover candidates must not be treated as sufficient for Process execution.
- An Activity or Task requirement in scope under the selected Conformance claim must not be omitted unless it has been legitimately changed through managed Tailoring.
- View-specific or modified Activities and Tasks must not silently alter Source Process Conformance.
- Tailoring must not be performed implicitly. Its scope, applicable Controls and Constraints, decision, and rationale must remain traceable.
- An unspecified execution sequence must not be assumed.
- Agents, models, Agent Skills, tools, and execution environments are Enablers rather than Process Inputs.

## Enablers

Representative Enablers include managed ALPS representations, Agent capabilities, resolution and validation tools, required execution tools, and execution environments.

## Conformance

This Skill represents the ALPS Application Process. Reference Process Conformance of that Process is distinct from Conformance of the Processes selected and invoked through it. Activation of a Process Model, Process Reference Model, or Process View is not Execution Conformance. When Conformance is claimed for an invoked Process, it is evaluated as Process Conformance or Reference Process Conformance, as applicable, against its applicable Conformance basis. When Source Process Conformance is claimed for a source Process referenced by an applied Process View, it is evaluated against that source Process's applicable Conformance basis. Assessment of Process View Outcomes remains separate from Outcome Conformance for source Processes.

## Interfaces & Traceability

| Provider | Output or information item | Recipient | Related information |
|---|---|---|---|
| ALPS Management Process | Managed representations, status, Tailoring decisions, application conditions | ALPS Application Process | Representation identity, kind, version, scope, and conditions. |
| Process Model / Reference Model / View | Process references and relationships | Representation Selection and Process Resolution | Canonical references, Purpose/Outcomes where applicable, source provenance, and Traceability. |
| Process A | Declared Output | Process B | Recipient Input, meaning, scope, quality conditions, and state. |
| ALPS Application Process | Selection rationale, execution evidence, Outcome evidence, handoffs, and lessons | ALPS Management Process | Process Instances, decisions, measurements, limitations, and proposed changes. |
| ALPS Application Process | Unmet representation need | ALPS Definition Process | Context, expected outcomes, missing coverage, and risk. |

## Shared Normative References

- The repository-shared [Process Framework](../../spec/process-framework.md) is the higher-order normative source.
- The repository-shared [ALPS Specification](../../spec/ALPS-SPEC.md) supplies representation, selection, Invocation, Tailoring, and Conformance rules.

## Bundled Resources

- This root `SKILL.md` is the authoritative English Process Description. For Japanese-language work, use the [Japanese localization](references/locales/ja/SKILL.md); if the localization conflicts with this file, this English description governs.
- [process-instance-record.md](references/process-instance-record.md) provides an optional Process Instance record for situations where the quality risk warrants a durable execution record.

## Common Approach

- Start with the need, then activate Models or Views only when they improve Process selection or composition.
- Treat Model/View activation as context loading and Process Invocation as a separate decision.
- Resolve canonical references before relying on a referenced Process.
- Use Purpose and Outcomes to distinguish overlapping Processes.
- Make cross-Process Output/Input handoffs explicit and reevaluate them after iteration changes shared information.
