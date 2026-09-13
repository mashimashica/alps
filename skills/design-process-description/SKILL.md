---
name: design-process-description
description: Create, revise, or review a Process Description—the Purpose, observable Outcomes, boundaries, and necessary detail of work—including the body of an Agent Skill's SKILL.md. Use when defining or reviewing what work must achieve and how success is judged; designing the agents, tools, and environment that carry out the work is outside this Skill.
---

# Process Description Design

## Purpose

Make the purpose and success conditions of the target work clear, as distinct from the configuration that performs it, through an understandable, applicable, and evaluable Process Description with necessary and sufficient boundaries and detail, or through findings about such a description.

## Outcomes

- The target work's Purpose and applicable scope, and its boundaries where adjacent work overlaps or the boundary is otherwise ambiguous, are identified in the description, or findings identify what is not identified.
- The description's Outcomes are observable result conditions individually necessary and collectively sufficient for the Purpose, or findings identify each unmet property.
- The description contains the detail needed to understand, apply, and evaluate the work and no detail that serves none of these, or findings identify missing or superfluous detail.
- Execution means remain open except where applicable conditions require them, or findings identify unnecessary fixing.
- Where the request involves changes, their affected elements, scope, rationale, consequences, and necessary revalidation are identified, or findings identify what remains unidentified.
- Where the request involves Process selection or changes to Process meaning, the choice is justified against the Purpose and applicable conditions, or findings identify what remains unjustified.
- The description's consistency with the Framework and required references is established or qualified by explicit findings.
- Unconfirmed matters and limits of application are explicit.

## Activities & Tasks

The Tasks below are required within the requested scope, except where stated as recommendations. Their relationships support revisiting the description as understanding develops.

### Work framing

1. Read the Process Framework and required references in full.
2. Identify the requested scope and the available description or information about the target work.
3. Clarify the result the work undertakes to establish and its boundary with adjacent work using the necessary information from affected parties. Distinguish that responsibility from benefits or results belonging to other work.
4. Confirm the source and applicability of that information and identify gaps; ask the requester where a gap could change the scope or success conditions and cannot be resolved from available information.
5. Identify uncertainties that could change the intended scope or success conditions.

### Success and work description

1. Formulate observable Outcomes that are individually necessary and collectively sufficient for the Purpose. Keep independently assessable results distinguishable.
2. Include detail where its absence would impair understanding, application, or evaluation; remove or combine repetitions that add none of these. Where work detail is needed, organize related actions into Activities and Tasks at a useful granularity and check their contribution to the Outcomes.
3. Describe necessary Inputs, Outputs, Controls, Constraints, Enablers, and Entry/Exit Criteria by their function. Preserve required methods and dependencies with their scope and leave other execution choices open.
4. For Markdown, apply the Framework's writing rules. When the target is an Agent Skill, use the body for the Process Description and the frontmatter for its discovery identifier and summary of the work and when it applies. Keep the frontmatter and Host displays consistent with the description's meaning and scope.

### Source and relationship alignment

1. Identify the description used as the reference point for meaning and confirm required references against their intended sources. Make the roles and conditions of required resources clear, and distinguish reference material from descriptions of work. For a Skill, verify that packaged links resolve in the intended distribution and that external references identify their sources and any access conditions.
2. Clarify the meaning, use, and change effects of information shared with related work, including which work reads or updates it.
3. For changes, establish the affected description and elements, scope, rationale, consequences, and necessary revalidation. Distinguish a change to the description used as the reference point for meaning, a context-limited change to what applies, and a change in presentation; distinguish all of these from a context-specific choice the description already permits, which is not a change to it.
4. For Process selection or changes to Process meaning, evaluate proposed choices against the Purpose and applicable conditions using the evidence needed to justify the decision.

### Description evaluation

1. Evaluate the description against the Framework and applicable contextual requirements, including the coherence of its elements, whether Activities and Sub-processes describing the work as a whole cover every Outcome and contribute to the Purpose, and whether those describing only selected work identify the Outcomes they support. Confirm that the criteria and evidence apply to the description and context being reviewed.
2. Re-evaluate affected criteria, evidence, and judgments when changed information or conditions affect their basis.
3. Representative cases should be examined when they can expose ambiguity, unsupported success conditions, or limits of application, with effort proportionate to consequences, uncertainty, and complexity. Hold the Purpose, responsibility, scope, and applicable conditions fixed when considering counterexamples: could all Outcomes hold without fulfilling the Purpose, or could the Purpose be fully fulfilled without one of them? Could an Output exist or processing succeed while an Outcome does not hold? A changed responsibility is not a counterexample within the original scope; finding none does not prove sufficiency for every case.
4. Use findings to decide the further revision or review needed within the requested scope.
5. Report findings with evidence and affected scope. Distinguish confirmed nonachievement from missing evidence and justified inapplicability; retain supported results and useful partial work without treating them as full success. In a review, assess these Outcomes in the supplied description; a finding qualifies an Outcome by identifying the unmet condition, but it does not make the description meet that condition.

## Controls

Apply the [Process Framework](references/process-framework.md) for meaning and Markdown presentation. For Agent Skill targets, apply the [Agent Skills specification](https://agentskills.io/specification) to the physical format. These sources are required within their subjects.

## Constraints

Changes must remain within the user's request and applicable environment conditions. A review-only request must be answered with findings and any requested corrections, without unsolicited changes. In creation or revision, findings may qualify an Outcome only for a condition that cannot be met within the requested scope, available information, or authority. Performing the described work or changing external state requires the applicable authorization. An unconfirmed reference or condition, including content of the Framework or a required reference that has not been read, must limit the dependent judgment or action; independent work may continue within its applicable conditions.

## Resources

This root `SKILL.md` is the English source for the [Japanese translation](references/locales/ja/SKILL.ja.md), which carries the same meaning and normative force.

- [Minimal template](references/SKILL-template.md): use when drafting an Agent Skill.
- [Examples and review cases](references/examples.md): consult relevant cases when checking success conditions, choosing work detail, describing shared information or views, or evaluating incomplete evidence.
