---
name: sync-locales
description: Review and synchronize authoritative English ALPS specifications, Process Descriptions, templates, examples, and guidance with their Japanese counterparts. Report semantic mismatches and unverified pairs. Repository-development Skill.
---

# Locale Synchronization

## Purpose

Preserve the meaning, normative force, and source identity of English ALPS assets in their supported Japanese counterparts.

## Outcomes

- The authoritative source and the supported counterpart for each affected asset are identified.
- Differences in meaning, applicability, normative force, and reference identity are explicit.
- Requested translation corrections preserve source meaning, with unverified correspondence identified.

## Activities

The following Tasks are required within the requested scope.

### Source and counterpart identification

- Read [localization.yaml](../../../localization.yaml) to identify authoritative and supported locales.
- Map specification files to `spec/locales/ja/`, repository guidance and documents to `docs/locales/ja/`, and distributed Skill content to its `references/locales/ja/` counterparts.
- Identify shared presentation resources and repository-development Skills using [AGENTS.md](../../../AGENTS.md); these do not require separate Plugin translations.

### Meaning alignment

- Compare complete semantic units by subject, modality, action or state, object, condition, quantifier, polarity, exceptions, and scope. Assess relationships between elements as well as individual statements.
- Check that work structure, Outcome judgments, contextual conditions, source identity, change effects, and uncertainty have the same meaning.
- Preserve canonical paths, identifiers, and code literals. Localized links may target the corresponding translation when its authoritative source remains identifiable.
- Correct affected translations when synchronization is requested, preserving unrelated work. Keep changes to the authoritative source within the requested scope.

### Correspondence evaluation

- Recheck corrected units in context, distinguishing wording differences from added, omitted, strengthened, or weakened obligations.
- Report reviewed pairs, remaining mismatches and their effects, and unverified pairs. File existence, locale metadata, and format checks do not establish semantic equivalence.

## Controls

The [Framework](../../../spec/process-framework.md) governs meaning and normative language. The localization configuration and AGENTS govern source roles and repository paths.

## Constraints

A review-only request permits findings, not unsolicited changes. Translation review does not establish successful execution of the described work.
