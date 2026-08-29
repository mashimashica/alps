---
name: sync-locales
description: Use this repository-development skill to check and synchronize semantic equivalence between authoritative English ALPS assets and supported Japanese counterparts. Preserve normative force, identifiers, paths, metadata keys, code literals, and scope; report omissions and pairs that could not be verified. Do not expose this skill as part of the distributed Plugin.
---

# Locale Synchronization Process

## Purpose

This Process establishes semantic equivalence between authoritative English
ALPS assets and their supported Japanese counterparts while preserving normative
force, canonical identity, and repository locale policy.

## Outcomes

- a) The authoritative locale, supported locale, and applicable pairs are
  identified according to repository policy.
- b) Corresponding Process semantics, discovery projections, requirements,
  recommendations, permissions, prohibitions, assessment boundaries,
  references, examples, and status words carry equivalent meaning.
- c) Normative force, identifiers, paths, metadata keys, code literals, and
  reference forms are preserved unless the authoritative source changed.
- d) Supported Japanese assets express the authoritative English meaning without
  silently changing the English source.
- e) Mismatches, harmless wording differences, equivalent pairs, and unverified
  pairs are distinguishable.

## Activities & Tasks

The Activities, Tasks, and their order organize synchronization and do not
prescribe an execution sequence or performer allocation.

### Locale Policy and Pair Scope

1. `localization.yaml` must be used to identify source and supported locales.
2. Every changed English or Japanese asset must be mapped to its applicable
   counterpart.
3. `spec/*.md` and `spec/locales/ja/*.md` pairs must be considered when a
   specification changes.
4. `skills/reusable-work-design/SKILL.md` and its Japanese counterpart must be
   considered when the distributed Skill changes.
5. Paired guidance, including README, AGENTS, CONTRIBUTING, and versioning, must
   be considered when affected.
6. Repository-development Skills must remain outside Plugin locale scope unless
   repository policy deliberately introduces counterparts.

### Semantic Equivalence Assessment

1. Corresponding semantic units on both sides must be identified.
2. Meaning must be compared rather than sentence shape.
3. Subject, modality, action or state, object, condition, quantifier, polarity,
   exception, and application scope must be checked for material omission or
   addition.
4. Purpose, Outcomes, Activities, Tasks, Inputs, Outputs, Controls, Constraints,
   discovery conditions, references, examples, and assessment boundaries must
   be checked where applicable.
5. The normative force of `must`, `should`, `may`, prohibitions, and their
   Japanese equivalents must be preserved.
6. Identifiers, paths, metadata keys, code literals, and reference forms must
   remain unchanged unless the authoritative source changed.
7. A supported-locale statement without an authoritative source, or an omitted
   authoritative statement, must be treated as a mismatch unless it is clearly
   locale-specific presentation.

### Synchronization and Reporting

1. When synchronization is requested, the supported locale must be updated to
   match the authoritative English meaning.
2. The authoritative English source must not be silently rewritten from the
   Japanese translation.
3. The resulting pair must be rechecked for semantic equivalence.
4. Unrelated translation drift must be excluded from the task-owned diff.
5. Each mismatch must identify its pair, semantic unit, and required correction.
6. Harmless wording differences must be distinguished from mismatches.
7. Every applicable pair must be reported as equivalent, requiring correction,
   or not checked.

## Inputs

- `localization.yaml` and applicable repository locale policy.
- Changed English or Japanese assets and the task-owned diff.
- Corresponding specifications, distributed Skill descriptions, guidance,
  metadata projections, and existing localized counterparts.
- Controlled identifiers, paths, metadata keys, code literals, and references.

## Outputs

- The applicable English/Japanese pair scope.
- Supported-locale assets synchronized to authoritative meaning when requested.
- A semantic-equivalence assessment distinguishing matches, wording differences,
  mismatches, and unverified pairs.
- Corrections, assumptions, and comparison limitations.

## Entry Criteria

- A changed paired asset or locale review request is available.
- Locale policy and candidate counterparts can be consulted.
- Corresponding semantic units can be identified.

## Exit Criteria

- Every applicable pair is classified as equivalent, requiring correction, or
  not checked.
- Requested synchronization is complete and the resulting pair has been
  rechecked.
- Normative force and canonical identity have been checked.
- Mismatches, harmless wording differences, unverified pairs, assumptions, and
  limitations are explicit.

## Controls

- `localization.yaml` defines English as authoritative and Japanese as supported.
- The Process Framework, ALPS Specification, and authoritative English Process
  Description govern meaning and normative force within their scopes.
- `AGENTS.md` defines paired guidance and the repository-only/distributed boundary.
- The authoritative English asset is the source for synchronization.

## Constraints

- Semantic equivalence must not be reduced to byte identity, literal translation,
  or sentence-shape identity.
- A repository-development Skill must not acquire a Japanese Plugin counterpart
  merely because its English description changed.
- The supported locale must not be strengthened or weakened relative to the
  authoritative normative force.
- This general Process must not prescribe a performer structure, Task allocation,
  implementation method, tool, metric, or execution sequence.

## Assessment Boundary

The synchronization result may be assessed against declared pair scope and
evidence. Synchronizing a pair does not by itself establish Conformance of the
represented asset.
