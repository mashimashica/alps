# Conversion record: arena, swarm, interrogate

[Conversion guide](../README.md)

## `skills/arena/SKILL.md`

Title: Arena. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Produce one synthesized artifact from parallel candidates at the same task, so that one attempt at a non-trivial artifact does not lock in the wrong shape.

| Outcome | Basis in the upstream text |
| --- | --- |
| The base is the candidate a future maintainer can extend most easily without breaking invariants. | Phase D: "Pick the base a future maintainer can extend most easily without breaking invariants." |
| The synthesized artifact carries what is worth porting from each losing candidate, or is the consensus shape where the candidates converge on one shape. | Phase E: "Walk each losing candidate once more for what is worth porting into the base". Alternative ending from Phase E: "If the candidates converge on one shape, that is strong agreement. Note it and ship the consensus shape. No graft is needed." |
| The synthesized artifact stays coherent under one mental model. | Phase E: "Fold each graft in by hand, per the **redesign-from-first-principles** principle skill, so the result stays coherent under one mental model. Don't paste mechanically." |
| The synthesized artifact has been verified like any other output, and every problem that verification finds is taken back to a re-frame and re-run or to Phase E. | Phase F: "Verify the synthesized artifact like any other output, per the **prove-it-works** principle skill. If verification finds a problem the arena missed, either Phase A was wrong (re-frame and re-run) or a candidate caught it and you missed the graft (go back to Phase E). Don't paper over it." Outputs: "and the verification result". It requires that the verification took place, not that it passed or that the problem is resolved, because the loop back has no stop condition. "Don't paper over it." stays in Phase F. |
| Every substituted slug, dropped seat, candidate dropout, skipped judge, and vendor check that did not run is stated. | Phase A step 3: "use the nearest valid slug of the same family or drop the seat, keep at least two runners, and say so". Phase B: "note the dropout". Phase C: "say that the vendor check did not run" and "use the nearest valid slug of the same family, then the next such entry, or skip the judge, and say so". Outputs: "the cross-judge's verdict or that Phase C skipped the judge ... any convergence or dropouts". |

Carried from the frontmatter description into the body:

- "when one attempt at a non-trivial artifact would lock in the wrong shape" (the body gives no reason for the work; carried into the Purpose as the reason, not added as an applicability Constraint. The slash name and the trigger phrases stay in the frontmatter only.)

Order dependencies stated under Constraints, with the reason for each:

- dependency: The todolist is open before anything launches.; reason: Upstream order word: "Open a todolist with one entry per phase (...) before launching anything."
- dependency: Phase B spawns the runners that Phase A step 3 picks and passes each the output location that step 4 gives it.; reason: Result use: Phase B spawns "each with ... its own output path"; the runners and the output locations exist only once Phase A steps 3 and 4 are done.
- dependency: Phases C and D score against the rubric that Phase A step 2 derives.; reason: Result use: step 2 "It is the picker's tool in Phase D"; Phase C "the judge scores each candidate ... on each rubric criterion"; Phase D "Score each against the rubric".
- dependency: Phase C starts after all Phase B candidates complete.; reason: Upstream order word: "After all Phase B candidates complete, spawn one readonly judge".
- dependency: In Phase D every candidate is read end to end before the base is picked.; reason: Upstream order word: "Read every candidate end to end before picking."
- dependency: Phase E grafts into the base that Phase D picks.; reason: Result use: "what is worth porting into the base" needs the picked base and the losing candidates.
- dependency: Phase F verifies the artifact that Phase E leaves.; reason: Result use: "Verify the synthesized artifact"; the synthesized artifact exists only after Phase E.

State-changing or external effects the work can have, with the condition upstream states:

- Spawns one background subagent per runner (N candidates) with the Task tool, and one readonly judge. Condition upstream states: No approval stated. Runners come from the `arena runners` line or its default. At least two runners are kept. The judge is never from the parent's vendor and may be skipped.
- Creates a git worktree per candidate where possible, otherwise writes under `/tmp/arena-<slug>/candidate-<n>/`, which is outside the repository. Condition upstream states: No approval stated. Each candidate gets its own output location, per the **separate-before-serializing-shared-state** principle skill.
- Writes the synthesized artifact and the synthesis note. Phase E says "ship the consensus shape" without saying what shipping does. Condition upstream states: No approval stated. Phase F verification is required, and a problem it finds sends the work back to Phase A or Phase E.

Also: 2 statements moved to the section their function calls for; 5 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/swarm/SKILL.md`

Title: Swarm. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Run a job across N parallel workers and return their results as one report. It serves parallel coverage, races, gauntlets, and exploration.

| Outcome | Basis in the upstream text |
| --- | --- |
| Every counted result is a `PASS`, `ISSUES`, or `BLOCKED` with evidence. | Phase B: "Reports use `PASS`, `ISSUES`, or `BLOCKED` with evidence." Scoped to counted results, because Phase C drops a result that does not record its SHAs and method. |
| Every counted result records the SHAs and method its brief names. | Phase A step 4: "each brief names the exact SHAs. A measurement brief also names the method ... The worker records both in its result." Phase C: "Drop a result that does not record the SHAs and method its brief names". |
| For coverage, every required slice has a result. | Phase C: "For coverage, every required slice needs a result.", next to "A gap does not count as a pass." |
| For a race, the selection follows the rule declared up front. | Phase C: "For a race, apply the selection rule declared up front." Phase A step 2: "For a race or mixed shape, declare `first pass`, `rank all`, or `best-of` before spawning." |
| No gap counts as a pass. | Phase C: "A gap does not count as a pass." |
| The report's result table and issue one-liners agree with the counted results. | Phase D: "Return one consolidated in-chat report with a result table, issue one-liners, gaps or dropouts, and the race rule when used." Phase C: "Do not paste raw worker dumps." The report aggregates what Phase C reads and counts. |
| Every gap and worker dropout is stated, and so is every rejected slug that the default replaced. | Phase C: "After a second miss, record a gap." Phase B: "If a worker drops out, proceed with N-1 and note it." Phase A step 3: "If the Task tool rejects a slug, use the default and say so." Phase D: "gaps or dropouts". Upstream states no "say so" for the fallback from a rejected default, so none is required here. Same treatment as arena's disclosure Outcome. |

Carried from the frontmatter description into the body:

- "drain them" (from "Fan out N parallel workers, drain them, and return one report."; the body says only "Read the terminal results"; carried as the Constraints dependency "The workers are drained before the report is returned.", which keeps the description's order and does not hold Phase C back, since Phase C respawns a worker after reading its result)
- "parallel coverage, races, gauntlets, and exploration" (the body names coverage and race only; carried into the second sentence of the Purpose as the kinds of job the work serves. The slash name and "swarm this" stay in the frontmatter only.)

Order dependencies stated under Constraints, with the reason for each:

- dependency: The todolist is open before anything launches.; reason: Upstream order word: "Open a todolist with one entry per phase before launching anything."
- dependency: For a race or mixed shape, the selection rule is declared before spawning.; reason: Upstream order word in Phase A step 2: "declare `first pass`, `rank all`, or `best-of` before spawning".
- dependency: For a model race, each arm's model is named up front.; reason: Upstream order word in Phase A step 3: "For a model race, name each arm's model up front."
- dependency: Phase B spawns with the model that Phase A step 3 picks.; reason: Result use: Phase B spawns with "the step 3 model".
- dependency: The workers are drained before the report is returned.; reason: Description order: "Fan out N parallel workers, drain them, and return one report." Not anchored to the start of Phase C, which reads each terminal result and may respawn a worker after reading it.
- dependency: Phase C applies the selection rule that Phase A step 2 declares.; reason: Result use: Phase C "For a race, apply the selection rule declared up front."
- dependency: Phase D reports what Phase C aggregates.; reason: Result use: the report's result table, issue one-liners, and gaps or dropouts come from the aggregation.

State-changing or external effects the work can have, with the condition upstream states:

- Spawns N background workers as cloud agents (`subagent_type: generalPurpose`, `environment: "cloud"`, `run_in_background: true`). Condition upstream states: No approval stated. `environment: "local"` only when the worker needs access to something on the user's computer. `cloud_base_branch` when a worker must start from a non-default pushed branch.
- Workers write to their own writable outputs. Condition upstream states: No approval stated. "Give each worker its own writable output when it writes."
- Respawns a worker whose result does not record the SHAs and method its brief names. Condition upstream states: Once per worker. After a second miss a gap is recorded.

Also: 3 statements moved to the section their function calls for; 5 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/interrogate/SKILL.md`

Title: Interrogate. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Find where a change or a design breaks its intent by having adversaries try to break it, and report the findings without applying fixes.

| Outcome | Basis in the upstream text |
| --- | --- |
| The stated intent restates what the user's message, the commits, and the PR description show, and where the intent was unclear it rests on the user's answer. | Frame: "State the intent with the **in-your-own-words** skill, from the user's message, the commits, and the PR description. Ask the user when the intent is unclear." Output: "**Intent**: the restatement." Verify keeps a finding only when "the failure breaks the intent", so every other Outcome depends on it. The quality of the restatement itself is governed by the in-your-own-words skill. |
| Every reported finding is backed by a rerun of its command whose output shows a failure that breaks the intent. | Opening paragraph: "A finding survives only when a run proves it." Verify: "Verify each finding per arena Phase F by rerunning its command. Keep a finding when the output shows the failure and the failure breaks the intent. Drop the rest." |
| The verdict holds every verified finding from every adversary, or the merged finding that contains it. | Verify, second paragraph: "Adversaries find different failures, so the verdict keeps every verified finding, not one adversary's list." Worded with the merge so that it agrees with "Merge findings that share a root cause." |
| Findings that share a root cause are merged into one. | Verify: "Merge findings that share a root cause." |
| Each adversary's dropped findings are counted, with why they were dropped. | Verify: "Drop the rest." Output: "**Dropped**: for each adversary, the count of dropped findings and why." |
| No fix is applied to the scope. | Opening paragraph: "Report the findings. Do not apply fixes." Restated as a result, per profile section 5 for guards. |

Headings whose text changed:

- "## Output" became "## Outputs". Profile section 5 allows only the element headings at level two and sends "## Output" to Outputs. The labels **Intent**, **Findings**, and **Dropped** are unchanged. No file cites the heading. The recipes cite "the Dropped list", which is kept.

Order dependencies stated under Constraints, with the reason for each:

- dependency: The intent is stated before the adversaries are spawned, because each adversary is given it.; reason: Result use: Fan out gives "each adversary the scope, the intent, and this brief"; the intent exists only after Frame.
- dependency: A finding is verified after its adversary reports it.; reason: Result use: Verify reruns the command that the adversary's report gives ("Verify each finding ... by rerunning its command").

State-changing or external effects the work can have, with the condition upstream states:

- Spawns one adversary per entry of the `interrogate reviewers` line as a background `generalPurpose` subagent, through arena Phase B. Condition upstream states: No approval stated.
- Gives each adversary its own output location (a git worktree where possible) through arena Phase A step 4, and copies the scope's uncommitted changes into each worktree. Condition upstream states: No approval stated.
- Adversaries run tests, repro scripts, prototypes, and commands against the real code. The lead reruns each reported command. Condition upstream states: No approval stated. The brief says "Keep repros in your own worktree."
- No fix is applied to the scope. Condition upstream states: Prohibition: "Report the findings. Do not apply fixes."

Also: 5 statements moved to the section their function calls for; 3 additions other than the Purpose and Outcomes (fixed sentences, pointers).
