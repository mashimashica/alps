# Autopilot-stack

## Purpose

Bring each PR to verified and green under the Autopilot-full playbook, stacking a PR only when it builds on another PR, and hand the PRs to the operator unmerged.

## Outcomes

- Each PR is verified and green at its current head when the PRs are handed to the operator, or stands at an open operator gate or the operator's stop.
- The run merges no PR.
- A PR is stacked only where it builds on another PR.

## Tasks

The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. **In place of step 5, stop at verified.** Stop when each PR is verified and green at its current head, then hand the PRs to the operator. After the handoff, nobody pushes without the operator's go. Every loop tick prompt names this file, so each tick sees the no-merge rule.
2. **Stack a PR only when it builds on another PR.** This is the one exception to step 3. Base the PR on the other PR's branch in place of trunk, per `playbooks/opening-a-pr.md`. In place of step 2's rebase onto trunk, each PR rebases onto its parent PR's branch, and the stack root rebases onto trunk. A new head on the lower PR restacks the PRs above it, and a PR whose `git patch-id` the restack leaves unchanged keeps its verdict.

## Outputs

**Reply:** list each PR with its verdict, in place of what merged.

## Constraints

Run the Autopilot-full playbook, but do not merge.

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Step 1 of this playbook takes the place of step 5 of the Autopilot-full playbook, so it applies where that step would.
- Step 2 of this playbook changes steps 2 and 3 of the Autopilot-full playbook, so it applies when those steps run.
