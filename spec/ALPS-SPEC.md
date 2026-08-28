# ALPS — Agent Lifecycle Process Skills Specification

---

## Foreword

ALPS applies the Process Framework (PF) to Agent Skills. It establishes how an Agent Skill represents a Process or another PF construct, how those representations are discovered and related, and how their application, life cycle, and Conformance are governed.

PF remains the authoritative source for general Process semantics. ALPS adds only the rules specific to Agent Skill representations and the ALPS reference life cycle.

---

## Contents

- 1. Scope
- 2. Normative Sources and Precedence
- 3. Terms and Definitions
- 4. Normative Language and Conventions
- 5. Representation Model
- 6. Representation Requirements
- 7. ALPS Life Cycle and Reference Model
- 8. Activation, Invocation, and Composition
- 9. Controls, Constraints, and Enablers
- 10. Entry/Exit Criteria, Decision Gates, and Reviews
- 11. Tailoring, Redefinition, and Instantiation
- 12. Conformance, Capability, and Assessment

---

## 1. Scope

### 1.1 Matters Specified

This specification establishes:

a) how an Agent Skill represents a Process, Process Model, Process Reference Model, or Process View;

b) ALPS-specific discovery and execution layers, logical Skill references, and Skill Package integrity;

c) the ALPS life cycle and the integrity contract between the ALPS Reference Model and the three reference Processes (Define ALPS, Apply ALPS, and Manage ALPS);

d) ALPS-specific rules for activation, Process Invocation, composition, Tailoring, authoritative redefinition, and representation management; and

e) subjects and criteria for Description Conformance for Process and non-Process representations, Reference Process Conformance, and Execution Conformance.

### 1.2 Matters Not Specified

This specification does not establish:

a) a concrete file format, storage layout, distribution mechanism, or toolchain beyond the minimum representation-kind metadata and logical references stated here;

b) a particular Agent implementation, model, execution environment, vendor, performer allocation, or execution method;

c) details of technical information-security and safety measures; the measures themselves are classified by function under PF, while requirements arising from them are handled as applicable Controls or Constraints; or

d) the business-domain content of a represented Process or other PF construct.

### 1.3 Intended Users

This specification is intended for authors and managers of ALPS representations, providers and operators of Agents that use them, and assessors of representations or Process execution.

## 2. Normative Sources and Precedence

### 2.1 Process Framework

The [Process Framework](process-framework.md) is indispensable for applying this specification and is referenced as “PF” followed by a clause number.

If this specification conflicts with PF, PF must take precedence. ALPS must not weaken a PF requirement, permit an action that PF prohibits, change the meaning of a PF construct, or replace it with a different construct.

### 2.2 ALPS Reference Assets

The following logical Skill references identify normative assets released with this specification:

| Asset | Logical reference | Normative role |
|---|---|---|
| ALPS Reference Model | `skill:#alps-reference-model` | Defines the three reference Processes by Name, Purpose, and Outcomes and places their relationships in an explicit structure. |
| Define ALPS | `skill:#define-alps` | Provides the authoritative complete Process Description for Define ALPS. |
| Apply ALPS | `skill:#apply-alps` | Provides the authoritative complete Process Description for Apply ALPS. |
| Manage ALPS | `skill:#manage-alps` | Provides the authoritative complete Process Description for Manage ALPS. |

PF, this specification, and the four assets above form one ALPS Release Package. Its package ID must be `alps`, and its package version must be the single ALPS release version declared by that release. The four assets are distinct Skill Packages within that Logical Package Scope. The ALPS Release Package is not itself a Skill Package; the one-authoritative-representation rule in 5.5 applies separately to each contained Skill Package.

For every same-scope short reference in the table and every same-scope short reference from the ALPS Reference Model to a Reference Process, the Logical Package Scope containing its referring representation is the same-version ALPS Release Package. Before resolution, an applicable Package Binding must bind package ID `alps` and the exact declared package version to one concrete release instance and its four Skill Packages. A resolver must resolve each same-scope short reference to exactly one matching Skill Package in that scope and must not resolve it across package versions.

Repository paths and Host manifests may implement a Package Binding but do not define or change these logical identities.

If a reference asset conflicts with PF or this specification, the asset is nonconforming. If the ALPS Reference Model and a referenced Process Description disagree on Process Name, Purpose, or Outcomes, the Reference Model representation is invalid; neither representation silently overrides the other.

## 3. Terms and Definitions

Terms defined or used in PF retain the meanings given there. ALPS adds the following terms.

**3.1 Agent**

An executing entity capable of performing Activities and Tasks under a stated Purpose, with some autonomy in observing its environment, making judgments, and acting. This includes software systems operating under human direction or supervision.

**3.2 Agent Skill (Skill)**

A unit an Agent can discover and load. By default it contains a reusable Process Description and represents a Process. It may instead represent a Process Model, Process Reference Model, or Process View. It may include accompanying resources.

**3.3 Skill Description**

The authoritative Process Description contained by an Agent Skill representing a Process.

**3.4 Discovery Layer and Execution Layer**

ALPS-specific functional presentation layers. The discovery layer supplies the Name and concise information used to discover a Skill and determine applicability before loading the complete representation. The execution layer supplies the authoritative Process Description used for Process execution and Assessment. These layers add no PF element and require no physical separation, file format, or storage structure.

**3.5 ALPS Reference Model**

The Process Reference Model identified by `skill:#alps-reference-model`.

**3.6 Invocation**

Determining that Entry Criteria are satisfied and beginning execution of a Process Instance through a selected Agent Skill representing that Process.

**3.7 Skill Asset**

An Agent Skill or Skill Package adopted and placed under management.

**3.8 Skill Discovery Description**

Concise reference information in the discovery layer stating what the represented Process does, when the Skill is used, and the information needed to determine applicability.

**3.9 Skill Package**

A unit managed as a whole that contains one authoritative Agent Skill representation and any accompanying resources that support understanding or applying the represented PF construct.

**3.10 Reference Process**

Define ALPS, Apply ALPS, or Manage ALPS as represented by the corresponding normative Process Skill identified in 2.2.

**3.11 Logical Package Scope**

A versioned namespace identified by a package ID and exact package version within which logical Skill references are resolved. It can contain multiple Skill Packages. It is distinct from a Skill Package and from a physical distribution layout.

**3.12 Package Binding**

A mapping that binds a Logical Package Scope's package ID and exact package version to one concrete release instance and its contained Skill Packages in a resolution environment.

**3.13 ALPS Release Package**

The Logical Package Scope whose package ID is `alps` and whose exact package version is the single ALPS release version declared by the release containing this specification. It contains PF, this specification, and the four normative Skill Packages identified in 2.2.

## 4. Normative Language and Conventions

The normative words used in this specification and in Skill Descriptions, and their meanings, are those defined by PF. This specification does not redefine them.

Clauses 1 through 12 are normative. Notes and material explicitly identified as informative are informative and must not alter normative meaning or force.

## 5. Representation Model

### 5.1 Representation Kinds

An Agent Skill represents one PF construct.

| `metadata.alps.kind` | Represented construct | Treatment |
|---|---|---|
| omitted or `process` | Process | Default. The authoritative content is a Skill Description conforming to PF. |
| `process-model` | Process Model | Must identify related Processes and their relationships. |
| `process-reference-model` | Process Reference Model | Must define included Processes by Name, Purpose, and Outcomes and place their relationships in an explicit structure. |
| `process-view` | Process View | Must state Name, Purpose, and Outcomes and provide application guidance for its concern. |

The `skills/` directory, `SKILL.md`, frontmatter, and Host registration are packaging or discovery conventions. They do not change the represented PF construct and do not make a Process Model, Process Reference Model, or Process View into a Process.

Agent Skill activation means selecting and loading a representation. Process Invocation begins a Process Instance. Only a Skill representing a Process directly represents an invokable Process; activating another representation kind does not invoke a Process.

### 5.2 Process Skills and Boundaries

A Skill representing a Process contains the authoritative Process Description and also functions as an Enabler when that Process is applied. The Agent Skill, Agent, model, tools, and execution environment are Enablers rather than Process Inputs.

PF governs Process boundary, granularity, cohesion, and performer independence. In applying those rules:

a) a significant Activity may be represented as a separate Process Skill when an independent Process boundary with Purpose and Outcomes is established;

b) work concerning an information item that spans Processes may be represented as a separate Process Skill when it has an independent Purpose, Outcomes, and cohesive Activities; and

c) a cross-cutting concern without an independent Process boundary can be represented as a Process View rather than as a Process.

### 5.3 Discovery and Execution Layers

A Skill Description claiming Description Conformance must provide distinguishable discovery and execution layers while retaining one identifiable authoritative Process Description.

a) The discovery layer must present the Name and Skill Discovery Description.

b) The Skill Discovery Description must state what the Process does, when the Skill is used, and the information needed to determine applicability. It must remain consistent with the authoritative Name, Purpose, Outcomes, scope, Entry Criteria, and Constraints and must not replace those elements.

c) The execution layer must present or provide access to the complete Skill Description, including Name, Purpose, and Outcomes and any optional PF elements included.

d) Mandatory references must resolve.

e) A summary of Entry Criteria in the discovery layer must not conflict with the authoritative Entry Criteria in the execution layer.

Cross-cutting Controls, Constraints, Enablers, or guidance should be treated separately from one Process Skill where their scope extends across Processes.

### 5.4 Logical Skill References

An ALPS representation that refers to another Agent Skill uses a logical package reference and Skill name as specified in this clause.

A package-qualified reference has the following form:

```text
skill:<package-id>#<skill-name>
```

A Logical Package Scope is identified by a package ID and an exact package version. The reference syntax carries the package ID; an applicable Package Binding must supply the exact package version. The package ID, exact package version, and Skill name together form the complete logical identity.

Within the same Logical Package Scope, the following same-scope short reference may be used:

```text
skill:#<skill-name>
```

The Logical Package Scope containing the representation must be declared by the representation or a governing normative source and must not be inferred from a Skill Package directory or repository path. A resolver must resolve the same-scope short reference to exactly one matching Skill Package within that declared scope and must normalize it with the scope's package ID and exact package version when a complete identity is needed. It must not silently resolve across Logical Package Scopes or package versions.

Repository-relative paths can locate a physical copy but must not serve as the representation's logical identity. ALPS does not require GitHub or another particular service to be the package identity authority.

### 5.5 Skill Packages

A Skill Package must contain exactly one authoritative Agent Skill representation.

A Skill Package is distinct from a Logical Package Scope. A Logical Package Scope can contain multiple Skill Packages, and the exactly-one rule above applies independently to each Skill Package.

Accompanying resources may provide reference information, execution resources, or deliverable resources. Their roles and conditions of use must be identifiable from the authoritative representation, and mandatory references must resolve.

When an authoritative representation contains a mandatory reference to another Skill Package, an applicable Package Binding must make the reference resolve to exactly one target under 5.4.

For a package-qualified reference, the target Skill Package must belong to the Logical Package Scope selected for the referenced package ID and exact package version.

For a same-scope short reference, the referring and target Skill Packages must belong to the same declared Logical Package Scope that contains the referring representation.

Unnecessary duplication or conflict must not arise between the authoritative representation and accompanying resources. Each resource is classified by its function in Process application—reference information, Input, Output, Control, Constraint, or Enabler—not by its directory. A Skill Package should contain only resources that directly support understanding or applying the represented PF construct.

### 5.6 Specialization of PF

| PF construct | ALPS treatment |
|---|---|
| Process Description | Skill Description when represented by an Agent Skill |
| Process | Default Agent Skill representation |
| Process Model | Agent Skill representation with `metadata.alps.kind: process-model` |
| Process Reference Model | Agent Skill representation with `metadata.alps.kind: process-reference-model` |
| Process View | Agent Skill representation with `metadata.alps.kind: process-view` |
| Resources that perform or support a Process | Agents, models, tools, Skills, and execution environments treated as Enablers |

ALPS may make a PF rule concrete for the Agent context and may strengthen it where needed, subject to 2.1.

## 6. Representation Requirements

### 6.1 Common Requirements

Every ALPS representation must:

a) identify or default to the representation kind that matches the PF construct actually represented;

b) retain one identifiable authoritative representation;

c) preserve the meaning of the represented PF construct;

d) keep reference information from altering normative meaning or force;

e) make every mandatory logical or accompanying-resource reference resolvable; and

f) avoid conflict or unnecessary duplication between the authoritative representation and accompanying resources.

### 6.2 Process Representations

A Process representation must satisfy the applicable PF requirements for a Process Description, including the required Name, Purpose, and Outcomes, and must satisfy 5.2 and 5.3.

A Skill Name must use a concise noun phrase as the Skill heading.

A general Skill Description must preserve PF's non-prescription of performer, Task allocation, method, tool, metric, management method, and execution sequence. An Instance-specific description must state its context and can include Instance-specific capabilities, resources, Inputs, Outputs, Controls, Constraints, criteria, and timing.

A statement used as a Task must express an individual action supporting one or more Outcomes so that its operation and object are distinguishable. A statement whose primary function is to direct or limit execution must be classified as a Control or Constraint rather than a Task. Every Task must have a distinguishable normative attribute.

The Skill Discovery Description of a Process representation claiming Description Conformance must end with exactly `ALPS-conformant.` in English or `ALPS準拠。` in Japanese. This marker is a shorthand Description Conformance claim about the containing Skill Description; it does not claim Reference Process Conformance, Outcome achievement, Capability, or Execution Conformance.

### 6.3 Process Model Representations

A Process Model representation must identify its Processes and their relationships. It may identify the Agent Skills that provide their authoritative Process Descriptions and need not repeat each Process Purpose or Outcomes.

A subset of Processes can be selected according to Purpose.

### 6.4 Process Reference Model Representations

A Process Reference Model representation must identify every included Process by Name, Purpose, and Outcomes and place their relationships in an explicit structure.

When it identifies a Process Skill:

a) the logical reference must resolve to a Process representation;

b) the Process Name must identify the same Process; and

c) the Purpose and Outcome set must equal those in the authoritative Process Description.

A mismatch makes the Process Reference Model representation invalid. Neither representation silently overrides the other.

### 6.5 Process View Representations

A Process View representation must:

a) state Name, Purpose, and Outcomes;

b) provide explanation and application guidance sufficient to understand how its Activities and Tasks contribute to its Outcomes;

c) identify every source Process whose Activity or Task it references;

d) maintain provenance and Traceability for referenced source elements; and

e) preserve each source element's meaning.

A Process View may describe View-local Activities and Tasks where needed for its concern. Referenced, modified, or View-local elements do not change the source Process and do not by themselves contribute to or alter Source Process Conformance.

A context-specific change to an applicable source Process must be handled through Tailoring. An authoritative semantic change to the source Process must be handled through controlled redefinition.

### 6.6 Representation-Specific Assessment Boundaries

Description Conformance concerns a representation. Process Conformance concerns a Process or Process Instance. Achievement of Process View Outcomes is a separate assessment from both Process View Description Conformance and Source Process Conformance.

Loading, parsing, resolving, or mechanically validating a representation does not by itself establish any of those claims.

## 7. ALPS Life Cycle and Reference Model

### 7.1 Life Cycle

The ALPS life cycle concerns definition, application, management, evolution, and retirement of ALPS representations and the Processes they enable.

| Stage | Concern |
|---|---|
| **Concept** | Needs for Process knowledge or another ALPS representation are identified and classified. |
| **Definition** | Authoritative representations are defined and verified. |
| **Operation** | Representations are activated, Processes are resolved and invoked, and compositions are executed. |
| **Evolution** | Representations and Process execution are assessed, tailored, changed, and improved. |
| **Retirement** | Representations that are unnecessary, unsafe, misleading, or superseded are withdrawn from active use under management. |

The order shown does not prescribe execution order. Processes and Activities can span Stages and can be applied concurrently, iteratively, or recursively under PF.

### 7.2 Reference Model Composition

The ALPS Reference Model identified by `skill:#alps-reference-model` must include exactly the following Reference Processes:

- `skill:#define-alps`;
- `skill:#apply-alps`; and
- `skill:#manage-alps`.

The ALPS Reference Model is authoritative for the explicit relationship structure among those Processes. Each referenced Process Skill is authoritative for the complete Process Description of its Process, including Activities, Tasks, Inputs, Outputs, Controls, Constraints, Enablers, Entry Criteria, Exit Criteria, and reference information when present.

The Name, Purpose, and Outcomes projected into the ALPS Reference Model must equal those in each authoritative Process Description. The integrity rules in 6.4 apply.

### 7.3 Reference Process Application

The three Reference Processes are general Processes. Their document order, Activity order, and Task order do not prescribe execution order.

Agent Skill activation and Process Invocation remain distinct when the ALPS Reference Model is used. The Reference Model can guide Process selection and composition but is not itself invoked as a Process.

A subset of the Reference Processes can be selected according to Purpose. Under Outcome Conformance, Activities and Tasks are guidance and can be selected without changing the declared Process scope. Under Task Conformance, a requirement Task in scope must not be omitted unless managed Tailoring changes the scope. Applying only some Activities as a Conformance scope must be declared as a tailored scope of the parent Reference Process.

A context-specific change to an applicable Reference Process is managed Tailoring; an authoritative semantic change to its Process Description is controlled redefinition.

### 7.4 Reference Process Conformance

Reference Process Conformance is assessed against the authoritative Process Skill identified in 7.2, not against a duplicate Process Description in this specification.

The valid Process units for Reference Process Conformance are Define ALPS, Apply ALPS, and Manage ALPS. A constituent Activity is not an independent unit of Process Conformance.

## 8. Activation, Invocation, and Composition

### 8.1 Selection and Activation

The representation kind must be determined before an Agent Skill is treated as a candidate for Process Invocation. Only a Process representation may be selected for direct Invocation.

A Process Model, Process Reference Model, or Process View may be activated to support selection, comparison, composition, or a cross-cutting concern. Its activation must not be treated as Invocation. A referenced Process Skill must be resolved before use.

### 8.2 Invocation and Completion

Before Invocation:

a) the Process Entry Criteria must be satisfied;

b) required Inputs and Enablers should be available; and

c) applicable Controls, Constraints, Tailoring decisions, and required Decision Gates must be identified.

If Entry Criteria are not satisfied, Invocation must be deferred or the unmet conditions must first be resolved.

The selected Conformance basis determines whether Activities and Tasks are guidance or mandatory execution conditions under PF 8.3. A requirement Task that is in scope must not be omitted unless managed Tailoring has changed it. An execution sequence not established by a Constraint must not be assumed.

A required Decision Gate must be passed before the action it governs occurs. Process Exit Criteria must be assessed before completion is declared. Outcome achievement should be determined from observable evidence.

### 8.3 Process Composition and Handoffs

When multiple Processes are composed:

a) the target Outcomes and the identity and provenance of each Process representation should be identifiable;

b) every provider Output to recipient Input mapping that affects successful application must be explicit, and the exchanged item names, meanings, and scopes should be aligned;

c) an undefined handoff may be introduced only through an applicable controlled change or Tailoring decision;

d) when an Output changes, affected Inputs and applicable criteria should be reevaluated;

e) when the same information item is changed by multiple Processes, its integrity, state, and change handling must be defined in proportion to quality risk; and

f) Integration must establish completeness within the selected scope and consistency across Process relationships and structural levels.

When Processes are applied concurrently, iteratively, or recursively, shared or interdependent information items and the reference or change relationships among them should be identified to the extent needed for application.

When Output quality affects a subsequent Outcome or stakeholder acceptance, the determination conditions and necessary evidence should be related to Entry Criteria, Exit Criteria, a review, or a Decision Gate.

Concurrency, Iteration, Recursion, and Integration retain their PF meanings and do not themselves prescribe an execution sequence.

### 8.4 Process View Application

When a Process View is active, referenced source elements retain their source meaning. View-local or modified elements must not silently change the applicable source Process or its Conformance basis.

Process View Outcome achievement can be assessed for the View as a whole but remains distinct from Source Process Outcome Conformance.

## 9. Controls, Constraints, and Enablers

### 9.1 Functional Classification

PF governs the classification of Inputs, Outputs, Controls, Constraints, and Enablers. An ALPS resource must be classified by its function in the Process, not by file type, directory, or distribution mechanism.

Framework-level Controls and Enablers must state scope, exceptions, and whether Tailoring is permitted. Elements common to a declared scope may be stated once rather than repeated in each Process Skill.

### 9.2 Agent Resources

Human and Agent capabilities, Agents, models, tools, Skills, automation, and execution environments used to perform or support a Process are Enablers rather than Process Inputs.

A capability limitation, availability condition, response time, or other circumstance that limits permitted execution can instead be represented as a Constraint according to its function.

Capabilities or conditions needed for execution should be stated as Enablers or Constraints without allocating Tasks.

## 10. Entry/Exit Criteria, Decision Gates, and Reviews

### 10.1 Entry and Exit Criteria

Entry Criteria and Exit Criteria retain their PF meanings. A summary of Entry Criteria should be placed in the discovery layer to support applicability determination and must not conflict with the authoritative execution layer.

Exit Criteria should be related to determining Outcome achievement.

### 10.2 Decision Gates

Decision Gates retain their PF meaning and remain separate decision mechanisms rather than Skill Description elements.

A Gate required for an irreversible or high-impact external effect must occur before that effect. Human confirmation or escalation can implement such a Gate. The decision, rationale, assumptions, criteria, and evidence should be recorded according to risk and applicable Controls.

### 10.3 Reviews and Audits

Reviews and audits retain their PF meanings and should be tailored to the subject and risk. Their Entry Criteria, Exit Criteria, and responses to problems should be established.

When an Output is transferred to another Process or stakeholder, it should be evaluated against applicable criteria to determine whether it can serve as the intended Input or result.

## 11. Tailoring, Redefinition, and Instantiation

### 11.1 Managed Tailoring

Tailoring retains its PF meaning and must be performed through the Tailoring and Formal Adoption Activity of Manage ALPS (`skill:#manage-alps`). Those requirements are prerequisites for Tailored Conformance.

The applicable requirements and recommendations of that Process govern the Tailoring scope, Controls and Constraints, affected elements, assumptions, criteria, evidence, affected-party Input, and rationale. Tailored Conformance requires the resulting decision and scope to remain traceable.

### 11.2 Tailoring and Authoritative Redefinition

A context-specific change to an applicable Process or life cycle model is Tailoring. A semantic change to an authoritative ALPS representation is redefinition.

Authoritative redefinition must be performed and verified through Define ALPS (`skill:#define-alps`). A changed semantic element must not be formally adopted until controlled redefinition and verification are complete.

A Process View does not redefine a source Process merely by containing a modified or View-local Activity or Task.

### 11.3 Process Instantiation

Process Instantiation retains its PF meaning. It can add Instance-specific success criteria, Activities, Tasks, capabilities, resources, conditions, and timing when quality risk justifies the detail. Instantiation does not replace Tailoring and can be applied to a tailored Process.

## 12. Conformance, Capability, and Assessment

### 12.1 Subjects of Conformance

Every Conformance claim must identify its subject and selected criteria.

| Subject | Required basis |
|---|---|
| **Description Conformance** | A Skill Description for a Process representation satisfies PF and applicable Clauses 4 through 6. If its Skill Package is included in the subject, 5.5 also applies. |
| **Process Model Description Conformance** | The representation satisfies applicable kind, Process identification, relationship, logical-reference, package, and internal-consistency requirements. |
| **Process Reference Model Description Conformance** | The representation satisfies applicable kind, Process identity, Name/Purpose/Outcomes equality, relationship, logical-reference, package, and internal-consistency requirements. |
| **Process View Description Conformance** | The representation satisfies applicable kind, Purpose and Outcomes, source provenance and Traceability, source-meaning preservation, relationships, application guidance, package, and internal-consistency requirements. |
| **Reference Process Conformance** | Define ALPS, Apply ALPS, or Manage ALPS satisfies 12.2 or 12.3 against its authoritative Process Skill under Clause 7. |
| **Execution Conformance** | A Process Instance executed through a Process Skill satisfies 12.2 or 12.3 against the Process described by that Skill. |

### 12.2 Full Conformance to a Process

PF 8.3 governs Full Conformance. A claim must select Outcome Conformance, Task Conformance, or both and satisfy the selected basis.

For Reference Process Conformance, only Define ALPS, Apply ALPS, and Manage ALPS are Process units. Independent Process Conformance must not be claimed for a constituent Activity.

Process View Outcome assessment remains separate from Process Conformance to a source Process.

### 12.3 Tailored Conformance

PF 8.4 governs Tailored Conformance. A claim must identify the Process tailored through managed Tailoring, declare the application scope, and demonstrate satisfaction of every Outcome and Activity or Task requirement remaining in scope.

Applying only some Activities of a Reference Process must be declared as a tailored scope of the parent Process and must not be claimed as independent Process Conformance to those Activities.

### 12.4 Capability and Assessment

Capability and Conformance are separate dimensions under PF 8.5. Neither establishes the other.

Assessment criteria must match the declared subject:

a) a Process representation may be assessed for Description Conformance, execution Conformance, Outcome achievement, performance, and effectiveness as applicable;

b) a Process Model should be assessed for Process coverage, relationship coherence, resolvability, and applicability;

c) a Process Reference Model should be assessed for Process identity, semantic-center equality, relationship coherence, resolvability, and suitability as a frame of reference;

d) a Process View should be assessed for Purpose and Outcomes, source provenance and Traceability, source-meaning preservation, handoffs, application guidance, and usefulness;

e) a Skill Package can be assessed for its authoritative representation, mandatory-reference resolution, resource roles and conditions of use, consistency, and reverification after change.

Assessment of a non-Process representation is not Process execution Conformance.

---

Informative examples, related-document notes, and guidance on human oversight, accountability, and non-deterministic evidence are maintained in [ALPS Informative Guidance](../docs/alps-informative-guidance.md).

(End)
