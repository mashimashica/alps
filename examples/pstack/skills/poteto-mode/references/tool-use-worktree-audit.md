# Tool use for worktree-audit.sh

## Responsibility and limits

`scripts/worktree-audit.sh` audits the linked worktrees of one git repository. It prints one row per worktree with its disk size, the age of its HEAD commit, whether HEAD is merged into a base ref, its uncommitted work, its remote state, the PR of its branch, the date of the newest chat transcript that names its path, and a suggested bucket. The main worktree gets no row.

It removes no worktree, no branch, and no entry of the worktree registry. What it does change is listed under Effects on external state.

It has these limits.

- The bucket is computed from the other columns of the row by the rule under Returned information. The script does not read which chats are pinned or open.
- A worktree path that contains whitespace is cut at the first whitespace, and every column of its row is computed from the cut path. When nothing exists at the cut path, the row shows an empty SIZE, AGE `?`, MERGED `no`, DIRTY `clean`, and REMOTE `detached`, whatever the worktree holds. Otherwise the row describes whatever is at the cut path. A worktree whose directory is gone prints the same values as a cut path with nothing at it. When the path of the main worktree contains whitespace, a worktree whose cut path equals the cut main path gets no row.
- The worktree the caller stands in is listed like any other. A locked worktree is not marked.
- MERGED is an ancestor test, so a squash-merged branch reads `no` and a worktree with no commit of its own reads `YES`. In a worktree whose branch has no commit yet, the test uses the HEAD of the directory the script audits from (`repo-path`, or the top level of the current repository) and can read `YES`.
- Only the base ref is fetched. REMOTE is read from the local `refs/remotes/origin/<branch>` and is as fresh as the last fetch of that branch.
- The PR lookup returns only PRs that the authenticated user authored, at most 1000 of them. For a branch with several PRs it uses the first one listed.
- LAST_CHAT searches one directory, `$HOME/.cursor/projects/<slug>/agent-transcripts`, where `<slug>` is the path of the main worktree without its leading `/` and with every other `/` replaced by `-`. Transcripts stored anywhere else are not searched.
- A transcript counts only when it holds the worktree path followed directly by `/` or `"`. A path followed by a space, a line end, or an escaped quote (`\"`) does not count. The path is used as a regular expression, so `.`, `+`, `(`, and similar characters in a path can cause a miss or a false match. A transcript whose file name contains whitespace is not counted. Neither is one that ripgrep skips by default, such as a file in a hidden directory.
- The window for a recent chat, the limit of 1000 PRs, and the remote name `origin` are fixed in the script.

## Invocation

```
scripts/worktree-audit.sh [-b|--base <ref>] [repo-path]
```

The path is relative to the poteto-mode skill folder, not to the playbook file or the audited repository. The file is a bash script with the executable bit set. Run it directly or as `bash <path>`. A POSIX `sh` such as dash stops with a syntax error and exit status 2.

| Argument | Meaning |
| --- | --- |
| `-b <ref>`, `--base <ref>` | The ref that MERGED is tested against. A ref that starts with `origin/` is fetched before the test. |
| no `-b` | The base is the first of these that resolves to a commit. They are the target of `refs/remotes/origin/HEAD`, then `origin/main`, then `origin/master`. A warning on stderr names the one used. |
| `repo-path` | A directory inside the repository to audit or inside one of its worktrees. Without it the script audits the repository of the current directory. |
| `-h`, `--help` | Prints the usage text to stdout and exits with status 0. |

Options must come before `repo-path`. Arguments after `repo-path` are ignored without a message. `--` is rejected as an unknown option.

Four environment variables affect a run. `HOME` locates the transcripts directory and must be set. `PATH` decides whether `origin`, `gh`, `jq`, and `rg` are found. `TMPDIR` sets where the temporary file goes. `TZ` sets the day that LAST_CHAT shows.

The two header lines are printed at once. No row is printed until every worktree has been processed, because the rows are sorted at the end. A run in the background is finished when the process exits. Each worktree costs one `du` walk of its directory and one search of the whole transcripts directory.

## Returned information

Stdout holds two header lines and then one tab-separated row per linked worktree, largest SIZE first. The first line is `# base: <ref>` and names the base ref that was used. The second line names the columns in the order of this table.

| Column | Values | Meaning |
| --- | --- | --- |
| `SIZE` | a `du -sh` size such as `2.9M`, or empty | Disk use of the worktree directory, ignored and untracked files included. Empty when `du` prints nothing, as for a missing directory. A directory that is only partly readable shows a smaller size, with no sign. |
| `AGE` | `<n>d` or `?` | Whole days since the committer date of the HEAD commit. It is not the age of the worktree. |
| `MERGED` | `YES` or `no` | `YES` when HEAD is an ancestor of the base ref. A HEAD that could not be read gives `no`, except on a branch with no commit yet, as stated under Responsibility and limits. |
| `DIRTY` | `clean`, `wip:N`, `scratch:N` | Counted from `git status --porcelain`. `wip:N` means N entries that are not untracked. Untracked entries beside them are not counted. `scratch:N` means N untracked entries and no other change. An untracked directory is one entry. Ignored files are never counted. No file name is printed. |
| `REMOTE` | `detached`, `pushed`, `aheadN`, `no-remote` | `detached` means HEAD is on no branch. `pushed` means the local `origin/<branch>` equals HEAD. `aheadN` means the two differ, with N commits on HEAD that `origin/<branch>` lacks. N is 0 for a branch that is only behind. `no-remote` means there is no local `origin/<branch>`. |
| `PR` | `#<number>/<state>` or `-` | The first listed PR whose head branch is the branch of the worktree. A state from `gh` is lower-cased to `open`, `closed`, or `merged`. A state from the `origin` CLI is printed as returned. |
| `LAST_CHAT` | `YYYY-MM-DD` or `-` | The local date on which the newest matching transcript file was last modified. |
| `BUCKET` | `hold-wip`, `hold-open-pr`, `verify-recent-chat`, `safe`, `review` | The suggestion, by the rule below. |
| `WORKTREE` | a path | The path from `git worktree list --porcelain`, cut at the first whitespace. |

The bucket comes from the first row of this table whose condition holds.

| Order | Condition | Bucket |
| --- | --- | --- |
| 1 | DIRTY is `wip:N` | `hold-wip` |
| 2 | PR ends in `/open` or `/draft` | `hold-open-pr` |
| 3 | The newest matching transcript was modified less than 120 hours before the run | `verify-recent-chat` |
| 4 | MERGED is `YES`, or PR is anything other than `-` | `safe` |
| 5 | None of the above | `review` |

Row 4 makes `safe` cover a worktree whose PR was closed without a merge and a worktree whose PR state is spelled any other way than lower-case `open` or `draft`. `scratch:N` does not keep a worktree out of `safe`.

The script writes these messages to stderr. Other text on stderr comes from bash or from the tools it calls, such as the `cd` error for a `repo-path` that does not exist.

- `warn: no -b given; MERGED checks against <ref>`
- `warn: could not fetch <ref>; merged column may be stale`
- `error: <option> needs a ref` and `error: unknown option: <option>`
- `not in a git repo; pass a repo path` and `error: not a git repo: <path>`
- `error: no base ref (origin/HEAD, origin/main, origin/master all missing); pass -b <ref>`
- `error: base ref not found: <ref>`

## Dependencies and environment

| Dependency | Used for | When it is missing |
| --- | --- | --- |
| bash and git with worktree support | everything | The run fails. |
| `du` | SIZE | SIZE is empty in every row, with no message. |
| `jq` | PR | PR is `-` in every row, with no message. |
| `rg` (ripgrep) | LAST_CHAT | LAST_CHAT is `-` in every row, with no message. |
| the `origin` CLI or `gh`, signed in and with network access | PR | PR is `-` in every row, with no message. |
| a remote named `origin`, reachable with git credentials | the default base, the fetch of the base, REMOTE | Without `-b` and without any of the three default refs the run fails. When the fetch fails the run warns and tests MERGED against the local ref, or fails when there is none. |
| `HOME` | the transcripts directory | The run fails with exit status 1. |
| the directory `$HOME/.cursor/projects/<slug>/agent-transcripts` | LAST_CHAT | LAST_CHAT is `-` in every row, with no message. |

The script also uses `awk`, `sed`, `grep`, `head`, `sort`, `date`, `stat`, `xargs`, and `mktemp`. It picks GNU or BSD flags for `stat` and `date` by probing `stat -c %Y /`. It declares no versions.

The PR lookup tries `origin` first. It uses `gh` when `origin` is not on `PATH` or exits with an error. When `origin` succeeds with output that `jq` cannot parse, `gh` is not tried.

The behavior in this file was checked against the script and in runs on Linux with GNU tools. The BSD branch of the script was not run.

## Success, failure, and incomplete results

| Exit status | Meaning |
| --- | --- |
| 0 | The usage text was printed, or the table stage was reached. No failure in the fetch, the PR lookup, the transcript search, or the commands run per worktree changes this status. |
| 1 | No repository was found, `repo-path` could not be entered or is not a git repository, no default base ref exists, the base ref does not resolve, or `HOME` is unset. Nothing is written to stdout. |
| 2 | An option is unknown or `-b` has no value. Nothing is written to stdout. |

A failure ends with status 1 or 2 and a message on stderr. A success ends with status 0, both header lines, and the rows.

A run with status 0 can be incomplete. These cases show a sign.

- `warn: could not fetch <ref>; merged column may be stale` means MERGED was tested against the local copy of the base ref.
- `warn: no -b given; MERGED checks against <ref>` means the base was picked by default.
- A row with an empty SIZE and AGE `?` means nothing could be read at its path. Its `clean` and `detached` are not findings.

These cases show no sign.

- The PR lookup failed or could not run. PR is `-` in every row, and a worktree with an open PR is no longer `hold-open-pr`.
- The transcript search could not run. LAST_CHAT is `-` in every row, and a merged worktree in recent use becomes `safe`.
- A row was dropped because of whitespace in the path of the main worktree.
- A PR beyond the first 1000, or one authored under another identity, is missing from its row.

The output alone cannot tell a branch with no PR from a failed PR lookup, or a worktree with no chat from transcripts that were not searched. Telling them apart takes checks outside the script. They are whether `jq`, `rg`, and a signed-in `gh` or `origin` are available, whether the transcripts directory exists, and whether the number of rows equals the number of linked worktrees in `git worktree list`.

## Effects on external state

- When the base ref starts with `origin/`, which every default base does, the script runs `git fetch origin` for that one branch with a forced refspec. The fetch moves `refs/remotes/origin/<branch>` to the tip of the remote, creates it when it is absent, rewrites `FETCH_HEAD`, and adds the fetched objects. A base that does not start with `origin/` is not fetched.
- `git status` in each worktree can rewrite the index file of that worktree to refresh cached file data. No tracked file changes.
- One temporary file is created with `mktemp` and removed at the end of the run. It holds the PR numbers, states, and head branches. A run that is interrupted, or that stops because `HOME` is unset, can leave it behind.
- The PR lookup only reads from the forge.

The script keeps no state between runs and can be run again at any time, also after an interruption. Each run with an `origin/` base fetches it again.

## Reproducibility

The script uses no randomness. Two runs on unchanged inputs print the same bytes. The output changes with the current time (AGE and the recent-chat window), the state of the remote at fetch time, the PR states on the forge, the modification times of the transcripts, the local time zone (LAST_CHAT), the block accounting of the file system (SIZE), and the locale for the order of rows with equal SIZE.

## What a result does not establish

- Exit status 0 does not establish that the PR and LAST_CHAT columns were computed.
- `safe` does not establish that the worktree is unused, that its branch was merged, or that removing it loses nothing. It reflects only the columns of its row.
- A date in LAST_CHAT is the modification time of a transcript file. It does not establish that the chat is pinned, open, or ongoing.
- MERGED `no` does not establish that the branch is unmerged, and MERGED `YES` does not establish that work of the worktree was merged.
- `detached` does not establish whether any ref still holds the HEAD commit. Apart from the MERGED test against the base, the audit does not check it.
