# watch-pr tool use

`scripts/watch-pr/watch-pr` reads the state of GitHub pull requests through `gh` and reduces it to one typed verdict. The path is relative to the poteto-mode skill folder.

## Responsibility and limits

The watcher observes and classifies. It changes nothing on GitHub. It never merges, comments, resolves a thread, reruns a check, rebases, retargets, or pushes.

It is one command with no subcommands. Flags select the behavior.

| Behavior | Selected by | Terminal verdicts |
| --- | --- | --- |
| One status read | `--status-only`, with any scope flag | `STATUS`. When GitHub cannot be read, `BLOCKER` (`status-query`) or `TIMEOUT`. |
| Watch one PR | default | `READY`, `BLOCKER`, `TIMEOUT` |
| Watch a connected open stack | `--stack` | `READY`, `BLOCKER`, `TIMEOUT` |
| Watch a fixed queue until every PR in it is merged | `--queued-stack` | `COMPLETE`, `BLOCKER`, `TIMEOUT` |

A watch classifies each PR that is not merged in this fixed order. The first match wins.

1. Merge conflict. `mergeable` is `CONFLICTING`, or `mergeStateStatus` is `DIRTY` or `CONFLICTING`.
2. Any unresolved review thread.
3. A failed check, or `mergeStateStatus` `BLOCKED` while the head commit's status rollup is `ERROR` or `FAILURE`.
4. Merge gate. The PR is closed without merge, is a draft, or has `reviewDecision` `CHANGES_REQUESTED`. A draft whose checks are still pending waits instead. `--allow-draft` removes the draft gate.
5. Pending checks. The watcher waits.
6. Otherwise the PR is ready.

With `--stack` and `--queued-stack`, each of the first three tiers is checked across every PR before the next tier, then the merge gate, then pending checks. A conflict on an upper PR outranks a failed check on the lowest one. A terminal `BLOCKER` names the first blocker only.

- **Checks.** Every reported check counts, required or not. A cancelled check counts as failed. A check named exactly `Code Review Gate` that is pending or `ACTION_REQUIRED` counts as neither pending nor failed. An open PR with no checks at all cannot be read. The run ends with exit 7, or with exit 5 when a deadline passes first.
- **Review threads.** Only unresolved threads are returned, each with its GraphQL thread `id` and its first comment. Later comments of a thread are dropped. REST comment ids, PR-level comments, and review summaries are not read. An unresolved thread on outdated code still counts.
- **Stack discovery** (`--stack`, and `--queued-stack` without `--stack-prs`). The watcher lists up to 300 open PRs once at start and never refreshes the list. A PR's parent is the open PR in the same repository whose head branch is its base. The stack is the seed PR, its chain of parents, and every descendant of the seed. A seed that is not in the list, because it is merged, closed, or beyond the 300, yields a stack of the seed alone.
- **Host.** Inference of the repository accepts only `github.com` remotes and PR URLs.
- **Time.** There is no deadline unless `--timeout` is set, and no timeout on a single `gh` call. A hung `gh` hangs the watcher.
- **History.** `hadPreviousPassingCi` and the head rollup are read from the PR's last 50 commits.
- **State.** Nothing is kept between runs.

## Invocation

```
scripts/watch-pr/watch-pr [options]
```

The launcher is an executable Bun script. It takes no positional arguments. Run it from inside the target repository's checkout when the PR or the repository is left to inference.

| Option | Value | Default | Meaning |
| --- | --- | --- | --- |
| `--owner <owner>` | text | inferred | Repository owner. |
| `--repo <repo>` | text | inferred | Repository name. |
| `--pr <number>` | positive integer, `#` prefix allowed | inferred | The PR to watch. With `--stack` it is the seed of discovery. With `--stack-prs` it only helps resolve the repository. |
| `--stack` | flag | off | Watch the connected open stack. Cannot be combined with `--queued-stack`. |
| `--queued-stack` | flag | off | Watch the captured queue until every PR in it is merged. |
| `--stack-prs <n,...>` | comma list of PR numbers, bottom to top, no duplicates | none | The queue, used as given. Order and membership are not checked against GitHub. Rejected without `--queued-stack`. |
| `--interval <seconds>` | number above 0 | 60 | Sleep between polls. Also the base of the retry backoff. |
| `--sweep-interval <seconds>` | number above 0 | 300 | Queued watch only. How often every unmerged PR of the queue is read again. Between sweeps only the lowest unmerged PR is polled. |
| `--timeout <seconds>` | number, 0 or more | 0, no deadline | Deadline measured from start. |
| `--max-query-errors <count>` | positive integer | 5 | The count of consecutive read failures at which the run ends with exit 7. |
| `--status-only` | flag | off | Emit one terminal `STATUS` verdict and apply no classification. |
| `--allow-draft` | flag | off | Do not treat a draft as a merge gate. |
| `--pretty` | flag | off | Human text in place of JSON. |
| `-h`, `--help` | flag | | Usage text on stdout, exit 0, no call to `gh`. |

The PR and the repository are resolved in this order.

1. With `--owner`, `--repo`, and `--pr` all given, they are used as they are.
2. With `--pr` but not both of the others, the watcher runs `git remote get-url origin`. If that is a `github.com` remote, the missing parts come from it.
3. Otherwise it runs `gh pr view [<pr>] --json number,url` in the working directory, which names the current branch's PR when no number is given. Owner, repository, and number come from the returned URL. Explicit `--owner` and `--repo` still win.
4. With `--stack-prs` and no `--pr`, the first listed number takes the place of `--pr` in steps 1 to 3.

`--status-only` covers one PR by default, the discovered stack with `--stack` or with `--queued-stack` alone, and exactly the listed PRs with `--queued-stack --stack-prs`.

## Returned information

Every verdict goes to stdout. The default is one compact JSON object per line, so a watch prints progress lines and then one terminal line. stderr carries only argument errors and crash output. stdin is not read.

Every JSON verdict begins with the same fields.

| Field | Meaning |
| --- | --- |
| `schemaVersion` | Always `1`. |
| `sequence` | Count of verdicts emitted by this process, from 1. |
| `observedAt` | Wall-clock time of the verdict, ISO 8601. |
| `mode` | `single`, `stack`, or `queued-stack`. |
| `kind` | The verdict kind, from the next table. |
| `terminal` | `true` on the last line of a run, `false` on progress lines. |
| `exitCode` | Present on the terminal line only. Equals the process exit status. |

| `kind` | Terminal | Carries | Emitted |
| --- | --- | --- | --- |
| `STATUS` | yes, with `reason` `status-only` | `rows` | By `--status-only`. |
| `STATUS` | no, with `reason` `poll` or `whole-stack-sweep` | `rows` | On every `--stack` poll and after every completed queued sweep. |
| `QUEUE` | no | `queue` | At the start of a queued watch. |
| `WAITING` | no | `frontier`, and `reason` of kind `pending-checks` (with `pending`) or `merge-queue` (with `unmergedCount`) | On every waiting poll of a single or stack watch. In a queued watch, only when the frontier, the reason kind, or the reason's count (pending checks or unmerged PRs) changes. |
| `ADVANCE` | no | `merged`, `frontier`, `remaining` | In a queued watch, when the lowest unmerged PR merged and the next one became the frontier. |
| `RETRY` | no | `failure`, `consecutiveFailures`, `retryInSeconds` | When a read failed and will be tried again. |
| `READY` | yes | `scope` of kind `single` (with `pr`) or `stack` (with `prs`). Each entry is a `ready-pr` with `proof` or a `merged-pr`. | By a single or stack watch. |
| `COMPLETE` | yes | `queue`, and `merged` with `mergedAt` per PR | By a queued watch. |
| `BLOCKER` | yes | `blocker` | By every behavior. |
| `TIMEOUT` | yes | `reason` | By every behavior, when `--timeout` is set. |

Each entry of `rows` is one PR, in stack or queue order. A merged or closed row has `kind`, `context`, and `facts`. An open row adds `threads`, `ci`, and `reviewAutomationRunning`.

- `facts` holds the PR's `context`, `mergeable`, `mergeStateStatus`, `reviewDecision`, `headRefOid`, `headRefName`, `baseRefName`, `state`, `mergedAt`, and `isDraft`.
- `threads` holds the unresolved threads. Each has `id`, `firstComment` (`authorLogin`, `body`, `path`, `line`, `createdAt`), `isBugbot`, and `bugbotReviewPasses`.
- `ci` holds `kind` (`ci-clean`, `ci-pending`, `ci-failing`, `ci-github-rejected`), `source` (`gh-pr-checks` or `graphql-rollup`), `all`, `failed`, `pending`, `hadPreviousPassingCi`, and `github`, which is GitHub's merge assessment (`kind` `allowed` or `refused`) and is absent on `ci-pending`.
- Each check has `name`, `description`, `link`, `workflow`, `kind` (`passed`, `skipped`, `failed`, `pending`, `code-review-gate`), and `reportedState`.

Derived fields mean the following.

- `isBugbot` is true when the first comment's author login contains `bugbot`, or the author is `cursor` and the body contains `bugbot`, `cursor_automation_id`, `agentic security review`, `description start`, or `severity`, compared without regard to case.
- `bugbotReviewPasses` counts the distinct `RUN_ID:` or `CURSOR_AUTOMATION_ID:` values across the PR's Bugbot threads, resolved ones included. It is 1 when such threads exist and none carries an id. Every thread of the PR repeats the same number.
- `reviewAutomationRunning` is true when a pending check's name contains `bugbot`, `security review`, `pr review automation`, or `review automation`.
- `hadPreviousPassingCi` is true when a commit other than the head had a `SUCCESS` rollup. A queued watch does not look this up for a `ci-pending` row and reports `false` there.
- `ci-github-rejected` means no check that was read failed, yet GitHub reports `BLOCKED` with a failing head rollup.
- `source` `graphql-rollup` means `gh pr checks` returned nothing usable and the checks came from the GraphQL rollup. Its checks have empty `description` and `workflow`.

`--pretty` prints a `STATUS` verdict as a Markdown table with the columns PR, CI, Review, and Merge, and every other verdict as lines that begin with its kind. The table leaves out thread ids, check names, and the head SHA. A pretty `BLOCKER` ends with an `action=` line for a conflict, a merge gate, and a failed status query, and a pretty single-PR `READY` for a draft that `--allow-draft` let through adds a `note=` line. Those lines are fixed text in the tool. They take no account of what the calling playbook permits. JSON output has none of them.

Comment bodies, check names, and check descriptions come from GitHub. JSON carries them as string values. `--pretty` writes them into its lines unescaped.

## Dependencies and environment

- Bun on `PATH`. The launcher starts with `#!/usr/bin/env bun` and needs its executable bit. No Bun version is declared.
- `gh` on `PATH`, authenticated with read access to the repository's PRs, checks, review threads, and commit statuses. No version is declared or checked.
- `git` on `PATH`, used only for `git remote get-url origin` when `--pr` is given without both `--owner` and `--repo`.
- `commander` 14.0.0, which the launcher installs itself. See Effects on external state.
- Network access to GitHub on every poll.

The watcher reads no environment variables. `gh` and `git` inherit the environment, so `gh`'s own settings apply.

## Success, failure, and incomplete results

| Exit | Last stdout line | Meaning |
| --- | --- | --- |
| 0 | `READY` | Single or stack watch. Nothing in the classification order blocks. Also returned for a PR that is already merged, as a `merged-pr` entry. |
| 0 | `STATUS` with `reason` `status-only` | The status read worked. The PR's health is in `rows`. |
| 0 | `COMPLETE` | Queued watch. Every PR in the captured queue reads merged. |
| 0 | usage text | `--help`. |
| 2 | `BLOCKER` of kind `merge-conflicts` | Carries `pr` and `facts`, which name the head and base branches. |
| 3 | `BLOCKER` of kind `review-threads` | Carries `pr` and every unresolved thread. |
| 4 | `BLOCKER` of kind `failing-checks` | Carries `pr` and the full `ci` state. |
| 5 | `TIMEOUT` | The deadline passed while waiting. `reason` is of kind `pending-checks`, `status-unavailable`, or `queued-stack`. |
| 6 | `BLOCKER` of kind `merge-gate` | `reason` is `closed-without-merge`, `draft-pr`, or `changes-requested`. |
| 7 | `BLOCKER` of kind `status-query` | GitHub could not be read. Carries the count of `failures` and the last `failure`, whose `kind` is `command-exit`, `json-parse`, `missing-key`, `checks-unavailable`, or `invalid-context-url`, and whose `detail` gives the reason. |
| 64 | none | Usage error. The message is on stderr. |
| 1 | none, or text that is not JSON | Uncaught error, such as `gh` or `git` missing from `PATH`, or a failed dependency install. |

- **Processing succeeded** when the last stdout line has `terminal: true` and the exit status equals its `exitCode` and is 0, 2, 3, 4, 5, or 6. Exits 2 to 6 are successful observations of a PR that is blocked or undecided. They are not tool failures.
- **Processing failed** on exit 7, 64, or 1. After exit 7 nothing is known about the PR. Check the PR context, `gh` authentication, and the `failure` detail, then run again.
- **The result is incomplete** when the stream ends without a `terminal: true` line, because the watcher was killed, crashed, or is still running. Earlier lines remain valid observations as of their `observedAt` and nothing more.
- **Exit 5 is undecided.** `reason` holds the state at the deadline. Run again to keep waiting.

A failed read inside the poll loop emits `RETRY` and sleeps `min(max(interval, 60) * 2^(n-1), 300)` seconds, where `n` is the count of consecutive failures. At `--max-query-errors` consecutive failures the run ends with exit 7. With the defaults that is sleeps of 60, 120, 240, and 300 seconds and exit 7 on the fifth failure. A successful read resets the count. `--status-only` runs in the same loop, so a status read can take minutes and can end with exit 7 or, under `--timeout`, exit 5. A failure while resolving the PR or discovering the stack is not retried. It ends with exit 7 at once.

`--timeout` is checked only when the watcher is about to wait. A `READY` or `BLOCKER` observed after the deadline is still reported as such. A sleep never runs past the deadline, so `retryInSeconds` can exceed the real sleep.

A queued watch does not end when the lowest unmerged PR becomes ready to merge. It emits one `WAITING` line with a `merge-queue` reason and keeps polling until that PR reads merged, a blocker appears on any unmerged PR of the queue, or the deadline passes. The watcher merges nothing, so the merge has to come from elsewhere. With the default `--timeout 0` the wait has no bound.

## Effects on external state

- **GitHub.** None. Every `gh` call is a read (`pr view`, `pr list`, `pr checks`, or `api graphql` with a query).
- **Local files.** On the first run, and on any run after `scripts/package.json` or `scripts/bun.lock` changed or `scripts/node_modules/` went missing, the launcher runs `bun install --frozen-lockfile` in the skill's `scripts/` folder, writes `scripts/node_modules/` with an install key file inside it, and then runs the same command again. This needs write access to the skill folder and can need network access to the package registry. A failed install ends with exit 1 and the installer's output on stdout and stderr.

Because the watcher changes nothing on GitHub, any run can be repeated at any point, including after a kill or a crash. An interrupted install is redone on the next run. Nothing guards two first runs that start at the same time and install into the same folder.

A restart keeps no memory and resolves the PR and the stack again. A queued watch restarted without `--stack-prs` rediscovers its queue from the open PRs. Once the seed PR has merged it is missing from that list, the queue becomes the seed alone, and the watch reports `COMPLETE` while PRs above it are still unmerged. Restarted with the same `--stack-prs` list, the watch keeps its queue and reads the merged PRs as merged.

## Reproducibility

Classification is deterministic for the same GitHub responses, options, and clock. There is no randomness. Observations are not repeatable, because they depend on live GitHub state, on the installed `gh`, and on timing.

`commander` is pinned to 14.0.0 and installed from the frozen lockfile. Bun, `gh`, and `git` are not pinned. Every JSON verdict carries `schemaVersion: 1` and its `observedAt`.

A single or stack watch reads every PR again each `--interval`. A queued watch reads the lowest unmerged PR each `--interval` and the other unmerged PRs only each `--sweep-interval`, so their rows can be that old when a verdict is reached. Stack and queue membership is captured once at start.

## What a result does not establish

- `READY` does not mean approved and does not mean GitHub will accept a merge. A `reviewDecision` of `REVIEW_REQUIRED` or none, a `mergeStateStatus` of `BLOCKED` with a head rollup that is not failing, a `mergeStateStatus` of `BEHIND`, and a `mergeable` of `UNKNOWN` all still give `READY`. A stale base is never reported as a blocker.
- `READY` does not name the head it judged. `headRefOid` appears in `rows` and in a conflict blocker's `facts`, not in the `proof` of a `READY`. One PR is read with several `gh` calls in sequence, and nothing checks that the head stayed the same between them.
- `STATUS` with exit 0 says the read worked, not that the PR is healthy.
- A `BLOCKER` names one blocker. Other problems on the same PR or stack can exist. The `rows` of a `STATUS` verdict show the full state, including the threads of a PR that also has a conflict.
- `COMPLETE` means every PR in the captured queue reads merged, by `state` `MERGED` or a set `mergedAt`. The base branch is not checked, so a PR merged into its parent's branch counts. The captured queue is the `--stack-prs` list when one is given, and the whole discovered stack otherwise.
- No verdict says a change works or was verified. The watcher reads merge state, review threads, and checks, and nothing else.
