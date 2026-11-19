# pstack to ALPS conversion profile

[Conversion guide](README.md)

These are the conventions that every converter, reviewer, and reviser of this tree worked under. They were synthesized from three independent proposals (Framework-first, operator-fidelity-first, work-system-first) and from analyses of pstack's tools, hosts, and upstream tooling. The [conversion records](records/) cite the sections below by number.

The profile is kept as it was used, so it addresses the converter. Two things in it refer to the working material and not to this tree. Names such as `absorbed_from_description`, `added`, `findings`, `anchors_kept`, and `profile_issues` are fields of the working records from which the conversion records were compiled. "The lead" is the agent that coordinated the conversion. The profile is the conversion's own convention. It is not part of the Process Framework, and nothing in it binds another conversion.

## 1. Sources and precedence

- **Source:** `pstack` 0.15.44 from `https://github.com/cursor/plugins` at commit `e58dd043600587dbaf58ba315e7f2b38373eeb43`, path `pstack/`, MIT License.
- **Target tree:** `examples/pstack/` in the ALPS repository. Before conversion every file in it holds the upstream bytes at the same relative path.
- **Governing sources:** the Process Framework governs meaning and Markdown presentation. The Design Principles for Agent Work Systems govern agents, tools, information supply, and host bindings.

When rules pull in different directions, apply them in this order:

1. **Preserve the meaning of the upstream work.** No obligation, prohibition, permission, recommendation, condition, exception, threshold, exact identifier, exact output string, label, count, or trigger may be lost, weakened, strengthened, narrowed, or widened.
2. **Meet the Framework's requirements** for a Process Description.
3. **Follow this profile's conventions.**
4. **Keep the file short.**

If 1 and 2 cannot both be met, keep the upstream meaning and record the deficiency as a finding about the source in the conversion record. Never invent a requirement, criterion, or success condition to make a description look complete.

## 2. What the conversion is

The conversion is a **change of presentation** that also makes explicit two things upstream leaves implicit: why the work is done (Purpose) and what observably holds when it has succeeded (Outcomes). It classifies the remaining content by its function in the work. It is **not** a redesign. Do not improve, extend, correct, modernize, or generalize how pstack works. Do not port it to another host. Do not repair an upstream ambiguity, inconsistency, or divergence between two files: keep both texts and record the finding. An agent that follows the converted file must do what an agent that follows the upstream file does.

**Purpose and Outcomes are the converter's derivation.** Upstream never wrote them, and its author has not confirmed them. They must follow from what the upstream text instructs, checks, and reports:

- Every Outcome needs a basis in one or more upstream sentences, and the record names that basis. An Outcome with no basis is not written.
- An Outcome must not demand more than the upstream instructions establish, and must not leave out a result that upstream insists on. `worker.md` tells workers "Add no check, gate, sign-off or review round above" the stated bar: a derived Outcome that raises the bar violates the source.
- An ambiguous upstream statement is not hardened into an Outcome. Keep the statement where it is, in its own words, and record the ambiguity.
- If you cannot tell what result upstream wants, write the most defensible reading and record the uncertainty as a finding.

**Fixed labels and counts are part of the meaning.** The README, the guide, the Claude Code adapter, and other skills state them as facts about a skill: verdict and result labels (`PASS`, `PASS+NOTES`, `FAIL`, `ISSUES`, `BLOCKED`, `COMPLETE`, `clean`, `changed`, `blocked`, `Accepted`, `Rejected`, `Backlog`, `VERIFIED`, `NOT VERIFIED`, `INCONCLUSIVE`, `MUST KILL`), named report sections ("Dropped", "Attention"), role-line labels (`arena runners`, `arena cross-judge pool`, `interrogate reviewers`, `swarm workers`, `judgment and prose`, `feature, refactoring`, `bug-fix`, `perf-issue`, `hillclimb`), file names (`decisions.tsv`), PR body heading names, TSV column names, and counts ("seven questions", "two different shapes", "one of three"). Keep each one exactly.

## 3. Which form each kind of file takes

Decide the kind by what the file does, not by where it sits. A file becomes a Process Description when its body defines work that has results of its own.

| Kind | Files | Treatment |
| --- | --- | --- |
| Skill entry | every `SKILL.md` | Frontmatter byte-identical (section 4), then a Process Description (section 5). |
| Playbook | `skills/poteto-mode/playbooks/*.md` | A Process Description without frontmatter (section 7). |
| Reviewing agent | `agents/comment-sicko.md` | Frontmatter byte-identical, then a Process Description of the work that agent performs (section 8). |
| Bootstrapping agent | `agents/poteto-agent.md` | **Byte-identical.** It configures a delegate (read poteto-mode first, how to find it, stop if absent). It is an Enabler, not independently defined work. |
| Shared worker rules | `skills/poteto-mode/worker.md` | **Byte-identical.** It is already a shared set of Constraints that states its scope and its rule for contextual change, and every worker reads it first. |
| Host adapter | `docs/harness/claude-code.md` | **Byte-identical.** It maps exact Cursor names, and upstream tooling checks its rows. |
| Work-directing reference | a reference that prescribes work with a result of its own | A Process Description (Sub-process) without frontmatter, in the same file. Use this only when the file clearly is a procedure. When in doubt, treat it as a knowledge reference. |
| Knowledge reference | references that supply knowledge, criteria, rubrics, patterns, prompts, or examples used by work described elsewhere (`references/bugbot-triage.md`, `patterns.md`, `prompting.md`, `recipes.md`, the feature-map examples, `render.md`, `routing.example.md`, `feature-map.example.md`) | **Byte-identical**, unless a relative link in it must change (section 13). |
| Payload text | prompt templates, the benny `FOR_AGENTS.md`, briefs quoted inside a skill for a subagent | **Byte-identical.** They are messages the work sends, not descriptions of the work. |
| README and guide | `README.md`, `automations/benny/README.md`, `docs/guide/**` | **Byte-identical**, except links to files that are not in the tree (section 13). The lead handles these. |
| Tool-use reference | new `references/tool-use.md` or `references/tool-use-<tool>.md` | The facts design principles section 4 requires (section 12). |
| Scripts, lockfiles, config, data | `scripts/**`, `*.tsv`, `*.yaml`, `*.json`, `LICENSE` | **Byte-identical.** Never edit. |

Text inside a skill that specifies what a *generated* skill, mode, or playbook must look like (`create-verification-skill`, `create-formal-verification-skill`, `automate-me`, `figure-it-out`) is carried unchanged and not extended. Requiring generated artifacts to take ALPS form would change those skills' Outputs.

## 4. Frontmatter

Keep the frontmatter block of every `SKILL.md` and agent file **byte-identical** to upstream: `name`, `description`, and every host field (`disable-model-invocation`, `icon`, `color`, `paths`, and for agents `model`, `is_background`), including quoting, order, and folded scalars. The hosts act on those fields (57 of 58 skills load only when the operator types them), and other upstream text is true only because of them. Nothing moves to `metadata`. Nothing is added.

**The body must carry every rule the description states.** The body is the Process Description and the frontmatter is discovery text. Several upstream files state a rule only in the `description` (at least `principle-exhaust-the-design-space`, `principle-encode-lessons-in-structure`, `principle-guard-the-context-window`, `principle-migrate-callers-then-delete-legacy-apis`, parts of `principle-laziness-protocol`, and `architect`: "then stay in the loop while implementation fills in"). Where the upstream body lacks a rule that its description states, carry the description's sentence into the body in its own words, in the section its function calls for, and record it under `absorbed_from_description`. Trigger phrases and slash names meant for discovery stay in the frontmatter only.

## 5. Process Description structure

```markdown
# <Name>

## Purpose

<One or two sentences.>

## Outcomes

- <One observable result condition.>

## Activities & Tasks        (or "## Tasks" when grouping adds nothing)

<Governing sentence.>

### <Activity>

1. <Task.>

## Inputs
## Outputs
## Controls
## Constraints
## Entry Criteria
## Exit Criteria
## Enablers
## Resources
```

Only `# Name`, `## Purpose`, and `## Outcomes` are always present. Add another section only when the upstream file has content with that function. Never add an empty section, a placeholder, or a section that restates another. Keep this section order. Use only these H2 headings.

**Name.** The title is the first line of the body and the first line in the whole file that starts with `# ` (upstream tooling inserts a host pointer after that line). Use the upstream H1 text verbatim. Where upstream has no H1 (`bro`, `in-your-own-words`, `sharpen`), use the skill's name in sentence case (`# Bro`, `# In your own words`, `# Sharpen`). Never rename.

**Purpose.** State the objective the work serves, in upstream's terms. Do not summarize the steps, and do not write "apply X". Do not join independent objectives. Name a boundary with neighboring work only where upstream draws one ("Use why for motivation", "Do not apply fixes"). A definition the work depends on ("The root cause is the first place ...") may follow as a carried sentence.

**Outcomes.** Each list item is one observable, assessable result condition, written in the present tense as a state of the work product or its evidence. The subject is the thing, not the agent.

- Not an action ("Run the tests"). Not the mere existence of an Output ("A report is written"): an Outcome must be able to fail when the artifact exists but is wrong.
- Derive them from conditions upstream states for done, stop, pass, or fail; from what a required reply or report must show; from verification steps; from the bold "You own X" lead line of a playbook; and from guards of the form "X never ships", restated as a result ("Every shipped line traces to runtime evidence").
- Where upstream gives an alternative ending ("if it cannot be reproduced, say why and use the closest check"), write the Outcome so that it can be met on that path too. Add such an alternative only where upstream provides one. A conditional Outcome carries its condition ("Where ...").
- Use as few as are sufficient. Usual sizes: a principle 1 to 4, a one-line skill 1 to 3, a playbook 3 to 6, a workflow skill 3 to 7.
- Test each set before you keep it. Could all Outcomes hold while the Purpose is unfulfilled? Could the Purpose be fulfilled without one of them? Could the Output exist while an Outcome does not hold? Does any Outcome demand more than upstream's instructions establish?

**Activities & Tasks.** Tasks carry the work content of the upstream file.

- An Activity is a cohesive group of Tasks. Use upstream's own section or phase headings as Activity headings, text unchanged (`### Phase A: Frame`). Use a plain `## Tasks` list when upstream has a single list or a single paragraph of instructions.
- One upstream numbered step is one Task with the same number. Never renumber, split, merge, or insert a numbered item. Unnumbered action bullets and action paragraphs become numbered Tasks in source order, one per independent action, when no other file cites them by position.
- Carry the upstream sentence wherever it keeps its function. Change only what a move requires: person, persona voice, or a modal that makes force explicit. Do not restyle. The first sentence of a Task is its action. The sentences after it are its method and its own conditions.
- **Placement.** A condition, limit, criterion, or capability that applies to one Task alone, and does not order two Tasks, stays inside that Task. A statement that applies to two or more Tasks or to the whole description goes to the section its function calls for. Order between Tasks goes to `## Constraints`.
- **Force.** An imperative under the governing sentence is a requirement. "Never", "do not", "don't", "no X" give **must not**. "Always" gives **must**. "Prefer", "should", "ideally" give **should**. "May", "can" used as permission, "is fine", "is a valid result" give **may** or a plain statement of permission. "By default" or "usually" followed by a rule stays a default with its override condition. Never raise or lower force. Use the modals only where upstream's wording does not already make the force plain.
- **Governing sentence.** Begin the section with exactly one of these, with "skill", "playbook", or "principle" as fits, and "runs" or "applies" as fits:
  - with upstream numbered steps or lettered phases: "The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks, and other files cite them as steps. Required order is stated under Constraints."
  - otherwise: "The following Tasks are required whenever this skill runs, each with the conditions it states. Numbers identify the Tasks and set no order."

**Inputs.** What the work examines or transforms: the user's request, a diff, files, transcripts, measurements. Add the section only when no Task already identifies the material, or when upstream has a scope statement ("The scope is what the user names. Otherwise ...").

**Outputs.** What the work produces or updates: a reply, a report, a PR, a log, a generated skill, an artifact. A required reply or report format ("**Reply:** ...", "## Output", "Final response") goes here with every required content item, with upstream's own label kept. Outputs are not Outcomes.

**Controls.** What directs the work or supplies the basis for judging it: rubrics, criteria, tests ("The test: ..."), keep-lists, style rules, title and body formats, definitions, role lines of the model rule file, and another skill when it governs the whole description as a criterion.

**Constraints.** What limits permitted execution or the conditions of application:

- scope fences and prohibitions ("Report the findings. Do not apply fixes.");
- approvals and conditions that must be confirmed before an action ("pause for irreversible writes");
- limits on agents, tools, and models ("No role runs above xhigh");
- conditions under which the work applies or does not apply, when the body states them or section 4 brings them into the body;
- **required order.** Document order and numbering never imply execution order, so order must be stated. Where upstream gives a numbered or lettered sequence, write: "Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required." followed by one list item per necessary dependency ("with Activities": "work the Activities and their Tasks in the order listed"). A dependency is necessary when upstream says so with an order word (first, before, after, then, once, until, only after), when the later Task uses a result only the earlier one produces, when the earlier Task is the gate, verdict, or approval for an effect of the later one, or when the earlier Task captures state the later one changes (a baseline). If you find no necessary dependency beyond the listed order, write only the first sentence. Order that upstream imposes on a result rather than on the work (commit order in history, landing order of PRs) stays in its Task. Never drop or loosen an order, and never add one upstream does not have.

**Entry Criteria and Exit Criteria.** Use Entry Criteria for conditions that must hold before the work as a whole can begin, and Exit Criteria for conditions under which it can be completed or handed back, when upstream states such conditions as gates ("Stop at the ceiling", "a run is not done until ..."). Do not restate Outcomes as Exit Criteria.

**Enablers.** Capabilities and resources the work depends on. Add the section only when upstream has a statement whose function is to name or describe a capability or resource rather than to order an action ("Bundled skills live at ...", "The first run installs TLC and Java with mise and needs the network"), or when the description uses a bundled tool or agent (section 12). Do not create it merely to list identifiers that Tasks already carry. A limit on an Enabler is a Constraint.

**Resources.** Links to bundled files, each with its role and when to consult it. Add only for bundled files that no other section already links.

**Another skill named in the work.** When the work applies another skill to do part of the job ("run the **arena** skill"), that is a related Process: keep the instruction in the Task. When another skill supplies a criterion ("per the **prove-it-works** principle skill"), keep the citation at the statement it governs. Keep upstream's way of naming a skill exactly as written in each place: "the **name** skill" (bold name, lowercase "skill"), `` `/name` ``, "the **name** principle skill", or a relative link. Upstream tooling and the Claude Code adapter match those literal forms. Do not turn one form into another, do not capitalize "Skill" for a pstack skill, and do not add or remove a link on such a line.

**Shared information.** Some information is written by one skill and read by others: the model rule file `pstack-models.mdc` (written by **setup-pstack**; read by poteto-mode, arena, swarm, interrogate, and the code playbooks through their role lines), the decision log (owned by **show-me-your-work**), a project's verification skill and feature map. Where upstream states who writes or reads such information, keep that statement with the Input, Output, or Control it concerns. Do not invent a relationship upstream does not state.

**Notes.** An explanation with no force may be a note: a blockquote beginning with `NOTE`, placed immediately after the text it explains, indented under a list item when it explains that item. Use a note only for a standalone rationale or example sentence (`**Why:** ...`, "X are the usual ways to ..."). Rationale that sits inside an instruction sentence ("because a merge lands whatever its branch holds") stays in that sentence. Never split a sentence between normative text and a note. No requirement, prohibition, recommendation, or permission may be stated only inside a note. Add no notes of your own.

**Literal text.** Briefs handed to another agent, kickoff lines, report templates, exact first lines, option labels, code blocks, tables, and examples are kept byte-identical where they are used. An upstream blockquote that holds a brief stays a blockquote, introduced by upstream's sentence.

**Colliding words.** pstack words collide with element names. Handle them this way:

- `Task` in backticks, "Task tool", "Task subagent", and "Task call" always mean Cursor's subagent tool, exactly as upstream writes them. The Framework's Tasks appear only in headings and in the governing and order sentences. Everywhere else keep upstream's word "step".
- An upstream section already titled "Outcomes" that lists run verdicts (`maintain-verification-skill`, `maintain-formal-verification-skill`) is not the Framework's Outcomes. Keep its text and labels, give it a heading that says what it is (for example `### Run outcome` under `## Outputs`), and record the retitling. Keep the word "outcome" in its sentences.
- "Constraint comments" (`no-comments`), "the control skill" (`control-ui` or `control-cli`), "Process" as a heading for git conventions (`automate-me`), and "Scope" as a PR body heading keep upstream's meaning. Do not let them become element headings by accident.

## 6. Small skills and principle skills

A skill that is one sentence or one paragraph still becomes a Process Description, at the smallest honest size: title, Purpose, Outcomes, and further sections only for content that Purpose and Outcomes do not already carry. If every instruction in the source is fully expressed by the Purpose and Outcomes, stop there. A skill written in the user's voice ("I want a deeper version of this task") is restated as instructions to the agent, with "the user" for "I" and every element kept.

**Principle skills (`principle-*`).** Each body describes the work of applying one principle. Other descriptions cite the same file as a criterion. Use this pattern:

```markdown
# <upstream H1, unchanged>

## Purpose

<The objective the principle secures. A definition the rule depends on follows, carried.>

## Outcomes

- <A state of the code, decision, or evidence that holds when the principle was honored. Never "the principle was applied".>

## Tasks

<Governing sentence for a principle.>

1. <Upstream instructions that are actions, in source order and wording.>

## Controls

<Statements that are criteria or tests rather than actions, carried.>

## Constraints

This principle applies <the trigger from the description, in its words>. When another description cites this principle, that description's own limits on it hold.
<Upstream exceptions, prohibitions, and applicability conditions, carried.>
```

- The first Constraints sentence states the trigger in declarative form with the description's words ("This principle applies when debugging."). The second sentence is fixed text in all 24 files. It records existing practice (**prototype** inverts Laziness Protocol, **feature** limits it, **no-comments** limits two principles to guiding intent) and is recorded under `added`.
- `## Tasks`, `## Controls` are present only when the source has content of that function.
- Keep every example and every listed instance. `**Why:**` lines become a NOTE after the text they explain.

## 7. Playbooks

Each playbook is a Process Description that **poteto-mode** selects. poteto-mode tells the agent to open the playbook and copy its steps into the todo list, and other files cite playbook steps by number.

- Title: `# <upstream heading text>` (upstream uses `###`; make it the H1, text unchanged, even where it differs from the title in poteto-mode's list).
- Purpose from the bold "You own X" lead line and what the playbook is for. Outcomes as in section 5.
- `## Tasks`: one numbered list. Step N is Task N. Sub-bullets and nested lists stay under their step. The todo list a run copies from it must hold the same items in the same order as today.
- The paragraphs before step 1 are requirements. "You own this task. Plan, review, verify. Delegate ..." allocates responsibility between the lead and its delegates: carry it under `## Constraints`. A standing discipline paragraph ("Be scientific. ...") splits by function into `## Controls` (what counts as a fix or a pass) and `## Constraints` (what must not ship). Do not drop them and do not leave them as unclassified prose.
- `## Outputs`: the upstream "**Reply:**" paragraph with its label and every item.
- `## Constraints`: the order statement of section 5 and the playbook's prohibitions and approval conditions.
- A playbook without numbered steps (`babysit`, `opening-a-pr`) gets Tasks numbered in source order for its action statements only. Its rules go to Controls or Constraints by function. An order it states in words ("Order: conflicts, threads, CI.") is carried as a required order for exactly what it orders.
- A playbook that reuses another with changes (`autopilot-stack` over `autopilot-full`) keeps upstream's by-reference form ("In place of step 5 ...") and never copies the reused text. It gets its own Purpose and Outcomes from its own text.

## 8. The reviewing agent definition

`agents/comment-sicko.md` holds the only statement of the review rules that **no-comments** judges the agent's report against. Convert its body to a Process Description of the comment review, addressed to the agent that performs it.

- Every rule that the persona voice carries is stated once, plainly, with the same force: the keep list as `## Controls`, the default under doubt ("When it is unclear whether a keep clause applies, delete the comment") as a rule, what the agent may and must not touch as `## Constraints`, what it reports as `## Outputs`.
- Keep the shared vocabulary exactly: "keep", "kill", `MUST KILL`, the suppression names, the scent words (`IMPORTANT`, `do not remove`, `too risky`, `fine for now`).
- The exact first output is a requirement: the agent's first output must be exactly `Yes... Ha ha ha... Yes!`.
- The persona is something the operator sees, and it weights the agent's judgment. Keep it as one explicit statement under `## Enablers`: the performing agent is Comment Sicko, a comment-hater that savors deletion and condemns workaround code; the voice sets how the agent speaks and how its report reads, and states no rule.
- Record under `findings` that the effect of removing the persona narration on the agent's deletion behavior is unverified until a trial.

## 9. poteto-mode

`skills/poteto-mode/SKILL.md` is read in full by every delegate and cited by section name from about twenty files and from another plugin. Its six named parts each remain **one whole section** with the upstream heading text, as an H3 under the element of its dominant function:

| Upstream part | Converted location |
| --- | --- |
| Opening line ("Bundled skills live at `../<name>/SKILL.md` ...") | `## Enablers`, first paragraph |
| Non-negotiables | `## Activities & Tasks`, as `### Non-negotiables` |
| Playbooks | `## Activities & Tasks`, as `### Playbooks` |
| Writing the reply | `## Outputs`, as `### Writing the reply` |
| Principles | `## Controls`, as `### Principles` |
| Autonomy | `## Constraints`, as `### Autonomy` |
| Subagents | `## Enablers`, as `### Subagents` |

- Inside each section the text stays upstream's, in upstream's order. Change wording only where a statement's force is unclear without it.
- The Principles index stays inline and whole. It is a view over the 24 principle skills: keep every entry's text, do not align it with the leaf wording, and do not copy any derived Purpose or Outcome into it. The leaf governs.
- The Playbooks list stays as upstream wrote it (names, and the path rule "`playbooks/<title>.md`, with the title in kebab case").
- Keep "Copy its steps into the todolist tool first." exactly.
- Derive the Purpose and Outcomes from the description and the Non-negotiables. Autonomy and Subagents rules are limits, not Outcomes.

## 10. Host bindings

pstack is written for Cursor. `docs/harness/claude-code.md` maps exact Cursor names to Claude Code, and upstream's generator finds those names by literal match inside each skill folder.

- Keep every host identifier **verbatim, in the same file, in the statement where upstream put it**: tool names (`Task`, `AskQuestion`), "todolist", field names and values (`subagent_type: generalPurpose`, `run_in_background: true`, `readonly: true`, `environment: "cloud"`, `cloud_base_branch`), model slugs, rule and transcript paths, commands (`/loop`, `/deslop`), and feature names (Bugbot, Cursor Automations).
- Do not replace an identifier with a paraphrase or a role name, do not move it to another file, do not translate it to another host, and do not introduce a host term that the upstream file lacks.
- Model routing. The `pstack-models.mdc` role lines direct the model choice. Keep every role-line name, default slug, and fallback order verbatim where upstream states it.

## 11. Citations and anchors

Other files cite parts of a file by name, letter, and number. Citations are never rewritten, so their targets must not move.

- Keep every upstream heading text, phase letter and name, and step number. A changed heading level is fine. A changed text is not.
- Numbered step headings that other files cite ("step 5" of **setup-pstack**, cited by the Claude Code adapter) keep their numbers and titles. The rule shape code block and every default slug stay inside `skills/setup-pstack/SKILL.md`, because upstream's documentation checker reads them there.
- Numbered rules that are stable ids (`unslop`: "Rule numbers are stable ids that other skills cite. A removed rule leaves a gap.") keep their numbers and gaps.
- Words are anchors too. **interrogate** says "In place of the arena task and rationale", which resolves against the words "the task" and "a short rationale" in arena's Phase B. Keep such words.
- When you cite another file, use exactly the words upstream uses. Do not cite another file's ALPS section names.
- No heading you add may equal an upstream heading or a pstack term of art.
- If the structure of your converted file changes how one of its parts must be found, record the old and new name under `anchors_kept`.

## 12. Tools

Bundled scripts are established processing and stay byte-identical. For each tool operation that a description directs an agent to use, the agent must be able to find the facts design principles section 4 requires. Put them in a tool-use reference inside the owning skill: `references/tool-use.md` when the skill has one tool, `references/tool-use-<tool>.md` when it has several. Use these sections, in this order, and omit one only if it would be empty:

`## Responsibility and limits`, `## Invocation`, `## Returned information`, `## Dependencies and environment`, `## Success, failure, and incomplete results`, `## Effects on external state`, `## Reproducibility`, `## What a result does not establish`.

- Write it as plain tool documentation, not as a Process Description. State only what a user of the tool needs.
- A tool facts report from an analysis of the source code and trial runs is supplied. Use it, and check each fact you state against the script itself. Do not copy the report's commentary on documentation gaps.
- Do not move sentences out of the description into the reference. The description keeps what upstream tells the agent. The reference adds what upstream does not tell.
- In the description, point to the reference from `## Enablers` with one sentence: "`<script path>` is bundled with this skill. Its invocation, results, exit statuses, dependencies, effects, and limits are in [tool use]\(references/<file>)." For a playbook the link is relative to the playbook file.
- Where the tool's verified behavior differs from what the upstream description says about it: state the verified behavior in the reference, plainly and without commentary on upstream; do **not** rewrite the upstream instruction to match and do not add new duties to the description; record the difference under `findings` with its effect.
- The reference is an addition with no upstream counterpart. Record it under `added`.

## 13. Links

Every relative Markdown link must resolve to a file inside the target tree. The tree contains the README and the guide text but not the guide's images, `assets/`, or the statechart tool's `scripts/test/`. A relative link to a file that is not in the tree is replaced by that file's URL at the pinned commit: `https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/<path>`. Leave absolute URLs as upstream wrote them. Do not add links.

## 14. Length and wording

- A converted file should be about as long as its upstream file plus its Purpose, Outcomes, headings, and the fixed sentences. If it is much longer, you added content: remove it. `poteto-mode/SKILL.md` and the principle files are read by every delegate, so every added word there costs context in every run.
- Do not explain ALPS, the conversion, or the Framework inside converted files. No provenance headers, no "converted from" lines. That information lives in the conversion record.
- Text you add follows pstack's own writing rules: short declarative sentences, no em or en dashes, no colon used as a connector, one name per thing, upstream's technical terms.
- One blank line between blocks, no trailing whitespace, a single newline at end of file.

## 15. Amendments after the first conversion pass

These refine the sections above. Where they differ, these govern.

1. **Governing sentence.** The ordered variant now reads: "The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints." This wording is already in the files. Do not change it back. Use the ordered variant in any file whose `## Constraints` states an order (including a principle whose source orders its instructions, such as "Reproduce first"), and the "set no order" variant in every other file. The two must agree with what `## Constraints` says.
2. **Scope of the order sentence.** The listed order is the default only for what upstream itself numbered or lettered. Where upstream numbered only the steps that are now Activity headings and the Tasks under them come from unnumbered paragraphs or bullets, write: "Unless a Task states otherwise, work the Activities in the order listed. Within an Activity, Tasks may be worked in any order unless one states otherwise. These dependencies are required." and then the dependencies, if any. Never let numbers that the conversion added create an order that upstream does not state.
3. **Outcomes on every permitted path.** An Outcome must be able to hold on every path upstream allows: a stop path ("Stop" when a precondition fails), a skip condition, an optional step, a permitted exception, a fallback. If a result holds only on some paths, state the condition in the Outcome ("Where ...") or leave it out. An Outcome must not turn an optional step into a required result, an instruction to apply another skill into the absolute absence of what that skill removes, or a "report the gap" rule into a pass.
4. **Bundled agent.** A description that uses a bundled agent names it once under `## Enablers`: "`<agent name>` is the subagent that `agents/<file>.md` defines. Its rules are in that file." Record it under `added`.
5. **A heading that carries the instruction.** An upstream heading that is itself the instruction ("### 1. Detect available models", "Pick the mode first (Diátaxis)") stays as the heading. The text under it need not restate it.
6. **Statements kept whole.** Where splitting an upstream paragraph or section between two element sections would separate a rule from the words it depends on, keep it whole under the element of its dominant function.
