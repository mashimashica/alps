# pstack in ALPS form

[Japanese translation](locales/ja/README.md)

This directory tree is the pstack Plugin with its work descriptions rewritten in ALPS form. It is an unofficial conversion, kept as reference material for the two ALPS design Skills. It is not affiliated with or endorsed by pstack's author.

The conversion changes how each piece of work is described. It does not change what the work is. An agent that follows a converted file is meant to do what an agent that follows the upstream file does. This guide states where that claim is supported, where it is not, and what the conversion found along the way. For the shortest account of what pstack asks of an agent, read [pstack as ten habits](habits.md).

## Source

| Item | Value |
| --- | --- |
| Plugin | pstack 0.15.44 |
| Repository | `https://github.com/cursor/plugins`, path `pstack/` |
| Commit | `e58dd043600587dbaf58ba315e7f2b38373eeb43` |
| License | MIT, Copyright (c) 2026 Lauren Tan. See [LICENSE](../../LICENSE). The ALPS modifications and additions in this tree are under the same license. |

The upstream files at the pinned commit are the baseline. To read the conversion as a diff, compare a checkout of the upstream repository at that commit with this tree: `git diff --no-index <upstream>/pstack examples/pstack`. The branch that added this tree first committed the upstream files unchanged, but a squash merge does not keep those commits.

## What changed and what did not

| Part of pstack | Count | Treatment |
| --- | --- | --- |
| Skill bodies (`SKILL.md`) | 58, plus 3 in the Benny automation pack | Rewritten as Process Descriptions |
| poteto-mode playbooks | 22 | Rewritten as Process Descriptions |
| The reviewing agent definition (`agents/comment-sicko.md`) | 1 | Rewritten as a Process Description of the review it performs |
| A Benny reference that prescribes work (`verify-existing-fix.md`) | 1 | Rewritten as a Process Description |
| Tool-use references for the bundled tools | 4 | Added. No upstream counterpart |
| Frontmatter of every Skill and agent | 63 | Unchanged, host fields included |
| Scripts, lockfiles, data, templates | all | Unchanged |
| `skills/poteto-mode/worker.md`, `agents/poteto-agent.md`, `docs/harness/claude-code.md` | 3 | Unchanged |
| Knowledge references, prompt templates, the Benny `FOR_AGENTS.md` | all | Unchanged |
| `README.md`, `docs/guide/` | 12 | Unchanged, except that six image links in the guide point to the files at the pinned commit |
| Plugin manifests | 2 | Description, homepage, repository, and author state that this is a conversion, and the version carries an `alps` suffix. The logo reference is removed |

Not in the tree: the guide's images, `assets/`, and the statechart tool's `scripts/test/` directory with its corpus.

Across the 85 rewritten files, the body text, frontmatter excluded, grew from about 40,900 words to about 59,500. The growth is mostly the derived Purposes and Outcomes, the section headings and their lead sentences, the statements of order, and the rules carried from the descriptions.

## How pstack maps to ALPS

The conversion followed one order of precedence: preserve the meaning of the upstream work, then meet the Process Framework's requirements, then follow the conventions of the [conversion profile](profile.md), then keep the file short. Where the first two could not both be met, the upstream meaning was kept and the gap was recorded. The table summarizes the profile.

| In pstack | In ALPS form | Reason |
| --- | --- | --- |
| The title of a Skill or playbook | Name, unchanged. Three Skills without a title were given one | Operators and other files already use it |
| Why the work is done, left unstated | Purpose, derived by the conversion | The Framework requires it |
| What counts as done, mostly left unstated | Outcomes, derived by the conversion, each with a recorded basis in the upstream text | The Framework requires observable result conditions |
| Numbered steps and lettered phases | Tasks and Activities with the same numbers, letters, and headings | Other files cite them by number and name |
| Unnumbered lists of actions | Numbered Tasks, with a sentence saying that the numbers set no order | Tasks need identifiers, and a number the conversion adds must not create an order |
| Order implied by numbering | Where upstream numbers or letters a sequence, a statement under Constraints: the listed order as the default, plus each dependency the work needs. Elsewhere, only the dependencies upstream states | Document order must not be read as execution order |
| "**Reply:** ..." and report formats | Outputs | A reply is an information item. Its existence is not success |
| "You own this task. Plan, review, verify." | Constraints | It allocates responsibility between the lead and its delegates |
| Rubrics, keep lists, tests, style rules | Controls | They direct the work or supply the basis for judging it |
| Prohibitions, approvals, limits on agents and models | Constraints | They limit permitted execution |
| The 24 principle Skills | A Process Description of applying the principle. The trigger is its first Constraint. One sentence is added after it: a citing description's own limits on the principle hold | Other descriptions cite the same file as a criterion, and some already limit or invert it |
| The six named sections of poteto-mode | Kept whole under the element of their main function | About twenty files cite them by name |
| Host identifiers such as `Task`, `subagent_type`, model slugs, rule paths | Unchanged, in the statement where upstream put them | The Claude Code adapter and upstream's generator match them literally |
| Citations such as "Phase A steps 3 and 4 of the **arena** skill" | Unchanged | Their targets keep their names |
| Rules that only the frontmatter description states | Carried into the body as well | The body is the Process Description |
| Persona narration in the reviewing agent | Each rule stated once in plain words. The persona and the exact first output line are kept as stated requirements | A rule must not live only in a figure of speech |
| Bundled scripts | Unchanged, with a tool-use reference beside each | The design principles require a tool's interface to be available to its users |

The conversion did not port pstack to another host, did not replace host identifiers with general terms, and did not repair anything it found unclear. The one exception is the sentence added to each principle.

## What the conversion made explicit

| Item | Count |
| --- | --- |
| Purposes derived | 85 |
| Outcomes derived, each with its basis recorded | 421 |
| Order dependencies stated under Constraints | 254 |
| State-changing or external effects listed with the condition upstream states | 277 |
| Description-only rules carried into a body | 78 |

The [conversion records](records/) list these per file.

Every Purpose and Outcome was selected or written by the conversion. Some Purposes repeat an upstream lead sentence word for word, but the upstream author did not designate any sentence as a Purpose or an Outcome and has not confirmed them. Where a derived statement and an upstream statement in the same file disagree, the upstream statement governs and the disagreement is a defect of the conversion.

## How pstack is built

These facts come from reading the whole Plugin and the upstream repository's scripts.

- **One router.** `poteto-mode` matches a task to one of 22 playbooks, copies the playbook's steps into a todo list, and routes to other Skills as steps fire. It holds an index of the 24 principle Skills.
- **Skills load only when typed.** 57 of the 58 Skills and all three Benny Skills carry `disable-model-invocation: true`. Only `setup-pstack` can load from the user's words. Because of this, the operator's rules reach a delegated agent only through `poteto-mode` and through `worker.md`, which every kickoff names in its first line.
- **Files address each other by structure.** Nineteen files cite "the Subagents section" of poteto-mode. Others cite arena's phases by letter and playbook steps by number. `unslop` numbers its rules as stable ids for other Skills to cite, although no file at this commit cites one. No upstream script checks these citations.
- **Model choice is shared information.** `setup-pstack` writes one rule file with nine role lines. `poteto-mode`, `arena`, `swarm`, `interrogate`, and five playbooks read it by label.
- **One source, two hosts.** Cursor installs the Plugin folder as it is. For Claude Code, an upstream script generates a second tree that copies the files and inserts one line into 22 Skills pointing to an adapter document. The adapter maps Cursor names to Claude Code at run time. The script finds the Skills that need the line by matching exact words in their text.
- **Four bundled tools.** Two are TypeScript command-line tools with test suites (`watch-pr`, the statechart tool). Two are shell scripts without tests (`worktree-audit.sh`, `log.sh`).

## What the conversion observed in the source

Writing a Purpose and Outcomes for a file forces two questions: what is this work for, and how would anyone tell it succeeded. Where the upstream text did not answer, or answered in two ways, the conversion kept the text as it was and recorded an observation.

The converters recorded observations as they worked, and 738 were screened. A second reader checked each one against the upstream file and kept only those that concern the upstream text and not the conversion, are not duplicates, are true of the text, are material to what an agent does or how success is judged, and are supported by quoted words. 173 remain. They are listed in [observations about the source text](findings.md) with their evidence.

| Kind of observation | Count |
| --- | --- |
| A statement can be read two ways | 65 |
| Two places state the same rule differently | 44 |
| A state-changing action lacks a stated condition | 18 |
| Success is stated as an artifact or a step | 12 |
| The tool behaves differently from the text | 11 |
| The work depends on something that is not bundled | 11 |
| An order is implied or in conflict | 7 |
| Other (a citation that does not resolve, shared information, an unstated objective) | 5 |

Examples:

- **Two lists of what needs confirmation.** `poteto-mode` lets team-chat messages and ticket updates proceed without asking. The principle Skill it indexes, `principle-never-block-on-the-human`, lists "send external messages" among actions that require confirmation.
- **A log format with two owners.** The Hillclimb playbook prescribes a nine-column `decision.tsv` and routes it through `show-me-your-work`, which fixes six columns, names the log `decisions.tsv` or `.audit/<task-slug>.tsv`, and bundles a helper that writes exactly six cells per row.
- **A trigger that other playbooks contradict.** Opening a PR begins "Invoked at the end of every other playbook." Investigation ends with no PR, and Multi-phase plan stops at handing back a plan.
- **Routing that depends on which file is read.** `poteto-mode` routes large or unattended work to `figure-it-out`. It also lists an Autonomous run playbook, which the README describes as one to "drive a long task to completion without stopping". `figure-it-out` itself begins "When the task matches no playbook, design one."
- **An end state that is never defined.** Babysit's `drive` mode "loops to merge-ready". The text does not define merge-ready, and the watcher it names reports `READY` while a required approval is still missing.
- **A guarantee that does not hold for one case.** Worktree cleanup says "Branch refs survive, so no commits are lost". The audit it runs also lists worktrees on a detached HEAD, where commits made in the worktree may be held by no branch.

These are readings of a text. The author may intend some of them, and an agent may settle others from context.

## The bundled tools

The scripts are unchanged. Each tool-use reference states what the tool does, how to invoke it, what it returns, how success, failure, and an incomplete result differ, what it changes, and what a result does not establish. The statements were checked against the script sources and against trial runs in throwaway directories.

| Tool | Reference | Facts the upstream text leaves out or states differently |
| --- | --- | --- |
| `watch-pr` | [tool use](../../skills/poteto-mode/references/tool-use-watch-pr.md) | Exit codes 0, 1, 2 to 7, and 64. `READY` does not mean approved or mergeable. An open PR without checks never reaches `READY`. `COMPLETE` counts a PR merged into its parent branch. The first run installs dependencies into the Skill folder. |
| `worktree-audit.sh` | [tool use](../../skills/poteto-mode/references/tool-use-worktree-audit.md) | It fetches the base ref, so it is not read-only. It exits 0 when the PR listing or the transcript search silently fails. It reads transcripts only from Cursor's location. The `safe` bucket is wider than the playbook's "clean and merged and not-in-use". |
| `log.sh` | [tool use](../../skills/show-me-your-work/references/tool-use.md) | It takes exactly six arguments: the log path and five cell values. It stamps the first cell, `ts`, itself. It never checks an existing header, so it appends a six-column row under a different header. |
| statechart | [tool use](../../skills/statechart/references/tool-use.md) | Exit 1 means a rule broke and the output was written. Exit 2 means nothing was written. `mise` must already be installed, or `TLA2TOOLS` must be set. Exit 0 does not mean the chart is complete. |

Where a tool behaves differently from what a playbook says, the playbook keeps the upstream sentence and the reference states the behavior. The difference is listed among the observations.

## Evidence and limits

The six kinds of evidence are kept apart. A pass in one does not establish another.

| Kind | What was done | Result | What it does not show |
| --- | --- | --- | --- |
| Format | The repository's form test for this tree. The Agent Skills reference validator on each Skill, as shipped and on a copy without the four host fields. | The form test passes. As shipped, 1 of 61 Skills passes the validator, the same as upstream. Without the host fields, 61 of 61 pass. | That a description is a valid account of its work. |
| Repository | Unit tests, link containment, whitespace. Upstream's own `check-pstack-docs.mjs`, run with this tree in place of `pstack/` inside a copy of the upstream repository at the pinned commit, because the check also reads the sibling Plugin `cursor-team-kit`. Upstream's `generate-pstack-harness-trees.mjs`, run against this tree. A per-Skill comparison of the Cursor terms upstream's generator looks for. A screen for upstream code spans, numbers, labels, and quoted strings that no longer occur. | Tests pass. The whitespace check passes with the unchanged upstream `README.md` exempted in `.gitattributes`, because three of its lines end in a space. The upstream documentation check reports 0 problems. The generator builds the Claude Code tree and inserts its adapter line into the same 22 Skills. The Cursor-term sets are the same in every Skill and playbook. The token screen leaves 7 items: five labels that became headings or notes, and two lead sentences that became Purposes. | Meaning. |
| Semantic review | For each of 29 units, one review for fidelity to the upstream text and one against the Process Framework, by agents that did not convert the unit. A reviser applied or rejected each finding. Ten units with the widest reach had a further independent verification. | The reviews raised 449 findings: 3 rated blocking, 139 major, 307 minor. Most concerned text the conversion derived or added: an Outcome that asked for more or less than the upstream instructions establish, or that could not hold on a path upstream allows, and Task numbers that implied an order upstream does not state. Several reported an upstream instruction that the first pass had moved out of its place or weakened. One is `bro`'s "Stop using jargon and speak coherently", which had survived only as a narrower Outcome. These were restored, or recorded where the reviser judged the force kept. Of the 449 findings, 433 were applied: 76 of them in a form different from the one suggested, and at least 40 by changing only the record. 15 minor ones were rejected with reasons. One minor finding has no recorded disposition, although the file now contains the change it asked for. Verification confirmed all but one of the fixes in its ten units. That fix, in `arena`, had introduced a new major gap. Verification raised 2 major and 12 minor items in all. Both major items and five minor ones were then fixed. Seven remain: four notes on the records, two Purposes in the Benny pack that do not cover one of their Outcomes, and one `statechart` Outcome that joins four hand-off items. | That the derived Purposes and Outcomes are what the author intends. |
| Tools | Upstream test suites, run in the upstream clone. Trial runs of the two untested shell scripts. Each reference statement checked against the source. | `watch-pr`: 54 of 54 tests pass. statechart: 373 of 373 with TLC available. Without it the suite reports 340 tests, of which 270 pass and 70 are skipped. | Behavior against live GitHub, Origin, or a `mise` installation. The statechart tests are not in this tree. |
| Requirements respected | The fidelity review compared every prohibition, approval condition, and limit with its upstream statement. | The first pass had narrowed the reach of several prohibitions by moving them out of the place upstream states them. The reviews found these and the fixes restored them, except in Babysit. There the prohibitions and the blocker order stay under Constraints, outside the Tasks an agent copies into its todo list, and the record notes the change. Verification found no other case remaining in its ten units. In the other nineteen units this rests on the reviser's own check. | Whether pstack's own rules are the right ones. |
| Effectiveness | Paired trials. The same task was run under the upstream text and under the converted text, and a judge who was not told which run used which text scored each run against the upstream instructions and the derived Outcomes. | See the table below. | Behavior in Cursor, with other models, or on other tasks. |

### Trials

The trials ran in Claude Code with Claude Opus as the working agent and as the judge. The converted arm used the Claude Code tree that upstream's generator builds from this tree. The upstream arm used upstream's committed Claude Code tree. No tool for starting subagents was available to the working agents.

| Task | Text the agent followed | Runs per text | Upstream instructions followed (converted, upstream) | Derived Outcomes met (converted, upstream) |
| --- | --- | --- | --- | --- |
| Fix a seeded bug test-first | `tdd` | 2 | 30 of 30, 30 of 30 | 10 of 10, 10 of 10 |
| Debug a crash that surfaces far from its cause | `principle-fix-root-causes` | 2 | 18 of 20, 18 of 20 | 8 of 8, 8 of 8 |
| Deepen a prompt without doing the task | `sharpen` | 2 | 20 of 20, 20 of 20 | 8 of 8, 8 of 8 |
| Restate a jargon-heavy message | `bro` | 8 | 41 of 48, 42 of 48 | 25 of 32, 26 of 32 |
| Review the comments in one file | `agents/comment-sicko.md` | 6 | 130 of 132, 128 of 132 | 28 of 30, 26 of 30 |
| Explain a number from the git record | `why` | 2 | 16 of 16, 16 of 16 | 8 of 8, 8 of 8 |
| Answer a read-only question about a codebase | `poteto-mode` and its Investigation playbook | 2 | 31 of 38, 31 of 38 | 5 of 8, 6 of 8 |

The task itself succeeded in every run under both texts, except in one comment review under each text.

What the trials show, and their limits:

- **No scenario separated the two texts.** Runs of the same text differed from each other as much as runs of different texts did.
- **`bro`.** In the first four runs, one converted run was scored as not concise. Twelve further runs did not repeat the difference: replies averaged 144 words under the converted text and 142 under the upstream text, against a 76-word message. The judge of those twelve counted every reply, under both texts, as longer than the message it restated.
- **The reviewing agent.** This is the one file whose persona narration was rewritten as plain rules, so it was given a second batch of runs: six per text in all. All twelve runs began with the required first line, left the code unchanged, kept the license header, the public API comment, and `prettier-ignore`, and deleted the `IMPORTANT` comment and both suppressions. The one comment whose keep clause could not be proven from the code was deleted in 3 of 6 converted runs and 4 of 6 upstream runs. The two judges ruled in opposite ways on keeping it. The judge of the first four runs counted keeping it as compliant. The judge of the later eight held that keeping it broke the rule for doubt, and counted one run under each text as failed, the upstream one also for a missing `MUST KILL` flag. The totals in the table add up both rulings. Under the second ruling alone, three converted runs and two upstream runs would fail, and the converted text's lead in the table would disappear.
- **`poteto-mode`.** Three instructions could not be decided from a reply: whether the principle files were read, whether the playbook's steps were copied into a todo list, and whether `unslop` was loaded. They count as not followed under both texts.
- **Limits.** Two to eight runs per text, one model, one host, small fixtures, no subagents. The judge knew which text was the original but not which run followed which text, and it is the same model as the working agents. These trials support the judgment that the eight converted files used in these seven tasks behave like their originals on these tasks. They are not evidence about the other 77 converted files.

### What was not established

- Whether the derived Purposes and Outcomes state the author's intent. Only the author can confirm that.
- Behavior in Cursor: the `Task` tool, cloud agents, `/loop`, the named model slugs, Bugbot, and Automations were not available.
- Behavior of the Skills that fan work out to subagents (`arena`, `swarm`, `interrogate`, most playbooks). Their conversion rests on review, not on trials.
- Behavior of the Benny automation pack, which runs only on Cursor Automations.
- Whether longer, sectioned descriptions cost more context than they return. Body text grew by about 45 percent.
- Japanese counterparts of the converted Skills. Only this guide and the ten habits are translated.

## Effects of the conversion that an operator should know

- **Skills that copy poteto-mode's shape.** `automate-me` drafts a personal mode and says "The **poteto-mode** skill shows the shape". The modes it drafts from this tree will follow the converted shape.
- **Frontmatter.** The host fields stay at the top level, because the hosts read them there. A strict Agent Skills validator rejects them, as it does for upstream.
- **Babysit's todo list.** Upstream Babysit has no numbered steps. The converted file numbers its actions as Tasks and keeps "Never rebase, retarget, or force-push", "Babysitting never authorizes merging", and the blocker order under Constraints. A todo list copied from the Tasks carries the actions only.
- **The name and version.** The manifests keep the name `pstack` so that the adapter's `pstack:` prefixes stay valid. Their version is `0.15.44-alps.1`: the source version with a suffix that marks the tree as derived. Do not install this tree beside upstream pstack.

## Design observations that the conversion did not apply

These go beyond a change of presentation. They are proposals, and the converted text does not carry them out.

- **Separate the host binding from the work.** The descriptions name host tools inside their steps, and the Claude Code adapter depends on those exact words. Stating each capability the work needs once, and binding it to a host in one place, would let one description serve both hosts. It would also require changing the adapter and upstream's generator.
- **Say how a cited principle may be adapted.** The principle Skills are used as shared criteria. Playbooks already limit or invert them in places. The sentence the conversion added to each principle says only that a citing description's own limits hold. A fuller statement of permitted exceptions belongs to the author.
- **Give shared information one owner.** The model rule file and the decision log are each read by several files. Naming the writer, the readers, and what a change invalidates in one place would remove the two-owner cases listed above.
- **Define the end state of long-running playbooks.** Several playbooks end at a state the tools do not report. An Outcome the watcher's output can decide would close that gap.

## Using this tree

The tree is reference material. To try it:

- **Cursor.** The tree keeps upstream's Plugin layout, so it can stand in for the upstream folder. This was not tried in Cursor.
- **Claude Code.** Generate the Claude Code tree with upstream's script. Put `scripts/generate-pstack-harness-trees.mjs` from the upstream repository at the pinned commit in a `scripts/` folder beside a copy of this tree named `pstack/`, then run `node scripts/generate-pstack-harness-trees.mjs` from the folder that holds both. The result is under `harness/pstack/claude-code/`. The trials above used a tree built this way.

## Records

- [pstack as ten habits](habits.md): the same way of working compressed to ten habits, with the principles and Skills each one covers.
- [Conversion profile](profile.md): the conventions the conversion followed. The records cite its sections by number. English only.
- [Conversion records](records/): for each converted file, the derived Purpose, each derived Outcome with its basis in the upstream text, rules carried from the description, headings that changed, order dependencies, and state-changing effects. English only.
- [Observations about the source text](findings.md). English only.
