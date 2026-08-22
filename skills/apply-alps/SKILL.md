---
name: apply-alps
description: Select Agent Skills suited to an application situation's needs, conditions, and risks; assess Entry/Exit Criteria and applicable Control, Constraint, and Tailoring decisions; execute the Skills singly or in combination; and manage Output/Input handoffs and the completeness and consistency of the composition as a whole. Use when work applies existing Skills, composes multiple Skills, or requires evidence of the application rationale or Outcome achievement. Do not use when the work only defines a new Skill or only adopts, changes, or retires Skill assets. Use also when resolving and applying a default or named Process Model or a compatible Process View. ALPS-conformant.
---

# Agent Lifecycle Process Skill Application

## Purpose

This Skill achieves the intended Outcomes through the single or combined application of Skills suited to the application situation.

## Outcomes

When this Skill succeeds, the following conditions are established.

- a) The needs and conditions of the application situation have been identified.
- b) The Skills to apply and the form of application have been determined with a rationale.
- c) The applicable Control, Constraint, and Tailoring decisions have been identified.
- d) The application results of the Process Instances conform to the declared application scope and to the applicable Control, Constraint, and Tailoring decisions.
- e) The declared Outcomes of the Skills being applied have been achieved.
- f) The required handoffs among Skills have been established.
- g) The completeness and consistency of the Skill composition have been established.

## Activities & Tasks

The order in which the headings, Activities, Tasks, and numbers below appear does not prescribe a procedure or execution sequence. This Skill's Entry Criteria are the decision conditions before invoking this application Process, and its Exit Criteria are the decision conditions before declaring completion; Controls and Constraints apply regardless of where they appear. The Entry Criteria of each selected Skill are assessed separately before invoking that Skill. Use Iteration, Concurrency, Recursion, and Integration as appropriate to the application situation.

### Skill Selection

This Activity determines the Skills to use for the application situation and their form of application. It contributes primarily to a), b), and c).

1. The needs and conditions of the application situation and the applicable Constraints must be identified.
2. Typically, the needs are compared with the Skills' Purposes and Outcomes.
3. Typically, candidate Skills are identified from discovery-layer information, including Skill Discovery Descriptions.
4. When candidates overlap, Purpose should be used to distinguish their scopes.
5. If there is no suitable candidate, the need may be handed off to Skill Need Identification in the definition Process.
6. Whether the uncertainty and risks associated with the application decision are acceptable must be determined.
7. The rationale for the decision should be recorded.


8. `.alps/MODEL.md` should be used as the default Model entry point when present unless another managed Model is explicitly selected.
9. The Model or View binding and ALPS compatibility range must be evaluated before application.
10. Local Skill sources must resolve to authoritative Skill Descriptions, and external plugin sources must preserve plugin and Skill identity.
11. An unresolved or incompatible required source must prevent application unless a managed decision explicitly accepts the unresolved condition within the declared scope.

### Skill Execution

This Activity uses the selected Skills to execute Process Instances and achieve the Process Outcomes declared by those Skills. It contributes primarily to c), d), and e).

1. Whether the Entry Criteria are satisfied must be assessed before a Skill is invoked. If they are not satisfied, invocation must be deferred or the unmet conditions must be resolved first.
2. The availability of the required Inputs and Enablers should be confirmed.
3. The applicable Control, Constraint, and Tailoring decisions must be identified.
4. The Activities and Tasks in the Skill Description must be performed in accordance with their assigned normative attributes. A requirement Task must not be omitted unless it has been legitimately changed through managed Tailoring.
5. Unless a Constraint explicitly specifies one, execution may proceed without assuming a particular sequence.
6. Iteration should continue until problems arising during execution are resolved.
7. A Decision Gate should be applied before an irreversible or high-impact action.
8. Completion must be determined against the Exit Criteria.
9. Outcome achievement should be assessed on the basis of observable evidence.
10. Outputs should be handed off to receivers according to the handoff definition. When quality conditions are specified, their satisfaction should be confirmed.
11. Significant execution decisions, their rationales, and assumptions should be recorded and placed under necessary change management.
12. Lessons learned from execution may be handed off to Skill Assessment and Improvement in the management Process.

### Skill Orchestration

This Activity combines multiple Skills and manages their interfaces, handoffs, and the completeness and consistency of the composition as a whole. It contributes primarily to e), f), and g).

1. The target set of Outcomes must be identified.
2. The provenance of each Skill used in the composition should be identified.
3. A repeatedly used composition may be documented as a Process View.
4. The mapping from each provider Output to each receiver Input must be made explicit.
5. Previously undefined handoffs may be added through Tailoring.
6. When Iteration or Recursion changes an Output, the affected Inputs should be identified and their integrity and the applicable criteria should be reevaluated.
7. Integration must establish completeness within the same level and consistency across different levels.
8. Outcome achievement for the composition as a whole should be assessed.
9. When the same information item is changed by multiple Skills, how its integrity, state, and changes are handled must be defined in proportion to the quality risk.


10. A Process View must be applied from its declared source Models, and every included element must retain its selected, adapted, or new treatment.
11. Adapted and new View elements must not be treated as source-Skill requirements unless managed Tailoring or formal adoption has incorporated them.
12. Model and View relationship tables should be used to seed Output/Input mappings and then refined for the actual application context.
13. Resolution results, accepted unresolved sources, and compatibility decisions should be included in the application record.

## Inputs

Typical Inputs include the needs of the application situation, an invocation request, Skill discovery-layer information and Skill Descriptions, the target set of Outcomes, Inputs defined by Skill Descriptions, Framework-level declarations, and Tailoring decisions. These do not prescribe the only method of execution.

## Outputs

Typical Outputs include the decision on which Skills to apply and the form of application, Outputs defined by Skill Descriptions, the definition of the Skill composition, Outputs of the composition as a whole, and execution and decision records. These do not prescribe the only method of execution.

## Entry Criteria

- Information for identifying the needs is available from the application request or application situation, or can be obtained through confirmation.
- Discovery information for candidate Skills can be accessed, or the unavailability of candidates can be stated explicitly.
- Priority Controls and critical Constraints needed to begin the application decision safely can be identified.

These Entry Criteria are the conditions for starting this application Process. The Entry Criteria of each selected Skill must be assessed separately before invocation.

## Exit Criteria

- The needs, conditions, selection result, form of application, and risk decision have been recorded.
- The Entry/Exit Criteria, requirement Tasks, Outcome evidence, and unresolved matters for each selected Skill have been assessed.
- For combined application, the Output/Input mappings, state of shared information, and Integration have been confirmed.
- The state of Output handoff, hold, handoff of a need to the definition Process, request for a Tailoring decision from the management Process, or termination has been stated explicitly.
- When Conformance is claimed, its basis and evidence have been verified.

## Controls

- Apply the Process Framework and ALPS. If they conflict, the Process Framework must take precedence.
- The normative words and their meanings are those defined in the Process Framework. This Skill does not redefine them.
- Applicable system instructions, user instructions, safety and privacy policies, laws, standards, and agreements must be applied.
- The Skill Description and Framework-level declarations for each selected Skill, together with Tailoring decisions approved through the management Process, must be applied.
- Rules concerning permissions, confirmation, and external effects in the execution environment must be followed.

- When `MODEL.md` or `VIEW.md` is in scope, the declared Environment Binding, location, metadata, compatibility, and resolution rules must be applied.

## Constraints

- Agents, models, Skills, tools, and execution environments must not be treated as Inputs. They must be treated as Enablers.
- Before executing a Skill, the parts of its Skill Description needed for execution must be reviewed. Information used only to identify candidates must not be treated as sufficient for execution.
- A Skill must not be invoked before its Entry Criteria are satisfied. Completion must not be declared before its Exit Criteria have been assessed.
- An execution sequence that is not explicitly specified must not be assumed.
- Tailoring must not be performed implicitly. The applicable Controls and Constraints and the management decision must be traceable. The scope and rationale of the change should also be recorded.
- For an irreversible or high-impact external effect, when an execution-environment Control or Constraint requires passage of a Decision Gate, the effect must not be performed before that passage.

## Enablers

Typical Enablers include managed Skill assets, Agent capabilities, required tools, and execution environments. These do not prescribe the only method of execution.

## Conformance

- A Conformance claim must state its subject, scope, and whether its basis is Outcomes, Tasks, or both.
- Full Conformance to Outcomes must demonstrate achievement of every Outcome listed in the Outcomes section.
- Full Conformance to Tasks must demonstrate satisfaction of every requirement stated with must or must not by an Activity or Task.
- When a decision that no Skill will be applied makes some Outcomes inapplicable, those Outcomes must be declared, Full Conformance must not be claimed, and Tailored Conformance under ALPS 12.3 must be used.
- When a change or exclusion causes the selected Full Conformance basis not to be met, a claim of Tailored Conformance must declare the Skill or Process tailored through the management Process and its scope and must demonstrate satisfaction of every Outcome and Activity/Task requirement that remains within that scope.
- Independent Process Outcome Conformance must not be claimed for an individual Activity alone.

## Interfaces & Traceability

| Provider | Output or information item | Receiver | Related information |
|---|---|---|---|
| Management Process | Managed Skill information, Tailoring decisions, application conditions | Application Process | Recipient Activities: Skill Selection and Skill Execution. Asset, version, status, scope, and conditions. |
| Skill A | Declared Output | Skill B | Recipient Input: declared Input of Skill B. Name, meaning, scope, quality conditions, and state. |
| This application Process | Execution records, decisions, lessons learned, measurement results | Management Process | Recipient Activity: Skill Assessment and Improvement. Process Instances, evidence, limitations, and proposed changes. |
| This application Process | Unmet need | Definition Process | Recipient Activity: Skill Need Identification. Context, expectations, rationale for the absence of a candidate, and risks. |

When a change to an Output affects another Skill's Input, the affected Skill and Input should be identified and the necessary reevaluation should be performed.

## Shared Normative References

This section is informative and has no normative force.

- When ambiguity, conflict, normative-attribute interpretation, Conformance, or Tailoring requires consultation of the governing texts, use the repository-shared [Process Framework](../../.alps/spec/process-framework.md) and [ALPS Specification](../../.alps/spec/ALPS-SPEC.md). Routine application continues to use the selected authoritative Skill Description, applicable Framework-level declarations, and managed Tailoring decisions as its direct basis.

## Bundled Resources

This section is informative and does not require a particular method of execution.

- This root `SKILL.md` is the authoritative English Skill Description. For Japanese-language work, use the [Japanese localization](references/locales/ja/SKILL.md) and its adjacent localized resources. Respond in the user's language; if the localization conflicts with this file, this English description governs.
- When the quality risk justifies a Process Instance record, the lightweight Markdown binding in [process-instance-record.md](references/process-instance-record.md) can be used. It keeps the application basis and intended Outcomes together with the later results, assessments, and evidence in the same human- and machine-readable record.
- `python3 scripts/process_instance_record.py new ...` can create a record from explicitly supplied source statements, and `python3 scripts/process_instance_record.py check --at instantiation|completion <record.md>` can check the binding. The script does not infer Skill meaning, Tailoring, Outcome achievement, or Conformance.

- For Model or View work, use the repository-shared [Markdown Repository and Agent Plugins Binding](../../.alps/bindings/markdown-agent-plugins.md), [MODEL template](../../.alps/templates/MODEL.md), [VIEW template](../../.alps/templates/VIEW.md), `scripts/check_model_view.py`, and `scripts/resolve_model_view.py` with their stated roles and limitations.

## Common Approach

This section is informative and has no normative force.

- Organizing the needs, conditions, target Outcomes, and Constraints before narrowing candidates using information suitable for candidate identification can make selection easier.
- A Process Instance record can be created before execution and completed in the same file after execution. Include detail in proportion to the quality risk and omit inapplicable optional blocks.
- Record the managed source and, when local reviewability matters, the applicable source statements. Add Instance-specific statements or success criteria without treating their mere presence as Tailoring; use the management Process when meaning, normative strength, or applicability is changed.
- Handing an unmet need to the definition Process, and a need for Tailoring to the management Process, can help avoid implicit changes.
- For combined application, a table of the provider Skill, Output, receiver Skill, Input, meaning, scope, and quality conditions can make handoffs easier to verify.
- Combining a managed source reference with readable statements can support both self-contained review and traceability.
- Where non-determinism matters, judging Outcome achievement from more than a single execution, and recording observed variation, evidence limits, and unresolved uncertainty, keeps later assessment grounded; quality risk can guide the need for repeated trials or continued monitoring.
- Records of human approval and intervention, conditions that required intervention, changed or rejected proposals, undetected failures, insufficient explanations or logs, signs of automation bias or excessive intervention, supervisor load and response delays, the adequacy of Decision Gates, and the quality and limits of the evidence used can be handed to Skill Assessment and Improvement in the management Process.
