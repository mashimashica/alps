---
name: interrogate
description: "Use for \"interrogate\", \"adversarial review\", \"multi-model review\", \"challenge this\", \"stress test this code\", \"find blind spots\", or \"tear this apart\". Adversaries try to break a change or design, and only findings proven by a run survive."
disable-model-invocation: true
---

# Interrogate

## Purpose

Find where a change or a design breaks its intent by having adversaries try to break it, and report the findings without applying fixes.

## Outcomes

- Every reported finding is backed by a rerun of its command whose output shows a failure that breaks the intent.
- The verdict holds every verified finding from every adversary.
- Findings that share a root cause are merged into one.
- Each adversary's dropped findings are counted, with why they were dropped.

## Activities & Tasks

The following Tasks are required whenever this skill runs, each with the conditions it states. Numbers identify the Tasks and set no order.

### Frame

1. State the intent with the **in-your-own-words** skill, from the user's message, the commits, and the PR description. Ask the user when the intent is unclear.

### Fan out

1. Run Phase A steps 3 and 4 and Phase B of the **arena** skill, with four changes. Read the `interrogate reviewers` line in place of `arena runners`. Copy the scope's uncommitted changes into each worktree. Spawn each adversary as `generalPurpose`. In place of the arena task and rationale, give each adversary the scope, the intent, and this brief:

    > Break this change. Prove each finding with a run against the real code, such as a failing test, a repro script, or command output that shows the wrong behavior. For a design or plan, run a prototype or probe the current tree. Keep repros in your own worktree. Report each finding with a title, the exact command, the output it printed, and the output the intent requires. Leave out anything you did not run. That covers style, naming, structure, and risks that need a future change to matter. No findings is a valid result.

### Verify

1. Verify each finding per arena Phase F by rerunning its command. Keep a finding when the output shows the failure and the failure breaks the intent. Drop the rest. Merge findings that share a root cause.

## Inputs

The scope is what the user names. Otherwise it is the branch diff from its merge base with the base branch, through the working tree.

## Outputs

- **Intent**: the restatement.
- **Findings**: for each verified finding, the command, its output, how it breaks the intent, and the adversaries that found it. Say "no verified findings" when none survive.
- **Dropped**: for each adversary, the count of dropped findings and why.

## Controls

A finding survives only when a run proves it.

## Constraints

Report the findings. Do not apply fixes.

Skip arena Phases C, D, and E. Adversaries find different failures, so the verdict keeps every verified finding, not one adversary's list.

These dependencies are required.

- The intent is stated before the adversaries are spawned, because each adversary is given it.
- A finding is verified after its adversary reports it.
