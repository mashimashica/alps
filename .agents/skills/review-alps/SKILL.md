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

## Activities & Tasks

The following Tasks are required within the requested review scope.

### Semantic assessment

1. Identify the affected sources and inspect the complete task-owned diff, including additions and removals.
2. Read the [Framework](../../../skills/design-process-description/references/process-framework.md) and affected Process Descriptions in full.
3. For work-system changes, read the [design principles](../../../skills/design-agent-work-system/references/agent-work-system-design.md). Review responsibility allocation, public tool operations, information supply, execution conditions, and adaptation against the work. Verify the independent meaning of each foundation and its application in the relevant design Skill.
4. Compare changed propositions by subject, modality, action or state, object, condition, quantifier, polarity, exception, and scope. Check that editorial changes preserve meaning and that intentional redefinitions have a basis in the requested design.
5. Assess each description's Purpose and independently assessable Outcomes for relevance, individual necessity, and collective sufficiency. Check necessary detail, Activity/Task cohesion and coverage, boundary roles, and the distinction between work relationships and execution order.
6. Review Markdown Process sections, Task lists, and note placement against the Framework, including `NOTE` in English and `注記` in Japanese. Check that notes explain the relevant content while obligations remain explicit in the main text; assess meaning separately from formatting.
7. Follow required references and information relationships. Assess source identity, shared conditions, context-limited changes, and effects on related work.
8. Check that description validity, execution results, satisfaction of requirements, and their supporting evidence remain distinguishable.
9. Assess the basis for Process selection and changes, including necessary information from affected parties and the applicability of criteria and evidence. Check the effects of changed conditions on dependent judgments and the treatment of unresolved findings.
10. Check the distinct design and evaluation subjects of both Skills, the common source of target work meaning, and resource roles. Assess the necessary correspondence between Tasks and tool operations, and between Process boundary information and tool interfaces.
11. For rules or restrictions implemented by tools, examine their correspondence to applicable Controls and Constraints, their sources and scope, and evidence that implementation preserves them. Distinguish configuration limits from requirements of the work.

### Distribution assessment

1. Compare the distribution with [AGENTS.md](../../../AGENTS.md): distributed and development Skills, native Host manifests, required sources, and presentation resources.
2. Run the applicable format and repository integrity checks in the validation Workflow. Examine path resolution from the Plugin's distributed layout.
3. Apply [sync-locales](../sync-locales/SKILL.md) to affected English/Japanese pairs.

### Implementation and work-system assessment

1. Check specified tool behavior and necessary connections, including failures, incomplete results, side effects, and retry conditions where applicable.
2. Evaluate representative work using the intended agent, tools, information, and environment within the authorized scope. Relate results to the work's Outcomes and conditions, distinguishing this evidence from component tests.
3. Identify the actual evaluation environment, evidence, unperformed checks, and limitations. Examine capability changes for effects on allocation, interfaces, and instructions while preserving work-specific criteria.

### Finding synthesis

1. Relate findings to their locations, evidence, effects, and coherent corrections.
2. Report mechanical checks and semantic review separately, including failed or unperformed checks and unexamined scope. A passing format or path check does not establish Process meaning or Outcome achievement.

## Controls

The Framework governs Process meaning and Markdown presentation, the work-system principles govern supporting configurations, and the design Skills apply these sources within their work. AGENTS governs repository layout. The requested change determines the review's scope.

## Constraints

Respect the user's information and authorization boundaries. A review-only request returns findings; it does not authorize editing, executing the described work, or publishing changes.
