# Pause safely

## Purpose

Bring in-flight work to a clean stop that a cold-start agent can resume from, only when the pause is explicit.

## Outcomes

- The work stands at a safe boundary, with the current atomic step finished or backed out and nothing new started.
- No nested subagent is left running.
- No irreversible action is taken to pause, with no PR and no push unless one was already out.
- Uncommitted edits are held in one clear `wip:` commit on the current branch, so nothing is lost.
- A cold-start agent can resume from the checkpoint, with the resume note held off-context.

## Tasks

The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. Stop at a safe boundary. Finish the current atomic step or back out of it. Start nothing new, and cancel any nested subagents.
2. Take no irreversible action to pause. No PR and no push unless you already had one out.
3. Make the work durable. Commit uncommitted edits as one clear `wip:` commit on the current branch so nothing is lost. If the tree is broken, say so in the commit body in one line.
4. Write the resume note off-context. Capture intent, what you were doing, progress and what's verified, current state, next steps, key files, and gotchas. For the compaction trigger write it to a file like `/tmp/<slug>-resume.md`. If a show-me-your-work trail exists, point at it instead of duplicating it.

## Outputs

**Reply:** where you are in the loop, what's on disk versus still in your head (paths, no diff dumps), the commits you made and whether the tree is clean, and the first action on resume. This is a pause, not a final report.

## Constraints

**You own a clean stop. Leave a checkpoint a cold-start agent can resume from.** This is explicit only. On "keep going", "going to bed, keep going", or "don't stop", do not pause.

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Step 2 holds for every action taken to pause.
- Step 3 commits and step 4 records the state that step 1 leaves.
