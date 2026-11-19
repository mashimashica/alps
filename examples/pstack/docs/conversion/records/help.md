# Conversion record: poteto-help

[Conversion guide](../README.md)

## `skills/poteto-help/SKILL.md`

Title: Poteto help. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Give a user who asks about pstack an answer they can act on themselves, leaving the work their question is about for them to start. A message that asks for work is not a help question, and its work is done under `poteto-mode`.

| Outcome | Basis in the upstream text |
| --- | --- |
| For a help question, the reply answers the user's question about pstack, for the need inferred from the message and the conversation or picked by the user. | Intro paragraph 1: "Answer the user's question about pstack". Find out what they need: "Infer the need from the message and the conversation." and "If the need is still unclear, ask one multiple-choice question with these options, then answer only the section they pick". Reply: "Lead with the answer." The condition follows intro paragraph 2, which separates a message that asks for work from a help question. |
| For a help question, what the reply states about a file it routes to matches that file, including where that file disagrees with this map. | Intro paragraph 3: "Those files own the details. Read the file you route to before you quote it, and trust it when it disagrees with this map." Pick a skill: "Read the skill before you recommend it". |
| For a help question, the reply hands the user a prompt they can send. | Intro paragraph 1: "hand them a prompt they can send" and "so let them send the prompt". Reply: "Give at most one example prompt in a code block, adapted from [`references/recipes.md`]\(references/recipes.md) when one fits". |
| For a help question, the reply links the file the answer came from by its public copy. | Intro paragraph 1: "link the file the answer came from". Intro paragraph 3: "so give the user the file's public copy: `https://github.com/cursor/plugins/blob/main/pstack/` followed by its path." The reason clause ("The links here point into the installed plugin, which the user may not be able to open") stays in Task 4 and is not made a second, negative condition. |
| For a help question, no work has been started. | Intro paragraph 1: "For a help question, don't start the work. The user asked how, and a pstack run spends real tokens, so let them send the prompt." A guard restated as a result (profile section 5). "let them send the prompt" follows from it and from the prompt Outcome, so it is not a separate condition. |
| Where the message asks for work, that work is done under `poteto-mode`. | Intro paragraph 2: "A message that asks for work, such as "use pstack to fix this bug", is not a help question. Read [`poteto-mode`]\(../poteto-mode/SKILL.md), do the work under it". The success of that work is judged by poteto-mode's own description; this Outcome holds only that the work runs under it. |
| Where the message asks for work, the reply mentions once that a Custom Mode keeps it on. | Intro paragraph 2: "and mention once that a Custom Mode keeps it on." This is the skill's own reply content on that path; no poteto-mode file states it. |

State-changing or external effects the work can have, with the condition upstream states:

- Starting pstack work (a pstack run that spends tokens and can edit, commit, or open PRs under its own playbook). Condition upstream states: Prohibited for a help question: "For a help question, don't start the work. ... so let them send the prompt." Done only when the message itself asks for work, and then under poteto-mode: "Read [`poteto-mode`]\(../poteto-mode/SKILL.md), do the work under it". poteto-mode's own approvals and limits govern every effect of that work. The help work itself only reads files, may ask the user up to two questions together, and replies.

Also: 9 statements moved to the section their function calls for; 3 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-help/references/prompting.md`

Unchanged from upstream.

## `skills/poteto-help/references/recipes.md`

Unchanged from upstream.
