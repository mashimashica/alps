# Feature

## Purpose

Build a feature under a design and a plan the lead owns, and deliver it for review verified on the matching surface.

## Outcomes

- The data shape and its organizing structure are chosen before the delegate writes logic.
- The throughput checkpoint keeps an item for each of its four dimensions, and a dimension that does not apply reads `n/a: <reason>`.
- The feature passes verification on the matching surface, or an inconclusive or wrong-surface result is flagged and not counted as a pass.
- The change is delivered as small, ordered commits, each small unit built, verified, and committed before the next.
- The change is open as a PR per **Opening a PR**.

## Tasks

The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. Trace the affected subsystem.
2. `architect` for the shape.
3. Write the throughput checkpoint as four todo items. A dimension that genuinely does not apply (single file, no fan-out) keeps its item with `n/a: <reason>` rather than being dropped:
   - **Blocking first steps.** Gates run before fan-out.
   - **Independent workstreams.** Disjoint files, services, or layers parallelize. Shared writes serialize.
   - **Shared mutable state.** Default to splitting the target (the **separate-before-serializing-shared-state** principle skill). Serialize only for real invariants.
   - **Smallest safe decomposition.** If one worker is best, name why.
4. Delegate code-writing to a subagent using your configured feature model (default `claude-opus-5-5-xhigh-fast`) with a specific scope (file paths, named data shape and its organizing structure per **principle-model-the-domain**, a state machine over scattered booleans, a table/registry over branching, a typed model over repeated shape assumptions, chosen before the delegate writes logic, and success criteria). Pick each subagent's reasoning level for the job, per the Subagents section. When the implementation admits multiple valid shapes (error handling, abstraction layer, test structure), delegate via the **arena** skill instead so the runners surface the alternatives and the cross-judge guards the pick. Mandatory: no skip-with-reason escape, and Laziness Protocol does not override it (the gain is review separation, not lines saved). A subagent forbidden to spawn satisfies this by owning the diff directly with the same review separation. No "standing by" reply that waits on a nested agent. Surgical edits, re-ground against the source for upstream-derived files. Port shared-primitive improvements to all consumers and verify each. Commit liberally.
5. Verify on the matching surface. "Inconclusive" or wrong-surface is not a pass. Flag it.
6. Rebase into small, ordered commits. Stack follow-ups.
   Use the **sequence-verifiable-units** principle skill, building, verifying, and committing each small unit before the next.
7. If the design is contested, `interrogate` before shipping.
8. Run **Opening a PR**.

## Outputs

**Reply:** what you built, what you chose and why, the throughput checkpoint, open decisions. Tables for design alternatives.

## Constraints

**You own the design. Plan, review, verify.** Delegate implementation. Stay in the lead.

Code-coupled work (one feature, one migration) goes to a single owner with the checkpoint inline. That owner fans out internally after the blocking phase. Parent-level fan-out is for slices that produce independent artifacts (audits, cross-subsystem investigations, competing experiments). Rewrite the checkpoint at phase boundaries. Spawn a fresh owner rather than chaining interrupts.

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Step 2 comes before step 4, because the shape is chosen before the delegate writes logic.
- Step 3 comes before step 4, because the checkpoint sets which gates run before fan-out and what parallelizes.
- Step 5 follows step 4, because it verifies what step 4 built.
- When step 7 applies, it comes before shipping.
- Step 8 follows step 6, because the PR carries the rebased commits.
