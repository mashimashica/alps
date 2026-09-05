---
name: design-process-description
description: Create, revise, or review a Process Description that makes the purpose, observable success conditions, and necessary boundaries of work clear. Use for general or context-specific work when its meaning or evaluation needs clarification.
---

# Process Description Design

## Purpose

Clarify the purpose and success conditions of the target work as an understandable, applicable, and evaluable Process Description with necessary and sufficient boundaries and detail.

## Outcomes

- The target work is identified by its purpose, applicable scope, and boundaries with adjacent work.
- Success conditions are described as observable result states relevant to and collectively sufficient for the purpose.
- The description contains the detail needed to understand, apply, and evaluate the work.
- Execution means remain open except where applicable conditions require them.
- The description's consistency with the Framework and required references is clear.
- Unconfirmed matters and limits of application are explicit.

## Activities

The Tasks below are required within the requested scope, except where stated as recommendations. Their relationships support revisiting the description as understanding develops.

### Work framing

- Identify the requested scope and the available description or information about the target work.
- Clarify the work's purpose and its boundary with adjacent work from that information.
- Identify uncertainties that could change the intended scope or success conditions.

### Success and work description

- Formulate observable Outcomes that are relevant to and collectively sufficient for the Purpose. Keep independently assessable results distinguishable.
- Determine the detail needed to understand, apply, or evaluate the work. Where work detail is needed, organize related actions into Activities and Tasks at a useful granularity and check their contribution to the Outcomes.
- Describe necessary Inputs, Outputs, Controls, Constraints, Enablers, and Entry/Exit Criteria by their function. Preserve required methods and dependencies with their scope and leave other execution choices open.

### Source and relationship alignment

- Identify the authoritative description and confirm required references against their intended sources.
- Clarify the meaning, use, and change effects of information shared with related work, including which work reads or updates it.
- For changes, establish the affected source and elements, scope, rationale, consequences, and necessary revalidation. Distinguish a source change, a context-limited change, an application-specific choice, and a change in presentation.

### Description evaluation

- Evaluate the description against the Framework and applicable contextual requirements, including the coherence of its elements and the coverage of its Outcomes.
- Representative cases should be examined when they can expose ambiguity, unsupported success conditions, or limits of application.
- Report findings with their evidence and affected scope, including remaining defects and unconfirmed matters. In a review, assess these Outcomes in the supplied description; identifying a defect does not satisfy the condition that remains unmet.

## Controls

Apply the [Process Framework](../../spec/process-framework.md) for meaning and the [ALPS Specification](../../spec/ALPS-SPEC.md) for Agent Skill representation. These sources are required; the Framework takes precedence. The user's request and applicable environment conditions govern the scope of changes.

## Constraints

A review-only request must be answered with findings and any requested corrections, without unsolicited wholesale revision. Performing the described work or changing external state requires the applicable authorization. An unconfirmed reference or condition must limit the dependent judgment or action; independent work may continue within its applicable conditions.

## Resources

This root `SKILL.md` is the authoritative English description. The [Japanese translation](references/locales/ja/SKILL.md) carries the same meaning and normative force.

- [Minimal template](references/SKILL-template.md): use when drafting an Agent Skill.
- [Examples and review cases](references/examples.md): consult relevant cases when choosing work detail, describing shared information or views, or evaluating incomplete evidence.
