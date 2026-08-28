# Process Framework

> “Or, paraphrasing, pragmatism identifies meaning with formation of a habit,
> or way of acting having the greatest generality possible, or the widest range
> of application to particulars.”
>
> — John Dewey, “The Pragmatism of Peirce” (1916), p. 711.

## Purpose and Authority

This Framework establishes a domain-independent basis for describing and understanding a Process—its intent, boundary, work content, context, relationships, application, and evaluation—without fixing one performer, tool, method, life cycle, or execution pattern.

ALPS applies this Framework to Agent Skills. If an ALPS provision conflicts with this Framework, this Framework must take precedence.

In this Framework, **must** states a requirement and **must not** states a prohibition. **Should** states a recommendation and **should not** states a recommendation against an action. **May** states permission. **Typically** describes customary practice without creating a requirement. **Can** and **could** express possibility or capability and have no normative attribute. Uppercase forms of these words are not used.

This Framework is the authoritative source for those meanings. A specification or description that applies it inherits them and does not redefine them. Examples, notes, conventions, diagnostic questions, and other reference information are informative and must not alter the meaning or normative force of primary Process elements.

## 1. Work and Its Description

### 1.1 Work, Description, and Application

| Construct | Meaning |
|---|---|
| **Process** | Related work performed under a stated Purpose to establish one or more Outcomes. It acts on Inputs, produces Outputs, and brings Activities and Tasks into a coherent whole. Its function is defined by its Purpose, Outcomes, and set of Activities and Tasks; its performance is intended to benefit stakeholders. |
| **Process Description** | An account of a Process, not its performance. It can describe a general Process or a particular Process Instance. |
| **Process Instance** | One application of a Process in a particular context. An Instance-specific description can identify needed capabilities and resources, incoming and outgoing items, applicable Controls and Constraints, and relevant timing. |

### 1.2 Necessary Core and Optional Detail

Every Process Description must contain Name, Purpose, and Outcomes. These elements preserve the Process's semantic center and provide common reference points for implementation and Assessment without requiring structural decomposition.

Activities, Tasks, Inputs, Outputs, Controls, Constraints, Enablers, Entry Criteria, Exit Criteria, and reference information are optional and are included according to the Purpose of the description and the detail needed. The selected detail can also help characterize maturity, Capability, or quality.

An explicit, systematic description supports consistent results, deployment of standard Processes, Tailoring, improvement, and Process Assessment and can be used with any Process Model.

### 1.3 Layers and Reference Information

A Process Description can present an overview and a detailed description for readers who need different depths of information. An overview can include Purpose, description, Inputs and Outputs, Activities, Common Approach, practical tips, and good-practice summaries. The detailed part treats matters specific to the Process; cross-cutting matters are treated separately.

This layered form is optional and does not replace Name, Purpose, and Outcomes. Overviews, descriptions, Common Approach, practical tips, notes, and examples are reference information.

### 1.4 Interpretation and Writing Rules

A Process Description must keep the functions of Name, Purpose, Outcomes, Activities, and Tasks distinct and internally consistent.

Each sentence should carry one meaning. Independent objectives, results, or actions should not be joined merely to shorten the text. Each statement should contain enough context to remain meaningful when referenced independently; supplementary explanation can be placed in reference information.

A general Process Description must not require a particular performer, method, technique, tool, metric, management method, or execution sequence. Methods and examples can be offered as guidance without becoming Process requirements.

A Procedure prescribes ordered steps. Activities and Tasks describe Process work and must not be interpreted as procedural steps merely because of their order on the page. Implicit timing, scheduling, and order should be avoided. A necessary temporal relationship should be stated explicitly as a Constraint; without such a Constraint, no particular execution sequence is required.

Wording must distinguish requirements, recommendations, permissions, typical actions, and non-normative statements.

## 2. Intent, Success, and Work Content

### 2.1 Name and Purpose

| Element | Function and rules |
|---|---|
| **Name** | Identifies the Process and distinguishes it from other Processes in the applicable Process Model. It must be a concise noun phrase, must express the central concern, and must not summarize the Purpose. In English, the word “process” should connect the Name; this is a language convention, not a semantic requirement. |
| **Purpose** | The Purpose must state the related high-level objective or objectives for performing the Process and must encompass the Outcomes expected from effective implementation. It should clarify the boundary where neighboring Processes appear to overlap, should be concise and wherever possible one sentence, and should not summarize Activities or Outcomes or combine independent objectives. Supplementary explanation can be reference information. |

### 2.2 Outcome and Output

An **Outcome** is a measurable and tangible result condition achieved through the Process. It must be observable and assessable. It is not an Output, and merely creating a document, record, or information item must not be stated as an Outcome.

Each Outcome must state one positive, observable condition in a declarative statement. An English Outcome must use a present-tense verb. Independent results must not be joined in one Outcome.

An Outcome of a general Process must remain meaningful throughout the Process's applicable scope. Together, the Outcomes must be sufficient for the Purpose, and every Outcome must be relevant to it. Each Outcome should remain meaningful when read separately. Outcomes should be concise, but one clear meaning takes priority over brevity; their number follows from what the Purpose requires. Benefits should be distinguished from Outcomes and can be explained in reference information.

An **Output** is a product, result, or service produced by a Process. An Output leaves the work; an Outcome is a condition used to assess success. An Output of one Process can become an Input to another Process.

### 2.3 Activity and Task

An **Activity** is a cohesive set of Tasks within a Process. It organizes related actions so that their contribution to the Process can be understood and communicated. A sufficiently cohesive and detailed Activity can be treated as a Sub-process with its own Purpose and Outcomes.

Taken together, the Activities and any Sub-processes must cover every Process Outcome and satisfy the Process Purpose; they need not map one-to-one to Outcomes. Tasks within an Activity should relate more closely to one another than to Tasks outside it. An Activity must be treated as a continuous or iterative function narrower than the Process as a whole. The Activity set should address all Outcomes and may extend beyond the minimum work needed to satisfy the Purpose.

A **Task** states an individual action intended to support one or more Outcomes. Each Task must make clear whether the action is required, recommended, permissible, or typical. The Tasks assigned to an Activity need not enumerate every possible action within the Activity's boundary. The timing and sequence rules in 1.4 apply to Activities and Tasks.

## 3. Process Boundary

### 3.1 Granularity and Cohesion

Process, Sub-process, and Activity have no universal size boundaries. Primary Outputs and Outcomes typically provide the boundary test; intermediate Activity Outputs do not usually determine it.

Closely connected automated work requiring little human intervention can share one Process Description. Decomposition is useful while it improves understanding of boundaries, responsibilities, or relationships and is omitted when another level would harm understanding or use.

Within the boundary, Outcomes, Activities, and Tasks form a coherent explanation of why the work belongs together. Dependencies on other Processes are reduced as far as practicable. A significant Activity with many Tasks can be described as a separate Process when separate treatment is useful.

### 3.2 What a General Process Leaves Open

A general Process does not prescribe the performer's structure, who performs any part, or the implementation method. It describes the functional relationship needed for performance.

Processes, Activities, and Tasks can be selected according to Purpose, and one Process or a combination of Processes can be performed. Leaving the performer and implementation open preserves reusability and does not make the Process boundary incomplete.

## 4. Boundary Elements and Exchanges

### 4.1 Functional Classification

Inputs and Outputs connect a Process to its external environment. Controls, Constraints, and Enablers shape execution. Classify each occurrence by the function it performs in that Process, not by its form or storage location.

| Element | Function |
|---|---|
| **Input** | An item the Process transforms into an Output. It can come from another Process, an information source, or a source outside the Process. Specifying required or representative Inputs is optional. |
| **Output** | A product, result, or service produced by the Process. |
| **Control** | Directs Process execution or the basis on which it is judged. Controls can arise from applicable laws or regulatory requirements, policies, conformance to voluntary standards, or agreements. |
| **Constraint** | Limits permitted Process execution. Constraints can arise from the environment or conditions of application outside the Process. |
| **Enabler** | Supplies capability that makes execution possible or supports it, including relevant capabilities, specialized capabilities, tools, and technologies. |

People, Agents, automation, tools, and execution environments used to perform a Process are resources, not Inputs. When represented in a Process Description, they are Enablers. Controls and Constraints can have their own sections or be associated with other Process elements.

### 4.2 Transformation Without Method Prescription

Outputs are optional when Outcome achievement can be demonstrated. They can include parts of a final product or service, intermediate work products used for validation or audit, and assets reusable by other Processes. Principal Output kinds include artifacts and information items.

A representative transformation relates Inputs, Activities, and Outputs: Activities transform Inputs; Enablers support the transformation; Controls direct it; Constraints limit it. Naming an Output does not by itself require creation of a document.

Representative Inputs and Outputs show one possible manner of performance and do not prescribe the only manner. A Process should be understood from the complete Process Description rather than only from its representative flow.

### 4.3 Entry and Exit Criteria

**Entry Criteria** state the conditions under which a Process can begin. **Exit Criteria** state the conditions under which it can be completed.

When Entry Criteria and Exit Criteria are needed for the Purpose of the description and its required detail, they should be included together with relevant Inputs and Outputs.

### 4.4 Handoffs and Traceability

Traceability should cover Outcomes, Activities, Tasks, and information items and show consistency among Process elements. Useful mappings include Tasks to Outcomes, Inputs to Outcomes, and Outputs to Outcomes; the resulting evidence can support Process Assessment.

A handoff maps a provider Process's Output to a recipient Process's Input. Making its direction and content explicit allows dependencies to be understood. A handoff not defined beforehand can be added through Tailoring.

### 4.5 Shared Controls and Enablers

A Framework-level Control directs or constrains Processes within a declared scope. A Framework-level Enabler supports Processes within a declared scope.

Every shared Control or Enabler must state its scope, exceptions, and whether Tailoring is permitted. Membership in a Framework does not by itself make a shared element applicable to every Process. Elements common to a declared scope may be stated once rather than repeated.

## 5. Reusable Process Structures

### 5.1 Frameworks, Models, and Reference Models

| Construct | Role |
|---|---|
| **Process Model** | A Framework of interrelated Processes that can be composed from multiple Processes. |
| **Process Reference Model** | Defines individual Processes by their Purposes and Outcomes and places their relationships in an explicit structure. |
| **Process Framework** | Provides a Process set and terminology for an application domain, used to compose Process Models and select Process subsets according to Purpose. |

A Process Framework can establish a desired Process environment, support selection and composition in an established environment, provide a basis for agreement about Processes and Activities, and support composition of life cycle models. For Assessment, it can also function as the Process Reference Model. This Framework supports both Process Assessment and improvement.

### 5.2 Life Cycle Models

A **life cycle model** brings life cycle Processes and Activities into a shared basis for communication and understanding. Its details are expressed through Processes, Outcomes, relationships, and ordering.

The purpose of the application and the selected life cycle model determine actual Process order. Document clause order does not prescribe execution order. Process selection and timing must be continually reviewed when the subject or context changes.

### 5.3 Process Views

A **Process View** organizes Activities and Tasks across multiple Processes around a particular concern or Purpose and explains how they are applied to achieve its Outcomes. It changes the angle of attention, not the source Processes.

Every Process View must state Name, Purpose, and Outcomes and must provide explanation and guidance for applying its Activities and Tasks.

A Process View may reference Activities and Tasks from existing Processes and may describe View-local Activities and Tasks where needed for its concern. When it references a source element, the source and necessary Traceability must be maintained.

View-local or modified Activities and Tasks do not change a source Process merely by appearing in the View and do not by themselves contribute to or alter source Process Conformance. A change to the source Process must be handled through Tailoring or Process redefinition, as applicable. A Process View may show connections among Processes and their sources.

## 6. Applying Processes in Combination

### 6.1 Independent Relationships

| Relationship | Meaning |
|---|---|
| **Concurrency** | At least two Processes are applied in parallel at the same structural level. |
| **Iteration** | A Process or Process set is reapplied without changing structural level, including repeated interaction among Processes. |
| **Recursion** | A Process or Process set is reapplied at successive structural levels of the subject of application. |
| **Integration** | Completeness is established within one level and consistency between levels. |

These relationships are independent and can be combined. Iteration returns without changing level; Recursion repeats across levels; Concurrency concerns coexistence; Integration concerns completeness and consistency.

Process execution is not limited to serial arrangement. Iteration progressively refines Outputs, incorporates decisions and evolving understanding, addresses Constraints, and resolves trade-offs. It should continue until problems arising from the Processes are resolved. In Recursion, an Output at one level can become an Input at the next.

### 6.2 Flow and Change Propagation

Concurrency, Iteration, and Recursion do not by themselves imply timing or sequence. Actual flow must be determined through Tailoring according to application needs.

When Iteration or Recursion changes an Output, affected Process Inputs change as well.

## 7. Tailoring and Instantiation

### 7.1 Adaptation and Rigor

**Tailoring** is the controlled Adaptation of a life cycle model or Process to the needs and conditions of a declared context. Such models and Processes typically cannot be applied unchanged in every context. It sets enough rigor to perform Activities at an acceptable level of risk; too little raises the chance of problems, while too much can raise cost or schedule risk.

Tailoring typically continues dynamically as risk and context change and should be reviewed and revised when conditions warrant.

### 7.2 Levels and Permitted Changes

**Common-level Tailoring** adapts an external standard to needs shared across an intended application domain. **Individual-level Tailoring** adapts the resulting common Process to one subject of application.

Tailoring can delete, modify, or add Outcomes, Activities, Tasks, representative Inputs, and representative Outputs.

### 7.3 Tailoring Decisions

Tailoring must identify application risks, requirements, complexity, available capabilities and resources, and relevant standards.

Candidate Processes or life cycle models must be evaluated using conditions of application, available expertise and experience, stakeholder expectations or requirements, and risk tolerance. Tailoring must obtain Input from affected parties and comply with applicable Controls and Constraints.

Decisions should rest on facts and evidence. Their scope should be explicit; assumptions and criteria should be identified; and rationale should be recorded and maintained. A means of continually assessing the tailored Process should be established.

Representative pitfalls include reusing another subject's tailored baseline without new Tailoring, including every Process or Activity merely as a precaution, treating one measure, risk, or Control as universal, applying a pre-established tailored baseline unchanged, or excluding affected stakeholders.

### 7.4 Process Instantiation

When justified by quality risk, **Process Instantiation** describes one Process Instance in greater detail. It derives Instance-specific success criteria from requirements and identifies the Activities and Tasks that will achieve them; those links support management of quality risk.

Tailoring changes the Process or life cycle model that applies. Instantiation describes one application of that Process. A tailored Process can also be instantiated.

## 8. Evidence, Decisions, and Claims

### 8.1 Decision Gates

A **Decision Gate** is a decision mechanism that controls Process application; it is not a Process Description component or a Process stage.

Decision Criteria determine whether the uncertainty and risk of proceeding or changing Process state are acceptable and can draw from Purpose, Outcomes, conditions of application, and risk assessment. Gate frequency, scope, and formality can be adjusted to context.

A Gate decision should be explicit and recorded. Available decisions can include continue, hold, change, re-execute, or terminate. Before a Gate, a review should use necessary expertise and relevant Inputs. Passage should rest on evidence that Decision Criteria are met. The criteria should be updated and reevaluated at each Gate and whenever the context changes.

An Output accepted at a Gate can become a basis for later Activities. The decision, rationale, and assumptions should be recorded under the change management needed for the context.

### 8.2 Reviews and Audits

A **review** evaluates Process performance, Outputs, and Outcome achievement against agreed criteria. An **audit** examines evidence of Conformance to Processes, Outputs, and requirements in detail and confirms whether mandatory attributes and applicable requirements are satisfied.

Reviews and audits should appear in the application plan and be tailored to the subject and methods. Good practice gives them unambiguous starting and completion conditions and triggers them by risk or events rather than schedule alone.

It is good practice to make preparation, conduct, and acceptance methods and conditions clear and to include the necessary expertise and an independent perspective. When a problem is detected, it is also good practice to establish a clear action with a due date and completion conditions and to track it.

### 8.3 Full Conformance

Full Conformance to a Process must be claimed as Outcome Conformance, Task Conformance, or both, and the selected basis must be identified. When both are claimed, both sets of conditions must be satisfied.

| Basis | Condition for Full Conformance | Status of other elements |
|---|---|---|
| **Outcome Conformance** | Every mandatory Outcome in the declared Process is achieved. | Activities and Tasks are guidance, allowing freedom in implementation. |
| **Task Conformance** | Every requirement stated with **must** or **must not** in the Activities and Tasks of the declared Process is satisfied. | Outcomes are guidance. Recommendations, permissions, and typical actions do not become mandatory merely from their presence. |

Outcomes can be achieved and Activities or Tasks can be performed beyond what a Conformance claim requires.

### 8.4 Tailored Conformance

**Tailored Conformance** may be claimed when a Process or Process set does not satisfy the selected Full Conformance basis.

The claim must identify the Process or Processes tailored through the Tailoring Process, declare the application scope, and demonstrate satisfaction of the Outcomes and Activity or Task requirements that remain in scope.

### 8.5 Capability and Process Assessment

Capability and Conformance are separate assessment dimensions. Performing specified Activities and Tasks can require a higher Capability level than achieving Outcomes alone. Neither Capability nor Conformance establishes the other.

Process Outcomes can serve as the Process Reference Model for Assessment and improvement. Purpose and Outcomes state implementation objectives, enabling effectiveness to be assessed by means other than conformity alone.

## 9. Process Management and Improvement

### 9.1 Governance and Application

Process management should define how Processes are governed and made available, provide Tailoring guidance for individual applications, establish indicators of effectiveness and efficiency, and use them to assess performance.

Applicable Processes should be identified; their implementation and maintenance should be documented; established supporting methods and techniques should be used; and Tailoring guidance should be applied to the specific need.

Changes in management guidance should be communicated to affected users. Improvement opportunities should be continually identified, prioritized, and implemented.

### 9.2 Standard Processes and Benchmarking

Consistent use of standard Processes across multiple subjects supports repeatable and predictable performance, reuse of proven practices and lessons, initiation of new applications, and continual improvement.

Process benchmarking compares performance with declared criteria, applicable standards, or other comparators to find improvement opportunities. It should address performance, effectiveness, Conformance, benefits, and costs.

### 9.3 Measures, Assessment, and Learning

Process strengths and weaknesses should be assessed, and reviews and audits should be established.

Measures should be established to provide insight into Process performance and effectiveness. Those measures should be analyzed to determine effectiveness.

Mechanisms should collect lessons learned, connect them to action, and analyze candidate Process changes.

Lessons should be collected throughout execution and at planned milestones. Lessons and measures should be reviewed periodically to improve Processes and practices.
