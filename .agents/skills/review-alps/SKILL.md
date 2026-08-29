---
name: review-alps
description: Use this repository-development skill to review changed ALPS assets across the Process Framework, thin ALPS profile, Reusable Work Design Process, locale pairs, Host projections, tests, and distribution boundary. Keep official form validation, repository integrity, and semantic review distinct. Do not expose this skill as part of the distributed Plugin.
---

# ALPS Repository Review Process

## Purpose

This Process establishes a cross-layer assessment of an ALPS repository change
so that semantic inconsistencies, boundary violations, and validation
limitations are visible before the change is accepted.

## Outcomes

- a) The semantic center of the change and its applicable Process Framework and
  ALPS dependencies are identified.
- b) Process semantics, normative force, Process boundaries, and product promises
  are consistent across affected authoritative sources and projections, or each
  divergence is explicit.
- c) Official form validation and repository-integrity checks remain within
  their mechanical boundaries.
- d) Locale equivalence, relative references, Host projections, repository
  layout, and the repository-only/distributed boundary are assessed.
- e) Actionable findings identify severity, location, evidence, impact, and the
  smallest coherent correction.
- f) Unperformed checks, assumptions, and other review limitations are explicit.

## Activities & Tasks

The Activities, Tasks, and their order organize the review and do not prescribe
an execution sequence or performer allocation.

### Change Scope Assessment

1. The changed files and semantic center of the change must be identified.
2. The applicable Process Framework, ALPS Specification, Reusable Work Design
   Process, locale policy, Host projections, tests, and layout assumptions must
   be identified.
3. The complete task-owned diff must be included in the review scope.
4. Every affected English/Japanese pair must be identified.
5. Each changed authoritative proposition and its dependent projections must be
   identified.
6. Historical release documents must be distinguished from active normative or
   usage surfaces.

### Cross-Layer Semantic Assessment

1. Terminology, definitions, normative force, Process boundaries, Outcomes,
   Activities, Tasks, Inputs, Outputs, Controls, Constraints, Enablers,
   handoffs, assessment boundaries, and execution semantics must be compared
   where applicable.
2. Repeated meaning must be traced to the applicable authoritative source.
3. A divergence between layers must be reported even when each asset is
   internally coherent.
4. Each changed, compressed, relocated, or deleted proposition must be compared
   across subject, modality, action or state, object, condition, quantifier,
   polarity, exception, and application scope.
5. The Reusable Work Design Process must be reviewed for one coherent Purpose,
   self-application without exception, semantic fixed-point stability,
   discovery-projection fidelity, and subtraction of unnecessary statements.
6. Changed relative links, canonical identifiers, paths, and Host projections
   must be checked.
7. The result of `sync-locales` must be integrated whenever an English or
   Japanese normative or guidance asset is affected.
8. Repository-only assets must be checked for unintended registration,
   discovery, or leakage into the distributed Plugin.
9. Official form validation and repository-integrity checks must be treated as
   evidence about form and layout only.

### Finding Reporting

1. Each finding must identify its severity, file or location, evidence, impact,
   and smallest coherent correction.
2. Concrete findings must be reported before summaries.
3. The result must state explicitly when no actionable inconsistency is found.
4. Validations that could not be performed must be listed.
5. Findings must not be invented to fill a review.

## Inputs

- The task-owned diff and every file it changes.
- Applicable authoritative Process Framework, ALPS Specification, and Reusable
  Work Design Process revisions.
- Affected locale assets, relative references, manifests, Host metadata, tests,
  and repository guidance.
- Repository layout, distribution metadata, and relevant change history.

## Outputs

- A cross-layer semantic and distribution assessment.
- Actionable findings with evidence and corrections, or an explicit no-action
  result.
- A locale-equivalence assessment integrating `sync-locales`.
- Unperformed checks, assumptions, and limitations.

## Entry Criteria

- A repository change or review request is available.
- The changed files and their task ownership can be identified.
- Applicable authoritative sources, locale policy, and distribution boundaries
  can be consulted.

## Exit Criteria

- The change boundary and semantic dependencies have been assessed.
- Cross-layer consistency, locale coverage, validation boundaries, references,
  Host projections, and distribution scope have been judged.
- Findings, no-action conclusions, assumptions, and unperformed checks are
  explicit.
- The evidence is usable for a subsequent correction or acceptance decision.

## Controls

- The Process Framework is the higher-order normative source for Process
  semantics.
- `spec/ALPS-SPEC.md` governs the thin Agent Skill application profile.
- `skills/reusable-work-design/SKILL.md` is the authoritative distributed
  Process Description.
- `AGENTS.md` governs repository layout and distribution boundaries.
- `localization.yaml` defines English as authoritative and Japanese as supported.
- Applicable official standards govern physical forms without redefining ALPS
  semantics.

## Constraints

- This general Process must not prescribe a performer structure, Task
  allocation, implementation method, tool, metric, or execution sequence.
- Repository-development Skills must not be treated as distributed Plugin Skills.
- Locale equivalence must be judged by meaning and normative force rather than
  byte identity or sentence shape.
- Mechanical validation must not substitute for semantic review.
- A finding must be supported by a concrete inconsistency, behavior, limitation,
  or missing validation.

## Assessment Boundary

This Process and its resulting review may be assessed against declared criteria
and evidence. A self-review or successful repository check does not by itself
establish Conformance of any reviewed asset.
