---
name: apply-alps
description: Select and activate ALPS representations suited to an application situation, resolve the applicable Processes, and achieve intended Outcomes through single or combined application of Process Skills. Use when a Process Model, Process Reference Model, or Process View must guide selection; when existing Process Skills must be invoked or composed; or when selection rationale, Tailoring, handoffs, or Outcome evidence must be established. Use define-alps for an unmet representation need and manage-alps for adoption, controlled change, Tailoring decisions, assessment, or retirement. ALPS-conformant.
---

# Apply ALPS

## Purpose

This Process selects and activates applicable ALPS representations, resolves the Processes needed for the application situation, and achieves the intended Outcomes through the single or combined application of Process Skills.

## Outcomes

Success of this Process establishes the following conditions.

- a) The needs, conditions, and risks of the application situation are identified.
- b) Applicable Process Models, Process Reference Models, Process Views, and Process representations are selected or activated as needed, and candidate Processes are resolved from them.
- c) The Process Skills to invoke and the form of application are determined with a rationale.
- d) Applicable Controls, Constraints, Tailoring decisions, and Decision Gates are identified before affected actions occur.
- e) Process Instances are executed within the declared application scope and applicable Controls, Constraints, and Tailoring decisions.
- f) The declared Outcomes of the applied Processes are achieved with observable evidence.
- g) Required handoffs and the completeness and consistency of the Process composition are established.

## Activities & Tasks

The order of headings, Activities, Tasks, and numbers does not prescribe an execution sequence. Entry Criteria govern invocation of this Process; the Entry Criteria of each selected Process are assessed separately before that Process is invoked. Controls and Constraints apply irrespective of where they appear. Iteration, Concurrency, Recursion, and Integration may be used according to the application situation.

### Representation Selection and Process Resolution

This Activity uses discovery information and ALPS representations to determine the Processes that fit the application situation. It primarily contributes to Outcomes a), b), and c).

1. The needs, conditions, risks, and applicable Constraints of the application situation must be identified.
2. Candidate Agent Skills should be discovered from their discovery information without assuming that every discovered Skill represents an invokable Process.
3. The representation kind must be determined before treating an Agent Skill as an Invocation candidate.
4. A Process Model may be activated to identify related Processes and their relationships.
5. A Process Reference Model may be activated to compare candidate Processes by Name, Purpose, Outcomes, and relationships.
6. A Process View may be activated to apply a cross-cutting concern and identify the source Processes and the Activities and Tasks relevant to the application situation.
7. Activating a Process Model, Process Reference Model, or Process View must not itself be treated as Process Invocation.
8. Canonical Skill references in the selected representation must be resolved before a referenced Process Skill is used.
9. Only an Agent Skill representing a Process may be selected for direct Process Invocation.
10. Candidate Process Purposes and Outcomes should be compared with the needs and target Outcomes of the application situation.
11. If no suitable representation or Process exists, the unmet need may be handed to Define ALPS.
12. The uncertainty and risks associated with the selection decision must be evaluated.
13. The rationale for the selection decision should be recorded.

### Process Invocation and Execution

This Activity invokes selected Process Skills and evaluates their execution. It primarily contributes to Outcomes c), d), e), and f).

1. The selected Agent Skill must represent a Process before Invocation begins.
2. The Process Entry Criteria must be satisfied before the Process is invoked.
3. If the Process Entry Criteria are not satisfied, Invocation must be deferred or the unmet conditions must be resolved first.
4. Required Inputs and Enablers should be confirmed as available.
5. Applicable Controls, Constraints, Tailoring decisions, and required Decision Gates must be identified.
6. When the selected Conformance basis includes Full Conformance to Tasks or a Tailored Conformance scope that retains Activity or Task requirements, the applicable Activities and Tasks in the authoritative Process Description must be applied according to their normative attributes.
7. When the selected Conformance basis makes a requirement Task applicable, that Task must not be omitted unless it has been legitimately changed through managed Tailoring. When only Full Conformance to Outcomes is selected, Activities and Tasks are guidance rather than mandatory execution conditions.
8. An execution sequence not explicitly established by a Constraint must not be assumed.
9. A required Decision Gate must be passed before the governed irreversible or high-impact action occurs.
10. Process Exit Criteria must be assessed before completion is declared.
11. Outcome achievement should be assessed from observable evidence.
12. Significant execution decisions, assumptions, deviations, and unresolved matters should be recorded.
13. Execution evidence and lessons may be handed to Manage ALPS for assessment and improvement.

### Process Composition and Handoffs

This Activity combines Processes and manages interfaces, handoffs, and composition integrity. It primarily contributes to Outcomes f) and g).

1. The target set of Outcomes for the composition must be identified.
2. The identity and provenance of each Process representation used in the composition should be recorded.
3. The mapping from each provider Output to each recipient Input must be explicit where the exchange affects successful application.
4. Previously undefined handoffs may be introduced only through an applicable controlled change or Tailoring decision.
5. When Iteration or Recursion changes an Output, affected Inputs and applicable criteria should be reevaluated.
6. Integration must establish completeness within the selected scope and consistency across Process relationships.
7. If a Process View is active, referenced source elements retain their source meaning. View-specific or modified Activities and Tasks must not silently alter Source Process Conformance.
8. Outcome achievement for the composition as a whole should be assessed.
9. When the same information item is changed by multiple Processes, its integrity, state, and change handling must be defined in proportion to quality risk.

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
- Entry/Exit Criteria, applicable requirement Tasks, Outcome evidence, and unresolved matters for each invoked Process have been assessed.
- For combined application, Output/Input mappings and composition integrity have been evaluated.
- Required handoffs, holds, requests to Define ALPS or Manage ALPS, or termination are explicit.
- Any Conformance claim states its subject, scope, basis, and evidence.

## Controls

- Apply the [Process Framework](../../spec/process-framework.md) and [ALPS Specification](../../spec/ALPS-SPEC.md). If they conflict, the Process Framework takes precedence.
- Normative words and their meanings are those defined in the Process Framework.
- Applicable system instructions, user instructions, safety and privacy policies, laws, standards, and agreements must be applied.
- The authoritative representation and managed Tailoring decisions applicable to each selected Process must be applied.
- Execution-environment rules concerning permissions, confirmation, and external effects must be followed.

## Constraints

- Agent Skill discovery or activation must not be treated as Process Invocation unless the selected Agent Skill represents a Process and its Entry Criteria are satisfied.
- A Process Model, Process Reference Model, or Process View must not be executed as though it were a Process.
- Information used only to discover candidates must not be treated as sufficient for Process execution.
- Tailoring must not be performed implicitly. Its scope, applicable Controls and Constraints, decision, and rationale must remain traceable.
- An unspecified execution sequence must not be assumed.
- Agents, models, Agent Skills, tools, and execution environments are Enablers rather than Process Inputs.

## Enablers

Representative Enablers include managed ALPS representations, Agent capabilities, resolution and validation tools, required execution tools, and execution environments.

## Conformance

This Skill represents the Apply ALPS Process. Its own Process Conformance is distinct from Conformance of the Processes selected and invoked through it. Activation of a Process Model, Process Reference Model, or Process View is not Execution Conformance. Source Process Conformance is evaluated against each invoked Process and its applicable basis. Assessment of Process View Outcomes remains separate from Process Outcome Conformance for Source Processes.

## Interfaces & Traceability

| Provider | Output or information item | Recipient | Related information |
|---|---|---|---|
| Manage ALPS | Managed representations, status, Tailoring decisions, application conditions | Apply ALPS | Representation identity, kind, version, scope, and conditions. |
| Process Model / Reference Model / View | Process references and relationships | Representation Selection and Process Resolution | Canonical references, Purpose/Outcomes where applicable, source provenance, and Traceability. |
| Process A | Declared Output | Process B | Recipient Input, meaning, scope, quality conditions, and state. |
| Apply ALPS | Execution evidence, decisions, lessons, measurements | Manage ALPS | Process Instances, limitations, and proposed changes. |
| Apply ALPS | Unmet representation need | Define ALPS | Context, expected outcomes, missing coverage, and risk. |

## Shared Normative References

- Use the repository-shared [Process Framework](../../spec/process-framework.md) as the higher-order normative source.
- Use the repository-shared [ALPS Specification](../../spec/ALPS-SPEC.md) for representation, selection, Invocation, Tailoring, and Conformance rules.

## Bundled Resources

- This root `SKILL.md` is the authoritative English Process Description. For Japanese-language work, use the [Japanese localization](references/locales/ja/SKILL.md); if the localization conflicts with this file, this English description governs.
- [process-instance-record.md](references/process-instance-record.md) provides an optional Process Instance record for situations where the quality risk warrants a durable execution record.

## Common Approach

- Start with the need, then activate Models or Views only when they improve Process selection or composition.
- Treat Model/View activation as context loading and Process Invocation as a separate decision.
- Resolve canonical references before relying on a referenced Process.
- Use Purpose and Outcomes to distinguish overlapping Processes.
- Make cross-Process Output/Input handoffs explicit and reevaluate them after iteration changes shared information.
