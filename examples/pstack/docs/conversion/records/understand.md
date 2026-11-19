# Conversion record: how, why, teach, recall

[Conversion guide](../README.md)

## `skills/how/SKILL.md`

Title: How. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Answer "how does X work?" questions from an exploration of the codebase, with an explanation that gives a solid mental model of the area. Use why for motivation.

| Outcome | Basis in the upstream text |
| --- | --- |
| The user's question is answered with an architectural explanation that comes from exploring the codebase. | Intro line: "Explore the codebase to answer "how does X work?" questions." Step 1: "Spawn one Task subagent ... that explores and explains in one pass. Give it the user's question and this brief". Brief: "You are writing an architectural explanation ... Explore the codebase and write an explanation". |
| The explanation is one that a senior engineer unfamiliar with the area could read and walk away with a solid mental model, understanding the architecture well enough to start working in it confidently. | Brief in step 1: "write an explanation that a senior engineer unfamiliar with this area could read and walk away with a solid mental model. They should understand the architecture well enough to start working in it confidently." Description: "Explains subsystem architecture, runtime flow, onboarding mental models." |
| Where the scope is ambiguous, the interpretation that was explored is stated. | Second paragraph: "If the scope is ambiguous, state your interpretation and explore. The user can redirect." |

Carried from the frontmatter description into the body:

- "Use why for motivation." (carried verbatim as the last sentence of the Purpose, as the boundary with neighboring work. The skill name stays bare, as the description writes it.)

Order dependencies stated under Constraints, with the reason for each:

- Step 2 presents the output of the subagent that step 1 spawns. Reason: step 2 uses a result that only step 1 produces ("Present the subagent's output.").

Also: 3 statements moved to the section their function calls for; 2 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/why/SKILL.md`

Title: Why. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Answer why the target is the way it is, with a cited read on decisions and tradeoffs. Use how for runtime behavior.

| Outcome | Basis in the upstream text |
| --- | --- |
| The answer comes from the record, not the code. | Sentence 1: "Answer from the record, not the code" |
| The answer cites what the authors wrote. | Sentence 2: "Cite what the authors wrote". Description: "Returns a cited read on decisions and tradeoffs." |
| The answer marks its own inferences as inferences. | Sentence 2: "mark your own inferences as inferences" |
| The answer says what the record does not answer. | Sentence 2: "and say what the record does not answer" |

Carried from the frontmatter description into the body:

- "Returns a cited read on decisions and tradeoffs." (carried into the Purpose as "with a cited read on decisions and tradeoffs". The body says to cite but does not name decisions and tradeoffs.)
- "Use how for runtime behavior." (carried verbatim as the last sentence of the Purpose, as the boundary with neighboring work. The skill name stays bare, as the description writes it.)
- The "Use for" list ("why does X work this way", "why we picked Y", design rationale, regressions, postmortems, data-backed thresholds) is not carried as rules and stays in the frontmatter. The Purpose states the work at the generality of the body ("why the target is the way it is"), so that regression and postmortem questions, which bug-fix step 2, benny, and recipes route to this skill, stay inside it.

Also: 2 statements moved to the section their function calls for; 2 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/teach/SKILL.md`

Title: Teach. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Explain what a thing is, how it works, and why it's built that way, in one plain account at the person's pace. The goal is that they understand it, not that you change anything.

| Outcome | Basis in the upstream text |
| --- | --- |
| The reply is the explanation itself, never a report about what you did or delivered. | Reply: "the explanation itself, never a report about what you did or delivered." |
| The explanation is aimed at the few things the person should walk away understanding, chosen from why they're asking and what they already know, and puts the depth where their question is. | Step 1: "Decide the few things they should walk away understanding. Choose them from why they're asking ... and what they already know, both read from the conversation ... Skip what they plainly already know. Put the depth where their question is." Step 3: "Give the smallest complete answer first, a sentence or two, not a dense paragraph, then stop. Add layers when they ask." (so the Outcome does not require that every one of the few things is covered on the path where the person does not ask for more). |
| The explanation is one plain account that blends what real skill invocations of `how` and `why` found, run at the size the question needs. | Lead line: "in one plain account". Paragraph 2: "run `how` for how it works and `why` for why it's that way. Those are real skill invocations that do their own digging. Blend what they find into one plain explanation". Step 2: "Let `how` and `why` do the work, don't redo it.", "Run them in parallel and combine the results. Match the size to the question. Run both for a subsystem, maybe one is enough for a small change." |
| `why`'s confidence language is intact in the explanation. | Paragraph 2: "Reword freely for teaching, with one exception. Keep `why`'s confidence language intact (its hedges are findings, not style)." |
| The explanation goes deeper when the person asks and follows their lead, or, running one-shot with no live human, puts any offer to go deeper at the end. | Lead line: "at the person's pace". Paragraph 2: "go deeper when they ask". Step 3: "Add layers when they ask." Step 4: "Offer to go deeper or move on, and follow their lead.", "Running one-shot with no live human, deliver it cleanly and put any offer to go deeper at the end." |
| Every response is plain spoken English that follows the writing rules under Controls, except that `why`'s confidence language stays intact. | Style paragraph: "Write every response through the **unslop** skill, in plain spoken English, the way you'd explain it to a colleague." and the rules that follow it. Lead line: "one plain account". Paragraph 2: "Reword freely for teaching, with one exception. Keep `why`'s confidence language intact (its hedges are findings, not style)." |

Order dependencies stated under Constraints, with the reason for each:

- Steps 3 to 5 follow steps 1 and 2. Reason: the explanation covers the things step 1 decides and blends what the runs of step 2 find ("Run them in parallel and combine the results.", "Blend what they find into one plain explanation").
- Steps 4 and 5 do not follow step 3. They hold for the whole explanation that step 3 starts. Reason: they are standing disciplines of the explanation, not successors of step 3. The item limits the fixed sentence so that no order is added.
- Kept inside upstream's own sentences and not restated: paragraph 2 "Get your bearings on what the work is and what it touches, then run `how` ... and `why`" (now under Constraints), step 2 "Read the code yourself to get oriented, then run `how` ... and `why`" and "Run them in parallel", step 3 "Give the smallest complete answer first ... then stop. Add layers when they ask.", step 5 "First A to B. Then redraw and add C. Then redraw and add the return edge or the next piece."

State-changing or external effects the work can have, with the condition upstream states:

- None stated. Step 5 can open the debugger and call the image-generation tool. `how`, run from step 2, spawns one read-only subagent. Condition upstream states: "when that is the fastest way to land it" and "When the idea is spatial". Upstream states no approval. The Purpose keeps "not that you change anything".

Also: 5 statements moved to the section their function calls for; 2 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/recall/SKILL.md`

Title: Recall. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Before you start or resume work, rebuild the user's recent working context and hand back a tight capsule of where things stand now and what to do next.

| Outcome | Basis in the upstream text |
| --- | --- |
| The scope searched is the scope stated back, which names the window, the topic if named, and the workspace, and a request for "all" is not quietly turned into "recent N". | Step 2: "Lock the scope before searching. Pin the window ("recent" is a real range, default the last 7 days), the topic if named, and the workspace ... State the scope back. Never quietly turn "all" into "recent N"." |
| The brief rests on the in-scope chats of your own chat history, or on the full state capsule where the user already gave one. | Paragraph 3: "Your own chat history holds what you did and decided." Step 3: "Fan out across your chat history.", "read only the matching chats", "For one or two chats, skip the fan-out and search directly." Step 1: "If the user already gave you a full state capsule (paths, branch, the change), use it and skip the mining." |
| Whenever the topic names a feature, file, subsystem, area, or bug, the brief folds in what the sweep of the shared record returned, null results included. | Step 4: "Sweep the shared record whenever the topic names a feature, file, subsystem, area, or bug. This is the default, not a judgment call", "Null results are findings.", "Fold what comes back into the brief." Paragraph 3: "so don't reconstruct it from your transcripts alone". |
| Where an MCP was unavailable for the sweep, it is reported as skipped. | Step 4: "Skip an unavailable MCP and say so." Upstream does not say where it is said, so the Outcome does not fix it. |
| Each PR, branch, and ticket status that the brief states matches its live state. | Step 5: "Verify against live state. Take the PRs, branches, and tickets that the mining and the sweep surfaced and check them with `git` and `gh`." Lead line: "where things stand now". Output contract: the thread status tags. |
| The brief follows the output contract, from the capsule of where the work stands to the single most useful next action. | Lead line: "hand back a tight capsule of where things stand now and what to do next". Step 6: "Write the brief to the contract below." Output contract: "Lead with the capsule, then the thread status, then the problems, then the next move." and its items. Reply: "the brief, to the contract above." |

Order dependencies stated under Constraints, with the reason for each:

- Step 1 comes first. Reason: it is the gate that can route the request elsewhere or skip the mining ("Classify, then route.", "use it and skip the mining").
- Step 2 comes before any searching in steps 3 and 4. Reason: "Lock the scope before searching."
- Step 4 runs in parallel with step 3. Reason: "Run them in parallel with the chat-history mining."
- Step 5 follows steps 3 and 4. Reason: it checks "the PRs, branches, and tickets that the mining and the sweep surfaced".
- Step 6 follows steps 3, 4, and 5. Reason: the brief is written from what they return ("Fold what comes back into the brief.").
- Kept inside upstream's own sentences and not restated: step 3 "grep the topic first and then read only the matching chats", the contract's "Lead with the capsule, then the thread status, then the problems, then the next move" and "cut detail before you cut threads" (orders of the result), and "sanitize private context before any public output".

State-changing or external effects the work can have, with the condition upstream states:

- Public output of the brief. Condition upstream states: "sanitize private context before any public output" (Output contract, closing paragraph). Upstream states no approval and does not say what counts as public.
- Step 4 spawns one investigator subagent per source in agent mode, with MCP access to source control, the issue tracker, chat and issue channels, long-form docs, and error tracking. Each is asked a question. Agent mode does not stop writes through MCP. Condition upstream states: "in agent mode because readonly strips MCP access". Upstream states no approval and no limit on writes.
- Reading another project's transcripts. It changes no state, but it reaches private chats outside the workspace. Condition upstream states: "Never read another project's transcripts without being asked" (step 2)

Also: 8 statements moved to the section their function calls for; 3 additions other than the Purpose and Outcomes (fixed sentences, pointers).
