---
name: figure-it-out
description: "Design an auditable playbook when no narrower one fits: a large migration, an ambitious multi-part change, or work a human reviews after stepping away. Scales rigor to the task, runs a hypothesis loop, and logs decisions. Use for /figure-it-out or 'figure it out'."
disable-model-invocation: true
---

# Figure it out

## Purpose

Give a task that matches no playbook a workflow designed for it, and take the task through that workflow so that a human who stepped away can audit the decisions and trust the work.

## Outcomes

- Before the run starts, the definition of done is a falsifiable predicate, the scope is quantified, and the rigor level is set.
- The phase list written before any code scales rigor to the task, runs the scientific method, and leaves a decision trail a human can audit after stepping away.
- Each unit that stays in the work advanced the predicate when measured on the real artifact.
- The decision trail has a row for each step of the design, written as the step landed.
- The whole's standing against the Phase A predicate is established on the real product, not just the harness.
- The reply's account of what is verified against the predicate and what is still open hides no negative and counts no inconclusive result as a pass.
- Where a correction recurred, a gate, a lint rule, a check, or a script encodes it.

## Activities & Tasks

The following Tasks are required whenever this skill runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

### Start

1. Open a todolist whose first item is to read the Principles section of the **poteto-mode** skill. Then add the phases below as todos.

### Phase A: Frame

1. Ground first, then commit. Don't start the run until you can state:
   - The definition of done as a falsifiable predicate (the **prove-it-works** principle skill).
   - Scope, quantified: rough units and effort, plus the blockers grounding surfaced.
   - The rigor level, biased high. One-way doors and high blast radius get more. Reversible low-stakes steps get less. Rigor is gates and artifacts, not "try harder".
2. Present the framing and tradeoffs before committing to a long run. Reversible work proceeds (the **never-block-on-the-human** principle skill), but a multi-hour run earns one checkpoint.

### Phase B: Design the workflow

1. Decompose into atomic, independently-landable units. Sequence riskiest-unknown-first. Scaffold and verification come before features (the **foundational-thinking** principle skill).
   - Build the verification harness before the work, with the baseline captured from the pre-change state, so the check reads as "old value vs new value".
   - For one-way-door design decisions, run the **architect** skill (it runs **arena**). Skip it for mechanical work whose shape is already concrete. A second arena over a settled design is over-engineering (the **laziness-protocol** principle skill).
   - Decide what fans out. Parallelize only across seams, and give each worker its own worktree or branch (the **separate-before-serializing-shared-state** principle skill). Don't over-fan. Pick each subagent's reasoning level for the job, per the Subagents section of the **poteto-mode** skill.
   - Write the designed phase list down. That list is what the human reviews.
2. Then execute the design. Add its steps to the todolist as concrete items between the Phase C and Phase D entries. Run each under the Phase C loop discipline, and weave the Phase D log through them, a row as each step lands, rather than saving the whole trail for the end.

### Phase C: Run the loop

1. Each unit is an experiment. State the hypothesis, make the smallest change, measure against the predicate on the real artifact, keep it if it advanced, revert it if it didn't. Apply the **sequence-verifiable-units** principle skill, verifying each unit before starting the next instead of batching checks at the end.
   - Verify by inspecting the artifact, never a self-report. When something passes too easily, suspect the observation method before the system.
   - Pair delegated work with a judge. If a worker games the gate, reset and harden the contract. If the gate itself is wrong, fix the gate in its own change rather than routing around it.
   - A verdict is VERIFIED, NOT VERIFIED, or INCONCLUSIVE. Inconclusive is not a pass. Don't hide a negative.

### Phase D: Keep the audit trail

1. Log the run via the **show-me-your-work** skill. figure-it-out's work is usually ambitious enough to commit the trail so the reviewer can read it in the PR. The trail plus the diff is what lets the human come back and trust the work.

### Phase E: Verify and hand back

1. Check the whole against the Phase A predicate on the real product, not just the harness.
2. Encode any recurring correction as a gate, a lint rule, a check, or a script (the **encode-lessons-in-structure** principle skill).

## Outputs

The deliverable before any code is the workflow itself: a sequence of phases that scales rigor to the task, runs the scientific method, and leaves a decision trail a human can audit after stepping away.

**Reply:** the playbook you designed, the rigor level and why, the decision-trail path, what's verified against the predicate, and what's still open.

## Constraints

This skill applies when the task matches no playbook. It applies when no narrower one fits: a large migration, an ambitious multi-part change, or work a human reviews after stepping away.

Unless a Task states otherwise, work the Activities in the order listed. Within an Activity, Tasks may be worked in any order unless one states otherwise. These dependencies are required.

- The run does not start until the Phase A statements can be made.
- The framing and tradeoffs are presented before committing to a long run.
- The workflow is the deliverable before any code.
- The verification harness is built before the work, with the baseline captured from the pre-change state.
- The design is executed after it is designed. Phase C and Phase D apply to each of its steps as it runs.
- Each unit is verified before the next one starts.
- Phase E checks the whole against the Phase A predicate, so it follows the executed work.
