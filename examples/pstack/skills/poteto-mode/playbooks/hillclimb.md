# Hillclimb

## Purpose

Improve one measurable thing against a target through sustained iteration rather than a one-off fix, with the metric and the experiment's integrity intact.

## Outcomes

- Where a case reproduces the user's complaint, the frozen harness reproduces the symptom on the target case and separates easier cases as expected.
- Every change the run keeps has its own before and after measurement on the frozen harness, with the regression gate green.
- No change the run keeps breaks behavior.
- Every attempt the run does not keep is reverted in full.
- Where a case reproduces the user's complaint, the decision log has one row per attempt, kept or reverted.
- Where a case reproduces the user's complaint, the stop predicate is met without being relaxed, or the run stops because the remaining ideas are marginal and not worth their cost while no cheap untried hypothesis remains, or the run is stuck and surfaces that.
- The accepted fixes are one commit each, stacked in the order they landed.

## Tasks

The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. Ground the workload and architecture before choosing the metric. Trace the target, name the realistic workload dimensions that can move the result (data size, history, state, concurrency), and select a case that reproduces the user's complaint. If no case reproduces it, fix the repro instead of hillclimbing. Then fix one metric, the direction that counts as better, and a checkable stop predicate that pairs a target with a floor on attempts so a lucky early win can't end the run (the example "at least 50% better than baseline and at least 10 iterations" is this shape). Use the user's numbers when given, otherwise agree them.
2. Build the measurement harness, prove its sensitivity, then freeze it (the **build-the-lever** principle skill). Run contrasting realistic workloads and confirm the target case reproduces the symptom while easier cases separate as expected. If the harness cannot distinguish them, revise the workload or metric. Vet the harness with the **benchmark-checklist** skill before you freeze it, and make it print its error count and a count of the work done. Once frozen, one repeatable command emits the metric, sampled enough to clear the noise (median of N, not a single run). Record the baseline metric and a green run of the regression gate (the tests that must keep passing) before any change.
3. Open the decision log via the **show-me-your-work** skill. A `decision.tsv`, one row per attempt: id, hypothesis, change, before, after, delta, tests, verdict (kept or reverted), note. Read it before each attempt. Keep it out of the tree (gitignored).
4. Ground each hypothesis in the architecture model from step 1, so it names a specific mechanism ("defer X off the boot path because it blocks first paint"), not "try memoizing something". For a perf metric, order hypotheses by the performance mantras in step 2 of the Perf issue playbook (`playbooks/perf-issue.md`). Borrow only their order, not that step's stop rule.
5. Loop, one hypothesis per iteration:
   - Hand the change to a subagent using your configured hillclimb model (default `claude-opus-5-5-xhigh-fast`) with a tight scope. Pick each subagent's reasoning level for the job, per the Subagents section. Supervise and review the diff rather than typing it (the **guard-the-context-window** principle skill). When several independent hypotheses are live, fan them to parallel subagents, each in its own worktree (the **separate-before-serializing-shared-state** principle skill).
   - Measure before and after with the frozen harness, and run the regression gate.
   - Accept only when the metric moves past noise and the gate stays green. Otherwise revert the change in full. A tweak that "might help" is not kept.
   - One commit per accepted fix, staging only the files you changed (`git add <files>`, never `-A`). Log the row either way, kept or reverted.
   Each iteration ends in a check before the next begins (the **sequence-verifiable-units** principle skill). If the run is unattended, borrow only the wake mechanism from the Autonomous run playbook (`playbooks/autonomous-run.md`), not its stop rule.
6. Push past the first plateau. On a stall, several rejects in a row, pivot category, combine near-misses, re-read the source, or try something more radical before concluding the hill is climbed. Correctness and simplicity outrank the number. Revert a win that breaks behavior, and keep a simplification that holds the number (the **laziness-protocol** principle skill).
7. Stop when the predicate is met, or when the remaining ideas are marginal and not worth their cost. Don't relax the predicate to meet it, and don't quit while cheap untried hypotheses remain. If you are stuck, surface it instead of spinning.
8. Run **Opening a PR** with the accepted commits stacked in the order they landed.

## Outputs

**Reply:** the metric and target, baseline to final with the percent delta, iterations run (kept vs reverted), each accepted fix on one line, the `decision.tsv` path, and the best idea you would try next if pushed further.

## Controls

Core discipline: one change, one measurement, keep or revert.

## Constraints

**You own the metric and the experiment's integrity. Supervise and review. Delegate the attempts.** For sustained, iterative improvement of one measurable thing against a target. A one-off fix is Bug fix or Perf issue. This is the loop.

Never stack untested changes, and never claim a win from code inspection (the **prove-it-works** principle skill).

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Step 1 comes before steps 2, 4, and 7. Step 2 measures its metric and case, step 4 uses its architecture model, and step 7 applies its stop predicate.
- Step 2 freezes the harness and records the baseline metric and a green run of the regression gate before any change in step 5.
- Step 3 opens the decision log before the first attempt in step 5.
- Step 5 repeats, one hypothesis per iteration, until step 7 stops the run.
- On a stall, step 6 comes before step 7 concludes the hill is climbed, and the run goes on with step 5.
- Step 8 uses the commits that step 5 accepted.
