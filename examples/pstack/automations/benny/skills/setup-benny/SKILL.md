---
name: setup-benny
description: Configure Benny and prepare its triage and repro automations. Use when installing Benny or changing its Slack, tracker, repository, routing, control, model, or budget settings.
disable-model-invocation: true
---

# Set up Benny

## Purpose

Configure Benny for a target repository and prepare its triage and repro automations to run there. Benny needs external configuration and two live Cursor automations.

## Outcomes

- `<target-repository>/.cursor/automations/benny/` contains `FOR_AGENTS.md`, this setup file, both operational files, their references, and the templates.
- For a fresh agent rooted in the target repository, every shared pstack skill that step 1 lists resolves from project scope.
- The source channel, triage identity, repository, tracker adapter, control skill, and feature map are explicit, and no required value is ambiguous.
- The named control skill is confirmed to have every capability that step 6 lists, or the repro automation is left disabled.
- The target repository's `.cursor/settings.json`, `.cursor/automations/benny/`, and every referenced secret-free configuration file are committed on the branch used by the automation checkout.
- Both live prompts point at their exact committed operational files.
- All seven checks of the thread-safety test pass.

## Activities & Tasks

The following Tasks are required whenever this skill runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

### 1. Copy the pack and enable shared pstack skills

1. Ask which repository will run the automations. The source pack is the directory containing `FOR_AGENTS.md`. The destination is `<target-repository>/.cursor/automations/benny/`.
2. Merge the entire source pack into the destination:

    1. Create the destination when it is absent.
    2. Copy every source file to the same relative path.
    3. Preserve destination-only files. Never delete unrelated files during install or refresh.
    4. Keep user-owned configuration, feature maps, and routing maps outside the destination. Never overwrite them.
    5. When an existing source-managed file differs, inspect the diff and merge without discarding local edits. If ownership is ambiguous, stop and ask before replacing it.
    6. Verify that the destination contains `FOR_AGENTS.md`, this setup file, both operational files, their references, and the templates.

    If this file is already being read from the target destination, treat the copy as complete and run the same verification before continuing.
3. Add pstack to the target repository's `.cursor/settings.json`. If the file or `.cursor` directory does not exist, create it. Merge this entry into the existing JSON or JSONC:

```json
{
	"plugins": {
		"pstack": { "enabled": true }
	}
}
```

4. Preserve every unrelated top-level setting and every other plugin entry. If `plugins.pstack` already exists, change only its `enabled` value. Preserve comments and valid JSONC syntax when the file uses JSONC. Validate the file after editing it.
5. Reload the target project or start a fresh agent rooted there. Verify that these shared pstack skills resolve from project scope:

    - `why`
    - `tdd`
    - `unslop`
    - `principle-separate-before-serializing-shared-state`
    - `principle-minimize-reader-load`
    - `principle-guard-the-context-window`
    - `principle-sequence-verifiable-units`
    - `principle-fix-root-causes`
    - `principle-prove-it-works`

    Do not count a skill loaded from the current session or a user-scoped plugin. The check must show that a fresh agent in the target repository receives pstack through project settings.

    If project-scoped plugin installation is unavailable or any shared dependency does not resolve, stop and explain the failure.
6. Tell the user that `.cursor/settings.json`, `.cursor/automations/benny/`, and any referenced secret-free configuration must be committed before either automation is enabled. Do not commit them unless the user asks.

### 2. Adapt the configuration

1. Open these copied examples:

    - `../../templates/configuration.example.yaml`
    - `../reproduce-and-fix-issues/references/feature-map.example.md`
2. Create user-owned copies outside `.cursor/automations/benny/`. These are configuration files, not pack files. Example locations:

    - Project config, such as `.cursor/benny/configuration.yaml`
    - Project feature map, such as `.cursor/benny/feature-map.md`
    - Project routing map, such as `.cursor/benny/routing.md`
    - User config, such as `~/.config/benny/configuration.yaml`
    - User feature map, such as `~/.config/benny/feature-map.md`
3. Fill one feature-map section for every user-facing feature the automation may reproduce. Keep it at the user point of view. Do not freeze implementation details or current code paths in the map.
4. Prefer committed, secret-free files in the target repository when a fresh automation checkout must read them. Otherwise paraphrase the required values into the live prompt. Reference a repository file only after the built-in `/automate` skill confirms that the file is committed in the repository where the automation runs.
5. Use stable repository-relative paths for committed pack and configuration files. Never reference the plugin source directory or a plugin cache path from a live automation.

### 3. Fill the required choices

1. Ask for or confirm:

    - Source Slack channel ID
    - Optional operations or status channel ID
    - Repository URL and default branch
    - Triage identity or Slack user ID
    - Issue tracker type, team, project, labels, and intake status
    - Tracker adapter skill or MCP actions
    - Optional routing map path
    - Required control skill name
    - Required user-facing feature-map path
    - Status emoji strings
    - Pull request URL format
    - Polling and effort budgets
    - Model slug for triage, repro, code work, and media review

    Use only model slugs shown as available in the user's Cursor model picker or supported model list. Do not guess a slug and do not carry over a private default.

    The source channel, triage identity, repository, tracker adapter, control skill, and feature map must be explicit. Fail setup if any required value stays ambiguous.
2. Use pstack's `unslop` skill on the final automation names, descriptions, and prompt shims before saving them.

### 4. Check integration capabilities

1. Check the integration capabilities each automation needs.

    The triage automation needs:

    - Read access to the configured source Slack channel and its threads
    - Thread-reply access in that channel
    - Attachment metadata and file download access when reports include media
    - Search, read, create, and update access through the configured issue-tracker adapter

    The repro automation needs:

    - Read access to the source thread
    - Thread-reply access in the source channel
    - Optional post and edit access in the configured operations channel
    - Repository read and history access
    - A pull request action that can open a draft pull request
    - The configured control-adapter skill
2. Prefer configured Cursor Slack actions for reads and posts. The optional `BENNY_SLACK_BOT_TOKEN` may fill a narrow gap such as editing one operations status message or downloading an attachment. Store the value in a secret manager or environment, not in YAML.

    Do not use undocumented integration endpoints.

### 5. Prepare the routing map

1. If the user wants reroutes or owner pings:

    1. Copy `../triage-issue-reports/references/routing.example.md` outside `.cursor/automations/benny/`.
    2. Replace every placeholder with public or organization-local values.
    3. Keep owner pings off by default.
    4. Allow a ping only for a configured feature owner or a confirmed likely regression author.

    If no routing map is configured, triage may classify a report but must not guess a destination or owner.

### 6. Verify the control adapter

1. Read `../reproduce-and-fix-issues/references/control-adapter.md` and the user's completed feature map.
2. Confirm that the named skill can:

    - Bring up the target app
    - Navigate every mapped feature through the real UI
    - Exercise mapped states through declared adapter actions
    - Inspect state without forcing the result
    - Capture screenshots
    - Start and stop a recording
    - Clean up its processes and temporary data

    If any capability is missing, leave the repro automation disabled. It must fail closed rather than claim a reproduction it did not perform.

### 7. Prepare the live automations

1. Ask whether this is first-time creation or configuration of existing automations.
2. Read `../../FOR_AGENTS.md` from the copied pack as the primary user-intent source for either path. Use it to understand the two triggers, tools, instructions, outcomes, and shared rules.

#### First-time creation

1. Create one automation at a time.

    For each automation:

    1. Read the matching copied prompt template as secondary internal source material.
    2. Turn `FOR_AGENTS.md`, the finished Benny configuration, and the template intent into a complete natural-language request.
    3. Tell the live prompt to read and follow its exact committed operational file under `.cursor/automations/benny/`.
    4. Use the stable repository-relative path, not a plugin source or cache path. Do not copy the operational file contents into the live prompt.
    5. Read and follow the built-in `automate` skill.
    6. Let `automate` discover Slack channels, the repository, and connected integrations.
    7. Let `automate` confirm that the copied pack and any referenced configuration files are committed in the same repository where the automation will run.
    8. Let `automate` show its draft table, obtain approval, ask readiness, and open the Automations editor.
    9. Finish the editor handoff for this automation before starting the next one.
2. Give `automate` this complete triage intent, filled from configuration:

    - Name `benny-triage`.
    - Read and follow `.cursor/automations/benny/skills/triage-issue-reports/SKILL.md` for every run.
    - Trigger on each new top-level report in the configured source Slack channel.
    - Read the triggering thread and reply only inside it.
    - Use the configured issue-tracker integration.
    - Classify, inspect evidence, trace cause, dedupe, and create only clear new bugs.
    - End one thread-only verdict with the configured `[benny:bug]`, `[benny:performance]`, or `[benny:other]` marker and optional tracker URL.
    - Never post a source-channel root message.
3. After the triage editor handoff is complete, give `automate` this complete repro and fix intent:

    - Name `benny-reproduce`.
    - Read and follow `.cursor/automations/benny/skills/reproduce-and-fix-issues/SKILL.md` for every run.
    - Trigger on the same new top-level reports in the configured source Slack channel.
    - Use the configured repository and default branch.
    - Read the source thread and reply only inside it.
    - Include pull request creation and the configured tracker, control-adapter, and feature-map requirements. Paraphrase mapped user paths and states unless `automate` confirms an eligible committed file in the same repository.
    - Wait for a trusted triage marker before acting.
    - Reproduce the exact symptom twice through the mapped real UI and capture evidence.
    - Verify an existing fix without authoring over it.
    - Attempt an optional bounded fix only after confirmed repro, then open a draft pull request when proof and checks pass.
    - Never post a source-channel root message.

#### Existing automations

1. Finish configuration, routing, control-adapter, and feature-map validation. Then give the user this concise editor checklist.

    For the existing triage automation, update:

    - Name and description
    - Direct instruction to read `.cursor/automations/benny/skills/triage-issue-reports/SKILL.md`
    - New top-level Slack report trigger and source channel
    - Slack thread read and reply capabilities
    - Issue-tracker integration
    - Paraphrased triage instructions, thread-only rule, and Benny verdict markers

    For the existing repro automation, update:

    - Name and description
    - Direct instruction to read `.cursor/automations/benny/skills/reproduce-and-fix-issues/SKILL.md`
    - Matching Slack trigger and source channel
    - Repository and default branch
    - Slack thread read and reply capabilities
    - Pull request action
    - Tracker, control-adapter, and feature-map requirements
    - Paraphrased marker wait, evidence, verification, and bounded-fix instructions
2. Ask the user to update each existing automation directly in its Automations editor. Do not create replacements or duplicates.

### 8. Test thread safety

1. Use a test channel or a harmless test report.
2. Before testing, confirm that the target repository's `.cursor/settings.json`, `.cursor/automations/benny/`, and every referenced secret-free configuration file are committed on the branch used by the automation checkout. Confirm that both live prompts point at their exact committed operational files. If any check fails, stop. Tell the user that the automation cannot be enabled yet.
3. Verify:

    1. Triage stores the root `thread_ts` and posts exactly one verdict as a reply.
    2. The verdict contains one configured marker.
    3. Repro accepts the marker only from the configured triage identity.
    4. Repro keeps the same immutable source coordinates.
    5. No source-channel root message appears.
    6. A delegated worker cannot use any Slack write action.
    7. Missing coordinates, a deleted parent, or a failed preflight produces no post and no tracker issue.
4. Enable normal traffic only after all seven checks pass.

## Constraints

Setup applies when installing Benny or changing its Slack, tracker, repository, routing, control, model, or budget settings.

Do not create or update an automation until the user explicitly asks. Never put a secret value in plugin files, prompts, or committed configuration.

Unless a Task states otherwise, work the Activities and their Tasks in the order listed. These dependencies are required.

- Do step 1 before asking for Benny configuration and before invoking the built-in `/automate` skill.
- Once the step 1 check passes, live automation prompts may read the committed operational files by their stable repository-relative paths. They must not embed a plugin cache path or copy the file contents.
- Step 6 needs the completed feature map, and step 7 needs the finished Benny configuration.
- The `unslop` pass of step 3 runs on the final automation names, descriptions, and prompt shims before they are saved.
- In step 7, work First-time creation or Existing automations as the user's answer directs.
- Under First-time creation, finish the editor handoff for one automation before starting the next one. Give `automate` the repro and fix intent after the triage editor handoff is complete.
- Under Existing automations, finish configuration, routing, control-adapter, and feature-map validation before giving the user the editor checklist.
- In step 8, make both confirmations before testing. Enable normal traffic only after all seven checks pass.

The Benny files are read directly from `.cursor/automations/benny/`. Do not add that directory to a plugin manifest or expect its `SKILL.md` files to appear in the slash-skill list.

Do not edit the copied examples. Pack refreshes may update source-managed files after conflict review, but they must never touch the user-owned copies.

Do not duplicate `automate`'s Slack, repository, integration, completeness, authentication, draft-review, approval, readiness, or editor-handoff work.

The built-in `automate` skill is creation-only. Do not use it to search for, inspect, or update existing automations.

### Creation boundary

Never call a direct automation backend service or backend automation tool. Never use a browser URL that carries draft fields. Never build or open a Cursor protocol deep link. For new automations, the only finish path is the built-in `automate` skill's reviewed Automations editor handoff.

Do not enable either automation until the thread-safety test passes after the editor save.

## Enablers

Benny ships as a dormant automation pack inside pstack. The plugin manifest exposes only pstack's normal skill root; this file and the two operational files are not slash skills.

The human enters setup by pointing Cursor at the pack's `FOR_AGENTS.md`. The bootstrap flow copies the whole pack into the target repository, then reads this file directly at `.cursor/automations/benny/skills/setup-benny/SKILL.md`.
