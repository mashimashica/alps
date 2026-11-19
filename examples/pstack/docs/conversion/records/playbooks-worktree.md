# Conversion record: Playbook: worktree cleanup

[Conversion guide](../README.md)

## `skills/poteto-mode/playbooks/worktree-cleanup.md`

Title: Worktree and simulator cleanup. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Reclaim disk space held by worktrees, simulators, and caches, deleting a worktree that is in use or holds tracked uncommitted edits only on the user's decision, and let the user see the space reclaimed, the worktrees pruned, and why each one held back was kept.

| Outcome | Basis in the upstream text |
| --- | --- |
| A re-list of the worktrees no longer shows any worktree of the confirmed set. | Step 5: "Prune the confirmed set. ... Confirm with `df -h /` and re-list." |
| No worktree that a pinned or active chat uses is pruned without the user's decision. | Step 2: "The bucket is advice, not permission. The pinned and active chats are the real artifact ... cross-check every candidate. ... so the pinned set wins." Step 3: "Verify usage before deleting. ... those are in use even when their names never hit the sidebar." Step 4: "Per Autonomy, clean and merged and not-in-use proceeds. `wip` and in-use pause." |
| No tracked uncommitted edit is removed before the user has seen its diff and decided. | Step 4: "Pause on irreversible loss. `wip:N` is N tracked uncommitted edits. Show the diff and get a decision first, since removing a clean worktree is recoverable from its branch but uncommitted work is gone." |
| No cache the user has said to keep is cleared. | Step 6: "Clear only caches the user has not said to keep." |
| Every worktree held back has a one-line reason (in-use by which chat, or uncommitted work). | Reply paragraph: "a one-line reason for each held back (in-use by which chat, or uncommitted work)". Necessary for the reporting clause of the Purpose. |
| The space reported as reclaimed follows from a `df -h /` reading recorded before anything was deleted and one taken after. | Step 1: "Record `df -h /`" (before any deletion). Step 5: "Confirm with `df -h /`". Reply paragraph: "`df -h /` before and after with space reclaimed". Upstream's "after" is kept unhardened: the Outcome does not say whether it follows step 5 or step 6. |

Order dependencies stated under Constraints, with the reason for each:

- Step 1 records `df -h /` before anything is deleted, because the Reply reports it before and after. Reason: baseline. Step 1 captures the state that steps 5 and 6 change.
- The cross-check in step 2 and steps 3 and 4 follow the audit of step 1, because they work on the rows it prints. Reason: later work uses a result only the earlier one produces (bucket, `verify-recent-chat`, `wip:N`, `scratch:N`). Getting the pinned and active set from the user or sidebar uses no row and is not ordered after the audit, which step 1 says to background.
- Step 5 follows steps 2, 3, and 4, because it prunes only the set they confirm. Reason: upstream order words ("Verify usage before deleting", "get a decision first") and gate for the deletion in step 5 ("Prune the confirmed set").

State-changing or external effects the work can have, with the condition upstream states:

- `git worktree remove --force <path>` per path of the confirmed set (step 5). Irreversible for uncommitted work. Upstream conditions: the bucket is advice and the pinned set wins (step 2); usage verified before deleting (step 3); `wip:N` needs the diff shown and a decision first; "Per Autonomy, clean and merged and not-in-use proceeds. `wip` and in-use pause." (step 4).
- Dropping untracked files of a `scratch:N` worktree with its removal (step 4). Upstream condition: "safe to drop, but name the files".
- `rm -rf` of a worktree directory (step 5). Upstream condition: "If the dir survives on ignored build artifacts".
- `git worktree prune` (step 5). No separate approval stated.
- Simulator deletion: `xcrun simctl --set testing delete all`, `xcrun simctl delete unavailable`, `xcrun simctl runtime list` then `runtime delete <id>` for old runtimes (step 6). No approval or condition stated in the playbook.
- Clearing Xcode `DerivedData` and `iOS DeviceSupport`, `~/Library/Application Support/Cursor` (`state.vscdb.backup`, `snapshots/roots/<root>`), and package caches (pnpm, uv, brew, yarn) (step 6). These write outside the repository. Upstream conditions: "More when needed" and "Clear only caches the user has not said to keep."
- Running `scripts/worktree-audit.sh` (step 1). Upstream states no effect. Verified effects: a forced `git fetch origin` of the base branch that moves `refs/remotes/origin/<branch>`, an index refresh in each worktree, and one temporary file. The audit removes nothing.
- Spawning subagents to read transcripts (step 3). No external state change stated.

Also: 2 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-mode/references/tool-use-worktree-audit.md`

Added by the conversion. It has no upstream counterpart. Its statements were checked against the script it documents.
