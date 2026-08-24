---
name: alps-reference-model
description: Provides the ALPS Reference Model for selecting, composing, and assessing the ALPS definition, application, and management Processes.
metadata:
  alps.kind: process-reference-model
---

# ALPS Reference Model

## Purpose

The ALPS Reference Model defines the Processes required to define, apply, and manage Agent Lifecycle Process Skills and places their relationships in an explicit structure.

## Processes

### Define ALPS

Skill: `skill:mashimashica/alps#define-alps`

#### Purpose

This Process establishes an assessable and usable Skill Description that satisfies identified stakeholder needs.

#### Outcomes

- a) The need to be addressed as a Skill and the intended contexts of use are identified.
- b) The Process Purpose, Outcomes, and boundary are aligned with the selected need.
- c) The Skill Description satisfies the applicable ALPS description requirements.
- d) Elements within the Skill Description and exchanges with external parties are traceable.
- e) The achievability of the Outcomes in representative contexts of use is confirmed.
- f) A decision on Skill adoption can be made from evidence that includes defects and limitations.

### Apply ALPS

Skill: `skill:mashimashica/alps#apply-alps`

#### Purpose

This Process achieves the intended Outcomes through the single or combined application of Processes represented by Skills suited to the application situation.

#### Outcomes

- a) The needs and conditions of the application situation have been identified.
- b) The Processes to apply, the Skills providing their authoritative descriptions, and the form of application have been determined with a rationale.
- c) The applicable Control, Constraint, and Tailoring decisions have been identified.
- d) The application results of the Process Instances conform to the declared application scope and to the applicable Control, Constraint, and Tailoring decisions.
- e) The declared Outcomes of the Processes being applied have been achieved.
- f) The required handoffs among Processes have been established.
- g) The completeness and consistency of the Process composition have been established.

### Manage ALPS

Skill: `skill:mashimashica/alps#manage-alps`

#### Purpose

This Process governs adopted ALPS assets and their application so that suitable Agent Skills, Skill Packages, Process Models, and Process Views remain available, controlled, and fit for their intended use.

#### Outcomes

- a) Policies and guidance for adoption, deployment, Tailoring, assessment, change, and retirement are established.
- b) Adopted Agent Skills, Skill Packages, Process Models, and Process Views are discoverable in a managed state.
- c) Identity, status, version, references, change, and retirement of managed subjects are controlled.
- d) Tailoring decisions and rationale are traceable to applicable Controls and Constraints.
- e) Process application performance is assessed against declared criteria.
- f) The fitness of managed Process Models and Process Views is assessed against declared criteria.
- g) Improvement opportunities are prioritized from evidence, lessons learned, and assessment results.
- h) Decided improvements are implemented.
- i) Subjects affected by implemented improvements are reverified as needed.

## Relationships

| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| Define ALPS | Verified Skill Description and verification evidence | Manage ALPS | Supports adoption, registration, change, and reverification decisions. |
| Manage ALPS | Information about managed Agent Skills, Skill Packages, Process Models, and Process Views; Tailoring decisions; and conditions of application | Apply ALPS | Establishes the managed assets and conditions available for application. |
| Apply ALPS | Execution and decision records, lessons learned, and measurable results | Manage ALPS | Supports assessment, improvement, change, and retirement decisions. |
| Manage ALPS | Change requests, redefinition requests, and reverification requests | Define ALPS | Initiates definition, redefinition, or reverification when an authoritative description or representation must change. |

The relationships do not prescribe an execution sequence. The three Processes can be applied iteratively, concurrently, or recursively when the application situation requires it.

## Application

Activate this Agent Skill to load the ALPS Reference Model. Use `apply-alps` to select and compose the referenced Processes for the application situation. Loading this Reference Model does not itself invoke a Process.

## Verification

A representation of this Process Reference Model is valid only when each referenced Process Skill resolves and its Name, Purpose, and Outcomes retain the same semantic center represented here. Purpose and Outcomes are required to match their authoritative Process Descriptions.

## Conformance

This Process Reference Model can be assessed as a Process Reference Model representation. Process Outcome Conformance and Process Task Conformance remain claims about the referenced Processes and their Process Instances, not about activation of this Agent Skill.

## Bundled Resources

- [Process Framework](../../spec/process-framework.md)
- [ALPS Specification](../../spec/ALPS-SPEC.md)
- [Japanese localization](references/locales/ja/SKILL.md)
