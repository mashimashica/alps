---
name: manage-alps
description: Govern adopted ALPS representations and their application, including Process Descriptions, Process Models, Process Reference Models, Process Views, and their Skill Packages. Use for adoption, discoverability, controlled change, retirement, Tailoring or formal adoption, assessment, improvement, change impact, communication, or reverification. Use define-alps to create or redefine an authoritative representation and apply-alps to activate representations and invoke selected Processes. ALPS-conformant.
---

# ALPS Management Process

## Purpose

This Process governs ALPS representations and their application and maintains the continual availability of suitable, coherent, and trustworthy ALPS assets.

## Outcomes

Success of this Process establishes the following conditions.

- a) Policies and guidance for managing, deploying, Tailoring, and adopting ALPS representations are established.
- b) Adopted ALPS representations are discoverable with their identity, kind, status, version, and applicable conditions under management.
- c) Changes and retirement are controlled with their impacts, reference integrity, and affected users or representations identified.
- d) Tailoring, formal adoption, and other management decisions are traceable to applicable Controls, Constraints, scope, evidence, and rationale.
- e) Process execution is assessed using criteria appropriate to its declared subject, including Conformance, performance, and effectiveness where relevant.
- f) Managed ALPS representations are assessed using criteria appropriate to their kind, including semantic consistency, Description Conformance, relationship coherence, and applicability where relevant.
- g) Improvement opportunities are prioritized from execution evidence, lessons learned, representation assessments, and change impacts.
- h) Decided improvements are implemented through controlled change.
- i) Representations affected by implemented improvements are reverified.
- j) Resulting management states are updated.

## Activities & Tasks

The order of headings, Activities, Tasks, and numbers does not prescribe an execution sequence. Entry Criteria are evaluated before invocation and Exit Criteria before completion is declared. Controls and Constraints apply irrespective of where they appear. Activities may be applied concurrently, iteratively, or recursively as needed.

### Representation Asset Management

This Activity manages adoption, discoverability, configuration, controlled change, communication, reference integrity, and retirement. It primarily contributes to Outcomes a), b), c), h), i), and j).

1. Means for managing and deploying ALPS representations, together with applicable Tailoring and adoption guidance, should be established.
2. Framework-level Controls, Constraints, and Enablers must be declared together with scope, exceptions, and whether Tailoring is permitted.
3. Verification evidence from the ALPS Definition Process should be confirmed before an authoritative representation is adopted.
4. An adopted representation must retain an identifiable representation kind, authoritative source, management status, and applicable conditions.
5. Canonical references affected by adoption, replacement, relocation, version change, or retirement must be identified.
6. The resolvability of canonical references affected by adoption, replacement, relocation, version change, or retirement must be preserved or deliberately changed through a controlled decision.
7. Changes to a Process Reference Model must identify affected Process semantic centers and referenced Process Descriptions.
8. Changes to a Process Model must identify affected Process membership and relationships.
9. Changes to a Process View must identify affected Source Processes, referenced Activities and Tasks and their Traceability, and application guidance.
10. Changes to a Process Description must identify affected Process Models, Process Reference Models, Process Views, and consumers where applicable.
11. Changes with material impact should be communicated to affected users and representations.
12. A representation whose need no longer exists, that has become unsafe or misleading, or that has been superseded should be retired under a controlled decision.
13. Retired representations may be retained for traceability or reference when permitted by applicable Controls and Constraints.

### Tailoring and Formal Adoption

This Activity controls context-specific changes and determines when View content or Process application requires a change to a managed Process or Model. It primarily contributes to Outcomes a) and d).

1. Application risks, requirements, complexity, capabilities, resources, stakeholder expectations, and relevant standards must be identified.
2. Candidate Processes or life cycle models must be evaluated using conditions of application, available expertise and experience, stakeholder expectations or requirements, and risk tolerance.
3. Each proposed change must be distinguished as context-specific Tailoring or an authoritative redefinition.
4. Compliance of the proposed Tailoring with applicable Controls and Constraints must be confirmed.
5. The Tailoring scope must be stated.
6. Tailoring assumptions should be recorded.
7. Tailoring decision criteria should be recorded.
8. Input from affected parties must be obtained.
9. The rationale for each Tailoring decision should be recorded.
10. When Tailoring changes a Process Name, consistency with its Purpose and Outcomes must be verified.
11. When Tailoring changes a Process Name, Traceability to the source Process must be retained.
12. Traceability must be ensured for changes to Process Outcomes, Activities, Tasks, Inputs, Outputs, Controls, Constraints, or Enablers when they affect the declared Conformance basis.
13. A change to an applicable source Process for a particular application must be handled through managed Tailoring.
14. An authoritative semantic change to an ALPS representation must be handed to the ALPS Definition Process for controlled redefinition.
15. Tailoring effectiveness should be reviewed during application.
16. Tailoring should be revised when conditions change.

### Representation and Process Assessment & Improvement

This Activity assesses representations and Process execution and connects the results to controlled improvement. It primarily contributes to Outcomes e), f), g), h), i), and j).

1. Assessment criteria must be selected according to the representation kind and declared subject.
2. A Process representation may be assessed for Description Conformance, internal consistency, and usability.
3. The Process described by a Process representation may be assessed for the applicable Process Conformance.
4. A Process Instance may be assessed for Execution Conformance, Outcome achievement, performance, and effectiveness as applicable.
5. A Process Model should be assessed for Process coverage, relationship coherence, resolvability, and applicability to its intended Purpose.
6. A Process Reference Model should be assessed for Process identification, Name/Purpose/Outcomes consistency, relationship coherence, resolvability, and suitability as a frame of reference.
7. A Process View should be assessed for Purpose and Outcomes, Source Process provenance and Traceability where source elements are referenced, preservation of source meaning, handoffs, application guidance, and usefulness for its intended concern.
8. Assessment of Process View Outcomes must be distinguished from Outcome Conformance for the applicable source Process.
9. Lessons learned and execution evidence should be collected throughout application and at useful review points.
10. Strengths, weaknesses, defects, gaps, duplication, and inconsistencies should be identified.
11. Improvement opportunities should be prioritized according to evidence, benefit, cost, risk, and impact.
12. A decided change to an authoritative representation must be handed to the ALPS Definition Process for controlled redefinition and verification.
13. Rework or inconsistency arising at references, relationships, or handoffs may be used as an improvement signal.
14. Decided improvements must be implemented through the applicable controlled change.
15. Representations affected by an implemented improvement must be reverified.
16. Management state must be updated after decided improvements are implemented and verified.

## Inputs

Representative Inputs include verified ALPS representations, adoption and change requests, application context, Tailoring guidance, affected-party input, execution and decision records, lessons learned, measurement results, representation-assessment results, and reference-resolution information.

## Outputs

Representative Outputs include managed ALPS representations, adoption and retirement decisions, Tailoring and formal-adoption decisions, change-impact and reference-integrity records, assessment results, prioritized improvements, redefinition or reverification requests, and updated management states.

## Entry Criteria

- A management trigger concerning adoption, change, retirement, Tailoring, formal adoption, assessment, or improvement has been identified.
- The representation or Process subject, its kind, scope, baseline, or assessment period can be identified.
- Primary applicable Controls and Constraints can be confirmed or their absence recorded as unresolved.
- When an irreversible or high-impact management action is anticipated, the necessary authority and Decision Gate can be determined.

## Exit Criteria

- The management subject, representation kind, scope, criteria, and applied Activities are recorded.
- Management decisions, rationale, assumptions, evidence, and affected references are traceable.
- Change, retirement, Tailoring, or adoption impacts and the need for redefinition or reverification are recorded.
- Applicable representation or Process assessment results and unresolved risks are determined.
- Handoffs to the ALPS Definition Process or ALPS Application Process are explicit.

## Controls

- The [Process Framework](../../spec/process-framework.md) and [ALPS Specification](../../spec/ALPS-SPEC.md) must be applied. If they conflict, the Process Framework must take precedence.
- Normative words and their meanings are those defined in the Process Framework.
- Applicable laws or regulatory requirements, policies, contracts, information-management requirements, safety requirements, and user-defined change scope must be applied.
- Framework-level Controls, Constraints, and Enablers must state scope, exceptions, and whether Tailoring is permitted.
- The rigor of application and evidence should be proportional to risk.
- Execution-environment Controls and Constraints governing retention, reference, recovery, deletion, permissions, and external effects must be followed within their declared scope.

## Constraints

- A general Process Description must not require a specific executor, tool, technique, measure, or fixed execution sequence.
- A Process Model, Process Reference Model, or Process View must not be assessed as though it were Process execution.
- A Conformance or effectiveness determination must be based on evidence appropriate to the declared subject and kind.
- Tailoring must not silently change an authoritative representation.
- A View-specific or modified Activity or Task must not contribute to Source Process Conformance merely because it appears in a Process View.
- Formal adoption of a changed semantic element must occur only after controlled redefinition and verification.
- Agents, models, tools, management systems, and execution environments are Enablers rather than Process Inputs.

## Enablers

- Managed representation registers, versions, configurations, canonical references, and change histories
- Stakeholder, domain, risk, and governance expertise
- Agents or tools supporting creation, resolution, comparison, retention, communication, and assessment
- Independent review or audit capability

## Conformance

This Skill represents the ALPS Management Process. Reference Process Conformance of that Process is assessed separately from the Conformance or validity of the representations being managed. Management assessment must state the subject and representation kind. Process Model, Process Reference Model, and Process View assessments must not be reported as Execution Conformance. Tailored Conformance remains a claim about the applicable Process or Processes and declared Tailoring scope.

## Interfaces & Traceability

| Provider | Information item | Recipient |
|---|---|---|
| ALPS Definition Process | Verified authoritative representation and verification evidence | ALPS Management Process |
| ALPS Management Process | Managed representation identity, kind, status, Tailoring decisions, and application conditions | ALPS Application Process |
| ALPS Application Process | Selection rationale, execution evidence, Outcome evidence, handoffs, and lessons | ALPS Management Process |
| ALPS Management Process | Redefinition or reverification request | ALPS Definition Process |

Reference relationships affected by a management decision must remain traceable from the prior state to the resulting state.

## Shared Normative References

- The repository-shared [Process Framework](../../spec/process-framework.md) is the higher-order normative source.
- The repository-shared [ALPS Specification](../../spec/ALPS-SPEC.md) supplies representation, management, Tailoring, and Conformance rules.

## Bundled Resources

- This root `SKILL.md` is the authoritative English Process Description. For Japanese-language work, use the [Japanese localization](references/locales/ja/SKILL.md); if the localization conflicts with this file, this English description governs.
- [management-records.md](references/management-records.md) provides optional record blocks for asset management, Tailoring, assessment, improvement, Decision Gates, changes, retirement, and handoffs.

## Common Approach

- Identify the representation kind before choosing assessment criteria.
- Treat reference integrity as part of change impact whenever Models, Reference Models, or Views are changed.
- Keep context-specific Tailoring distinct from authoritative redefinition.
- Route authoritative semantic changes through the ALPS Definition Process and route application evidence back from the ALPS Application Process.
- Preserve source provenance and Traceability when a View references source elements, and keep View-local descriptions distinct from changes to Source Processes.
