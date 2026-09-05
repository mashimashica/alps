# Process Framework

[Japanese translation](locales/ja/process-framework.md)

> “Or, paraphrasing, pragmatism identifies meaning with formation of a habit,
> or way of acting having the greatest generality possible, or the widest range
> of application to particulars.”
>
> — John Dewey, “The Pragmatism of Peirce” (1916), p. 711.

## 1. Purpose and authority

This Framework establishes a domain-independent basis for describing and understanding work: its intent, boundaries, work content, context, relationships, application, and evaluation. It supports general and context-specific work, including work performed once, while leaving execution means open where the context permits.

The Framework governs Process meaning. The [ALPS Specification](ALPS-SPEC.md) applies it to Agent Skills and must preserve its semantics and normative force. If the two conflict, this Framework must take precedence.

**Must** states a requirement; **must not** states a prohibition. **Should** and **should not** state recommendations. **May** states permission. **Typically** describes customary practice; **can** and **could** express possibility or capability. These last expressions carry no normative force. A description must make each statement's force and scope clear. Applicable requirements and prohibitions retain their force regardless of the assessment method or whether a claim is made.

Examples, notes, conventions, and other reference information are informative. They must not alter the meaning or normative force of the Process elements they explain.

## 2. Work, description, and results

| Term | Meaning |
| --- | --- |
| **Process** | Related work performed under a Purpose to establish one or more Outcomes. Its Activities and Tasks, when described, explain how the work forms a coherent whole. |
| **Process Description** | An account of a Process, distinct from its performance. It can describe a general Process or a particular application. |
| **Process Instance** | One application of a Process in a particular context. Its actual results are evaluated separately from the description. |

Every Process Description must contain **Name**, **Purpose**, and **one or more Outcomes**. These elements provide the semantic center and shared reference points for application and evaluation.

| Element | Meaning |
| --- | --- |
| **Name** | Identifies the work and its central concern, distinguishing it within the relevant scope. |
| **Purpose** | States the related high-level objective or objectives for performing the work and encompasses its intended Outcomes. |
| **Outcome** | An observable, assessable result condition established by the work. |

The Name should be concise. The Purpose should clarify boundaries with neighboring work where they overlap; it should not combine independent objectives or merely summarize Activities. Benefits to stakeholders may explain the value of achieving the Purpose, but are distinct from the Outcomes used to judge success.

Each Outcome must state one observable result condition. Independent results must not be joined in one Outcome; they must be distinguishable when judging achievement. Every Outcome must remain meaningful throughout the description's applicable scope, be relevant to its Purpose, and, together with the other Outcomes, be sufficient to satisfy it. Review must check these properties. Each statement should carry one meaning and enough context to remain meaningful when referenced separately; brevity must not obscure independent objectives, results, or actions.

A Task states an action; an Outcome states a result condition. An **Output** is a product, information item, or service produced or updated by the work. Merely creating an Output must not be stated as an Outcome. An Output can provide evidence of an Outcome, but its existence alone does not establish success. For example, an explanation is an Output; the recipient's demonstrated understanding is an Outcome.

## 3. Work content and necessary detail

Activities, Tasks, Inputs, Outputs, Controls, Constraints, Enablers, and Entry/Exit Criteria are included according to the purpose of the description and the detail needed to understand, apply, or evaluate the work. Their inclusion is optional; their meanings and relationships follow this Framework when they are used. A description must include necessary detail and must not contain empty optional sections or completeness-driven fields. Clarify an otherwise ambiguous scope where it matters. The applicable context and source identity can be expressed in the description or associated information.

An **Activity** is a cohesive set of Tasks within a Process. It organizes related actions as a continuous or iterative function narrower than the Process as a whole, so that their contribution can be understood. Tasks within an Activity should relate more closely to one another than to Tasks outside it.

A **Task** states an individual action intended to support one or more Outcomes. Its operation, object, and normative force must be clear. The Tasks described within an Activity need not enumerate every possible action within its boundary.

Taken together, the Activities and any Sub-processes used to describe the Process's work must cover every Process Outcome and satisfy the Process Purpose. Their relationship to Outcomes can be one-to-one, one-to-many, many-to-one, or many-to-many. Review must check this coverage and the contribution of the described Tasks. An Activity can be described as a **Sub-process** with its own Name, Purpose, and Outcomes when separate treatment is useful.

Process, Sub-process, and Activity have no universal size boundaries. Outcomes and principal Outputs usually help identify a Process boundary; intermediate Outputs do not by themselves require another Process. Divide work where it clarifies boundaries, responsibilities, or relationships, and omit a level where it impairs understanding or use. A difference in performer or tool alone does not determine a Process boundary. Dependencies on other Processes should be reduced where practicable while keeping necessary relationships clear.

A general description must avoid unnecessarily fixing performers, tools, methods, metrics, management methods, or order. It describes the functional relationships needed for performance. A method or sequence required in a particular context may be stated with its scope and force. A **Procedure** prescribes ordered steps; Activities and Tasks describe work whose document order must not be interpreted as execution order. Necessary temporal dependencies must be explicit Constraints.

## 4. Boundary elements and information

Classify each occurrence of an element by its function in the work, independently of its filename, medium, or location.

| Element | Function |
| --- | --- |
| **Input** | An item acted on as source material for a result, including information examined or transformed by the work. |
| **Output** | A product, information item, or service produced or updated by the work. |
| **Control** | Directs execution or supplies the basis on which work or results are judged. |
| **Constraint** | Limits permitted execution or conditions of application. |
| **Enabler** | Supplies capability or resources that make execution possible or support it. |

A policy used as a criterion is a Control; a policy being revised is an Input. People, Agents, tools, and execution environments used to perform the work are Enablers. A limitation on their use is a Constraint. The same resource can have different roles, and each role must be identifiable.

An **information item** is an identifiable body of information treated as a unit, independent of its storage medium or presentation. Naming an Output need not require a document or a fixed artifact. Outputs can include final results, intermediate work products, or information shared with other work.

A representative transformation relates Inputs, Activities, and Outputs: Activities act on Inputs, Enablers support the work, Controls direct it, and Constraints limit it. Representative Inputs and Outputs illustrate a possible manner of performance. They must not be read as the only permitted means or as a replacement for the complete description's requirements.

**Entry Criteria** state the conditions under which the affected work can begin. **Exit Criteria** state the conditions under which it can be completed. They govern conditions, not positions on a schedule. Required conditions, including approvals, must be confirmed before the actions they govern; an unconfirmed condition prevents those dependent actions. Other work can proceed under its own applicable conditions. Completion of an Output must not replace evaluation of the Outcomes.

Controls, Constraints, and Enablers may be associated with individual elements or shared across descriptions. A shared element must identify its scope, any exceptions, and whether contextual changes are permitted, directly or by reference. Membership in a collection or reference to a document does not by itself make every element applicable to every Process. Elements common to a declared scope may be stated once and referenced where they apply.

**Traceability** makes the relationships among Outcomes, Activities, Tasks, and information items identifiable so that their consistency and the effects of change can be examined. It should connect work and necessary Inputs and Outputs to the Outcomes they support, with enough detail for the intended use.

Processes may exchange information or repeatedly consult and update the same information. A needed relationship must make the information's meaning, scope, conditions of use, and relevant change impacts clear. Identify which work reads or changes it and which decisions or results require reconsideration after a change. A handoff relates a provider's Output to a recipient's Input; shared information can also support repeated interaction among several Processes. Storage and coordination mechanisms belong to the applying environment.

## 5. Applying Processes in combination

Processes, Activities, and Tasks can be selected and combined according to Purpose and applicable conditions. The following relationships describe different aspects of application:

| Relationship | Meaning |
| --- | --- |
| **Concurrency** | At least two Processes are applied in parallel at the same structural level. |
| **Iteration** | A Process or Process set is reapplied at the same structural level, including repeated interaction among Processes. |
| **Recursion** | A Process or Process set is reapplied at successive structural levels of the subject of application. |
| **Integration** | Completeness is established within one level and consistency between levels. |
| **Incremental application** | Successive usable portions of the intended result or scope are established. |

These relationships are independent and can be combined. Incremental application concerns which portion is established; Iteration concerns reapplication. A structural level belongs to the subject of application and does not by itself imply an organizational or performer hierarchy.

Iteration can refine Outputs as decisions and understanding develop. In Recursion, an Output at one level can become an Input at another. When an Output changes, affected Inputs and judgments must be reconsidered. Actual flow follows the purpose and conditions of application; the relationship names alone prescribe no sequence. Process selection and timing must be reviewed when the subject or context changes in a way that affects them.

## 6. Models, views, and references

| Construct | Role |
| --- | --- |
| **Process Model** | Organizes interrelated Processes and the relationships needed to understand their composition or application. |
| **Process Reference Model** | Provides a common basis for comparison or assessment through identified Process Descriptions, their Purposes and Outcomes, and their relationships. |
| **Process View** | Selects and explains elements across Process Descriptions around a particular concern. |

These constructs can be ordinary reference materials. They must refer to source Process Descriptions and must not maintain duplicated Purpose or Outcome definitions for management. A domain framework can use a Process set and common terminology to support selection and composition. A **life cycle model** organizes Processes and Activities in relation to the life of a subject; its relationships and any ordering depend on the application.

A View must retain source identity and necessary Traceability. It can select, explain, or propose changes to source elements, with proposals and local additions clearly distinguished from source requirements. A change in presentation alone must not change obligations or success conditions. Reference material that organizes work is distinct from a Process Description; independently defined work needs its own Name, Purpose, and Outcomes.

The authoritative description must be uniquely identifiable using ordinary links or identifying information. When reproducibility is needed, identify the applicable version, commit, digest, or equivalent alongside the reference. Each necessary reference must identify its intended target. If the target cannot be confirmed, report the missing reference and affected scope as unconfirmed; do not substitute a same-named document or another version.

Summaries, translations, examples, and views must preserve authoritative meaning and normative force. Their sources must be identifiable wherever necessary to distinguish source content from interpretation or local additions. A translation is not a second authority.

## 7. Context, instantiation, and change

**Process Instantiation** describes one application in enough detail for its context. It derives application-specific success criteria from the applicable requirements and identifies the work, resources, conditions, and timing needed to achieve them. These details must remain consistent with the Process being applied.

**Tailoring** adapts a Process Description or life cycle model to the needs and conditions of a declared context. It can change the applicable Name, Outcomes, Activities, Tasks, or boundary elements within the permitted scope. The Name, Purpose, and Outcomes must remain coherent, and the relationship to the source must remain identifiable. A context can cover one application or a group of applications.

Instantiation makes an application concrete; Tailoring changes what applies. A tailored Process can also be instantiated. A context-specific choice already permitted by the description does not itself change that description.

Distinguish a change to the authoritative description, a context-limited change to what applies, and a change in presentation. A change must identify the affected source and elements, scope, rationale, consequences, and necessary revalidation. Consider affected requirements and stakeholder needs, risks, available capabilities and resources, and applicable Controls and Constraints. The level of detail and rigor should be proportionate to these conditions.

Authority and approval follow the applying environment's conditions. A context-limited change must not silently redefine the source, remove an externally imposed requirement, or imply authority to waive a prohibition. When conditions change, assumptions and adaptation decisions should be reviewed. Revalidation must address affected Outcomes, work, conditions, references, shared information, and translations where relevant. Its results and unresolved limits must be explicit. The environment determines how the source, applicable description, changes, and supporting rationale are retained and versioned.

## 8. Evaluation and improvement

An evaluation must identify its subject, scope, applicable criteria, evidence, and resulting judgment. Evidence supports a judgment; it is not the judgment itself. Keep these questions distinct:

| Subject | Question |
| --- | --- |
| Description validity | Are the purpose, success conditions, boundaries, references, work, and necessary detail coherent and usable? |
| Execution result | What actually happened in this application, and which Outcomes were achieved? |
| Satisfaction of requirements | Were applicable mandatory conditions and prohibitions respected? |

A **review** evaluates a description, work, or results against applicable criteria. An **audit** examines evidence of satisfaction of applicable requirements. Their scope, criteria, and evidence must make clear which question is answered. A **Decision Gate** is a mechanism for deciding whether to proceed under stated criteria, not a stage or a component of the Process Description. Passing a gate establishes only what its criteria and evidence support.

A successful description review must not be reported as successful execution. Execution success must not be inferred merely from an Output, an approval, or passed format checks. Representative examples or trials can support an applicability judgment but must not be reported as proof for every context.

**Capability** concerns the ability to achieve intended results. **Maturity** concerns how far a Process or its implementation is established, managed, and capable of consistent performance. These characteristics require evidence relevant to the assessed context; one successful application or satisfaction of requirements does not by itself establish them. Capability does not itself establish satisfaction of requirements. Effectiveness can be evaluated through Purpose and Outcomes, while benefits and costs can inform improvement decisions.

Measures used in an evaluation should connect the information needed to defined measures, collected data, analysis, indicators, and the decisions they support. Findings and lessons can inform changes whose effects are evaluated against the intended results. Execution, approval, measurement, and record-keeping arrangements are supplied by the applying environment.

Unconfirmed facts, assumptions, unmet conditions, and exclusions must remain distinguishable. An exclusion needs an applicability rationale; missing evidence is not a reason to mark a requirement inapplicable. None of these conditions may be silently converted into success. Findings must expose evidence gaps and their consequences.
