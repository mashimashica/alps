---
name: no-comments
description: "Spawn Comment Sicko, fix accepted findings, and offer encodings for claimed constraints."
disable-model-invocation: true
---

# No comments

## Purpose

Clear the scope of comments that do not survive Comment Sicko's fresh perspective, and act on the accepted findings so that the code behind each accepted flag is fixed and each constraint a comment claimed is encoded or reported open.

## Outcomes

- No application-code edit, scope escape, or exception-protected deletion by Comment Sicko stands.
- No accepted flag misstates its `MUST KILL` reason or treats kept intentional code as guilty.
- Every restored deletion has an exact exception and scoped proof.
- Every keep that is refuted or still ambiguous is deleted.
- Every accepted flag has its smallest root-cause fix in scope with every named workaround removed, or, where the root cause is out of scope, the smallest in-scope fix with the rest reported open.
- Each constraint comment that is not a keep about things we cannot change is deleted, with its constraint encoded where approval was given and otherwise reported open with the out-of-scope work sketched.
- The report names the deletion count, restored comments, reruns, architect sketch, fixes, encoding offers, encodings, unenforced constraints, and other open work.

## Tasks

The following Tasks are required whenever this skill runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. Spawn `Task` with `subagent_type: "comment-sicko"`. Pass the scope. Pick each subagent's reasoning level for the job, per the Subagents section of the **poteto-mode** skill. Do not restate its rules.
2. Inspect its report and diff. Reject application-code edits, scope escapes, exception-protected deletions, misstated `MUST KILL` reasons, and flags that treat kept intentional code as guilty. Reshape flags on our-code surprises stay actionable. Do not restore those comments. A keep survives only with proof it is about something we cannot change. Audit missed scoped lint and TypeScript suppressions. Correctness or safety suppressions stay actionable `MUST KILL`s. Restore deletions only with exact exceptions and scoped proof. Before accepting thin `IMPORTANT` or `do not remove` kills or keeps, trace their symbol or run `/why` on it. If a kill is ambiguous, do not restore. If a keep is refuted or still ambiguous, delete it. Revert and rerun one rejected report with the failure named. Reject a second, report it open, and fail `/no-comments`.
3. Fix trivial accepted flags directly by deleting a dead path, dropping a parameter, or using the real API. If any fix needs a shape, run `/architect` once for the accepted set and surrounding code. Stop at the sketch. Architect shapes. Step 4 implements.
4. Implement the smallest root-cause fix in scope. Remove every named workaround. If the root cause is out of scope, land the smallest in-scope fix and report the rest open. The **principle-fix-root-causes** and **principle-redesign-from-first-principles** skills guide intent only. Neither authorizes widening the fence nor fixing instances outside it. Never bolt on symptom guards.
5. Constraint comments say `do not remove`, `do not change wording`, or `talk to X before changing`. Leave keeps about things we cannot change. Offer the cheapest in-scope type, runtime, test, or CI lint. Wait for interactive approval. Unattended and eval require caller pre-approval. If approved, encode then delete. Otherwise delete, report the constraint open, and sketch out-of-scope work.
6. Report the deletion count, restored comments, reruns, architect sketch, fixes, encoding offers, encodings, unenforced constraints, and other open work.

## Inputs

### Scope

Use the caller's files or diff. Otherwise use the current diff against the base branch, default `main`, including the working tree.

## Controls

Defer to Comment Sicko's fresh perspective.

## Constraints

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Step 1 comes before step 2, which inspects the report and diff that the spawn returns.
- Step 2 comes before steps 3 to 5, which act on accepted findings.
- Step 3 comes before step 4, which implements what step 3 sketches.
- Step 6 comes last, because it reports what the other steps did.
