# ALPS — Agent Lifecycle Process Skills Specification

---

## Foreword

This specification, ALPS (Agent Lifecycle Process Skills), applies the Process Framework (hereafter “PF”) to Agent Skills. Authors vary in the granularity, normative force, life cycle management, and conformance criteria they use for Agent Skills. A shared Process Description structure makes results more consistent and supports deployment, Tailoring, improvement, and Assessment of the described Process. Name, Purpose, and Outcomes establish shared reference points for Process application and Assessment (PF 1.2). This specification therefore establishes common rules for Skill description, life cycle management, and conformance.

This specification treats an Agent Skill as an asset that, by default, provides an authoritative Process Description, and applies the PF design principles throughout the Skill life cycle. It also permits Agent Skills to represent Process Models, Process Reference Models, and Process Views without changing the meanings of those PF constructs.

---

## Contents

- 1. Scope
- 2. Normative Reference and Precedence
- 3. Terms and Definitions
- 4. Normative Language and Conventions
- 5. Fundamental Concepts
- 6. Requirements for Skill Descriptions
- 7. Skill Life Cycle and ALPS Reference Model
- 8. Process Application Structures and Relationships
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

c) Rules for execution structures, interfaces, exchanges, and Process Views used to apply multiple Processes in combination (Clause 8).

d) The declaration and handling of Controls, Constraints, and Enablers applicable to Processes described by Skills (Clause 9), and the application of Entry/Exit Criteria, Decision Gates, reviews, and audits (Clause 10).

e) Rules for Tailoring and Process Instantiation (Clause 11), criteria for claims of Conformance to this specification and to Processes described by Skills, and treatment of Capability (Clause 12).

f) The logical composition and integrity of a Skill Package comprising an authoritative Agent Skill representation and accompanying resources that support understanding or applying the represented PF construct (5.7).

g) Rules for representing a Process, Process Model, Process Reference Model, or Process View through an Agent Skill and for resolving references among those representations (5.1, 5.6, and 8.3).

### 1.2 Matters Not Specified by This Specification

This specification does not establish:

a) A concrete implementation form for a Skill Package beyond the minimum representation metadata and logical references specified in 5.1 and 5.6. Other file formats, metadata formats, physical storage structures, distribution mechanisms, and toolchains are outside the scope of this specification. However, 5.7 applies to the logical composition and integrity of the authoritative Agent Skill representation and accompanying resources.

b) A particular Agent implementation, model, execution environment, or vendor.

c) Details of technical information-security and safety measures. Requirements arising from such measures are handled as Controls or Constraints within the framework of this specification (Clause 9).

d) The content of the individual business domains addressed by Processes described through Skills.

### 1.3 Intended Users

This specification is intended for authors who draft Skill Descriptions, managers of Skill assets, providers and operators of Agents that apply Processes through Skills, and assessors of Conformance of a Skill Description or Process execution.

## 2. Normative Reference and Precedence

The following document is indispensable for application of this specification:

- **Process Framework** (`process-framework.md`). It is abbreviated as “PF” in the text and referenced by clause number, as in “PF 4.3.”

If this specification conflicts with the PF, the PF takes precedence. This specification must not relax a PF requirement or permit an action that the PF prohibits. The specialization of PF constructs for Agent Skills is given in 5.8.

## 3. Terms and Definitions

Terms defined or used in the PF are used with the meanings given in the PF. In addition, the following terms are defined.

**3.1 Agent**
An executing entity capable of performing Activities and Tasks under a stated Purpose, with some autonomy in observing its environment, making judgments, and acting. This includes software systems operating under human direction or supervision.

**3.2 Agent Skill (Skill)**
A unit that an Agent can discover and load. By default, it provides an authoritative reusable Process Description through which the described Process can be applied. As specified in 5.1, it may instead represent a Process Model, Process Reference Model, or Process View. Accompanying resources may be included when needed. It is referred to simply as a “Skill” in this specification.

**3.3 Skill Description**
The authoritative Process Description provided by an Agent Skill representing a Process. It has Name, Purpose, and Outcomes as mandatory elements and can include optional elements and reference information (see Clause 6).

**3.4 Discovery Layer and Execution Layer**
ALPS-specific functional presentation layers through which a Skill Description is made available to an Agent. The discovery layer presents the Name and concise reference information used to discover the Skill and determine its applicability before the complete Skill Description is loaded. The execution layer presents the authoritative Process Description elements and reference information used to execute and assess the described Process.

These layers do not add Process Description elements and do not require a particular physical separation, file format, or storage structure.

**3.5 ALPS Reference Model**
The Process Reference Model in Clause 7 of this specification, which defines the ALPS definition process, ALPS application process, and ALPS management process through their respective Purposes and Outcomes. Each Process comprises three Activities. The model can be used as a frame of reference for assessment and improvement of the Skill life cycle.

**3.6 Invocation**
Determining that Entry Criteria are satisfied and beginning execution of a Process Instance through a selected Agent Skill representing a Process.

**3.7 Skill Asset**
An Agent Skill or Skill Package that has been adopted and placed under management.

**3.8 Skill Discovery Description**
Concise reference information placed in the ALPS-specific discovery layer that an Agent uses to discover a Skill and determine its applicability before loading the complete Skill Description. It states what the described Process does, when the Skill is used, and the information needed to determine applicability.

**3.9 Skill Package**
A unit managed as a whole that contains one authoritative Agent Skill representation and any accompanying resources that support understanding or applying the represented PF construct.

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

### 5.1 Agent Skills and Process Descriptions

An Agent Skill represents a Process by default. When an Agent Skill represents a Process, its authoritative content must be a Process Description conforming to the PF. This is the base ALPS case and requires no explicit asset-kind declaration.

A Skill Description can describe a general Process or, when explicitly scoped to a particular context, a Process Instance. A description of a Process Instance can specify the required capabilities, resources, Inputs, Outputs, Constraints, Controls, and time (PF 1.1).

ALPS also permits an Agent Skill to represent a Process Model, Process Reference Model, or Process View. An Agent Skill representing one of these constructs must declare `metadata.alps.kind` in its `SKILL.md` frontmatter as one of the following values:

- `process-model`;
- `process-reference-model`; or
- `process-view`.

The `skills/` directory and `SKILL.md` are Agent Skill packaging and discovery conventions. They do not change the meaning of the represented PF construct and do not make a Process Model, Process Reference Model, or Process View into a Process.

Agent Skill activation means that an Agent selects and loads an Agent Skill representation. Process Invocation means that execution of a Process Instance begins. Only an Agent Skill representing a Process directly represents an invokable Process. Activating a Process Model, Process Reference Model, or Process View does not itself begin a Process Instance.

### 5.2 Dual Nature of a Process Skill: Descriptive Asset and Enabler

An Agent Skill representing a Process provides a Process Description as its authoritative content and functions as an Enabler for application of the described Process.

Skills, Agents, and tools must be treated as Enablers, not as Inputs (PF 4.1).

### 5.3 Non-Prescription of Performers

A Skill Description must not prescribe the structure of the performer or allocation of Tasks. Capabilities or conditions needed for execution should be stated as Enablers or Constraints without allocating Tasks (PF 3.2).

### 5.4 Skill Boundary and Granularity

The boundary of a Process described by a Skill is typically established from primary Outputs and Outcomes rather than from intermediate Outputs of Activities (PF 3.1). Within the described Process, strong relationships are maintained among Outcomes, Activities, and Tasks, while dependencies on other Processes are reduced as far as practicable.

A significant Activity containing many Tasks may be treated as a separate Process with its own Purpose and Outcomes and described by a separate Skill (PF 3.1).

When the definition, maintenance, assessment, or change handling of an information item spanning multiple Processes has an independent Purpose and Outcomes and mutually cohesive Activities, and can be bounded as one Process, that Process may be described by a separate Skill. By contrast, when no independent Process boundary is established and relationships among existing Processes are presented as a cross-cutting concern, they can be described as a Process View (8.3).

### 5.5 Functional Layers and Progressive Disclosure

PF 1.3 permits a Process Description to present information in layers for readers with different needs. For Agent Skills representing Processes, ALPS defines a discovery layer and an execution layer as functional presentation layers for progressive disclosure. The names and functions of these layers are specific to ALPS and are not PF constructs.

A Skill Description claiming Description Conformance must provide both layers and make their functions distinguishable. The layers may be represented together or separately, provided that one authoritative Skill Description remains identifiable and mandatory references are resolvable.

a) The **discovery layer** must present the Name and Skill Discovery Description. The Skill Discovery Description must state what the described Process does, when the Skill is used, and the information needed to determine applicability.

b) The **execution layer** must present or provide access to the complete Skill Description used for Process execution and Assessment. It includes Name, Purpose, and Outcomes, together with any optional elements and reference information included under 6.1.

c) Matters that cut across multiple Processes should be treated separately from an individual Skill's execution layer. Common Controls and Enablers may be declared as Framework-level elements.

NOTE: These functional layers support progressive disclosure without requiring two files, two sections, or another particular physical structure.

### 5.6 Process Models, Process Reference Models, and Life Cycle Models

Process Models, Process Reference Models, and life cycle models are interpreted with the meanings established by the PF.

A Process Model represented through an Agent Skill identifies a set of related Processes and their relationships. Each Process may identify the Agent Skill that supplies its authoritative Process Description. A Process Model does not need to repeat each Process Purpose and Outcomes.

A Process Reference Model represented through an Agent Skill must identify its Processes by Name, Purpose, and Outcomes and place their relationships in an explicit structure. For every referenced Process Skill, the Process Name must identify the same Process, the Purpose in the Process Reference Model must equal the Purpose in the authoritative Process Description, and the Outcomes in the Process Reference Model must equal the Outcomes in the authoritative Process Description. A mismatch makes the representation invalid; neither representation silently overrides the other.

A Process Model, Process Reference Model, or Process View refers to an Agent Skill by logical package identity and Skill name rather than by repository-relative file path. The canonical form is:

```text
skill:<package-id>#<skill-name>
```

Within the same package, the short form `skill:#<skill-name>` may be used. A resolver must normalize the short form to the full form using the containing package identity before semantic checks are performed. The applicable package binding supplies `package-id`; ALPS does not require GitHub to be the package identity authority.

A subset of Processes can be selected from a Process Model according to Purpose. The selected Processes can then be applied singly or in combination through the Skills that describe them. Selection and timing need continual review when the subject or context of application changes (PF 5.1 and 5.2).

### 5.7 Skill Packages and Accompanying Resources

A Skill Package must contain one authoritative Agent Skill representation.

A Skill Package may include, as needed, reference information, execution resources, and deliverable resources that support understanding or applying the represented PF construct. When accompanying resources are included, their roles and conditions of use must be identifiable from the authoritative representation. Mandatory references must be resolvable.

Unnecessary duplication or conflict must not arise between the authoritative representation and accompanying resources. Accompanying resources must be treated according to their function rather than where they are stored. For a Skill Description, they are treated as reference information, Inputs, Outputs, Controls, Constraints, or Enablers according to the function they perform in Process execution (9.1).

A Skill Package should contain only resources that directly support understanding or applying the represented PF construct.

### 5.8 Specialization of the Process Framework

ALPS specializes the general constructs of the PF for Agent Skills. The normative source for each general concept remains the PF; this specification does not restate general definitions and adds only what is specific to Agent Skills.

| PF construct | ALPS treatment |
|---|---|
| Process Description | Skill Description (3.3) when the Agent Skill represents a Process |
| Process Model | May be represented directly by an Agent Skill with `metadata.alps.kind: process-model` (5.1, 5.6) |
| Process Reference Model | May be represented directly by an Agent Skill with `metadata.alps.kind: process-reference-model` (5.1, 5.6) |
| Process View | May be represented directly by an Agent Skill with `metadata.alps.kind: process-view` (5.1, 8.3) |
| Resources that perform or support a Process | Agents, models, tools, and execution environments, treated as Enablers (5.2, 9.3) |

ALPS may make a PF rule concrete for the Agent context and may strengthen it where needed. ALPS must not change the meaning of a PF concept, weaken a PF requirement, or replace a PF concept with a different one (see Clause 2).

## 6. Requirements for Skill Descriptions

### 6.1 Composition of Elements

A Skill Description must contain Name, Purpose, and Outcomes (PF 1.2).

Activities, Tasks, Inputs, Outputs, Controls, Constraints, Enablers, Entry Criteria, Exit Criteria, and reference information are optional elements added according to the Purpose of the description and the required level of detail. A Decision Gate is not a component of a Skill Description; it is treated as a decision mechanism that controls application of the described Process (PF 1.2 and 8.1, Clause 10).

### 6.2 General Writing Rules

a) The roles of Name, Purpose, Outcomes, Activities, and Tasks must be distinguished, and consistency among them must be maintained (PF 1.4).

b) Each sentence should address only one meaning, and independent objectives, results, or actions should not be joined in one sentence. Each statement should contain enough context to remain meaningful when referenced independently within its Skill Description. When supplementary explanation is needed, it can be separated as a reference statement or note rather than superimposing meaning on the primary statement.

c) A general Process Description must not require a specific method, technique, tool, metric, management method, or execution sequence. Any necessary temporal relationship should be stated explicitly as a Constraint.

d) Activities and Tasks must not be interpreted as procedural steps (PF 1.4).

e) The normative attribute of a statement must be distinguishable through the normative language in 4.1.

NOTE: Rule d) also protects against an Agent misreading the listed order of Activities and Tasks as a prescribed sequence of steps.

### 6.3 Writing Rules for Individual Elements

#### 6.3.1 Name

The Name in a Skill Description must use a concise noun phrase as the Skill heading. The Name states the described Process's central concern and differentiates it from other Processes represented in the applicable Process Model. The Name must not be written as a summary of the Purpose (PF 2.1).

#### 6.3.2 Purpose

The Purpose in a Skill Description must state one or more related high-level objectives for performing the described Process. The Purpose should be stated concisely in one sentence wherever possible. Summarizing Activities or Outcomes in the Purpose should be avoided. Combining multiple independent Purposes in one sentence should also be avoided. If further explanation is needed, it can be placed in a reference statement or note. When Process scopes appear to overlap, the Purpose should characterize the scope or boundary of the described Process (PF 2.1).

#### 6.3.3 Outcome

An Outcome in a Skill Description represents a measurable and tangible result condition achieved through the described Process. An Outcome must be observable and assessable and must be clearly distinguished from an Output. The creation of a document, record, or information item itself must not be written as an Outcome (PF 2.2).

An Outcome must be written as a declarative statement of a condition in which a positive and observable result is established. Each Outcome must describe only one result, and joining multiple independent results with conjunctions must be avoided. An Outcome of a general Process must be meaningful in every applicable scope.

Taken together, the Outcomes must fully support attainment of the Process Purpose, and no listed Outcome must be irrelevant to that attainment. Each Outcome should remain meaningful when read independently. Singularity and clarity of meaning take precedence over brevity, and the size of the Outcome set follows from what attainment of the Purpose needs. Benefits of performing the Process should be distinguished from Outcomes and, when useful, explained separately in a non-normative note attached to the Purpose.

#### 6.3.4 Activity

An Activity describes a cohesive set of actions within the Process described by a Skill and functions as an organizing construct for classifying related Tasks. An Activity should contain Tasks that are strongly related to one another and weakly related to Tasks belonging to other Activities or Processes.

The Activities and any separated Processes must collectively cover all Outcomes and satisfy the Process Purpose. Activities need not map individually to Outcomes (PF 2.3).

#### 6.3.5 Task

A Task must have the primary function of expressing an individual action that supports achievement of one or more Outcomes and must be written so that the object and operation of that action are distinguishable. A statement whose primary function is not an individual action must not be treated as a Task and must be placed in the element corresponding to that function. Each Task must be assigned a normative attribute, and the normative language in 4.1 must make clear whether the action is a requirement, recommendation, permissible action, or typical action. Tasks assigned to an Activity need not exhaust every action within that Activity's boundary. The rules in 6.2 c) and d) apply to both Activities and Tasks.

#### 6.3.6 Input and Output

Inputs and Outputs represent connections between the described Process and its external environment. It is optional whether mandatory or representative Inputs are specified, and it is also optional whether Outputs are specified when achievement of the Outcomes can be demonstrated (PF 4.1 and 4.2). An Output can be expressed as an artifact or information item. An Output of one Process can become an Input to another Process.

When the Output of one Process is used as an Input to another Process, their names, meanings, and scopes should be aligned. The level of detail used to describe the relationship should be determined according to the Purpose of the Process Description, dependencies among Processes, and quality risk.

Representative Inputs and Outputs do not prescribe the only manner of execution. The described Process should be understood from the entire Skill Description (PF 4.2).

#### 6.3.7 Control, Constraint, Enabler, Entry Criteria, and Exit Criteria

Controls and Constraints declare conditions that direct or limit execution of the described Process. Enablers make Process execution possible or assist it. Entry Criteria state conditions under which the described Process can begin; Exit Criteria state conditions under which a Process Instance can be completed. These elements are used according to the Purpose of the description and the required level of detail. Details are given in Clauses 9 and 10.

The primary function of a Control or Constraint statement must be to declare a condition that directs or limits execution. A statement whose primary function is an individual action must be classified as a Task.

When a summary of Entry Criteria is placed in the discovery layer, it must not conflict with the Entry Criteria available through the execution layer.

#### 6.3.8 Reference Information

Overviews, descriptions, Common Approach, practical tips, notes, and examples are used as reference information to support understanding or application of the described Process. Reference information must not alter the meaning or normative force of primary Process elements (PF 1.4).

As reference information placed in the ALPS-specific discovery layer, a Skill Discovery Description must state concisely what the described Process does, when the Skill is used, and the information needed to determine applicability. It must be consistent with the authoritative Name, Purpose, Outcomes, scope, Entry Criteria, and Constraints available through the execution layer and must not replace those elements or alter their normative meanings.

The Skill Discovery Description of a Skill claiming Description Conformance to this specification must end with a short ALPS conformance marker in the language of the description. The marker must be exactly `ALPS-conformant.` in English and `ALPS準拠。` in Japanese. This marker is a standardized shorthand claim whose subject is the containing Skill Description and whose criteria are Description Conformance under 12.1 a); it does not assert Reference Model Conformance or Execution Conformance.

## 7. Skill Life Cycle and ALPS Reference Model

### 7.1 Skill Life Cycle Model

A Skill life cycle model is a Framework of Skill-related Processes and Activities and serves as a common frame of reference for communication and understanding (PF 5.2). This specification establishes a reference life cycle model comprising the following Stages:

a) **Concept Stage** — Needs for treatment as Skills are identified and selected.

b) **Definition Stage** — Skill Descriptions are designed and verified.

c) **Operation Stage** — Skills are selected and loaded, and the Processes they describe are invoked, executed, and orchestrated with other Processes.

d) **Evolution Stage** — Skills are assessed, tailored, and improved.

e) **Retirement Stage** — Skills that have become unnecessary or unsuitable are withdrawn from use.

The order shown does not prescribe execution order. Processes and Activities can span multiple Stages and can be applied iteratively, recursively, or concurrently (PF 5.2, Clause 8).

### 7.2 Composition and Interpretation of the Reference Model

The ALPS Reference Model comprises the following three Processes. Each Process is defined by its Purpose and Outcomes and comprises three Activities (PF 1.1 and 5.1).

| Process | Activities |
|---|---|
| ALPS definition process | Skill Need Identification / Skill Design / Skill Verification |
| ALPS application process | Skill Selection / Process Execution / Process Orchestration |
| ALPS management process | ALPS Asset Management / Tailoring / Assessment and Improvement |

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
| ALPS management process | Information about managed Agent Skills, Skill Packages, Process Models, and Process Views; Tailoring decisions; and conditions of application | ALPS application process |
| ALPS application process | Execution and decision records, lessons learned, and measurable results | ALPS management process |
| ALPS management process | Change requests, redefinition requests, and reverification requests | ALPS definition process |

### 7.3 ALPS Definition Process

**Purpose**: This Process establishes an assessable and usable Skill Description that satisfies identified stakeholder needs.

**Outcomes**: Success of this Process establishes the following conditions:

a) The need to be addressed as a Skill and the intended contexts of use are identified.

b) The Process Purpose, Outcomes, and boundary are aligned with the selected need.

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

a) The Process boundary must be established from the primary Outputs and Outcomes (5.4).

b) Dependencies on other Processes must be reduced as far as practicable.

c) The Skill Description must provide distinguishable discovery-layer and execution-layer information. Their physical separation is not required (5.5).

d) A significant Activity that benefits from detailed treatment may be separated into another Process described by another Skill.

e) Name, Purpose, and Outcomes must be written in accordance with 6.3.1 through 6.3.3.

f) Each Task must have the primary function of expressing an individual action that supports achievement of one or more Outcomes and must be written so that the object and operation of that action are distinguishable (6.3.5).

g) Each statement must be classified under the Skill element corresponding to its primary function (6.2 a), 6.3).

h) Each Task must be assigned a normative attribute (6.3.5).

i) Guidance on how to apply the Skill should be separated as Common Approach and practical tips.

j) It must be confirmed that the set of Activities covers all Outcomes and satisfies the Purpose (6.3.4).

k) Relationships between Tasks and Outcomes should be identified (8.2).

l) The Skill Discovery Description must state what the Process does, when the Skill is used, and the information needed to determine applicability in accordance with 3.8, 5.5, and 6.3.8.

m) When representative Inputs and Outputs are shown, the principal relationships with other Processes should be identified as needed (6.3.6, 8.2).

n) When a Skill Package is composed, the need, role, and conditions of use for its accompanying resources must be identified (5.7).

#### 7.3.3 Skill Verification

This Activity confirms the descriptive conformance of the Skill Description and the achievability of the intended Outcomes.

a) The Skill Description must be reviewed using agreed criteria (Clause 10).

b) It must be confirmed that each Task has the primary function of expressing an individual action that supports achievement of one or more Outcomes and that the object and operation of that action are distinguishable (6.3.5, 8.2).

c) It must be confirmed that the element classification of each statement is consistent with its primary function, including the distinction between conditions declared by Controls and Constraints and individual actions expressed by Tasks (6.2 a), 6.3.5, 6.3.7, 9.2).

d) It must be confirmed that normative attributes are distinguishable (4.1).

e) When a general Process Description is verified, it must be confirmed that its normative part does not require a specific method, technique, tool, or execution sequence (6.2 c)).

f) It must be confirmed that the discovery-layer and execution-layer information are consistent (5.5, 6.3.8).

g) The review should incorporate a perspective independent of the Skill author.

h) The achievability of the Outcomes should be evaluated through trials in representative contexts of use.

i) It should be evaluated whether applicability can be determined from discovery-layer information alone, including the Skill Discovery Description.

j) Boundary cases from the intended contexts of use may be included in the evaluation.

k) Detected defects should be recorded, and actions with due dates and completion conditions should be established (PF 8.2).

l) Completion of defect treatment should be confirmed before the Decision Gate for the adoption decision.

m) When the Skill Description identifies an exchange with another Process, it should be evaluated whether the Output can be used as the intended recipient's Input.

n) When the Skill Package is included in the verification scope, the existence of the authoritative Skill Description, resolvability of mandatory references, roles and conditions of use of accompanying resources, and consistency between the Skill Description and those resources must be evaluated (5.7).

**Representative Inputs**: Stakeholder expectations, lessons learned, information about execution performance, applicable Controls and Constraints, information about existing Skill assets, verification criteria, and representative contexts of use.

**Representative Outputs**: The selected Skill need and selection rationale, verified Skill Description, record of mappings among elements, verification results, and record of defect treatment.

NOTE: Appendix D gives reference guidance on evidence for Skills whose behavior is not deterministic.

### 7.4 ALPS Application Process

**Purpose**: This Process achieves intended Outcomes by applying, individually or in combination, Processes represented by Skills suited to the context of application.

**Outcomes**: When this Process succeeds, the following conditions are established:

a) The needs and conditions of the context of application are identified.

b) The Processes to apply, the Skills providing their authoritative descriptions, and the form of application are determined with rationale.

c) Applicable Controls, Constraints, and Tailoring decisions are identified.

d) The results of applying a Process Instance conform to the declared scope, applicable Controls and Constraints, and Tailoring decisions.

e) The declared Outcomes of the Processes subject to application are achieved.

f) Necessary exchanges among Processes are established.

g) Completeness and consistency of the Process composition are established.

| Activity | Outcomes primarily supported |
|---|---|
| Skill Selection | a), b), c) |
| Process Execution | c), d), e) |
| Process Orchestration | e), f), g) |

NOTE: A decision to apply no Process can also be a legitimate judgment for the context of application. When this decision makes some Outcomes of this Process inapplicable, Full Conformance to this Process must not be claimed. The inapplicable Outcomes must be declared, and Tailored Conformance under 12.3 must be used.

**Activities and Tasks**:

#### 7.4.1 Skill Selection

This Activity determines the Processes to apply, the Skills providing their authoritative descriptions, and their form of application.

a) The needs and conditions of the context of application and applicable Constraints must be identified.

b) The needs are typically compared with the Purposes and Outcomes of the Processes described by candidate Skills.

c) Candidate Skills are typically identified from discovery-layer information, including Skill Discovery Descriptions.

d) When candidates overlap, their scopes should be distinguished by their Purposes (6.3.2).

e) When no suitable candidate exists, the need may be transferred to Skill Need Identification in the ALPS definition process.

f) It must be determined whether the uncertainty and risk associated with the application decision are acceptable (Clause 10).

g) The rationale for the decision should be recorded.

#### 7.4.2 Process Execution

This Activity uses a selected Skill to execute an Instance of the represented Process and achieve the Outcomes declared in its Process Description.

a) The described Process must be invoked through its providing Skill only after determining that the Process Entry Criteria are satisfied. If they are not satisfied, invocation must be deferred or resolution of the deficiency must precede it.

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

l) Lessons learned through execution may be transferred to Assessment and Improvement in the ALPS management process.

#### 7.4.3 Process Orchestration

This Activity combines multiple Processes and manages their interfaces, exchanges, and the completeness and consistency of the composition as a whole.

a) The target set of Outcomes must be identified.

b) The source of each Process and the Skill providing its authoritative description should be identified (8.3).

c) A repeatedly used composition may be documented as a Process View (8.3).

d) The mapping between each provider Output and recipient Input must be made explicit (8.2).

e) An exchange not defined in advance may be added through Tailoring (PF 4.4).

f) When an Output changes through Iteration or Recursion, affected Inputs should be identified and their integrity and applicable criteria reevaluated (PF 6.2).

g) Integration must ensure completeness within a level and consistency across levels (8.1).

h) Achievement of Outcomes for the composition as a whole should be determined.

i) When the same information item is changed by multiple Processes, handling of its integrity, status, and change must be established according to quality risk (8.2).

**Representative Inputs**: Needs of the context of application, invocation requests, Skill discovery layers and Skill Descriptions, the target set of Outcomes, Inputs specified by Skill Descriptions, Framework-level declarations, and Tailoring decisions.

**Representative Outputs**: Decisions on applied Processes and the Skills providing their descriptions, forms of application, Outputs specified by Skill Descriptions, definitions of Process compositions, Outputs of the compositions as a whole, and execution and decision records.

**Representative Enablers**: Managed Skill assets, Agent capabilities, necessary tools, and execution environments.

NOTE: Records of human approval, intervention, and oversight can form part of the execution and decision records exchanged with the ALPS management process. Appendix D lists representative items.

### 7.5 ALPS Management Process

**Purpose**: This Process governs adopted ALPS assets and their application so that suitable Agent Skills, Skill Packages, Process Models, and Process Views remain available, controlled, and fit for their intended use.

**Outcomes**: Success of this Process establishes the following conditions:

a) Policies and guidance for adoption, deployment, Tailoring, assessment, change, and retirement are established.

b) Adopted Agent Skills, Skill Packages, Process Models, and Process Views are discoverable in a managed state.

c) Identity, status, version, references, change, and retirement of managed subjects are controlled.

d) Tailoring decisions and rationale are traceable to applicable Controls and Constraints.

e) Process application performance is assessed against declared criteria.

f) The fitness of managed Process Models and Process Views is assessed against declared criteria.

g) Improvement opportunities are prioritized from evidence, lessons learned, and assessment results.

h) Decided improvements are implemented.

i) Subjects affected by implemented improvements are reverified as needed.

| Activity | Outcomes primarily supported |
|---|---|
| ALPS Asset Management | a), b), c), h), i) |
| Tailoring | a), d) |
| Assessment and Improvement | e), f), g), h), i) |

**Activities and Tasks**:

#### 7.5.1 ALPS Asset Management

This Activity manages adoption, discoverability, reference integrity, change communication, configuration, and retirement of managed ALPS subjects.

a) The means for managing and deploying Agent Skills, Skill Packages, Process Models, and Process Views, together with Tailoring guidance, should be established.

b) Framework-level Controls and Enablers must be declared together with their scope, exceptions, and whether Tailoring is permitted.

c) Verification evidence from the ALPS definition process should be confirmed before an authoritative description or representation is adopted.

d) The authority, version or state, applicability, references, and management status of each adopted subject should be recorded.

e) Mandatory references among Process Descriptions, Process Models, Process Views, and accompanying resources must be checked for resolvability.

f) Changes to management guidance or a managed subject should be communicated to affected users and dependent subjects.

g) A managed subject for which the need no longer exists or that has become harmful must be identified for retirement.

h) A subject identified for retirement must be retired through a controlled decision.

i) A retired description or representation may be retained for reference when its status and conditions of use remain explicit.

j) Duplication, gaps, and inconsistent relationships within applicable Process Models and Process Views should be continually identified.

k) When a Skill Package component or referenced subject changes, affected descriptions, representations, and accompanying resources should be identified.

l) Affected descriptions, representations, and accompanying resources that require reverification must be reverified.

#### 7.5.2 Tailoring

This Activity adapts applicable Processes and Process Models to the needs, conditions, and risks of a particular context of application.

a) Application-related risks, requirements, complexity, available capabilities and resources, and relevant standards must be identified.

b) Candidate Processes or life cycle models must be evaluated against the conditions of application, available expertise, stakeholder expectations, and risk tolerance.

c) Tailoring decisions should be based on facts and evidence.

d) Outcomes, Activities, Tasks, representative Inputs, and representative Outputs may be deleted, modified, or added within the declared Tailoring scope.

e) Tailoring must comply with applicable Controls and Constraints.

f) Input must be obtained from affected parties.

g) The rigor of Process application should be set according to risk.

h) The Tailoring scope should be recorded.

i) Tailoring assumptions should be recorded.

j) Tailoring criteria should be recorded.

k) The rationale for each Tailoring decision should be recorded.

l) Tailoring should be reviewed throughout application.

m) Tailoring should be revised when conditions warrant.

n) A means of assessing the performance of a tailored Process should be established.

o) The detail used to describe Inputs, Outputs, and their exchanges should be adjusted according to dependencies, concurrency, iteration, and quality risk.

#### 7.5.3 Assessment and Improvement

This Activity assesses managed subjects and connects the results to controlled improvement.

a) Assessment criteria should be established according to the subject being assessed.

b) Process application should be assessed using relevant performance, effectiveness, Outcome, Task, and Conformance evidence.

c) A Process Model should be assessed for coverage, relationships, consistency, applicability, and resolvability of referenced Process Descriptions.

d) A Process View should be assessed for fitness to its Concern or Purpose, source integrity, application guidance, and achievement of its declared Outcomes.

e) Lessons learned should be collected throughout application and at planned review points.

f) Strengths, weaknesses, gaps, duplication, and inconsistent exchanges should be assessed.

g) Improvement opportunities should be continually identified.

h) Improvement opportunities should be prioritized according to available evidence.

i) Decided improvements should be implemented.

j) Candidate changes should be analysed for impacts on dependent subjects, references, users, and Conformance claims.

k) A changed authoritative description or representation should be submitted to the ALPS definition process for reverification.

**Representative Inputs**: Verified Skill Descriptions and other verified ALPS representations, change requests, contexts of application, Tailoring guidance, Input from affected parties, Process Instance and decision records, lessons learned, measurement results, and reference-integrity findings.

**Representative Outputs**: Managed Agent Skills, Skill Packages, Process Models, and Process Views; Tailoring decisions and rationale; assessment results; prioritized improvements; change or redefinition requests; reverification requests; and retirement decisions.

## 8. Process Application Structures and Relationships

### 8.1 Concurrency, Iteration, Recursion, and Integration

Processes can be executed in structures other than a serial sequence. The following execution structures can be applied (PF 6.1):

a) **Concurrency** — Applying two or more Processes in parallel at the same structural level.

b) **Iteration** — Repeatedly applying the same Process or set of Processes at the same level. It should continue as far as needed to resolve problems and refine Outputs.

c) **Recursion** — Repeatedly applying the same Process or set of Processes at successive structural levels of the subject of application. The Output of a Process applied at one structural level can become an Input to a Process applied at the next structural level.

d) **Integration** — Ensuring completeness within a level and consistency across levels.

These relationships do not prescribe execution order. The actual flow is determined through Tailoring, with consideration for the effects of Output changes on Inputs to other Processes (PF 6.2).

### 8.2 Interfaces, Exchanges, and Traceability Among Processes

An interface and exchange between Processes represented by Skills is treated as a mapping from a provider Process's Output to a recipient Process's Input. An interface is not an independent Skill element, and an undefined exchange can be added through Tailoring (PF 4.4).

When multiple Processes are composed for application, the mapping from each provider Output to each recipient Input must be made explicit (7.4.3 d)).

When Processes are applied concurrently, iteratively, or recursively, shared or interdependent information items and the reference or change relationships among them should be identified to the extent needed for application. When the same information item is changed by multiple Processes, handling of its integrity, status, and change must be established according to quality risk.

When a change to an Output affects an Input to another Process, the affected Process and mapping should be identified and necessary reassessment performed.

When Output quality affects a subsequent Outcome or stakeholder acceptance, the determination conditions and necessary evidence should be related to Entry Criteria, Exit Criteria, a review, or a Decision Gate.

Traceability should cover Outcomes, Activities, Tasks, and information items. These mappings provide a basis for integrity and Process Assessment (PF 4.4).

NOTE: Explicit exchange mappings keep the meaning, scope, state, and quality conditions of an information item from being lost as it passes between Processes.

### 8.3 Process View

A Process View organizes Activities and Tasks spanning multiple Processes around a particular concern or Purpose (PF 5.3).

When an independent Process boundary is established, the Process can be described by a separate Skill in accordance with 5.4.

A Process View represented through an Agent Skill must declare `metadata.alps.kind: process-view`. Activating that Agent Skill loads the View representation and does not itself invoke a Process.

a) Every Process View must state its Name, Purpose, and Outcomes.

b) To achieve the Outcomes, a Process View may include Activities and Tasks selected from an existing Process Model, adapted Activities and Tasks, or Activities and Tasks specific to the Process View.

c) A Process View must include explanations and guidance for applying those Activities and Tasks.

d) A Process View must explicitly identify the source Process of each Activity and Task and whether it is `selected`, `adapted`, or `new`. Elements selected from an existing Process Model must retain their source Process and source statement. Source Process Skills must be identified by the canonical Skill references specified in 5.6.

e) Adapted elements and elements specific to the Process View are not treated as changes to the original Process Model. Unless Tailoring or formal adoption into the Process Model occurs, these elements do not count toward Conformance to the source Process.

f) Operation of a particular Process Model may adopt a restricted Process View that uses only Activities and Tasks from existing Processes. Under this approach, Activities and Tasks specific to the Process View must not be included.

g) A Process View may show connections among Processes and the sources of the Processes used in its composition.

Process View Description Conformance concerns the View representation itself. It requires the View Purpose, Outcomes, source provenance, treatment classifications, relationships or handoffs, and application guidance to be complete and internally consistent.

Source Process Conformance remains a claim about the applicable source Process. A `selected` element can contribute to that claim according to the source Process Conformance basis. `adapted` and `new` elements do not contribute to Source Process Conformance unless managed Tailoring or formal adoption incorporates them into that Process.

Achievement of the Process View Outcomes can be assessed separately. That assessment is not Process Outcome Conformance for a source Process.

## 9. Controls, Constraints, and Enablers

### 9.1 Framework-Level Controls and Enablers

Framework-level Controls and Enablers must state their scope, exceptions, and whether Tailoring is permitted (PF 4.5).

Elements common to Processes within the declared scope may be declared once rather than repeated in each Skill Description (PF 4.1 and 4.5).

Information resources that apply in common to multiple Processes can be declared as Framework-level Controls or Enablers according to their function. An item transformed by a Process is treated as an Input or Output. These classifications must be based on the function performed by the information resource in Process execution, not on its form or location.

### 9.2 Skill-Level Controls and Constraints

Controls and Constraints declare conditions or permissible boundaries for execution of the described Process. Controls can arise from applicable laws or regulatory requirements, policies, conformance to voluntary standards, or agreements. Constraints can arise from environmental factors or conditions of application external to the Process (PF 4.1 and 4.5).

A Control or Constraint statement must be classified according to its primary function as specified in 6.3.7.

Controls and Constraints can be described in separate sections of a Skill Description or as conditions associated with other Skill elements. Any temporal relationship needed in a general Process should be declared explicitly as a Constraint (6.2 c)).

### 9.3 Enablers, Capabilities, and Tools

Human or Agent capabilities, tools, and technologies support Process execution as Enablers (PF 4.1 and 4.5).

Human and automated resources that execute a Process, including Agents, models, execution environments, and tools, are not treated as Process Inputs (PF 4.1 and 4.2). When described as elements, they must be described as Enablers.

NOTE: Treating Agents, models, tools, and execution environments as Enablers keeps the items a Process transforms distinct from the capability that performs the transformation.

## 10. Entry/Exit Criteria, Decision Gates, and Reviews

### 10.1 Entry Criteria and Exit Criteria

a) Entry Criteria state conditions under which the described Process can begin. A summary should be placed in the discovery layer as reference information for determining applicability (5.5).

b) Exit Criteria state conditions under which a Process Instance can be completed. Exit Criteria should be related to determining achievement of the Outcomes.

### 10.2 Decision Gate

A Decision Gate is not a component of a Skill Description; it is treated as a decision mechanism that controls application of the described Process (PF 8.1).

a) A Decision Gate uses Decision Criteria based on the Purpose, Outcomes, conditions of application, and risk to determine whether a state transition can occur (PF 8.1).

b) The frequency, scope, and formality of Decision Gates can be adjusted to the context of application.

c) The decision, its rationale, and its assumptions should be recorded (PF 8.1).

d) A decision to pass should be based on evidence, and Decision Criteria should be reevaluated as the context of application changes.

NOTE: Confirmation and human escalation before an irreversible or high-impact action are forms of applying a Decision Gate. The Gate gives the application a controlled point at which such an external effect can be held, changed, or stopped before it occurs. Appendix D describes how human oversight can be composed from existing elements.

### 10.3 Reviews and Audits

A review evaluates Process performance, Outputs, and achievement of Outcomes using agreed criteria. An audit includes a detailed review of evidence demonstrating conformance to the Process, Outputs, and requirements and confirms that mandatory attributes and applicable requirements are satisfied (PF 8.2).

When an Output is transferred to another Skill or a stakeholder, it should be evaluated against applicable criteria to determine whether the Output can be used as the intended Input or result.

Reviews and audits should be tailored to the needs and risks of the subject of application, and their Entry Criteria, Exit Criteria, and responses to problems should be established (PF 8.2).

## 11. Tailoring and Process Instantiation

### 11.1 Discipline of Tailoring

Tailoring must be performed in accordance with Tailoring in the ALPS management process (7.5.2), whose requirements are prerequisites for Tailored Conformance (12.3).

NOTE: Requiring Tailoring to pass through the ALPS management process prevents unrecorded changes to a Process's meaning, normative force, or applicability.

### 11.2 Levels of Tailoring

Common-level Tailoring adapts an external standard, including this specification, to needs shared across an intended application domain. Individual-level Tailoring adapts the resulting common Process to the needs of a particular subject of application (PF 7.2).

### 11.3 Process Instantiation

When justified by quality risk, a Process Instance can be described in greater detail, and instance-specific success criteria, Activities, and Tasks can be identified (PF 7.4).

## 12. Conformance, Capability, and Assessment

### 12.1 Subjects of Conformance

Conformance relating to this specification can be claimed for the following subjects. Every claim must identify the subject and the selected criteria.

a) **Description Conformance** — A Skill Description satisfies the applicable requirements of Clauses 4 through 6. When a Skill Package containing a Process representation is included in the subject of conformance, the Package also satisfies the applicable requirements of 5.7.

b) **Reference Model Conformance** — For definition, application, or management of Skills, Conformance under 12.2 or 12.3 is established for the declared Process among the three Processes in Clause 7.

c) **Execution Conformance** — Execution of a Process Instance through a Skill establishes Conformance under 12.2 or 12.3 to the Process described by that Skill.

d) **Process View Description Conformance** — An Agent Skill representation of a Process View satisfies the applicable representation, source-provenance, treatment-classification, relationship, application-guidance, and internal-consistency requirements of 5.1, 5.6, and 8.3.

### 12.2 Full Conformance

Full Conformance must be claimed as Conformance to Outcomes, Tasks, or both, and the selected criteria must be stated. When both are selected, both must be satisfied (PF 8.3).


a) **Full Conformance to Outcomes** requires achievement of all mandatory Outcomes in the declared Process described by a Skill or in the declared Reference Model Process. This approach provides greater freedom in how the conformant Process is implemented; Activities and Tasks are treated as guidance.

b) **Full Conformance to Tasks** requires satisfaction of every requirement stated with **must** or **must not** by an Activity or Task in the declared Process described by a Skill or in the declared Reference Model Process. Recommendations, permissible actions, and typical actions are not, solely by virtue of those attributes, mandatory conditions for Full Conformance to Tasks. When this approach is selected, Outcomes are treated as guidance.

For Conformance to the Reference Model, the units for which Outcome Conformance to a Process can be claimed are the ALPS definition process, ALPS application process, and ALPS management process. Independent Outcome Conformance must not be claimed for an individual constituent Activity.

Assessment of Process View Outcomes is separate from Process Outcome Conformance for a source Process.

### 12.3 Tailored Conformance

Tailored Conformance may be claimed for a Process described by a Skill or for a Reference Model Process that does not meet Full Conformance. The claim must declare the Process tailored in accordance with Tailoring in the ALPS management process (7.5.2) and its scope of application. It must also demonstrate satisfaction of every Outcome and Activity/Task requirement remaining within that scope (PF 8.3 and 8.4).

When only some Activities constituting a Reference Model Process are applied, the application must not be claimed as independent Process Conformance to those Activities. It must be declared as a tailored scope of the parent Process, and the Tailored Conformance criteria must be used.

### 12.4 Capability and Assessment

Capability is treated as a dimension of assessment separate from Conformance. Specifically performing Activities and Tasks can require a higher Capability level than achieving Outcomes alone. However, Capability level alone does not establish Conformance, nor does Conformance alone determine Capability level (PF 8.5).

Outcomes in Skill Descriptions and the Purposes and Outcomes of the three Processes can be used for Process Assessment and effectiveness assessment (PF 8.5, 7.5.3).

Assessment of a Skill Package can evaluate the existence of the authoritative Agent Skill representation, resolvability of mandatory references, consistency between the authoritative representation and accompanying resources, roles and conditions of use of accompanying resources, and reverification after changes (5.7, 7.3.3, 7.5.1).

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

This Process establishes a state in which decisions, action items, and open issues can be distinguished from the meeting record.

## Outcomes

When this Process succeeds, the following conditions are established:

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

NOTE 1: `description` states what the described Process does and when the Skill is used, making that information available before Skill selection (3.8).

NOTE 2: “Consolidated meeting minutes” is an Output, not an Outcome (6.3.3). The Constraint declares the permitted transfer condition, while the corresponding transfer action is stated as a Task (6.3.7, 9.2). Enablers are not Inputs (9.3), and this Skill does not prescribe a performer (5.3).

### A.3 Example Composition of a File-Based Skill Package

The following is an informative example of applying 5.7 through a file-based Environment Binding. This composition and these names are not requirements (1.2). Storage groupings other than `SKILL.md` are optional and are established only when necessary accompanying resources exist. The authoritative Agent Skill representation remains the semantic source; an Environment Binding may project discovery information into frontmatter or a separate registration record without changing its meaning or normative force.

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
| `SKILL.md` | Authoritative Agent Skill representation. For a Process representation, the body provides the authoritative Skill Description and frontmatter can project discovery-layer information. Non-Process representations declare `metadata.alps.kind` as specified in 5.1. |
| `references/` | Reference information loaded as needed. Individual filenames are not prescribed. |
| `scripts/` | Execution resources that support reproducibility or reliability. For Process execution they are typically treated as Enablers. |
| `assets/` | Resources used to create Outputs or support the representation. They are treated according to function. |

## Appendix B (informative) Correspondence with the Process Framework

| PF clause | Subject | Corresponding clause in this specification |
|---|---|---|
| 1.1 | Process, Process Description, and Process Instance | 5.1, 5.8 |
| 1.2–1.3 | Required elements, optional detail, and the two-part form | 3.8, 5.1, 5.5, 6.1 |
| 1.4 | Description and interpretation rules | 4.1, 6.2, 6.3.8 |
| 2.1–2.3 | Name, Purpose, Outcome, Output, Activity, and Task | 6.3.1–6.3.6 |
| 3.1 | Boundary, granularity, and cohesion | 5.4 |
| 3.2 | Relationship with performers; selection of subsets | 5.3, 7.2 e) |
| 4.1–4.2 | Functional classification and transformation | 5.2, 5.8, 6.3.6–6.3.7, 7.2 c), Clause 9 |
| 4.3 | Entry Criteria and Exit Criteria | 10.1 |
| 4.4 | Traceability and handoffs | 8.2 |
| 4.5 | Framework-level Controls and Enablers | 9.1 |
| 5.1–5.2 | Models, Frameworks, and life cycle models | 3.5, 5.6, 5.8, 7.1–7.2 |
| 5.3 | Process View | 5.8, 8.3 |
| 6.1–6.2 | Concurrency, Iteration, Recursion, and Integration | 8.1 |
| 7.1–7.4 | Tailoring and Instantiation | 7.5.2, Clause 11 |
| 8.1–8.2 | Decision Gates, reviews, and audits | 10.2–10.3 |
| 8.3–8.5 | Conformance, Capability, and Assessment | Clause 12 |
| 9.1–9.3 | Deployment, standards, assessment, and learning | 7.5.1, 7.5.3 |

## Appendix C (informative) Related Documents

The following documents are related to ALPS. They are informative references, not normative references for ALPS. Conformance to ALPS neither requires nor establishes conformance to them.

### C.1 Agent Skills Specification

The [Agent Skills Specification](https://agentskills.io/specification) defines an open, file-based format centered on `SKILL.md`, with optional directories for scripts, references, and assets. When this format is used for an ALPS representation, it supplies the Agent-facing packaging, discovery, and loading form; ALPS supplies the PF-based semantics, life cycle, representation rules, and Conformance rules. ALPS requires only the minimum representation metadata and logical references specified in this specification and otherwise does not require a particular file-based implementation form (1.2 a)).

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

The following are representative information items that the ALPS application process can hand to Assessment and Improvement in the ALPS management process as execution records and lessons learned:

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
