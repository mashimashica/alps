---
name: swarm
description: "Fan out N parallel workers, drain them, and return one report. Use for /swarm, 'swarm this', or parallel coverage, races, gauntlets, and exploration."
disable-model-invocation: true
---

# Swarm

## Purpose

Run a job across N parallel workers and return their results as one report. It serves parallel coverage, races, gauntlets, and exploration.

## Outcomes

- Every counted result is a `PASS`, `ISSUES`, or `BLOCKED` with evidence.
- Every counted result records the SHAs and method its brief names.
- For coverage, every required slice has a result.
- For a race, the selection follows the rule declared up front.
- No gap counts as a pass.
- The report's result table and issue one-liners agree with the counted results.
- Every gap and worker dropout is stated, and so is every rejected slug that the default replaced.

## Activities & Tasks

The following Tasks are required whenever this skill runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

### Start

1. Open a todolist with one entry per phase before launching anything.

    1. Frame
    2. Fan out
    3. Aggregate
    4. Report

### Phase A: Frame

1. State the done predicate and the artifact or report the swarm must return.
2. Choose the shape. Partition into slices, race N workers on identical briefs, or mix both. For a race or mixed shape, declare `first pass`, `rank all`, or `best-of` before spawning.
3. Pick the worker model from the `swarm workers` line in `~/.cursor/rules/pstack-models.mdc`. If the rule or that line is missing, use `claude-opus-5-5-high-fast`. For `auto` or `inherit-parent`, omit `model` so the workers run on the parent model. If the Task tool rejects a slug, use the default and say so. If it rejects the default, use the closest valid slug of the same family from its error message. For a model race, name each arm's model up front. Pick each subagent's reasoning level for the job, per the Subagents section of the **poteto-mode** skill.
4. Give each worker its own writable output when it writes. When workers verify or measure commits, each brief names the exact SHAs. A measurement brief also names the method (sample count, what one sample is, order). The worker records both in its result.

### Phase B: Fan out

1. Spawn all N workers in one message with `subagent_type: generalPurpose`, `environment: "cloud"`, `run_in_background: true`, and the step 3 model, left unset for `auto` or `inherit-parent`. Use `environment: "local"` only when the worker needs access to something on the user's computer.

    When a worker must start from a non-default pushed branch, pass `cloud_base_branch`.

    Every brief stands alone. Include the goal, scope, exact slice or race arm, how to verify, and what to report. Reports use `PASS`, `ISSUES`, or `BLOCKED` with evidence. A worker that can prove a defect reports `ISSUES` and lists every issue it can prove, not only the first.

    If a worker drops out, proceed with N-1 and note it.

### Phase C: Aggregate

1. Read the terminal results. Drop a result that does not record the SHAs and method its brief names, and respawn that worker once. After a second miss, record a gap. A gap does not count as a pass. For coverage, every required slice needs a result. For a race, apply the selection rule declared up front. Use first pass, rank all, or best-of. Do not paste raw worker dumps.

### Phase D: Report

1. Return one consolidated in-chat report.

## Outputs

One consolidated in-chat report with a result table, issue one-liners, gaps or dropouts, and the race rule when used.

## Constraints

Unless a Task states otherwise, work the Activities and their Tasks in the order listed. These dependencies are required.

- The todolist is open before anything launches.
- For a race or mixed shape, the selection rule is declared before spawning.
- For a model race, each arm's model is named up front.
- Phase B spawns with the model that Phase A step 3 picks.
- The workers are drained before the report is returned.
- Phase C applies the selection rule that Phase A step 2 declares.
- Phase D reports what Phase C aggregates.
