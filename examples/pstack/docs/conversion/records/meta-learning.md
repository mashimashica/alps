# Conversion record: reflect, correct, automate-me

[Conversion guide](../README.md)

## `skills/reflect/SKILL.md`

Title: Reflect. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Route each durable learning in this conversation to a concrete edit on an existing skill, so that it changes what a future agent does.

| Outcome | Basis in the upstream text |
| --- | --- |
| The findings are drawn from the whole transcript. | Paragraph 2: "Read the whole transcript." |
| Each kept finding will still hold in six months, would change what a future agent does, and routes to a skill the session used. | Paragraph 3: "Keep a finding only if it will still hold in six months, would change what a future agent does, and routes to a skill the session used." |
| Kept findings hold nothing their skill already says clearly, no one-offs, and no details that drift. | Paragraph 3: "Read that skill first and drop what it already says clearly. Drop one-offs and details that drift, such as SHAs, versions and counts." Worded so that it covers a drifting detail or an already-stated point inside a kept finding, not only a whole finding. Outcomes 2 and 3 each keep upstream's keep test and drop test as one test, as paragraph 3 states them; their conditions are not split into separate Outcomes. |
| What a lint, script or check could enforce is in the backlog, not in prose. | Paragraph 3: "What a lint, script or check could enforce goes to the backlog, not into prose." |
| The presentation gives Accepted with a problem, a proposal and a skill for each item, Rejected with a reason for each item, and Backlog. | Paragraph 4: "Present Accepted (problem, proposal, skill), Rejected (reason) and Backlog". docs/guide/09-make-it-yours.md: "sorts the proposals into `Accepted`, `Rejected`, and `Backlog`". |
| Every skill edit follows the user's approval. | Paragraph 4: "wait for approval before editing any skill." Paragraph 5: "After approval, ... edit the copy." The approver is named by skills/poteto-help/SKILL.md line 154 ("skill edits the user approves") and docs/guide/09-make-it-yours.md ("It waits for your approval before any skill changes."). |
| Where the user approves an edit, the edit is made. | Opening sentence: "route each to an edit on an existing skill". Paragraph 4: "wait for approval before editing any skill", which presupposes the edit after approval. Paragraph 5: "After approval, copy the skill folder there and edit the copy." skills/poteto-help/SKILL.md line 154: "turns its lessons into skill edits the user approves". docs/guide/09-make-it-yours.md: "It waits for your approval before any skill changes." |
| A skill under `plugins/cache/` is edited only as a copy of its folder at the destination shown before approval. | Paragraph 5: "Never edit a skill under `plugins/cache/`. Before approval, show its destination, `.cursor/skills/<skill>/` or `~/.cursor/skills/<skill>/`. After approval, copy the skill folder there and edit the copy." |

Carried from the frontmatter description into the body:

- "route each to a concrete edit on an existing skill": the word "concrete". The upstream body says "an edit". It is carried in the Purpose ("a concrete edit on an existing skill"). "Use when the user says reflect." is a trigger and stays in the frontmatter only. "the active transcript" is the body's "this conversation" and "the whole transcript", so nothing was carried for it.

Order dependencies stated under Constraints, with the reason for each:

- Step 2 after step 1, and step 3 after step 2. Reason: step 2 keeps or drops the findings that step 1 produces, and step 3 presents the result (Accepted, Rejected, Backlog). Stated as "comes after" items. Otherwise the Tasks may be worked in any order, because upstream numbered none of them.
- Approval before any skill edit. Reason: upstream order word and approval gate, "wait for approval before editing any skill" (kept verbatim in step 3).
- In step 4, the destination is shown before approval and the copy and its edit come after approval. Reason: upstream order words "Before approval" and "After approval" (kept verbatim in step 4).
- Inside step 2, "Read that skill first and drop what it already says clearly." The order word stays in the step because it orders two parts of one step.

State-changing or external effects the work can have, with the condition upstream states:

- Editing a skill. Condition: approval first ("wait for approval before editing any skill").
- Copying a skill folder from `plugins/cache/` to `.cursor/skills/<skill>/` (in the project) or `~/.cursor/skills/<skill>/` (outside the repository) and editing the copy. Conditions: the destination is shown before approval, and the copy and the edit happen after approval.
- Editing a skill under `plugins/cache/`. Prohibited ("Never edit a skill under `plugins/cache/`.").
- Opening a PR or pushing. Prohibited ("Never open a PR or push.").

Also: 5 statements moved to the section their function calls for; 3 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/correct/SKILL.md`

Title: Correct. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Change this repo so the next agent can't make the same mistakes the operator keeps correcting agents for.

| Outcome | Basis in the upstream text |
| --- | --- |
| Each mistake class has evidence that it happened at least twice. | "Find the mistake classes": "Group the mistakes into classes. A class counts once it has happened twice." (a floor, so at least twice). Reply: "each class with its evidence". |
| Each fix is at the highest level that works for its class. | Heading "Fix each class at the highest level that works". Reply: "the level you picked, and why a higher level didn't work". "Keep the rule table": "fix it at the highest level in the same change". |
| The most frequent classes are fixed, one commit each. | "Fix and prove": "Then fix the most frequent classes now, one commit each." |
| Each new check is shown to fail on a real past mistake. | "Fix and prove": "Prove each new check fails on a real past mistake." Description: "Prove each check fails on a real past mistake." |
| The same command runs locally and in CI. | "Fix and prove": "Run the same command locally and in CI." |
| A table in the agent instruction file pairs each rule with what enforces it. | "Keep the rule table": "Last, keep a table in the agent instruction file that pairs each rule with what enforces it." |
| The reply gives each class with its evidence, the level picked, and why a higher level didn't work. | "**Reply:** each class with its evidence, the level you picked, and why a higher level didn't work." |

Carried from the frontmatter description into the body:

- "Try architecture first, then types, then a lint whose error names the fix, then a test, and write docs last." The upstream body states this order only through the heading "Fix each class at the highest level that works" and the numbering 1 to 4. Carried verbatim in the second dependency item under Constraints.
- "Repeat this each time the operator corrects you." The upstream body has a narrower sentence ("When the operator corrects you, fix the mistake and add the rule. ..."), kept verbatim in "Keep the rule table" step 2. The description's sentence is carried as the first sentence under Constraints, "Repeat this work each time the operator corrects you.", with "this" made "this work" because the sentences it pointed back to are not next to it.
- "Find the mistakes agents keep repeating in this repo and make each one impossible." and "Prove each check fails on a real past mistake." are already in the body ("Change the repo so the next agent can't make them.", "Prove each new check fails on a real past mistake."), so nothing was carried. "Use for /correct." is a trigger and stays in the frontmatter only.

Order dependencies stated under Constraints, with the reason for each:

- "Find the mistake classes" first. Reason: upstream order word "First,", and every later step works on the classes it produces.
- "Fix and prove" after it. Reason: upstream order word "Then", and it fixes "the most frequent classes", which only the grouping produces.
- "Keep the rule table" last. Reason: upstream order word "Last,".
- The four steps under "Fix each class at the highest level that works" are levels, highest first, and each class is fixed at the highest level that works (stated first in the item). Reason: the heading, "Write docs or agent rules last", and the description ("Try architecture first, then types, then a lint whose error names the fix, then a test, and write docs last.").
- In "Fix and prove", step 2 after step 1. Reason: it proves the new checks that the fixes of step 1 add. Other Tasks inside an Activity may be worked in any order unless one states otherwise ("First," and "Last," state it).
- "fix it at the highest level in the same change" is an order upstream imposes on the result (one change), so it stays in its step.

State-changing or external effects the work can have, with the condition upstream states:

- Changes to the repo's code and structure: new owners and supported ways, hidden internals, one source of truth in place of hand-synced lists, deletion of old ways and dead code, types, a lint or CI check, tests fixed or deleted, docs or agent rules. Upstream states no approval for these.
- Commits, one per class ("one commit each"). Upstream states no approval. No push, PR, or merge is named.
- A check that runs in CI ("add a lint or CI check", "Run the same command locally and in CI"). Upstream states no approval.
- Edits to the agent instruction file (the rule table: add a rule, drop a rule). Upstream states no approval.
- An exception to a check. Condition: it goes on the offending line with a reason, an expiry date, and a human's approval.

Also: 5 statements moved to the section their function calls for; 6 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/automate-me/SKILL.md`

Title: Automate me. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Turn the user's working conventions into a skill agents will follow, through a guided flow.

| Outcome | Basis in the upstream text |
| --- | --- |
| Where the run is in update mode, the existing file is edited in place. | Step 0: "Step 4 edits the existing file in place. Preserve sections the user hasn't contradicted." |
| Where the run is in update mode, the sections the user hasn't contradicted are kept. | Step 0: "Step 4 edits the existing file in place. Preserve sections the user hasn't contradicted." |
| The skill meets the Guardrails, each with the force it states. | "Guardrails", all six entries. Each states a rule for what the mode skill holds ("Require multiple instances before codifying it.", "Keep it operational.", "Other skills the user relies on should appear as path references, not pasted excerpts.", "Only add a section if the user has a specific, non-default rule there.", "Use "the user" or "the human" in imperatives", "skip the Process section entirely"). Each Guardrail keeps its own force: "should appear as path references" stays a recommendation. |
| The skill's path and frontmatter follow the placement rules of step 4. | Step 4, the list after "Placement:" (Path, Handle, Frontmatter `description`, Frontmatter formatting, Frontmatter `disable-model-invocation: true` by default). |
| The user judges that the skill reads like them and misses nothing. | "Evaluation": "Vibe-check with the user: does it read like them? Did it miss anything? Then ship." Step 5: "Show the draft to the user and take feedback. Expect multiple iterations." Shipping follows the vibe-check, so the result is the user's positive judgment. Medium confidence: upstream does not say what happens if the user never judges it so. |
| Where the skill is placed in the project, it is committed in a worktree off main and open as a PR. | Step 6: "Work in a worktree off main. Commit and open a PR." Conditional because step 4 allows `~/.cursor/skills/<handle>-mode/` "if the user prefers a personal skill", where this cannot hold (profile 15.3). |
| Nothing is pushed to main directly. | Step 6: "Don't push to main directly." It holds on every path, so it is a separate Outcome. |

Carried from the frontmatter description into the body:

- "Drafts or revises a personal -mode skill via create-skill + unslop, optionally pulling fresh evidence from recent transcripts." The body states the mining (step 1) with no option, so the description's "optionally" is a permission the body lacks. The sentence is carried whole as the first sentence under Constraints, with the subject "This skill" and the description's own naming (plain -mode and create-skill, no code formatting). The trigger phrases ("automate me", "create/update/refresh my -mode skill", "turn/capture my preferences or working style into a skill", "wanting agents to follow how the user works") stay in the frontmatter only.

Headings whose text changed:

- "## Flow" became "## Tasks". Only element names are allowed as H2 headings, and the seven step headings sit directly under it. No other file cites the heading "Flow". Step 0's "Update mode changes the rest of the flow" still resolves: the Purpose keeps the words "a guided flow".

Order dependencies stated under Constraints, with the reason for each:

- Step 0 first. Reason: its result changes later steps. "Update mode changes the rest of the flow", with entries for steps 1, 2, and 4.
- Step 3 after steps 1 and 2. Reason: it uses results only they produce. "Group the combined signals into sections."
- Step 4 after step 3, and step 5 after step 4. Reason: step 4 drafts the skill whose sections step 3 forms, and step 5 applies the prose rules "to every line" of that draft and shows "the draft" to the user.
- The vibe-check under Evaluation before the skill ships. Reason: upstream order word, "Vibe-check with the user ... Then ship."
- Step 6 has no stated dependency beyond the listed order.
- Orders inside one step stay in the step: "Locate the active workspace's transcripts before fanning out.", "Cross-check across slices before elevating a signal.", "Start broad ..., then follow up on selected areas", "After the structured rounds, one free-form chat question", "ask why before doing it".

State-changing or external effects the work can have, with the condition upstream states:

- Starting fresh over an existing mode skill. Condition: confirm intent with `AskQuestion` unless the user already said, and "ask why before doing it".
- Editing an existing mode skill file in place (update mode). Condition: the same confirmation of intent in step 0.
- Writing the mode skill to `.cursor/skills/<handle>/<handle>-mode/SKILL.md` or `.cursor/skills/<handle>-mode/SKILL.md` in the project. Upstream states no approval beyond showing the draft and taking feedback (step 5).
- Writing the mode skill to `~/.cursor/skills/<handle>-mode/`, which is outside the repository. Condition: "if the user prefers a personal skill".
- Creating a worktree off main, committing, and opening a PR (step 6). Upstream states no approval. Prohibition: "Don't push to main directly."
- Reading chat transcripts and spawning parallel subagents (step 1). Reading is limited to the active workspace's `agent-transcripts/` directory. "Don't glob across `~/.cursor/projects/*/`."

Also: 6 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).
