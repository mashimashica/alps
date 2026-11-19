# Session pickup

## Purpose

Establish the resume point of a prior agent's work from the prior trail, without redoing that work. The routed playbook owns the remaining work.

## Outcomes

- Where the prior agent stopped is established from the prior trail.
- The resume point is named from a comparison of what shipped against what was planned.
- No completed work is redone, the prior repro included.
- The remaining work is routed to the matching playbook, with the verdict picked.
- The inherited claims are verified against the original goal on the real artifact, not taken from a prior self-report.

## Tasks

The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. Locate the prior trail. A local transcript under the active workspace's `agent-transcripts/` directory (the system prompt names the path. Do not glob across `~/.cursor/projects/*/`, that crosses workspace boundaries and reads private chats from unrelated projects), a cloud-agent URL, or a pushed branch. Read the metadata overview and last messages first, then scan back for the decision points. Parse a long transcript in a subagent and keep the reduced timeline in the main thread (the **principle-guard-the-context-window** skill). Pick each subagent's reasoning level for the job, per the Subagents section.
2. Reconstruct operational state. The branch and worktree, what already landed (`git log`, `git diff` against the base), the open todos, the decisions made. The prior trail is authoritative input. Resist the bias to re-derive it.
3. Diff done vs pending. Compare what shipped against what was planned, name the resume point, do not re-run the prior repro or redo completed work. A "let me verify from scratch" pass means you're treating the trail as untrustworthy when it's authoritative.
4. Route the remaining work to the matching playbook and pick the verdict: continue the execution, ship a finished recommendation, ratify or override a prior conclusion, or postmortem a failed run. The pickup playbook ends here. The routed playbook owns the rest.
5. Verify the inherited claims against the original goal on the real artifact (the **principle-prove-it-works** skill). A passing prior self-report is not the proof.

## Outputs

**Reply:** where the prior agent stopped, what you inherited vs redid (ideally nothing redone), the resume point, and the outcome.

## Constraints

**You own the resume point. Read the prior trail, don't redo it.**

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Step 2 reconstructs state from the trail that step 1 locates.
- Step 3 compares what step 2 reconstructs.
- Step 4 routes the remaining work that step 3 identifies.
