---
name: sync-locales
description: Check and synchronize semantic equivalence between authoritative English ALPS assets and supported Japanese counterparts when paired specifications, reference Processes, guidance, templates, bindings, or related assets change, and report omissions or unverified pairs. Repository-development Skill; not part of the distributed ALPS Plugin. ALPS-conformant.
---

# Locale Synchronization

## Purpose

This Process establishes semantic equivalence between authoritative English ALPS assets and their supported Japanese counterparts while preserving normative force, canonical identity, and the repository locale policy.

## Outcomes

Success of this Process establishes the following conditions.

- a) The authoritative locale, supported locale, and applicable English/Japanese pairs are identified according to repository policy.
- b) Corresponding Purpose, Outcomes, Activities, Tasks, requirements, recommendations, permissions, prohibitions, Conformance boundaries, references, examples, identifiers, code literals, and status words carry equivalent meaning.
- c) Normative force and canonical paths, metadata keys, code, identifiers, and reference forms are preserved unless the authoritative source changed.
- d) When synchronization is requested, the supported Japanese assets express the authoritative English meaning without silently changing the English source.
- e) Semantic mismatches, harmless wording differences, equivalent pairs, and pairs that could not be checked are distinguishable and reported.

## Activities & Tasks

The headings, Activities, Tasks, and numbers below organize the synchronization content and do not prescribe an execution sequence or performer allocation. A pair can be revisited when its source or evidence changes.

### Locale Policy and Pair Scope

This Activity establishes which assets are authoritative, supported, and in scope.

1. `localization.yaml` must be used to identify the source locale and supported locales.
2. The corresponding English and Japanese assets for each changed specification, reference Process, guidance, template, binding, or related paired asset must be identified.
3. `spec/*.md` and `spec/locales/ja/*.md` pairs must be considered when specification assets change.
4. `skills/*/SKILL.md` and existing `skills/*/references/locales/ja/SKILL.md` pairs must be considered when distributed Skill assets change.
5. Paired repository guidance such as `README.md` / `docs/locales/ja/README.md` and `AGENTS.md` / `docs/locales/ja/AGENTS.md` must be considered when those assets change.
6. Repository-development Skills under `.agents/skills/` must be excluded from Plugin locale scope unless localized counterparts are deliberately introduced.

### Semantic Equivalence Assessment

This Activity determines whether each applicable pair preserves the same ALPS meaning.

1. The changed side and the corresponding semantic units on the other side must be identified.
2. Meaning must be compared rather than sentence shape.
3. Purpose, Outcomes, Activities, Tasks, requirements, recommendations, permissions, prohibitions, Conformance boundaries, references, examples, identifiers, code literals, and status words must be checked for material omission or addition.
4. The normative force of `must`, `should`, `may`, and their locale equivalents must be preserved.
5. Canonical identifiers, paths, metadata keys, code, and reference forms must remain unchanged unless the authoritative source changed.
6. A supported-locale statement with no authoritative source, or an authoritative statement omitted from the supported locale, must be treated as a semantic mismatch unless it is clearly locale-specific presentation.

### Synchronization and Result Reporting

This Activity aligns the supported locale when requested and makes comparison limits visible.

1. When synchronization is requested, the supported locale must be updated to match the authoritative English meaning.
2. The authoritative English source must not be silently rewritten from the Japanese translation.
3. The resulting English/Japanese pair must be rechecked for semantic equivalence.
4. Unrelated translation drift must be excluded from the final change diff.
5. Each mismatch must be reported with its paired files, affected semantic unit, and required correction.
6. Harmless wording differences must be distinguished from semantic mismatches.
7. A semantically equivalent pair must be identified explicitly.
8. A pair that could not be checked must be reported rather than assumed equivalent.

## Inputs

- `localization.yaml` and other applicable locale policy.
- Changed English or Japanese assets and the task-owned diff.
- Corresponding specifications, reference Processes, guidance, templates, bindings, and existing localized counterparts.
- Canonical identifiers, paths, metadata, code, and references used by the paired assets.
- Repository layout and distribution metadata relevant to the pair scope.

## Outputs

- An identified set of authoritative English and supported Japanese pairs.
- Supported-locale assets synchronized to authoritative meaning when requested.
- A semantic-equivalence assessment distinguishing matches, wording differences, mismatches, and unverified pairs.
- Required corrections, assumptions, and comparison limitations.

## Entry Criteria

- An English or Japanese asset, or a change affecting a paired asset, is available.
- The authoritative and supported locale policy can be consulted.
- Candidate counterparts and their semantic units can be identified.

## Exit Criteria

- Every applicable pair is classified as semantically equivalent, requiring correction, or not checked.
- Any requested supported-locale synchronization is complete and the resulting pair has been rechecked.
- Normative force and canonical identity have been checked.
- Mismatches, harmless wording differences, unverified pairs, assumptions, and limitations are explicit.

## Controls

- `localization.yaml` defines English as authoritative and Japanese as supported.
- The Process Framework and `spec/ALPS-SPEC.md` govern the meaning and normative force of ALPS representations.
- `AGENTS.md` defines paired repository guidance and the boundary between repository-development Skills and distributed Plugin Skills.
- The authoritative English asset is the source of meaning for synchronization; Japanese wording must not silently redefine it.
- Canonical identifiers, paths, metadata keys, code, and reference forms are controlled information when the authoritative source has not changed.

## Constraints

- Semantic equivalence must not be reduced to byte identity, literal translation, or sentence-shape identity.
- A repository-development Skill under `.agents/skills/` must not acquire a Japanese Plugin counterpart merely because its English description changed; such a counterpart requires deliberate repository policy.
- The supported locale must not be strengthened or weakened relative to the authoritative normative force.
- This general Process must not normatively prescribe a performer structure, Task allocation, implementation method, tool, metric, or execution sequence.

## Enablers

- Bilingual ALPS and Process Framework expertise.
- Locale-aware comparison, search, and change-review capabilities.
- Existing English/Japanese reference, template, binding, and guidance assets.
- Structural and semantic preflight capabilities, including the ALPS Markdown profile checker bundled with `review-alps`.

## Conformance

This Skill represents the Locale Synchronization Process and claims Description Conformance against the applicable Process Framework and ALPS Description requirements. Full Process Conformance may be assessed against Outcomes, Tasks, or both; the selected basis and evidence must be stated. Synchronizing a pair does not by itself establish Conformance of the represented ALPS asset.

## Interfaces & Traceability

| Information item provided | Primary recipient | Related information |
|---|---|---|
| Pair scope and locale authority | Change owner or review Process | `localization.yaml`, changed assets, and counterpart paths. |
| Semantic-equivalence assessment | Change owner or acceptance decision | Compared semantic units, normative force, and canonical identity. |
| Synchronized supported-locale assets | Repository maintenance | Authoritative English source, changed scope, and recheck evidence. |
| Mismatch and unverified-pair report | Change owner or subsequent reviewer | Required correction, assumptions, and limitations. |

## Common Approach

A typical synchronization assessment starts with the locale policy, maps changed assets to counterparts, compares semantic units and normative force, updates only the supported locale when requested, and rechecks the pair. It treats wording variation as harmless only when meaning is preserved and reports every mismatch or unverified pair instead of assuming equivalence.
