# Conversion record: figure-it-out, show-me-your-work

[Conversion guide](../README.md)

## `skills/figure-it-out/SKILL.md`

Title: Figure it out. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Give a task that matches no playbook a workflow designed for it, and take the task through that workflow so that a human who stepped away can audit the decisions and trust the work.

| Outcome | Basis in the upstream text |
| --- | --- |
| Before the run starts, the definition of done is a falsifiable predicate, the scope is quantified, and the rigor level is set. | Phase A: "Ground first, then commit. Don't start the run until you can state:" with its three bullets ("The definition of done as a falsifiable predicate", "Scope, quantified: rough units and effort, plus the blockers grounding surfaced.", "The rigor level, biased high."). Written as a state of the framing rather than upstream's "can state", and it does not require that the framing was presented (fix round 1, W6). |
| The phase list written before any code scales rigor to the task, runs the scientific method, and leaves a decision trail a human can audit after stepping away. | Lead paragraph: "The deliverable before any code is the workflow itself: a sequence of phases that scales rigor to the task, runs the scientific method, and leaves a decision trail a human can audit after stepping away." Phase B: "Write the designed phase list down. That list is what the human reviews." Worded so the subject is the written list and its assessable properties, not its existence (fix round 1, W7). |
| Each unit that stays in the work advanced the predicate when measured on the real artifact. | Phase C: "State the hypothesis, make the smallest change, measure against the predicate on the real artifact, keep it if it advanced, revert it if it didn't." and "Verify by inspecting the artifact, never a self-report." |
| The decision trail has a row for each step of the design, written as the step landed. | Phase D: "Log the run via the **show-me-your-work** skill." Phase B closing paragraph: "weave the Phase D log through them, a row as each step lands, rather than saving the whole trail for the end." |
| The whole's standing against the Phase A predicate is established on the real product, not just the harness. | Phase E: "Check the whole against the Phase A predicate on the real product, not just the harness." Stated as the state of the evidence, not the performed check (fix round 1, W3). It does not require a VERIFIED whole, which upstream does not require. |
| The reply's account of what is verified against the predicate and what is still open hides no negative and counts no inconclusive result as a pass. | Reply: "what's verified against the predicate, and what's still open". Phase C: "A verdict is VERIFIED, NOT VERIFIED, or INCONCLUSIVE. Inconclusive is not a pass. Don't hide a negative." |
| Where a correction recurred, a gate, a lint rule, a check, or a script encodes it. | Phase E: "Encode any recurring correction as a gate, a lint rule, a check, or a script (the **encode-lessons-in-structure** principle skill)." Written as a conditional Outcome because upstream conditions it on a correction recurring. |

Carried from the frontmatter description into the body:

- "when no narrower one fits: a large migration, an ambitious multi-part change, or work a human reviews after stepping away" (description, first sentence). Carried into Constraints as its own sentence, "It applies when no narrower one fits: ...", after the body's own trigger ("This skill applies when the task matches no playbook."). The two triggers are separate sentences so neither narrows the other (fix round 1, F3). The slash name and the phrase 'figure it out' stay in the frontmatter only.

Order dependencies stated under Constraints, with the reason for each:

- The run does not start until the Phase A statements can be made. Reason: upstream order word, "Don't start the run until you can state:".
- The framing and tradeoffs are presented before committing to a long run. Reason: upstream order word, "Present the framing and tradeoffs before committing to a long run."
- The workflow is the deliverable before any code. Reason: upstream order word in the lead paragraph, "The deliverable before any code is the workflow itself".
- The verification harness is built before the work, with the baseline captured from the pre-change state. Reason: upstream order word and a baseline that the later work changes.
- The design is executed after it is designed. Phase C and Phase D apply to each of its steps as it runs. Reason: upstream "Then execute the design." and the sentences after it, which stay in Phase B step 2 with the todolist placement and the row-as-each-step-lands rule. This is also the Task that states an exception to listed order: Phase C and Phase D apply during execution. Shortened in fix round 1 (W8) so it does not restate the step.
- Each unit is verified before the next one starts. Reason: upstream order word, "verifying each unit before starting the next instead of batching checks at the end".
- Phase E follows the executed work. Reason: it checks the whole against the Phase A predicate, a result only the earlier work produces.

State-changing or external effects the work can have, with the condition upstream states:

- Committing to a long, multi-hour run. Condition upstream states: "Present the framing and tradeoffs before committing to a long run. Reversible work proceeds (the **never-block-on-the-human** principle skill), but a multi-hour run earns one checkpoint."
- Reverting a unit that did not advance the predicate ("revert it if it didn't"). No approval stated.
- Resetting a worker's work that gamed the gate ("reset and harden the contract"). No approval stated.
- Creating a worktree or branch per worker when work fans out ("give each worker its own worktree or branch"). No approval stated.
- Spawning subagents: workers, a judge for delegated work, and the **architect** skill (which runs **arena**) for one-way-door design decisions. Limits upstream states: "Parallelize only across seams", "Don't over-fan", reasoning level per the Subagents section of the **poteto-mode** skill, "Skip it for mechanical work whose shape is already concrete".
- Committing the decision trail so the reviewer can read it in the PR. Condition: upstream says figure-it-out's work is "usually ambitious enough"; the governing rule is in the **show-me-your-work** skill ("Commit it only when ...").
- The designed workflow's own steps may change external state. This file states no approvals for them beyond the checkpoint above and what the **poteto-mode** skill's Principles and Subagents sections supply.

Also: 3 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/show-me-your-work/SKILL.md`

Title: Show me your work. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Let a human who reviews long-running or unattended work after stepping away follow what was decided, why, on what evidence, and with what result, and see what needs attention.

| Outcome | Basis in the upstream text |
| --- | --- |
| Each decision point and checkpoint of the run that is not trivial or self-evident has a row in one canonical log, including each fork, pivot, or abandoned approach that shaped the work. | Lead: "Keep one canonical log." The format: "A single TSV file, one row per decision." Logging a row: "Log decision points and checkpoints, not every action: a fork chosen, a unit completed with its verification result, a pivot or revert with its trigger, a blocker surfaced, a gate fixed." Audit: "A fork, pivot, or abandoned approach that shaped the work but isn't logged is a gap. Add it." Qualified with upstream's "Skip the trivial and self-evident." so the Outcome does not raise the bar (fix round 1, F4). |
| Each row this run wrote records a real decision or action, with evidence that resolves and shows what the row claims, or a later row supersedes it with what actually happened and a pointer that resolves. | Audit: "Check that every row maps to a real decision or action.", "Check that each row's evidence resolves and shows what the row claims.", and "When a row records neither a real decision nor a real action, or its claim or evidence is wrong, add a row that supersedes it with what actually happened and a pointer that resolves." Scope from "This audit does not check rows outside this run's stretches." |
| No row of the log's history is edited or deleted. | Rules: "Append-only. A wrong call gets a new row that supersedes it. Never edit or delete history." Audit: "The audit never edits or removes a row, even an invented one." |
| Every reply for a run that produced a trail ends with an "Attention" section that names the reviewer's model and gives the flags of a subagent on another vendor's model than the one that did the work, each pointing to specific rows or moments, or "No flags". | Cross-model review of the trail: "Before handing back, spawn a subagent on another vendor's model than the one that did the work." and "Every reply for a run that produced a trail ends with an "Attention" section. Lead with the reviewer's model on its own line (`reviewed by <model>`), then list each flag pointing to specific rows or moments. "No flags" is a valid value." |

Carried from the frontmatter description into the body:

- "for long-running or unattended work" (description, first sentence) and "autonomous or multi-phase runs, or work a human reviews after stepping away" (description, "Use for" sentence). The upstream body states no applicability. Carried into Constraints as "This skill applies to long-running or unattended work, autonomous or multi-phase runs, or work a human reviews after stepping away." The slash name stays in the frontmatter only.

Order dependencies stated under Constraints, with the reason for each:

- A run that comes back to a log in a later turn first reads the log's last rows. Reason: upstream order word, "first reads the log's last rows to see whether another run wrote since".
- The audit of the log against the transcript comes at the end of the run, before handing back. Reason: upstream order words, "At the end of the run, before handing back, check the log told the truth."
- The cross-model review of the trail comes before handing back. Reason: upstream order word, "Before handing back, spawn a subagent ...".

State-changing or external effects the work can have, with the condition upstream states:

- Creating and appending to the log file (`decisions.tsv` in the work dir, or `.audit/<task-slug>.tsv` when several efforts run at once). Condition: append-only, "Never edit or delete history." By default the file is left out of git.
- Committing the log. Condition upstream states: "Commit it only when the work is ambitious enough that a reviewer needs the trail to trust the result."
- `scripts/log.sh` creates missing parent directories, the log file, the header line, and one row per call. It never rewrites existing content. Details in references/tool-use.md.
- Spawning a subagent on another vendor's model, which reads the audit trail and the run's transcript. Upstream states no approval and no limit on what is shared with that model. Reasoning level per the Subagents section of the **poteto-mode** skill.
- Reading this run's transcript. Limit upstream states: "Don't glob across `~/.cursor/projects/*/`. That reads unrelated private chats."

Also: 8 statements moved to the section their function calls for; 6 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/show-me-your-work/references/tool-use.md`

Added by the conversion. It has no upstream counterpart. Its statements were checked against the script it documents.

## `skills/show-me-your-work/scripts/log.sh`

Unchanged from upstream.

## `skills/show-me-your-work/references/decision-log-template.tsv`

Unchanged from upstream.
