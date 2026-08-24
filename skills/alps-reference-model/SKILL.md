---
name: alps-reference-model
description: Provides the ALPS Reference Model for selecting, composing, assessing, and improving the ALPS definition, application, and management Processes.
metadata:
  alps.kind: process-reference-model
---

# ALPS Reference Model

## Purpose

The ALPS Reference Model defines the Processes required to define, apply, and manage Agent Lifecycle Process Skills and places their relationships in an explicit structure.

## Processes

### Define ALPS

Skill: `skill:#define-alps`

#### Purpose

This Process establishes an assessable and usable ALPS representation that satisfies an identified need while preserving the semantics of the represented Process Framework construct.

#### Outcomes

- a) The need for the ALPS representation and the intended contexts of use are identified.
- b) The represented Process Framework construct, Purpose, boundary, and required level of detail are aligned with the selected need.
- c) The authoritative representation satisfies the applicable Process Framework and ALPS requirements for its representation kind.
- d) References, relationships, provenance, and exchanges required by the representation are traceable and resolvable.
- e) A Process Description has demonstrated Outcome achievability in representative contexts, or a non-Process representation has demonstrated semantic consistency and applicability to its intended concern.
- f) A decision on adoption can be made from verification evidence that includes defects, assumptions, and limitations.

### Apply ALPS

Skill: `skill:#apply-alps`

#### Purpose

This Process selects and activates applicable ALPS representations, resolves the Processes needed for the application situation, and achieves the intended Outcomes through the single or combined application of Process Skills.

#### Outcomes

- a) The needs, conditions, and risks of the application situation are identified.
- b) Applicable Process Models, Process Reference Models, Process Views, and Process representations are selected or activated as needed, and candidate Processes are resolved from them.
- c) The Process Skills to invoke and the form of application are determined with a rationale.
- d) Applicable Controls, Constraints, Tailoring decisions, and Decision Gates are identified before affected actions occur.
- e) Process Instances are executed within the declared application scope and applicable Controls, Constraints, and Tailoring decisions.
- f) The declared Outcomes of the applied Processes are achieved with observable evidence.
- g) Required handoffs and the completeness and consistency of the Process composition are established.

### Manage ALPS

Skill: `skill:#manage-alps`

#### Purpose

This Process governs ALPS representations and their application and maintains the continual availability of suitable, coherent, and trustworthy ALPS assets.

#### Outcomes

- a) Policies and guidance for managing, deploying, Tailoring, and adopting ALPS representations are established.
- b) Adopted ALPS representations are discoverable with their identity, kind, status, version, and applicable conditions under management.
- c) Changes and retirement are controlled with their impacts, reference integrity, and affected users or representations identified.
- d) Tailoring, formal adoption, and other management decisions are traceable to applicable Controls, Constraints, scope, evidence, and rationale.
- e) Process execution is assessed using criteria appropriate to its declared subject, including Conformance, performance, and effectiveness where relevant.
- f) Managed ALPS representations are assessed using criteria appropriate to their kind, including semantic consistency, description Conformance, relationship coherence, and applicability where relevant.
- g) Improvement opportunities are prioritized from execution evidence, lessons learned, representation assessments, and change impacts.
- h) Decided improvements are implemented through controlled change.
- i) Representations affected by implemented improvements are reverified.
- j) Resulting management states are updated.

## Relationships

| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| Define ALPS | Verified authoritative ALPS representation and verification evidence | Manage ALPS | Supports adoption, registration, controlled change, and reverification. |
| Manage ALPS | Managed representations, status, Tailoring decisions, and application conditions | Apply ALPS | Establishes the authoritative assets and conditions available for application. |
| Apply ALPS | Selection rationale, execution evidence, Outcome evidence, handoffs, and lessons | Manage ALPS | Supports assessment, improvement, change, and retirement decisions. |
| Manage ALPS | Redefinition, reverification, or formal-adoption request | Define ALPS | Initiates controlled definition or redefinition of an authoritative representation. |

The relationships do not prescribe an execution sequence. The three Processes may be applied iteratively, concurrently, or recursively according to the application situation.

## Application

Activate this Agent Skill to load the ALPS Reference Model. Use Apply ALPS to select or activate relevant Models and Views, resolve the required Processes, and invoke only Agent Skills that represent Processes. Loading this Reference Model does not itself invoke a Process.

## Verification

This Process Reference Model is valid only when each referenced Process Skill resolves, represents a Process, and has the same Process Name, Purpose, and Outcomes represented here. Purpose and Outcomes must match their authoritative Process Descriptions. A mismatch is an error and neither representation silently overrides the other.

## Conformance

This Process Reference Model can be assessed as a Process Reference Model representation. Process Outcome Conformance and Process Task Conformance remain claims about the referenced Processes and their Process Instances. Activation of this Agent Skill is not Process Invocation or Execution Conformance.

## Bundled Resources

- [Process Framework](../../spec/process-framework.md)
- [ALPS Specification](../../spec/ALPS-SPEC.md)
- [Japanese localization](references/locales/ja/SKILL.md)
