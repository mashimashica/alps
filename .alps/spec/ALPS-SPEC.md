# ALPS — Agent Lifecycle Process Skills Specification

---

## Foreword

This specification, ALPS (Agent Lifecycle Process Skills), applies the Process Framework (hereafter “PF”) to Agent Skills. Authors vary in the granularity, normative force, life cycle management, and conformance criteria they use for Agent Skills. A shared Skill Description structure makes results more consistent and supports Skill deployment, Tailoring, improvement, and Assessment. Name, Purpose, and Outcomes establish shared reference points for Skill execution and Assessment (PF 1.2). This specification therefore establishes common rules for Skill description, life cycle management, and conformance.

This specification treats a Skill as a Process Description and applies the PF design principles throughout the Skill life cycle.

---

## Contents

- 1. Scope
- 2. Normative Reference and Precedence
- 3. Terms and Definitions
- 4. Normative Language and Conventions
- 5. Fundamental Concepts
- 6. Requirements for Skill Descriptions
- 7. Skill Life Cycle and ALPS Reference Model
- 8. Skill Execution Structures and Relationships
- 9. Controls, Constraints, and Enablers
- 10. Entry/Exit Criteria, Decision Gates, and Reviews
- 11. Tailoring and Process Instantiation
- 12. Conformance, Capability, and Assessment
- Appendix A (informative) Examples of a Skill Description and Skill Package
- Appendix B (informative) Correspondence with the Process Framework
- Appendix C (informative) Related Documents
- Appendix D (informative) Human Oversight, Accountability, and Evidence in Agent Contexts

---

## 1. Scope

### 1.1 Matters Specified by This Specification

This specification establishes:

a) Requirements, recommendations, and writing rules for describing an Agent Skill as a Process Description (Clauses 5 and 6).

b) A reference model defining the three Processes that constitute the Skill life cycle and their constituent Activities and Tasks (the ALPS Reference Model; Clause 7).

c) Rules for execution structures, interfaces, exchanges, and Process Views used to apply multiple Skills in combination (Clause 8).

d) The declaration and handling of Controls, Constraints, and Enablers applicable to Skills (Clause 9), and the application of Entry/Exit Criteria, Decision Gates, reviews, and audits (Clause 10).

e) Rules for Tailoring and Process Instantiation (Clause 11), criteria for claims of Conformance to this specification and to Skills, and treatment of Capability (Clause 12).

f) The logical composition and integrity of a Skill Package comprising a Skill Description and accompanying resources that support understanding or executing the Skill or creating its Outputs (5.7).

### 1.2 Matters Not Specified by This Specification

This specification does not establish:

a) A concrete implementation form for a Skill Package. File formats, metadata formats, physical storage structures, distribution mechanisms, and toolchains are outside the scope of this specification. However, 5.7 applies to the logical composition and integrity of the Skill Description and accompanying resources.

b) A particular Agent implementation, model, execution environment, or vendor.

c) Details of technical information-security and safety measures. Requirements arising from such measures are handled as Controls or Constraints within the framework of this specification (Clause 9).

d) The content of the individual business domains described by Skills.

### 1.3 Intended Users

This specification is intended for authors who draft Skills, managers of Skill assets, providers and operators of Agents that execute Skills, and assessors of Conformance of a Skill or its execution.

## 2. Normative Reference and Precedence

The following document is indispensable for application of this specification:

- **Process Framework** (`process-framework.md`). It is abbreviated as “PF” in the text and referenced by clause number, as in “PF 4.3.”

If this specification conflicts with the PF, the PF takes precedence. This specification must not relax a PF requirement or permit an action that the PF prohibits. The specialization of PF constructs for Agent Skills is given in 5.8.

## 3. Terms and Definitions

Terms defined or used in the PF are used with the meanings given in the PF. In addition, the following terms are defined.

**3.1 Agent**
An executing entity capable of performing Activities and Tasks under a stated Purpose, with some autonomy in observing its environment, making judgments, and acting. This includes software systems operating under human direction or supervision.

**3.2 Agent Skill (Skill)**
A unit consisting of a reusable Process Description, and accompanying resources when needed, made into an asset in a form that an Agent can discover, load, and execute. It is referred to simply as a “Skill” in this specification.

**3.3 Skill Description**
The Process Description constituting the content of a Skill. It has Name, Purpose, and Outcomes as mandatory elements and can include optional elements and reference information (see Clause 6).

**3.4 Discovery Layer and Execution Layer**
ALPS-specific functional presentation layers through which a Skill Description is made available to an Agent. The discovery layer presents the Name and concise reference information used to discover the Skill and determine its applicability before the complete Skill Description is loaded. The execution layer presents the authoritative Process Description elements and reference information used to execute and assess the Skill.

These layers do not add Process Description elements and do not require a particular physical separation, file format, or storage structure.

**3.5 ALPS Reference Model**
The Process Reference Model in Clause 7 of this specification, which defines the ALPS definition process, ALPS application process, and ALPS management process through their respective Purposes and Outcomes. Each Process comprises three Activities. The model can be used as a frame of reference for assessment and improvement of the Skill life cycle.

**3.6 Invocation**
Determining that Entry Criteria are satisfied and beginning execution of a Process Instance through a selected Skill.

**3.7 Skill Asset**
A Skill or Skill Package that has been adopted and placed under management.

**3.8 Skill Discovery Description**
Concise reference information placed in the ALPS-specific discovery layer that an Agent uses to discover a Skill and determine its applicability before loading the complete Skill Description. It states what the Skill does, when the Skill is used, and the information needed to determine applicability.

**3.9 Skill Package**
A unit managed as a whole that contains one Skill Description and any accompanying resources that support understanding or executing the Skill or creating its Outputs.

## 4. Normative Language and Conventions

### 4.1 Normative Language

The normative words used in this specification and in Skill Descriptions, and their meanings, are those defined in the PF. This specification does not redefine them. To avoid confusing normative meanings (PF 1.4), this specification and Skill Descriptions must use those words so that the normative attribute of a statement can be determined.

The following table restates the PF vocabulary as reference information and does not alter it.

| Normative attribute | English expression |
|---|---|
| Requirement | must / must not |
| Recommendation | should / should not |
| Permissible action | may |
| Typical action | typically |

“Can” and “could” express possibility or capability and have no normative attribute. Uppercase renderings of these words are not used.

### 4.2 Normative and Informative Parts

The main text of this specification (Clauses 1 through 12) is normative. Notes, examples, and appendices marked “informative” are informative. Informative material must not alter normative force (PF 1.4). The same rule applies to reference information in a Skill Description (see 6.3.8).

## 5. Fundamental Concepts

### 5.1 A Skill Is a Process Description

The content of a Skill must be written as a Process Description conforming to the PF.

A Skill Description can describe a general Process or, when explicitly scoped to a particular context, a Process Instance. A description of a Process Instance can specify the required capabilities, resources, Inputs, Outputs, Constraints, Controls, and time (PF 1.1).

### 5.2 Dual Nature of a Skill: Process Description and Enabler

A Skill is a Process Description in its content and functions as an Enabler for the Process that uses it.

Skills, Agents, and tools must be treated as Enablers, not as Inputs (PF 4.1).

### 5.3 Non-Prescription of Performers

A Skill Description must not prescribe the structure of the performer or allocation of Tasks. Capabilities or conditions needed for execution should be stated as Enablers or Constraints without allocating Tasks (PF 3.2).

### 5.4 Skill Boundary and Granularity

Skill boundaries are typically established from primary Outputs and Outcomes rather than from intermediate Outputs of Activities (PF 3.1). Within a Skill, strong relationships are maintained among Outcomes, Activities, and Tasks, while dependencies on other Skills are reduced as far as practicable.

A significant Activity containing many Tasks may be described as a separate Skill with its own Purpose and Outcomes (PF 3.1).

When the definition, maintenance, assessment, or change handling of an information item spanning multiple Skills has an independent Purpose and Outcomes and mutually cohesive Activities, and can be bounded as one Process, it may be described as a separate Skill. By contrast, when no independent Process boundary is established and relationships among existing Skills are presented as a cross-cutting concern, it can be described as a Process View (8.3).

### 5.5 Functional Layers and Progressive Disclosure

PF 1.3 permits a Process Description to present information in layers for readers with different needs. For Agent Skills, ALPS defines a discovery layer and an execution layer as functional presentation layers for progressive disclosure. The names and functions of these layers are specific to ALPS and are not PF constructs.

A Skill Description claiming Description Conformance must provide both layers and make their functions distinguishable. The layers may be represented together or separately, provided that one authoritative Skill Description remains identifiable and mandatory references are resolvable.

a) The **discovery layer** must present the Name and Skill Discovery Description. The Skill Discovery Description must state what the Skill does, when it is used, and the information needed to determine applicability.

b) The **execution layer** must present or provide access to the complete Skill Description used for execution and Assessment. It includes Name, Purpose, and Outcomes, together with any optional elements and reference information included under 6.1.

c) Matters that cut across multiple Skills should be treated separately from an individual Skill's execution layer. Common Controls and Enablers may be declared as Framework-level elements.

NOTE: These functional layers support progressive disclosure without requiring two files, two sections, or another particular physical structure.

### 5.6 Process Models and Life Cycle Models

Process Models and life cycle models are interpreted with the meanings established by the PF. When Processes in a Process Model are made available as Skills, the Model may identify the Skill Package that supplies each authoritative Process Description and the relationships among the Processes.

A subset of Processes can be selected from a Process Model according to Purpose. The Skills that describe the selected Processes can then be applied singly or in combination. Selection and timing need continual review when the subject or context of application changes (PF 5.1 and 5.2).

### 5.7 Skill Packages and Accompanying Resources

A Skill Package must contain one authoritative Skill Description.

A Skill Package may include, as needed, reference information, execution resources, and deliverable resources that support understanding or executing the Skill or creating its Outputs. When accompanying resources are included, their roles and conditions of use must be identifiable from the Skill Description. Mandatory references must be resolvable.

Unnecessary duplication or conflict must not arise between a Skill Description and accompanying resources. Accompanying resources must be treated as reference information, Inputs, Outputs, Controls, Constraints, or Enablers based on the function they perform in Skill execution, not on where they are stored (9.1).

A Skill Package should contain only resources that directly support understanding or executing the Skill or creating its Outputs.

### 5.8 Specialization of the Process Framework

ALPS specializes the general constructs of the PF for Agent Skills. The normative source for each general concept remains the PF; this specification does not restate general definitions and adds only what is specific to Agent Skills.

| PF construct | ALPS specialization |
|---|---|
| Process Description | Skill Description (3.3) |
| Resources that perform or support a Process | Agents, models, tools, and execution environments, treated as Enablers (5.2, 9.3) |

ALPS may make a PF rule concrete for the Agent context and may strengthen it where needed. ALPS must not change the meaning of a PF concept, weaken a PF requirement, or replace a PF concept with a different one (see Clause 2).

## 6. Requirements for Skill Descriptions

### 6.1 Composition of Elements

A Skill Description must contain Name, Purpose, and Outcomes (PF 1.2).

Activities, Tasks, Inputs, Outputs, Controls, Constraints, Enablers, Entry Criteria, Exit Criteria, and reference information are optional elements added according to the Purpose of the description and the required level of detail. A Decision Gate is not a component of a Skill Description; it is treated as a decision mechanism that controls application of the Skill (PF 1.2 and 8.1, Clause 10).

### 6.2 General Writing Rules

a) The roles of Name, Purpose, Outcomes, Activities, and Tasks must be distinguished, and consistency among them must be maintained (PF 1.4).

b) Each sentence should address only one meaning, and independent objectives, results, or actions should not be joined in one sentence. Each statement should contain enough context to remain meaningful when referenced independently within its Skill Description. When supplementary explanation is needed, it can be separated as a reference statement or note rather than superimposing meaning on the primary statement.

c) A general Skill must not require a specific method, technique, tool, metric, management method, or execution sequence. Any necessary temporal relationship should be stated explicitly as a Constraint.

d) Activities and Tasks must not be interpreted as procedural steps (PF 1.4).

e) The normative attribute of a statement must be distinguishable through the normative language in 4.1.

NOTE: Rule d) also protects against an Agent misreading the listed order of Activities and Tasks as a prescribed sequence of steps.

### 6.3 Writing Rules for Individual Elements

#### 6.3.1 Name

A Skill Name must use a concise noun phrase as the Skill heading. The Name states the Process's central concern and differentiates it from other Processes represented in the applicable Process Model. The Name must not be written as a summary of the Purpose (PF 2.1).

#### 6.3.2 Purpose

A Skill Purpose must state one or more high-level objectives that belong together. The Purpose should be stated concisely in one sentence wherever possible. Summarizing Activities or Outcomes in the Purpose should be avoided. Combining multiple independent Purposes in one sentence should also be avoided. If further explanation is needed, it can be placed in a reference statement or note. When Skill scopes appear to overlap, the Purpose should characterize the scope or boundary of the Skill (PF 2.1).

#### 6.3.3 Outcome

A Skill Outcome represents a measurable and tangible result achieved by the Skill. An Outcome must be observable and assessable and must be clearly distinguished from an Output. The creation of a document, record, or information item itself must not be written as an Outcome (PF 2.2).

An Outcome must be written as a declarative statement of a condition in which a positive and observable result is established. Each Outcome must describe only one result, and joining multiple independent results with conjunctions must be avoided. An Outcome of a general Skill must be meaningful in every applicable scope.

Taken together, the Outcomes must fully support attainment of the Skill Purpose, and no listed Outcome must be irrelevant to that attainment. Each Outcome should remain meaningful when read independently. Singularity and clarity of meaning take precedence over brevity, and the size of the Outcome set follows from what attainment of the Purpose needs. Benefits of a Skill should be distinguished from Outcomes and, when useful, explained separately in a non-normative note attached to the Purpose.

#### 6.3.4 Activity

An Activity describes a set of actions for achieving or performing a Skill and functions as an organizing construct for classifying related Tasks. An Activity should contain Tasks that are strongly related to one another and weakly related to Tasks belonging to other Activities or Skills.

The Activities and any separated Skills must collectively cover all Outcomes and satisfy the Skill Purpose. Activities need not map individually to Outcomes (PF 2.3).

#### 6.3.5 Task

A Task must have the primary function of expressing an individual action that supports achievement of one or more Outcomes and must be written so that the object and operation of that action are distinguishable. A statement whose primary function is not an individual action must not be treated as a Task and must be placed in the element corresponding to that function. Each Task must be assigned a normative attribute, and the normative language in 4.1 must make clear whether the action is a requirement, recommendation, permissible action, or typical action. Tasks assigned to an Activity need not exhaust every action within that Activity's boundary. The rules in 6.2 c) and d) apply to both Activities and Tasks.

#### 6.3.6 Input and Output

Inputs and Outputs represent connections between a Skill and its external environment. It is optional whether mandatory or representative Inputs are specified, and it is also optional whether Outputs are specified when achievement of the Outcomes can be demonstrated (PF 4.1 and 4.2). An Output can be expressed as an artifact or information item. An Output of one Skill can become an Input to another Skill or Process.

When the Output of one Skill is used as an Input to another Skill or Process, their names, meanings, and scopes should be aligned. The level of detail used to describe the relationship should be determined according to the Purpose of the Skill Description, dependencies among Skills, and quality risk.

Representative Inputs and Outputs do not prescribe the only manner of execution. A Skill should be understood from the entire Skill Description (PF 4.2).

#### 6.3.7 Control, Constraint, Enabler, Entry Criteria, and Exit Criteria

Controls and Constraints declare conditions that direct or limit Skill execution. Enablers make Skill execution possible or assist it. Entry Criteria state conditions under which a Skill can be invoked; Exit Criteria state conditions under which a Process Instance can be completed. These elements are used according to the Purpose of the description and the required level of detail. Details are given in Clauses 9 and 10.

The primary function of a Control or Constraint statement must be to declare a condition that directs or limits execution. A statement whose primary function is an individual action must be classified as a Task.

When a summary of Entry Criteria is placed in the discovery layer, it must not conflict with the Entry Criteria available through the execution layer.

#### 6.3.8 Reference Information

Overviews, descriptions, Common Approach, practical tips, notes, and examples are used as reference information to support understanding or application of a Skill. Reference information must not alter the meaning or normative force of primary Skill elements (PF 1.4).

As reference information placed in the ALPS-specific discovery layer, a Skill Discovery Description must state concisely what the Skill does, when it is used, and the information needed to determine applicability. It must be consistent with the authoritative Name, Purpose, Outcomes, scope, Entry Criteria, and Constraints available through the execution layer and must not replace those elements or alter their normative meanings.

The Skill Discovery Description of a Skill claiming Description Conformance to this specification must end with a short ALPS conformance marker in the language of the description. The marker must be exactly `ALPS-conformant.` in English and `ALPS準拠。` in Japanese. This marker is a standardized shorthand claim whose subject is the containing Skill Description and whose criteria are Description Conformance under 12.1 a); it does not assert Reference Model Conformance or Execution Conformance.

## 7. Skill Life Cycle and ALPS Reference Model

### 7.1 Skill Life Cycle Model

A Skill life cycle model is a Framework of Skill-related Processes and Activities and serves as a common frame of reference for communication and understanding (PF 5.2). This specification establishes a reference life cycle model comprising the following Stages:

a) **Concept Stage** — Needs for treatment as Skills are identified and selected.

b) **Definition Stage** — Skill Descriptions are designed and verified.

c) **Operation Stage** — Skills are selected, invoked, executed, and orchestrated with other Skills.

d) **Evolution Stage** — Skills are assessed, tailored, and improved.

e) **Retirement Stage** — Skills that have become unnecessary or unsuitable are withdrawn from use.

The order shown does not prescribe execution order. Processes and Activities can span multiple Stages and can be applied iteratively, recursively, or concurrently (PF 5.2, Clause 8).

### 7.2 Composition and Interpretation of the Reference Model

The ALPS Reference Model comprises the following three Processes. Each Process is defined by its Purpose and Outcomes and comprises three Activities (PF 1.1 and 5.1).

| Process | Activities |
|---|---|
| ALPS definition process | Skill Need Identification / Skill Design / Skill Verification |
| ALPS application process | Skill Selection / Skill Execution / Skill Orchestration |
| ALPS management process | Skill Asset Management / Skill Tailoring / Skill Assessment and Improvement |

Interpret the Reference Model as follows:

a) The three Processes are general Processes and do not require a particular method, tool, or execution sequence (6.2 c)).

b) The order in which Activities and Tasks are presented does not prescribe their execution order. The normative attribute of each Task is expressed through the normative language in 4.1.

c) Representative Inputs/Outputs do not prescribe the only method, and exchanges between Activities do not alter Process boundaries (PF 4.2).

d) When Conformance to Outcomes is selected, Activities and Tasks are treated as guidance. When Conformance to Tasks is selected, Outcomes are treated as guidance (see 12.2).

e) Subsets of Processes, Activities, and Tasks can be selected according to Purpose. Changes to Activities or Tasks are handled as Tailoring when necessary (PF 3.2 and 5.1, Clause 11).

Representative exchanges among the three Processes are shown below. This table does not prescribe a fixed execution sequence.

| Provider Process | Representative exchange item | Recipient Process |
|---|---|---|
| ALPS definition process | Verified Skill Description and verification results | ALPS management process |
| ALPS management process | Information about managed Skills, Tailoring decisions, and conditions of application | ALPS application process |
| ALPS application process | Execution and decision records, lessons learned, and measurable results | ALPS management process |
| ALPS management process | Change requests, redefinition requests, and reverification requests | ALPS definition process |

### 7.3 ALPS Definition Process

**Purpose**: This Process establishes an assessable and usable Skill Description that satisfies identified stakeholder needs.

**Outcomes**: Success of this Process establishes the following conditions:

a) The need to be addressed as a Skill and the intended contexts of use are identified.

b) The Skill Purpose, Outcomes, and boundary are aligned with the selected need.

c) The Skill Description satisfies the applicable description requirements of this specification.

d) Elements within the Skill Description and exchanges with external parties are traceable.

e) The achievability of the Outcomes in representative contexts of use is confirmed.

f) A decision on Skill adoption can be made from evidence that includes defects and limitations.

| Activity | Outcomes primarily supported |
|---|---|
| Skill Need Identification | a), b) |
| Skill Design | b), c), d) |
| Skill Verification | c), d), e), f) |

**Activities and Tasks**:

#### 7.3.1 Skill Need Identification

This Activity explores candidates for treatment as Skills and selects the need to be defined.

a) Opportunities for Skills are typically collected from recurring Tasks, lessons learned, and failure cases.

b) The expectations of intended users and stakeholders must be identified.

c) Existing Skill assets should be investigated to identify duplication, adjacency, or gaps.

d) Expected benefits, risks, and costs should be evaluated for each candidate.

e) The rationale for selection and deferral should be recorded.

f) Candidates may be prioritized by frequency of use or impact when selecting a need.

#### 7.3.2 Skill Design

This Activity determines the structure and content of a Skill Description that satisfies the selected need.

a) The Skill boundary must be established from the primary Outputs and Outcomes (5.4).

b) Dependencies on other Skills must be reduced as far as practicable.

c) The Skill Description must provide distinguishable discovery-layer and execution-layer information. Their physical separation is not required (5.5).

d) A significant Activity that benefits from detailed treatment may be separated into another Skill.

e) Name, Purpose, and Outcomes must be written in accordance with 6.3.1 through 6.3.3.

f) Each Task must have the primary function of expressing an individual action that supports achievement of one or more Outcomes and must be written so that the object and operation of that action are distinguishable (6.3.5).

g) Each statement must be classified under the Skill element corresponding to its primary function (6.2 a), 6.3).

h) Each Task must be assigned a normative attribute (6.3.5).

i) Guidance on how to apply the Skill should be separated as Common Approach and practical tips.

j) It must be confirmed that the set of Activities covers all Outcomes and satisfies the Purpose (6.3.4).

k) Relationships between Tasks and Outcomes should be identified (8.2).

l) The Skill Discovery Description must be written in accordance with 3.11, 5.5, and 6.3.8.

m) When representative Inputs and Outputs are shown, the principal relationships with other Skills or Processes should be identified as needed (6.3.6, 8.2).

n) When a Skill Package is composed, the need, role, and conditions of use for its accompanying resources must be identified (5.7).

#### 7.3.3 Skill Verification

This Activity confirms the descriptive conformance of the Skill Description and the achievability of the intended Outcomes.

a) The Skill Description must be reviewed using agreed criteria (Clause 10).

b) It must be confirmed that each Task has the primary function of expressing an individual action that supports achievement of one or more Outcomes and that the object and operation of that action are distinguishable (6.3.5, 8.2).

c) It must be confirmed that the element classification of each statement is consistent with its primary function, including the distinction between conditions declared by Controls and Constraints and individual actions expressed by Tasks (6.2 a), 6.3.5, 6.3.7, 9.2).

d) It must be confirmed that normative attributes are distinguishable (4.1).

e) When a general Skill is verified, it must be confirmed that its normative part does not require a specific method, technique, tool, or execution sequence (6.2 c)).

f) It must be confirmed that the discovery-layer and execution-layer information are consistent (5.5, 6.3.8).

g) The review should incorporate a perspective independent of the Skill author.

h) The achievability of the Outcomes should be evaluated through trials in representative contexts of use.

i) It should be evaluated whether applicability can be determined from discovery-layer information alone, including the Skill Discovery Description.

j) Boundary cases from the intended contexts of use may be included in the evaluation.

k) Detected defects should be recorded, and actions with due dates and completion conditions should be established (PF 8.2).

l) Completion of defect treatment should be confirmed before the Decision Gate for the adoption decision.

m) When the Skill Description identifies an exchange with another Skill or Process, it should be evaluated whether the Output can be used as the intended recipient's Input.

n) When the Skill Package is included in the verification scope, the existence of the authoritative Skill Description, resolvability of mandatory references, roles and conditions of use of accompanying resources, and consistency between the Skill Description and those resources must be evaluated (5.7).

**Representative Inputs**: Stakeholder expectations, lessons learned, information about execution performance, applicable Controls and Constraints, information about existing Skill assets, verification criteria, and representative contexts of use.

**Representative Outputs**: The selected Skill need and selection rationale, verified Skill Description, record of mappings among elements, verification results, and record of defect treatment.

NOTE: Appendix D gives reference guidance on evidence for Skills whose behavior is not deterministic.

### 7.4 ALPS Application Process

**Purpose**: This Process achieves intended Outcomes by applying, individually or in combination, Skills suited to the context of application.

**Outcomes**: When this Process succeeds, the following conditions are established:

a) The needs and conditions of the context of application are identified.

b) The Skills to apply and the form of application are determined with rationale.

c) Applicable Controls, Constraints, and Tailoring decisions are identified.

d) The results of applying a Process Instance conform to the declared scope, applicable Controls and Constraints, and Tailoring decisions.

e) The declared Outcomes of the Skills subject to application are achieved.

f) Necessary exchanges among Skills are established.

g) Completeness and consistency of the Skill composition are established.

| Activity | Outcomes primarily supported |
|---|---|
| Skill Selection | a), b), c) |
| Skill Execution | c), d), e) |
| Skill Orchestration | e), f), g) |

NOTE: A decision to apply no Skill can also be a legitimate judgment for the context of application. When this decision makes some Outcomes of this Process inapplicable, Full Conformance to this Process must not be claimed. The inapplicable Outcomes must be declared, and Tailored Conformance under 12.3 must be used.

**Activities and Tasks**:

#### 7.4.1 Skill Selection

This Activity determines the Skills to use for the context of application and their form of application.

a) The needs and conditions of the context of application and applicable Constraints must be identified.

b) The needs are typically compared with Skill Purposes and Outcomes.

c) Candidate Skills are typically identified from discovery-layer information, including Skill Discovery Descriptions.

d) When candidates overlap, their scopes should be distinguished by their Purposes (6.3.2).

e) When no suitable candidate exists, the need may be transferred to Skill Need Identification in the ALPS definition process.

f) It must be determined whether the uncertainty and risk associated with the application decision are acceptable (Clause 10).

g) The rationale for the decision should be recorded.

#### 7.4.2 Skill Execution

This Activity uses a selected Skill to execute a Process Instance and achieve the Process Outcomes declared by the Skill.

a) A Skill must be invoked only after determining that its Entry Criteria are satisfied. If they are not satisfied, invocation must be deferred or resolution of the deficiency must precede it.

b) Availability of necessary Inputs and Enablers should be confirmed.

c) Applicable Controls, Constraints, and Tailoring decisions must be identified.

d) Activities and Tasks in the Skill Description must be performed in accordance with their assigned normative attributes. A required Task must not be omitted unless legitimately changed through Tailoring (Clause 11).

e) Execution may proceed without assuming a particular sequence unless one is stated as a Constraint (6.2 c)).

f) Iteration should continue until problems arising during execution are resolved (8.1).

g) A Decision Gate should be applied before an irreversible or high-impact action (10.2).

h) Completion must be determined against the Exit Criteria.

i) Achievement of the Outcomes should be determined from observable evidence.

j) Outputs should be transferred to recipients in accordance with the exchange definition (8.2). When quality conditions applicable to the transfer have been established, their satisfaction should be confirmed.

k) Significant execution decisions, their rationale, and assumptions should be recorded and placed under necessary change management (PF 8.1).

l) Lessons learned through execution may be transferred to Skill Assessment and Improvement in the ALPS management process.

#### 7.4.3 Skill Orchestration

This Activity combines multiple Skills and manages their interfaces, exchanges, and the completeness and consistency of the composition as a whole.

a) The target set of Outcomes must be identified.

b) The source of each Skill used in the composition should be identified (8.3).

c) A repeatedly used composition may be documented as a Process View (8.3).

d) The mapping between each provider Output and recipient Input must be made explicit (8.2).

e) An exchange not defined in advance may be added through Tailoring (PF 4.4).

f) When an Output changes through Iteration or Recursion, affected Inputs should be identified and their integrity and applicable criteria reevaluated (PF 6.2).

g) Integration must ensure completeness within a level and consistency across levels (8.1).

h) Achievement of Outcomes for the composition as a whole should be determined.

i) When the same information item is changed by multiple Skills, handling of its integrity, status, and change must be established according to quality risk (8.2).

**Representative Inputs**: Needs of the context of application, invocation requests, Skill discovery layers and Skill Descriptions, the target set of Outcomes, Inputs specified by Skill Descriptions, Framework-level declarations, and Tailoring decisions.

**Representative Outputs**: Decisions on applied Skills and forms of application, Outputs specified by Skill Descriptions, definitions of Skill compositions, Outputs of the compositions as a whole, and execution and decision records.

**Representative Enablers**: Managed Skill assets, Agent capabilities, necessary tools, and execution environments.

NOTE: Records of human approval, intervention, and oversight can form part of the execution and decision records exchanged with the ALPS management process. Appendix D lists representative items.

### 7.5 ALPS Management Process

**Purpose**: This Process governs Skill assets and their application and maintains the continual availability of suitable Skills.

**Outcomes**: A successful application of this Process establishes the following conditions:

a) Policies and guidance for Skill management, deployment, and Tailoring are established.

b) Adopted Skills are discoverable in a managed state.

c) Changes to and retirement of Skills are controlled, including their impacts on affected users.

d) Tailoring decisions and rationale are traceable to applicable Controls and Constraints.

e) Skill performance and effectiveness are assessed against established criteria.

f) Improvement opportunities are prioritized from lessons learned and assessment results.

g) Decided improvements are implemented.

| Activity | Outcomes primarily supported |
|---|---|
| Skill Asset Management | a), b), c), g) |
| Skill Tailoring | a), d) |
| Skill Assessment and Improvement | e), f), g) |

**Activities and Tasks**:

#### 7.5.1 Skill Asset Management

This Activity manages adoption, discoverability, change communication, configuration, and retirement of Skill assets.

a) The means for managing and deploying Skills, together with Tailoring guidance, should be established (PF 9.1).

b) Framework-level Controls and Enablers must be declared together with their scope, exceptions, and whether Tailoring is permitted (9.1).

c) Evidence from Skill Verification in the ALPS definition process should be confirmed before a Skill is adopted.

d) When management guidance or a Skill changes, the change should be communicated to affected users (PF 9.1).

e) A Skill for which the need no longer exists or that has become harmful must be identified and retired.

f) The description of a retired Skill may be retained for reference.

g) Duplication and gaps within the Process Model should be continually identified.

h) Skills established as standards should be used consistently across multiple subjects of application (PF 9.2).

i) When a component of a Skill Package changes, affected Skill Descriptions and accompanying resources should be identified and necessary reverification performed.

#### 7.5.2 Skill Tailoring

This Activity adapts Skills and Process Models to the needs, conditions, and risks of a particular context of application.

a) Application-related risks, requirements, complexity, available capabilities and resources, and relevant standards must be identified (PF 7.3).

b) Candidate Skills or life cycle models must be evaluated by considering conditions of application, available expertise and experience, stakeholder expectations or requirements, and risk tolerance (PF 7.3).

c) Tailoring decisions should be based on facts and evidence (PF 7.3).

d) Outcomes, Activities, Tasks, representative Inputs, and representative Outputs may be deleted, modified, or added (PF 7.2).

e) Tailoring must comply with applicable Controls and Constraints (PF 7.3).

f) Input must be obtained from affected parties (PF 7.3).

g) The rigor of Skill application should be set on the basis of risk so that Activities can be performed with sufficient rigor at an acceptable level of risk (PF 7.1).

h) The scope of Tailoring should be made clear. Assumptions and criteria should be identified, and the rationale for decisions should be recorded (PF 7.3).

i) Tailoring is typically performed dynamically throughout the period of application according to risk and context (PF 7.1).

j) Tailoring operation should be reviewed throughout application and revised when conditions warrant.

k) A means of continually assessing the performance of the tailored Skill should be established (PF 7.3).

l) The level of detail used to describe Inputs, Outputs, and their exchanges should be adjusted according to dependencies among Skills, concurrent or iterative application, and quality risk.

#### 7.5.3 Skill Assessment and Improvement

This Activity assesses Skill performance and effectiveness and connects the results to improvement.

a) Measures should be established to gain insight into Skill performance and effectiveness (PF 9.3).

b) Lessons learned should be identified and collected throughout the period of Skill execution.

c) Collection of lessons learned at predefined milestones should also be planned (PF 9.3).

d) Measures should be analyzed to determine Skill effectiveness (PF 9.3).

e) Skill strengths and weaknesses should be assessed, and reviews and audits should be established (Clause 10).

f) Skill performance may be compared with established criteria, applicable standards, or comparators to identify improvement opportunities. The comparison should analyze performance, effectiveness, conformance, benefits, and costs (PF 9.2).

g) Improvement opportunities should be continually identified, prioritized, and implemented (PF 9.1).

h) Mechanisms should be established both to collect lessons learned and connect them to action and to analyze candidate changes for improvement (PF 9.3).

i) A changed Skill should undergo confirmation through Skill Verification in the ALPS definition process.

j) Inconsistency and rework arising from exchanges among Skills may be used to identify improvement opportunities.

**Representative Inputs**: Verified Skill Descriptions, change requests, contexts of application, Tailoring guidance, Input from affected parties, execution and decision records, lessons learned, and measurement results.

**Representative Outputs**: Managed Skill assets, tailored Skills, Tailoring decisions and rationale, assessment results, prioritized improvement opportunities, change requests for Skills, and retirement decisions.

## 8. Skill Execution Structures and Relationships

### 8.1 Concurrency, Iteration, Recursion, and Integration

Skills can be executed in structures other than a serial sequence. The following execution structures can be applied (PF 6.1):

a) **Concurrency** — Applying two or more Skills in parallel at the same structural level.

b) **Iteration** — Repeatedly applying the same Skill or set of Skills at the same level. It should continue as far as needed to resolve problems and refine Outputs.

c) **Recursion** — Repeatedly applying the same Skill or set of Skills at successive structural levels of the subject of application. The Output of a Skill applied at one structural level can become an Input to a Skill applied at the next structural level.

d) **Integration** — Ensuring completeness within a level and consistency across levels.

These relationships do not prescribe execution order. The actual flow is determined through Tailoring, with consideration for the effects of Output changes on Inputs to other Skills (PF 6.2).

### 8.2 Interfaces, Exchanges, and Traceability Among Skills

An interface and exchange between Skills is treated as a mapping from a provider's Output to a recipient's Input. An interface is not an independent Skill element, and an undefined exchange can be added through Tailoring (PF 4.4).

When multiple Skills are composed for application, the mapping from each provider Output to each recipient Input must be made explicit (7.4.3 d)).

When Skills are applied concurrently, iteratively, or recursively, shared or interdependent information items and the reference or change relationships among them should be identified to the extent needed for application. When the same information item is changed by multiple Skills, handling of its integrity, status, and change must be established according to quality risk.

When a change to an Output affects an Input to another Skill, the affected Skill and mapping should be identified and necessary reassessment performed.

When Output quality affects a subsequent Outcome or stakeholder acceptance, the determination conditions and necessary evidence should be related to Entry Criteria, Exit Criteria, a review, or a Decision Gate.

Traceability should cover Outcomes, Activities, Tasks, and information items. These mappings provide a basis for integrity and Process Assessment (PF 4.4).

NOTE: Explicit exchange mappings keep the meaning, scope, state, and quality conditions of an information item from being lost as it passes between Skills.

### 8.3 Process View

A Process View organizes Activities and Tasks spanning multiple Skills around a particular concern or Purpose (PF 5.3).

When an independent Process boundary is established, the subject can be described as a separate Skill in accordance with 5.4.

a) Every Process View must state its Name, Purpose, and Outcomes.

b) To achieve the Outcomes, a Process View may include Activities and Tasks selected from an existing Process Model, adapted Activities and Tasks, or Activities and Tasks specific to the Process View.

c) A Process View must include explanations and guidance for applying those Activities and Tasks.

d) A Process View must explicitly identify the source of each Activity and Task and whether it is selected, adapted, or new. Elements selected from an existing Process Model must retain their source.

e) Adapted elements and elements specific to the Process View are not treated as changes to the original Process Model. Unless Tailoring or formal adoption into the Process Model occurs, these elements do not count toward Conformance to the original Skill.

f) Operation of a particular Process Model may adopt a restricted Process View that uses only Activities and Tasks from existing Skills. Under this approach, Activities and Tasks specific to the Process View must not be included.

g) A Process View may show connections among Skills and the sources of the Skills used in its composition.

## 9. Controls, Constraints, and Enablers

### 9.1 Framework-Level Controls and Enablers

Framework-level Controls and Enablers must state their scope, exceptions, and whether Tailoring is permitted (PF 4.5).

Elements common to Skills within the declared scope may be declared once rather than repeated in each Skill (PF 4.1 and 4.5).

Information resources that apply in common to multiple Skills can be declared as Framework-level Controls or Enablers according to their function. An item transformed by a Skill is treated as an Input or Output. These classifications must be based on the function performed by the information resource in Skill execution, not on its form or location.

### 9.2 Skill-Level Controls and Constraints

Controls and Constraints declare conditions or permissible boundaries for Skill execution. Controls can arise from applicable laws or regulatory requirements, policies, conformance to voluntary standards, or agreements. Constraints can arise from environmental factors or conditions of application external to the Skill (PF 4.1 and 4.5).

A Control or Constraint statement must be classified according to its primary function as specified in 6.3.7.

Controls and Constraints can be described in separate sections of a Skill Description or as conditions associated with other Skill elements. Any temporal relationship needed in a general Skill should be declared explicitly as a Constraint (6.2 c)).

### 9.3 Enablers, Capabilities, and Tools

Human or Agent capabilities, tools, and technologies support a Skill as Enablers (PF 4.1 and 4.5).

Human and automated resources that execute a Skill, including Agents, models, execution environments, and tools, are not treated as Process Inputs (PF 4.1 and 4.2). When described as elements, they must be described as Enablers.

NOTE: Treating Agents, models, tools, and execution environments as Enablers keeps the items a Skill transforms distinct from the capability that performs the transformation.

## 10. Entry/Exit Criteria, Decision Gates, and Reviews

### 10.1 Entry Criteria and Exit Criteria

a) Entry Criteria state conditions under which a Skill can be invoked. A summary should be placed in the discovery layer as reference information for determining applicability (5.5).

b) Exit Criteria state conditions under which a Process Instance can be completed. Exit Criteria should be related to determining achievement of the Outcomes.

### 10.2 Decision Gate

A Decision Gate is not a component of a Skill Description; it is treated as a decision mechanism that controls application of the Skill (PF 8.1).

a) A Decision Gate uses Decision Criteria based on the Purpose, Outcomes, conditions of application, and risk to determine whether a state transition can occur (PF 8.1).

b) The frequency, scope, and formality of Decision Gates can be adjusted to the context of application.

c) The decision, its rationale, and its assumptions should be recorded (PF 8.1).

d) A decision to pass should be based on evidence, and Decision Criteria should be reevaluated as the context of application changes.

NOTE: Confirmation and human escalation before an irreversible or high-impact action are forms of applying a Decision Gate. The Gate gives the application a controlled point at which such an external effect can be held, changed, or stopped before it occurs. Appendix D describes how human oversight can be composed from existing elements.

### 10.3 Reviews and Audits

A review evaluates Skill performance, Outputs, and achievement of Outcomes using agreed criteria. An audit includes a detailed review of evidence demonstrating conformance to the Skill, Outputs, and requirements and confirms that mandatory attributes and applicable requirements are satisfied (PF 8.2).

When an Output is transferred to another Skill or a stakeholder, it should be evaluated against applicable criteria to determine whether the Output can be used as the intended Input or result.

Reviews and audits should be tailored to the needs and risks of the subject of application, and their Entry Criteria, Exit Criteria, and responses to problems should be established (PF 8.2).

## 11. Tailoring and Process Instantiation

### 11.1 Discipline of Tailoring

Tailoring must be performed in accordance with Skill Tailoring in the ALPS management process (7.5.2), whose requirements are prerequisites for Tailored Conformance (12.3).

NOTE: Requiring Tailoring to pass through the ALPS management process prevents unrecorded changes to a Skill's meaning, normative force, or applicability.

### 11.2 Levels of Tailoring

Common-level Tailoring adapts an external standard, including this specification, to needs shared across an intended application domain. Individual-level Tailoring adapts the resulting common Skill to the needs of a particular subject of application (PF 7.2).

### 11.3 Process Instantiation

When justified by quality risk, a Process Instance can be described in greater detail, and instance-specific success criteria, Activities, and Tasks can be identified (PF 7.4).

## 12. Conformance, Capability, and Assessment

### 12.1 Subjects of Conformance

Conformance relating to this specification can be claimed for the following subjects. Every claim must identify the subject and the selected criteria.

a) **Description Conformance** — A Skill Description satisfies the applicable requirements of Clauses 4 through 6. When a Skill Package is included in the subject of conformance, the Package also satisfies the applicable requirements of 5.7.

b) **Reference Model Conformance** — For definition, application, or management of Skills, Conformance under 12.2 or 12.3 is established for the declared Process among the three Processes in Clause 7.

c) **Execution Conformance** — Execution of a Process Instance through a Skill establishes Conformance under 12.2 or 12.3 to the Process described by that Skill.

### 12.2 Full Conformance

Full Conformance must be claimed as Conformance to Outcomes, Tasks, or both, and the selected criteria must be stated. When both are selected, both must be satisfied (PF 8.3).


a) **Full Conformance to Outcomes** requires achievement of all mandatory Outcomes in the declared Skill or Reference Model Process. This approach provides greater freedom in how the conformant Process is implemented; Activities and Tasks are treated as guidance.

b) **Full Conformance to Tasks** requires satisfaction of every requirement stated with **must** or **must not** by an Activity or Task in the declared Skill or Reference Model Process. Recommendations, permissible actions, and typical actions are not, solely by virtue of those attributes, mandatory conditions for Full Conformance to Tasks. When this approach is selected, Outcomes are treated as guidance.


For Conformance to the Reference Model, the units for which Outcome Conformance to a Process can be claimed are the ALPS definition process, ALPS application process, and ALPS management process. Independent Outcome Conformance must not be claimed for an individual constituent Activity.

### 12.3 Tailored Conformance

Tailored Conformance may be claimed for a Skill or Reference Model Process that does not meet Full Conformance. The claim must declare the Skill or Process tailored in accordance with Skill Tailoring in the ALPS management process (7.5.2) and its scope of application. It must also demonstrate satisfaction of every Outcome and Activity/Task requirement remaining within that scope (PF 8.3 and 8.4).

When only some Activities constituting a Reference Model Process are applied, the application must not be claimed as independent Process Conformance to those Activities. It must be declared as a tailored scope of the parent Process, and the Tailored Conformance criteria must be used.

### 12.4 Capability and Assessment

Capability is treated as a dimension of assessment separate from Conformance. Specifically performing Activities and Tasks can require a higher Capability level than achieving Outcomes alone. However, Capability level alone does not establish Conformance, nor does Conformance alone determine Capability level (PF 8.5).

Skill Outcomes and the Purposes and Outcomes of the three Processes can be used for Process Assessment and effectiveness assessment (PF 8.5, 7.5.3).

Assessment of a Skill Package can evaluate the existence of the authoritative Skill Description, resolvability of mandatory references, consistency between the Skill Description and accompanying resources, roles and conditions of use of accompanying resources, and reverification after changes (5.7, 7.3.3, 7.5.1).

---

## Appendix A (informative) Examples of a Skill Description and Skill Package

### A.1 Status of This Appendix

This appendix is an informative example and does not require a particular form (1.2).

### A.2 Description Example: Meeting Minutes Consolidation Skill `SKILL.md`

The following `SKILL.md` example uses `name` as an identifier corresponding to the Skill Name and `description` as the Skill Discovery Description.

```markdown
---
name: consolidate-meeting-minutes
description: Extract decisions, action items, and open issues from meeting notes, transcripts, and distributed materials, then produce minutes that preserve traceability to the source record. Use when asked to organize meeting records, produce meeting minutes, or organize post-meeting actions. ALPS-conformant.
---

# Meeting Minutes Consolidation Skill

## Purpose

This Skill establishes a state in which decisions, action items, and open issues can be distinguished from the meeting record.

## Outcomes

When this Skill succeeds, the following conditions are established:

a) Decisions made in the meeting are identified.

b) Action items and their due dates are identified.

c) Open issues are identified.

d) Mappings between the consolidated content and the source record are traceable.

## Entry Criteria

- A meeting record is available.
- The scope of consolidation is stated.

## Exit Criteria

- Achievement of every Outcome has been determined.
- The Output has been transferred to the recipient.

## Representative Inputs

Meeting records, including notes, transcripts, and distributed materials.

## Representative Outputs

Consolidated meeting minutes.

## Activities and Tasks

The order shown below does not prescribe execution order.

### Record Understanding

- The scope of consolidation and gaps in the records must be identified.
- Unclear statements must not be completed by conjecture.
- Applicable policies for handling confidential information must be applied.
- The list of participants and agenda items is typically confirmed.

### Item Extraction

- Decisions, action items, and open issues must be distinguished and identified.
- A decision not present in the source records must not be included in the Output.
- Each action item should be associated with a due date.
- Items may be assigned a priority classification.

### Establishment of Verifiability

- Mappings between extracted items and the source records must be maintained.
- The Output must be transferred only after mappings between extracted items and the source records have been established.
- Items that cannot be confirmed from the source records should be marked as requiring confirmation.

## Constraints

- The Output is limited to decisions, action items, and open issues supported by the source records.
- Transfer is permitted only after mappings between extracted items and the source records have been established.

## Controls

- Applicable policies for handling confidential information.

## Enablers

- Transcription support tools
- Domain glossary
- Natural-language-processing capability of the performer

## Common Approach and Practical Tips

This section is reference information and has no normative force.

- Decisions often appear near expressions of agreement or approval.
- For a lengthy record, progressive refinement can use Iteration by agenda item.
```

NOTE 1: `description` states what the Skill does and when it is used, making that information available before Skill selection (3.11).

NOTE 2: “Consolidated meeting minutes” is an Output, not an Outcome (6.3.3). The Constraint declares the permitted transfer condition, while the corresponding transfer action is stated as a Task (6.3.7, 9.2). Enablers are not Inputs (9.3), and this Skill does not prescribe a performer (5.3).

### A.3 Example Composition of a File-Based Skill Package

The following is an informative example of applying 5.7 through a file-based Environment Binding. This composition and these names are not requirements (1.2). Storage groupings other than `SKILL.md` are optional and are established only when necessary accompanying resources exist. The authoritative Skill Description remains the semantic source for both discovery-layer and execution-layer information; an Environment Binding may project discovery information into frontmatter or a separate registration record without changing its meaning or normative force.

```text
<skill-name>/
├── SKILL.md
├── references/
│   └── <reference>.md
├── scripts/
└── assets/
```

| Component | ALPS treatment |
|---|---|
| `SKILL.md` | Authoritative Skill Description for the Skill. In this representative Environment Binding, frontmatter projects discovery-layer information and the body provides execution-layer information; ALPS does not require this physical arrangement. |
| `references/` | Reference information loaded as needed. Individual filenames are not prescribed. |
| `scripts/` | Execution resources that support reproducibility or reliability. They are typically treated as Enablers. |
| `assets/` | Resources used to create Outputs. They are treated as Inputs, Outputs, or Enablers according to function. |

## Appendix B (informative) Correspondence with the Process Framework

| PF clause | Subject | Corresponding clause in this specification |
|---|---|---|
| 1.1 | Process, Process Description, and Process Instance | 5.1, 5.8 |
| 1.2–1.3 | Required elements, optional detail, and the two-part form | 3.11, 5.1, 5.5, 6.1 |
| 1.4 | Description and interpretation rules | 4.1, 6.2, 6.3.8 |
| 2.1–2.3 | Name, Purpose, Outcome, Output, Activity, and Task | 6.3.1–6.3.6 |
| 3.1 | Boundary, granularity, and cohesion | 5.4 |
| 3.2 | Relationship with performers; selection of subsets | 5.3, 7.2 e) |
| 4.1–4.2 | Functional classification and transformation | 5.2, 5.8, 6.3.6–6.3.7, 7.2 c), Clause 9 |
| 4.3 | Entry Criteria and Exit Criteria | 10.1 |
| 4.4 | Traceability and handoffs | 8.2 |
| 4.5 | Framework-level Controls and Enablers | 9.1 |
| 5.1–5.2 | Models, Frameworks, and life cycle models | 3.5, 3.6, 5.6, 5.8, 7.1–7.2 |
| 5.3 | Process View | 5.8, 8.3 |
| 6.1–6.2 | Concurrency, Iteration, Recursion, and Integration | 8.1 |
| 7.1–7.4 | Tailoring and Instantiation | 7.5.2, Clause 11 |
| 8.1–8.2 | Decision Gates, reviews, and audits | 10.2–10.3 |
| 8.3–8.5 | Conformance, Capability, and Assessment | Clause 12 |
| 9.1–9.3 | Deployment, standards, assessment, and learning | 7.5.1, 7.5.3 |

## Appendix C (informative) Related Documents

The following documents are related to ALPS. They are informative references, not normative references for ALPS. Conformance to ALPS neither requires nor establishes conformance to them.

### C.1 Agent Skills Specification

The [Agent Skills Specification](https://agentskills.io/specification) defines an open, file-based format centered on `SKILL.md`, with optional directories for scripts, references, and assets. When this format is used for an ALPS-conformant Skill, it supplies an implementation form for the Skill Package; ALPS supplies the Process Description semantics, life cycle, and Conformance rules. ALPS does not require this implementation form (1.2 a)).

### C.2 AGENTS.md

[AGENTS.md](https://agents.md/) is an open format for providing repository-scoped context and instructions to coding agents. An `AGENTS.md` file can direct agents to discover, select, apply, and manage ALPS-conformant Skills and can state repository Controls and Constraints. It is not itself a Skill Description and does not alter the meaning or normative force of the Process Framework, this specification, or a Skill Description.

### C.3 Standards on Life Cycle Processes and Process Description

The following standards address life cycle processes and the description of processes in related fields:

- ISO/IEC/IEEE 15288 — system life cycle processes
- ISO/IEC/IEEE 12207 — software life cycle processes
- ISO/IEC/IEEE 24774:2021 — specification for process description

They are listed for readers who also work with those documents. The wording of this specification and of the Process Framework was created independently, and no text, figure, table, example, or translation from those standards is reproduced here. ALPS is not developed, approved, or certified by the organizations that publish them.

## Appendix D (informative) Human Oversight, Accountability, and Evidence in Agent Contexts

### D.1 Status of This Appendix

This appendix is informative. It adds no Skill element, requirement, or Conformance criterion, and it does not alter the meaning or normative force of the PF or of Clauses 1 through 12. The matters collected here are open considerations rather than settled practice, so this appendix offers reference guidance for application and improvement only.

### D.2 Composing Human Oversight from Existing Elements

Human Oversight is not a separate element of a Skill Description. A context of application that needs oversight can express it by combining existing constructs:

- Controls that direct execution or the basis for judgment;
- Constraints that limit the permitted execution;
- Enablers that supply human capability;
- Entry Criteria and Exit Criteria that condition invocation and completion;
- Decision Gates applied before irreversible or high-impact actions;
- records of execution and decisions; and
- judgments made within the ALPS application process and the ALPS management process.

The form of oversight, the granularity and conditions of intervention, the deciding authority, and the escalation path are chosen for the context of application from its risk, the impact and reversibility of the effects involved, the uncertainty present, and the Capabilities of both the humans and the Agents concerned.

Non-determinism, emergent behavior, supervisor cognitive load, automation bias, and unclear responsibility relationships can make oversight difficult to put into practice. These concerns belong to the Agent context and are treated here; they are not part of the general semantics of the PF.

### D.3 Traceability and Accountability

Traceability is the property that the relationships among Inputs, judgments, Tasks, Outputs, evidence, and changes can be followed.

Accountability is the relationship that determines who holds decision authority, supervisory responsibility, or the obligation to answer for a particular Process Instance.

Traceability supports Accountability but does not by itself assign responsibility. A general Process Description fixes neither a performer nor an organizational structure; a particular Process Instance can define the responsibilities, authority, approvers, and escalation paths that it needs. Logs and audit evidence support after-the-fact verification and help clarify responsibility relationships.

### D.4 Human Capability as Enabler and Constraint

- Human expertise, judgment, and the capacity to intervene can be Enablers.
- Cognitive load, response time, and supervisor availability can be Constraints.
- When the needed oversight capability cannot be secured, Entry Criteria may fail to hold.
- Conformance of a Process Instance does not demonstrate the general Capability of a supervisor or an oversight regime, and a high Capability assessment does not demonstrate the Conformance of an individual execution (12.4).

ALPS defines no human capability levels, maturity model, or certification scheme.

### D.5 Evidence for Skills with Non-Deterministic Behavior

The definition of Outcome and the Conformance criteria are unchanged. The following guidance applies existing Skill Verification, Outcome evidence, and risk-based Tailoring; it adds no requirement.

- Where non-determinism matters, a single execution is not treated as sufficient to establish the achievability of Outcomes or a Capability level.
- Representative contexts of use include boundary conditions, abnormal conditions, and novel situations.
- When a unique expected result cannot be defined, acceptance conditions, prohibited conditions, or an evaluation method is defined instead.
- Execution records retain observed variation, the limits of the evidence, and unresolved uncertainty.
- The need for repeated trials or continuous monitoring is decided from quality risk.

Non-determinism and the difficulty of defining a unique expected result can complicate both verification and human oversight.

### D.6 Returning Oversight Results to the ALPS Management Process

The following are representative information items that the ALPS application process can hand to Skill Assessment and Improvement in the ALPS management process as execution records and lessons learned:

- records of human approval and intervention;
- the conditions that made intervention necessary;
- cases in which a human changed or rejected an Agent's proposal;
- failures that humans did not detect;
- cases in which explanations or logs were insufficient for a judgment;
- signs of automation bias or of excessive intervention;
- supervisor load and response delays;
- excess or deficiency of Decision Gates; and
- the quality and limits of the evidence used.

---

(End)
