# Shipping

## Purpose

Land the contiguous verified run of a stack on trunk, and nothing that an independent verdict does not cover.

## Outcomes

- Every PR that landed has a `PASS` or `PASS+NOTES` verdict posted on it by an agent that did not write its code.
- Each of those verdicts covers the patch that landed, as step 3's patch-id rule decides.
- Where a landed patch differs from its verdict's only in tests, docs, or lint config, the change got fresh checks and a review.
- Every PR of the verified run, from the bottom to the ceiling, reads merged with trunk as its base.
- No PR above the ceiling landed, except one that was moved onto trunk on its own and got a fresh verdict first.
- While the run landed, the run changed no branch or base except by step 4's move of the next PR, and a base that moved to trunk when its parent merged was left as it was.

## Tasks

The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. **Resolve the forge, then verify each PR independently before it lands.** GitHub CLI (`gh`) is the default. If `command -v origin` succeeds and Origin can resolve the repository, use `origin pr` for every PR operation. Otherwise stay on `gh` and record the fallback. Never require Graphite (`gt`). One verifier per PR, each a Cursor cloud agent, runs the change the way a user would with the matching control skill (such as `control-ui` or `control-cli` from `cursor-team-kit`), parent against head, and posts `PASS`, `PASS+NOTES`, or `FAIL` on that PR. Only a verdict from an agent that did not write the code counts, because an author checks what it meant to build. Green CI and an approving bot review are not verdicts, because neither runs the change as a user would.
2. **Land only the contiguous verified run rooted at the bottom.** Walk up from the lowest unmerged PR and stop at the first one without `PASS` or `PASS+NOTES`. The PRs below it are the run, and the top one is the ceiling. A verified PR above an unverified one waits, because it cannot land without the code below it. One whose branch neither holds nor needs that code can move onto trunk and land on its own. It needs a fresh verdict first, because its old one ran with that code beneath it and trunk does not have it.
3. **Re-check that the verdicts still describe the code.** A verdict covers a patch, and a chain rebase moves every PR above it to a new SHA without failing any check. Compare `git patch-id` at the verdict SHA with the current head before trusting an older verdict. When the patches differ only in tests, docs, or lint config, a lane's result stands if what it ran builds the same at both SHAs apart from noise. Noise is a difference that also shows up between two builds of the verdict SHA, or an embedded commit SHA. Report each kind of noise with its files, so a reader can check the call. The change itself still gets fresh checks and a review, because the old verdict never saw it. A lane with no build output, such as a dev server, cannot show this, so rerun it, and re-verify anything else that drifted.
4. **Land bottom-up, one PR at a time.** Always merge the run's lowest unmerged PR, with `origin pr merge <pr>` or `gh pr merge <pr> --squash`. On Origin the plain command also merges every PR below the one you name, and on GitHub a PR whose base is still its parent's branch merges into that branch, not trunk. Read the PR back for the result (`origin pr view <pr>` or `gh pr view <pr> --json state,mergedAt,baseRefName`), because a merge command can report success when a merge queue only queued the PR, and a requested auto-merge is not a merge. A landed PR reads merged with trunk as its base, not its parent's branch. Arm `--auto` (Origin merge-when-ready or GitHub auto-merge) only on a PR whose verdict covers its current head, because it lands whatever head is ready. After a merge lands, retarget the PR whose base was the merged branch to trunk (`origin pr edit <pr> --base <trunk>` or `gh pr edit <pr> --base <trunk>`), move its patch onto the merge result, and push with `--force-with-lease`. The verdict covers the patch, not its commits, so step 3's patch-id rule decides whether the verdict survives. Merge it once its checks pass and its verdict survives.
5. **Leave the stack alone while it lands.** Step 4's move of the next PR is the only change to a branch or base, because a merge lands whatever its branch and base hold at that moment, verdict or not. On GitHub, watch the run with `scripts/watch-pr/watch-pr --queued-stack` under `/loop` until it reports `COMPLETE` at the ceiling. Pass the run's PR numbers, bottom-to-top, in `--stack-prs`, and pass the same list each time you restart the watcher. On Origin, re-read the current PR with `origin pr view <pr> --checks` each time `origin pr checks <pr> --watch` returns, until the ceiling reads merged. A base that moves to trunk when its parent merges is expected, not damage to repair. If a merge stalls, find out why before you change anything.
6. **Stop at the ceiling.** Extending the run takes new verdicts, so it is a new pass through step 1.

## Outputs

**Reply:** the verified run and its ceiling, each PR's verdict and who produced it, what landed and how you confirmed it, and what the next gap needs.

## Constraints

**You own what lands. Verify each PR independently, land only the verified run from the root, then keep your hands off the stack.**

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- A PR lands in step 4 only after step 1 has produced its verdict.
- Step 2 reads the run and its ceiling from step 1's verdicts.
- Step 3's re-check comes before step 4 trusts an older verdict.
- Step 5 holds while step 4 lands the run.
- Extending the run past the ceiling starts again at step 1.

## Enablers

`scripts/watch-pr/watch-pr` is bundled with this skill. Its invocation, results, exit statuses, dependencies, effects, and limits are in [tool use](../references/tool-use-watch-pr.md).
