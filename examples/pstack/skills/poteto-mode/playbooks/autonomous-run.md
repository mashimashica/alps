# Autonomous run

## Purpose

Drive a task to a defined exit condition without stopping, with each iteration keeping only the changes that verifiably advance it, and surface a genuine dead end rather than spinning.

## Outcomes

- The exit condition is stated as a checkable predicate before the first iteration.
- The run does not stop before the predicate is met, except at a genuine dead end it surfaces.
- The predicate is not relaxed to declare victory.
- Every change step 3 keeps was verified against the predicate and advanced it.
- No reversible work is parked for the human.

## Tasks

The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. State the exit condition as a checkable predicate before the first iteration (tests green, repro fixed, all N PRs merged, pixel-diff zero).
2. Pick the wake mechanism using Cursor's `/loop` command (a built-in, not a pstack skill). An event to watch (CI, a merge, a ref advancing) gets a watcher subagent that wakes you on the event, with a long time-based heartbeat as fallback. No event gets a fixed-interval heartbeat sized to when the result is worth re-checking. Pick each subagent's reasoning level for the job, per the Subagents section.
3. Each iteration makes the smallest change the evidence justifies, verifies it against the predicate, commits if it advanced, discards changes that didn't help. Belt-and-suspenders that "might help" gets reverted, not left to ride.
   Sequence the work via the **sequence-verifiable-units** principle skill, verifying each unit before the next instead of batching checks at the end.
4. Mid-run discoveries that support the goal are yours. Address broken skills, related bugs, flaky verifiers, review noise, tooling failures, orphaned follow-ups, and fixable drift yourself via poteto-mode. Put out-of-band fixes in their own PR. Do not park reversible work for the human or use `AskQuestion`. Surface only irreversible actions, genuine product or preference calls no experiment can settle, or a real dead end. Keep the predicate as the main drive, and return to it after each side fix.
5. Checkpoint every iteration via the **show-me-your-work** skill, a row for what changed and whether the predicate moved.
6. Stop when the predicate is met. A plateau is not a stop, so keep going and pivot your approach to push past it. Surface a genuine dead end rather than spinning, and never relax the predicate to declare victory.

## Outputs

**Reply:** the exit condition, iterations run, what landed, what was discarded, final predicate state.

## Constraints

**You own the exit condition. Define done, then drive to it without stopping.**

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Step 1 comes before the first iteration, because step 3 verifies each change against the predicate that step 1 states.
- Step 5 writes an iteration's row after that iteration's change and check in step 3, because the row records what changed and whether the predicate moved.
- The iterations of step 3 continue until step 6 stops the run.
