# Conversion record: create-verification-skill, maintain-verification-skill

[Conversion guide](../README.md)

## `skills/create-verification-skill/SKILL.md`

Title: Create a verification skill. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Give a project a scripted way to drive the real app and prove behavior, which every serious project needs: launch it, exercise a feature the way a user would, and capture evidence. This skill generates that as a project-local skill (`.cursor/skills/verify-<app>/`) tailored to the repo, for any language, framework, or platform.

| Outcome | Basis in the upstream text |
| --- | --- |
| The generated `SKILL.md` has the frontmatter and the sections step 2 lists, each section grounded in what the interview found and meeting what step 2 states for it, with no placeholders left. | Step 2: "Write `.cursor/skills/verify-<app>/SKILL.md` with YAML frontmatter (`name: verify-<app>` and a `description` that names the app, the surface, and when to reach for it — without frontmatter the skill never registers) and these sections, each grounded in what the interview actually found (no placeholders left)", followed by what each section must contain (for example Launch: "Launch must reach a usable state from an empty data dir"; Doctor: "one read-only check"; Drive: "real selectors/commands from this repo, not examples"; Cleanup: "Never kill by process name"; Helpers: "executable and its invocation is shown in the skill body"); step 1: "Answer these from the codebase". |
| The feature map has a README index and one file for each feature it lists, each answering from the user's point of view what the feature is, how to reach it, how to drive it with the harness, and what observable end state proves it works. | Step 3: "Create `.cursor/skills/verify-<app>/features/README.md` plus one file per user-facing feature you can identify (aim for the top 3-5 to start, from routes, commands, menus, or docs)"; "with a README index and one file per feature. Each file answers, from the user's point of view: what the feature is, how to reach it, how to drive it with the harness, and what observable end state proves it works." Scoped to the features the map lists, because upstream seeds the map with the features identified and aims for the top 3-5 to start, not every feature of the app. |
| One run of the generated skill's own instructions has gone end to end with no part of them failing: launch, doctor, the drive of one mapped feature, evidence capture, and cleanup. | Step 4: "Run its own instructions end to end once: launch, doctor, drive ONE mapped feature (one is enough; the map exists so later runs can cover the rest), capture evidence, clean up."; "a cleanup that eats the proof fails this step"; "Fix what fails, and run the generated cleanup after every failed iteration too"; "A generated skill that was never executed is a draft, not a deliverable." The passing condition follows from "Fix what fails" and the failed-iteration rule, which imply iterating until a run passes. |
| The evidence of that run still exists at the named location after cleanup. | Step 4: "After cleanup, confirm the evidence still exists at the named location — a cleanup that eats the proof fails this step."; step 2 Cleanup bullet: "Cleanup removes instances and scratch state, never the evidence: proof artifacts survive the teardown, in a location the skill names." |
| Where the skill was proved in a stand-in for the real target, every setup step the stand-in did that the target will not is listed as unverified. | Step 4: "If you proved it in a stand-in for the real target (a container in place of a fresh VM, a local stack in place of a remote one), list every setup step the stand-in did that the target will not. Those steps stay unverified until a run on the real target covers them." |

Carried from the frontmatter description into the body:

- "any language, framework, or platform" (description: "Generate a project-local verification skill that drives your app the way a user does — any language, framework, or platform."), carried into the second Purpose sentence as the scope of the work. The body had no statement of it. The trigger phrases ("Use for /create-verification-skill, \"make a control skill for this repo\", or when a project has no scripted way to prove UI/CLI/service behavior") stay in the frontmatter only.

Order dependencies stated under Constraints, with the reason for each:

- Step 1 fixes a checkout that doesn't build or start, or reports it precisely, before step 2 generates. Reason: upstream order words in step 1, "fix that first (or report it precisely) before generating".
- Step 2 writes from what the interview of step 1 found. Reason: the later step uses a result only the earlier one produces, "each grounded in what the interview actually found".
- Step 4 runs the instructions that step 2 wrote and drives a feature that step 3 mapped. Reason: the later step uses results only the earlier ones produce, "Run its own instructions end to end once" and "drive ONE mapped feature".
- Step 4 comes before the skill is handed over. Reason: upstream order word in the step heading, "Prove the generated skill before handing it over"; the proof is the gate for the handover.

State-changing or external effects the work can have, with the condition upstream states:

- Writes the generated skill into the project: `.cursor/skills/verify-<app>/SKILL.md`, `.cursor/skills/verify-<app>/features/README.md`, one file per feature, and any helper script. Upstream states no approval. The skill loads only when invoked (`disable-model-invocation: true`), and step 1 limits questions to "only ask the user what you cannot observe".
- May change the checkout so that it builds or starts: "If the checkout doesn't build or start as-is, fix that first (or report it precisely) before generating". Upstream states no approval and no limit on what the fix may touch.
- Launches the app, drives one mapped feature, and tears down what it started (processes, ports, data dirs, scratch state). Conditions upstream states for the generated skill: "Never kill by process name; kill what you started"; "Cleanup removes instances and scratch state, never the evidence"; if two instances cannot run side by side, "say so in the generated skill: refusing to double-drive a shared instance beats corrupting the user's session". For the proof run: "run the generated cleanup after every failed iteration too".
- Driving the real user path can produce side effects ("files written, rows inserted, messages sent"). Conditions upstream states: "mocks only where a production boundary already isolates the external system"; "When the safe path is a dry-run or test mode, verify what it actually skips by observing (files, network, git refs) rather than trusting its name".
- The generated skill may create an irrelevant missing asset that blocks startup, "clearly marked as verification scaffolding, and remove it in cleanup" (permission stated by upstream).

Also: 2 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/maintain-verification-skill/SKILL.md`

Title: Maintain a verification skill. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Keep a project's verification skill and feature map honest, or say exactly what blocked the pass. A feature map rots the moment the app changes. This skill is the upkeep loop for a skill generated by `/create-verification-skill` (or any project-local verification skill with a feature map).

| Outcome | Basis in the upstream text |
| --- | --- |
| Every feature file has a returned summary from the source wave, or the run is `blocked`. | Step 2: "One read-only subagent per feature file, launched concurrently. ... Return shape: feature summary / source entry points / likely drift or none / one recipe."; step 3: "Every feature file has a returned summary."; intro: "cover every feature file from source"; run outcome list: "**blocked** — coverage could not finish or a proven fix could not ship safely." |
| Every feature is exercised live at least once or is `verified-unreachable` with the concrete prerequisite and the route attempted, or the run is `blocked`. | Step 4: "Exercise every feature at least once"; "A feature that can't be reached is `verified-unreachable` only with the concrete prerequisite (auth, entitlement, OS, external state) and the route attempted"; intro: "exercise every feature live"; run outcome list: "**clean** — every feature got source and live coverage" and "**blocked** — coverage could not finish". |
| Where the pass proved doc, harness, or map corrections, one PR ships them and holds nothing unproven, or the run is `blocked`. | Run outcome list: "**changed** — one PR ships proven doc, harness, or map corrections." and "**blocked** — ... a proven fix could not ship safely."; step 6: "For changed: one PR of proven corrections"; step 4: "Any harness fix from triage gets re-driven live before it ships."; description: "at most one PR of proven corrections". |
| Every product gap the pass found is recorded for the user and kept out of the run's PR. | Step 5: "App behavior that's actually broken → product gap; record it for the user, keep it out of this PR."; Edit scope: "a product regression (report it, don't paper over it in docs)". |
| The run states the one run outcome that holds: `clean`, `changed`, or `blocked`. | Run outcome list: "Pick one, and say which:" with the three definitions; step 6: "report the outcome". |
| Where the run is `clean` or `blocked`, its report states the coverage the pass actually reached. | Step 6: "For clean or blocked: no PR, report the outcome and the coverage honestly." Conditioned on `clean` or `blocked` because step 6 states the coverage report only for those endings. |
| A `blocked` run says exactly what blocked it. | Run outcome list: "**blocked** — coverage could not finish or a proven fix could not ship safely. Say exactly what blocked it." |

Headings whose text changed:

- "## Outcomes" became "### Run outcome (under ## Outputs)". Profile section 5, Colliding words. The upstream section lists the three run verdicts the agent picks from and states, which is an Output of the run and not the Framework's Outcomes. Its text and the labels **clean**, **changed**, **blocked** are unchanged, and the word "outcome" stays in step 6 and in the run notes sentence.

Order dependencies stated under Constraints, with the reason for each:

- Step 0 comes first. The other steps work on the target it locates. Reason: every later step uses the located target, and step 0 is the gate ("none → stop and point at `/create-verification-skill` instead of inventing a target").
- Step 3 reconciles what the children of step 2 return. Reason: the later step uses a result only the earlier one produces ("Every feature file has a returned summary. Merge overlapping recipes").
- Step 4 drives the app states that step 3 merged. Reason: the later step uses a result only the earlier one produces (step 3: "Merge overlapping recipes into as few app states as practical"; step 4: "The coordinator owns all driving").
- Step 5 triages the drift and gaps that steps 2 to 4 found. Reason: the later step uses results only the earlier ones produce (step 2 "flags likely doc drift with citations"; step 3 "Spot-check cited drift" and the churn sweep; step 4 live findings). Step 4's re-drive of triage fixes keeps the two interleaved, as step 4 states.
- Step 6 ships or reports the results of the earlier steps. Reason: step 6 ships "one PR of proven corrections" made in earlier steps, or reports "the outcome and the coverage" they reached.
- A harness fix from the triage of step 5 is re-driven live before step 6 ships it. Reason: upstream order word in step 4, "Any harness fix from triage gets re-driven live before it ships."
- Final teardown comes after the last drive of the run, including those re-proofs. Reason: upstream order word in step 4, "Final teardown happens after the last drive of the run — including those re-proofs — so nothing outlives the run".

State-changing or external effects the work can have, with the condition upstream states:

- Edits files of the verification skill (its SKILL.md, features/, harness scripts it owns). Condition upstream states (Edit scope): "Only edit the verification skill's own directory"; "Never edit product code during a run".
- Opens one PR for the `changed` outcome ("one PR ships proven doc, harness, or map corrections"). Conditions upstream states: only proven corrections; "re-read every changed file first"; "Any harness fix from triage gets re-driven live before it ships"; product gaps are kept "out of this PR". For `clean`: "No branch, no PR". For `blocked`: "no PR". Upstream states no user approval before the PR.
- Launches and drives live app instances and tears them down. Conditions upstream states (step 4): never drive an instance not health-checked since it last did something surprising; evidence survives every cleanup; nothing a drive started outlives that drive's usefulness; "for a shared instance, clean the residue, not the instance"; final teardown after the last drive, "evidence stays, per the skill".
- Spawns one read-only subagent per feature file, concurrently. Limit upstream states: "Children never drive the app and never edit files."
- Writes run notes "in a scratch location; don't commit them".
- Asks the user which target to maintain when several candidates exist; stops when none exists.

Also: 6 statements moved to the section their function calls for; 5 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/create-verification-skill/references/feature-map-example/README.md`

Unchanged from upstream.

## `skills/create-verification-skill/references/feature-map-example/create-note.md`

Unchanged from upstream.

## `skills/create-verification-skill/references/feature-map-example/search.md`

Unchanged from upstream.
