---
name: design-agent-work-system
description: Design, revise, or review the agents, tools, information resources, and execution environment that realize work. Use when choosing capabilities, allocating judgment and processing, designing tool interfaces, or assessing an agent work system; include implementation, connections, and verification within the request.
---

# Agent Work System Design

## Purpose

Design the configuration and interaction of agents, tools, information resources, and execution environments suited to the target work and its applicable conditions, and establish its feasibility and effectiveness.

## Outcomes

- The configuration's responsibilities and interactions cover the target work under its applicable conditions.
- The allocation of judgment and processing is justified by the work and the available capabilities.
- Interfaces and information supply are sufficient for the required interactions and interpretation of results.
- The realization within the requested scope meets its specified behavior, supported by applicable evidence.
- Judgments of feasibility and effectiveness are supported by the examined work, with assumptions, unconfirmed matters, and limits explicit.

## Activities

The following Tasks are required within the requested scope, except where stated as recommendations. Their relationships allow the design to be revisited as evidence changes.

### Establishing the design basis

- Identify the target work's source description, applicable conditions, available capabilities, and the requested extent of design, implementation, and evaluation. Confirm the information needed from affected parties and identify gaps that limit dependent decisions.
- Determine whether the work description is sufficient for the requested design. Refer to its meaning and success conditions instead of maintaining a second copy. Revisit the affected description when design exposes a problem with its assumptions; preserve its meaning unless a change is within scope and justified.

### Configuring responsibilities and interactions

- Assess existing agents, tools, resources, and environments for the required capabilities. Allocate contextual interpretation, selection, and composition to agents where needed, and established processing and decision rules to suitable implementations.
- Define component responsibilities and interfaces, information sources and conditions, and responses to results and failures. Distinguish internal module boundaries from operations exposed to an agent. Combine stable operations where useful and preserve meaningful choices.
- Identify gaps requiring a new or adapted method, tool, or connection. Judge boundaries by cohesion, change effects, and ease of use, composition, and verification.

### Realizing the requested configuration

- Within the requested scope, implement and connect the necessary capabilities using the applicable environment. Make tool use, dependencies, result interpretation, failure handling, and state-changing effects available where they are needed.
- For a target Skill, reflect its required tool use and conditions in `SKILL.md` and necessary resources. Put bundled business processing in that target Skill's `scripts/`; tools for design or evaluation belong with the design work they support.
- Confirm required conditions before dependent operations. Address uncertain or partial effects before retrying an operation that changes state.

### Evaluating and adjusting the system

- Review the design's responsibilities, relationships, and conditions against the target work. Check the components and connections against their specified behavior, including relevant failures and incomplete results.
- Evaluate representative work using the intended agent, tools, information, and environment to the extent authorized and available. Assess the work's Outcomes against evidence and applicable conditions, distinguishing them from tool completion and generated Outputs.
- Reconsider instructions, information supply, public operations, and allocation where evidence or changed capabilities warrants it. Preserve work-specific knowledge and conditions while reviewing guidance that compensates for capability limits. Revalidate affected behavior.
- Report each judgment's subject, criteria, evidence, scope, unperformed checks, and unresolved findings. In a review, assess these Outcomes in the supplied design; finding a defect does not satisfy the condition that remains unmet.

## Controls

Apply the [Process Framework](../../spec/process-framework.md) to this Process Description, [Design Principles for Agent Work Systems](../../spec/agent-work-system-design.md) to its design subject, and the [ALPS Specification](../../spec/ALPS-SPEC.md) to their integration in Skills. These are required sources. The target work description, the user's request, and applicable environment conditions govern the design's scope.

## Constraints

A review-only request must return findings and any requested corrections without unsolicited changes. Performing the target work is a separate application and must remain within the applicable authorization. Missing references or unconfirmed conditions must limit dependent actions and judgments; independent analysis or drafting may continue within its own conditions. Unperformed evaluation must remain unconfirmed.

## Resources

This root `SKILL.md` is the English source for the [Japanese translation](references/locales/ja/SKILL.md), which preserves its meaning and normative force.

- [Design prompts and examples](references/examples.md): use relevant prompts and cases to develop or review a configuration.
- [Working example](../../examples/README.md): inspect a target Skill with a processing script, conditions, and evaluation cases.
- [Process Description Design](../design-process-description/SKILL.md) and its [minimal template](../design-process-description/references/SKILL-template.md): use when the work's meaning needs clarification or an Agent Skill description needs to be authored.
