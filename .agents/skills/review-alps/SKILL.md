---
name: review-alps
description: Review ALPS repository changes for semantic consistency, source authority, evaluation limits, and distribution integrity across specifications, the distributed Skill, resources, tests, and guidance. Repository-development Skill; not distributed by the Plugin.
---

# ALPS Repository Review

## Purpose

Make inconsistencies and validation limits in an ALPS repository change clear enough to support a justified change decision.

## Outcomes

- The task-owned change, its semantic effects, and affected sources are identified.
- Cross-layer consistency, authority, distribution boundaries, and English/Japanese meaning are assessed with evidence.
- Findings identify affected locations, consequences, and coherent corrections; unperformed checks and remaining uncertainty are explicit.

## Tasks

The following review actions are required within the requested scope.

- Read the current [Framework](../../../spec/process-framework.md), [Specification](../../../spec/ALPS-SPEC.md), [AGENTS.md](../../../AGENTS.md), and the complete affected Skill descriptions. Review the entire task-owned diff, including additions and removals. Respect the user's information and authorization boundaries.
- Compare changed propositions by subject, modality, action or state, object, condition, quantifier, polarity, exception, and scope. Distinguish intentional redefinition from accidental loss; do not restore a superseded rule against the requested design.
- Check that Purpose, Outcome, and Output remain distinct; Outcomes are observable, relevant, and collectively sufficient; and optional detail is included for an actual need. Check one-off work and work without fixed artifacts as well as repeated work.
- Check required references, source identity, context-limited changes, and views against their actual sources. Preserve necessary approvals and order without imposing general execution means. Follow change effects through shared information, not only serial handoffs.
- Check that a review result, execution result, requirement judgment, and supporting evidence are distinguished. Look for unsupported success, missing references treated as verified, or exclusions used to hide missing evidence.
- Assess the single distributed Skill separately from repository-development Skills. Check each Host's real paths, required specification resources, icons, and the Plugin root boundary without defining a replacement Host schema.
- Apply [sync-locales](../sync-locales/SKILL.md) to affected pairs. Separate official form checks, repository integrity, and semantic review. Fixed strings can detect retired vocabulary; their absence does not prove meaning.
- Report concrete findings first, with location, evidence, impact, and the smallest coherent correction. State when no actionable inconsistency remains and identify every unexamined scope or unperformed validation. A review-only request does not authorize a rewrite.

## Controls and constraints

The Framework governs Process meaning; the Specification governs Agent Skill correspondence; AGENTS governs repository layout. The user's task determines authorized changes and available evidence. Tests and examples supply evidence, not additional Process requirements. Review does not authorize execution, publication, or changes outside the requested scope.
