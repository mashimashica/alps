# Worktree and simulator cleanup

## Purpose

Reclaim disk space held by worktrees, simulators, and caches, deleting a worktree that is in use or holds tracked uncommitted edits only on the user's decision, and let the user see the space reclaimed, the worktrees pruned, and why each one held back was kept.

## Outcomes

- A re-list of the worktrees no longer shows any worktree of the confirmed set.
- No worktree that a pinned or active chat uses is pruned without the user's decision.
- No tracked uncommitted edit is removed before the user has seen its diff and decided.
- No cache the user has said to keep is cleared.
- Every worktree held back has a one-line reason (in-use by which chat, or uncommitted work).
- The space reported as reclaimed follows from a `df -h /` reading recorded before anything was deleted and one taken after.

## Tasks

The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. Snapshot and audit. Record `df -h /`, then run `scripts/worktree-audit.sh [-b <pr-base-ref>] [repo-path]` (principle-build-the-lever). Without `-b` it checks `MERGED` against `origin/HEAD`, so pass `-b origin/<branch>` when PRs target another branch. It reads paths from `git worktree list`, never hand-typed, since a hand-typed `myrepo-worktrees/x` misses one that lives at `.cursor/worktrees/myrepo/x` (principle-encode-lessons-in-structure). It classifies each worktree by size, age, merge state, uncommitted work, PR state, and the newest chat that touched it, then suggests a bucket. The transcript scan is slow, so background it.
2. The bucket is advice, not permission. The pinned and active chats are the real artifact (principle-prove-it-works). Get that set from the user or sidebar and cross-check every candidate. The lever has marked `safe` a worktree the user had pinned, so the pinned set wins.
3. Verify usage before deleting. For every `verify-recent-chat` row, or anything you doubt, fan subagents out to read the transcripts and report whether the chat is pinned or ongoing and which worktrees it touches (principle-guard-the-context-window, transcripts are bulk). A pinned chat spawns arena and repro trees into sibling worktrees via background subagents, and those are in use even when their names never hit the sidebar. Pick each subagent's reasoning level for the job, per the Subagents section.
4. Pause on irreversible loss. `wip:N` is N tracked uncommitted edits. Show the diff and get a decision first, since removing a clean worktree is recoverable from its branch but uncommitted work is gone. `scratch:N` is untracked throwaway, safe to drop, but name the files. Per Autonomy, clean and merged and not-in-use proceeds. `wip` and in-use pause.
5. Prune the confirmed set. Per path, `git worktree remove --force <path>`. If the dir survives on ignored build artifacts, `rm -rf` it, then `git worktree prune`. Branch refs survive, so no commits are lost. Confirm with `df -h /` and re-list.
6. Simulators and other reclaimers. Simulators are usually the next-biggest win. `xcrun simctl --set testing delete all` (XCTestDevices clones), `xcrun simctl delete unavailable`, and `xcrun simctl runtime list` then `runtime delete <id>` for old runtimes. More when needed: Xcode `DerivedData` and `iOS DeviceSupport`, `~/Library/Application Support/Cursor` (`state.vscdb.backup`, and `snapshots/roots/<root>` where a `<root>` named for a folder you opened as a workspace balloons), package caches (pnpm, uv, brew, yarn). Clear only caches the user has not said to keep.

## Outputs

**Reply:** `df -h /` before and after with space reclaimed, the worktrees pruned, and a one-line reason for each held back (in-use by which chat, or uncommitted work).

## Constraints

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Step 1 records `df -h /` before anything is deleted, because the Reply reports it before and after.
- The cross-check in step 2 and steps 3 and 4 follow the audit of step 1, because they work on the rows it prints.
- Step 5 follows steps 2, 3, and 4, because it prunes only the set they confirm.

This is the one playbook that deletes user state with no code review to catch a slip, so the gates above are the review.

## Enablers

`scripts/worktree-audit.sh` is bundled with this skill. Its invocation, results, exit statuses, dependencies, effects, and limits are in [tool use](../references/tool-use-worktree-audit.md).
