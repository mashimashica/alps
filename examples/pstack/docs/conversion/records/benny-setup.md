# Conversion record: Benny: setup

[Conversion guide](../README.md)

## `automations/benny/skills/setup-benny/SKILL.md`

Title: Set up Benny. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Configure Benny for a target repository and prepare its triage and repro automations to run there. Benny needs external configuration and two live Cursor automations.

| Outcome | Basis in the upstream text |
| --- | --- |
| `<target-repository>/.cursor/automations/benny/` contains `FOR_AGENTS.md`, this setup file, both operational files, their references, and the templates. | Step 1, merge list item 6: "Verify that the destination contains `FOR_AGENTS.md`, this setup file, both operational files, their references, and the templates." Also step 1: "If this file is already being read from the target destination, treat the copy as complete and run the same verification before continuing." |
| For a fresh agent rooted in the target repository, every shared pstack skill that section 1 lists resolves from project scope. | Step 1: "Reload the target project or start a fresh agent rooted there. Verify that these shared pstack skills resolve from project scope:" (nine names) and "Do not count a skill loaded from the current session or a user-scoped plugin. The check must show that a fresh agent in the target repository receives pstack through project settings." Failing it ends setup: "If project-scoped plugin installation is unavailable or any shared dependency does not resolve, stop and explain the failure." |
| The source channel, triage identity, repository, tracker adapter, control skill, and feature map are explicit. | Section 3: "The source channel, triage identity, repository, tracker adapter, control skill, and feature map must be explicit. Fail setup if any required value stays ambiguous." The Outcome takes the six named values as the required values (two of them are the items the section 3 list marks "Required"). "Fail setup if any required value stays ambiguous." stays in its Task unchanged; the extent of "required value" is recorded under findings. |
| The named control skill is confirmed to have every capability that section 6 lists, or the repro automation is left disabled. | Step 6: "Confirm that the named skill can:" (seven capabilities) and "If any capability is missing, leave the repro automation disabled. It must fail closed rather than claim a reproduction it did not perform." The second clause of the Outcome is upstream's own alternative ending. |
| The target repository's `.cursor/settings.json`, `.cursor/automations/benny/`, and every referenced secret-free configuration file are committed on the branch used by the automation checkout. | Step 8: "Before testing, confirm that the target repository's `.cursor/settings.json`, `.cursor/automations/benny/`, and every referenced secret-free configuration file are committed on the branch used by the automation checkout. ... If any check fails, stop. Tell the user that the automation cannot be enabled yet." Also step 1: "must be committed before either automation is enabled". |
| Both live prompts point at their exact committed operational files. | Step 8: "Confirm that both live prompts point at their exact committed operational files." Also step 1 ("live automation prompts may read the committed operational files by their stable repository-relative paths"), step 2 ("Never reference the plugin source directory or a plugin cache path from a live automation."), and step 7 First-time creation items 3 and 4. |
| All seven checks of the thread-safety test pass. | Step 8: "Verify:" (checks 1 to 7) and "Enable normal traffic only after all seven checks pass." Also Creation boundary: "Do not enable either automation until the thread-safety test passes after the editor save." |

Carried from the frontmatter description into the body:

- "Configure Benny and prepare its triage and repro automations." Not a rule. It is the basis of the first Purpose sentence, noted here because the body had no such statement.
- "Use when installing Benny or changing its Slack, tracker, repository, routing, control, model, or budget settings." Not absorbed. It is a discovery trigger, and as a body Constraint it would narrow the cases the body itself handles (pack refresh). It stays in the frontmatter only.

Order dependencies stated under Constraints, with the reason for each:

- Activities in the order listed (upstream numbered sections 1 to 8). Within an Activity, Tasks in any order unless one states otherwise (profile 15.2).
- Do section 1 before asking for Benny configuration and before invoking the built-in `/automate` skill. Reason: upstream order word "before".
- Numbered items inside a Task in the order listed. Reason: upstream numbered those lists; listed order is their default.
- In section 1, ask the repository before merging and editing settings; add the settings entry before the project-scope check. Reason: later Tasks use results only the earlier ones produce.
- Once the section 1 check passes, live automation prompts may read the committed operational files. Reason: upstream order word "Once".
- In section 2, open the examples before creating copies; create the feature map before filling it. Reason: result dependency.
- pstack's `unslop` skill runs on the final names, descriptions, and prompt shims before saving them. Reason: upstream "before"; the Task is listed in section 3 but acts on section 7 text.
- In section 6, read the control-adapter reference and feature map before confirming capabilities. Reason: result dependency.
- In section 7, ask the path question and read FOR_AGENTS.md before either path; the user's answer selects the path. Reason: result dependency and selection.
- Under First-time creation, one automation at a time; the repro intent after the triage editor handoff. Reason: upstream "before", "After", "one automation at a time".
- Under Existing automations, validation before the checklist. Reason: upstream "Then".
- In section 8, both confirmations before testing; normal traffic only after all seven checks pass. Reason: upstream "Before testing", "only after".
- Stated as standing Constraints, not in the list: "Reference a repository file only after the built-in `/automate` skill confirms that the file is committed ..." (upstream "only after"), and in Creation boundary "Do not enable either automation until the thread-safety test passes after the editor save." (upstream "until").

State-changing or external effects the work can have, with the condition upstream states:

- Writes the pack into the target repository at `<target-repository>/.cursor/automations/benny/` (create, copy, merge). Conditions: "Preserve destination-only files. Never delete unrelated files during install or refresh."; "Keep user-owned configuration, feature maps, and routing maps outside the destination. Never overwrite them."; "When an existing source-managed file differs, inspect the diff and merge without discarding local edits. If ownership is ambiguous, stop and ask before replacing it."
- Creates or edits the target repository's `.cursor/settings.json` (and creates `.cursor` when absent). Conditions: "Preserve every unrelated top-level setting and every other plugin entry. If `plugins.pstack` already exists, change only its `enabled` value. Preserve comments and valid JSONC syntax when the file uses JSONC. Validate the file after editing it."
- Creates user-owned configuration, feature-map, and routing-map copies outside `.cursor/automations/benny/`, in the repository (`.cursor/benny/`) or outside it (`~/.config/benny/`). Conditions: "Do not edit the copied examples."; no secret value in committed configuration; pack refreshes "must never touch the user-owned copies".
- Commits `.cursor/settings.json`, `.cursor/automations/benny/`, and referenced secret-free configuration. Condition: "Do not commit them unless the user asks."
- Stores `BENNY_SLACK_BOT_TOKEN`. Condition: "Store the value in a secret manager or environment, not in YAML."; "Never put a secret value in plugin files, prompts, or committed configuration."
- Creates the live automations `benny-triage` and `benny-reproduce` through the built-in `automate` skill. Conditions: "Do not create or update an automation until the user explicitly asks."; `automate` shows its draft table, obtains approval, asks readiness, and opens the Automations editor; one automation at a time; "For new automations, the only finish path is the built-in `automate` skill's reviewed Automations editor handoff."; never a direct automation backend service or tool, a browser URL that carries draft fields, or a Cursor protocol deep link.
- Updates existing automations. Condition: done by the user in each Automations editor from the checklist; `automate` must not be used; "Do not create replacements or duplicates."
- Enables an automation and normal traffic. Conditions: referenced files committed before either automation is enabled; "Do not enable either automation until the thread-safety test passes after the editor save."; "Enable normal traffic only after all seven checks pass."; "If any capability is missing, leave the repro automation disabled."
- Runs the thread-safety test, in which the automations post a verdict reply in Slack and may touch the tracker. Conditions: "Use a test channel or a harmless test report."; the two confirmations before testing; "If any check fails, stop."
- Reloads the target project or starts a fresh agent rooted there. No approval stated.

Also: 17 statements moved to the section their function calls for; 15 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `automations/benny/README.md`

Unchanged from upstream.

## `automations/benny/FOR_AGENTS.md`

Unchanged from upstream.

## `automations/benny/templates/configuration.example.yaml`

Unchanged from upstream.

## `automations/benny/templates/reproduce-automation-prompt.md`

Unchanged from upstream.

## `automations/benny/templates/triage-automation-prompt.md`

Unchanged from upstream.
