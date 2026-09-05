---
name: sync-locales
description: Review and synchronize authoritative English ALPS specifications, the distributed Process Description, templates, examples, and guidance with their Japanese counterparts. Report semantic mismatches and unverified pairs. Repository-development Skill; not distributed by the Plugin.
---

# Locale Synchronization

## Purpose

Preserve the meaning, normative force, and source identity of English ALPS assets in their supported Japanese counterparts.

## Outcomes

- The authoritative locale and all affected counterpart pairs are identified.
- Meaning, applicability, normative force, references, and canonical literals agree across reviewed pairs, or differences and their impact are explicit.
- Requested translation corrections are complete and rechecked; unverified pairs remain identified.

## Tasks

The following review actions are required within the requested scope.

- Read [localization.yaml](../../../localization.yaml). Use English as authoritative and Japanese as supported; do not silently rewrite the authority from the translation.
- Map changes in `spec/*.md` to `spec/locales/ja/*.md`, root guidance to `docs/locales/ja/`, and `docs/*.md` to `docs/locales/ja/`. Map the distributed root `SKILL.md` to its `references/locales/ja/SKILL.md` and each English reference to its Japanese counterpart there.
- Keep repository-development Skills outside Plugin locale scope. They do not acquire translations merely because their English text changes. Shared icons and Host metadata are presentation resources, not additional locale authorities.
- Compare the full resulting semantic units, including purpose, result conditions, optional detail, conditions, references, uncertainty, changes, and examples. Check subject, modality, action or state, object, condition, quantifier, polarity, exception, and scope; similarity of headings or words is insufficient.
- Preserve the force of must / must not / should / should not / may and their Japanese equivalents. Preserve Skill identifiers, paths, metadata keys, code literals, and ordinary reference identity unless the English source changes them. Localized links may point to the corresponding translation where its English authority remains identifiable.
- When synchronization is requested, correct affected Japanese assets and recheck the result. Distinguish harmless wording differences from additions, omissions, or stronger or weaker obligations.
- Report each reviewed pair, any remaining mismatch and necessary correction, and any pair that could not be checked. Do not infer semantic equivalence from file existence, a locale manifest's status, or mechanical validation.

## Controls and constraints

The [Framework](../../../spec/process-framework.md) governs meaning and normative language, and [AGENTS.md](../../../AGENTS.md) governs scope and distribution. Preserve unrelated translation work. A review-only request permits findings, not unsolicited wholesale revision. Translation review does not establish successful execution of the described work.
