# Refactoring

## Purpose

Change the structure of the code while its behavior holds against a pinned contract, keep only a change that lowers reader load, and deliver what is kept for review.

## Outcomes

- A characterization test, snapshot, or equivalence harness pins the current behavior, captured before any structure moved.
- The behavior is proven unchanged on the real artifact.
- The pin is green after every small behavior-preserving move and at every behavior-preserving slice.
- The shipped change carries no new behavior.
- The shipped diff lowers reader load somewhere, and a diff that does not is reverted.
- The shipped history is small ordered commits, a subtraction commit, then the reshape, then any follow-on cleanup.
- The shipped change is open as a PR per **Opening a PR**.

## Tasks

The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. Pin the behavior contract first. Trace the affected subsystem to learn the contract, then write a characterization test, snapshot, or equivalence harness that captures current behavior before any structure moves. If the area has no coverage, write the pin before touching structure. Type check and lint are not a pin.
2. Name the structure the code is missing per **principle-model-the-domain**. Boring code stays when the shape is already clear and local. The reshape must delete branches or invalid states, not add indirection.
3. Name the target shape. State what the module layout, types, and call graph should be if built today (**principle-foundational-thinking**, **principle-redesign-from-first-principles**). If the target crosses a function boundary, run the **architect** skill for the shape before the move.
4. Subtract before you add. Delete dead code, collapse one-caller wrappers, drop redundant validators, and remove orphan references before introducing the new shape (**principle-subtract-before-you-add**). The smallest change that reaches the target shape ships (**principle-laziness-protocol**). A speculative cleanup that "might help" gets reverted.
5. Move in small behavior-preserving steps, each keeping the pin green. For API reshapes, migrate every caller and delete the old API in the same wave (**principle-migrate-callers-then-delete-legacy-apis**). No compatibility shims, no parallel old-and-new paths. Spot-check every rename against the actual files. Renames silently miss usages in strings, prose, and back-references. Delegate the mechanical edits to a subagent using your configured refactoring model (default `claude-opus-5-5-xhigh-fast`) with a specific scope (file paths, the names being moved, the behavior to hold). Pick each subagent's reasoning level for the job, per the Subagents section.
6. Prove behavior is unchanged on the real artifact, not "it compiles" (**principle-prove-it-works**). For larger reshapes, run an equivalence check: a script that diffs old-vs-new outputs, a recorded baseline replayed against the new code, or a smoke run on the matching surface via the relevant control skill.
7. Confirm the change is worth keeping. The success measure is reduced reader load (**principle-minimize-reader-load**). If the diff does not lower reader load somewhere, revert it.
8. Rebase into small ordered commits. A subtraction commit, then the reshape, then any follow-on cleanup. Shape them with the **sequence-verifiable-units** principle skill, so each behavior-preserving slice stays green before the next. Run **Opening a PR**.

## Outputs

**Reply:** the structure that changed, the pin you held it against, the equivalence proof, the reader-load delta, what shipped and what got reverted. No new behavior.

## Constraints

**You own the contract. The structure changes. The behavior does not.** Distinct from Feature, which adds behavior, and Bug fix, which corrects it.

If the cleanup reveals a missing feature or a real bug, split it out and ship the structural change first against the pinned contract. A redesign is allowed, but name it and route to Feature. Large or cross-cutting structural work belongs to the **figure-it-out** skill. This playbook is the focused-to-medium change.

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Step 1 comes before any structure moves, because the pin captures current behavior.
- Step 3 comes before step 5, because the move needs the target shape.
- Step 4 comes before step 5, because the subtraction comes before the new shape.
- Step 6 follows step 5, because it proves the behavior of the moved code.
- Step 7 comes before step 8, because it decides whether the diff is kept or reverted.
