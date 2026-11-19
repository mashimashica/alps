# Perf issue

## Purpose

Fix a perf issue with a one-off fix whose effect is measured against a baseline, not read from source.

## Outcomes

- Every fix is tied to a measurement, with a baseline trace captured before it and a post-fix trace captured after it.
- The baseline and each later number are vetted with the **benchmark-checklist** skill.
- An inconclusive or wrong-surface comparison is flagged and not counted as a pass.
- The PR cites the measurement.

## Tasks

The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. Capture a baseline trace via the matching control skill. Vet the baseline, and each later number, with the **benchmark-checklist** skill.
2. Trace the code to ground hypotheses. Don't claim a perf ceiling without running it first.
   Try the performance mantras in order, cheapest first:
   1. Don't do it. Stop work whose result nothing uses rather than cheapening it.
   2. Do it, but don't do it again.
   3. Do it less.
   4. Do it later.
   5. Do it when they're not looking.
   6. Do it concurrently.
   7. Do it cheaper.

   When an earlier mantra meets the target, stop.
3. Plan the fix from the trace. If it crosses a function boundary, `architect` first. Delegate implementation to a subagent using your configured perf-issue model (default `claude-opus-5-5-xhigh-fast`). Pick each subagent's reasoning level for the job, per the Subagents section. Review the diff. Capture a post-fix trace.
   Apply the **sequence-verifiable-units** principle skill, verifying each attempt before trying the next.
4. Parse and compare the artifacts (JSON to sqlite, diff). "Inconclusive" or wrong-surface is not a pass. Flag it.
5. Cite the measurement in the PR.
6. Run **Opening a PR**.

## Outputs

**Reply:** baseline number, post-fix number, delta, artifact path.

## Constraints

**You own the measurement story. Plan, review, verify the numbers.** Tie every fix to a measurement, don't read source instead of measuring.

For sustained improvement against a metric rather than a one-off fix, use the Hillclimb playbook (`playbooks/hillclimb.md`).

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Step 3 follows steps 1 and 2, because it plans the fix from the trace and changes the code the baseline measures.
- Step 4 follows step 3, because it compares the baseline with the post-fix trace.
- Step 5 follows step 4, because it cites the measurement step 4 compares.
