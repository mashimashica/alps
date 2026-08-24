---
name: review-alps
description: Review ALPS repository changes across the Process Framework, ALPS Specification, ALPS Reference Model, reference Processes, checker logic, record bindings, locale counterparts, and the final diff. Use for cross-cutting consistency review before merge or when a change can affect multiple ALPS semantic layers. Repository-development Skill; not part of the distributed ALPS Plugin.
---

# Review ALPS

Review a change as one ALPS system rather than as isolated files.

## Review scope

Inspect the changed files first, then follow every semantic dependency needed to judge the change. At minimum, consider:

- `spec/process-framework.md` as the higher-order Process Framework source;
- `spec/ALPS-SPEC.md` and the applicable clauses;
- `skills/alps-reference-model/SKILL.md` and `skills/alps-reference-model/references/locales/ja/SKILL.md` as the English and Japanese ALPS Process Reference Model representations;
- `skills/define-alps/`, `skills/apply-alps/`, and `skills/manage-alps/` as the distributed reference Processes;
- `skills/define-alps/scripts/check_alps_asset.py` and other affected mechanical checks;
- record templates and bindings under the distributed Skills;
- English/Japanese counterparts when either locale is affected; and
- the complete task-owned diff.

Do not assume that consistency in one layer establishes consistency elsewhere.

## Review method

1. Identify the semantic center of the change and the ALPS/PF constructs it affects.
2. Check terminology, definitions, normative force, Process boundaries, Outcomes, Activities, Tasks, Inputs/Outputs, Controls, Constraints, Enablers, references, Conformance subjects, Tailoring, and execution semantics as applicable.
3. Trace duplicated or repeated normative meaning across the PF, ALPS Specification, ALPS Reference Model, reference Processes, checker behavior, and record bindings. Report divergence even when each file is internally coherent.
4. Verify that checker behavior enforces the intended invariant without creating an additional normative requirement.
5. Verify that record bindings preserve the specification boundary and do not silently turn binding fields into ALPS requirements.
6. Check changed relative links, canonical references, paths, and repository layout assumptions.
7. Use `sync-locales` for a dedicated semantic-equivalence pass whenever English or Japanese normative or guidance assets change.
8. Inspect the final diff for unrelated edits, stale terminology, dead references, duplicated sources of truth, and repository-only assets leaking into Plugin distribution.

## Findings

Report concrete findings before summaries. For each finding, identify severity, file/location, the conflicting statements or behavior, why the inconsistency matters, and the smallest coherent correction.

If no actionable inconsistency is found, state that explicitly and list any validation that could not be performed. Do not invent findings to fill a review.
