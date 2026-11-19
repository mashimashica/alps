---
name: arena
description: "Spawn N parallel candidates at the same task, pick a base, graft the strongest parts of the losers into it. Use for /arena, 'arena this', 'throw it in the arena', or when one attempt at a non-trivial artifact would lock in the wrong shape."
disable-model-invocation: true
---

# Arena

## Purpose

Produce one synthesized artifact from parallel candidates at the same task, so that one attempt at a non-trivial artifact does not lock in the wrong shape.

## Outcomes

- Each candidate that produced output has a score on every rubric criterion.
- The base is the candidate a future maintainer can extend most easily without breaking invariants.
- The synthesized artifact carries what is worth porting from each losing candidate, or is the consensus shape where the candidates converge on one shape.
- The synthesized artifact stays coherent under one mental model.
- Verification of the synthesized artifact, done as for any other output, leaves no problem papered over.
- Every substituted slug, dropped seat, candidate dropout, skipped judge, and vendor check that did not run is stated.

## Activities & Tasks

The following Tasks are required whenever this skill runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

### Run tracking

1. Open a todolist with one entry per phase (Frame, Fan out, Cross-judge, Pick, Graft, Verify) before launching anything.

### Phase A: Frame

1. State the artifact each candidate is producing.
2. Derive the rubric, 3-6 concrete gradeable criteria for what success looks like on *this* task. It is the picker's tool in Phase D. Candidates only see the task.
3. Pick the runners from the `arena runners` line in `~/.cursor/rules/pstack-models.mdc`, by default `claude-fable-5-2-high`, `claude-opus-5-5-high-fast`, and `gemini-4-neon-high`. An `auto` or `inherit-parent` entry is the parent model, so omit `model` and spawn `generalPurpose`. If the Task tool rejects a slug, use the nearest valid slug of the same family or drop the seat, keep at least two runners, and say so. Families go by prefix, and the longest match wins: `claude-fable-*`, `claude-*`, and `gemini-*`, after dropping a leading `cursor-`. Any other slug's family is its text before the first hyphen. Spawn more for multiple design directions, and repeat one model when the work is generation-bound, not judgment-sensitive. Pick each subagent's reasoning level per the Subagents section of the **poteto-mode** skill.
4. Give each candidate its own output location (a git worktree where possible, otherwise `/tmp/arena-<slug>/candidate-<n>/`), per the **separate-before-serializing-shared-state** principle skill.

### Phase B: Fan out

1. Spawn all N subagents in one message with `run_in_background: true`, each with the task, the path to the shared grounding, its own output path, and instructions to produce the artifact and a short rationale naming the alternatives it considered and what it rejected.

    If a candidate produces no output, proceed with N-1 and note the dropout.

### Phase C: Cross-judge

1. After all Phase B candidates complete, spawn one readonly judge from the `arena cross-judge pool` line in `~/.cursor/rules/pstack-models.mdc`, by default `claude-opus-5-5-high-fast`, `gemini-4-neon-high`. The judge is never from the parent's vendor, and Fable counts as Claude for that check, so use the first entry from another vendor. An `auto` or `inherit-parent` entry is the parent model. If you do not know the parent's model, use the first real slug and say that the vendor check did not run. If the Task tool rejects a slug, use the nearest valid slug of the same family, then the next such entry, or skip the judge, and say so. While you read in Phase D, the judge scores each candidate, by path label, on each rubric criterion and recommends a base.

### Phase D: Pick a base

1. Read every candidate end to end before picking. Score each against the rubric criterion by criterion, not on holistic feel, and compare with the cross-judge when Phase C ran one. Agreement on the base confirms the pick. Disagreement means one of you is biased or the rubric was ambiguous. Read both rationales before deciding.
2. Pick the base a future maintainer can extend most easily without breaking invariants. When two feel tied, prefer the cleaner boundary or smaller API, per the Laziness Protocol.

### Phase E: Graft

1. Walk each losing candidate once more for what is worth porting into the base, usually one or two things per candidate, not most of it. Fold each graft in by hand, per the **redesign-from-first-principles** principle skill, so the result stays coherent under one mental model. Don't paste mechanically.

    If the candidates converge on one shape, that is strong agreement. Note it and ship the consensus shape. No graft is needed. If they wildly diverge, Phase A was under-specified. Reframe and re-run rather than averaging the divergence.

### Phase F: Verify

1. Verify the synthesized artifact like any other output, per the **prove-it-works** principle skill. If verification finds a problem the arena missed, either Phase A was wrong (re-frame and re-run) or a candidate caught it and you missed the graft (go back to Phase E). Don't paper over it.

## Outputs

One synthesized artifact, with a short synthesis note alongside naming the base and why, the cross-judge's verdict or that Phase C skipped the judge, each graft with its source candidate, what was rejected and why, any convergence or dropouts, and the verification result.

## Constraints

Every candidate gets the same prompt, so the prompt is the contract.

Unless a Task states otherwise, work the Activities and their Tasks in the order listed. These dependencies are required.

- The todolist is open before anything launches.
- Phase B spawns the runners that Phase A step 3 picks and passes each the output location that step 4 gives it.
- Phases C and D score against the rubric that Phase A step 2 derives.
- Phase C starts after all Phase B candidates complete.
- The Phase C judge scores while the candidates are read in Phase D.
- In Phase D every candidate is read end to end before the base is picked.
- Phase E grafts into the base that Phase D picks.
- Phase F verifies the artifact that Phase E leaves.
