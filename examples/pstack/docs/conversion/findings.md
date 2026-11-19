# Observations about the source text

[Conversion guide](README.md)

While rewriting each pstack file, the conversion recorded places where the upstream text leaves an agent or an evaluator without a clear answer. The conversion did not repair them. It kept the upstream wording and listed them here.

Read this list with its limits in mind.

- Each observation was checked by a second reader against the upstream file. Only observations that the second reader found true of the text, material to what an agent does or how success is judged, and supported by quoted words were kept. The quotes below were also matched against the upstream files mechanically.
- The second reader kept 173 observations and set aside 565 as untrue, immaterial, unsupported, duplicate, or about the conversion's own choices.
- These are readings of a text. The author may intend some of them, and an agent may resolve others from context. None has been confirmed by the author.
- Line numbers refer to the upstream file at the pinned commit. Each path links to that file.

| Kind of observation | Count |
| --- | --- |
| [Two places state the same rule differently](#two-places-state-the-same-rule-differently) | 44 |
| [A statement can be read two ways](#a-statement-can-be-read-two-ways) | 65 |
| [Success is stated as an artifact or a step](#success-is-stated-as-an-artifact-or-a-step) | 12 |
| [An order is implied or in conflict](#an-order-is-implied-or-in-conflict) | 7 |
| [A state-changing action lacks a stated condition](#a-state-changing-action-lacks-a-stated-condition) | 18 |
| [The tool behaves differently from the text](#the-tool-behaves-differently-from-the-text) | 11 |
| [The work depends on something that is not bundled](#the-work-depends-on-something-that-is-not-bundled) | 11 |
| [A citation does not resolve](#a-citation-does-not-resolve) | 2 |
| [Shared information has unstated readers or writers](#shared-information-has-unstated-readers-or-writers) | 2 |
| [The objective is not stated](#the-objective-is-not-stated) | 1 |

## Two places state the same rule differently

Two upstream files, or two places in one file, state the same rule, list, limit, or trigger in different words. An agent that reads both cannot follow both exactly.

### `agents/comment-sicko.md`

**README and guide call Comment Sicko read-only; its definition deletes comments in files.** A user who invokes the agent directly, as the README allows, or a host that configures it read-only, expects no edits; the definition and no-comments step 2 assume it deletes comments in the working tree and leaves a diff to inspect and revert.

- [`README.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/README.md#L220), line 220: "pstack also ships [Comment Sicko]\(./agents/comment-sicko.md), a read-only comment reviewer available as `subagent_type: "comment-sicko"`."
- [`docs/guide/05-build-and-clean.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/docs/guide/05-build-and-clean.md#L77), line 77: "spawns [Comment Sicko]\(../../agents/comment-sicko.md), a read-only reviewer with a short keep list"
- [`agents/comment-sicko.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/agents/comment-sicko.md#L30), line 30: "I touch comments and identify refactor targets. I never write application code."
- [`agents/comment-sicko.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/agents/comment-sicko.md#L32), line 32: "Report only. Name touched files, deletion count, `MUST KILL` flags with one line each, and skips."
- [`skills/no-comments/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/no-comments/SKILL.md#L20), line 20: "Inspect its report and diff. Reject application-code edits, scope escapes, exception-protected deletions"

### `automations/benny/skills/reproduce-and-fix-issues/SKILL.md`

**Verify-mode status labels are absent from the skill's list and the configuration.** The skill requires configured status strings, but no configured or listed string exists for a verified or reproduced-but-not-fixed result, and the configuration supplies emoji rather than text strings; a verify-mode run must invent a status.

- [`automations/benny/skills/reproduce-and-fix-issues/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/SKILL.md#L111), line 111: "Use the configured plain Unicode status strings. Keep status text short:"
- [`automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md#L67), line 67: "Mark operations status as verified."
- [`automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md#L77), line 77: "Mark operations status as reproduced but not fixed."
- [`automations/benny/templates/configuration.example.yaml`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/templates/configuration.example.yaml#L60), line 60: "status_emoji:"

### `automations/benny/skills/reproduce-and-fix-issues/references/control-adapter.md`

**Adapter setup check gates enabling repro, but setup-benny's enable gates omit it.** An agent following setup-benny's explicit gates (capability confirmation and the seven thread-safety checks) may enable the repro automation without running the nine-step adapter check that the contract requires before enabling.

- [`automations/benny/skills/reproduce-and-fix-issues/references/control-adapter.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/references/control-adapter.md#L157), line 157: "Before enabling the repro automation, run one harmless adapter check:"
- [`automations/benny/skills/reproduce-and-fix-issues/references/control-adapter.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/references/control-adapter.md#L169), line 169: "Enable repro work only when all nine steps succeed and no source-channel Slack post is involved."
- [`automations/benny/skills/setup-benny/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/setup-benny/SKILL.md#L154), line 154: "Confirm that the named skill can:"
- [`automations/benny/skills/setup-benny/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/setup-benny/SKILL.md#L265), line 265: "Enable normal traffic only after all seven checks pass."

### `automations/benny/skills/setup-benny/SKILL.md`

**Repro trigger is fixed in the setup skill but selectable in FOR_AGENTS.md.** The file the skill names as the primary intent source permits choosing another trigger for the repro automation, while the skill's complete repro intent fixes the trigger and no step offers a choice. An agent cannot tell whether a different trigger may be configured.

- [`automations/benny/FOR_AGENTS.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/FOR_AGENTS.md#L18), line 18: "trigger: i want this automation to start from the same new top-level report, or another supported trigger chosen during setup, then wait for the trusted triage marker in the original thread."
- [`automations/benny/skills/setup-benny/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/setup-benny/SKILL.md#L170), line 170: "Read `../../FOR_AGENTS.md` from the copied pack as the primary user-intent source for either path."
- [`automations/benny/skills/setup-benny/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/setup-benny/SKILL.md#L203), line 203: "Trigger on the same new top-level reports in the configured source Slack channel."

### `automations/benny/skills/triage-issue-reports/SKILL.md`

**Evidence bar for a regression-author ping differs between triage, routing, and setup.** An agent cannot tell whether a likely author with strong evidence suffices or a confirmed author is required, nor how a regression author found in history can also be named in the routing map; pings may be sent or withheld differently across runs.

- [`automations/benny/skills/triage-issue-reports/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/triage-issue-reports/SKILL.md#L122), line 122: "The item is a feature request that needs owner input, or recent history identifies a likely regression author with strong evidence."
- [`automations/benny/skills/triage-issue-reports/references/routing.example.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/triage-issue-reports/references/routing.example.md#L48), line 48: "- "confirmed-regression-author""
- [`automations/benny/skills/setup-benny/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/setup-benny/SKILL.md#L146), line 146: "Allow a ping only for a configured feature owner or a confirmed likely regression author."
- [`automations/benny/skills/triage-issue-reports/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/triage-issue-reports/SKILL.md#L120), line 120: "The routing map explicitly names the owner."

**Routing example offers a fallback destination that the triage rules never use.** When an operator fills `fallback.destination`, the triage skill gives no rule for it; an agent may either route unmatched reports there or say the owner is unclear, and the operator's configuration may silently have no effect.

- [`automations/benny/skills/triage-issue-reports/references/routing.example.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/triage-issue-reports/references/routing.example.md#L56), line 56: "Leave `fallback.destination` empty unless one team accepts all unmatched reports."
- [`automations/benny/skills/triage-issue-reports/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/triage-issue-reports/SKILL.md#L115), line 115: "If no route matches, say the owner is unclear. Do not guess."

### `skills/architect/SKILL.md`

**figure-it-out says architect runs arena; architect runs arena only conditionally.** An agent following figure-it-out expects an arena run for every one-way-door decision and treats a further arena as redundant, while architect sketches alone unless the design is large or contested, so the arena step can be skipped by both.

- [`skills/figure-it-out/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/figure-it-out/SKILL.md#L30), line 30: "For one-way-door design decisions, run the **architect** skill (it runs **arena**)."
- [`skills/architect/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/architect/SKILL.md#L11), line 11: "For a large or contested design, run the **arena** skill instead of sketching alone."

### `skills/automate-me/SKILL.md`

**Evidence bar for codifying a preference is stated with different force.** Step 1 permits keeping a lone signal ("usually"), the Guardrail requires multiple instances, and its "it" may mean any preference or only a contradicted one. An agent cannot tell whether a preference seen once, or given only in the user's step-2 answers, may go into the skill.

- [`skills/automate-me/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/automate-me/SKILL.md#L40), line 40: "Patterns seen in 2+ slices are high-confidence. Lone signals are weak and usually get dropped."
- [`skills/automate-me/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/automate-me/SKILL.md#L87), line 87: "A preference stated once and contradicted another time is noise. Require multiple instances before codifying it."
- [`skills/automate-me/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/automate-me/SKILL.md#L44), line 44: "Mining misses intent that hasn't come up yet."

### `skills/benchmark-checklist/SKILL.md`

**Guide states fewer and broader inconclusive triggers than the skill.** A reader judging a returned verdict by the guide would not expect inconclusive when errors or work-happened were unchecked, and would expect it for a missing limiter even when no difference is claimed.

- [`docs/guide/06-verify-and-ship.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/docs/guide/06-verify-and-ship.md#L49), line 49: "It says inconclusive when it can't name the limiter or a side ran untuned."
- [`skills/benchmark-checklist/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/benchmark-checklist/SKILL.md#L33), line 33: "Call the verdict inconclusive when you claim a difference but cannot name the limiter, when a side ran untuned, or when you could not check questions 4 and 7."

### `skills/blast-radius/SKILL.md`

**Number of safety facts to prove differs: one, one or two, or each.** An agent cannot tell whether a change resting on two facts needs both proven and reported, or only one in the single hand-back slot, and an evaluator cannot tell which count the Reply must satisfy.

- [`skills/blast-radius/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/blast-radius/SKILL.md#L17), line 17: "Find the one or two facts the whole thing depends on and prove them by running code."
- [`skills/blast-radius/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/blast-radius/SKILL.md#L21), line 21: "For each fact the change's safety depends on, get it as far down this list as is cheap, and say where it stopped."
- [`skills/blast-radius/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/blast-radius/SKILL.md#L37), line 37: "5. Prove the one fact."
- [`skills/blast-radius/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/blast-radius/SKILL.md#L50), line 50: "**Reply:** the writeup above, with the one safety fact either proven or marked unproven."

### `skills/correct/SKILL.md`

**Description repeats the whole skill on every correction; body escalates only on repeats.** On a first-time correction, one text calls for repeating the work (mining history, fixing classes, proving checks), while the body calls only for fixing the mistake and adding a rule. An agent cannot tell which response is required, so two agents can do very different amounts of repository change.

- [`skills/correct/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/correct/SKILL.md#L3), line 3: "Repeat this each time the operator corrects you."
- [`skills/correct/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/correct/SKILL.md#L30), line 30: "When the operator corrects you, fix the mistake and add the rule. If the rule was already there and nothing enforces it, that's a repeat, so fix it at the highest level in the same change."
- [`skills/correct/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/correct/SKILL.md#L15), line 15: "A class counts once it has happened twice."

### `skills/create-formal-verification-skill/SKILL.md`

**Citing skill says /statechart reads checker results and charts every passing check.** The statechart skill takes a spec and config and runs TLC itself; it does not read another checker's result, and above 500 states a passing check yields no chart. A generated skill following the citing text can direct agents to feed it checker output or to expect a chart that is not produced.

- [`skills/create-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/create-formal-verification-skill/SKILL.md#L35), line 35: "tell the next agent to read every result with the pstack [`/statechart`]\(../statechart/SKILL.md) skill."
- [`skills/create-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/create-formal-verification-skill/SKILL.md#L35), line 35: "When the check passes, `/statechart` draws a chart of how the system moves between states."
- [`skills/statechart/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/SKILL.md#L13), line 13: "Write a TLA+ spec and its config. Then run:"
- [`skills/statechart/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/SKILL.md#L74), line 74: "Above that, the chart draws only the paths to the rules that break, and when no rule breaks, the command writes no `chart.mmd`."

### `skills/figure-it-out/SKILL.md`

**Routing condition for figure-it-out differs between its body and poteto-mode.** For large or unattended work that a playbook such as Autonomous run also matches, poteto-mode routes to figure-it-out while figure-it-out's own body applies only when no playbook matches, so an agent cannot tell which governs.

- [`skills/figure-it-out/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/figure-it-out/SKILL.md#L9), line 9: "When the task matches no playbook, design one."
- [`skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/SKILL.md#L108), line 108: "Large, cross-cutting, or unattended work, or a task no playbook fits, routes to the **figure-it-out** skill."
- [`skills/poteto-help/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-help/SKILL.md#L111), line 111: "`/figure-it-out` designs one rigorous run. The Autonomous run playbook drives one task to a finish condition."

### `skills/how/SKILL.md`

**Description adds placement and ownership questions the body and fixed brief do not address.** For a trigger such as "where should this live", the fixed brief asks for an architectural explanation, not a placement answer. An agent following the body may return an explanation that does not answer the question that invoked the skill.

- [`skills/how/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/how/SKILL.md#L3), line 3: "code walkthroughs before changing something, and placement / ownership / layering questions"
- [`skills/how/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/how/SKILL.md#L9), line 9: "Explore the codebase to answer "how does X work?" questions."
- [`skills/how/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/how/SKILL.md#L17), line 17: "You are writing an architectural explanation for a senior engineer."

### `skills/interrogate/SKILL.md`

**Interrogate's Output omits the dropouts that its reused arena Phase B requires noting.** Arena's output lists dropouts but interrogate's fixed report has no item for an adversary that returned nothing or ran on a substituted model, so a reader of "no verified findings" cannot tell that fewer adversaries ran.

- [`skills/interrogate/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/interrogate/SKILL.md#L17), line 17: "Run Phase A steps 3 and 4 and Phase B of the **arena** skill, with four changes."
- [`skills/arena/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/arena/SKILL.md#L24), line 24: "If a candidate produces no output, proceed with N-1 and note the dropout."
- [`skills/interrogate/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/interrogate/SKILL.md#L31), line 31: "**Dropped**: for each adversary, the count of dropped findings and why."
- [`skills/arena/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/arena/SKILL.md#L48), line 48: "what was rejected and why, any convergence or dropouts, and the verification result."

### `skills/maintain-formal-verification-skill/SKILL.md`

**Outcome rule requires one outcome per check, then allows updated and bug together.** An agent cannot tell whether to report one label or two for an updated check that then fails, and 'updated' is defined as passing, so the combined case contradicts its own definition. An evaluator cannot judge a report's outcome labels as right or wrong.

- [`skills/maintain-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-formal-verification-skill/SKILL.md#L13), line 13: "Give each check one outcome, and say which:"
- [`skills/maintain-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-formal-verification-skill/SKILL.md#L16), line 16: "**updated**: the code changed, the verification now describes the new code, and the check passes."
- [`skills/maintain-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-formal-verification-skill/SKILL.md#L20), line 20: "A check can be both updated and bug: the update makes the verification describe the code again, and then the property fails on it."

### `skills/maintain-verification-skill/SKILL.md`

**Description and step 4 state different live session models.** For short-lived CLIs the description promises one session for all features while the body requires a fresh session per drive; an agent or host reading only the description expects the wrong model.

- [`skills/maintain-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-verification-skill/SKILL.md#L3), line 3: "one live session driving every feature"
- [`skills/maintain-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-verification-skill/SKILL.md#L33), line 33: "follow the verification skill's own launch model — one long-lived instance driven serially for servers and UIs, or a fresh isolated session per drive for short-lived CLIs (the skill's Launch section decides, not this one)"

### `skills/no-comments/SKILL.md`

**no-comments keep criterion is narrower than Comment Sicko's five-item keep list.** Read literally, the lead deletes keeps the agent's list protects, such as public API doc comments or `// prettier-ignore`, while the same step tells it to reject exception-protected deletions; the two files cannot both be followed for those comments.

- [`skills/no-comments/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/no-comments/SKILL.md#L20), line 20: "A keep survives only with proof it is about something we cannot change."
- [`skills/no-comments/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/no-comments/SKILL.md#L20), line 20: "If a keep is refuted or still ambiguous, delete it."
- [`skills/no-comments/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/no-comments/SKILL.md#L23), line 23: "Leave keeps about things we cannot change."
- [`agents/comment-sicko.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/agents/comment-sicko.md#L18), line 18: "`// prettier-ignore`. Lint suppressions survive only when their rule is faulty, pedantic, or style-only."
- [`agents/comment-sicko.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/agents/comment-sicko.md#L19), line 19: "Doc comments that define a public API contract."

### `skills/poteto-help/SKILL.md`

**Clarifying-question options omit the Playbooks and principles section yet restrict the answer.** The five options cover five of the six answer sections, and "answer only the section they pick" then bars the agent from the Playbooks and principles section (trigger phrases, planning, principles) for a user whose need was unclear, even when "Pick a skill" defers principles to it.

- [`skills/poteto-help/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-help/SKILL.md#L17), line 17: "If the need is still unclear, ask one multiple-choice question with these options, then answer only the section they pick:"
- [`skills/poteto-help/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-help/SKILL.md#L21), line 21: "- Pick a skill for a situation"
- [`skills/poteto-help/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-help/SKILL.md#L119), line 119: "## Playbooks and principles"
- [`skills/poteto-help/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-help/SKILL.md#L103), line 103: "The `principle-*` directories are covered under principles below."

### `skills/poteto-mode/SKILL.md`

**Three files give different stop lists for outgoing messages.** A team-chat post or ticket update proceeds without asking under Autonomy, but needs a stop under worker.md and confirmation under the principle the Principles index points to; the texts do not say which governs or whether the lead and its workers are meant to differ.

- [`skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/SKILL.md#L76), line 76: "Reversible work and external actions (team chat, ticket updates, kicking off evals) proceed without asking."
- [`skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/SKILL.md#L78), line 78: "**Always pause** for irreversible writes: force-push to shared branches, deploys, data deletion, customer messages."
- [`skills/poteto-mode/worker.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/worker.md#L7), line 7: "Stop only for a deploy, deleted data, a force-push to a shared branch, or a message to someone outside the run."
- [`skills/principle-never-block-on-the-human/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-never-block-on-the-human/SKILL.md#L13), line 13: "Irreversible actions (force-push, delete production data, send external messages) still require confirmation."

### `skills/poteto-mode/playbooks/autopilot-stack.md`

**Rebased PR with unchanged patch-id: kept verdict versus a single verifier.** Autopilot-stack declares only step 3 as its exception, while Autopilot-full step 4 gives every rebase a verifier, so an agent cannot tell whether a restacked PR with an unchanged patch-id needs a verifier at its new head.

- [`skills/poteto-mode/playbooks/autopilot-stack.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/autopilot-stack.md#L6), line 6: "A new head on the lower PR restacks the PRs above it, and a PR whose `git patch-id` the restack leaves unchanged keeps its verdict."
- [`skills/poteto-mode/playbooks/autopilot-stack.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/autopilot-stack.md#L6), line 6: "This is the one exception to step 3."
- [`skills/poteto-mode/playbooks/autopilot-full.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/autopilot-full.md#L14), line 14: "A rebase, a merge-conflict resolution, or a minor fix gets a single verifier at the new head, and a wording-only change gets none."
- [`skills/poteto-mode/playbooks/autopilot-full.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/autopilot-full.md#L5), line 5: "The patch-id rule in `playbooks/shipping.md` can carry a lane's result"

### `skills/poteto-mode/playbooks/babysit.md`

**Babysit and bugbot-triage route security, auth, billing, and data findings differently.** A plausible auth or billing finding is `fix` under bugbot-triage line 9, but `ask` under its line 11 and escalate under Babysit, which cites that reference. An agent can fix it without asking or stop to ask, and both readings follow a cited text.

- [`skills/poteto-mode/playbooks/babysit.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/babysit.md#L9), line 9: "fix real findings, dismiss noise with a concrete disproof, escalate billing, data, auth, and security."
- [`skills/poteto-mode/references/bugbot-triage.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/references/bugbot-triage.md#L9), line 9: "`fix`: The comment identifies a plausible correctness, security, privacy, data loss, auth, billing, migration, idempotency, race, or shipped-behavior issue. Fix it in the lowest owning PR"
- [`skills/poteto-mode/references/bugbot-triage.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/references/bugbot-triage.md#L11), line 11: "`ask`: The comment is novel, high-severity, security/privacy/data-related, or ambiguous. Ask the user instead of guessing."

### `skills/poteto-mode/playbooks/hillclimb.md`

**Hillclimb defines its own decision-log file and columns, conflicting with show-me-your-work's format.** An agent running Hillclimb cannot follow both files: the playbook asks for a nine-column `decision.tsv` while the skill it invokes fixes six columns, a `decisions.tsv` name, and a helper that writes only six-field rows.

- [`skills/poteto-mode/playbooks/hillclimb.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/hillclimb.md#L9), line 9: "Open the decision log via the **show-me-your-work** skill. A `decision.tsv`, one row per attempt: id, hypothesis, change, before, after, delta, tests, verdict (kept or reverted), note."
- [`skills/show-me-your-work/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/show-me-your-work/SKILL.md#L82), line 82: "Reference it by name and let it own the format. Don't restate the columns."
- [`skills/show-me-your-work/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/show-me-your-work/SKILL.md#L15), line 15: "Copy `references/decision-log-template.tsv` (the header row) to start a clean log. Columns:"
- [`skills/show-me-your-work/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/show-me-your-work/SKILL.md#L38), line 38: "Use the helper `scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>`."

**Hillclimb's decision log name and columns differ from show-me-your-work's format and helper.** An agent cannot follow both files: the cited skill and its helper produce a six-column `decisions.tsv`, while Hillclimb asks for a nine-column `decision.tsv` that `log.sh` cannot write (it exits 1 unless given exactly six arguments). Which file name and columns a run's log, and its reply's path, must use is left to the agent.

- [`skills/poteto-mode/playbooks/hillclimb.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/hillclimb.md#L9), line 9: "Open the decision log via the **show-me-your-work** skill. A `decision.tsv`, one row per attempt: id, hypothesis, change, before, after, delta, tests, verdict (kept or reverted), note."
- [`skills/show-me-your-work/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/show-me-your-work/SKILL.md#L46), line 46: "Keep it at `decisions.tsv` in the work dir"
- [`skills/show-me-your-work/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/show-me-your-work/SKILL.md#L82), line 82: "Reference it by name and let it own the format. Don't restate the columns."
- [`skills/show-me-your-work/scripts/log.sh`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/show-me-your-work/scripts/log.sh#L6), line 6: "if [ "$#" -ne 6 ]; then"
- [`skills/show-me-your-work/scripts/log.sh`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/show-me-your-work/scripts/log.sh#L22), line 22: "printf 'ts\tphase\tdecision\twhy\tevidence\tresult\n' >> "$logfile""

**Step 5 accepts only metric gains; step 6 keeps simplifications that merely hold.** A change that simplifies code without moving the metric past noise must be reverted under step 5 and kept under step 6. The agent's keep-or-revert verdict, and an evaluator's judgment of whether the loop rule was followed, depend on which statement is taken to govern.

- [`skills/poteto-mode/playbooks/hillclimb.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/hillclimb.md#L14), line 14: "Accept only when the metric moves past noise and the gate stays green. Otherwise revert the change in full."
- [`skills/poteto-mode/playbooks/hillclimb.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/hillclimb.md#L17), line 17: "Correctness and simplicity outrank the number. Revert a win that breaks behavior, and keep a simplification that holds the number"

### `skills/poteto-mode/playbooks/multi-phase-plan.md`

**Opening a PR claims to end every playbook; Multi-phase plan stops without one.** The two files cannot both be followed literally: an agent reading Opening a PR may open a PR for the plan, while Multi-phase plan ends at handing back the plan path. Several other playbooks (for example Investigation) also do not invoke it, so the "every other playbook" scope is not reliable.

- [`skills/poteto-mode/playbooks/opening-a-pr.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/opening-a-pr.md#L3), line 3: "Invoked at the end of every other playbook."
- [`README.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/README.md#L91), line 91: "invoked at the end of every other playbook."
- [`skills/poteto-mode/playbooks/multi-phase-plan.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/multi-phase-plan.md#L3), line 3: "The plan is the deliverable. Do not implement."
- [`skills/poteto-mode/playbooks/multi-phase-plan.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/multi-phase-plan.md#L9), line 9: "5. Hand back the plan path and stop. Execution starts on the operator's explicit go."

### `skills/poteto-mode/playbooks/opening-a-pr.md`

**Opening a PR claims every playbook ends with it; Eval and Prototype do not.** Eval and Prototype have no "Run **Opening a PR**" step, and Prototype says its output is not shippable code, yet Opening a PR states it is invoked at the end of every other playbook. Whether an Eval or Prototype run is complete without a PR is judged differently depending on which file is read.

- [`skills/poteto-mode/playbooks/opening-a-pr.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/opening-a-pr.md#L3), line 3: "Invoked at the end of every other playbook."
- [`skills/poteto-mode/playbooks/eval.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/eval.md#L25), line 25: "**Reply:** variant under test, rubric, per-candidate notes, judge's verdict, your synthesis, and a recommendation for whether to promote the variant."
- [`skills/poteto-mode/playbooks/prototype.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/prototype.md#L12), line 12: "The output is the decision plus the throwaway artifact, not shippable code."

**Opening a PR claims to follow every playbook; Investigation and Pause safely exclude PRs.** The trigger for opening a PR is stated one way in opening-a-pr.md and the README and the opposite way in two playbooks. An agent that takes line 3 as the condition of application could open a PR at the end of an investigation or a pause.

- [`skills/poteto-mode/playbooks/opening-a-pr.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/opening-a-pr.md#L3), line 3: "Invoked at the end of every other playbook."
- [`skills/poteto-mode/playbooks/investigation.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/investigation.md#L12), line 12: "No PR, no babysit, no `architect` unless the investigation precedes a code change."
- [`skills/poteto-mode/playbooks/pause-safely.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/pause-safely.md#L6), line 6: "No PR and no push unless you already had one out."
- [`README.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/README.md#L91), line 91: "invoked at the end of every other playbook."

### `skills/poteto-mode/playbooks/session-pickup.md`

**Re-verification is forbidden in step 3 and required in step 5.** No line separates the forbidden re-run from the required check on the real artifact, and the Reply softens the prohibition to "ideally", so an agent cannot tell how much prior verification to repeat and an evaluator cannot judge a re-run check as compliant or not.

- [`skills/poteto-mode/playbooks/session-pickup.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/session-pickup.md#L7), line 7: "do not re-run the prior repro or redo completed work. A "let me verify from scratch" pass means you're treating the trail as untrustworthy when it's authoritative."
- [`skills/poteto-mode/playbooks/session-pickup.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/session-pickup.md#L9), line 9: "Verify the inherited claims against the original goal on the real artifact (the **principle-prove-it-works** skill). A passing prior self-report is not the proof."
- [`skills/poteto-mode/playbooks/session-pickup.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/session-pickup.md#L11), line 11: "what you inherited vs redid (ideally nothing redone)"

### `skills/principle-attack-the-premise/SKILL.md`

**Description gates only fixes assuming the premise; body gates any next fix.** A fix built on a different premise is allowed without testing under the description (also repeated in the poteto-mode index) but forbidden under the body, so whether the agent may proceed depends on which text it follows.

- [`skills/principle-attack-the-premise/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-attack-the-premise/SKILL.md#L3), line 3: "Write the premise down and test it directly before you write another fix that assumes it."
- [`skills/principle-attack-the-premise/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-attack-the-premise/SKILL.md#L15), line 15: "Do not start the next fix before the premise is written down and tested."
- [`skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/SKILL.md#L40), line 40: "Write the premise down and test it directly before you write another fix that assumes it."

### `skills/principle-encode-lessons-in-structure/SKILL.md`

**poteto-mode index trigger omits the recurring-correction case stated in the skill description.** The skill sets disable-model-invocation and poteto-mode says each index entry names when the principle applies, so an agent routed by the index may not apply it on a recurring correction.

- [`skills/principle-encode-lessons-in-structure/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-encode-lessons-in-structure/SKILL.md#L3), line 3: "Apply when you catch yourself writing the same instruction a second time, or notice a recurring correction."
- [`skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/SKILL.md#L72), line 72: "**Encode Lessons in Structure.** You catch yourself writing the same instruction a second time."

### `skills/principle-exhaust-the-design-space/SKILL.md`

**poteto-mode index trigger omits the leaf's feel-dependent product-design case and codebase scope.** The index is the stated source of when each principle applies, and the leaf is read only once a principle is chosen. An agent selecting from the index will not apply this principle to feel-dependent product decisions, and reads 'no precedent' without the leaf's 'in the codebase' scope.

- [`skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/SKILL.md#L33), line 33: "Read the leaf skill in full for any principle you apply. Each entry names when it applies."
- [`skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/SKILL.md#L45), line 45: "A novel interaction or architectural decision with no precedent. Build 2-3 competing prototypes and compare before committing."
- [`skills/principle-exhaust-the-design-space/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-exhaust-the-design-space/SKILL.md#L9), line 9: "It also applies to product design decisions where user experience depends on feel, not logic."

### `skills/principle-model-the-domain/SKILL.md`

**Refactoring playbook restates the leaf's exception with fewer conditions and stronger force.** Code that is clear and local but likely to grow stays boring under the playbook yet should be modeled under the leaf the playbook cites; the leaf's 'distrust' becomes a 'must' in the playbook. An agent following both gets different decisions for the same code.

- [`skills/principle-model-the-domain/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-model-the-domain/SKILL.md#L13), line 13: "Keep boring code when the shape is clear, local, and unlikely to grow, and distrust an abstraction that adds indirection without removing branches or invalid states."
- [`skills/poteto-mode/playbooks/refactoring.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/refactoring.md#L8), line 8: "Name the structure the code is missing per **principle-model-the-domain**. Boring code stays when the shape is already clear and local. The reshape must delete branches or invalid states, not add indirection."

### `skills/principle-outcome-oriented-execution/SKILL.md`

**Planned intermediate breakage conflicts with sequence-verifiable-units' green-before-advancing rule for migrations.** In a planned migration both principles apply, and neither file says which governs or how declared breakage relates to the per-unit green check. An agent cannot tell whether it may advance past a planned red state.

- [`skills/principle-outcome-oriented-execution/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-outcome-oriented-execution/SKILL.md#L15), line 15: "Intermediate breakage is acceptable when it is planned, scoped, and reversible"
- [`skills/principle-outcome-oriented-execution/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-outcome-oriented-execution/SKILL.md#L18), line 18: "Use this for planned rewrites and migrations with explicit phase boundaries"
- [`skills/principle-sequence-verifiable-units/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-sequence-verifiable-units/SKILL.md#L9), line 9: "Order work as small units that each end in a state you can check, and do not advance until the current one is green."
- [`skills/principle-sequence-verifiable-units/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-sequence-verifiable-units/SKILL.md#L11), line 11: "In a sweep, migration, or run of similar edits, each unit is a bracket: known-good state, one change, run the check, proceed."

### `skills/recall/SKILL.md`

**Step 3 keeps raw transcripts in subagents; step 5 says read the full transcript.** Step 5 is addressed to the main agent, so it can be read as permitting the main thread to load a full transcript, contrary to step 3, or as an instruction to delegate. "Trimmed local copy" is not defined.

- [`skills/recall/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/recall/SKILL.md#L19), line 19: "The raw transcripts stay in the subagents. The main thread gets only their findings."
- [`skills/recall/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/recall/SKILL.md#L21), line 21: "When the answer hinges on what an agent actually did (the tools it ran, files it read, errors it hit), read the full transcript, not just a trimmed local copy."

### `skills/setup-pstack/SKILL.md`

**Re-run keeps only family, list, or alias changes; guide and README say any differing model.** A role the user set to a different effort of the default family (for example `claude-opus-5-5-high-fast` for `bug-fix`) is reset to the budget target by step 3(b), while the guide and README promise it is kept. An evaluator or user judging a re-run against the guide reaches a different verdict than one judging against the skill.

- [`skills/setup-pstack/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/setup-pstack/SKILL.md#L38), line 38: "Build the working table from the skill defaults, and on a re-run keep any role you changed by family, list, or alias (`inherit-parent`, `auto`)."
- [`skills/setup-pstack/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/setup-pstack/SKILL.md#L38), line 38: "Set the effort token of every real slug in the role, panel entries included, to the role's target."
- [`docs/guide/01-setup.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/docs/guide/01-setup.md#L29), line 29: "A rerun of `/setup-pstack` keeps any role whose model differs from the default."
- [`README.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/README.md#L280), line 280: "keeps any other role whose model differs from the default"

### `skills/sharpen/SKILL.md`

**The stop-after-rewrite boundary appears in poteto-help but not in sharpen.** An agent working from sharpen alone has no statement that it must stop after returning the rewritten prompt, and may go on to perform the task that poteto-help says sharpen does not do.

- [`skills/poteto-help/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-help/SKILL.md#L70), line 70: "It returns the prompt and doesn't do the task"
- [`skills/sharpen/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/sharpen/SKILL.md#L14), line 14: "Then rewrite my prompt to ask for exactly that."

### `skills/tdd/SKILL.md`

**Description skips the skill for impractical tests; the body routes them to a fallback.** For an expensive or unclear test path, an agent reading the description does not apply the skill, while one reading the body applies its fallback check and the Final Response report; the two give different work and different evidence for the same case.

- [`skills/tdd/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/tdd/SKILL.md#L3), line 3: "Skip when the test path is unclear, expensive, integration-heavy, or not requested."
- [`skills/tdd/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/tdd/SKILL.md#L11), line 11: "skip adding a new test and use the closest useful verification instead."
- [`skills/tdd/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/tdd/SKILL.md#L22), line 22: "## If a Failing Test Is Impractical"
- [`skills/tdd/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/tdd/SKILL.md#L42), line 42: "If failing-before evidence could not be demonstrated, state why and describe the closest regression check used instead."

**The description's use and skip conditions overlap and give opposite answers.** A bug with an obvious cheap local test target that the user did not request a test for satisfies both the use clause and the skip clause (as does an explicit request on an expensive path), so an agent cannot tell from the trigger whether the skill applies.

- [`skills/tdd/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/tdd/SKILL.md#L3), line 3: "Use only when the user explicitly asks for TDD, a failing test, or a regression test, OR when the bug has an obvious cheap local test target."
- [`skills/tdd/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/tdd/SKILL.md#L3), line 3: "Skip when the test path is unclear, expensive, integration-heavy, or not requested."

**The fallback is named three ways, one of which does not require executability.** Under the second paragraph any useful verification, including a non-executable one, satisfies the fallback, while the If a Failing Test Is Impractical section requires an executable regression check; an agent and an evaluator can accept different evidence.

- [`skills/tdd/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/tdd/SKILL.md#L11), line 11: "use the closest useful verification instead."
- [`skills/tdd/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/tdd/SKILL.md#L24), line 24: "Use the closest executable regression check instead"
- [`skills/tdd/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/tdd/SKILL.md#L42), line 42: "describe the closest regression check used instead."

### `skills/teach/SKILL.md`

**First-reply opening and size stated differently in step 3 and the Reply line.** An agent can open with a definition or with the main point, and can stop after a sentence or two or give the what, how, why, and threads in the first reply. The two readings produce materially different first replies.

- [`skills/teach/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/teach/SKILL.md#L15), line 15: "Start with a plain definition."
- [`skills/teach/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/teach/SKILL.md#L15), line 15: "Give the smallest complete answer first, a sentence or two, not a dense paragraph, then stop. Add layers when they ask."
- [`skills/teach/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/teach/SKILL.md#L21), line 21: "Lead with the main point, then the plain account of what it is, how it works, and why, and the threads worth chasing with `how` or `why`."

### `skills/typescript-best-practices/SKILL.md`

**Frontmatter trigger and path globs imply automatic use; guide says it never loads itself.** Whether the rules apply to TypeScript work without a user command depends on whether the host honors `paths` despite `disable-model-invocation`, which the text does not settle. A user or agent cannot tell from upstream whether a session that touched `.ts` files without the command was governed by these rules.

- [`skills/typescript-best-practices/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/typescript-best-practices/SKILL.md#L3), line 3: "description: TypeScript best practices. Use when reading or editing any .ts or .tsx file."
- [`skills/typescript-best-practices/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/typescript-best-practices/SKILL.md#L4), line 4: "paths: ["**/*.ts", "**/*.tsx"]"
- [`skills/typescript-best-practices/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/typescript-best-practices/SKILL.md#L5), line 5: "disable-model-invocation: true"
- [`docs/guide/05-build-and-clean.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/docs/guide/05-build-and-clean.md#L55), line 55: "It doesn't load on its own, so type `/typescript-best-practices` when a task touches `.ts` or `.tsx` files."

**Table and patterns reference differ on discriminant name and on when casting is allowed.** In a codebase that uses a `type` or `tag` discriminant, the table reads as requiring `kind` while the reference allows keeping the existing name. A cast after runtime validation is allowed by the table but not by the reference's compile-time condition, so the agent and a reviewer can judge the same code differently.

- [`skills/typescript-best-practices/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/typescript-best-practices/SKILL.md#L14), line 14: "Model variants with a `kind` literal discriminant so impossible states can't be represented."
- [`skills/typescript-best-practices/references/patterns.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/typescript-best-practices/references/patterns.md#L43), line 43: "Pick one discriminant name (`kind`, `type`, `tag`) and stick to it."
- [`skills/typescript-best-practices/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/typescript-best-practices/SKILL.md#L20), line 20: "Every `as` is a runtime crash waiting. Cast only after validation."
- [`skills/typescript-best-practices/references/patterns.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/typescript-best-practices/references/patterns.md#L157), line 157: "Cast only after the type system has verified the claim."

### `skills/typescript-best-practices/references/patterns.md`

**Exhaustiveness prose says assign the discriminant; the code and table assign the value.** An agent following the prose writes `const _exhaustive: never = s.kind;`. Checked with tsc --strict, that line fails to compile even when every variant is handled (TS2339 on `never`), while the code shown and the table rule compile as intended.

- [`skills/typescript-best-practices/references/patterns.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/typescript-best-practices/references/patterns.md#L225), line 225: "In default arms, assign the discriminant to a `never`-typed local."
- [`skills/typescript-best-practices/references/patterns.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/typescript-best-practices/references/patterns.md#L236), line 236: "const _exhaustive: never = s;"
- [`skills/typescript-best-practices/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/typescript-best-practices/SKILL.md#L23), line 23: "Inline `const _exhaustive: never = x;` in default arms so the compiler errors when a new variant is added."

## A statement can be read two ways

The scope, force, referent, or condition of a statement admits two readings that lead to different actions, or a term is used without a definition.

### `agents/comment-sicko.md`

**Report term "skips" is undefined, and kept comments and their proof are not reported.** No-comments step 2 judges each keep by its proof, but unless "skips" means kept comments, the report names neither the keeps nor their exceptions, and unchanged comments do not appear in the diff, so the lead must rescan the scope.

- [`agents/comment-sicko.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/agents/comment-sicko.md#L32), line 32: "Report only. Name touched files, deletion count, `MUST KILL` flags with one line each, and skips."
- [`skills/no-comments/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/no-comments/SKILL.md#L20), line 20: "A keep survives only with proof it is about something we cannot change."
- [`skills/no-comments/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/no-comments/SKILL.md#L20), line 20: "If a keep is refuted or still ambiguous, delete it."

### `automations/benny/skills/reproduce-and-fix-issues/SKILL.md`

**"Repeat it twice" after a first run can mean two or three patched runs.** An agent may run the patched build twice or three times, and with three runs it cannot tell whether a Confirmed result requires all three to resolve the symptom or two.

- [`automations/benny/skills/reproduce-and-fix-issues/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/SKILL.md#L273), line 273: "Run the same real UI path."
- [`automations/benny/skills/reproduce-and-fix-issues/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/SKILL.md#L274), line 274: "Repeat it twice."
- [`automations/benny/skills/reproduce-and-fix-issues/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/SKILL.md#L222), line 222: "Both paths use the real UI twice."
- [`automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md#L65), line 65: "The baseline reproduces twice and the patched build resolves it twice."

**Which numbered repro steps still apply after switching to verify mode is unstated.** A run that finds an artifact at step 3 must infer whether to open the operations thread (step 4), check the adapter's seven capabilities (step 5), study and reproduce (steps 6 to 9), and wait for the rejection window before verifying; the reference relies on some of these without saying so.

- [`automations/benny/skills/reproduce-and-fix-issues/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/SKILL.md#L99), line 99: "If an open pull request or merged commit plausibly fixes this report, switch to `references/verify-existing-fix.md`."
- [`automations/benny/skills/reproduce-and-fix-issues/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/SKILL.md#L220), line 220: "When a fix artifact exists, follow `references/verify-existing-fix.md`."
- [`automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md#L38), line 38: "Through the configured control adapter:"
- [`automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md#L67), line 67: "Mark operations status as verified."
- [`automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md#L79), line 79: "Post the normal confirmed-repro source update if the run has not already used it."

### `automations/benny/skills/setup-benny/SKILL.md`

**Automations must not be enabled before a test that requires them to run.** The checks need both automations to trigger and post, but enabling is forbidden until they pass, and only the last line distinguishes "normal traffic". An agent cannot tell how the automations are run for the test (enabled on a test channel, run manually, or otherwise) before they count as enabled.

- [`automations/benny/skills/setup-benny/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/setup-benny/SKILL.md#L247), line 247: "Do not enable either automation until the thread-safety test passes after the editor save."
- [`automations/benny/skills/setup-benny/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/setup-benny/SKILL.md#L251), line 251: "Use a test channel or a harmless test report."
- [`automations/benny/skills/setup-benny/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/setup-benny/SKILL.md#L257), line 257: "Triage stores the root `thread_ts` and posts exactly one verdict as a reply."
- [`automations/benny/skills/setup-benny/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/setup-benny/SKILL.md#L265), line 265: "Enable normal traffic only after all seven checks pass."

**Commit-confirmation gate for live-prompt file references cannot be met on the existing-automations path.** The section 2 rule is not scoped to first-time creation, yet the existing-automations checklist requires a repository-file reference while forbidding use of the only named confirmer. A second gate ("once this check passes") names a different condition, so an agent cannot tell what permits the reference on that path or whether the section 8 commit confirmation is meant to replace the automate confirmation.

- [`automations/benny/skills/setup-benny/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/setup-benny/SKILL.md#L89), line 89: "Reference a repository file only after the built-in `/automate` skill confirms that the file is committed in the repository where the automation runs."
- [`automations/benny/skills/setup-benny/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/setup-benny/SKILL.md#L217), line 217: "The built-in `automate` skill is creation-only. Do not use it to search for, inspect, or update existing automations."
- [`automations/benny/skills/setup-benny/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/setup-benny/SKILL.md#L224), line 224: "- Direct instruction to read `.cursor/automations/benny/skills/triage-issue-reports/SKILL.md`"
- [`automations/benny/skills/setup-benny/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/setup-benny/SKILL.md#L68), line 68: "Once this check passes, live automation prompts may read the committed operational files by their stable repository-relative paths."

### `automations/benny/skills/triage-issue-reports/SKILL.md`

**"Do not post" after an already-linked permalink may bar the verdict or only duplicates.** When the permalink is already linked to a tracker issue but no triage reply exists, one reading posts no verdict at all, which leaves the repro automation waiting until timeout; the other posts a verdict that links the existing issue.

- [`automations/benny/skills/triage-issue-reports/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/triage-issue-reports/SKILL.md#L146), line 146: "Always check whether this source permalink is already linked to a tracker issue or a prior triage reply. If so, do not post or create a duplicate."
- [`automations/benny/FOR_AGENTS.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/FOR_AGENTS.md#L13), line 13: "outcome: i want exactly one reply in the source thread with a short verdict and `[benny:bug]`, `[benny:performance]`, or `[benny:other]`."
- [`automations/benny/skills/reproduce-and-fix-issues/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/SKILL.md#L76), line 76: "Stop silently for `other`, a missing verdict, an untrusted author, conflicting markers, or a timeout."

### `skills/arena/SKILL.md`

**"Read both rationales" has no clear referent among N candidate rationales and the judge.** Only candidates are asked for a rationale and there are N of them, while "both" follows a sentence about the lead and the judge; an agent resolving a disagreement may read the two disputed candidates' rationales or try to reconstruct the judge's reasoning.

- [`skills/arena/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/arena/SKILL.md#L32), line 32: "Disagreement means one of you is biased or the rubric was ambiguous. Read both rationales before deciding."
- [`skills/arena/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/arena/SKILL.md#L22), line 22: "a short rationale naming the alternatives it considered and what it rejected"
- [`skills/arena/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/arena/SKILL.md#L28), line 28: "the judge scores each candidate, by path label, on each rubric criterion and recommends a base"

**"The shared grounding" handed to every candidate is never defined or created.** No phase says what the shared grounding contains or who writes it, so the lead may invent one, pass nothing, or pass different context per run; interrogate inherits the same handover through its reuse of Phase B.

- [`skills/arena/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/arena/SKILL.md#L22), line 22: "each with the task, the path to the shared grounding, its own output path"
- [`skills/interrogate/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/interrogate/SKILL.md#L17), line 17: "Run Phase A steps 3 and 4 and Phase B of the **arena** skill"

**Minimum of two runners applies to slug rejection but not to candidate dropouts.** With the default three runners, one dropped seat and one dropout leave a single candidate, and the text does not say whether to continue to pick and graft with nothing to compare or to respawn to restore the floor.

- [`skills/arena/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/arena/SKILL.md#L17), line 17: "use the nearest valid slug of the same family or drop the seat, keep at least two runners, and say so"
- [`skills/arena/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/arena/SKILL.md#L24), line 24: "If a candidate produces no output, proceed with N-1 and note the dropout."

### `skills/automate-me/SKILL.md`

**Personal skill path allowed, but landing and update steps assume a repository file.** For a skill under the home directory, step 6 (worktree, commit, PR) cannot be followed and the update-mode git log gives no last-edit date, yet no alternative ending or date source is given. An agent must improvise how the work ends and which history to mine, and an evaluator has no stated completion condition for that path.

- [`skills/automate-me/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/automate-me/SKILL.md#L69), line 69: "(or `~/.cursor/skills/<handle>-mode/` if the user prefers a personal skill)"
- [`skills/automate-me/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/automate-me/SKILL.md#L83), line 83: "Work in a worktree off main. Commit and open a PR. Don't push to main directly."
- [`skills/automate-me/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/automate-me/SKILL.md#L23), line 23: "Step 1 mines only history since the skill was last edited (`git log -1 --format=%cI <path>`)."
- [`skills/automate-me/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/automate-me/SKILL.md#L17), line 17: "`~/.cursor/skills/*-mode/SKILL.md` matching the user's handle"

### `skills/benchmark-checklist/SKILL.md`

**Report rules requiring range and limiter are not reconciled with the one-run ballpark.** A ballpark skips question 1 (the limiter) and has no range from one run, so an agent cannot tell whether a ballpark that shows a difference may be reported as faster or slower or must be called inconclusive, or which Report items a ballpark omits.

- [`skills/benchmark-checklist/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/benchmark-checklist/SKILL.md#L11), line 11: "For a quick ballpark the user asked for, one run is enough. Still check questions 4 and 7, and say that it is one run. Skip the rest unless that run looks wrong."
- [`skills/benchmark-checklist/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/benchmark-checklist/SKILL.md#L32), line 32: "Give the number with its unit, the run count, the range, and the limiter."
- [`skills/benchmark-checklist/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/benchmark-checklist/SKILL.md#L33), line 33: "Call the verdict inconclusive when you claim a difference but cannot name the limiter"

**Verdict rules conflict when a gap is within noise and a side is untuned.** Question 5 makes such a result no measurable difference while Report bullet 3 makes it inconclusive, and it is unclear whether "when you claim a difference" scopes only the first clause; agents can return different verdicts for the same runs.

- [`skills/benchmark-checklist/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/benchmark-checklist/SKILL.md#L25), line 25: "A gap smaller than the run-to-run variation is no measurable difference."
- [`skills/benchmark-checklist/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/benchmark-checklist/SKILL.md#L33), line 33: "Call the verdict inconclusive when you claim a difference but cannot name the limiter, when a side ran untuned, or when you could not check questions 4 and 7."
- [`skills/benchmark-checklist/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/benchmark-checklist/SKILL.md#L22), line 22: "If you cannot tune it, do not pick a winner from that run."

### `skills/blast-radius/SKILL.md`

**"Step" names both the How sure are you levels and the Steps list.** In the hand-back, "which step you got it to" can be read as a level 1 to 5 of How sure are you or as a numbered item of ## Steps, so an agent may report the wrong number and an evaluator may misread the level of proof.

- [`skills/blast-radius/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/blast-radius/SKILL.md#L29), line 29: "Step 4 is usually one small script that imports the same library the app ships and calls the exact function you're worried about."
- [`skills/blast-radius/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/blast-radius/SKILL.md#L36), line 36: "4. Be honest about each risk."
- [`skills/blast-radius/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/blast-radius/SKILL.md#L43), line 43: "**The one fact it's safe because of.** State it, say which step you got it to, and show the proof."

**Unclear whether stopping at levels 2 or 3 counts as proven.** The Reply is binary (proven or unproven), but the text allows stopping where it is cheap and calls level 3 a showing, so agents may mark a fact proven at level 2 or 3 or unproven, and the success condition varies.

- [`skills/blast-radius/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/blast-radius/SKILL.md#L17), line 17: "Find the one or two facts the whole thing depends on and prove them by running code."
- [`skills/blast-radius/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/blast-radius/SKILL.md#L21), line 21: "get it as far down this list as is cheap, and say where it stopped."
- [`skills/blast-radius/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/blast-radius/SKILL.md#L25), line 25: "3. You showed the bad case can't happen. You walked the failure step by step and it doesn't reach."
- [`skills/blast-radius/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/blast-radius/SKILL.md#L43), line 43: "If you couldn't prove it, write unproven."

### `skills/correct/SKILL.md`

**Which classes to fix in a run is undefined; the remainder's treatment is unstated.** The heading and the Reply cover each class, but the fixing step covers only "the most frequent" with no threshold, and nothing says whether the other classes are left, deferred, or only reported. An agent cannot tell how many classes a run must fix, and an evaluator cannot tell when the run is done.

- [`skills/correct/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/correct/SKILL.md#L17), line 17: "## Fix each class at the highest level that works"
- [`skills/correct/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/correct/SKILL.md#L26), line 26: "Then fix the most frequent classes now, one commit each."
- [`skills/correct/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/correct/SKILL.md#L32), line 32: "**Reply:** each class with its evidence, the level you picked, and why a higher level didn't work."

### `skills/create-formal-verification-skill/SKILL.md`

**Whether a user-named area bounds target choice or only starts the search.** When the user names a specific race or invariant, one reading verifies it; the other moves to a stronger target elsewhere in the repo. The two readings produce different verifications and different judgments of whether the run met the request.

- [`skills/create-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/create-formal-verification-skill/SKILL.md#L13), line 13: "If the user named an area or a bug, start there."
- [`skills/create-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/create-formal-verification-skill/SKILL.md#L15), line 15: "Choose the strongest such target in the repo, not the one that is easiest to verify."
- [`skills/create-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/create-formal-verification-skill/SKILL.md#L3), line 3: "Use for /create-formal-verification-skill, \"model-check this race\", \"prove this invariant\""

### `skills/create-verification-skill/SKILL.md`

**Ending after reporting an unfixable broken checkout is not stated.** When the checkout cannot be fixed, an agent cannot tell whether to stop after the report or generate anyway, and an evaluator has no stated success condition for a report-only run.

- [`skills/create-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/create-verification-skill/SKILL.md#L21), line 21: "If the checkout doesn't build or start as-is, fix that first (or report it precisely) before generating; a skill written against a broken base teaches wrong steps."
- [`skills/create-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/create-verification-skill/SKILL.md#L40), line 40: "A generated skill that was never executed is a draft, not a deliverable."

**Whether the one-feature proof must drive every mapped entry point is unstated.** For a feature whose map file lists several entry points, an agent cannot tell whether the step 4 proof is complete after driving one of them, so the handover gate can be judged two ways.

- [`skills/create-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/create-verification-skill/SKILL.md#L36), line 36: "a proof that drives one convenient entry point is incomplete when the map lists others."
- [`skills/create-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/create-verification-skill/SKILL.md#L40), line 40: "drive ONE mapped feature (one is enough; the map exists so later runs can cover the rest)"

### `skills/figure-it-out/SKILL.md`

**Whether a multi-hour run's checkpoint waits for human approval is unstated.** An agent can read "checkpoint" as a stop that waits for the human before the long run, or as a presentation after which it proceeds; for work a human reviews after stepping away, the two readings differ between blocking for hours and not blocking.

- [`skills/figure-it-out/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/figure-it-out/SKILL.md#L23), line 23: "Present the framing and tradeoffs before committing to a long run. Reversible work proceeds (the **never-block-on-the-human** principle skill), but a multi-hour run earns one checkpoint."
- [`skills/principle-never-block-on-the-human/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-never-block-on-the-human/SKILL.md#L11), line 11: "Proceed, then present. Do the work, show the result. Don't ask "should I do X?" Do X, explain why."

### `skills/how/SKILL.md`

**Stated scope interpretation is not said to reach the exploring subagent.** The subagent receives only the question and the brief, so it can explore under a reading other than the one the lead states to the user. When the interpretation is stated (before spawning or with the result) is also open.

- [`skills/how/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/how/SKILL.md#L11), line 11: "If the scope is ambiguous, state your interpretation and explore. The user can redirect."
- [`skills/how/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/how/SKILL.md#L15), line 15: "Give it the user's question and this brief:"

### `skills/ketchup/SKILL.md`

**Ketchup's window and 100-word limit are undefined when autopilot-full applies it.** In an hourly loop tick or the playbook's final reply no /ketchup is typed, so an agent cannot tell whether each catch-up covers only the tick or everything since the operator's last message. Neither file says whether the playbook's required coverage of every PR overrides ketchup's 100-word cap on what happened.

- [`skills/ketchup/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/ketchup/SKILL.md#L9), line 9: "Catch the user up on what changed in this chat since the last message they wrote before `/ketchup`"
- [`skills/ketchup/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/ketchup/SKILL.md#L23), line 23: "Keep what happened under 100 words, not counting pictures, and shorter when less happened. Leave out work that changed nothing for the user."
- [`skills/poteto-mode/playbooks/autopilot-full.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/autopilot-full.md#L22), line 22: "A tick that changed something for the operator ends by catching them up per the **ketchup** skill, and one that changed nothing stays quiet."
- [`skills/poteto-mode/playbooks/autopilot-full.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/autopilot-full.md#L25), line 25: "**Reply:** catch the operator up per the **ketchup** skill, covering each PR's state and verdict, what merged, countersigns and why, open operator gates, and parked follow-ups"

### `skills/maintain-formal-verification-skill/SKILL.md`

**Ban on editing product code conflicts with the required temporary break of the code.** Read literally, the two statements cannot both be followed; an agent may skip the required break, perform it only on a copy, or edit product code against the stated ban. Whether a temporary, reverted break is outside the prohibition is not said.

- [`skills/maintain-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-formal-verification-skill/SKILL.md#L24), line 24: "Edit only the verification: models, harnesses, property files, and the verify skill itself. Never edit product code during a run, unless the user asks you to."
- [`skills/maintain-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-formal-verification-skill/SKILL.md#L41), line 41: "Break the new code the way the property guards against, such as removing a new check or reordering a new step, and confirm that the check catches it. Then drop the break."

**Failure judgment presumes a replayable counterexample though provers are in scope.** For a failed proof that yields no step sequence, the only stated method for telling drift from a bug does not apply, so an agent has no basis for the drift-or-bug judgment the skill exists to report.

- [`skills/maintain-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-formal-verification-skill/SKILL.md#L9), line 9: "or for any project-local skill that runs a model checker, prover, or code-level verifier against named code."
- [`skills/maintain-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-formal-verification-skill/SKILL.md#L42), line 42: "**Fail:** replay the counterexample against the real code, step by step. If a step cannot happen in the code, the verification is wrong."

### `skills/maintain-verification-skill/SKILL.md`

**What makes a doc or map correction proven is not defined.** Only harness fixes have a stated proof (re-driven live); an agent cannot tell whether a doc or map correction needs live observation or a source check before it may ship in the PR.

- [`skills/maintain-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-verification-skill/SKILL.md#L16), line 16: "one PR ships proven doc, harness, or map corrections."
- [`skills/maintain-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-verification-skill/SKILL.md#L33), line 33: "Any harness fix from triage gets re-driven live before it ships."
- [`skills/maintain-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-verification-skill/SKILL.md#L31), line 31: "Spot-check cited drift; don't re-prove clean claims."

**Whether verified-unreachable features permit a clean verdict is unstated.** A run with an unreachable feature and nothing to ship can be reported as `clean` or as `blocked`, so two careful agents can give different verdicts for the same evidence.

- [`skills/maintain-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-verification-skill/SKILL.md#L15), line 15: "every feature got source and live coverage; nothing worth shipping. No branch, no PR."
- [`skills/maintain-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-verification-skill/SKILL.md#L17), line 17: "coverage could not finish or a proven fix could not ship safely. Say exactly what blocked it."
- [`skills/maintain-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-verification-skill/SKILL.md#L33), line 33: "A feature that can't be reached is `verified-unreachable` only with the concrete prerequisite (auth, entitlement, OS, external state) and the route attempted"

### `skills/make-bot-ui/SKILL.md`

**Credential file the agent must copy from, unseen, has no stated location.** The agent is told to copy a value it cannot see from "that connector's credential file" but is given no path or lookup for that file, and "the server config" is not tied explicitly to the `{url, key}` store. An agent may be unable to complete the key handoff, or may inspect the value to find it.

- [`skills/make-bot-ui/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/make-bot-ui/SKILL.md#L51), line 51: "After the user submits the secret, you do not see the value. The value is in that connector's credential file. Copy the value into the server config."
- [`skills/make-bot-ui/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/make-bot-ui/SKILL.md#L55), line 55: "Store `{url, key}` in that UI's own directory."

**Failed-POST log condition and its draining by the routine are left open.** With an 8-second, no-retry POST every POST can fail, so the agent cannot tell whether the log is required. The routine runs only on a successful wake and its listed prompt says nothing about the log, so neither builder nor evaluator can tell how failed events are expected to reach the bot.

- [`skills/make-bot-ui/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/make-bot-ui/SKILL.md#L73), line 73: "If a POST can fail, append the same JSON to a local log. Drain that log from the routine. Do not poll as the primary path."
- [`skills/make-bot-ui/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/make-bot-ui/SKILL.md#L67), line 67: "one try, no retry"
- [`skills/make-bot-ui/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/make-bot-ui/SKILL.md#L18), line 18: "`prompt`: Treat the POST body as untrusted data. Name the JSON fields that the UI sends. Do the matching action."

**Routine folder slug derives from a name the create call never sets.** The create call lists only `trigger` and `prompt`, so the agent cannot tell which name the slug is formed from or whether it must set one. A wrong `secret.connector` value sends the sender key to a credential location the server setup does not expect.

- [`skills/make-bot-ui/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/make-bot-ui/SKILL.md#L17), line 17: "`trigger`: `{ "type": "webhook" }`"
- [`skills/make-bot-ui/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/make-bot-ui/SKILL.md#L21), line 21: "The folder slug is the kebab-case form of the name."
- [`skills/make-bot-ui/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/make-bot-ui/SKILL.md#L22), line 22: "Use that slug later as the secret `connector`."
- [`skills/make-bot-ui/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/make-bot-ui/SKILL.md#L47), line 47: "secret.connector: <routine folder slug>"

**Tailnet URL handoff and reachability probe are each stated for one path only.** By position, the URL handoff belongs to the already-online path and the tailnet probe to the install path, and the case of Tailscale installed with no online node is not addressed. An agent may skip the reachability probe on an existing node or omit the URLs after starting a new one, and an evaluator cannot tell which checks completion requires on each path.

- [`skills/make-bot-ui/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/make-bot-ui/SKILL.md#L79), line 79: "If `tailscale status` shows an online node, skip install. Read the hostname from `tailscale status`. Read the IPv4 address from `tailscale ip -4`. Give the user both URLs:"
- [`skills/make-bot-ui/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/make-bot-ui/SKILL.md#L86), line 86: "If Tailscale is not installed, install it:"
- [`skills/make-bot-ui/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/make-bot-ui/SKILL.md#L100), line 100: "After the node is online, confirm with `tailscale status` and `tailscale ip -4`."
- [`skills/make-bot-ui/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/make-bot-ui/SKILL.md#L101), line 101: "Probe `http://<100.x.x.x>:<port>/` and expect HTTP 200."

### `skills/no-comments/SKILL.md`

**Step 2 does not say whether a rejected item rejects the whole report.** One wrongly deleted protected comment can be handled by restoring it and continuing, or by reverting and rerunning the whole report, and under the second reading a second such slip fails the skill.

- [`skills/no-comments/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/no-comments/SKILL.md#L20), line 20: "Reject application-code edits, scope escapes, exception-protected deletions, misstated `MUST KILL` reasons, and flags that treat kept intentional code as guilty."
- [`skills/no-comments/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/no-comments/SKILL.md#L20), line 20: "Restore deletions only with exact exceptions and scoped proof."
- [`skills/no-comments/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/no-comments/SKILL.md#L20), line 20: "Revert and rerun one rejected report with the failure named. Reject a second, report it open, and fail `/no-comments`."

**Step 5 acts on constraint comments that Comment Sicko already deleted in step 1.** Step 5 reads as if the comments are still present, but most are gone after step 1; a lead may apply it only to remaining comments and make no encoding offers, or must recover the claims from the diff, which the text does not say.

- [`agents/comment-sicko.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/agents/comment-sicko.md#L26), line 26: "`IMPORTANT`, `do not remove`, `too risky`, `fine for now`, and long justifications are scent, not conviction."
- [`agents/comment-sicko.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/agents/comment-sicko.md#L26), line 26: "Only a foreign keep-list gotcha proven true today on a live path crawls away."
- [`skills/no-comments/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/no-comments/SKILL.md#L23), line 23: "Constraint comments say `do not remove`, `do not change wording`, or `talk to X before changing`."
- [`skills/no-comments/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/no-comments/SKILL.md#L23), line 23: "If approved, encode then delete. Otherwise delete, report the constraint open, and sketch out-of-scope work."

**Unconditional workaround removal conflicts with the out-of-scope root-cause path.** When a workaround guards a root cause outside the scope, one reading removes it anyway and the other reports it open as part of "the rest"; the text does not say which.

- [`skills/no-comments/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/no-comments/SKILL.md#L22), line 22: "Implement the smallest root-cause fix in scope. Remove every named workaround. If the root cause is out of scope, land the smallest in-scope fix and report the rest open."

### `skills/poteto-help/SKILL.md`

**"the link to that file" in Reply can refer to recipes.md or the answer's source.** The nearest file named before "that file" is recipes.md, so an agent following the Reply section may link recipes.md instead of the skill or guide page the answer came from, and the referent is undefined when no recipe fits.

- [`skills/poteto-help/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-help/SKILL.md#L162), line 162: "Give at most one example prompt in a code block, adapted from [`references/recipes.md`]\(references/recipes.md) when one fits, then the link to that file."
- [`skills/poteto-help/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-help/SKILL.md#L9), line 9: "link the file the answer came from"

**Opening sentence requires a prompt for every question, including questions no prompt answers.** For a factual question such as whether `/orchestrate` belongs to pstack, an agent cannot tell whether a reply without a prompt is acceptable ("at most one") or a failure ("hand them a prompt"). An evaluator likewise cannot tell whether a missing prompt counts against the reply.

- [`skills/poteto-help/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-help/SKILL.md#L9), line 9: "Answer the user's question about pstack, hand them a prompt they can send, and link the file the answer came from."
- [`skills/poteto-help/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-help/SKILL.md#L162), line 162: "Give at most one example prompt in a code block, adapted from [`references/recipes.md`]\(references/recipes.md) when one fits"
- [`skills/poteto-help/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-help/SKILL.md#L117), line 117: "pstack has no `/orchestrate` skill. If the slash menu shows `/orchestrate`, another plugin provides it."

### `skills/poteto-mode/SKILL.md`

**Routing rule leaves unclear whether unattended work fitting a playbook goes to figure-it-out.** For an unattended run that also matches the Autonomous run (or Autopilot) playbook, an agent cannot tell whether to run that playbook or have figure-it-out design a new one, and figure-it-out's own condition (no playbook matches) contradicts the unattended route.

- [`skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/SKILL.md#L108), line 108: "Large, cross-cutting, or unattended work, or a task no playbook fits, routes to the **figure-it-out** skill."
- [`skills/poteto-mode/playbooks/autonomous-run.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/autonomous-run.md#L3), line 3: "**You own the exit condition. Define done, then drive to it without stopping.**"
- [`skills/figure-it-out/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/figure-it-out/SKILL.md#L9), line 9: "When the task matches no playbook, design one."
- [`docs/guide/07-overnight.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/docs/guide/07-overnight.md#L38), line 38: "Because you'll review this work after stepping away, `/poteto-mode` routes it through [`/figure-it-out`]\(../../skills/figure-it-out/SKILL.md)"

### `skills/poteto-mode/playbooks/autonomous-run.md`

**No criterion separates a plateau, which continues the run, from a genuine dead end.** The only permitted ending short of the predicate rests on an undefined distinction, so two agents on the same unattended run can stop at different points, and an evaluator cannot tell whether a surfaced dead end was premature.

- [`skills/poteto-mode/playbooks/autonomous-run.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/autonomous-run.md#L11), line 11: "A plateau is not a stop, so keep going and pivot your approach to push past it. Surface a genuine dead end rather than spinning, and never relax the predicate to declare victory."
- [`skills/poteto-mode/playbooks/autonomous-run.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/autonomous-run.md#L9), line 9: "Surface only irreversible actions, genuine product or preference calls no experiment can settle, or a real dead end."

### `skills/poteto-mode/playbooks/bug-fix.md`

**"Skip it" may skip the tdd cadence or the failing-repro-first commit staging.** One reading drops only the tdd cadence and still requires the failing repro to land first; the other drops the staging requirement. The resulting git history, and whether a reviewer may treat its order as required, differ.

- [`skills/poteto-mode/playbooks/bug-fix.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/bug-fix.md#L11), line 11: "Stage the commits so the failing repro lands before the fix in git history."
- [`skills/poteto-mode/playbooks/bug-fix.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/bug-fix.md#L11), line 11: "See the **tdd** skill for the failing-test-first cadence when the bug has a cheap local test path. Skip it when the test would be expensive, integration-heavy, or unclear."

### `skills/poteto-mode/playbooks/eval.md`

**Banned-word rule's scope over file contents versus names is unstated.** Read as covering file contents, the rule requires scrubbing words such as `test` from the planted skeleton, skills, and variant, which may alter the variant under test; read as covering names only, those contents stay. The two readings lead to different environments, and a blinding check cannot be judged without choosing one.

- [`skills/poteto-mode/playbooks/eval.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/eval.md#L7), line 7: "No `eval`, `test`, `judge`, `experiment`, `rubric`, `score`, `compare`, `benchmark`, `candidate`, or `arena` in any directory, file, or prompt the candidate sees."
- [`skills/poteto-mode/playbooks/eval.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/eval.md#L10), line 10: "Sanitize directory and slug names. Use project-shaped names a user might pick."
- [`skills/poteto-mode/playbooks/eval.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/eval.md#L18), line 18: "Per-candidate working dir with the variant in place. Plant any context an organic task would have: a project skeleton, the skills the candidate would naturally read."

### `skills/poteto-mode/playbooks/feature.md`

**"Mandatory" in step 4 may cover all code-writing delegation or only the arena route.** An agent cannot tell whether the no-skip rule binds delegation of code-writing in every run or only the arena delegation for multi-shape work, so it may skip one of them with a reason under one reading and not the other. "Review separation", the stated test for the alternative path, is not defined in the file.

- [`skills/poteto-mode/playbooks/feature.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/feature.md#L12), line 12: "When the implementation admits multiple valid shapes (error handling, abstraction layer, test structure), delegate via the **arena** skill instead so the runners surface the alternatives and the cross-judge guards the pick."
- [`skills/poteto-mode/playbooks/feature.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/feature.md#L12), line 12: "Mandatory: no skip-with-reason escape, and Laziness Protocol does not override it (the gain is review separation, not lines saved)."
- [`skills/poteto-mode/playbooks/feature.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/feature.md#L12), line 12: "A subagent forbidden to spawn satisfies this by owning the diff directly with the same review separation."

### `skills/poteto-mode/playbooks/investigation.md`

**Investigation preceding a code change: exception clause conflicts with hand-back instruction.** "unless" reads as permitting a PR, babysit, or `architect` when a code change follows, while the next sentence says to hand back and re-route. An agent cannot tell whether to stop and wait for the user or to continue itself into Bug fix or Feature.

- [`skills/poteto-mode/playbooks/investigation.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/investigation.md#L12), line 12: "No PR, no babysit, no `architect` unless the investigation precedes a code change. If it does, hand back to the user and re-route to Bug fix or Feature."

### `skills/poteto-mode/playbooks/opening-a-pr.md`

**Worktree off trunk conflicts with stacking a follow-up on another PR's branch.** For a stacked follow-up the file does not say whether the worktree starts from trunk or from the parent PR's branch, although autopilot-stack cites this file for that case. The two readings produce branches with different contents.

- [`skills/poteto-mode/playbooks/opening-a-pr.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/opening-a-pr.md#L5), line 5: "Work from a git worktree off trunk, and keep unrelated work out of it."
- [`skills/poteto-mode/playbooks/opening-a-pr.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/opening-a-pr.md#L9), line 9: "Stack follow-ups by base branch."
- [`skills/poteto-mode/playbooks/autopilot-stack.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/autopilot-stack.md#L6), line 6: "Base the PR on the other PR's branch in place of trunk, per `playbooks/opening-a-pr.md`."

### `skills/poteto-mode/playbooks/prototype.md`

**Who chooses the direction, and when it goes to Feature, is unstated.** The file says the agent owns the decision but also that it presents a recommendation, and "the chosen direction" names no chooser. An agent may start the Feature build in the same run on its own recommendation or stop and wait for the user, and an evaluator cannot tell whether a run that ends with a recommendation is complete.

- [`skills/poteto-mode/playbooks/prototype.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/prototype.md#L3), line 3: "You own the design decision, not the code."
- [`skills/poteto-mode/playbooks/prototype.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/prototype.md#L12), line 12: "Present alternatives, tradeoffs, and a recommendation. The output is the decision plus the throwaway artifact, not shippable code. Hand the chosen direction to **Feature** (or `architect` for the shape) for the real build."
- [`skills/poteto-mode/playbooks/prototype.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/prototype.md#L14), line 14: "tradeoffs, your recommendation, and the scratch path."

### `skills/poteto-mode/playbooks/refactoring.md`

**Which redesigns route to Feature, and whether routing ends this run, is unstated.** Step 3 itself asks for a from-first-principles target shape, and Feature is defined as adding behavior, so an agent cannot tell which structural redesigns leave this playbook. It also cannot tell whether the refactoring run stops when it routes or continues beside Feature.

- [`skills/poteto-mode/playbooks/refactoring.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/refactoring.md#L3), line 3: "Distinct from Feature, which adds behavior, and Bug fix, which corrects it."
- [`skills/poteto-mode/playbooks/refactoring.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/refactoring.md#L5), line 5: "A redesign is allowed, but name it and route to Feature."
- [`skills/poteto-mode/playbooks/refactoring.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/refactoring.md#L9), line 9: "State what the module layout, types, and call graph should be if built today (**principle-foundational-thinking**, **principle-redesign-from-first-principles**)."

### `skills/poteto-mode/playbooks/visual-parity.md`

**Per-component loop has no ending for a diff that never reaches zero.** Step 4's only stop condition is a zero diff, while the Reply's "what's left" implies a run may end with work outstanding. For a component whose diff cannot reach zero without a forbidden shortcut, an agent may loop indefinitely or stop and report it, and the file does not say which.

- [`skills/poteto-mode/playbooks/visual-parity.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/visual-parity.md#L8), line 8: "A nonzero diff is a fail. Investigate the pixel delta. `/loop` per component until the diff is zero."
- [`skills/poteto-mode/playbooks/visual-parity.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/visual-parity.md#L11), line 11: "**Reply:** components migrated, the diff result for each, the baseline harness location, what's left."

### `skills/principle-encode-lessons-in-structure/SKILL.md`

**Corollary does not say whether existing instruction text is removed after a structural fix.** The trigger presupposes an instruction already written; an agent cannot tell whether 'only use the structural fix' requires deleting that existing instruction or only forbids adding more text, so two agents may leave different repositories.

- [`skills/principle-encode-lessons-in-structure/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-encode-lessons-in-structure/SKILL.md#L11), line 11: "**Corollary:** If the fix is structural, only use the structural fix. The instruction is the symptom."
- [`skills/principle-encode-lessons-in-structure/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-encode-lessons-in-structure/SKILL.md#L3), line 3: "Encode the rule as a lint, metadata flag, runtime check, or script instead of more text."

### `skills/principle-exhaust-the-design-space/SKILL.md`

**Body opens with 'It also applies'; rule and trigger exist only in frontmatter.** The body's only sentence has no antecedent for 'It' and states no action; the instruction lives only in the description metadata. Where a host presents the body without frontmatter, the agent receives no rule to apply.

- [`skills/principle-exhaust-the-design-space/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-exhaust-the-design-space/SKILL.md#L9), line 9: "It also applies to product design decisions where user experience depends on feel, not logic."
- [`skills/principle-exhaust-the-design-space/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-exhaust-the-design-space/SKILL.md#L3), line 3: "Apply when facing a novel UI interaction or architectural decision with no precedent in the codebase. Build 2-3 competing prototypes and compare side by side before committing."

### `skills/principle-explain-the-number/SKILL.md`

**'Stop' when spread exceeds the effect has no stated object or resulting verdict.** An agent cannot tell whether to stop adding runs, abandon the measurement, or stop and report no measurable difference; the condition also depends on run data although it sits in the pre-run bullet.

- [`skills/principle-explain-the-number/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-explain-the-number/SKILL.md#L9), line 9: "**Write the decision before you run.** Name the result that would change it, and the noise floor. Stop when the run-to-run spread is larger than the effect."

**Limiter requirement and its failure verdict are undefined for eval results.** For an eval result an agent cannot tell whether a profiled resource or code-path limiter is required, or what to report when none can be named; the 'inconclusive' rule exists only in benchmark-checklist, which the file applies to performance numbers.

- [`skills/principle-explain-the-number/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-explain-the-number/SKILL.md#L3), line 3: "a speedup, a regression, a throughput, a latency, or an eval result. Find what limits it"
- [`skills/principle-explain-the-number/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-explain-the-number/SKILL.md#L10), line 10: "Name the resource or code path that bounds the result, from a profile or counters taken during a run."
- [`skills/principle-explain-the-number/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-explain-the-number/SKILL.md#L14), line 14: "For an eval result, ask whether every run did the task, whether the gap holds across trials and models, and whether the scenario matters."
- [`skills/benchmark-checklist/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/benchmark-checklist/SKILL.md#L33), line 33: "Call the verdict inconclusive when you claim a difference but cannot name the limiter"

### `skills/principle-guard-the-context-window/SKILL.md`

**'mechanism costs' is used without definition.** An agent cannot tell which costs to account for (for example subagent spawning, tool-output size, or summary overhead), so the instruction may be applied differently or ignored.

- [`skills/principle-guard-the-context-window/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-guard-the-context-window/SKILL.md#L12), line 12: "**Size phases and cap scope.** Limit files per phase, set turn budgets, account for mechanism costs."

### `skills/principle-laziness-protocol/SKILL.md`

**Consolidation rule's scope unstated; it can conflict with the smallest-change rule.** When the code already repeats a choice the change touches, an agent cannot tell whether to consolidate it (enlarging the diff) or leave it (keeping the diff minimal); the file gives no scope or priority between the two bullets.

- [`skills/principle-laziness-protocol/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-laziness-protocol/SKILL.md#L9), line 9: "Do not repeat the same choice in several places. Put it behind one source of truth and pass the result as a simple flag."
- [`skills/principle-laziness-protocol/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-laziness-protocol/SKILL.md#L10), line 10: "Make the smallest change that solves the problem. Fewer lines beat "elegant" boilerplate."

### `skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md`

**Applicability list does not say whether all conditions or any one must hold.** The list gates deleting an old API. Read as 'any', a refactor initiative alone would license removing an API that external users depend on; read as 'all', it would not, so the agent's decision to delete depends on an unstated reading.

- [`skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md#L11), line 11: "**When this applies:**"
- [`skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md#L12), line 12: "- No external users depend on backward compatibility"
- [`skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md#L14), line 14: "- The new API is part of a simplification or refactor initiative"

### `skills/principle-never-block-on-the-human/SKILL.md`

**No rule for a needed product-direction decision the human has not given.** When work requires a product decision, an agent cannot tell whether to wait for the human (product direction comes from the human) or decide and proceed (agents must stay unblocked).

- [`skills/principle-never-block-on-the-human/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-never-block-on-the-human/SKILL.md#L9), line 9: "Agents must stay unblocked. Make reasonable decisions, proceed, and let the human course-correct after the fact."
- [`skills/principle-never-block-on-the-human/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-never-block-on-the-human/SKILL.md#L15), line 15: "Product direction comes from the human. Execution should not block."

### `skills/principle-sequence-verifiable-units/SKILL.md`

**'Each commit lands on its own' is unclear beside failing-test-first delivery and green gating.** If 'lands on its own' means each commit is independently green and mergeable, a commit holding only the failing test violates it; an agent cannot tell whether to commit a red test separately, combine it with the fix, or mark it expected-to-fail.

- [`skills/principle-sequence-verifiable-units/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-sequence-verifiable-units/SKILL.md#L9), line 9: "do not advance until the current one is green."
- [`skills/principle-sequence-verifiable-units/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-sequence-verifiable-units/SKILL.md#L13), line 13: "Deliver in the order that proves the work: the failing test first, then the fix."
- [`skills/principle-sequence-verifiable-units/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-sequence-verifiable-units/SKILL.md#L13), line 13: "Each commit lands on its own."

### `skills/recall/SKILL.md`

**"Fast, cheap model" maps to no poteto-mode role, model line, or slug.** The cited section requires an explicit model per role and keeping the role's model family, but recall names no role, so an agent cannot tell whether "cheap" means a lower level of the default model or a different model family.

- [`skills/recall/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/recall/SKILL.md#L19), line 19: "Spawn parallel subagents on a fast, cheap model, each taking a slice of the corpus."
- [`skills/recall/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/recall/SKILL.md#L19), line 19: "Pick each subagent's reasoning level for the job, per the Subagents section of the **poteto-mode** skill."
- [`skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/SKILL.md#L88), line 88: "an explicit model per role, Project workers included."
- [`skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/SKILL.md#L96), line 96: "Start from the role's line or default, keep its family, and set the level the job needs."

**Thread status tags cover no closed-unmerged or abandoned thread, yet exactly one is required.** Abandoned attempts and PRs closed without merging are expected content of the brief, but no tag fits them. An agent must mislabel such a thread, omit it, or break the exactly-one-tag rule.

- [`skills/recall/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/recall/SKILL.md#L29), line 29: "prefixed with exactly one status tag: `[merged #N]`, `[open PR #N]`, `[in flight <branch>]`, `[verified, uncommitted]`, `[reverted #N]`, or `[planned, not started]`."
- [`skills/recall/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/recall/SKILL.md#L20), line 20: "what's been tried and didn't hold"

### `skills/reflect/SKILL.md`

**Two copy destinations offered with no criterion for project versus user folder.** The project folder makes the edited copy apply to work in this repository, while the user folder makes it apply to this user across projects; the text gives no rule for proposing one. Agents may propose different scopes for the same learning, leaving the choice to whatever the user notices at approval.

- [`skills/reflect/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/reflect/SKILL.md#L17), line 17: "Before approval, show its destination, `.cursor/skills/<skill>/` or `~/.cursor/skills/<skill>/`. After approval, copy the skill folder there and edit the copy."

### `skills/setup-pstack/SKILL.md`

**"(optional)" on steps 7 and 8 leaves unclear whether the offer must be made.** The heading can mean the agent may skip the step or that the user may decline; the body and the user-facing docs describe the offer as always made. An agent may omit the offers, and an evaluator cannot tell whether an omitted offer is a failure.

- [`skills/setup-pstack/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/setup-pstack/SKILL.md#L74), line 74: "### 7. Offer a verification skill (optional)"
- [`skills/setup-pstack/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/setup-pstack/SKILL.md#L76), line 76: "Check whether the project has a way to drive the real app for proof (a `verify-*` skill, or an existing harness). If not, offer once:"
- [`skills/poteto-help/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-help/SKILL.md#L39), line 39: "Then it offers once each to generate a verification skill and a formal verification skill for the project, unless the project already has one."
- [`docs/guide/01-setup.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/docs/guide/01-setup.md#L35), line 35: "If it finds neither, it offers once to generate one with"

**"Detected set" undefined when two detection sources differ or slugs are pasted.** An agent cannot tell whether a slug listed by the models API but not passable to `Task`, or a slug the user pasted, counts as detected and confirmed. Read one way it writes slugs the Task tool may reject; read the other way step 4 rejects every real slug after a paste fallback.

- [`skills/setup-pstack/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/setup-pstack/SKILL.md#L14), line 14: "That is the dependable source. If Cursor also exposes a models API or CLI that lists the user's entitled models, prefer it for completeness."
- [`skills/setup-pstack/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/setup-pstack/SKILL.md#L14), line 14: "If you cannot detect any, ask the user to paste the slugs they have access to. Never write a real slug you have not confirmed is available."
- [`skills/setup-pstack/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/setup-pstack/SKILL.md#L44), line 44: "Every real slug written must be in the detected set and at `xhigh` or below."

**Slug invariants of step 3(b) conflict with options offered for user picks in 3(c).** Step 3(c) offers every detected model at `xhigh` or below, which can include a non-fast Opus 5.5 slug or a Gemini `xhigh` slug, and step 4 accepts them. Whether the 3(b) statements bind only the budget mapping or every written value is unstated, so an agent may write the user's pick or override it.

- [`skills/setup-pstack/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/setup-pstack/SKILL.md#L38), line 38: "Opus 5.5 always runs its `-fast` slug, so every Opus 5.5 value ends in `-fast`."
- [`skills/setup-pstack/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/setup-pstack/SKILL.md#L38), line 38: "a Gemini entry stays at `high` when its role's target is `xhigh`."
- [`skills/setup-pstack/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/setup-pstack/SKILL.md#L40), line 40: "offering the detected models at `xhigh` or below plus `inherit-parent` and `auto`"
- [`skills/setup-pstack/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/setup-pstack/SKILL.md#L44), line 44: "Every real slug written must be in the detected set and at `xhigh` or below."

### `skills/sharpen/SKILL.md`

**Unclear whether the rewritten prompt must reserve preference choices for the user.** Read as part of what the rewritten prompt asks, the prompt must tell the receiving agent to leave those choices to the user; read as an instruction to the sharpening agent, the prompt need not say so and the receiving agent may make them.

- [`skills/sharpen/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/sharpen/SKILL.md#L16), line 16: "Have the rewritten prompt ask the agent to prototype any choice an experiment can settle and recommend an option based on what it observed. Leave product or preference choices that no experiment can settle for me to make."

### `skills/swarm/SKILL.md`

**Coverage requires a result per slice, yet dropouts proceed without respawn.** For a coverage run the lead cannot tell whether a dropped worker's slice must be respawned to get a result or simply reported, and whether a run that ends with a gap or dropout has met the coverage rule or failed it.

- [`skills/swarm/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/swarm/SKILL.md#L33), line 33: "If a worker drops out, proceed with N-1 and note it."
- [`skills/swarm/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/swarm/SKILL.md#L37), line 37: "Drop a result that does not record the SHAs and method its brief names, and respawn that worker once. After a second miss, record a gap. A gap does not count as a pass."
- [`skills/swarm/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/swarm/SKILL.md#L37), line 37: "For coverage, every required slice needs a result."

### `skills/technical-writing/SKILL.md`

**Exception for rules that worsen a sentence has unclear reach over applied unslop rules.** Where removing a dash or applying another twin rule makes a sentence worse, technical-writing permits leaving it, while the unslop skill it requires states the same rule with no exception. An agent cannot tell whether the sentence may stay, and the two files cannot both be followed for it.

- [`skills/technical-writing/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/technical-writing/SKILL.md#L13), line 13: "When a rule makes a sentence worse, fix the sentence another way or leave it alone."
- [`skills/technical-writing/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/technical-writing/SKILL.md#L67), line 67: "Apply the **unslop** skill to every doc this skill touches."
- [`skills/technical-writing/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/technical-writing/SKILL.md#L61), line 61: "Use periods, not semicolons or em dashes."
- [`skills/unslop/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/unslop/SKILL.md#L21), line 21: "13. No em dashes, en dashes, or hyphens used as dashes, and no parentheses in their place. Use a period or a comma."

**Review use is named, but the body gives no review result: fix or report.** On a review request an agent cannot tell whether to rewrite the document in place or report the rules it breaks, so it may change files the user wanted only assessed, or return a report where edits were expected.

- [`skills/technical-writing/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/technical-writing/SKILL.md#L3), line 3: "Use for /technical-writing or when writing or reviewing docs, RFCs, readmes, PR descriptions, or commit messages."
- [`skills/technical-writing/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/technical-writing/SKILL.md#L9), line 9: "Write so a tired engineer understands on the first read."
- [`docs/guide/09-make-it-yours.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/docs/guide/09-make-it-yours.md#L69), line 69: "/technical-writing review the readme changes"
- [`docs/guide/09-make-it-yours.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/docs/guide/09-make-it-yours.md#L72), line 72: "Use it to review what you or an agent just wrote, or name it up front when you ask for a doc."

### `skills/typescript-best-practices/SKILL.md`

**Patterns reference, cited as examples, adds rules whose binding force is unstated.** The table's schema rule assumes the repository has a runtime schema library; only the reference, presented as examples, says not to add one for a single guard. An agent that reads only the table may add a dependency, and an evaluator cannot tell whether the reference's extra instructions are criteria.

- [`skills/typescript-best-practices/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/typescript-best-practices/SKILL.md#L31), line 31: "Examples: `references/patterns.md`."
- [`skills/typescript-best-practices/references/patterns.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/typescript-best-practices/references/patterns.md#L3), line 3: "Code examples for each rule in `SKILL.md`."
- [`skills/typescript-best-practices/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/typescript-best-practices/SKILL.md#L19), line 19: "Before hand-writing a property-by-property type guard, use the repository's runtime schema library and infer the type from the schema, such as `z.infer`."
- [`skills/typescript-best-practices/references/patterns.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/typescript-best-practices/references/patterns.md#L153), line 153: "Use `safeParse` when failure is an expected branch. Use the equivalent inference helper when the repository uses another schema library. Do not add a new schema dependency for one guard."
- [`skills/typescript-best-practices/references/patterns.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/typescript-best-practices/references/patterns.md#L26), line 26: "Match the `readonly __brand: 'X'` shape. Don't invent a new convention."

### `skills/unslop/SKILL.md`

**Fact-supplying rules beside "Preserve meaning" give no fallback when the fact is absent.** When the text being edited lacks the plan, mechanism, or number a rule asks for, an agent cannot tell whether to delete the sentence, leave it, or supply a fact the source does not contain, and the last adds unsupported claims. An evaluator cannot tell which result passes.

- [`skills/unslop/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/unslop/SKILL.md#L9), line 9: "Edit text to remove AI patterns. Scan for the patterns below, then rewrite. Preserve meaning and match the intended tone."
- [`skills/unslop/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/unslop/SKILL.md#L32), line 32: "25. No generic conclusions. State specific plans or facts."
- [`skills/unslop/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/unslop/SKILL.md#L34), line 34: "27. Say what it does, not how it feels. Name the mechanism or the number."
- [`skills/unslop/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/unslop/SKILL.md#L37), line 37: "30. Cut adverbs or use a stronger verb. Give the number."

## Success is stated as an artifact or a step

The text says what to produce or do and leaves the result that counts as done unstated.

### `automations/benny/skills/setup-benny/SKILL.md`

**Integration capability check gives no consequence when a capability is missing.** Section 4 lists required Slack, tracker, repository, and pull request capabilities but, unlike section 6, does not say whether a missing one stops setup, disables an automation, or is left to runtime fail-closed behavior. The agent decides whether setup continues.

- [`automations/benny/skills/setup-benny/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/setup-benny/SKILL.md#L117), line 117: "## 4. Check integration capabilities"
- [`automations/benny/skills/setup-benny/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/setup-benny/SKILL.md#L122), line 122: "Thread-reply access in that channel"
- [`automations/benny/skills/setup-benny/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/setup-benny/SKILL.md#L164), line 164: "If any capability is missing, leave the repro automation disabled."

**Setup completion undefined when the repro automation is left disabled.** With repro disabled, the repro checks cannot pass, so the enable rule also blocks triage. An agent or evaluator cannot tell whether a triage-only setup may go live or counts as complete.

- [`automations/benny/skills/setup-benny/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/setup-benny/SKILL.md#L164), line 164: "If any capability is missing, leave the repro automation disabled. It must fail closed rather than claim a reproduction it did not perform."
- [`automations/benny/skills/setup-benny/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/setup-benny/SKILL.md#L259), line 259: "Repro accepts the marker only from the configured triage identity."
- [`automations/benny/skills/setup-benny/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/setup-benny/SKILL.md#L265), line 265: "Enable normal traffic only after all seven checks pass."

### `skills/architect/SKILL.md`

**"Stay in the loop" is undefined, and the body never says when work ends.** The body says nothing about the post-sketch phase, so an agent cannot tell whether architect ends with the chosen shape or continues through implementation, what staying in the loop requires, or when the skill is done.

- [`skills/architect/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/architect/SKILL.md#L3), line 3: "Sketch types, signatures, and module structure before code, then stay in the loop while implementation fills in."
- [`skills/architect/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/architect/SKILL.md#L9), line 9: "Redesign instead of patching if workarounds repeat."
- [`skills/no-comments/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/no-comments/SKILL.md#L21), line 21: "Stop at the sketch. Architect shapes. Step 4 implements."

### `skills/how/SKILL.md`

**Lead's step is presenting subagent output; no check against the brief's target.** The only result condition sits inside the subagent brief; the lead's own work ends at presenting the output. An agent has no stated check or next action when the output misses the target, and is told not to substantially rewrite it.

- [`skills/how/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/how/SKILL.md#L17), line 17: "write an explanation that a senior engineer unfamiliar with this area could read and walk away with a solid mental model."
- [`skills/how/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/how/SKILL.md#L21), line 21: "Present the subagent's output. Light edits for clarity or context from the conversation are fine. Do not substantially rewrite it."

### `skills/poteto-mode/playbooks/authoring-a-skill.md`

**Skill success is checked only by form validation and undefined conditional test cases.** The file does not say what makes a skill or change "structural" or "subjective", what a test case checks, or what passing means, so an agent cannot tell when step 3 is required, and an evaluator has only form checks to judge whether the authored skill does its job.

- [`skills/poteto-mode/playbooks/authoring-a-skill.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/authoring-a-skill.md#L6), line 6: "2. Validate the skill: frontmatter has `name` and `description`, referenced files exist, cross-skill links resolve."
- [`skills/poteto-mode/playbooks/authoring-a-skill.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/authoring-a-skill.md#L7), line 7: "3. Test cases if structural. Skip if subjective."

### `skills/poteto-mode/playbooks/babysit.md`

**`drive` ends at undefined "merge-ready"; the watcher's READY ignores required approval.** The end state of `drive` is never defined, and the status source the playbook names returns READY, exit 0, while approval is still required or a Code Review Gate is pending (facts report, section 1 Limits and runs). An agent can report a PR merge-ready that still waits on its owner, or cannot tell whether "a wait" means keep looping or stop.

- [`skills/poteto-mode/playbooks/babysit.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/babysit.md#L5), line 5: "Modes: `drive` loops to merge-ready"
- [`skills/poteto-mode/playbooks/babysit.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/babysit.md#L10), line 10: "Owner approval is a wait. Babysitting never authorizes merging."
- [`skills/poteto-mode/scripts/watch-pr/policy.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/scripts/watch-pr/policy.ts#L202), line 202: "if (reviewDecision === "CHANGES_REQUESTED") return null;"
- [`skills/poteto-mode/scripts/watch-pr/github.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/scripts/watch-pr/github.ts#L251), line 251: "A gate that is pending or waits on an owner approval must not count as"

### `skills/poteto-mode/playbooks/feature.md`

**A flagged non-pass verification has no stated effect on proceeding to the PR.** After an inconclusive or wrong-surface result, an agent cannot tell whether to stop, re-verify, or continue through rebase and PR with the flag noted, and an evaluator cannot tell whether a run that opened a PR on a flagged non-pass succeeded.

- [`skills/poteto-mode/playbooks/feature.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/feature.md#L13), line 13: "5. Verify on the matching surface. "Inconclusive" or wrong-surface is not a pass. Flag it."
- [`skills/poteto-mode/playbooks/feature.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/feature.md#L17), line 17: "8. Run **Opening a PR**."

### `skills/poteto-mode/playbooks/perf-issue.md`

**"The target" governs the stop rule but is never defined or sourced.** The playbook never says where the target comes from or what threshold counts as success, so an agent cannot apply the stop rule and an evaluator has only a reported delta, not a result condition, to judge the fix.

- [`skills/poteto-mode/playbooks/perf-issue.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/perf-issue.md#L16), line 16: "When an earlier mantra meets the target, stop."
- [`skills/poteto-mode/playbooks/perf-issue.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/perf-issue.md#L25), line 25: "**Reply:** baseline number, post-fix number, delta, artifact path."

### `skills/poteto-mode/playbooks/runtime-forensics.md`

**No ending stated when the mechanism cannot be proven live.** The reply presumes a proven mechanism, and unlike Trace forensics the playbook gives no instruction to mark an unproven finding as a hypothesis. An agent may report an unproven mechanism as proven or have no defined finish.

- [`skills/poteto-mode/playbooks/runtime-forensics.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/runtime-forensics.md#L7), line 7: "3. Prove the mechanism before believing it."
- [`skills/poteto-mode/playbooks/runtime-forensics.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/runtime-forensics.md#L11), line 11: "**Reply:** the signal captured, the reduced finding, how you proved the mechanism, the source location, artifact paths."
- [`skills/poteto-mode/playbooks/trace-forensics.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/trace-forensics.md#L11), line 11: "Otherwise, mark the finding as the strongest hypothesis the artifact supports, not a confirmed cause."

### `skills/statechart/SKILL.md`

**Hand-off contents omit unchecked rules, cut-short charts, and rules without numbered paths.** The hand-off is defined as a list of items, none of which covers rules under 'Rules not checked' or a chart the drawing run cut short (which can accompany exit 0), so the person who must decide can receive an incomplete check without being told. For a rule whose report section has no numbered path, the required 'path as the report numbers it' cannot be given and no alternative is stated.

- [`skills/statechart/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/SKILL.md#L80), line 80: "Add one line for each bug: the rule, the reader's sentence for that rule, and the path as the report numbers it. Say what the model leaves out."
- [`skills/statechart/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/SKILL.md#L69), line 69: "A rule that is not checked can hold or break."
- [`skills/statechart/scripts/backends/report.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/scripts/backends/report.ts#L153), line 153: "`TLC found a counterexample. It is in tlc-${rule.name}.out.`,"
- [`skills/statechart/scripts/backends/report.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/scripts/backends/report.ts#L90), line 90: "`TLC stopped the drawing run with exit ${drawing.status}, so the chart draws only the states that it reached before it stopped.`,"

### `skills/swarm/SKILL.md`

**The done predicate stated in Frame is never checked when aggregating or reporting.** Completion is defined as returning the report; neither Aggregate nor Report says whether the swarm met its done predicate, so an evaluator cannot tell from the required report whether the run succeeded.

- [`skills/swarm/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/swarm/SKILL.md#L20), line 20: "State the done predicate and the artifact or report the swarm must return."
- [`skills/swarm/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/swarm/SKILL.md#L41), line 41: "Return one consolidated in-chat report with a result table, issue one-liners, gaps or dropouts, and the race rule when used."

### `skills/teach/SKILL.md`

**Goal is the person's understanding, but no observable completion condition is given.** The stated requirements constrain the explanation and the conversation, and direct checks of understanding are excluded. An evaluator cannot tell from them whether the goal was reached, and an agent has no stated point at which the teaching is done beyond following the person's lead.

- [`skills/teach/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/teach/SKILL.md#L9), line 9: "The goal is that they understand it, not that you change anything."
- [`skills/teach/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/teach/SKILL.md#L16), line 16: "No quizzes. No pacing theater. Don't print "Pause", don't ask them to say it back"
- [`skills/teach/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/teach/SKILL.md#L21), line 21: "the explanation itself, never a report about what you did or delivered."

## An order is implied or in conflict

An order the work needs is carried only by position or numbering, or two statements give different orders.

### `skills/blast-radius/SKILL.md`

**Arena step has an unclear referent and position relative to Steps 1 to 5.** Listed last, the step does not say whether "it" is the whole analysis run in parallel instead of Steps 1 to 5, or an extra pass after them, so an agent may do the work twice or skip the arena.

- [`skills/blast-radius/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/blast-radius/SKILL.md#L38), line 38: "6. For a big or wide change, run it as an `arena`. Ask more than one model the same question and merge the answers."

### `skills/poteto-mode/playbooks/feature.md`

**Step 6's per-unit build, verify, commit rule overlaps the earlier build and verify steps.** Numbering places this rule after building (step 4) and verifying (step 5), so an agent cannot tell whether to build and verify unit by unit during steps 4 and 5 or to build and check each commit only while rebasing in step 6.

- [`skills/poteto-mode/playbooks/feature.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/feature.md#L12), line 12: "Commit liberally."
- [`skills/poteto-mode/playbooks/feature.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/feature.md#L14), line 14: "6. Rebase into small, ordered commits. Stack follow-ups."
- [`skills/poteto-mode/playbooks/feature.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/feature.md#L15), line 15: "Use the **sequence-verifiable-units** principle skill, building, verifying, and committing each small unit before the next."

### `skills/poteto-mode/playbooks/perf-issue.md`

**Mantra stop rule in step 2 needs measurements produced only in steps 3-4.** Whether a mantra meets the target is known only after a fix is implemented and a post-fix trace compared (steps 3 and 4), yet the stop rule sits in step 2. The playbook does not say whether to loop steps 2 to 4 per mantra or to choose a mantra before planning.

- [`skills/poteto-mode/playbooks/perf-issue.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/perf-issue.md#L7), line 7: "Try the performance mantras in order, cheapest first:"
- [`skills/poteto-mode/playbooks/perf-issue.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/perf-issue.md#L16), line 16: "When an earlier mantra meets the target, stop."
- [`skills/poteto-mode/playbooks/perf-issue.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/perf-issue.md#L18), line 18: "Apply the **sequence-verifiable-units** principle skill, verifying each attempt before trying the next."

### `skills/poteto-mode/playbooks/session-pickup.md`

**Pickup is said to end at step 4, yet step 5 follows it.** An agent cannot tell whether step 5 belongs to the pickup or to the routed playbook, nor whether the verdict to ratify or override a prior conclusion is picked before or after the inherited claims are verified.

- [`skills/poteto-mode/playbooks/session-pickup.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/session-pickup.md#L8), line 8: "pick the verdict: continue the execution, ship a finished recommendation, ratify or override a prior conclusion, or postmortem a failed run. The pickup playbook ends here. The routed playbook owns the rest."
- [`skills/poteto-mode/playbooks/session-pickup.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/session-pickup.md#L9), line 9: "Verify the inherited claims against the original goal on the real artifact (the **principle-prove-it-works** skill)."

### `skills/show-me-your-work/SKILL.md`

**Order of the log audit and the cross-model review is implied only by position.** Both steps are only "before handing back"; if the review runs first, the reviewer reads a trail the audit later supersedes, and its Attention flags may point at rows that are no longer the record.

- [`skills/show-me-your-work/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/show-me-your-work/SKILL.md#L57), line 57: "At the end of the run, before handing back, check the log told the truth."
- [`skills/show-me-your-work/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/show-me-your-work/SKILL.md#L67), line 67: "Before handing back, spawn a subagent on another vendor's model than the one that did the work."
- [`skills/show-me-your-work/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/show-me-your-work/SKILL.md#L63), line 63: "When a row records neither a real decision nor a real action, or its claim or evidence is wrong, add a row that supersedes it"

### `skills/statechart/SKILL.md`

**Bug-path replay has no stated order relative to the hand-off.** SKILL.md puts the replay after the hand-off contents and states no order or result for it, while the guide requires it before the hand-off. An agent following SKILL.md can hand the reader bugs that a replay would show to be modeling errors, and an evaluator cannot tell what the hand-off must say about a bug that did not reproduce.

- [`skills/statechart/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/SKILL.md#L80), line 80: "Give each chart and its Mermaid text to the person who must decide."
- [`skills/statechart/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/SKILL.md#L82), line 82: "If a bug does not occur, think that the model is wrong until you show that it is not."
- [`docs/guide/06-verify-and-ship.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/docs/guide/06-verify-and-ship.md#L126), line 126: "Before the hand-off, the agent reproduces each bug path in the real code, so a modeling error doesn't reach the reader as a bug."

### `skills/tdd/SKILL.md`

**Fallback path does not say to run the check before and after the fix.** Only the Final Response implies that the executable check must fail before the fix and pass after it; an agent following the fallback section may fix first and then lack the failing-before evidence the report asks for. Which Workflow steps the fallback replaces is also left to the heading.

- [`skills/tdd/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/tdd/SKILL.md#L24), line 24: "Use the closest executable regression check instead: a targeted script, manual reproduction command, browser automation, snapshot comparison, log assertion, or focused integration check."
- [`skills/tdd/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/tdd/SKILL.md#L40), line 40: "Name the failing-before test or executable check and the failure it produced."
- [`skills/tdd/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/tdd/SKILL.md#L41), line 41: "Name the passing-after test run and any nearby validation performed."

## A state-changing action lacks a stated condition

The approval, scope, or retry condition of an external, state-changing, or irreversible action is unstated or stated inconsistently.

### `automations/benny/skills/reproduce-and-fix-issues/SKILL.md`

**Confirmed verification posts a source reply without the one-unprompted-reply limit.** When a fix artifact is found after a step 9 repro reply, the Confirmed outcome directs a further source-thread reply while the Insufficient outcome and step 14 limit the run to one; an agent cannot tell whether a second source post is permitted.

- [`automations/benny/skills/reproduce-and-fix-issues/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/SKILL.md#L206), line 206: "For a confirmed repro, run the source preflight and post at most one unprompted source reply:"
- [`automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md#L69), line 69: "Post one concise source-thread reply after the source preflight."
- [`automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md#L79), line 79: "Post the normal confirmed-repro source update if the run has not already used it."
- [`automations/benny/skills/reproduce-and-fix-issues/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/SKILL.md#L299), line 299: "Do not create a second source-channel root or unprompted source reply."

### `automations/benny/skills/triage-issue-reports/SKILL.md`

**Triage requires no source-parent preflight before follow-up replies, unlike repro.** A triage follow-up answer posted to the source thread during the follow-up window has no stated parent check, so a run can reply after the parent was deleted or became inaccessible; the repro skill applies the check to every post.

- [`automations/benny/skills/triage-issue-reports/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/triage-issue-reports/SKILL.md#L18), line 18: "Preflight the source parent before any tracker write and immediately before the verdict post."
- [`automations/benny/skills/triage-issue-reports/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/triage-issue-reports/SKILL.md#L234), line 234: "Answer only a direct question to the triage identity."
- [`automations/benny/skills/reproduce-and-fix-issues/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/reproduce-and-fix-issues/SKILL.md#L17), line 17: "Preflight the source parent before every source-thread post."

### `skills/benchmark-checklist/SKILL.md`

**Stopping whatever is running on a busy machine has no approval or scope.** The text implies the agent should stop other processes when it can, without saying whose processes may be stopped or whether the user must agree, so an agent may terminate unrelated user work.

- [`skills/benchmark-checklist/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/benchmark-checklist/SKILL.md#L17), line 17: "If the machine is busy, find out what is running. If you cannot stop it, interleave the sides so both see the same noise, and say so in the report."

### `skills/create-verification-skill/SKILL.md`

**Fixing a checkout that does not build has no stated scope or approval.** An agent may change product code, dependencies, or configuration outside the generated skill's directory without asking; the sibling maintenance skill forbids product code edits, while this skill sets no limit.

- [`skills/create-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/create-verification-skill/SKILL.md#L21), line 21: "If the checkout doesn't build or start as-is, fix that first (or report it precisely) before generating"
- [`skills/maintain-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-verification-skill/SKILL.md#L21), line 21: "Never edit product code during a run"

### `skills/maintain-formal-verification-skill/SKILL.md`

**Required separate change leaves commit, branch, push, and approval unstated.** An agent may leave the edits uncommitted, commit on the current branch, or create and push a branch or pull request; which is expected and whether the user must approve it is not stated.

- [`skills/maintain-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-formal-verification-skill/SKILL.md#L58), line 58: "Put the verification updates in a change of their own, separate from any product fix."
- [`skills/maintain-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-formal-verification-skill/SKILL.md#L42), line 42: "Do not commit it to the product code."

### `skills/maintain-verification-skill/SKILL.md`

**PR approval, branch, and fate of unshipped edits are unstated.** The agent edits files during the pass and may open a PR with no stated approval or branch/remote condition; on a `blocked` or `clean` ending it cannot tell whether to keep, revert, or report edits already made.

- [`skills/maintain-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-verification-skill/SKILL.md#L37), line 37: "For changed: one PR of proven corrections, re-read every changed file first. For clean or blocked: no PR, report the outcome and the coverage honestly."
- [`skills/maintain-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-verification-skill/SKILL.md#L27), line 27: "Fix missing, extra, duplicate, or dead entries."
- [`skills/maintain-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/maintain-verification-skill/SKILL.md#L33), line 33: "fix it under edit scope and retry once"

### `skills/no-comments/SKILL.md`

**Revert of a rejected report has no method, baseline, or failure-path end state.** The agent's edits land in files that can hold the caller's uncommitted changes, and no snapshot is taken before spawning, so a file-level revert can discard the caller's work; after the second rejection, whether its edits are reverted is unstated.

- [`skills/no-comments/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/no-comments/SKILL.md#L15), line 15: "Otherwise use the current diff against the base branch, default `main`, including the working tree."
- [`skills/no-comments/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/no-comments/SKILL.md#L20), line 20: "Revert and rerun one rejected report with the failure named. Reject a second, report it open, and fail `/no-comments`."
- [`agents/comment-sicko.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/agents/comment-sicko.md#L32), line 32: "Name touched files, deletion count, `MUST KILL` flags with one line each, and skips."

### `skills/poteto-mode/SKILL.md`

**Session overrides do not say whether they lift the pause for irreversible writes.** Under "going to bed" or "be fully autonomous", an agent reaching a deploy or force-push to a shared branch cannot tell whether to wait for the user or proceed, and an evaluator cannot tell which behavior complied.

- [`skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/SKILL.md#L78), line 78: "**Always pause** for irreversible writes: force-push to shared branches, deploys, data deletion, customer messages."
- [`skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/SKILL.md#L80), line 80: "**Session overrides:** "Don't stop" / "going to bed" / "run until done" / "be fully autonomous" → keep going."
- [`docs/guide/07-overnight.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/docs/guide/07-overnight.md#L31), line 31: ""im going to bed" is a session override. The agent stops asking and keeps going."

### `skills/poteto-mode/playbooks/autopilot-full.md`

**The operator's go is required but its scope over spawning and merging is unstated.** The only action explicitly tied to the go is arming the audit loop, so an agent cannot tell whether spawning owners, which push, open PRs, and merge, must wait for the go or may start once the plan is stated.

- [`skills/poteto-mode/playbooks/autopilot-full.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/autopilot-full.md#L7), line 7: "A request to state the plan is not a go."
- [`skills/poteto-mode/playbooks/autopilot-full.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/autopilot-full.md#L8), line 8: "Spawn one owner per PR, and keep its work where a replacement can find it."
- [`skills/poteto-mode/playbooks/autopilot-full.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/autopilot-full.md#L22), line 22: "On the operator's go, arm `/loop 1h` to audit until no delegated work is left"

### `skills/poteto-mode/playbooks/bug-fix.md`

**Failed verification is flagged, but whether the PR step still runs is unstated.** Neither playbook says where the flag goes or whether the later steps, including opening a PR, proceed after a non-pass. An agent may open a PR for an unverified fix or stop, and an evaluator cannot tell which ending is correct.

- [`skills/poteto-mode/playbooks/bug-fix.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/bug-fix.md#L10), line 10: ""Inconclusive" or wrong-surface is not a pass. Flag it."
- [`skills/poteto-mode/playbooks/bug-fix.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/bug-fix.md#L13), line 13: "6. Run **Opening a PR**."
- [`skills/poteto-mode/playbooks/perf-issue.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/perf-issue.md#L19), line 19: ""Inconclusive" or wrong-surface is not a pass. Flag it."
- [`skills/poteto-mode/playbooks/perf-issue.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/perf-issue.md#L21), line 21: "6. Run **Opening a PR**."

### `skills/poteto-mode/playbooks/pause-safely.md`

**Unclear whether the wip checkpoint is pushed when a PR is already out.** The exception does not say whether pushing the possibly broken `wip:` commit is then expected or only allowed, so one agent leaves the checkpoint local, where a cold-start agent on another machine cannot reach it, and another pushes it to an open PR.

- [`skills/poteto-mode/playbooks/pause-safely.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/pause-safely.md#L6), line 6: "Take no irreversible action to pause. No PR and no push unless you already had one out."
- [`skills/poteto-mode/playbooks/pause-safely.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/pause-safely.md#L7), line 7: "Commit uncommitted edits as one clear `wip:` commit on the current branch so nothing is lost."
- [`skills/poteto-mode/playbooks/pause-safely.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/pause-safely.md#L3), line 3: "Leave a checkpoint a cold-start agent can resume from."

### `skills/poteto-mode/playbooks/runtime-forensics.md`

**Work labeled read-only permits injecting into and hotfixing the live process.** Step 3 changes the state of a running process with no stated condition on which process may be modified or whether to revert, while the checkpoint calls the work read-only. An agent cannot tell whether a live hotfix is permitted without asking, or whether it counts as the excluded fix.

- [`skills/poteto-mode/playbooks/runtime-forensics.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/runtime-forensics.md#L7), line 7: "Inject instrumentation via CDP eval on the running process, or hotfix the live code without reloading, to confirm the hypothesis cheaply."
- [`skills/poteto-mode/playbooks/runtime-forensics.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/runtime-forensics.md#L9), line 9: "`throughput checkpoint: n/a, read-only forensics`"
- [`skills/poteto-mode/playbooks/runtime-forensics.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/runtime-forensics.md#L11), line 11: "No fix unless asked."

### `skills/poteto-mode/playbooks/shipping.md`

**Shipping force-pushes stack branches without the pause SKILL.md requires for shared branches.** Neither file says whether an open PR branch in a stack is a shared branch. An agent may force-push each retargeted PR without pausing, or pause before every push, and the approval condition cannot be judged from the text.

- [`skills/poteto-mode/playbooks/shipping.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/shipping.md#L8), line 8: "move its patch onto the merge result, and push with `--force-with-lease`."
- [`skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/SKILL.md#L78), line 78: "**Always pause** for irreversible writes: force-push to shared branches, deploys, data deletion, customer messages."
- [`skills/poteto-mode/worker.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/worker.md#L7), line 7: "Stop only for a deploy, deleted data, a force-push to a shared branch, or a message to someone outside the run."

### `skills/poteto-mode/playbooks/worktree-cleanup.md`

**Pruning of clean, unmerged, unused worktrees has no stated approval condition.** Step 4 decides only merged-clean-unused (proceed) and wip or in-use (pause), so an agent cannot tell whether a clean but unmerged worktree (audit `review`, `hold-open-pr`, or `safe` because any non-open PR state counts) may be pruned, must pause, or must be kept. The README counts abandoned worktrees as targets, and the Reply has no reason category for holding such a worktree back.

- [`skills/poteto-mode/playbooks/worktree-cleanup.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/worktree-cleanup.md#L6), line 6: "Per Autonomy, clean and merged and not-in-use proceeds. `wip` and in-use pause."
- [`skills/poteto-mode/scripts/worktree-audit.sh`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/scripts/worktree-audit.sh#L125), line 125: "elif [ "$merged" = YES ] || [ "$pr" != "-" ]; then bucket=safe"
- [`README.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/README.md#L90), line 90: "reclaim disk by pruning merged or abandoned worktrees and stale ios simulators, safety-gated."
- [`skills/poteto-mode/playbooks/worktree-cleanup.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/worktree-cleanup.md#L12), line 12: "a one-line reason for each held back (in-use by which chat, or uncommitted work)."

**Step 5's no-commits-lost claim fails for detached worktrees the audit reports.** A clean worktree on a detached HEAD has no branch, so commits made there are referenced by no branch once `git worktree remove --force` deletes it. An agent relying on the stated guarantee will not check such a worktree for unreferenced commits before pruning.

- [`skills/poteto-mode/playbooks/worktree-cleanup.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/worktree-cleanup.md#L7), line 7: "Branch refs survive, so no commits are lost."
- [`skills/poteto-mode/playbooks/worktree-cleanup.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/worktree-cleanup.md#L6), line 6: "since removing a clean worktree is recoverable from its branch but uncommitted work is gone."
- [`skills/poteto-mode/scripts/worktree-audit.sh`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/scripts/worktree-audit.sh#L100), line 100: "if [ -z "$branch" ]; then remote=detached"

**Step 6 deletions have no approval condition and an undefined need threshold.** An agent cannot tell whether deleting all testing simulators, old runtimes, and the listed caches proceeds without asking (step 6 states no gate) or must pause under Autonomy's data-deletion rule, which step 4 applies to worktrees only. It also cannot tell which runtimes count as old or when the further reclaimers are needed, since no disk target is stated.

- [`skills/poteto-mode/playbooks/worktree-cleanup.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/worktree-cleanup.md#L8), line 8: "`xcrun simctl --set testing delete all` (XCTestDevices clones), `xcrun simctl delete unavailable`, and `xcrun simctl runtime list` then `runtime delete <id>` for old runtimes."
- [`skills/poteto-mode/playbooks/worktree-cleanup.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/worktree-cleanup.md#L8), line 8: "More when needed: Xcode `DerivedData` and `iOS DeviceSupport`"
- [`skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/SKILL.md#L78), line 78: "**Always pause** for irreversible writes: force-push to shared branches, deploys, data deletion, customer messages."
- [`skills/poteto-mode/playbooks/worktree-cleanup.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/worktree-cleanup.md#L10), line 10: "This is the one playbook that deletes user state with no code review to catch a slip, so the gates above are the review."

### `skills/principle-never-block-on-the-human/SKILL.md`

**Confirmation list for irreversible and external actions differs from poteto-mode Autonomy section.** An agent following both files cannot tell whether a team-chat or ticket message, a force-push to its own branch, or a deploy needs confirmation, since one file requires it where the other does not, or omits the action.

- [`skills/principle-never-block-on-the-human/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-never-block-on-the-human/SKILL.md#L13), line 13: "Irreversible actions (force-push, delete production data, send external messages) still require confirmation."
- [`skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/SKILL.md#L76), line 76: "Reversible work and external actions (team chat, ticket updates, kicking off evals) proceed without asking."
- [`skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/SKILL.md#L78), line 78: "**Always pause** for irreversible writes: force-push to shared branches, deploys, data deletion, customer messages."

### `skills/statechart/SKILL.md`

**Replay as a test or live repro has no stated scope or approval.** The scratch-folder rule sits in the Run section with no stated scope, and the replay names a test or a live repro without saying where either runs. An agent cannot tell whether it may add a test to the repository or act on a running system, or what approval either needs.

- [`skills/statechart/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/SKILL.md#L13), line 13: "Work in a scratch folder outside the repo. Write a TLA+ spec and its config."
- [`skills/statechart/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/SKILL.md#L82), line 82: "replay each bug path against the real code, as a test or a live repro, one step for each action."

## The tool behaves differently from the text

A bundled tool's behavior differs from what the text says about it, or the text omits a fact that changes how the tool's result must be read. The tool-use references state the verified behavior.

### `skills/create-formal-verification-skill/SKILL.md`

**Description of /statechart differs from what the bundled statechart tool does.** The tool runs TLC itself on a spec and config rather than reading another checker's result, and on a passing check above 500 states (CHART_STATES = 500 in scripts/ir.ts; observed: 1,600-state passing model, exit 0, no chart.mmd) it draws no chart. A generated skill written from this text can promise a read-out or chart the tool does not produce.

- [`skills/create-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/create-formal-verification-skill/SKILL.md#L35), line 35: "tell the next agent to read every result with the pstack [`/statechart`]\(../statechart/SKILL.md) skill."
- [`skills/create-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/create-formal-verification-skill/SKILL.md#L35), line 35: "When the check passes, `/statechart` draws a chart of how the system moves between states."
- [`skills/statechart/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/SKILL.md#L13), line 13: "Write a TLA+ spec and its config. Then run:"
- [`skills/statechart/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/SKILL.md#L74), line 74: "The chart has a budget of 500 states, counted by TLC on the config as written. Above that, the chart draws only the paths to the rules that break, and when no rule breaks, the command writes no `chart.mmd`."

### `skills/poteto-mode/playbooks/babysit.md`

**Babysit requires reporting a stale base; the named watcher never reports one.** The watcher's only branch-state blocker is a conflict (`CONFLICTING` or `DIRTY`); a `BEHIND` PR yields READY (facts report, run). An agent that takes status from the watcher, as instructed, will not detect a stale base and will not stop for it.

- [`skills/poteto-mode/playbooks/babysit.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/babysit.md#L7), line 7: "Report a conflict or a stale base with the branch that needs the rebase, and stop."
- [`skills/poteto-mode/playbooks/babysit.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/babysit.md#L6), line 6: "On GitHub, status comes from the mode's watcher at `scripts/watch-pr/watch-pr`."
- [`skills/poteto-mode/scripts/watch-pr/policy.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/scripts/watch-pr/policy.ts#L144), line 144: "row.facts.mergeStateStatus === "DIRTY" ||"

**Watcher invocation is given only for `check`; `threads-only` has no matching watcher result.** No flags are given for `drive` or `threads-only`. A default watch reports only the first blocker in the order conflict, threads, CI, so in `threads-only` a conflicted PR returns a conflict and no threads; the threads are visible only in `--status-only` rows (facts report, sections 1 and 8).

- [`skills/poteto-mode/playbooks/babysit.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/babysit.md#L6), line 6: "In `check` mode pass `--status-only`."
- [`skills/poteto-mode/playbooks/babysit.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/babysit.md#L5), line 5: "`threads-only` touches only review threads"
- [`skills/poteto-mode/scripts/watch-pr/policy.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/scripts/watch-pr/policy.ts#L223), line 223: "conflictBlocker(row),"

**`check` is described as one status pass; `--status-only` retries and can end without status.** `--status-only` runs inside the retry loop, so a read failure, including a PR with no checks at all, produces RETRY lines and about 720 s of default backoff before exit 7 (or exit 5 under `--timeout`) with no STATUS row (facts report, runs). An agent expecting a single quick pass cannot tell a slow or failed read from a hang, and may report no status.

- [`skills/poteto-mode/playbooks/babysit.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/babysit.md#L5), line 5: "`check` is one status pass and a report."
- [`skills/poteto-mode/scripts/watch-pr/cli.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/scripts/watch-pr/cli.ts#L129), line 129: ".option("--status-only", "print one status table and exit 0", false)"
- [`skills/poteto-mode/scripts/watch-pr/policy.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/scripts/watch-pr/policy.ts#L519), line 519: "return pollUntilTerminal({"
- [`skills/poteto-mode/scripts/watch-pr/github.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/scripts/watch-pr/github.ts#L26), line 26: "super({ kind: "checks-unavailable", retryable: true, detail });"

### `skills/poteto-mode/playbooks/shipping.md`

**Queued watcher never exits at a ready frontier; step 4 has the agent merge.** A blocker-free frontier yields one non-terminal WAITING line and the watcher keeps polling, with no deadline by default, until something else merges the PR (facts report, section 2.5 and run). The text does not say how the agent's per-PR merge, retarget, and push interleave with a watch that runs until COMPLETE, so an agent waiting for the watcher to return can wait without bound.

- [`skills/poteto-mode/playbooks/shipping.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/shipping.md#L8), line 8: "Always merge the run's lowest unmerged PR, with `origin pr merge <pr>` or `gh pr merge <pr> --squash`."
- [`skills/poteto-mode/playbooks/shipping.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/shipping.md#L9), line 9: "watch the run with `scripts/watch-pr/watch-pr --queued-stack` under `/loop` until it reports `COMPLETE` at the ceiling."
- [`skills/poteto-mode/scripts/watch-pr/policy.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/scripts/watch-pr/policy.ts#L699), line 699: "? ({ kind: "merge-queue", unmergedCount: active.length } as const)"
- [`skills/poteto-mode/scripts/watch-pr/policy.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/scripts/watch-pr/policy.ts#L829), line 829: "return { kind: "sleep", seconds: args.options.interval };"

**Watcher COMPLETE counts a PR merged into its parent branch as merged.** The watcher does not check the base branch, so `COMPLETE` at the ceiling, step 5's stopping condition, can be reported when a PR landed in its parent's branch rather than trunk (facts report, run). COMPLETE alone does not establish what step 4 defines as landed.

- [`skills/poteto-mode/playbooks/shipping.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/shipping.md#L8), line 8: "A landed PR reads merged with trunk as its base, not its parent's branch."
- [`skills/poteto-mode/scripts/watch-pr/policy.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/scripts/watch-pr/policy.ts#L66), line 66: "if (facts.state === "MERGED" || facts.mergedAt !== null)"

### `skills/poteto-mode/scripts/worktree-audit.sh`

**Audit's chat and PR columns can be silently empty, hiding in-use and open-PR worktrees.** With `rg`, `jq`, or a working `gh` missing, no transcript directory, or a host that stores transcripts elsewhere (the Claude Code adapter maps them to `~/.claude/projects/`, which the script never searches), every LAST_CHAT or PR cell reads `-` with exit 0 and no message, so no row becomes `verify-recent-chat` or `hold-open-pr` and step 3 is never triggered. The playbook does not say that `-` can mean not searched, leaving step 2's pinned-set cross-check as the only guard.

- [`skills/poteto-mode/playbooks/worktree-cleanup.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/worktree-cleanup.md#L3), line 3: "It classifies each worktree by size, age, merge state, uncommitted work, PR state, and the newest chat that touched it, then suggests a bucket."
- [`skills/poteto-mode/playbooks/worktree-cleanup.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/worktree-cleanup.md#L5), line 5: "For every `verify-recent-chat` row, or anything you doubt, fan subagents out to read the transcripts"
- [`skills/poteto-mode/scripts/worktree-audit.sh`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/scripts/worktree-audit.sh#L74), line 74: "transcripts="$HOME/.cursor/projects/$slug/agent-transcripts""
- [`skills/poteto-mode/scripts/worktree-audit.sh`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/scripts/worktree-audit.sh#L115), line 115: "f=$(rg -l -e "${wt}/" -e "${wt}\"" "$transcripts" 2>/dev/null \"
- [`skills/poteto-mode/scripts/worktree-audit.sh`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/scripts/worktree-audit.sh#L70), line 70: "[ -s "$prs" ] || echo "[]" > "$prs""
- [`docs/harness/claude-code.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/docs/harness/claude-code.md#L57), line 57: "Transcripts in `~/.cursor/projects/<slug>/agent-transcripts/` | `~/.claude/projects/<slug>/<session>.jsonl`."

### `skills/statechart/SKILL.md`

**Chart budget is not counted on the config as written, as stated.** The number compared with 500 is the largest over all verdict runs, including reruns with broken rules removed; the facts report observed tlc.out showing 8 distinct states while the report said the model exceeded the budget. An agent that sizes a model by the run on the config as written, or by tlc.out, can expect a whole chart and get only bug paths.

- [`skills/statechart/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/SKILL.md#L74), line 74: "The chart has a budget of 500 states, counted by TLC on the config as written."
- [`skills/statechart/scripts/run.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/scripts/run.ts#L373), line 373: "states.distinct = Math.max(states.distinct, distinct);"
- [`skills/statechart/scripts/run.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/scripts/run.ts#L437), line 437: "if (judged.states.distinct <= CHART_STATES) {"

**Description promises a shortest path per bad state; the report gives one per rule.** The report keeps the first state reached for each broken rule and, for a PROPERTY, gives TLC's counterexample rather than a computed shortest path. A reader or evaluator relying on the description expects a path for every marked state and a shortest path for every rule.

- [`skills/statechart/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/SKILL.md#L3), line 3: "The report gives the shortest path to each state that breaks a rule."
- [`skills/poteto-help/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-help/SKILL.md#L92), line 92: "with the shortest path to each state that breaks a rule"
- [`skills/statechart/scripts/passes/reach.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/scripts/passes/reach.ts#L121), line 121: "if (!first.has(k) && (ends.get(k) ?? ids[i]) === ids[i]) first.set(k, { rule, i });"
- [`skills/statechart/scripts/backends/report.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/scripts/backends/report.ts#L136), line 136: ": `The shortest path has ${steps}:`,"

**Exit statuses, including exit 1 for a found bug, are not stated.** The exit codes appear only in the script's usage text, which is printed after an argument error. An agent following SKILL.md can read exit 1, the normal result when a bug is found, as a tool failure, and is not told that exit 2 means nothing was written.

- [`skills/statechart/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/SKILL.md#L16), line 16: "<skill dir>/scripts/statechart SPEC.tla [--config FILE] [--view FILE] [--out DIR]"
- [`skills/statechart/scripts/statechart.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/scripts/statechart.ts#L21), line 21: "Exit code: TLC's own on the config as written: 0 when every rule holds, 1 when a rule breaks,"
- [`skills/statechart/scripts/statechart.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/scripts/statechart.ts#L23), line 23: "Only exits 0 and 1 write output."

**Install statement omits the mise prerequisite and the TLA2TOOLS alternative.** The command installs nothing unless mise is already on PATH; without it the run exits 2 ('Cannot find TLC: mise install failed: spawn mise ENOENT', observed in the facts report). An agent following SKILL.md alone has no stated way to proceed, and is not told that setting TLA2TOOLS (and JAVA) avoids the install and the network.

- [`skills/statechart/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/SKILL.md#L21), line 21: "The first run installs TLC and Java with mise and needs the network."
- [`skills/statechart/scripts/run.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/scripts/run.ts#L196), line 196: "if (TLA2TOOLS) return { jar: TLA2TOOLS, java: JAVA || "java" };"
- [`skills/statechart/scripts/run.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/scripts/run.ts#L206), line 206: "Cannot find TLC: mise install failed:"

## The work depends on something that is not bundled

A step needs a host feature or another plugin's skill that pstack does not bundle and for which the text gives no fallback or adapter mapping.

### `skills/blast-radius/SKILL.md`

**Bare backtick skill names get no Claude Code adapter mapping.** The generator only detects "the **name** skill" or `/name`, so the Claude Code copy of blast-radius gets no adapter line, and arena and unslop both set disable-model-invocation: true; an agent there has no stated way to run them.

- [`skills/blast-radius/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/blast-radius/SKILL.md#L38), line 38: "run it as an `arena`."
- [`skills/blast-radius/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/blast-radius/SKILL.md#L48), line 48: "Write it through `unslop`, cite real code, and strip anything private before it goes anywhere public."
- [`../scripts/generate-pstack-harness-trees.mjs`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/../scripts/generate-pstack-harness-trees.mjs#L72), line 72: "const route = new RegExp(`the \\*\\*(?<bold>${others})\\*\\* skill|\`/(?<command>${others})\``, "g");"
- [`docs/harness/claude-code.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/docs/harness/claude-code.md#L12), line 12: "| Run another pstack skill (`/name` or "the **name** skill") | `Read` `<pstack>/skills/<name>/SKILL.md` and follow it. The `Skill` tool refuses most pstack skills."

### `skills/create-formal-verification-skill/SKILL.md`

**Generated skill must route results through /statechart, which is not model-invocable.** The next agent working from the project-local skill has no path or command for the tool, and the skill it is told to use is marked not to be invoked by the model; whether it can run without the user typing /statechart, or where pstack is not installed, is unstated and has no fallback.

- [`skills/create-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/create-formal-verification-skill/SKILL.md#L35), line 35: "Refer to `/statechart` by name. Its commands, options, and file paths change between releases and machines, so copy none of them into the generated skill or its scripts."
- [`skills/statechart/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/statechart/SKILL.md#L4), line 4: "disable-model-invocation: true"
- [`skills/automate-me/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/automate-me/SKILL.md#L73), line 73: "Frontmatter `disable-model-invocation: true` by default. Opt out only if the user explicitly wants their mode to apply on every turn."

### `skills/ketchup/SKILL.md`

**Charts for numbers require /visualize, which pstack does not bundle or define.** No skill or command named visualize exists anywhere in the pstack tree, and no fallback is given, so on a host without it an agent cannot follow the chart instruction as written and must choose between another charting means and omitting the chart.

- [`skills/ketchup/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/ketchup/SKILL.md#L43), line 43: "Draw diagrams and charts from facts you have: a Mermaid diagram for how things connect and a `/visualize` chart for numbers."
- [`skills/ketchup/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/ketchup/SKILL.md#L37), line 37: "A visual is a picture: a screenshot, a video, a Mermaid diagram, a chart or diagram from `/visualize`, or a generated image."

### `skills/poteto-mode/SKILL.md`

**Mandatory pre-commit and shipping steps rely on an unbundled plugin with no fallback.** The README treats cursor-team-kit as optional, yet the Non-negotiables require it before every commit and when shipping UI or CLI work; an agent without it must either skip a non-negotiable or improvise, and the agent-facing text says neither.

- [`skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/SKILL.md#L24), line 24: "Before commit → `/deslop` from the `cursor-team-kit` plugin. Before review → **no-comments**."
- [`skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/SKILL.md#L25), line 25: "Shipping UI / IDE / CLI → `control-ui` or `control-cli` from `cursor-team-kit`."
- [`README.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/README.md#L260), line 260: "a few things `poteto-mode` references but doesn't bundle:"
- [`README.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/README.md#L266), line 266: "install `cursor-team-kit` alongside pstack if you want the full set."

### `skills/poteto-mode/playbooks/authoring-a-skill.md`

**Step 1 requires Cursor's built-in create-skill, with no fallback on other hosts.** In Claude Code the harness mapping for another skill points to `<pstack>/skills/create-skill/SKILL.md`, which is not bundled, and no row maps the Cursor built-in, so an agent there has no stated way to perform step 1.

- [`skills/poteto-mode/playbooks/authoring-a-skill.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/authoring-a-skill.md#L5), line 5: "1. Use the **create-skill** skill (Cursor's built-in for authoring SKILL.md files)."
- [`skills/poteto-help/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-help/SKILL.md#L116), line 116: "`/loop` and `/create-skill` are Cursor built-ins."
- [`docs/harness/claude-code.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/docs/harness/claude-code.md#L12), line 12: "`Read` `<pstack>/skills/<name>/SKILL.md` and follow it."

### `skills/poteto-mode/playbooks/autonomous-run.md`

**The wake mechanism requires Cursor's /loop, which the Claude Code adapter does not map.** The Claude Code adapter has no row or skip rule for `/loop`, so an agent on that host cannot tell how to keep an autonomous run or the Autopilot-full audit loop awake, or whether to skip the step.

- [`skills/poteto-mode/playbooks/autonomous-run.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/autonomous-run.md#L6), line 6: "Pick the wake mechanism using Cursor's `/loop` command (a built-in, not a pstack skill)."
- [`skills/poteto-mode/playbooks/autopilot-full.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/autopilot-full.md#L22), line 22: "On the operator's go, arm `/loop 1h` to audit until no delegated work is left"
- [`docs/harness/claude-code.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/docs/harness/claude-code.md#L3), line 3: "If a Cursor field has no row, drop it and say so."
- [`docs/harness/claude-code.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/docs/harness/claude-code.md#L61), line 61: "Claude Code has no Cursor Automations, Bugbot, Cursor cloud agents, or built-in PR tool."
- [`skills/poteto-help/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-help/SKILL.md#L48), line 48: "and Custom Modes and `/loop` are Cursor features, so those parts may not work there."

### `skills/poteto-mode/playbooks/autopilot-full.md`

**Decision trail and agent records depend on a store path the system prompt supplies.** Where the system prompt names no such path, as the Claude Code adapter does not provide, an owner cannot tell where the shared trail goes; the cited skill's default location is per work directory, so the root and replacements may not find the records they probe.

- [`skills/poteto-mode/playbooks/autopilot-full.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/autopilot-full.md#L12), line 12: "push and start a decision trail in the root agent's store (path in the system prompt) per the **show-me-your-work** skill"
- [`skills/poteto-mode/playbooks/autopilot-full.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/autopilot-full.md#L12), line 12: "Whoever spawns a subagent records its id, state, and a stuck-after runtime from past runs of its kind in that store, so the root can probe it if the parent dies."
- [`skills/show-me-your-work/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/show-me-your-work/SKILL.md#L46), line 46: "Keep it at `decisions.tsv` in the work dir, or `.audit/<task-slug>.tsv` when several efforts run at once, and leave it out of git."

### `skills/poteto-mode/playbooks/babysit.md`

**The watcher needs Bun and a first-run install, which no pstack text states.** Without Bun on PATH, an authenticated `gh`, and a writable skill folder with registry access on first run, the watcher exits 1 with no verdict (facts report, section 3). Babysit gives no GitHub fallback, so the agent has no stated status source in that environment.

- [`skills/poteto-mode/scripts/watch-pr/watch-pr`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/scripts/watch-pr/watch-pr#L1), line 1: "#!/usr/bin/env bun"
- [`skills/poteto-mode/scripts/bootstrap.ts`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/scripts/bootstrap.ts#L36), line 36: "[process.execPath, "install", "--frozen-lockfile"],"
- [`skills/poteto-mode/playbooks/babysit.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/babysit.md#L6), line 6: "On GitHub, status comes from the mode's watcher at `scripts/watch-pr/watch-pr`."

### `skills/poteto-mode/playbooks/visual-parity.md`

**Visual verification depends on unbundled control skill with no fallback.** The parity claim in Visual parity and the visual evidence in Prototype both rest on a skill that pstack does not bundle, and neither playbook names another way to capture the screenshots or diffs. Without cursor-team-kit an agent must improvise the verification surface, and an evaluator cannot tell what evidence satisfies the step.

- [`skills/poteto-mode/playbooks/visual-parity.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/visual-parity.md#L8), line 8: "Verify each component against its baseline via image diff on the matching surface via the control skill."
- [`skills/poteto-mode/playbooks/prototype.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/prototype.md#L11), line 11: "For a visual decision, screenshot each variant via the control skill and drive the interaction."
- [`README.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/README.md#L263), line 263: "`control-cli` (for CLIs and TUIs) and `control-ui` (for browser, Electron, web) ship in `cursor-team-kit` too."

### `skills/teach/SKILL.md`

**Requires invoking how and why, which are marked disable-model-invocation, with no stated means.** Both required skills are flagged against model invocation, and the bundle elsewhere describes such skills as loading only from a slash command. teach gives no path or mechanism for the agent to run them, let alone in parallel, so an agent may skip them or redo their work itself.

- [`skills/teach/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/teach/SKILL.md#L11), line 11: "Those are real skill invocations that do their own digging."
- [`skills/teach/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/teach/SKILL.md#L14), line 14: "Run them in parallel and combine the results."
- [`skills/how/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/how/SKILL.md#L4), line 4: "disable-model-invocation: true"
- [`skills/why/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/why/SKILL.md#L4), line 4: "disable-model-invocation: true"
- [`skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/SKILL.md#L20), line 20: "The operator's rules live in skills that only load from a slash command, so they reach another agent no other way."

**Spatial ideas require an unnamed image-generation tool, and the text excludes a fallback.** On a host without image generation, step 5 cannot be met for a spatial idea, and the text gives no permitted substitute. An agent must either violate the instruction or improvise a fallback.

- [`skills/teach/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/teach/SKILL.md#L17), line 17: "reach for the image-generation tool and draw it marker-on-whiteboard style with a few short labels"
- [`skills/teach/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/teach/SKILL.md#L17), line 17: "Generate that picture, don't settle for describing it in words."

## A citation does not resolve

A cited part does not exist, is not bundled, or does not say what the citing text relies on.

### `skills/poteto-mode/playbooks/eval.md`

**Eval cites arena phases for model choice that do not state it.** The cited Phase B names no models (runner selection is in Phase A step 3, which Eval does not cite), and Phase C's rule is relative to the parent's vendor while Eval says only "a different model family". Under arena's defaults the judge can share a family with a candidate, so whether the judge must differ from the parent or from every candidate is unresolved.

- [`skills/poteto-mode/playbooks/eval.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/eval.md#L20), line 20: "**Spawn N parallel candidates** on different models per the **arena** skill's Phase B."
- [`skills/arena/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/arena/SKILL.md#L22), line 22: "Spawn all N subagents in one message with `run_in_background: true`, each with the task, the path to the shared grounding, its own output path"
- [`skills/arena/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/arena/SKILL.md#L17), line 17: "Pick the runners from the `arena runners` line in `~/.cursor/rules/pstack-models.mdc`, by default `claude-fable-5-2-high`, `claude-opus-5-5-high-fast`, and `gemini-4-neon-high`."
- [`skills/poteto-mode/playbooks/eval.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/eval.md#L21), line 21: "**Spawn one blinded judge** on a different model family per the **arena** skill's Phase C."
- [`skills/arena/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/arena/SKILL.md#L28), line 28: "The judge is never from the parent's vendor, and Fable counts as Claude for that check, so use the first entry from another vendor."

### `skills/principle-minimize-reader-load/SKILL.md`

**Triage skill applies a code-defined principle to a prose verdict.** The cited skill's rules and test (wrappers, state scope, "where does X come from?") are stated for code, so an agent writing a Slack verdict cannot tell which of them apply or how the verdict is judged against it.

- [`automations/benny/skills/triage-issue-reports/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/automations/benny/skills/triage-issue-reports/SKILL.md#L28), line 28: "Apply pstack's `principle-minimize-reader-load` and `unslop` skills to the final verdict."
- [`skills/principle-minimize-reader-load/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-minimize-reader-load/SKILL.md#L9), line 9: "Reader load is the work a reader must do to understand code."

## Shared information has unstated readers or writers

Information written by one skill and read by others, where the text leaves the relationship unstated.

### `skills/poteto-mode/playbooks/pause-safely.md`

**Resume note location is given only for an undefined compaction trigger.** "The compaction trigger" is defined nowhere upstream, and for other pauses the note has no stated place; Session pickup, which the guide names as the note's reader, lists trail forms that do not include it, so a resuming agent may not find the note.

- [`skills/poteto-mode/playbooks/pause-safely.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/pause-safely.md#L3), line 3: "This is explicit only."
- [`skills/poteto-mode/playbooks/pause-safely.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/pause-safely.md#L8), line 8: "Write the resume note off-context."
- [`skills/poteto-mode/playbooks/pause-safely.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/pause-safely.md#L8), line 8: "For the compaction trigger write it to a file like `/tmp/<slug>-resume.md`."
- [`skills/poteto-mode/playbooks/session-pickup.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/session-pickup.md#L5), line 5: "a cloud-agent URL, or a pushed branch."
- [`docs/guide/07-overnight.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/docs/guide/07-overnight.md#L40), line 40: "A fresh chat picks the work up from that note through the Session pickup playbook."

### `skills/poteto-mode/references/bugbot-triage.md`

**Babysit runs append and promote skip patterns in the bundled rubric, unreviewed.** The file every later triage reads as its dismissal rubric is changed by the runs that apply it. It does not say which copy to edit (the installed plugin or the source repository), who reviews a promotion, or how a new skip pattern affects later dismissals.

- [`skills/poteto-mode/references/bugbot-triage.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/references/bugbot-triage.md#L88), line 88: "Append new candidate learnings here during or after babysitting when they look team-useful but not yet mature."
- [`skills/poteto-mode/references/bugbot-triage.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/references/bugbot-triage.md#L88), line 88: "Prefer promoting recurring candidates into the section above once several PRs confirm the pattern."

## The objective is not stated

The file never says why the work is done, so the conversion inferred the Purpose.

### `skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md`

**Body omits the central migrate-and-delete rule; it appears only in frontmatter description.** The body's only instruction concerns tests; the rule the skill is named for and that refactoring.md cites ('same wave', no compatibility layers) exists only in the description. An agent given the body without the frontmatter sees only the title's wording and must infer the objective.

- [`skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md#L3), line 3: "Migrate callers and delete the old API in the same wave instead of preserving compatibility layers."
- [`skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md#L9), line 9: "- Update tests to assert the new contract, and delete tests that only protect pre-refactor implementation details"
- [`skills/poteto-mode/playbooks/refactoring.md`](https://github.com/cursor/plugins/blob/e58dd043600587dbaf58ba315e7f2b38373eeb43/pstack/skills/poteto-mode/playbooks/refactoring.md#L11), line 11: "migrate every caller and delete the old API in the same wave (**principle-migrate-callers-then-delete-legacy-apis**)"
