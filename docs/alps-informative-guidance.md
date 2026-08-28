# ALPS Informative Guidance

<p align="right">
  <strong>English</strong> | <a href="locales/ja/alps-informative-guidance.md">Japanese</a>
</p>

This document is informative. It adds no ALPS requirement, representation element, or Conformance criterion and does not alter the Process Framework, the ALPS Specification, or an authoritative Agent Skill representation.

## 1. Process Skill Example

The following example uses a file-based Agent Skill representation. The physical form is illustrative; the semantic distinctions are the relevant part.

```markdown
---
name: consolidate-meeting-minutes
description: Extract decisions, action items, and open issues from meeting records, then produce minutes that preserve traceability to the source record. Use when asked to organize meeting records, produce minutes, or organize post-meeting actions. ALPS-conformant.
---

# Meeting Minutes Consolidation Skill

## Purpose

This Process establishes a state in which decisions, action items, and open issues can be distinguished from the meeting record.

## Outcomes

- Decisions made in the meeting are identified.
- Action items and their due dates are identified.
- Open issues are identified.
- Mappings between the consolidated content and the source record are traceable.

## Activities & Tasks

The order shown does not prescribe execution order.

### Record Understanding

1. The scope of consolidation and gaps in the records must be identified.
2. Unclear statements must not be completed by conjecture.
3. Applicable policies for handling confidential information must be applied.
4. The list of participants and agenda items is typically confirmed.

### Item Extraction

1. Decisions, action items, and open issues must be distinguished and identified.
2. A decision not present in the source records must not be included in the Output.
3. Each action item should be associated with a due date.
4. Items may be assigned a priority classification.

### Establishment of Verifiability

1. Mappings between extracted items and the source records must be maintained.
2. The Output must be transferred only after those mappings have been established.
3. Items that cannot be confirmed from the source records should be marked as requiring confirmation.

## Inputs

Meeting records, including notes, transcripts, and distributed materials.

## Outputs

Consolidated meeting minutes.

## Entry Criteria

- A meeting record is available.
- The scope of consolidation is stated.

## Exit Criteria

- Achievement of every Outcome has been determined.
- The Output has been transferred to the recipient.

## Controls

- Applicable policies for handling confidential information.

## Constraints

- The Output is limited to decisions, action items, and open issues supported by the source records.
- Transfer is permitted only after mappings between extracted items and the source records have been established.

## Enablers

- Transcription support tools
- Domain glossary
- Natural-language-processing capability of the performer

## Common Approach

This section is reference information and has no normative force.

- Decisions often appear near expressions of agreement or approval.
- For a lengthy record, Iteration can proceed by agenda item.
```

The consolidated minutes are an Output, not an Outcome. The transfer condition is a Constraint, while the corresponding transfer action is a Task. Tools and performer capability are Enablers rather than Inputs.

## 2. File-Based Skill Package Example

An Environment Binding can represent a Skill Package as files without changing the logical roles defined by ALPS.

```text
<skill-name>/
├── SKILL.md
├── references/
│   └── <reference>.md
├── scripts/
└── assets/
```

| Component | Representative ALPS treatment |
|---|---|
| `SKILL.md` | The authoritative Agent Skill representation. For a Process, its body supplies the authoritative Skill Description; discovery information may be projected into frontmatter or another registration record. |
| `references/` | Reference information loaded as needed. Individual filenames are not prescribed by ALPS. |
| `scripts/` | Execution resources supporting reproducibility or reliability, typically treated as Enablers. |
| `assets/` | Resources used to create Outputs or support application, classified according to function. |

Storage groupings are optional. A Package needs only the resources that directly support understanding or applying its represented PF construct.

## 3. Related Documents

### 3.1 Agent Skills Specification

The [Agent Skills Specification](https://agentskills.io/specification) defines an open, file-based format centered on `SKILL.md`, with optional directories for scripts, references, and assets. When used for an ALPS representation, it supplies an Agent-facing packaging, discovery, and loading form; ALPS supplies PF-based semantics, life-cycle rules, representation integrity, and Conformance rules.

### 3.2 AGENTS.md

[AGENTS.md](https://agents.md/) is an open format for repository-scoped context and instructions to coding Agents. It can direct Agents to discover, select, apply, and manage ALPS representations and can state repository Controls and Constraints. It is not itself an ALPS representation and does not alter a normative source.

### 3.3 Related Life-Cycle Standards

The following standards address life-cycle Processes or Process description in related fields:

- ISO/IEC/IEEE 15288 — system life-cycle Processes;
- ISO/IEC/IEEE 12207 — software life-cycle Processes; and
- ISO/IEC/IEEE 24774:2021 — specification for Process description.

They are informative references for readers who also work with those standards. ALPS and the Process Framework were written independently; Conformance to ALPS neither requires nor establishes Conformance to those standards. ALPS is not developed, approved, or certified by their publishers.

Terminology must be mapped before comparing claims. Some life-cycle standards use a Process View as a concern-oriented projection with profile-specific assessment rules. PF's Process View definition and Conformance boundary govern ALPS; a claim made under another standard does not transfer automatically.

Some life-cycle Process descriptions express production of an artifact in an Outcome. Under PF, the artifact is an Output; an observable result condition established or evidenced by that artifact is an Outcome. This distinction preserves the separation between work products and successful Process state.

## 4. Allocation Between PF and ALPS

PF remains authoritative for every general Process concept. ALPS specializes those concepts only where Agent Skill representation or the ALPS life cycle requires additional rules.

| PF subject | PF authority | ALPS specialization |
|---|---|---|
| Work and Process Description | Process, Process Description, Process Instance, required semantic core, layers, and writing rules | Skill Description plus discovery and execution layers |
| Intent and work content | Name, Purpose, Outcome, Output, Activity, and Task | Agent-facing discovery consistency and distinguishable Task operation and object |
| Process boundary | Granularity, cohesion, performer independence, and selection | Process Skill versus Process View representation boundary |
| Boundary elements and exchanges | Inputs, Outputs, Controls, Constraints, Enablers, criteria, handoffs, and Traceability | Skill Package resource roles and cross-Skill composition |
| Reusable structures | Process Model, Process Reference Model, Process Framework, life cycle model, and Process View | Representation kinds and the ALPS Reference Model integrity contract |
| Combined application | Concurrency, Iteration, Recursion, and Integration | Activation, Process resolution, Invocation, and Agent Skill composition |
| Adaptation | Tailoring and Process Instantiation | Managed Tailoring and authoritative redefinition through the ALPS reference Processes |
| Evidence and claims | Decision Gates, reviews, audits, Process Conformance, and Capability | ALPS-specific Conformance subjects and representation assessment boundaries |
| Management and improvement | General Process governance, measures, benchmarking, and learning | Define ALPS, Apply ALPS, and Manage ALPS as the ALPS reference life cycle |

## 5. Human Oversight, Accountability, and Evidence

The matters in this section are open considerations rather than settled practice. They provide informative guidance for application and improvement only.

### 5.1 Composing Human Oversight

Human Oversight is not a separate Skill Description element. A context requiring oversight can compose it from:

- Controls directing execution or judgment;
- Constraints limiting permitted execution;
- Enablers supplying human capability;
- Entry Criteria and Exit Criteria conditioning Invocation and completion;
- Decision Gates before irreversible or high-impact actions;
- execution and decision records; and
- judgments made through Apply ALPS and Manage ALPS.

The context determines the form of oversight, intervention conditions and granularity, deciding authority, and escalation path from risk, impact, reversibility, uncertainty, and the Capabilities of the humans and Agents involved.

Non-determinism, emergent behavior, supervisor cognitive load, automation bias, and unclear responsibility relationships can make oversight difficult. These are Agent-context considerations rather than general PF semantics.

### 5.2 Traceability and Accountability

**Traceability** is the property that relationships among Inputs, judgments, Tasks, Outputs, evidence, and changes can be followed.

**Accountability** is the relationship determining who holds decision authority, supervisory responsibility, or the obligation to answer for a Process Instance.

Traceability supports Accountability but does not assign responsibility. A general Process Description fixes neither a performer nor an organization. A Process Instance can identify its responsibilities, authority, approvers, and escalation paths. Logs and audit evidence support later verification and help clarify those relationships.

### 5.3 Human Capability

Human expertise, judgment, and capacity to intervene can be Enablers. Cognitive load, response time, and supervisor availability can be Constraints. If required oversight capability is unavailable, Entry Criteria may not be satisfied.

Conformance of one Process Instance does not establish the general Capability of a supervisor or oversight regime, and a high Capability assessment does not establish Conformance of one execution.

ALPS defines no human Capability levels, maturity model, or certification scheme.

### 5.4 Non-Deterministic Process Skills

Outcome and Conformance definitions do not change for non-deterministic behavior. Risk-based Representation Verification, Outcome evidence, and Tailoring can be applied as follows:

- one execution is not treated as sufficient evidence of Outcome achievability or a Capability level when variation matters;
- representative contexts include boundary, abnormal, and novel situations;
- when a unique expected result cannot be defined, acceptance conditions, prohibited conditions, or an evaluation method are defined instead;
- execution records retain observed variation, evidence limits, and unresolved uncertainty; and
- quality risk determines whether repeated trials or continuous monitoring are needed.

Non-determinism and the absence of one expected result can complicate both verification and human oversight.

### 5.5 Returning Oversight Results to Manage ALPS

Apply ALPS can hand the following representative information to Manage ALPS as execution records and lessons:

- records of human approval and intervention;
- conditions that made intervention necessary;
- cases in which a human changed or rejected an Agent proposal;
- failures humans did not detect;
- cases in which explanations or logs were insufficient for judgment;
- signs of automation bias or excessive intervention;
- supervisor load and response delays;
- excess or deficiency of Decision Gates; and
- the quality and limits of the evidence used.
