# Conversion record: Playbooks: pull requests and landing

[Conversion guide](../README.md)

## `skills/poteto-mode/playbooks/opening-a-pr.md`

Title: Opening a PR. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Put the change up for review as a ready PR.

| Outcome | Basis in the upstream text |
| --- | --- |
| Every PR the run opens is open and ready, not a draft. | Paragraph 4: "Open PRs ready, through the run's PR tool with `draft: false`. Without one, use `gh pr create` without `--draft`, or `origin pr create --status open` when Origin's CLI resolves the repository." Plural as upstream ("Open PRs ready"), so stacked follow-ups are covered. |
| Each such PR's commits are small and landable. | Paragraph 2: "Rebase into small, landable commits." |
| The worktree each such PR comes from holds no unrelated work. | Paragraph 2: "Work from a git worktree off trunk, and keep unrelated work out of it." The Outcome is worded about the worktree, as upstream is, not about the PR's diff. |
| Each such PR's title follows the title format under Controls. | Paragraph 3: "Title: `type(scope): subject`, naming a real symbol when one carries the change." |
| Each such PR's body is a one-minute briefing that follows the body format under Controls. | Paragraph 3: "Body: a one-minute briefing under 40 lines with these `##` headings in order, dropping empty ones: ..." |
| Where there are follow-ups, they are stacked by base branch. | Paragraph 4: "Stack follow-ups by base branch." Conditional, because a change can have no follow-ups. |

State-changing or external effects the work can have, with the condition upstream states:

- Rewrites the branch's history ("Rebase into small, landable commits") and creates commits. Condition upstream states: None stated in this file. `/deslop` runs over the diff before commit.
- Opens a pull request on the forge through the run's PR tool, `gh pr create`, or `origin pr create --status open` (an external, visible action; pushing the branch is implied and not stated). Condition upstream states: None stated in this file. The PR is opened ready, not as a draft. poteto-mode's Autonomy section, a different file, lets external actions proceed without asking.

Also: 5 statements moved to the section their function calls for; 2 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-mode/playbooks/babysit.md`

Title: Babysit. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Clear what blocks the merge frontier, as far as the declared mode goes, and stop where the human's call begins.

| Outcome | Basis in the upstream text |
| --- | --- |
| The mode is declared in the first line, before any poll. | Bullet 1: "Declare the mode in your first line, before any poll." Lead line: "Declare a mode". |
| The run ended at merge-ready in `drive` mode and after one status pass and a report in `check` mode, or earlier where the human's call begins. | Bullet 1: "Modes: `drive` loops to merge-ready, ... `check` is one status pass and a report." Lead line: "stop where the human's call begins." Bullets 3 and 6 name such stops (a conflict or stale base, owner approval, merging). Upstream gives `threads-only` no end point, so none is stated for it. |
| Where the mode is `threads-only`, the run touched only review threads. | Bullet 1: "`threads-only` touches only review threads". Split from the end-point Outcome because it is a separate result judged on different evidence. |
| Where a PR has a conflict or a stale base, the run stopped there with a report that names the branch that needs the rebase and, for a conflict, the drift sweep. | Bullet 3: "Report a conflict or a stale base with the branch that needs the rebase, and stop." Bullet 4: "Say which branch needs the rebase and stop." and "Name the drift sweep in that report". |
| Where the run reaches review threads in `drive` or `threads-only` mode, each Bugbot finding was verified against the code, each billing, data, auth, or security finding was escalated, and each other finding was fixed as real or dismissed as noise with a concrete disproof. | Bullet 5: "Triage Bugbot skeptically: fix real findings, dismiss noise with a concrete disproof, escalate billing, data, auth, and security." and "Verify each claim against the code per `../references/bugbot-triage.md`." Conditional because a `check` run is one status pass and a report, and a conflict stops the run before threads (bullet 4). |
| Each reply about a fix cites the commit that was pushed before it. | Bullet 5: "Push that wave before replying so the reply cites the commit." |
| Every commit the run added for CI answers one of the diff's own failures. | Bullet 4: "Only the diff's own failures get a commit." (a guard restated as a result) |

Order dependencies stated under Constraints, with the reason for each:

- "Order: conflicts, threads, CI." Upstream's own order statement for the blockers, carried verbatim. Reason: upstream states it, and a conflict stops the run before threads or CI ("Do not fall through to CI to look busy").
- "Declaring the mode comes before any poll." Reason: upstream's order word in bullet 1 ("before any poll").

State-changing or external effects the work can have, with the condition upstream states:

- Pushes fix commits to the PR branch ("Push that wave", "Only the diff's own failures get a commit"). Condition upstream states: Only the diff's own failures get a commit. Never a force-push, rebase, or retarget. No human approval is stated.
- Posts replies on PR review threads (`gh api --method POST ".../comments/<comment-id>/replies"` or `origin pr thread reply`). Condition upstream states: After the fix wave is pushed, so the reply cites the commit. Never with shell built from comment text. The cited reference also resolves the thread.
- Starts one fresh CI build for a flake. Condition upstream states: "Flake earns one fresh build." One only.
- Escalates billing, data, auth, and security findings to the human. Condition upstream states: Stated as the required handling of those findings.
- Merging. Condition upstream states: Not permitted. "Owner approval is a wait. Babysitting never authorizes merging."
- Rebase, retarget, force-push. Condition upstream states: Prohibited ("Never rebase, retarget, or force-push"). A conflict or stale base is reported and the run stops. autopilot-full overrides this for an owner's own branch.
- First run of the bundled watcher installs its dependency into the skill's `scripts/node_modules/`. Condition upstream states: Not stated upstream. Documented in the tool-use reference.

Also: 12 statements moved to the section their function calls for; 3 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-mode/playbooks/shipping.md`

Title: Shipping. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Land the contiguous verified run of a stack on trunk, and nothing that an independent verdict does not cover.

| Outcome | Basis in the upstream text |
| --- | --- |
| Every PR that landed has a `PASS` or `PASS+NOTES` verdict posted on it by an agent that did not write its code. | Step 1: "posts `PASS`, `PASS+NOTES`, or `FAIL` on that PR. Only a verdict from an agent that did not write the code counts". Step 2: "stop at the first one without `PASS` or `PASS+NOTES`". |
| Each of those verdicts covers the patch that landed, as step 3's patch-id rule decides. | Step 3: "Re-check that the verdicts still describe the code. A verdict covers a patch ... Compare `git patch-id` at the verdict SHA with the current head before trusting an older verdict." Step 4: "Arm `--auto` ... only on a PR whose verdict covers its current head", "step 3's patch-id rule decides whether the verdict survives. Merge it once its checks pass and its verdict survives." |
| Where a landed patch differs from its verdict's only in tests, docs, or lint config, the change got fresh checks and a review. | Step 3: "When the patches differ only in tests, docs, or lint config, a lane's result stands if ... The change itself still gets fresh checks and a review, because the old verdict never saw it." |
| Every PR of the verified run, from the bottom to the ceiling, reads merged with trunk as its base. | Step 2: "Land only the contiguous verified run rooted at the bottom." Step 4: "A landed PR reads merged with trunk as its base, not its parent's branch." Step 5: "until it reports `COMPLETE` at the ceiling", "until the ceiling reads merged". |
| No PR above the ceiling landed, except one that was moved onto trunk on its own and got a fresh verdict first. | Step 2: "A verified PR above an unverified one waits ... One whose branch neither holds nor needs that code can move onto trunk and land on its own. It needs a fresh verdict first". Step 6: "Stop at the ceiling." |
| While the run landed, the run changed no branch or base except by step 4's move of the next PR, and a base that moved to trunk when its parent merged was left as it was. | Step 5: "Leave the stack alone while it lands. Step 4's move of the next PR is the only change to a branch or base" and "A base that moves to trunk when its parent merges is expected, not damage to repair." Lead line: "then keep your hands off the stack". The subject is the run, so an expected automatic base move does not fail the Outcome. |

Order dependencies stated under Constraints, with the reason for each:

- "A PR lands in step 4 only after step 1 has produced its verdict." Reason: step 1's title says "before it lands", and the verdict is the gate for the merge.
- "Step 2 reads the run and its ceiling from step 1's verdicts." Reason: step 2 uses a result only step 1 produces (`PASS` or `PASS+NOTES` per PR).
- "Step 3's re-check comes before step 4 trusts an older verdict." Reason: upstream's order word ("before trusting an older verdict"); step 4 merges and arms `--auto` only on a verdict that covers the current head.
- "Step 5 holds while step 4 lands the run." Reason: step 5 says "while it lands", so it is concurrent with step 4, not after it. This is the case "Unless a Task states otherwise" allows for.
- "Extending the run past the ceiling starts again at step 1." Reason: step 6, "Extending the run takes new verdicts, so it is a new pass through step 1."

State-changing or external effects the work can have, with the condition upstream states:

- Spawns one verifier per PR as a Cursor cloud agent, which runs the change and posts `PASS`, `PASS+NOTES`, or `FAIL` on the PR. Condition upstream states: The verifier is an agent that did not write the code. No human approval is stated.
- Merges PRs (`origin pr merge <pr>` or `gh pr merge <pr> --squash`). Irreversible on trunk. Condition upstream states: Only PRs in the contiguous verified run rooted at the bottom, each with `PASS` or `PASS+NOTES` from a non-author agent, the lowest unmerged PR first, after step 3's patch-id re-check, and once its checks pass and its verdict survives. No human approval is stated in this file. poteto-help says Babysit "doesn't merge unless the user asks to merge, land, or ship" and that "land the stack" runs Shipping, so the user's request is the only stated go.
- Arms `--auto` (Origin merge-when-ready or GitHub auto-merge). Condition upstream states: "only on a PR whose verdict covers its current head, because it lands whatever head is ready".
- Retargets the next PR to trunk (`origin pr edit <pr> --base <trunk>` or `gh pr edit <pr> --base <trunk>`), moves its patch onto the merge result, and pushes with `--force-with-lease`. Condition upstream states: Only after a merge lands, only for the PR whose base was the merged branch. It is "the only change to a branch or base" while the run lands. No human approval is stated here, while poteto-mode's Autonomy section pauses for a "force-push to shared branches".
- Moves a PR that neither holds nor needs the unverified code onto trunk so it can land on its own. Condition upstream states: "It needs a fresh verdict first".
- Reruns lanes and re-verifies drift (step 3). Condition upstream states: When the patch-id comparison or a lane without build output cannot carry the old result.
- First run of the bundled watcher installs its dependency into the skill's `scripts/node_modules/`. Condition upstream states: Not stated upstream. Documented in the tool-use reference.

Also: 2 statements moved to the section their function calls for; 3 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-mode/references/tool-use-watch-pr.md`

Added by the conversion. It has no upstream counterpart. Its statements were checked against the script it documents.

## `skills/poteto-mode/references/bugbot-triage.md`

Unchanged from upstream.
