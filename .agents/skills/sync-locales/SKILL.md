---
name: sync-locales
description: Review and synchronize English ALPS source documents—specifications, Process Descriptions, templates, examples, and guidance—with their Japanese counterparts. Report semantic mismatches and unverified pairs. Repository-development Skill.
---

# Locale Synchronization

## Purpose

Preserve the meaning, normative force, and source identity of English ALPS assets in their supported Japanese counterparts.

## Outcomes

- The English source and the supported counterpart for each affected asset are identified.
- Differences in meaning, applicability, normative force, and reference identity are explicit.
- Requested translation corrections preserve source meaning, with unverified correspondence identified.

## Activities & Tasks

The following Tasks are required within the requested scope.

### Source and counterpart identification

1. Read [localization.yaml](../../../localization.yaml) to identify source and supported locales.
2. Map repository guidance and documents to `docs/locales/ja/`, and distributed Skill content, including its principles and supporting references, to its `references/locales/ja/` counterparts.
3. Map the working-example guide to `examples/locales/ja/` and the example Skill's documents to its `references/locales/ja/`. Shared code and fixture data keep their source identifiers.
4. Identify shared presentation resources and repository-development Skills using [AGENTS.md](../../../AGENTS.md); these do not require separate Plugin translations.

### Meaning alignment

1. Compare complete semantic units by subject, modality, action or state, object, condition, quantifier, polarity, exceptions, and scope. Assess relationships between elements as well as individual statements.
2. Check that work structure, Outcome judgments, contextual conditions, source identity, change effects, and uncertainty have the same meaning.
3. Check work-system responsibilities, judgment and processing allocation, interfaces, effects, and the distinctions between design review, component checks, and whole-system effectiveness. Preserve each source's independence and its application in the design Skills.
4. Use `NOTE` in English and `注記` in Japanese, preserving the note's attachment, scope, and informative role under the Framework's Markdown rules.
5. Preserve canonical paths, identifiers, and code literals. Localized links may target the corresponding translation when its English source remains identifiable.
6. Correct affected translations when synchronization is requested, preserving unrelated work. Keep changes to the English source within the requested scope.

### Correspondence evaluation

1. Recheck corrected units in context, distinguishing wording differences from added, omitted, strengthened, or weakened obligations.
2. Report reviewed pairs, remaining mismatches and their effects, and unverified pairs. File existence, locale metadata, and format checks do not establish semantic equivalence.

## Controls

The [Framework](../../../skills/design-process-description/references/process-framework.md) governs Process meaning and Markdown presentation. The [work-system principles](../../../skills/design-agent-work-system/references/agent-work-system-design.md) govern the supporting configuration. Preserve the meaning and normative force of each source and its application in the design Skills. The localization configuration and AGENTS govern source roles and repository paths.

## Constraints

A review-only request permits findings, not unsolicited changes. Translation review does not establish successful execution of the described work.
