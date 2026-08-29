---
name: review-alps
description: Review changed ALPS repository assets as an integrated Process system before a change is merged or when a change can affect the Process Framework, ALPS Specification, ALPS Reference Model, reference Processes, record aids, locales, or repository distribution. Repository-development Skill; not part of the distributed ALPS Plugin.
---

# ALPS Review

## Purpose

This Process establishes a cross-layer assessment of an ALPS repository change so that semantic inconsistencies, boundary violations, and validation limitations are visible before a change is accepted.

## Outcomes

Success of this Process establishes the following conditions.

- a) The semantic center of the change and its applicable ALPS and Process Framework dependencies are identified.
- b) Terminology, normative meaning, Process boundaries, and execution semantics are consistent across the affected representations, or each divergence is made explicit with evidence.
- c) Standard validation, repository-integrity checks, and record aids preserve the ALPS specification boundary without introducing an additional normative requirement.
- d) Locale equivalence, canonical references, repository layout, and the boundary between repository-only and distributed assets are assessed.
- e) Actionable findings identify their severity, location, evidence, impact, and smallest coherent correction, while unperformed checks and other limitations are explicit.

## Activities & Tasks

The headings, Activities, Tasks, and numbers below organize the review content and do not prescribe an execution sequence or performer allocation. Applicable dependencies can be revisited when the change or its evidence warrants it.

### Change Scope Assessment

This Activity establishes the change boundary and the semantic material that can affect the assessment.

1. The changed files and the semantic center of the change must be identified.
2. The applicable Process Framework, ALPS Specification, ALPS Reference Model, reference Processes, record aids, standard-validation boundaries, and repository layout assumptions must be identified.
3. The complete task-owned diff must be included in the review scope.
4. The English and Japanese counterparts affected by the change must be identified.
5. The prior authoritative version and every dependent authoritative projection affected by the change must be identified.

### Cross-Layer Semantic Assessment

This Activity assesses whether the affected ALPS layers preserve one coherent meaning.

1. Terminology, definitions, normative force, Process boundaries, Outcomes, Activities, Tasks, Inputs, Outputs, Controls, Constraints, Enablers, references, Conformance subjects, Tailoring, and execution semantics must be compared where applicable.
2. Repeated normative meaning across the Process Framework, ALPS Specification, ALPS Reference Model, reference Processes, record aids, and locale counterparts must be traced to its authoritative source.
3. A divergence between those layers must be reported even when each individual representation is internally coherent.
4. Each changed, compressed, relocated, or deleted proposition must be compared across subject, modality, action or state, object, condition, quantifier, polarity, exception, and application scope.
5. Reference Model Names, Purposes, and Outcomes must be compared semantically with the authoritative reference Process descriptions instead of treating string equality as meaning equivalence.
6. Record aids must be reviewed to preserve the specification boundary, and their headings or fields must not silently be treated as ALPS requirements.
7. Changed relative links, canonical references, paths, and repository layout assumptions must be checked.
8. The result of `sync-locales` must be integrated whenever an English or Japanese normative or guidance asset is affected.
9. Repository-only assets must be checked for unintended registration, discovery, or leakage into the distributed Plugin.
10. Official form validation and repository-integrity checks must be treated as evidence about form and layout only, not as substitutes for semantic review.

### Finding Reporting

This Activity makes the review judgment and its limitations usable by the change owner and subsequent decision makers.

1. Each finding must identify its severity, file or location, conflicting statements or behavior, importance of the inconsistency, and smallest coherent correction.
2. Concrete findings must be reported before summaries.
3. The result must state explicitly when no actionable inconsistency is found.
4. Validations that could not be performed must be listed.
5. Findings must not be invented to fill a review.

## Inputs

- The task-owned change diff and the files it changes.
- The applicable Process Framework, ALPS Specification, ALPS Reference Model, and reference Process representations, including their prior authoritative revisions where meaning preservation is claimed.
- Affected record aids, canonical references, and repository-integrity rules.
- The locale policy and the applicable English/Japanese assets.
- Repository guidance, Plugin metadata, distributed symlink layout, and relevant change history.

## Outputs

- A cross-layer ALPS semantic assessment.
- Actionable findings with evidence and smallest coherent corrections, or an explicit no-action result.
- A locale-equivalence and repository-distribution assessment.
- A list of unperformed validations, unresolved limitations, and assumptions.

## Entry Criteria

- A repository change or review request is available.
- The changed files and their task ownership can be identified.
- The applicable ALPS and Process Framework sources can be consulted.
- The locale policy and repository distribution boundaries can be determined.

## Exit Criteria

- The change boundary and applicable semantic dependencies have been assessed.
- Cross-layer consistency, validation and binding boundaries, locale coverage, and repository distribution scope have been judged.
- Findings, no-action conclusions, assumptions, and unperformed validations are explicit.
- The evidence is sufficient for a subsequent change, acceptance, or further-review decision.

## Controls

- The Process Framework is the higher-order normative source for Process semantics.
- `spec/ALPS-SPEC.md` governs Agent Skill representations, their boundaries, and their Conformance claims.
- `AGENTS.md` governs repository layout, repository-development Skills, and distributed Plugin boundaries.
- `localization.yaml` defines English as authoritative and Japanese as supported.
- Applicable Agent Skills and Agent Plugins standards govern their physical forms without redefining ALPS semantics.
- `AGENTS.md` separates official form validation, repository-integrity checks, and cross-layer semantic review.

## Constraints

- This general Process must not normatively prescribe a performer structure, Task allocation, implementation method, tool, metric, or execution sequence.
- Repository-development Skills under `.agents/skills/` must not be treated as distributed Plugin Skills unless repository policy deliberately registers them.
- Locale equivalence must be judged by meaning and normative force, not by byte identity or sentence shape.
- A review finding must be supported by a concrete inconsistency, behavior, limitation, or missing validation.

## Enablers

- Process Framework and ALPS Specification expertise.
- ALPS Reference Model, reference Processes, record aids, locale assets, and repository change history.
- Independent review capability and the repository-development `sync-locales` Skill.
- Official Agent Skill and Plugin validation, repository-integrity evidence, and version-control history.

## Interfaces & Traceability

| Information item provided | Primary recipient | Related information |
|---|---|---|
| Cross-layer semantic assessment | Change owner or acceptance decision | Change scope, affected representations, and evidence. |
| Actionable findings and corrections | Change owner | Severity, location, impact, and disposition. |
| Locale and distribution assessment | Repository maintenance and subsequent review | Locale policy, counterpart coverage, Plugin registration, and symlink layout. |
| Unperformed validations and limitations | Subsequent reviewer or decision maker | Assumptions, unresolved references, and evidence gaps. |

## Common Approach

A typical review begins with the changed files, identifies the previous and current authoritative propositions, and follows every dependent authoritative projection. It records each proposition's subject, modality, action or state, object, condition, quantifier, polarity, exceptions, scope, target location, and English/Japanese disposition. It compares the Reference Model semantic centers with the three authoritative Process descriptions, integrates the dedicated `sync-locales` result, and distinguishes standard-validation or repository-integrity evidence from semantic judgment. The result reports concrete findings before summaries and identifies every unexamined scope, assumption, and judgment limit.
