---
name: define-alps
description: Identify Skill needs; design and verify assessable Skill Descriptions that conform to ALPS and the Process Framework. Use when conceiving a new Skill, redefining an existing Skill, designing its Purpose, Outcomes, Activities, or Tasks, reviewing description conformance, trialing it in representative contexts, establishing traceability, or producing evidence for an adoption decision. Use the management process when the work concerns only adoption, change control, or retirement. ALPS-conformant.
---

# Agent Lifecycle Process Skill Definition

## Purpose

This Skill establishes an assessable and usable Skill Description that satisfies identified stakeholder needs.

## Outcomes

Success of this Skill establishes the following conditions.

- a) The need to be addressed as a Skill and the intended contexts of use are identified.
- b) The Skill Purpose, Outcomes, and boundary are aligned with the selected need.
- c) The Skill Description satisfies the applicable ALPS description requirements.
- d) Elements within the Skill Description and exchanges with external parties are traceable.
- e) The achievability of the Outcomes in representative contexts of use is confirmed.
- f) A decision on Skill adoption can be made from evidence that includes defects and limitations.

## Activities & Tasks

The following headings, Activities, Tasks, and numbers present the content for readability; they do not prescribe a procedure or execution sequence. Entry Criteria are conditions evaluated before invocation, and Exit Criteria are conditions evaluated before declaring completion. Controls and Constraints apply regardless of where they appear. Use Iteration, Concurrency, and necessary redesign as appropriate to the context of application.

### Skill Need Identification

This Activity explores candidates for treatment as Skills and selects the need to be defined. It primarily contributes to Outcomes a) and b).

1. Opportunities for Skills are typically collected from recurring Tasks, lessons learned, and failure cases.
2. The expectations of intended users and stakeholders must be identified.
3. Existing Skill assets should be investigated to identify duplication, adjacency, or gaps.
4. Expected benefits, risks, and costs should be evaluated for each candidate.
5. The rationale for selection and deferral should be recorded.
6. Candidates may be prioritized by frequency of use or impact when selecting a need.

### Skill Design

This Activity determines the structure and content of a Skill Description that satisfies the selected need. It primarily contributes to Outcomes b), c), and d).

1. The Skill boundary must be established from the primary Outputs and Outcomes.
2. Dependencies on other Skills must be reduced as far as practicable.
3. The Skill Description must provide distinguishable discovery-layer and execution-layer information. Their physical separation is not required.
4. A significant Activity that benefits from detailed treatment may be separated into another Skill.
5. Name, Purpose, and Outcomes must be written in accordance with the applicable description rules.
6. Each Task must have the primary function of expressing an individual action that supports achievement of one or more Outcomes and must be written so that the object and operation of that action are distinguishable.
7. Each statement must be classified under the Skill element corresponding to its primary function.
8. Each Task must be assigned the normative attribute of requirement, recommendation, permissible action, or typical action.
9. Guidance on how to apply the Skill should be separated as Common Approach and practical tips.
10. It must be confirmed that the set of Activities covers all Outcomes and satisfies the Purpose.
11. Relationships between Tasks and Outcomes should be identified.
12. The Skill Discovery Description must state what the Skill does, when it is used, and the information needed to determine applicability. A Skill Discovery Description claiming ALPS Description Conformance must end with `ALPS-conformant.`
13. When representative Inputs and Outputs are shown, the principal relationships with other Skills or Processes should be identified as needed.
14. When a Skill Package is composed, the need, role, and conditions of use for its accompanying resources must be identified.

### Skill Verification

This Activity confirms the descriptive conformance of the Skill Description and the achievability of its intended Outcomes. It primarily contributes to Outcomes c), d), e), and f).

1. The Skill Description must be reviewed using agreed criteria.
2. It must be confirmed that each Task has the primary function of expressing an individual action that supports achievement of one or more Outcomes and that the object and operation of that action are distinguishable.
3. It must be confirmed that the element classification of each statement is consistent with its primary function.
4. It must be confirmed that normative attributes are distinguishable.
5. When a general Skill is verified, it must be confirmed that its normative part does not require a specific method, technique, tool, or execution sequence.
6. It must be confirmed that the discovery-layer and execution-layer information are consistent.
7. The review should incorporate a perspective independent of the Skill author.
8. The achievability of the Outcomes should be evaluated through trials in representative contexts of use.
9. It should be evaluated whether applicability can be determined from discovery-layer information alone, including the Skill Discovery Description.
10. Boundary cases from the intended contexts of use may be included in the evaluation.
11. Detected defects should be recorded, and actions with due dates and completion conditions should be established.
12. Completion of defect treatment should be confirmed before the Decision Gate for the adoption decision.
13. When the Skill Description identifies an exchange with another Skill or Process, it should be evaluated whether the Output can be used as the intended recipient's Input.
14. When the Skill Package is included in the verification scope, the existence of the authoritative Skill Description, resolvability of mandatory references, roles and conditions of use of accompanying resources, and consistency between the Skill Description and those resources must be evaluated.

## Inputs

The following are representative Inputs and do not prescribe the only manner of execution.

Stakeholder expectations, lessons learned, information about execution performance, applicable Controls and Constraints, information about existing Skill assets, verification criteria, and representative contexts of use.

## Outputs

The following are representative Outputs and do not prescribe the only manner of execution.

The selected Skill need and selection rationale, verified Skill Description, record of mappings among elements, verification results, and record of defect treatment.

## Entry Criteria

- A need, problem, lesson, or change request for which Skill definition or redefinition is being considered is available.
- Intended users, stakeholders, and representative contexts of use can be identified.
- Applicable Controls, Constraints, and higher-order norms can be identified, or their absence can be recorded as an unresolved matter.
- It can be determined whether the scope is the Skill Description alone or also the Skill Package with accompanying resources.

## Exit Criteria

- Achievement against the selected Conformance criteria has been determined with observable evidence.
- Unresolved defects, limitations, assumptions, and boundary cases are recorded.
- The verified Skill Description, traceability, and verification results can be transferred for an adoption decision or management.
- Completion does not mean adoption or publication; it means that adoption can be decided.

## Controls

- Apply the Process Framework and ALPS. If they conflict, the Process Framework must take precedence.
- The normative words and their meanings are those defined in the Process Framework. This Skill does not redefine them.
- The applicable clauses of [process-framework.md](../../.alps/spec/process-framework.md) and [ALPS-SPEC.md](../../.alps/spec/ALPS-SPEC.md) must be consulted when interpreting a Process Framework or ALPS requirement, confirming a normative attribute, determining Conformance, or changing this Skill.
- The Name must be a short noun phrase that distinguishes the Skill from other Skills. The Name must not summarize the Purpose.
- The Purpose must state the high-level objective or objectives that belong together.
- The Purpose should be stated concisely in one sentence wherever possible.
- Each Outcome must state one positive, observable, and assessable result condition, rather than the creation of an Output.
- The Outcome set must contain all and only the results needed to achieve the Purpose.
- The set of Activities and any separated Skills must cover all Outcomes. Activities may map to Outcomes on a basis other than one to one.
- Each sentence should address only one meaning.
- Reference information must not alter the meaning or normative force of the primary elements.
- Applicable laws, regulatory requirements, policies, voluntary standards, and agreements must be applied within their declared scope.
- Rules for Skill creation, verification, and saving that are effective in the execution environment must be followed.

## Constraints

- A general Skill must not normatively fix a specific performer, Task allocation, method, tool, metric, or execution sequence.
- Agents, models, tools, and execution environments must not be treated as Inputs. They must be treated as Enablers.
- A Decision Gate must not be treated as a component of a Skill Description. It must be treated as a separate decision mechanism that controls adoption, hold, change, re-execution, or termination.
- Mandatory references must be resolvable. Unnecessary duplication or conflict must not arise between the Skill Description and accompanying resources.

## Enablers

- Stakeholder and domain expertise
- Managed Skill assets and change history
- Agents or tools that support drafting, comparison, search, and trials
- Review capability independent of the author
- Mechanical pre-checking with `scripts/check_skill_description.py`

## Conformance

- When Conformance is claimed, the subject, scope, and whether the criteria are Outcomes, Tasks, or both must be stated.
- Full Conformance to Outcomes must demonstrate achievement of every Outcome listed in the Outcomes section. Activities and Tasks are treated as guidance.
- Full Conformance to Tasks must demonstrate satisfaction of every requirement stated with must or must not by an Activity or Task. Outcomes are treated as guidance.
- Tailored Conformance may be claimed for a Skill or Process that does not satisfy the selected Full Conformance criteria. The claim must declare the Skill or Process tailored in accordance with Skill Tailoring in the ALPS management process and its scope of application. It must also demonstrate satisfaction of every Outcome and Activity/Task requirement remaining within that scope.
- Independent Process Outcome Conformance must not be claimed for an individual Activity alone.

## Interfaces & Traceability

| Information item provided | Primary recipient | Related information |
|---|---|---|
| Verified Skill Description | Skill Asset Management | Adoption subject, version, conditions of application, and verification results. |
| Verification results and defect treatment | Adoption Decision Gate | Decision criteria, evidence, unresolved limitations, and the decision. |
| Task–Outcome mapping | Assessment or reverification | Tasks, Outcomes, evidence, and status. |
| Redefinition and reverification results | Skill management | Change request, affected scope, and post-change evidence. |

When an Output becomes another Skill's Input, their names, meanings, and scopes should be aligned.

## Shared Normative References

This section identifies repository-level normative assets and does not require a specific manner of execution.

- Use the repository-shared [Process Framework](../../.alps/spec/process-framework.md) as the higher-order normative source for Process Descriptions. It takes precedence if it conflicts with ALPS.
- Use the repository-shared [ALPS Specification](../../.alps/spec/ALPS-SPEC.md) to confirm ALPS normative requirements. Consult the relevant clauses according to the interpretation needed.

## Bundled Resources

This section is reference information and does not require a specific manner of execution.

- This root `SKILL.md` is the authoritative English Skill Description. For Japanese-language work, use the [Japanese localization](references/locales/ja/SKILL.md) and its adjacent localized resources. Respond in the user's language; if the localization conflicts with this file, this English description governs.
- When drafting an ALPS-conformant Skill Description, [SKILL-template.md](references/SKILL-template.md) can be used as an informative example. Select the structure to apply according to the Purpose and required level of detail.
- When designing the composition of a Skill Package and the roles of accompanying resources, [skill-package-format.md](references/skill-package-format.md) can be used as an informative example. Adopt only the resources that are needed.
- When producing a formal need record, Skill Description, traceability table, verification record, or adoption-decision record, [record-templates.md](references/record-templates.md) can be tailored to the subject of application.
- For the representative Markdown Environment Binding used by this Package, `python3 scripts/check_skill_description.py <SKILL.md>` can pre-check YAML frontmatter, canonical headings, and related structural signals. Those representations are binding-specific rather than ALPS requirements; the script does not by itself demonstrate Conformance or achievement of Outcomes.

## Common Approach

This section is reference information and has no normative force.

- Comparing needs, failure cases, and gaps in existing assets in one candidate register makes it easier to retain the selection rationale.
- Decomposing backward from Outcomes into Activities and Tasks, then tracing from Tasks back to Outcomes, makes omissions and excess easier to find.
- Separating a selection test that shows only the discovery layer to a third party from a representative-task trial that uses the execution layer makes each layer easier to evaluate.
- Including boundary cases, ambiguous Inputs, missing Enablers, and conflicting Controls in trials makes invocation conditions and limitations easier to refine.
- When behavior can vary across executions, judging Outcome achievability from repeated trials rather than a single run, and recording observed variation and the limits of the evidence, gives the adoption decision a firmer basis.
- When a unique expected result cannot be defined, stating acceptance conditions, prohibited conditions, or an evaluation method gives verification an observable basis.
