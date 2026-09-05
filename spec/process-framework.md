# Process Framework

[Japanese translation](locales/ja/process-framework.md)

> “Or, paraphrasing, pragmatism identifies meaning with formation of a habit,
> or way of acting having the greatest generality possible, or the widest range
> of application to particulars.”
>
> — John Dewey, “The Pragmatism of Peirce” (1916), p. 711.

## 1. Purpose and authority

This Framework defines the meaning of a Process Description so that the purpose, success conditions, and necessary boundaries of work can be understood, applied, and evaluated independently of its execution means. It covers general and context-specific work, including work performed only once. Reuse is a benefit, not an admission condition.

The Framework governs Process semantics; the [ALPS Specification](ALPS-SPEC.md) maps them to Agent Skills. If the two conflict, this Framework must take precedence. Execution, storage, authorization, approval, and version management belong to the applying environment. This Framework prescribes no execution engine, management procedure, certification system, or record format.

**Must** states a requirement; **must not** states a prohibition. **Should** and **should not** state recommendations. **May** states permission. **Can** expresses possibility; examples and customary approaches are informative. A description must make each statement's force clear. A requirement or prohibition applies within its stated scope regardless of the assessment method or whether a claim is made. Choosing to assess Outcomes does not waive mandatory actions or prohibitions.

## 2. Work, description, and application

| Term | Meaning |
| --- | --- |
| **Process** | Related work directed toward a Purpose and one or more Outcomes. |
| **Process Description** | An account of that work, distinct from its performance. It can describe a general Process or work in a particular context. |
| **One application (Process Instance)** | The actual performance of the described work in a particular situation. Its results are assessed separately from the description. |

Every Process Description must contain **Name**, **Purpose**, and **one or more Outcomes**.

| Element | Function |
| --- | --- |
| **Name** | Identifies the work with a concise name that distinguishes it within the relevant scope. |
| **Purpose** | States why the work is undertaken and the objective its success conditions serve. |
| **Outcome** | States an observable result condition by which success can be evaluated. |

Each Outcome must describe a result state rather than an action or merely the creation of an artifact. Outcomes must be relevant to the Purpose and, together, sufficient to satisfy it. Review must check both relevance and collective sufficiency. A description of how success will be judged is not evidence that success has occurred.

An **Output** is a product, information item, or service produced or updated by the work. An Output can evidence an Outcome, but its existence alone must not be treated as success. Work need not produce a fixed artifact. For example, an explanation is an Output; the recipient's demonstrated understanding is an Outcome.

## 3. Necessary detail and execution means

Activities, Tasks, Inputs, Outputs, Controls, Constraints, Enablers, and Entry/Exit Criteria are optional. They must be included only where needed to understand, apply, or evaluate the work. A description must not contain empty optional sections or completeness-driven “Not applicable” fields. Context, ID, and version are not universally required fields. When the necessary scope is unclear, it must be clarified where it matters; a separate context section is not required.

An **Activity** groups related actions. A **Task** describes an action contributing to an Outcome, with its operation and object identifiable. A Task's force must be clear. When work detail is included, review must check how it supports the Outcomes and expose any uncovered result conditions; no fixed decomposition or mapping table is required.

General descriptions must avoid unnecessarily fixing performers, tools, methods, or order. A method or sequence genuinely required in a particular context may be stated as an applicable condition, with that scope made clear. Document order must not be interpreted as execution order. A required dependency must be explicit. Other work may proceed iteratively, concurrently, or at multiple levels when appropriate; no execution pattern is mandatory.

Divide work only where separate treatment makes its purpose, success, or boundary clearer. A difference in tool or performer alone does not require a separate Process. Necessary boundaries with adjacent work must be understandable without forcing every description into a lifecycle model.

## 4. Conditions and information relationships

Classify an element by its function in the described work, not its filename, medium, or directory.

| Element | Function |
| --- | --- |
| **Input** | Information or another item examined, used as source material, or transformed by the work. |
| **Output** | A product, information item, or service produced or updated by the work. |
| **Control** | Directs the work or supplies the criteria by which it is judged. |
| **Constraint** | Limits permitted action or conditions of application. |
| **Enabler** | Supplies capability or resources that make the work possible. |

A policy used as a criterion is a Control; a policy being revised is an Input. People, Agents, tools, and environments used to perform the work are Enablers. A limitation on their use is a Constraint. The same resource can play different roles; those roles must not be confused.

**Entry Criteria** specify conditions for starting the affected work. **Exit Criteria** specify conditions for declaring it complete. Required conditions and approvals must be confirmed before the actions they govern. If they are missing or unconfirmed, the affected action must not proceed. Independent analysis or drafting may continue within the authorized scope. Completion of an Output must not stand in for assessment of the Outcomes.

Processes may exchange information or repeatedly consult and update the same information. For a relationship needed to understand, apply, or evaluate the work, the description must make the information's meaning, scope, conditions of use, and relevant change impacts clear. Identify which work reads or changes it and which decisions or results need reconsideration after a change. Shared information must not be reduced to a single serial handoff when that misrepresents the work. Storage, coordination, and change mechanisms are supplied by the environment.

## 5. Authority, references, and views

The authoritative description must be uniquely identifiable using ordinary links or identifying information. When reproducibility is needed, identify the applicable environment version, commit, digest, or equivalent alongside the reference. Each necessary reference must identify its intended target. If that target cannot be confirmed, report the missing reference and affected scope as unconfirmed; do not substitute a same-named document or another version.

Summaries, translations, examples, and views must not silently change the authoritative meaning or normative force. They must identify their sources where needed to distinguish source content from interpretation or local additions. A translation is not a second authority.

A **Process Model**, **Reference Model**, or **View** may be ordinary reference material that organizes relationships or presents a concern across descriptions. It must refer to the source Process Descriptions and must not maintain duplicated Purpose or Outcome definitions for management. A view can select and explain source elements without changing them. Local proposals must be distinguished from source requirements. A change in presentation alone must not change the work's obligations or success conditions.

Non-Process reference material must not be treated as a Process merely because it is loaded by an Agent or displayed alongside Skills. When independently defined work is needed, describe its own Purpose and Outcomes. No special type metadata or invocation system is required.

## 6. Change

Distinguish a change to the authoritative description, a context-limited change to what applies, and a change in presentation. A change must identify the affected source and elements, scope, rationale, consequences, and necessary revalidation in enough detail to prevent confusion between the original and the changed meaning. A contextual interpretation that leaves meaning unchanged is not itself a change to the source.

Authority and approval follow applicable environment conditions. No particular management Skill is required. A context-limited change must not silently redefine the source, remove an externally imposed requirement, or imply authority to waive a prohibition. Revalidation must address affected Outcomes, conditions, references, shared information, and translations where relevant. Its results and unresolved limits must be explicit. The environment determines how these facts are retained; no fixed change record is required.

## 7. Evaluation and uncertainty

An evaluation must identify what is evaluated, its scope, the applicable criteria, the evidence considered, and the resulting judgment. Evidence supports a judgment; it is not the judgment itself. Keep the following questions distinct:

| Subject | Question |
| --- | --- |
| Description validity | Are the purpose, success conditions, boundaries, references, and necessary detail coherent and usable? |
| Execution result | What actually happened in this application, and which Outcomes were achieved? |
| Satisfaction of requirements | Were the applicable mandatory conditions and prohibitions respected? |

A successful description review must not be reported as successful execution. Successful execution must not be inferred merely from a produced artifact, an approval, or passed format checks. Representative examples or trials can support applicability judgments but must not be reported as proof for every context.

Unconfirmed facts, assumptions, unmet conditions, and exclusions must remain distinguishable. An exclusion needs an applicability rationale; missing evidence is not a reason to mark a requirement inapplicable. None of these conditions may be silently converted into success. Findings must expose evidence gaps and their consequences. ALPS defines no assessment status enum, diagnostic schema, or certification claim.
