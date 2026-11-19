# Multi-phase or multi-PR plan

## Purpose

Give multi-phase or multi-PR work a plan that an owner can run box by box and the operator can audit from the evidence, without implementing it.

## Outcomes

- The plan opens with what changes, the PR ids in landing order, and the dependency graph, and has one section of checkboxes per PR. Where the change is one or two files with an obvious approach, the plan is skipped instead and the skip is stated.
- Each PR in the plan is one change with its own evidence.
- Each PR's verification in the plan has unit, live, and perf boxes.
- The plan marks every PR that changes an interaction as waiting for the operator's review before merge.
- The open questions that a run can settle are settled by prototype before the plan is written.
- No part of the plan is implemented in this run.

## Tasks

The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. When the change is one or two files with an obvious approach, skip the plan. Say so and stop.
2. Settle open questions by prototype before you write, per `playbooks/prototype.md`. Ask the operator only about a product or preference call that no run can settle.
3. Write the plan file. Open with what changes, the PR ids in landing order, and the dependency graph, which says which PRs are independent and branch from trunk, which wait for which, and the files each may touch. Then one section per PR. One PR is one change with its own evidence (the **sequence-verifiable-units** principle skill). Each section has checkboxes for what it depends on, the files it edits, the one change it builds, the result you see, and its verification.
4. Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked. Each live box drives the real surface with a concrete scenario and a pass predicate. The perf box names the metric, the probe, the trunk baseline measured first, and the number that fails. A PR that changes an interaction waits for the operator's review before merge.
5. Hand back the plan path and stop. Execution starts on the operator's explicit go.

## Outputs

**Reply:** the plan path, the PR ids with their dependencies and the review-gated set, and what stays unproven.

## Constraints

**You own the plan, not the code. The plan is a checklist an owner runs box by box and the operator audits from the evidence.** The plan is the deliverable. Do not implement.

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Step 1 comes before every other step, because it can skip the plan.
- Step 2 comes before step 3, because open questions are settled before the plan is written.
- Step 5 follows step 3, because it hands back the path of the plan file.
