---
name: design-process-description
description: Create, revise, or review a Process Description that makes the purpose, observable success conditions, and necessary boundaries of work clear. Use for general or context-specific work, including one-off work, when its meaning or evaluation needs clarification.
---

# Process Description Design

## Purpose

Clarify the purpose and success conditions of the target work as an understandable, applicable, and evaluable Process Description with necessary and sufficient boundaries and detail.

## Outcomes

- The target work's purpose, applicable scope, and boundaries with adjacent work are identified.
- Success conditions are described as observable result states relevant to the purpose.
- Necessary detail is present, and unnecessary fixation of execution means is avoided.
- Consistency, references, unconfirmed matters, and limits of application are clear.

## Tasks

These actions concern the same description and can be revisited as understanding changes; their order is not an execution sequence.

- The requested scope and available target description or work information must be identified. A review-only request must be answered with findings and any requested corrections, without unsolicited wholesale revision.
- The intended purpose and result conditions must be clarified from the available information. Material uncertainty about scope or adjacent work must be exposed rather than filled by conjecture.
- Each Outcome must be reviewed for observability and relevance, and the set for sufficiency to satisfy the Purpose. Distinguish creating an Output from establishing the condition it is meant to support.
- Necessary detail must be assessed using the Framework. Add or retain it only where it changes understanding, application, or evaluation. Preserve contextually necessary methods, approvals, and order with their scope; remove unnecessary prescriptions when revision is requested.
- Required references, relationships, and conditions must be checked. For shared information, identify its meaning, use, readers or updaters, and the effect of changes on related work where material.
- For a revision, the authoritative source, affected scope, rationale, impact, and needed revalidation must be clear. Distinguish source changes, context-limited changes, and presentation changes.
- The resulting description or review must be assessed against the requested scope. Report the judgment and its supporting evidence, remaining defects, assumptions, unconfirmed references, and applicability limits. For a review, evaluate these Outcomes in the supplied description; do not report a defect as repaired merely because it was identified.
- Representative cases should be examined when they can expose an ambiguity or unsupported success condition. A trial that performs the target work requires the applicable authorization; an example alone does not establish execution success or universal applicability.

## Controls

Apply the [Process Framework](../../spec/process-framework.md) for meaning and the [ALPS Specification](../../spec/ALPS-SPEC.md) for Agent Skill representation. These sources are required; the Framework takes precedence. Apply the user's requested scope and the environment's applicable conditions for changes and external actions.

## Constraints

Designing or reviewing a description does not authorize executing the target work, approving its use, publishing it, or changing external state. If a required source or condition is unconfirmed, identify the affected judgment or action and its limitation. Independent review or drafting may continue within the authorized scope. Review completion must not be reported as execution success or as evidence that every design Outcome is satisfied.

## Resources

This root `SKILL.md` is the authoritative English description. For Japanese-language work, use the [Japanese translation](references/locales/ja/SKILL.md) with the same meaning and normative force.

- [Minimal template](references/SKILL-template.md): use when drafting an Agent Skill; begin with only its required core.
- [Examples and review cases](references/examples.md): consult relevant cases when deciding whether detail is necessary, describing shared information or views, or judging incomplete evidence.
- `agents/openai.yaml` and `assets/alps.svg`: Host presentation resources; they add no Process requirements.
