# Conversion record: poteto-mode

[Conversion guide](../README.md)

## `skills/poteto-mode/SKILL.md`

Title: Poteto mode. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Work the user's task in poteto's agent style, through the playbook or skill that owns its result.

| Outcome | Basis in the upstream text |
| --- | --- |
| Where the agent is the runner for `/poteto-mode`, not one of its delegates, the task runs under the playbook matched to it, or under the **figure-it-out** skill where the work is large, cross-cutting, or unattended, or no playbook fits. | Playbooks: "Match the task to a playbook and open its steps at `playbooks/<title>.md`, with the title in kebab case. Copy its steps into the todolist tool first. Large, cross-cutting, or unattended work, or a task no playbook fits, routes to the **figure-it-out** skill." Scope: Subagents, "The chat that receives `/poteto-mode` runs the playbook itself."; agents/poteto-agent.md, "Use for delegates, not as the runner for `/poteto-mode` itself." and "The chat that receives `/poteto-mode` owns the playbook, the todo list, and every Task spawn. You are one of its delegates." "runner" is used rather than "the chat that receives `/poteto-mode`" so the condition also covers a chat that reads poteto-mode and does the work under it (poteto-help: "Read `poteto-mode`, do the work under it"). The Outcome keeps upstream's disjunction and does not decide which route wins where both could apply. The Playbooks step itself stays unscoped as upstream wrote it. |
| Each trigger that fired is answered as its entry states. | Non-negotiables: "The Principles section below grounds every trigger." and "The remaining triggers live only here:" with its eleven entries of the form trigger → response; Principles: "Each entry names when it applies." The Outcome uses upstream's word "trigger" without a qualifier, so it covers whatever upstream means by it, the Principles entries included where they are triggers (guide page 8: poteto-mode "applies the ones the task triggers"). It neither narrows nor hardens the ambiguity recorded under findings. |
| The reply names each principle that shaped a decision and the specific choice it changed. | Non-negotiables, first paragraph: "In your reply, name each principle that shaped a decision and the specific choice it changed." |
| The reply cites only principles whose leaf SKILL.md the agent writing it read this session. | Non-negotiables, first paragraph: "Cite only principles whose leaf SKILL.md you read this session." The reader is the agent that writes the reply, as upstream's "you" states. Kept separate from the naming Outcome because the two can fail independently. |

Places where meaning, force, or scope differs from upstream:

- The shape this file shows as the exemplar for **automate-me** ("The **poteto-mode** skill shows the shape. Read it for granularity. Don't copy its content.") is now the element shape (Purpose, Outcomes, Activities & Tasks, Outputs, Controls, Constraints, Enablers, a governing sentence, numbered steps) around the six upstream parts, instead of six flat H2 sections of rules. Reason: Profile sections 5 and 9. No edit inside the profile removes it. A mode skill that automate-me drafts may take up the element shape, which changes automate-me's Output (profile section 3 rules that out for generated artifacts). The six parts and their granularity are unchanged. Unverified until an automate-me trial. Lead decision: run the trial or accept the change.

State-changing or external effects the work can have, with the condition upstream states:

- External actions: team chat, ticket updates, kicking off evals, and use of any MCP tool Condition upstream states: Autonomy: "**Just do it.** Use any MCP tool. Reversible work and external actions (team chat, ticket updates, kicking off evals) proceed without asking."
- Irreversible writes: force-push to shared branches, deploys, data deletion, customer messages Condition upstream states: Autonomy: "**Always pause** for irreversible writes". Upstream does not say whether "**Session overrides:** ... → keep going" lifts this pause (see findings).
- Starting agents (a Task subagent or a Project worker) Condition upstream states: Non-negotiables step 2: the first line of the kickoff is `Read <path>/worker.md before anything else.`. Subagents: defaults for every `Task` call, an explicit model per role, fresh subagents by default.
- Commits Condition upstream states: Non-negotiables step 6: "Before commit → `/deslop` from the `cursor-team-kit` plugin."
- Opening a PR, replying on PR threads, and merging a stack Condition upstream states: This file only routes: "PR status → the **Babysit** playbook", "Landing a green stack → the **Shipping** playbook", and each playbook ends in Opening a PR. The approvals are stated in those playbooks and in Autonomy.
- A message to the user to rerun `/setup-pstack` Condition upstream states: Subagents: when the rule has no `# defaults: 3` line, "tell the user once per session to rerun `/setup-pstack`".

Also: 8 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-mode/worker.md`

Unchanged from upstream.

## `agents/poteto-agent.md`

Unchanged from upstream.
