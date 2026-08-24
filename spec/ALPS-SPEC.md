# ALPS — Agent Lifecycle Process Skills Specification

---

## Foreword

This specification, ALPS (Agent Lifecycle Process Skills), applies the Process Framework (hereafter “PF”) to Agent Skills. Authors vary in the granularity, normative force, life cycle management, and conformance criteria they use for Agent Skills. A shared Skill Description structure makes results more consistent and supports Skill deployment, Tailoring, improvement, and Assessment. Name, Purpose, and Outcomes establish shared reference points for Skill execution and Assessment (PF 1.2). This specification therefore establishes common rules for Skill description, life cycle management, representation, and conformance.

This specification treats an Agent Skill as a Process Description by default and applies the PF design principles throughout the Skill life cycle. It also permits Agent Skills to represent Process Models, Process Reference Models, and Process Views without changing the meanings of those PF constructs.

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

b) A Process Reference Model defining the three Processes that constitute the ALPS life cycle and their constituent Activities and Tasks (the ALPS Reference Model; Clause 7).

c) Rules for execution structures, interfaces, exchanges, and Process Views used to apply multiple Processes in combination (Clause 8).

d) The declaration and handling of Controls, Constraints, and Enablers applicable to Processes and Agent Skill representations (Clause 9), and the application of Entry/Exit Criteria, Decision Gates, reviews, and audits (Clause 10).

e) Rules for Tailoring and Process Instantiation (Clause 11), criteria for claims of Conformance to this specification and to Processes or representations, and treatment of Capability (Clause 12).

f) The logical composition and integrity of a Skill Package comprising an authoritative Agent Skill representation and accompanying resources that support understanding or applying the represented PF construct (5.7).

g) Rules for representing a Process, Process Model, Process Reference Model, or Process View through an Agent Skill and for resolving references among those representations (5.1, 5.6, and 8.3).

### 1.2 Matters Not Specified by This Specification

This specification does not establish:

a) A concrete implementation form for a Skill Package beyond the minimum representation metadata and logical references specified in 5.1 and 5.6. Other file formats, metadata formats, physical storage structures, distribution mechanisms, and toolchains are outside the scope of this specification. However, 5.7 applies to the logical composition and integrity of the authoritative Agent Skill representation and accompanying resources.

b) A particular Agent implementation, model, execution environment, or vendor.

c) Details of technical information-security and safety measures. Requirements arising from such measures are handled as Controls or Constraints within the framework of this specification (Clause 9).

d) The content of the individual business domains described by Agent Skill representations.

### 1.3 Intended Users

This specification is intended for authors who draft Agent Skill representations, managers of those representations, providers and operators of Agents that use them, and assessors of Conformance of a representation or Process execution.

## 2. Normative Reference and Precedence

The following document is indispensable for application of this specification:

- **Process Framework** (`process-framework.md`). It is abbreviated as “PF” in the text and referenced by clause number, as in “PF 4.3.”

If this specification conflicts with the PF, the PF takes precedence. This specification must not relax a PF requirement or permit an action that the PF prohibits. The specialization of PF constructs for Agent Skills is given in 5.8.

## 3. Terms and Definitions

Terms defined or used in the PF are used with the meanings given in the PF. In addition, the following terms are defined.

**3.1 Agent**
An executing entity capable of performing Activities and Tasks under a stated Purpose, with some autonomy in observing its environment, making judgments, and acting. This includes software systems operating under human direction or supervision.

**3.2 Agent Skill (Skill)**
A unit that an Agent can discover and load. By default, it contains a reusable Process Description and represents a Process. As specified in 5.1, it may instead represent a Process Model, Process Reference Model, or Process View. Accompanying resources may be included when needed. It is referred to simply as a “Skill” in this specification.

**3.3 Skill Description**
The authoritative Process Description that constitutes the content of an Agent Skill representing a Process. It has Name, Purpose, and Outcomes as mandatory elements and can include optional elements and reference information (see Clause 6).

**3.4 Discovery Layer and Execution Layer**
ALPS-specific functional presentation layers through which a Skill Description is made available to an Agent. The discovery layer presents the Name and concise reference information used to discover the Skill and determine its applicability before the complete Skill Description is loaded. The execution layer presents the authoritative Process Description elements and reference information used to execute and assess the Skill.

These layers do not add Process Description elements and do not require a particular physical separation, file format, or storage structure.

**3.5 ALPS Reference Model**
The Process Reference Model represented by `alps-reference-model`, which defines the Define ALPS, Apply ALPS, and Manage ALPS Processes through their respective Names, Purposes, and Outcomes and places their relationships in an explicit structure. Clause 7 specifies the same reference Processes and their Activities and Tasks. The model can be used as a frame of reference for assessment and improvement of ALPS representations and their application.

**3.6 Invocation**
Determining that Entry Criteria are satisfied and beginning execution of a Process Instance through a selected Agent Skill representing a Process.

**3.7 Skill Asset**
An Agent Skill or Skill Package that has been adopted and placed under management.

**3.8 Skill Discovery Description**
Concise reference information placed in the ALPS-specific discovery layer that an Agent uses to discover a Skill and determine its applicability before loading the complete Skill Description. It states what the Process does, when the Skill is used, and the information needed to determine applicability.

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

An Agent Skill describes a Process by default. When an Agent Skill represents a Process, its authoritative content must be a Process Description conforming to the PF. This is the base ALPS case and requires no explicit asset-kind declaration. A Process representation may explicitly declare `metadata.alps.kind: process`; omission has the same meaning.

A Skill Description can describe a general Process or, when explicitly scoped to a particular context, a Process Instance. A description of a Process Instance can specify the required capabilities, resources, Inputs, Outputs, Constraints, Controls, and time (PF 1.1).

ALPS also permits an Agent Skill to represent a Process Model, Process Reference Model, or Process View. An Agent Skill representing one of these constructs must declare `metadata.alps.kind` in its `SKILL.md` frontmatter as one of the following values:

- `process-model`;
- `process-reference-model`; or
- `process-view`.

The `skills/` directory and `SKILL.md` are Agent Skill packaging and discovery conventions. They do not change the meaning of the represented PF construct and do not make a Process Model, Process Reference Model, or Process View into a Process.

Agent Skill activation means that an Agent selects and loads an Agent Skill representation. Process Invocation means that execution of a Process Instance begins. Only an Agent Skill representing a Process directly represents an invokable Process. Activating a Process Model, Process Reference Model, or Process View does not itself begin a Process Instance.

### 5.2 Dual Nature of a Process Skill: Process Description and Enabler

An Agent Skill representing a Process is a Process Description in its authoritative content and functions as an Enabler for the Process that uses it.

Skills, Agents, and tools must be treated as Enablers, not as Inputs (PF 4.1).

### 5.3 Non-Prescription of Performers

A Skill Description must not prescribe the structure of the performer or allocation of Tasks. Capabilities or conditions needed for execution should be stated as Enablers or Constraints without allocating Tasks (PF 3.2).

### 5.4 Skill Boundary and Granularity

Skill boundaries are typically established from primary Outputs and Outcomes rather than from intermediate Outputs of Activities (PF 3.1). Within a Skill representing a Process, strong relationships are maintained among Outcomes, Activities, and Tasks, while dependencies on other Processes are reduced as far as practicable.

A significant Activity containing many Tasks may be described as a separate Process Skill with its own Purpose and Outcomes (PF 3.1).

When the definition, maintenance, assessment, or change handling of an information item spanning multiple Processes has an independent Purpose and Outcomes and mutually cohesive Activities, and can be bounded as one Process, it may be described as a separate Process Skill. By contrast, when no independent Process boundary is established and relationships among existing Processes are presented as a cross-cutting concern, it can be represented as a Process View (8.3).

### 5.5 Functional Layers and Progressive Disclosure

PF 1.3 permits a Process Description to present information in layers for readers with different needs. For Agent Skills representing Processes, ALPS defines a discovery layer and an execution layer as functional presentation layers for progressive disclosure. The names and functions of these layers are specific to ALPS and are not PF constructs.

A Skill Description claiming Description Conformance must provide both layers and make their functions distinguishable. The layers may be represented together or separately, provided that one authoritative Skill Description remains identifiable and mandatory references are resolvable.

a) The **discovery layer** must present the Name and Skill Discovery Description. The Skill Discovery Description must state what the Process does, when the Skill is used, and the information needed to determine applicability.

b) The **execution layer** must present or provide access to the complete Skill Description used for execution and Assessment. It includes Name, Purpose, and Outcomes, together with any optional elements and reference information included under 6.1.

c) Matters that cut across multiple Processes should be treated separately from an individual Process Skill's execution layer. Common Controls and Enablers may be declared as Framework-level elements.

NOTE: These functional layers support progressive disclosure without requiring two files, two sections, or another particular physical structure.

### 5.6 Process Models, Process Reference Models, and Life Cycle Models

Process Models, Process Reference Models, and life cycle models are interpreted with the meanings established by the PF.

A Process Model represented through an Agent Skill identifies a set of related Processes and their relationships. Each Process may identify the Agent Skill that supplies its authoritative Process Description. A Process Model does not need to repeat each Process Purpose and Outcomes.

A Process Reference Model represented through an Agent Skill must identify its Processes by Name, Purpose, and Outcomes and place their relationships in an explicit structure. For every referenced Process Skill, the Process Name must identify the same Process, the Purpose in the Process Reference Model must equal the Purpose in the authoritative Process Description, and the Outcomes in the Process Reference Model must equal the Outcomes in the authoritative Process Description. A mismatch makes the representation invalid; neither representation silently overrides the other.

A Process Model, Process Reference Model, or Process View refers to an Agent Skill by logical package identity and Skill name rather than by repository-relative file path. The canonical form is:

```text
skill:<package-id>#<skill-name>
```

Within the same package, the short form `skill:#<skill-name>` may be used. A resolver must resolve the short form within the containing package. When a full reference is needed outside that package scope, the resolver must normalize it using the package identity supplied by the applicable package binding. ALPS does not require GitHub to be the package identity authority.

A subset of Processes can be selected from a Process Model according to Purpose. The Skills that describe the selected Processes can then be applied singly or in combination. Selection and timing need continual review when the subject or context of application changes (PF 5.1 and 5.2).

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

As reference information placed in the ALPS-specific discovery layer, a Skill Discovery Description must state concisely what the Process does, when the Skill is used, and the information needed to determine applicability. It must be consistent with the authoritative Name, Purpose, Outcomes, scope, Entry Criteria, and Constraints available through the execution layer and must not replace those elements or alter their normative meanings.

The Skill Discovery Description of a Skill claiming Description Conformance to this specification must end with a short ALPS conformance marker in the language of the description. The marker must be exactly `ALPS-conformant.` in English and `ALPS準拠。` in Japanese. This marker is a standardized shorthand claim whose subject is the containing Skill Description and whose criteria are Description Conformance under 12.1 a); it does not assert Reference Process Conformance or Execution Conformance.

## 7. Skill Life Cycle and ALPS Reference Model

### 7.1 Skill Life Cycle Model

The ALPS life cycle concerns the definition, application, management, evolution, and retirement of ALPS representations and the Processes they enable. This specification establishes a reference life cycle model comprising the following Stages:

a) **Concept Stage** — Needs for Process knowledge or other ALPS representations are identified and classified.

b) **Definition Stage** — Authoritative Process Descriptions, Process Models, Process Reference Models, and Process Views are defined and verified.

c) **Operation Stage** — Applicable representations are activated, Processes are resolved and invoked, and Process compositions are executed.

d) **Evolution Stage** — Representations and Process execution are assessed, tailored, changed, and improved.

e) **Retirement Stage** — Representations that have become unnecessary, unsafe, misleading, or superseded are withdrawn from active use under management.

The order shown does not prescribe execution order. Processes and Activities can span multiple Stages and can be applied iteratively, recursively, or concurrently (PF 5.2, Clause 8).

### 7.2 Composition and Interpretation of the Reference Model

The ALPS Reference Model comprises the following three Processes. Each Process is defined by its Name, Purpose, and Outcomes and comprises three Activities (PF 1.1 and 5.1). The packaged Process Reference Model `alps-reference-model` must retain the same Name, Purpose, and Outcomes as the authoritative Process Descriptions identified here.

| Process | Activities |
|---|---|
| Define ALPS | Representation Need Identification / Representation Design / Representation Verification |
| Apply ALPS | Representation Selection and Process Resolution / Process Invocation and Execution / Process Composition and Handoffs |
| Manage ALPS | Representation Asset Management / Tailoring and Formal Adoption / Representation and Process Assessment & Improvement |

Interpret the Reference Model as follows:

a) The three Processes are general Processes and do not require a particular method, tool, or execution sequence (6.2 c)).

b) The order in which Activities and Tasks are presented does not prescribe their execution order. The normative attribute of each Task is expressed through the normative language in 4.1.

c) Agent Skill activation and Process Invocation are distinct. Process Models, Process Reference Models, and Process Views can guide selection and composition without themselves being invoked as Processes.

d) Representative Inputs/Outputs do not prescribe the only method, and exchanges between Activities do not alter Process boundaries (PF 4.2).

e) When Conformance to Outcomes is selected, Activities and Tasks are treated as guidance. When Conformance to Tasks is selected, Outcomes are treated as guidance (see 12.2).

f) Subsets of Processes, Activities, and Tasks can be selected according to Purpose. Changes to a Process are handled as Tailoring or controlled redefinition when necessary (PF 3.2 and 5.1, Clause 11).

Representative exchanges among the three Processes are shown below. This table does not prescribe a fixed execution sequence.

| Provider Process | Representative exchange item | Recipient Process |
|---|---|---|
| Define ALPS | Verified authoritative ALPS representation and verification evidence | Manage ALPS |
| Manage ALPS | Managed representations, status, Tailoring decisions, and application conditions | Apply ALPS |
| Apply ALPS | Selection rationale, execution evidence, Outcome evidence, handoffs, and lessons | Manage ALPS |
| Manage ALPS | Redefinition, reverification, or formal-adoption request | Define ALPS |

### 7.3 Define ALPS

**Purpose**: This Process establishes an assessable and usable ALPS representation that satisfies an identified need while preserving the semantics of the represented Process Framework construct.

**Outcomes**: Success of this Process establishes the following conditions:

a) The need for the ALPS representation and the intended contexts of use are identified.

b) The represented Process Framework construct, Purpose, boundary, and required level of detail are aligned with the selected need.

c) The authoritative representation satisfies the applicable Process Framework and ALPS requirements for its representation kind.

d) References, relationships, provenance, and exchanges required by the representation are traceable and resolvable.

e) A Process Description has demonstrated Outcome achievability in representative contexts, or a non-Process representation has demonstrated semantic consistency and applicability to its intended concern.

f) A decision on adoption can be made from verification evidence that includes defects, assumptions, and limitations.

| Activity | Outcomes primarily supported |
|---|---|
| Representation Need Identification | a) and b) |
| Representation Design | b), c), and d) |
| Representation Verification | c), d), e), and f) |

**Activities and Tasks**:

#### 7.3.1 Representation Need Identification

This Activity identifies a need and determines whether it should be represented as a Process, Process Model, Process Reference Model, or Process View.

a) Candidate needs should be collected from recurring work, composition needs, cross-cutting concerns, lessons learned, gaps, and failure cases.

b) Intended users, stakeholders, and contexts of use must be identified.

c) Existing ALPS representations should be investigated for duplication, adjacency, reuse, or gaps.

d) The represented Process Framework construct must be selected according to the meaning of the need rather than the preferred storage or presentation format.

e) A Process must be selected when an independent Process boundary with Purpose and Outcomes is established.

f) A Process Model should be selected when the need is to organize related Processes and their relationships.

g) A Process Reference Model should be selected when the need is to define individual Processes by Name, Purpose, and Outcomes and place them in an explicit relationship structure.

h) A Process View should be selected when the need is to organize Activities and Tasks from multiple source Processes around a particular concern or Purpose without creating an independent Process boundary.

i) Expected benefits, risks, and costs should be evaluated.

j) The rationale for selection or deferral should be recorded.

#### 7.3.2 Representation Design

This Activity determines the structure and content required by the selected representation kind.

a) The authoritative representation must preserve the meaning of the represented Process Framework construct.

b) An Agent Skill representing a Process must contain a Process Description with Name, Purpose, and Outcomes.

c) The Process Description must apply the applicable rules in Clause 6 of ALPS.

d) A Process Description must distinguish discovery-layer and execution-layer information. Their physical separation is not required.

e) Each Task in a Process Description must express an individual action supporting one or more Outcomes so that its object and operation are distinguishable.

f) Each normative statement in a Process Description must have a distinguishable normative attribute.

g) A Process Model must identify its Processes and their relationships.

h) A Process Model may identify the Agent Skills that provide the authoritative Process Descriptions.

i) A Process Reference Model must identify each included Process by Name, Purpose, and Outcomes, identify their relationships, and identify the corresponding Process Skill where one is supplied.

j) A Process View must state Name, Purpose, and Outcomes; identify any source Processes it references; maintain provenance and Traceability for referenced source Activities and Tasks; permit Activities and Tasks to be described within the View where needed for its concern or Purpose; and provide application guidance.

k) Logical references among Agent Skill representations must use the canonical Skill-reference rules in ALPS rather than repository-relative paths as identity.

l) Reference information must not alter the meaning or normative force of the authoritative representation.

m) When a Skill Package includes accompanying resources, their role and conditions of use must be identifiable.

n) Relationships and handoffs that affect another representation or Process should be made explicit where needed.

#### 7.3.3 Representation Verification

This Activity verifies the representation against its kind-specific requirements and its intended use.

a) The authoritative representation must be reviewed against the Process Framework and the applicable ALPS requirements.

b) The declared or default representation kind must match the construct actually represented.

c) Mandatory references must resolve to the intended targets.

d) A Process Description must be checked for Name, Purpose, Outcomes, element classification, normative attributes, non-prescription of implementation, and consistency between discovery and execution information.

e) The achievability of Process Outcomes should be evaluated through representative trials when the representation is a Process Description.

f) A Process Model must be checked for identifiable Processes and coherent relationships.

g) A Process Reference Model must be checked for the required Name, Purpose, and Outcomes of each Process and for equality of that semantic center with each referenced authoritative Process Description.

h) A Process View must be checked for source provenance and Traceability where source elements are referenced, preservation of source Process meaning, relationships or handoffs, application guidance, and separation of View-local descriptions from changes to source Processes.

i) The review should include a perspective independent of the author when the quality risk warrants it.

j) Detected defects, assumptions, limitations, and unresolved references must be recorded.

k) Defect treatment should be completed or explicitly dispositioned before an adoption Decision Gate.

l) When a Skill Package is in scope, consistency between the authoritative representation and its accompanying resources must be verified.

**Representative Inputs**: stakeholder expectations, needs and change requests, existing ALPS representations, Process Framework and ALPS requirements, verification criteria, execution evidence when relevant, and representative contexts of use.

**Representative Outputs**: the selected representation need and rationale, a verified authoritative ALPS representation, traceability and reference information, verification results, and defect-treatment records.

### 7.4 Apply ALPS

**Purpose**: This Process selects and activates applicable ALPS representations, resolves the Processes needed for the application situation, and achieves the intended Outcomes through the single or combined application of Process Skills.

**Outcomes**: Success of this Process establishes the following conditions:

a) The needs, conditions, and risks of the application situation are identified.

b) Applicable Process Models, Process Reference Models, Process Views, and Process representations are selected or activated as needed, and candidate Processes are resolved from them.

c) The Process Skills to invoke and the form of application are determined with a rationale.

d) Applicable Controls, Constraints, Tailoring decisions, and Decision Gates are identified before affected actions occur.

e) Process Instances are executed within the declared application scope and applicable Controls, Constraints, and Tailoring decisions.

f) The declared Outcomes of the applied Processes are achieved with observable evidence.

g) Required handoffs and the completeness and consistency of the Process composition are established.

| Activity | Outcomes primarily supported |
|---|---|
| Representation Selection and Process Resolution | a), b), and c) |
| Process Invocation and Execution | c), d), e), and f) |
| Process Composition and Handoffs | f) and g) |

**Activities and Tasks**:

#### 7.4.1 Representation Selection and Process Resolution

This Activity uses discovery information and ALPS representations to determine the Processes that fit the application situation.

a) The needs, conditions, risks, and applicable Constraints of the application situation must be identified.

b) Candidate Agent Skills should be discovered from their discovery information without assuming that every discovered Skill represents an invokable Process.

c) The representation kind must be determined before treating an Agent Skill as an Invocation candidate.

d) A Process Model may be activated to identify related Processes and their relationships.

e) A Process Reference Model may be activated to compare candidate Processes by Name, Purpose, Outcomes, and relationships.

f) A Process View may be activated to apply a cross-cutting concern and identify the source Processes and the Activities and Tasks relevant to the application situation.

g) Activating a Process Model, Process Reference Model, or Process View must not itself be treated as Process Invocation.

h) Canonical Skill references in the selected representation must be resolved before a referenced Process Skill is used.

i) Only an Agent Skill representing a Process may be selected for direct Process Invocation.

j) Candidate Process Purposes and Outcomes should be compared with the needs and target Outcomes of the application situation.

k) If no suitable representation or Process exists, the unmet need may be handed to Define ALPS.

l) The uncertainty and risks associated with the selection decision must be evaluated.

m) The rationale for the selection decision should be recorded.

#### 7.4.2 Process Invocation and Execution

This Activity invokes selected Process Skills and evaluates their execution.

a) The selected Agent Skill must represent a Process before Invocation begins.

b) The Process Entry Criteria must be satisfied before the Process is invoked.

c) If the Process Entry Criteria are not satisfied, Invocation must be deferred or the unmet conditions must be resolved first.

d) Required Inputs and Enablers should be confirmed as available.

e) Applicable Controls, Constraints, Tailoring decisions, and required Decision Gates must be identified.

f) When the selected Conformance basis includes Full Conformance to Tasks or a Tailored Conformance scope that retains Activity or Task requirements, the applicable Activities and Tasks in the authoritative Process Description must be applied according to their normative attributes.

g) When the selected Conformance basis makes a requirement Task applicable, that Task must not be omitted unless it has been legitimately changed through managed Tailoring. When only Full Conformance to Outcomes is selected, Activities and Tasks are guidance rather than mandatory execution conditions.

h) An execution sequence not explicitly established by a Constraint must not be assumed.

i) A required Decision Gate must be passed before the governed irreversible or high-impact action occurs.

j) Process Exit Criteria must be assessed before completion is declared.

k) Outcome achievement should be assessed from observable evidence.

l) Significant execution decisions, assumptions, deviations, and unresolved matters should be recorded.

m) Execution evidence and lessons may be handed to Manage ALPS for assessment and improvement.

#### 7.4.3 Process Composition and Handoffs

This Activity combines Processes and manages interfaces, handoffs, and composition integrity.

a) The target set of Outcomes for the composition must be identified.

b) The identity and provenance of each Process representation used in the composition should be recorded.

c) The mapping from each provider Output to each recipient Input must be explicit where the exchange affects successful application.

d) Previously undefined handoffs may be introduced only through an applicable controlled change or Tailoring decision.

e) When Iteration or Recursion changes an Output, affected Inputs and applicable criteria should be reevaluated.

f) Integration must establish completeness within the selected scope and consistency across Process relationships.

g) If a Process View is active, referenced source elements retain their source meaning. View-specific or modified Activities and Tasks must not silently alter Source Process Conformance.

h) Outcome achievement for the composition as a whole should be assessed.

i) When the same information item is changed by multiple Processes, its integrity, state, and change handling must be defined in proportion to quality risk.

**Representative Inputs**: application needs and conditions, target Outcomes, discovery information, Process Models, Process Reference Models, Process Views, Process Descriptions, declared Inputs, Framework-level declarations, Tailoring decisions, and execution requests.

**Representative Outputs**: activated representations, resolved Process selections and rationale, Process Outputs, composition definitions, handoff records, Outcome evidence, execution decisions, and unresolved needs or change requests.

### 7.5 Manage ALPS

**Purpose**: This Process governs ALPS representations and their application and maintains the continual availability of suitable, coherent, and trustworthy ALPS assets.

**Outcomes**: Success of this Process establishes the following conditions:

a) Policies and guidance for managing, deploying, Tailoring, and adopting ALPS representations are established.

b) Adopted ALPS representations are discoverable with their identity, kind, status, version, and applicable conditions under management.

c) Changes and retirement are controlled with their impacts, reference integrity, and affected users or representations identified.

d) Tailoring, formal adoption, and other management decisions are traceable to applicable Controls, Constraints, scope, evidence, and rationale.

e) Process execution is assessed using criteria appropriate to its declared subject, including Conformance, performance, and effectiveness where relevant.

f) Managed ALPS representations are assessed using criteria appropriate to their kind, including semantic consistency, description Conformance, relationship coherence, and applicability where relevant.

g) Improvement opportunities are prioritized from execution evidence, lessons learned, representation assessments, and change impacts.

h) Decided improvements are implemented through controlled change.

i) Representations affected by implemented improvements are reverified.

j) Resulting management states are updated.

| Activity | Outcomes primarily supported |
|---|---|
| Representation Asset Management | a), b), c), h), i), and j) |
| Tailoring and Formal Adoption | a) and d) |
| Representation and Process Assessment & Improvement | e), f), g), h), i), and j) |

**Activities and Tasks**:

#### 7.5.1 Representation Asset Management

This Activity manages adoption, discoverability, configuration, controlled change, communication, reference integrity, and retirement.

a) Means for managing and deploying ALPS representations, together with applicable Tailoring and adoption guidance, should be established.

b) Framework-level Controls and Enablers must be declared together with scope, exceptions, and whether Tailoring is permitted.

c) Verification evidence from Define ALPS should be confirmed before an authoritative representation is adopted.

d) An adopted representation must retain an identifiable representation kind, authoritative source, management status, and applicable conditions.

e) Canonical references affected by adoption, replacement, relocation, version change, or retirement must be identified and their resolvability preserved or deliberately changed through a controlled decision.

f) Changes to a Process Reference Model must identify affected Process semantic centers and referenced Process Descriptions.

g) Changes to a Process Model must identify affected Process membership and relationships.

h) Changes to a Process View must identify affected Source Processes, referenced Activities and Tasks and their Traceability, and application guidance.

i) Changes to a Process Description must identify affected Process Models, Process Reference Models, Process Views, and consumers where applicable.

j) Changes with material impact should be communicated to affected users and representations.

k) A representation whose need no longer exists, that has become unsafe or misleading, or that has been superseded should be retired under a controlled decision.

l) Retired representations may be retained for traceability or reference when permitted by applicable Controls and Constraints.

#### 7.5.2 Tailoring and Formal Adoption

This Activity controls context-specific changes and determines when View content or Process application requires a change to a managed Process or Model.

a) Application risks, requirements, complexity, capabilities, resources, stakeholder expectations, and relevant standards must be identified.

b) Each proposed change must be distinguished as context-specific Tailoring or an authoritative redefinition.

c) Tailoring must comply with applicable Controls and Constraints.

d) The Tailoring scope must be stated.

e) Tailoring assumptions should be recorded.

f) Tailoring decision criteria should be recorded.

g) Input from materially affected parties must be obtained when required by applicable Controls or quality risk.

h) The rationale for each Tailoring decision should be recorded.

i) Changes to Process Outcomes, Activities, Tasks, Inputs, Outputs, Controls, Constraints, or Enablers must be traceable when they affect the declared Conformance basis.

j) A View-specific or modified Activity or Task must not contribute to Source Process Conformance merely because it appears in a Process View.

k) A change to an applicable Source Process for a particular application must be handled through managed Tailoring.

l) An authoritative semantic change to an ALPS representation must be handed to Define ALPS for controlled redefinition.

m) Formal adoption of a changed semantic element must occur only after controlled redefinition and verification.

n) Tailoring effectiveness should be reviewed during application.

o) Tailoring should be revised when conditions change.

p) The rigor of application and evidence should be proportional to risk.

#### 7.5.3 Representation and Process Assessment & Improvement

This Activity assesses representations and Process execution and connects the results to controlled improvement.

a) Assessment criteria must be selected according to the representation kind and declared subject.

b) A Process representation may be assessed for Description Conformance, Process execution Conformance, Outcome achievement, performance, and effectiveness as applicable.

c) A Process Model should be assessed for Process coverage, relationship coherence, resolvability, and applicability to its intended Purpose.

d) A Process Reference Model should be assessed for Process identity, Name/Purpose/Outcomes consistency, relationship coherence, resolvability, and suitability as a frame of reference.

e) A Process View should be assessed for Purpose and Outcomes, Source Process provenance and Traceability where source elements are referenced, preservation of source meaning, handoffs, application guidance, and usefulness for its intended concern.

f) Assessment of Process View Outcomes must remain distinct from Source Process Outcome Conformance.

g) Lessons learned and execution evidence should be collected throughout application and at useful review points.

h) Strengths, weaknesses, defects, gaps, duplication, and inconsistencies should be identified.

i) Improvement opportunities should be prioritized according to evidence, benefit, cost, risk, and impact.

j) A decided change to an authoritative representation must be handed to Define ALPS for controlled redefinition and verification.

k) Rework or inconsistency arising at references, relationships, or handoffs may be used as an improvement signal.

l) Decided improvements must be implemented through the applicable controlled change.

m) Representations affected by an implemented improvement must be reverified.

n) Management state must be updated after decided improvements are implemented and verified.

**Representative Inputs**: verified ALPS representations, adoption and change requests, application context, Tailoring guidance, affected-party input, execution and decision records, lessons learned, measurement results, representation-assessment results, and reference-resolution information.

**Representative Outputs**: managed ALPS representations, adoption and retirement decisions, Tailoring and formal-adoption decisions, change-impact and reference-integrity records, assessment results, prioritized improvements, redefinition or reverification requests, and updated management states.

## 8. Skill Execution Structures and Relationships

### 8.1 Concurrency, Iteration, Recursion, and Integration

Processes can be executed in structures other than a serial sequence. The following execution structures can be applied (PF 6.1):

a) **Concurrency** — Applying two or more Processes in parallel at the same structural level.

b) **Iteration** — Repeatedly applying the same Process or set of Processes at the same level. It should continue as far as needed to resolve problems and refine Outputs.

c) **Recursion** — Repeatedly applying the same Process or set of Processes at successive structural levels of the subject of application. The Output of a Process applied at one structural level can become an Input to a Process applied at the next structural level.

d) **Integration** — Ensuring completeness within a level and consistency across levels.

These relationships do not prescribe execution order. The actual flow is determined through Tailoring, with consideration for the effects of Output changes on Inputs to other Processes (PF 6.2).

### 8.2 Interfaces, Exchanges, and Traceability Among Skills

An interface and exchange between Process Skills is treated as a mapping from a provider Process's Output to a recipient Process's Input. An interface is not an independent Skill element, and an undefined exchange can be added through Tailoring (PF 4.4).

When multiple Processes are composed for application, the mapping from each provider Output to each recipient Input must be made explicit (7.4.3 c)).

When Processes are applied concurrently, iteratively, or recursively, shared or interdependent information items and the reference or change relationships among them should be identified to the extent needed for application. When the same information item is changed by multiple Processes, handling of its integrity, status, and change must be established according to quality risk.

When a change to an Output affects an Input to another Process, the affected Process and mapping should be identified and necessary reassessment performed.

When Output quality affects a subsequent Outcome or stakeholder acceptance, the determination conditions and necessary evidence should be related to Entry Criteria, Exit Criteria, a review, or a Decision Gate.

Traceability should cover Outcomes, Activities, Tasks, and information items. These mappings provide a basis for integrity and Process Assessment (PF 4.4).

NOTE: Explicit exchange mappings keep the meaning, scope, state, and quality conditions of an information item from being lost as it passes between Processes.

### 8.3 Process View

A Process View organizes Activities and Tasks spanning multiple Processes around a particular concern or Purpose and explains how those Activities and Tasks are applied (PF 5.3). It is a representation that supports cross-cutting application; it is not a Process merely because it is represented by an Agent Skill.

When an independent Process boundary is established, the subject can be described as a separate Process Skill in accordance with 5.4.

A Process View represented through an Agent Skill must declare `metadata.alps.kind: process-view`. Activating that Agent Skill loads the View representation and does not itself invoke a Process.

a) Every Process View must state its Name, Purpose, and Outcomes.

b) A Process View may reference Activities and Tasks from existing Processes and may describe Activities and Tasks within the View where needed for its concern or Purpose.

c) A Process View must provide explanation and application guidance sufficient to understand how its Activities and Tasks contribute to the stated Outcomes.

d) When a Process View references an Activity or Task from a source Process, it must identify the source and maintain the provenance and Traceability needed to keep the source relationship clear. References to source Process Skills must use the canonical Skill-reference rules in 5.6 where applicable.

e) Activities and Tasks described within a Process View do not change the source Process merely by appearing in the View. View-specific or modified Activities and Tasks do not by themselves contribute to or alter Source Process Conformance.

f) If the source Process itself is changed for an application, the change must be handled through Tailoring. An authoritative change to the source Process must be handled as Process redefinition through Define ALPS.

g) A Process View may show connections among Processes and the sources of the Processes used in its composition.

**Process View Description Conformance** concerns the View representation itself. It requires the View Purpose, Outcomes, source provenance and Traceability where source elements are referenced, preservation of source meaning, relationships or handoffs, application guidance, and internal consistency.

**Source Process Conformance** remains a claim about the applicable source Process. Referenced source Activities and Tasks contribute according to that source Process Conformance basis. View-specific or modified Activities and Tasks do not affect Source Process Conformance unless the source Process itself is changed through Tailoring or Process redefinition.

Achievement of the Process View Outcomes can be assessed separately. That assessment is distinct from both Process View Description Conformance and Process Outcome Conformance for a source Process.

## 9. Controls, Constraints, and Enablers

### 9.1 Framework-Level Controls and Enablers

Framework-level Controls and Enablers must state their scope, exceptions, and whether Tailoring is permitted (PF 4.5).

Elements common to Processes within the declared scope may be declared once rather than repeated in each Process Skill (PF 4.1 and 4.5).

Information resources that apply in common to multiple Processes can be declared as Framework-level Controls or Enablers according to their function. An item transformed by a Process is treated as an Input or Output. These classifications must be based on the function performed by the information resource in Process execution, not on its form or location.

### 9.2 Skill-Level Controls and Constraints

Controls and Constraints declare conditions or permissible boundaries for Process execution. Controls can arise from applicable laws or regulatory requirements, policies, conformance to voluntary standards, or agreements. Constraints can arise from environmental factors or conditions of application external to the Process (PF 4.1 and 4.5).

A Control or Constraint statement must be classified according to its primary function as specified in 6.3.7.

Controls and Constraints can be described in separate sections of a Skill Description or as conditions associated with other Skill elements. Any temporal relationship needed in a general Process should be declared explicitly as a Constraint (6.2 c)).

### 9.3 Enablers, Capabilities, and Tools

Human or Agent capabilities, tools, and technologies support a Process as Enablers (PF 4.1 and 4.5).

Human and automated resources that execute a Process, including Agents, models, execution environments, and tools, are not treated as Process Inputs (PF 4.1 and 4.2). When described as elements, they must be described as Enablers.

NOTE: Treating Agents, models, tools, and execution environments as Enablers keeps the items a Process transforms distinct from the capability that performs the transformation.

## 10. Entry/Exit Criteria, Decision Gates, and Reviews

### 10.1 Entry Criteria and Exit Criteria

a) Entry Criteria state conditions under which a Process Skill can be invoked. A summary should be placed in the discovery layer as reference information for determining applicability (5.5).

b) Exit Criteria state conditions under which a Process Instance can be completed. Exit Criteria should be related to determining achievement of the Outcomes.

### 10.2 Decision Gate

A Decision Gate is not a component of a Skill Description; it is treated as a decision mechanism that controls Process application (PF 8.1).

a) A Decision Gate uses Decision Criteria based on the Purpose, Outcomes, conditions of application, and risk to determine whether a state transition can occur (PF 8.1).

b) The frequency, scope, and formality of Decision Gates can be adjusted to the context of application.

c) The decision, its rationale, and its assumptions should be recorded (PF 8.1).

d) A decision to pass should be based on evidence, and Decision Criteria should be reevaluated as the context of application changes.

NOTE: Confirmation and human escalation before an irreversible or high-impact action are forms of applying a Decision Gate. The Gate gives the application a controlled point at which such an external effect can be held, changed, or stopped before it occurs. Appendix D describes how human oversight can be composed from existing elements.

### 10.3 Reviews and Audits

A review evaluates Process performance, Outputs, and achievement of Outcomes using agreed criteria. An audit includes a detailed review of evidence demonstrating conformance to the Process, Outputs, and requirements and confirms that mandatory attributes and applicable requirements are satisfied (PF 8.2).

When an Output is transferred to another Process or a stakeholder, it should be evaluated against applicable criteria to determine whether the Output can be used as the intended Input or result.

Reviews and audits should be tailored to the needs and risks of the subject of application, and their Entry Criteria, Exit Criteria, and responses to problems should be established (PF 8.2).

## 11. Tailoring and Process Instantiation

### 11.1 Discipline of Tailoring

Tailoring must be performed in accordance with Tailoring and Formal Adoption in Manage ALPS (7.5.2), whose requirements are prerequisites for Tailored Conformance (12.3).

NOTE: Requiring Tailoring to pass through Manage ALPS prevents unrecorded changes to a Process's meaning, normative force, or applicability and keeps context-specific changes distinct from authoritative redefinition.

### 11.2 Levels of Tailoring

Common-level Tailoring adapts an external standard, including this specification, to needs shared across an intended application domain. Individual-level Tailoring adapts the resulting common Process to the needs of a particular subject of application (PF 7.2).

### 11.3 Process Instantiation

When justified by quality risk, a Process Instance can be described in greater detail, and instance-specific success criteria, Activities, and Tasks can be identified (PF 7.4).

## 12. Conformance, Capability, and Assessment

### 12.1 Subjects of Conformance

Conformance relating to this specification can be claimed for the following subjects. Every claim must identify the subject and the selected criteria.

a) **Description Conformance** — A Skill Description satisfies the applicable requirements of Clauses 4 through 6. When a Skill Package containing a Process representation is included in the subject of conformance, the Package also satisfies the applicable requirements of 5.7.

b) **Process Model Description Conformance** — An Agent Skill representation of a Process Model satisfies the applicable representation, Process-reference, relationship, resolvability, and internal-consistency requirements of 5.1, 5.6, and 5.7.

c) **Process Reference Model Description Conformance** — An Agent Skill representation of a Process Reference Model satisfies the applicable representation, Process identity, Name/Purpose/Outcomes equality, relationship, resolvability, and internal-consistency requirements of 5.1, 5.6, and 5.7.

d) **Process View Description Conformance** — An Agent Skill representation of a Process View satisfies the applicable representation, source-provenance and Traceability, source-meaning-preservation, relationship, application-guidance, and internal-consistency requirements of 5.1, 5.6, and 8.3.

e) **Reference Process Conformance** — For Define ALPS, Apply ALPS, or Manage ALPS, Conformance under 12.2 or 12.3 is established for the declared Process in Clause 7.

f) **Execution Conformance** — Execution of a Process Instance through a Process Skill establishes Conformance under 12.2 or 12.3 to the Process described by that Skill.

### 12.2 Full Conformance

Full Conformance to a Process must be claimed as Conformance to Outcomes, Tasks, or both, and the selected criteria must be stated. When both are selected, both must be satisfied (PF 8.3).

a) **Full Conformance to Outcomes** requires achievement of all mandatory Outcomes in the declared Process Skill or Reference Process. This approach provides greater freedom in how the conformant Process is implemented; Activities and Tasks are treated as guidance.

b) **Full Conformance to Tasks** requires satisfaction of every requirement stated with **must** or **must not** by an Activity or Task in the declared Process Skill or Reference Process. Recommendations, permissible actions, and typical actions are not, solely by virtue of those attributes, mandatory conditions for Full Conformance to Tasks. When this approach is selected, Outcomes are treated as guidance.

For Reference Process Conformance, the units for which Outcome Conformance can be claimed are Define ALPS, Apply ALPS, and Manage ALPS. Independent Outcome Conformance must not be claimed for an individual constituent Activity.

Assessment of Process View Outcomes is separate from Process Outcome Conformance for a source Process.

### 12.3 Tailored Conformance

Tailored Conformance may be claimed for a Process Skill or Reference Process that does not meet Full Conformance. The claim must declare the Process tailored in accordance with Tailoring and Formal Adoption in Manage ALPS (7.5.2) and its scope of application. It must also demonstrate satisfaction of every Outcome and Activity/Task requirement remaining within that scope (PF 8.3 and 8.4).

When only some Activities constituting a Reference Process are applied, the application must not be claimed as independent Process Conformance to those Activities. It must be declared as a tailored scope of the parent Process, and the Tailored Conformance criteria must be used.

### 12.4 Capability and Assessment

Capability is treated as a dimension of assessment separate from Conformance. Specifically performing Activities and Tasks can require a higher Capability level than achieving Outcomes alone. However, Capability level alone does not establish Conformance, nor does Conformance alone determine Capability level (PF 8.5).

Process Outcomes and the Purposes and Outcomes of the three Reference Processes can be used for Process Assessment and effectiveness assessment (PF 8.5, 7.5.3).

Assessment of a Skill Package can evaluate the existence of the authoritative Agent Skill representation, resolvability of mandatory references, consistency between the authoritative representation and accompanying resources, roles and conditions of use of accompanying resources, and reverification after changes (5.7, 7.3.3, 7.5.1).

Assessment of a Process Model, Process Reference Model, or Process View is not Process execution Conformance. Manage ALPS applies representation-kind-appropriate assessment criteria as specified in 7.5.3.

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

NOTE 1: `description` states what the Process does and when the Skill is used, making that information available before selection (3.8).

NOTE 2: “Consolidated meeting minutes” is an Output, not an Outcome (6.3.3). The Constraint declares the permitted transfer condition, while the corresponding transfer action is stated as a Task (6.3.7, 9.2). Enablers are not Inputs (9.3), and this Process Description does not prescribe a performer (5.3).

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
| 3.2 | Relationship with performers; selection of subsets | 5.3, 7.2 f) |
| 4.1–4.2 | Functional classification and transformation | 5.2, 5.8, 6.3.6–6.3.7, 7.2 d), Clause 9 |
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

[AGENTS.md](https://agents.md/) is an open format for providing repository-scoped context and instructions to coding agents. An `AGENTS.md` file can direct agents to discover, select, apply, and manage ALPS-conformant Agent Skill representations and can state repository Controls and Constraints. It is not itself an ALPS representation and does not alter the meaning or normative force of the Process Framework, this specification, or an authoritative Agent Skill representation.

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
- judgments made within Apply ALPS and Manage ALPS.

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

### D.5 Evidence for Process Skills with Non-Deterministic Behavior

The definition of Outcome and the Conformance criteria are unchanged. The following guidance applies existing Representation Verification, Outcome evidence, and risk-based Tailoring; it adds no requirement.

- Where non-determinism matters, a single execution is not treated as sufficient to establish the achievability of Outcomes or a Capability level.
- Representative contexts of use include boundary conditions, abnormal conditions, and novel situations.
- When a unique expected result cannot be defined, acceptance conditions, prohibited conditions, or an evaluation method is defined instead.
- Execution records retain observed variation, the limits of the evidence, and unresolved uncertainty.
- The need for repeated trials or continuous monitoring is decided from quality risk.

Non-determinism and the difficulty of defining a unique expected result can complicate both verification and human oversight.

### D.6 Returning Oversight Results to Manage ALPS

The following are representative information items that Apply ALPS can hand to Representation and Process Assessment & Improvement in Manage ALPS as execution records and lessons learned:

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
