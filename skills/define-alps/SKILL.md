---
name: define-alps
description: Identify needs for ALPS representations; define and verify Process Descriptions, Process Models, Process Reference Models, and Process Views in accordance with ALPS and the Process Framework. Use when creating or redefining an ALPS representation, establishing its Purpose and boundary, reviewing applicable Description Conformance, verifying references and semantic consistency, trialing a Process Description in representative contexts, or producing evidence for adoption. Use manage-alps when the work concerns only adoption, controlled change, Tailoring, or retirement. ALPS-conformant.
---

# ALPS Definition Process

## Purpose

This Process establishes an assessable and usable ALPS representation that satisfies an identified need while preserving the semantics of the represented Process Framework construct.

## Outcomes

Success of this Process establishes the following conditions.

- a) The need for the ALPS representation and the intended contexts of use are identified.
- b) The represented Process Framework construct, Purpose, boundary, and required level of detail are aligned with the selected need.
- c) The authoritative representation satisfies the applicable Process Framework and ALPS requirements for its representation kind.
- d) References, relationships, provenance, and exchanges required by the representation are traceable and resolvable.
- e) A Process Description has demonstrated Outcome achievability in representative contexts, or a non-Process representation has demonstrated semantic consistency and applicability to its intended concern.
- f) A decision on adoption can be made from verification evidence that includes defects, assumptions, and limitations.

## Activities & Tasks

The headings, Activities, Tasks, and numbers below present the content for readability and do not prescribe an execution sequence. Entry Criteria are evaluated before invocation, and Exit Criteria before completion is declared. Controls and Constraints apply regardless of where they appear. Iteration, Concurrency, and necessary redesign may be used according to the application context.

### Representation Need Identification

This Activity identifies a need and determines whether it should be represented as a Process, Process Model, Process Reference Model, or Process View. It primarily contributes to Outcomes a) and b).

1. Candidate needs should be collected from recurring work, composition needs, cross-cutting concerns, lessons learned, gaps, and failure cases.
2. Intended users, stakeholders, and contexts of use must be identified.
3. Existing ALPS representations should be investigated for duplication, adjacency, reuse, or gaps.
4. The represented Process Framework construct must be selected according to the meaning of the need rather than the preferred storage or presentation format.
5. A Process must be selected when an independent Process boundary with Purpose and Outcomes is established.
6. A Process Model should be selected when the need is to organize related Processes and their relationships.
7. A Process Reference Model should be selected when the need is to define individual Processes by Name, Purpose, and Outcomes and place them in an explicit relationship structure.
8. A Process View should be selected when the need is to organize Activities and Tasks from multiple source Processes around a particular concern or Purpose without creating an independent Process boundary.
9. Expected benefits, risks, and costs should be evaluated.
10. The rationale for selection or deferral should be recorded.

### Representation Design

This Activity determines the structure and content required by the selected representation kind. It primarily contributes to Outcomes b), c), and d).

1. The authoritative representation must preserve the meaning of the represented Process Framework construct.
2. An Agent Skill representing a Process must contain a Process Description with Name, Purpose, and Outcomes.
3. The Process Description must apply the applicable rules in Clause 6 of ALPS.
4. Discovery-layer and execution-layer information must be distinguished in a Process Description.
5. Each Task in a Process Description must express an individual action supporting one or more Outcomes so that its object and operation are distinguishable.
6. The normative attribute of each normative statement in a Process Description must be made distinguishable.
7. A Process Model must identify its Processes and their relationships.
8. A Process Model may identify the Agent Skills that provide the authoritative Process Descriptions.
9. A Process Reference Model must identify each included Process by Name, Purpose, and Outcomes.
10. A Process Reference Model must identify the relationships among its included Processes.
11. A Process Reference Model must identify the corresponding Process Skill where one is supplied for an included Process.
12. A Process View must state Name, Purpose, and Outcomes.
13. A Process View must identify every source Process that it references.
14. A Process View must maintain provenance and Traceability for referenced source Activities and Tasks.
15. A Process View may describe View-local Activities and Tasks where needed for its concern or Purpose.
16. A Process View must provide application guidance.
17. Logical references among Agent Skill representations must use the canonical Skill-reference rules in ALPS rather than repository-relative paths as identity.
18. When a Skill Package includes accompanying resources, their role and conditions of use must be identified.
19. Relationships and handoffs that affect another representation or Process should be made explicit where needed.

### Representation Verification

This Activity verifies the representation against its kind-specific requirements and its intended use. It primarily contributes to Outcomes c), d), e), and f).

1. The authoritative representation must be reviewed against the Process Framework and the applicable ALPS requirements.
2. The correspondence between the declared or default representation kind and the construct actually represented must be checked.
3. Mandatory references must be resolved to the intended targets.
4. A Process Description must be checked for Name, Purpose, Outcomes, element classification, normative attributes, non-prescription of implementation, and consistency between discovery and execution information.
5. The achievability of Process Outcomes should be evaluated through representative trials when the representation is a Process Description.
6. A Process Model must be checked for identifiable Processes and coherent relationships.
7. A Process Reference Model must be checked for the required Name, Purpose, and Outcomes of each Process and for equality of that semantic center with each referenced authoritative Process Description.
8. A Process View must be checked for source provenance and Traceability where source elements are referenced, preservation of source Process meaning, relationships or handoffs, application guidance, and separation of View-local descriptions from changes to source Processes.
9. The review should include a perspective independent of the author when the quality risk warrants it.
10. Detected defects, assumptions, limitations, and unresolved references must be recorded.
11. Defect treatment should be completed or explicitly dispositioned before an adoption Decision Gate.
12. When a Skill Package is in scope, consistency between the authoritative representation and its accompanying resources must be verified.

## Inputs

Representative Inputs include stakeholder expectations, needs and change requests, existing ALPS representations, execution evidence when relevant, and representative contexts of use.

## Outputs

Representative Outputs include the selected representation need and rationale, a verified authoritative ALPS representation, traceability and reference information, verification results, and defect-treatment records.

## Entry Criteria

- A need, problem, concern, composition requirement, lesson, or change request for which an ALPS representation is being considered is available.
- Intended users, stakeholders, and contexts of use can be identified.
- Applicable Process Framework and ALPS requirements can be consulted.
- Applicable Controls and Constraints can be identified, or their absence can be recorded as unresolved.

## Exit Criteria

- The representation kind and scope are explicit.
- Achievement against the applicable representation and Conformance criteria has been determined with observable evidence appropriate to the kind.
- Mandatory references resolve and required semantic-consistency checks have passed.
- Unresolved defects, assumptions, limitations, and boundary cases are recorded.
- The verified representation and verification evidence can be transferred for adoption or management.
- Completion means that adoption can be decided; it does not itself mean adoption or publication.

## Controls

- The [Process Framework](../../spec/process-framework.md) and [ALPS Specification](../../spec/ALPS-SPEC.md) must be applied. If they conflict, the Process Framework must take precedence.
- Normative words and their meanings are those defined in the Process Framework.
- A representation must preserve the meaning of the Process Framework construct it represents.
- Name, Purpose, and Outcomes must be written and interpreted according to the applicable Process Framework rules.
- Discovery-layer and execution-layer information may be represented together or separately, provided that they remain distinguishable and the authoritative Process Description remains identifiable.
- Applicable verification criteria govern Representation Verification as Controls.
- Applicable laws, regulatory requirements, policies, standards, and agreements must be applied within their declared scope.
- Repository and execution-environment rules governing creation, verification, and saving must be followed.

## Constraints

- A general Process Description must not normatively fix a specific performer, Task allocation, method, tool, metric, or execution sequence.
- Process Models, Process Reference Models, and Process Views must not be treated as Processes merely because they are represented by Agent Skills.
- Agent Skill activation must not be treated as Process Invocation for a non-Process representation.
- Agents, models, tools, and execution environments must not be treated as Inputs to a Process; they are Enablers.
- A Decision Gate is a separate decision mechanism and must not be treated as a component of a Process Description.
- Reference information must not alter the meaning or normative force of the authoritative representation.
- Mandatory references must be resolvable, and unnecessary duplication or conflict must not arise between an authoritative representation and accompanying resources.

## Enablers

- Stakeholder and domain expertise
- Managed ALPS representations and change history
- Agents or tools supporting drafting, comparison, search, resolution, and trials
- Independent review capability

## Conformance

This Skill represents the ALPS Definition Process. Its Skill Description may be assessed for Description Conformance, the represented Process for Reference Process Conformance, and a Process Instance resulting from Process Invocation for Execution Conformance. The representation produced by this Process is assessed separately according to its own kind. A successful execution of the ALPS Definition Process does not by itself establish Conformance of the produced representation unless the applicable representation checks and evidence have been satisfied.

## Interfaces & Traceability

| Information item provided | Primary recipient | Related information |
|---|---|---|
| Verified ALPS representation | ALPS Management Process | Adoption subject, kind, version, conditions of use, and verification results. |
| Verification results and defect treatment | Adoption Decision Gate | Decision criteria, evidence, unresolved limitations, and decision. |
| Semantic mappings and references | Assessment or reverification | Source and target identities, required equality or provenance, and status. |
| Redefinition and reverification results | ALPS Management Process | Change request, affected scope, and post-change evidence. |

## Shared Normative References

- The repository-shared [Process Framework](../../spec/process-framework.md) is the higher-order normative source.
- The repository-shared [ALPS Specification](../../spec/ALPS-SPEC.md) supplies Agent Skill representation, life-cycle, and Conformance rules.

## Bundled Resources

- This root `SKILL.md` is the authoritative English Process Description. For Japanese-language work, use the [Japanese localization](references/locales/ja/SKILL.md); if the localization conflicts with this file, this English description governs.
- [SKILL-template.md](references/SKILL-template.md) is an informative Process Description output-creation resource; its concrete headings and order do not define ALPS requirements.
- [record-templates.md](references/record-templates.md) is an informative output-creation resource for definition and verification records.
- [skill-package-format.md](references/skill-package-format.md) is reference information for identifying logical Package resource roles.
- These resources must not override ALPS or the Process Framework. Official form validation and repository review remain separate from the ALPS Definition Process itself.

## Common Approach

- Start from the need and select the Process Framework construct before choosing a file layout.
- For a Process, work backward from Outcomes into Activities and Tasks and then trace back to the Outcomes.
- For a Process Reference Model, compare each Process semantic center semantically against its authoritative Process Description.
- For a Process View, review source provenance and Traceability for referenced source elements, application guidance, and the separation between View-local descriptions and changes to source Processes.
- Use representative trials for Process Outcome achievability and structural/semantic review for non-Process representations.
