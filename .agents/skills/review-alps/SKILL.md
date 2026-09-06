---
name: review-alps
description: Review ALPS repository changes for semantic consistency, source relationships, evaluation limits, and distribution integrity across specifications, design Skills, tools, examples, tests, and guidance. Repository-development Skill.
---

# ALPS Repository Review

## Purpose

Make inconsistencies and validation limits in an ALPS repository change clear enough to support a justified change decision.

## Outcomes

- The change's effects on Process meaning and applicable requirements are identified.
- The consistency of affected sources, translations, and distribution resources is established or qualified by explicit findings.
- Findings and validation limits provide evidence for deciding how to proceed with the change.

## Activities

The following Tasks are required within the requested review scope.

### Semantic assessment

- Identify the affected sources and inspect the complete task-owned diff, including additions and removals.
- Read the [Framework](../../../spec/process-framework.md), [Specification](../../../spec/ALPS-SPEC.md), and affected Process Descriptions in full.
- For work-system changes, read the [design principles](../../../spec/agent-work-system-design.md). Review responsibility allocation, public tool operations, information supply, execution conditions, and adaptation against the work. Verify the independent meaning of each foundation and their integration in the Specification.
- Compare changed propositions by subject, modality, action or state, object, condition, quantifier, polarity, exception, and scope. Check that editorial changes preserve meaning and that intentional redefinitions have a basis in the requested design.
- Assess each description's Purpose and independently assessable Outcomes for relevance, individual necessity, and collective sufficiency. Check necessary detail, Activity/Task cohesion and coverage, boundary roles, and the distinction between work relationships and execution order.
- Follow required references and information relationships. Assess source identity, shared conditions, context-limited changes, and effects on related work.
- Check that description validity, execution results, satisfaction of requirements, and their supporting evidence remain distinguishable.
- Assess the basis for Process selection and changes, including necessary information from affected parties and the applicability of criteria and evidence. Check the effects of changed conditions on dependent judgments and the treatment of unresolved findings.
- Check the distinct design and evaluation subjects of both Skills, the common source of target work meaning, and resource roles. Assess the necessary correspondence between Tasks and tool operations, and between Process boundary information and tool interfaces.

### Distribution assessment

- Compare the distribution with [AGENTS.md](../../../AGENTS.md): distributed and development Skills, native Host manifests, required sources, and presentation resources.
- Run the applicable format and repository integrity checks in the validation Workflow. Examine path resolution from the Plugin's distributed layout.
- Apply [sync-locales](../sync-locales/SKILL.md) to affected English/Japanese pairs.

### Implementation and work-system assessment

- Check specified tool behavior and necessary connections, including failures, incomplete results, side effects, and retry conditions where applicable.
- Evaluate representative work using the intended agent, tools, information, and environment within the authorized scope. Relate results to the work's Outcomes and conditions, distinguishing this evidence from component tests.
- Identify the actual evaluation environment, evidence, unperformed checks, and limitations. Examine capability changes for effects on allocation, interfaces, and instructions while preserving work-specific criteria.

### Finding synthesis

- Relate findings to their locations, evidence, effects, and coherent corrections.
- Report mechanical checks and semantic review separately, including failed or unperformed checks and unexamined scope. A passing format or path check does not establish Process meaning or Outcome achievement.

## Controls

The Framework governs Process meaning, the work-system principles govern supporting configurations, the Specification governs their integration in Agent Skills, and AGENTS governs repository layout. The requested change determines the review's scope.

## Constraints

Respect the user's information and authorization boundaries. A review-only request returns findings; it does not authorize editing, executing the described work, or publishing changes.
