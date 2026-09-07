---
name: design-process-description
description: Create, revise, or review a Process Description that makes the purpose, observable success conditions, and necessary boundaries of work clear. Use for general or context-specific work when its meaning or evaluation needs clarification.
---

# Process Description Design

## Purpose

Clarify the purpose and success conditions of the target work as an understandable, applicable, and evaluable Process Description with necessary and sufficient boundaries and detail.

## Outcomes

- The target work is identified by its purpose, applicable scope, and boundaries with adjacent work.
- Success conditions are described as observable result states individually necessary and collectively sufficient for the purpose.
- The description contains the detail needed to understand, apply, and evaluate the work.
- Execution means remain open except where applicable conditions require them.
- The description's consistency with the Framework and required references is clear.
- Unconfirmed matters and limits of application are explicit.

## Activities & Tasks

The Tasks below are required within the requested scope, except where stated as recommendations. Their relationships support revisiting the description as understanding develops.

### Work framing

1. Identify the requested scope and the available description or information about the target work.
2. Clarify the work's purpose and its boundary with adjacent work using the necessary information from affected parties. Confirm that information's source and applicability, and identify any gaps.
3. Identify uncertainties that could change the intended scope or success conditions.

### Success and work description

1. Formulate observable Outcomes that are individually necessary and collectively sufficient for the Purpose. Keep independently assessable results distinguishable.
2. Determine the detail needed to understand, apply, or evaluate the work. Where work detail is needed, organize related actions into Activities and Tasks at a useful granularity and check their contribution to the Outcomes.

    > NOTE Activities group related work, while Tasks state individual actions. The [Production Release example](references/examples.md#production-release) shows this structure with explanatory notes attached to the relevant work.

3. Describe necessary Inputs, Outputs, Controls, Constraints, Enablers, and Entry/Exit Criteria by their function. Preserve required methods and dependencies with their scope and leave other execution choices open.
4. For Markdown, apply the Framework's writing rules. When the target is an Agent Skill, use the body for the Process Description and the frontmatter for its discovery identifier and summary of the work and when it applies. Keep the frontmatter and Host displays consistent with the description's meaning and scope.

### Source and relationship alignment

1. Identify the description used as the reference point for meaning and confirm required references against their intended sources. Make the roles and conditions of required resources clear, and distinguish reference material from descriptions of work. For a Skill, verify that packaged links resolve in the intended distribution and that external references identify their sources and access conditions.
2. Clarify the meaning, use, and change effects of information shared with related work, including which work reads or updates it.
3. For changes, establish the affected description and elements, scope, rationale, consequences, and necessary revalidation. Distinguish a change to the description used as the reference point for meaning, a context-limited change, an application-specific choice, and a change in presentation.
4. For Process selection or changes to Process meaning, evaluate proposed choices against the Purpose and applicable conditions using the evidence needed to justify the decision.

### Description evaluation

1. Evaluate the description against the Framework and applicable contextual requirements, including the coherence of its elements and the coverage of its Outcomes. Confirm that the criteria and evidence apply to the description and context being reviewed. Re-evaluate affected judgments when their supporting information or conditions change.

    > NOTE In this design work, the Framework and applicable requirements supply Controls. Reading, search, and format-checking capabilities supply Enablers; format-check results provide evidence about the aspects they check. Coherence and Outcome sufficiency also depend on interpretation of the work and its conditions.

2. Representative cases should be examined when they can expose ambiguity, unsupported success conditions, or limits of application.
3. Findings should guide further revision or review within the requested scope.
4. Report findings with their evidence and affected scope, including remaining defects and unconfirmed matters. In a review, assess these Outcomes in the supplied description; identifying a defect does not satisfy the condition that remains unmet.

## Controls

Apply the [Process Framework](references/process-framework.md) for meaning and Markdown presentation. For Agent Skill targets, apply the [Agent Skills specification](https://agentskills.io/specification) to the physical format. These sources are required within their subjects. The user's request and applicable environment conditions govern the scope of changes.

## Constraints

A review-only request must be answered with findings and any requested corrections, without unsolicited wholesale revision. Performing the described work or changing external state requires the applicable authorization. An unconfirmed reference or condition must limit the dependent judgment or action; independent work may continue within its applicable conditions.

## Resources

This root `SKILL.md` is the English source for the [Japanese translation](references/locales/ja/SKILL.md), which carries the same meaning and normative force.

- [Minimal template](references/SKILL-template.md): use when drafting an Agent Skill.
- [Examples and review cases](references/examples.md): consult relevant cases when choosing work detail, describing shared information or views, or evaluating incomplete evidence.
- [Agent Work System Design](../design-agent-work-system/SKILL.md): use when the requested work concerns the supporting configuration, its implementation, or its effectiveness. Refer to the shared work description; revisit it when configuration design reveals a problem with its assumptions.
