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

## Activities & Tasks

The following Tasks are required within the requested scope, except where stated as recommendations. Their relationships allow the design to be revisited as evidence changes.

### Establishing the design basis

1. Identify the target work's source description, applicable conditions, available capabilities, and the requested extent of design, implementation, and evaluation. Confirm the information needed from affected parties and identify gaps that limit dependent decisions.
2. Determine whether the work description is sufficient for the requested design. Refer to its meaning and success conditions instead of maintaining a second copy. Identify which descriptions and Skills the configuration supports; either may be supported by different configurations. Revisit the affected description when design exposes a problem with its assumptions; preserve its meaning unless a change is within scope and justified under the Framework's change principles.

### Configuring responsibilities and interactions

1. Assess existing agents, tools, resources, and environments for the required capabilities. Allocate contextual interpretation, selection, and composition to agents where needed, and established processing and decision rules to suitable implementations.
2. Define component responsibilities and interfaces, information sources and conditions, and responses to results and failures. Distinguish internal module boundaries from operations exposed to an agent. Combine stable operations where useful and preserve meaningful choices.
3. Relate the agents, tools, and environment to the work as Enablers, and identify each information resource's role using the Framework. Explain how tool operations contribute to the Tasks and how their results support Outcome assessment. Design Task boundaries and tool interfaces for their respective responsibilities; relate Process Inputs and Outputs to arguments and returned information where needed for performance or evaluation.
4. Relate rules and restrictions implemented by tools to their applicable Controls and Constraints, identifying their common source, scope, and how each operation applies them. Distinguish limitations of the selected tools and environment from work requirements, and assess their effects on feasibility and Outcome judgments.

    > NOTE One operation can supply processing capability, apply a judgment criterion, and enforce a restriction. These roles describe different relationships to the work. The [capabilities, criteria, and limits example](references/examples.md#capabilities-criteria-and-limits) shows their correspondence in a measurement tool.

5. Identify gaps requiring a new or adapted method, tool, or connection. Judge boundaries by cohesion, change effects, and ease of use, composition, and verification.

### Realizing the requested configuration

1. Within the requested scope, implement and connect the necessary capabilities using the applicable environment. Existing CLIs or APIs may be used directly. Make tool use, dependencies, result interpretation, failure handling, and state-changing effects available where they are needed.
2. For a target Skill, reflect the work, judgment criteria, required tool use, and conditions in `SKILL.md` and necessary resources. Apply the Framework's Markdown rules and the [Process Description Design guidance](../design-process-description/SKILL.md) for Agent Skill correspondence. Put bundled business processing in that target Skill's `scripts/` and document it using the script guidance; scripts in a design Skill must support its design or evaluation work.
3. Verify that required resources and their conditions of use are available under the intended distribution. Packaged links must resolve within it; external references must identify their intended sources and any access conditions.
4. Confirm required conditions before dependent operations. Address uncertain or partial effects before retrying an operation that changes state.

### Evaluating and adjusting the system

1. Review the design's responsibilities, relationships, and conditions against the target work. Check the components and connections against their specified behavior, including relevant failures and incomplete results.

    > NOTE In this design work, specifications and applicable work requirements supply the criteria. Existing command tools support component checks and integration trials. Their observations provide evidence for assessing the design; whole-system effectiveness also depends on the agent's interpretation and response during representative work.

2. Evaluate representative work using the intended agent, tools, information, and environment to the extent authorized and available. Assess the work's Outcomes against evidence and applicable conditions, distinguishing them from tool completion and generated Outputs.
3. Reconsider instructions, information supply, public operations, and allocation where evidence or changed capabilities warrants it. Preserve work-specific knowledge and conditions while reviewing guidance that compensates for capability limits. Revalidate affected behavior.
4. Report each judgment's subject, criteria, evidence, scope, unperformed checks, and unresolved findings. In a review, assess these Outcomes in the supplied design; finding a defect does not satisfy the condition that remains unmet.

## Controls

Apply the [Process Framework](../design-process-description/references/process-framework.md) to this Process Description and [Design Principles for Agent Work Systems](references/agent-work-system-design.md) to its design subject. For Agent Skill targets, apply the [Agent Skills specification](https://agentskills.io/specification) to the physical format and its [script guidance](https://agentskills.io/skill-creation/using-scripts) when documenting bundled processing. These sources are required within their subjects. The target work description, the user's request, and applicable environment conditions govern the design's scope.

## Constraints

A review-only request must return findings and any requested corrections without unsolicited changes. Performing the target work is a separate application and must remain within the applicable authorization. Missing references or unconfirmed conditions must limit dependent actions and judgments; independent analysis or drafting may continue within its own conditions. Unperformed evaluation must remain unconfirmed.

## Resources

This root `SKILL.md` is the English source for the [Japanese translation](references/locales/ja/SKILL.md), which preserves its meaning and normative force.

- [Design prompts and examples](references/examples.md): use relevant prompts and cases to develop or review a configuration.
- [Working example](../../examples/README.md): inspect a target Skill with a processing script, conditions, and evaluation cases.
- [Process Description Design](../design-process-description/SKILL.md) and its [minimal template](../design-process-description/references/SKILL-template.md): use when the work's meaning needs clarification or an Agent Skill description needs to be authored.
