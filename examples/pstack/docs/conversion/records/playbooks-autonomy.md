# Conversion record: Playbooks: autonomous runs and handoffs

[Conversion guide](../README.md)

## `skills/poteto-mode/playbooks/autonomous-run.md`

Title: Autonomous run. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Drive a task to a defined exit condition without stopping, with each iteration keeping only the changes that verifiably advance it, and surface a genuine dead end rather than spinning.

| Outcome | Basis in the upstream text |
| --- | --- |
| The exit condition is stated as a checkable predicate before the first iteration. | Step 1: "State the exit condition as a checkable predicate before the first iteration (tests green, repro fixed, all N PRs merged, pixel-diff zero)." Lead line: "Define done". |
| The run does not stop before the predicate is met, except at a genuine dead end it surfaces. | Step 6: "Stop when the predicate is met. A plateau is not a stop, so keep going and pivot your approach to push past it. Surface a genuine dead end rather than spinning". Step 4 lists "a real dead end" among what is surfaced. Lead line: "drive to it without stopping". Written as a stop rule, not a fixed ending, so a run that waits on a call surfaced under step 4 does not read as failed. |
| The predicate is not relaxed to declare victory. | Step 6: "never relax the predicate to declare victory". Split from the stop rule because either can hold without the other. |
| Every change step 3 keeps was verified against the predicate and advanced it. | Step 3: "Each iteration makes the smallest change the evidence justifies, verifies it against the predicate, commits if it advanced, discards changes that didn't help. Belt-and-suspenders that \"might help\" gets reverted, not left to ride." Reply: "what landed, what was discarded". Scoped to step 3's iteration changes, because step 4 keeps out-of-band fixes in their own PR that need not move the predicate. |
| No reversible work is parked for the human. | Lead line: "drive to it without stopping". Step 4: "Do not park reversible work for the human or use `AskQuestion`. Surface only irreversible actions, genuine product or preference calls no experiment can settle, or a real dead end." Step 5's checkpoint row is an Output and stays Task 5. It is not lifted into an Outcome. |

Order dependencies stated under Constraints, with the reason for each:

- Step 1 comes before the first iteration, because step 3 verifies each change against the predicate that step 1 states. Reason: Step 1 says "before the first iteration", and step 3 verifies "against the predicate" that only step 1 states.
- Step 5 writes an iteration's row after that iteration's change and check in step 3, because the row records what changed and whether the predicate moved. Reason: Step 5 asks for "a row for what changed and whether the predicate moved", which only the iteration's change and its check in step 3 produce.
- The iterations of step 3 continue until step 6 stops the run. Reason: Step 3 is stated per iteration and step 6 says "Stop when the predicate is met. A plateau is not a stop, so keep going".

State-changing or external effects the work can have, with the condition upstream states:

- Commits a change in each iteration (step 3). Condition upstream states: Only "if it advanced" on verification against the predicate.
- Discards or reverts changes (step 3). Condition upstream states: Changes "that didn't help", and belt-and-suspenders that "might help".
- Opens PRs for out-of-band fixes (step 4: "Put out-of-band fixes in their own PR"). Condition upstream states: None stated in this playbook. The fixes go through poteto-mode, whose Autonomy section lets reversible work proceed without asking.
- Starts a watcher subagent and a `/loop` heartbeat (step 2). Condition upstream states: None stated.
- Writes a checkpoint row every iteration through the show-me-your-work skill (step 5). Condition upstream states: Every iteration.
- Irreversible actions. Condition upstream states: Not taken on the run's own authority. Step 4 lists them among the only things to surface to the human.

Also: 2 statements moved to the section their function calls for; 6 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-mode/playbooks/autopilot-full.md`

Title: Autopilot-full. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Carry each PR of a queue from build to merge under one owner whose work a replacement can find, inside the operator's grant, with nothing merged until a swarm that never wrote the code has proven the code that lands.

| Outcome | Basis in the upstream text |
| --- | --- |
| Each PR the grant covers lands on its own, or stands at an open operator gate or the operator's stop. | Lead line: "One owner carries each PR from build to merge". Step 3: "so each PR lands on its own". Step 1: "The grant covers only the queue's items". The alternatives are the ones upstream provides: the Reply's "open operator gates" and step 7's operator's stop. Step 7's zero-writes order is a limit on agents. It stays in Task 7 and is not a separate Outcome. |
| Items the operator names as theirs and PRs outside the queue stop at merge-ready, or earlier at the operator's stop. | Step 1: "The grant covers only the queue's items, so items the operator names as theirs and PRs outside the queue stop at merge-ready." Reply: "open operator gates". Step 7: "Stand down at once on the operator's stop." supplies the earlier ending (profile amendment 3). |
| Every merged PR lands code proven, before the merge, by a swarm that never wrote it. | Lead line: "nothing merges until your swarm, which never wrote the code, has proven the code that lands". Step 4 ("Swarm-verify once", independent verifiers, the live lane). Step 5 lead: "The owner merges only what you verified". |
| Every merged PR is tested on the trunk it lands on, as step 5's cases decide, at a head with its own green CI. | Step 5: "tested on the trunk it lands on", "Green CI alone never authorizes a merge", "merge prep rebases onto current trunk, reports the new head, and waits for green CI", and its second paragraph's cases, including the lockfile case and "Otherwise merge". Lead paragraph: "green CI covers one head" and "every new head needs its own green CI". |
| Every loosened gate carries a verifier's proof and then the root's fresh countersign. | Step 6, first paragraph: "Anything that loosens a gate, such as a raised budget or an allowlist entry, needs a verifier's proof and then your fresh countersign". The sentence "Never give or bypass an approval the forge enforces" is a limit on agents. It stays in Task 6 and is not an Outcome. |
| No disabled or soft-failed check is left in place. | Step 6, first paragraph: "A disabled or soft-failed check always comes out, because it stops guarding every case." Split from the countersign Outcome because either can hold without the other. The wording holds whether "comes out" means the check or its disablement is removed. |
| Each owner's work, heads, and agents are on record where a replacement can find them. | Step 2 lead: "keep its work where a replacement can find it". Step 2, third paragraph: push early, the decision trail in the root agent's store, "Whoever spawns a subagent records its id, state, and a stuck-after runtime". Step 2: "Report every later head". Step 6: drift is "an unreported head or an unrecorded agent", "a gap in the record". |

Order dependencies stated under Constraints, with the reason for each:

- Step 1 comes first, because its gates decide which PRs may go past merge-ready. Reason: Step 1 lead: "The operator's gates come first." Its gates are the approval for the merge of step 5 ("stop at merge-ready").
- The full swarm of step 4 runs at the code-ready head that the owner reports in step 2. Reason: Step 4: "A full swarm runs once, at the code-ready head" and "at the code-ready SHA". Step 2: "report the code-ready head before self-proof". Only step 2 produces that head.
- The verdict of step 4 is not clean before the root audits the receipts of the merge-ready report from step 2. Reason: Step 4: "The verdict is not clean without the live lane, or before you audit the merge-ready report's receipts". Step 2: the owner reports "merge-ready once self-proof, CI, and babysit are done".
- Merge prep in step 5 starts once the swarm's lanes of step 4 have started. Reason: Step 5: "Once the swarm's lanes have started, merge prep rebases onto current trunk, reports the new head, and waits for green CI."
- An owner merges once steps 4 and 5 clear its PR. Reason: Step 2: the owner "merges once steps 4 and 5 clear it". Lead line: "nothing merges until your swarm ... has proven the code that lands".
- The first paragraph of step 6 holds throughout the run and does not wait for the steps listed before it. Reason: its rules are standing rules with no time of their own, and the listed order would otherwise place the gate rule after the merge it governs.
- The audit of step 6 runs from the operator's go until no delegated work is left, and step 7 applies at once on the operator's stop, so neither waits for the steps listed before it. Reason: Step 6: "On the operator's go, arm `/loop 1h` to audit until no delegated work is left". Step 7: "Stand down at once on the operator's stop." Both steps state their own timing, which the listed order would otherwise hide.

State-changing or external effects the work can have, with the condition upstream states:

- Spawns one Cursor cloud agent per PR as its owner (step 2). Condition upstream states: The operator's grant, which "covers only the queue's items" (step 1). "A request to state the plan is not a go."
- Owners open PRs early, per `playbooks/opening-a-pr.md` (step 2). Condition upstream states: None beyond the grant.
- Owners push branches, and rebase and publish with `git push --force-with-lease` (step 2). Condition upstream states: "Force-push only your own branch, with `--force-with-lease` pinned to the SHA you last pushed or took over, and on any push you did not make, stop and report to the root." Fix rounds stay on the base unless trunk conflicts, breaks CI, or lands a known concurrent change to the same files.
- Owners merge PRs (steps 2 and 5). Condition upstream states: Only queue items the grant covers. Items the operator names as theirs and PRs outside the queue stop at merge-ready (step 1). The owner "merges once steps 4 and 5 clear it", "merges only what you verified, tested on the trunk it lands on", and "Green CI alone never authorizes a merge." The cases of step 5's second paragraph decide rebase, check, or merge. A third rebase past merge prep means hold and report to the root.
- Loosening a gate, such as a raised budget or an allowlist entry (step 6). Condition upstream states: "needs a verifier's proof and then your fresh countersign". "Under a grant that covers approvals, that countersign is the approval". "A disabled or soft-failed check always comes out". "Never give or bypass an approval the forge enforces".
- Writes decision trails and agent records to the root agent's store (step 2). Condition upstream states: Required of every owner and of whoever spawns a subagent.
- Arms `/loop 1h` for the audit (step 6). Condition upstream states: "On the operator's go".
- Replaces a stuck agent (step 6). Condition upstream states: The agent is stuck as step 6 defines it. "Replace a stuck agent at once, without waiting for its stop to land." An agent waiting on the root or the operator is not stuck.
- Verifiers drive the load-bearing behavior live on the real surface (step 4). Condition upstream states: Through its control skill or a named driver. No approval stated.
- Posts catch-ups to the operator per the ketchup skill (step 6 and the Reply). Condition upstream states: A tick "that changed something for the operator". One that changed nothing stays quiet.
- All writes stop (step 7). Condition upstream states: "at once on the operator's stop". Each owner keeps its brief "until the operator releases it".

Also: 3 statements moved to the section their function calls for; 10 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-mode/playbooks/autopilot-stack.md`

Title: Autopilot-stack. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Bring each PR to verified and green under the Autopilot-full playbook, stacking a PR only when it builds on another PR, and hand the PRs to the operator unmerged.

| Outcome | Basis in the upstream text |
| --- | --- |
| Each PR is verified and green at its current head when the PRs are handed to the operator, or stands at an open operator gate or the operator's stop. | Step 1: "Stop when each PR is verified and green at its current head, then hand the PRs to the operator." Lead sentence: "Run the Autopilot-full playbook", whose step 1 stops items the operator names as theirs and PRs outside the queue at merge-ready and whose step 7 stands down at once on the operator's stop. Those are the alternative endings upstream provides (profile amendment 3). |
| The run merges no PR. | Lead sentence: "Run the Autopilot-full playbook, but do not merge." Step 1: "the no-merge rule". Reply: "in place of what merged". Scoped to the run, because the operator lands the PRs after the handoff (README: "for the operator to review and land"). |
| A PR is stacked only where it builds on another PR. | Step 2: "Stack a PR only when it builds on another PR. This is the one exception to step 3." |

Order dependencies stated under Constraints, with the reason for each:

- Step 1 of this playbook takes the place of step 5 of the Autopilot-full playbook, so it applies where that step would. Reason: Step 1: "In place of step 5, stop at verified."
- Step 2 of this playbook changes steps 2 and 3 of the Autopilot-full playbook, so it applies when those steps run. Reason: Step 2: "This is the one exception to step 3." and "In place of step 2's rebase onto trunk".

State-changing or external effects the work can have, with the condition upstream states:

- Every state-changing effect of the Autopilot-full playbook except the merge (spawning owners, opening PRs, pushes, force-pushes of an owner's own branch, the audit loop). Condition upstream states: The conditions the Autopilot-full playbook states for each.
- Merge. Condition upstream states: Never. "Run the Autopilot-full playbook, but do not merge."
- Pushes after the handoff. Condition upstream states: "After the handoff, nobody pushes without the operator's go."
- Bases a PR on another PR's branch and restacks the PRs above a lower PR's new head (step 2). Condition upstream states: Only when the PR builds on that other PR. The stack root rebases onto trunk.
- Hands the PRs to the operator (step 1). Condition upstream states: "when each PR is verified and green at its current head".

Also: 2 statements moved to the section their function calls for; 5 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-mode/playbooks/session-pickup.md`

Title: Session pickup. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Take over a prior agent's in-flight work at its resume point from the prior trail, with the inherited claims verified. The routed playbook owns the remaining work.

| Outcome | Basis in the upstream text |
| --- | --- |
| Where the prior agent stopped is established from the prior trail. | Step 1: "Locate the prior trail." Step 2: "Reconstruct operational state. ... The prior trail is authoritative input." Reply: "where the prior agent stopped". |
| The resume point is named from a comparison of what shipped against what was planned. | Lead line: "You own the resume point." Step 3: "Compare what shipped against what was planned, name the resume point". Reply: "the resume point". |
| The remaining work is routed to the matching playbook, with the verdict picked. | Step 4: "Route the remaining work to the matching playbook and pick the verdict: continue the execution, ship a finished recommendation, ratify or override a prior conclusion, or postmortem a failed run." |
| The inherited claims are verified against the original goal on the real artifact, not taken from a prior self-report. | Step 5: "Verify the inherited claims against the original goal on the real artifact (the **principle-prove-it-works** skill). A passing prior self-report is not the proof." |

Order dependencies stated under Constraints, with the reason for each:

- Step 2 reconstructs state from the trail that step 1 locates. Reason: Step 2 treats "The prior trail" as "authoritative input", and only step 1 locates it.
- Step 3 compares what step 2 reconstructs. Reason: Step 3 compares "what shipped against what was planned", which step 2 reconstructs ("what already landed", "the open todos, the decisions made").
- Step 4 routes the remaining work that step 3 identifies. Reason: Step 4 routes "the remaining work", the pending side of step 3's "Diff done vs pending".

State-changing or external effects the work can have, with the condition upstream states:

- Reads transcripts under the active workspace's `agent-transcripts/` directory (step 1). Read-only. Condition upstream states: "Do not glob across `~/.cursor/projects/*/`, that crosses workspace boundaries and reads private chats from unrelated projects".
- Starts a subagent to parse a long transcript (step 1). Condition upstream states: For a long transcript. The reduced timeline stays in the main thread.
- Drives the real artifact to verify inherited claims (step 5). Condition upstream states: None stated.
- No push, merge, or other external write is instructed by this playbook. Condition upstream states: "The routed playbook owns the rest."

Also: 2 statements moved to the section their function calls for; 6 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-mode/playbooks/pause-safely.md`

Title: Pause safely. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Bring in-flight work to a clean stop that a cold-start agent can resume from, only when the pause is explicit.

| Outcome | Basis in the upstream text |
| --- | --- |
| The work stands at a safe boundary, with the current atomic step finished or backed out and nothing new started. | Step 1: "Stop at a safe boundary. Finish the current atomic step or back out of it. Start nothing new". |
| No nested subagent is left running. | Step 1: "cancel any nested subagents". Split from the boundary Outcome because a pause can meet one and not the other. |
| No irreversible action is taken to pause, with no PR and no push unless one was already out. | Step 2: "Take no irreversible action to pause. No PR and no push unless you already had one out." |
| Uncommitted edits are held in one clear `wip:` commit on the current branch, so nothing is lost. | Step 3: "Make the work durable. Commit uncommitted edits as one clear `wip:` commit on the current branch so nothing is lost." |
| A cold-start agent can resume from the checkpoint, with the resume note held off-context. | Lead line: "Leave a checkpoint a cold-start agent can resume from." Step 4: "Write the resume note off-context." The Reply asks for "the first action on resume". |

Order dependencies stated under Constraints, with the reason for each:

- Step 2 holds for every action taken to pause. Reason: Step 2 limits what may be done "to pause", which covers steps 1, 3, and 4. It is a standing prohibition written as a numbered step.
- Step 3 commits and step 4 records the state that step 1 leaves. Reason: Step 3 commits edits "as one clear `wip:` commit" "so nothing is lost", and step 4 captures "current state". Both need the stop of step 1 to have happened.

State-changing or external effects the work can have, with the condition upstream states:

- Cancels nested subagents and may back out of the current atomic step (step 1). Condition upstream states: Always, at the safe boundary.
- Creates one `wip:` commit on the current branch (step 3). Condition upstream states: For uncommitted edits. A broken tree is stated in the commit body in one line.
- PR or push (step 2). Condition upstream states: "No PR and no push unless you already had one out." No irreversible action is taken to pause.
- Writes the resume note outside the context, for the compaction trigger to a file like `/tmp/<slug>-resume.md`, which is outside the repository (step 4). Condition upstream states: If a show-me-your-work trail exists, the note points at it and does not duplicate it.

Also: 2 statements moved to the section their function calls for; 5 additions other than the Purpose and Outcomes (fixed sentences, pointers).
