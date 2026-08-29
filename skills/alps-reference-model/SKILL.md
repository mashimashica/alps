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

### ALPS Definition Process

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

### ALPS Application Process

Skill: `skill:#apply-alps`

#### Purpose

This Process selects and activates applicable ALPS representations, resolves the Processes needed for the application situation, and achieves the intended Outcomes through the single or combined application of Process Skills.

#### Outcomes

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

### ALPS Management Process

Skill: `skill:#manage-alps`

#### Purpose

This Process governs ALPS representations and their application and maintains the continual availability of suitable, coherent, and trustworthy ALPS assets.

#### Outcomes

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

## Relationships

| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| ALPS Definition Process | Verified authoritative ALPS representation and verification evidence | ALPS Management Process | Supports adoption, registration, controlled change, and reverification. |
| ALPS Management Process | Managed representations, status, Tailoring decisions, and application conditions | ALPS Application Process | Establishes the authoritative assets and conditions available for application. |
| ALPS Application Process | Selection rationale, execution evidence, Outcome evidence, handoffs, and lessons | ALPS Management Process | Supports assessment, improvement, change, and retirement decisions. |
| ALPS Management Process | Redefinition or reverification request | ALPS Definition Process | Initiates controlled definition or redefinition of an authoritative representation. |
| ALPS Application Process | Unmet representation need | ALPS Definition Process | Initiates definition of missing or unsuitable representation coverage. |

The relationships do not prescribe an execution sequence. The three Processes may be applied iteratively, concurrently, or recursively according to the application situation.

## Use and Integrity

Activate this Agent Skill when the three Reference Processes and their relationships are needed to understand or select applicable Process work. This representation is not an invokable Process, and loading it does not invoke any Process.

Each logical Process Skill reference must resolve to a Process representation whose Name, Purpose, and Outcomes equal those represented here. The [Process Framework](../../spec/process-framework.md) and [ALPS Specification](../../spec/ALPS-SPEC.md) provide the normative basis; a [Japanese localization](references/locales/ja/SKILL.md) is also available.
