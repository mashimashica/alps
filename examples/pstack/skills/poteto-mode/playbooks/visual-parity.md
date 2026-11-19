# Visual parity

## Purpose

Hold pixel-exact equivalence through a migration, so that each migrated component matches its baseline.

## Outcomes

- Every parity claim rests on a zero image diff of the component against its baseline on the matching surface.
- The baseline every diff runs against is the one established before any migration, untouched by the run.
- No diff passes because of a harness modification or a component restructuring made to pass it.
- Each component is reported either as migrated, with its diff result, or as part of what is left.

## Tasks

The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. Establish the baseline first, before any migration: a visual regression harness that screenshots the current component across its states, plus the target when matching two implementations. No baseline, no parity claim. A blocking prerequisite, not a follow-up.
2. Anti-shortcut clauses, stated and held: no harness modifications, no baseline tampering, no component restructuring to make a diff pass. If the baseline looks wrong, stop and ask, don't edit it.
3. Migrate one component at a time. Parallelize across worktrees, one owner per component (the **separate-before-serializing-shared-state** principle skill). Shared primitives migrate first as a blocking phase.
4. Verify each component against its baseline via image diff on the matching surface via the control skill. A nonzero diff is a fail. Investigate the pixel delta. `/loop` per component until the diff is zero.
5. Run **Opening a PR** per component or per safe batch.

## Outputs

**Reply:** components migrated, the diff result for each, the baseline harness location, what's left.

## Controls

Equivalence is verified by image diff, not by eye.

## Constraints

**You own pixel-exact equivalence. The baseline is the spec. You do not touch it.**

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Step 1 establishes the baseline before any migration in step 3.
- For each component, step 4 verifies it after step 3 migrates it and before step 5 opens its PR.
