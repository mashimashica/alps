---
name: review-alps
description: Review ALPS repository changes for semantic consistency, source authority, evaluation limits, and distribution integrity across specifications, the design Skill, resources, tests, and guidance. Repository-development Skill.
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
- Compare changed propositions by subject, modality, action or state, object, condition, quantifier, polarity, exception, and scope. Check that editorial changes preserve meaning and that intentional redefinitions have a basis in the requested design.
- Assess each description's Purpose and independently assessable Outcomes for relevance and collective sufficiency. Check necessary detail, Activity/Task cohesion and coverage, boundary roles, and the distinction between work relationships and execution order.
- Follow required references and information relationships. Assess source identity, shared conditions, context-limited changes, and effects on related work.
- Check that description validity, execution results, satisfaction of requirements, and their supporting evidence remain distinguishable.

### Distribution assessment

- Compare the distribution with [AGENTS.md](../../../AGENTS.md): distributed and development Skills, native Host manifests, required sources, and presentation resources.
- Run the applicable format and repository integrity checks in the validation Workflow. Examine path resolution from the Plugin's distributed layout.
- Apply [sync-locales](../sync-locales/SKILL.md) to affected English/Japanese pairs.

### Finding synthesis

- Relate findings to their locations, evidence, effects, and coherent corrections.
- Report mechanical checks and semantic review separately, including failed or unperformed checks and unexamined scope. A passing format or path check does not establish Process meaning or Outcome achievement.

## Controls

The Framework governs Process meaning, the Specification governs Agent Skill correspondence, and AGENTS governs repository layout. The requested change determines the review's scope.

## Constraints

Respect the user's information and authorization boundaries. A review-only request returns findings; it does not authorize editing, executing the described work, or publishing changes.
