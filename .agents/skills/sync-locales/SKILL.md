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

## Activities

The following Tasks are required within the requested scope.

### Source and counterpart identification

- Read [localization.yaml](../../../localization.yaml) to identify source and supported locales.
- Map specification files to `spec/locales/ja/`, repository guidance and documents to `docs/locales/ja/`, and distributed Skill content to its `references/locales/ja/` counterparts.
- Map the working-example guide to `examples/locales/ja/` and the example Skill's documents to its `references/locales/ja/`. Shared code and fixture data keep their source identifiers.
- Identify shared presentation resources and repository-development Skills using [AGENTS.md](../../../AGENTS.md); these do not require separate Plugin translations.

### Meaning alignment

- Compare complete semantic units by subject, modality, action or state, object, condition, quantifier, polarity, exceptions, and scope. Assess relationships between elements as well as individual statements.
- Check that work structure, Outcome judgments, contextual conditions, source identity, change effects, and uncertainty have the same meaning.
- Check work-system responsibilities, judgment and processing allocation, interfaces, effects, and the distinctions between design review, component checks, and whole-system effectiveness. Preserve each source's independence and the Specification's integration relationships.
- Preserve canonical paths, identifiers, and code literals. Localized links may target the corresponding translation when its English source remains identifiable.
- Correct affected translations when synchronization is requested, preserving unrelated work. Keep changes to the English source within the requested scope.

### Correspondence evaluation

- Recheck corrected units in context, distinguishing wording differences from added, omitted, strengthened, or weakened obligations.
- Report reviewed pairs, remaining mismatches and their effects, and unverified pairs. File existence, locale metadata, and format checks do not establish semantic equivalence.

## Controls

The [Framework](../../../spec/process-framework.md) governs Process meaning. The [work-system principles](../../../spec/agent-work-system-design.md) govern the supporting configuration, and the [Specification](../../../spec/ALPS-SPEC.md) governs integration in Skills. Preserve the meaning and normative force of the applicable source. The localization configuration and AGENTS govern source roles and repository paths.

## Constraints

A review-only request permits findings, not unsolicited changes. Translation review does not establish successful execution of the described work.
