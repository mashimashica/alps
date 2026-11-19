# Conversion record: create-formal-verification-skill, maintain-formal-verification-skill

[Conversion guide](../README.md)

## `skills/create-formal-verification-skill/SKILL.md`

Title: Create a formal verification skill. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Verify one property of the part of the repo where formal verification matters most, and leave a project-local skill that lets the next agent check a change against that property. A test checks the cases that someone thought to write. Formal verification checks every case in a stated scope: every order of steps in a model, every input up to a bound, or every input.

| Outcome | Basis in the upstream text |
| --- | --- |
| The target is a promise the code makes, where a break harms users and tests rarely reach the case that breaks it, and it is the strongest such target, not the one that is easiest to verify. | Section 'Choose the target from the code': "A good target is a promise the code makes, where a break harms users and tests rarely reach the case that breaks it. Choose the strongest such target in the repo, not the one that is easiest to verify." "in the repo" is left out so that the Outcome does not decide whether a named area bounds the choice. |
| Every part of the model or proof points to code that a reviewer can open, and what the verification treats as one indivisible step is one indivisible step in the code. | 'What makes it good', True to the code: "Every part of the model or proof points to code that a reviewer can open. What the verification treats as one indivisible step is one indivisible step in the code." Without it the property is verified of a model and not of the part of the repo that the Purpose names. On the generated-inputs fallback there is no model or proof, and the condition holds with nothing to assess. |
| The check of the chosen property passes within its stated bounds and assumptions, or fails only on findings that are reported with the counterexample in the code's terms. | Intro: "verifies one property of it". 'What makes it good', Findings stay findings: "When the current code breaks the property, report it with the counterexample in the code's terms." Honest about scope: "Say what is verified, under which bounds and assumptions, and what is left out. A pass covers the model or the bound, not the whole system." 'Prove it before you hand off': "confirm that the check is back where it started: passing, or failing only on the findings you will report". |
| Each property has been seen to fail on a broken variant of the code it guards. | 'What makes it good', Able to fail: "A check that you have never seen fail proves nothing. Show each property failing on a broken variant of the code it guards, such as a removed check or a reordered step." With one property, the scratch-change Outcome already shows that property failing. This Outcome differs from it when a run verifies more than one property (upstream's "each property"), and it keeps Able to fail as upstream's own requirement apart from the hand-off proof. |
| The generated skill registers, through frontmatter that names the area and says when to use it. | 'Generate the verify skill': "Write a project-local skill with frontmatter that names the area and says when to use it. Without frontmatter, the skill never registers." |
| From the generated skill alone, the next agent can tell whether a change touches the verified code, run the check, tell a real bug from a modeling error, and update the verification when a change is intended. | 'Generate the verify skill': "From the skill alone, the next agent must be able to tell whether a change touches the verified code, run the check, tell a real bug from a modeling error, and update the verification when a change is intended." |
| The generated skill records which files and functions each check covers and the sync commit at which the verification was last confirmed to describe them. | 'Generate the verify skill': "Put the coverage record and the sync commit in the skill". 'What makes it good', Kept in step with the code: "Record which files and functions each check covers, and the commit at which you last confirmed that the verification describes them." maintain-formal-verification-skill step 1 reads this record. |
| The generated skill, followed as the next agent would on a scratch change that breaks the property in the real code, runs every step and catches the break. | 'Prove it before you hand off': "Follow the generated skill once, as the next agent would, on a scratch change that breaks the property in the real code. It must catch the break." and "If the skill misses the break or a step does not run, fix the skill or the verification, not the scratch change." |
| The user can trust the result and act on it without learning the verification language. | Intro: "The user must be able to trust the result and act on it without learning the verification language." No Task establishes it alone. It is established through the Hand off Output and the Controls, and it is assessed with the Hand off items and the criteria "Readable without the tool" and "Honest about scope". |

Order dependencies stated under Constraints, with the reason for each:

- dependency: The target is chosen before the tool is picked.; reason: Result use. Heading "Let the question choose the tool" and "Pick the tool that answers the question at the lowest cost": the question is a question about the chosen target, so the tool cannot be picked before the target is known.
- dependency: The tool is picked before the verification of the property is written with it.; reason: Result use. The verification is written and run with the tool that was picked.
- dependency: The verification of the property is written and run before the verify skill is generated.; reason: Result use. "Put the coverage record and the sync commit in the skill", where the sync commit is "the commit at which you last confirmed that the verification describes them", and "Use this repo's real commands": the skill records a verification that already exists. Worded as work and not as a result, so that it does not read as a gate on the ending where the check fails on reported findings and the skill is still generated.
- dependency: The verify skill is generated before it is followed on the scratch change.; reason: Result use. "Follow the generated skill once, as the next agent would, on a scratch change" needs the generated skill.
- dependency: The verify skill is followed on the scratch change before the hand off.; reason: Order word in the upstream heading: "Prove it before you hand off".

State-changing or external effects the work can have, with the condition upstream states:

- Writes verification files (a model, proof, or harness) and a project-local skill into the project. Condition upstream states: None stated. It is the work the operator starts by typing the command. Upstream names no path for the generated skill and does not say whether to commit.
- Temporary edits to product code: the "broken variant of the code it guards" (Able to fail) and the "scratch change that breaks the property in the real code" (Prove it before you hand off). Condition upstream states: "Then drop the scratch change and confirm that the check is back where it started: passing, or failing only on the findings you will report." No such sentence is given for the broken variant.
- Any other change to product code. Condition upstream states: "do not change product code unless the user asks."
- Installing or pinning a verification tool ("Prefer a tool that the repo's developers can install and run", "a reproducible tool version"). Condition upstream states: None stated.

Also: 7 statements moved to the section their function calls for; 5 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/maintain-formal-verification-skill/SKILL.md`

Title: Maintain a formal verification skill. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Bring a project's formal verification back in line with the code after the code changes, so that each check describes the code as it is now and each failure is known as drift in the verification or a bug in the code. This skill is the upkeep loop for a verify skill that `/create-formal-verification-skill` generated, or for any project-local skill that runs a model checker, prover, or code-level verifier against named code. The project-local skill handles a change that an agent makes while it uses that skill. This skill handles the changes that skipped it: merges, edits made without the skill, and drift that builds up across many commits.

| Outcome | Basis in the upstream text |
| --- | --- |
| Each check's verification describes the current code, or the check is reported as blocked with exactly why. | Upstream section 'Outcomes': in sync ("no change since the last sync alters what the check describes"), updated ("the verification now describes the new code"), bug ("the verification describes the current code"), and "blocked: the check could not be brought back in line or could not run. Say exactly why." Step 4: "Change the model or harness so that each changed part again points to code that a reviewer can open". |
| Each changed property follows a promise that changed on purpose, and the evidence for that is cited. | Step 3, third kind of change: "The property must change, and you must cite that evidence." Step 4: "Change a property only for a promise that changed on purpose. Write down the old wording, the new wording, and the evidence." Edit scope: "do not weaken the property or the model to make it pass". |
| Each updated check that passes has caught a break of the new code that its property guards against. | Step 5, Pass: "the check can now pass on a description that has lost the ability to fail. Break the new code the way the property guards against ... and confirm that the check catches it." Report: "the break that you used to show the updated check can still fail". |
| Each failure is named for what it is: drift in the verification or a bug in the code. | Purpose: "each failure is known as drift in the verification or a bug in the code". Step 2: "A failure here can be drift or a bug. Do not decide which until step 5." Step 5, Fail: "If a step cannot happen in the code, the verification is wrong. ... If every step can happen, it is a bug." Report: "Say outright which failures were drift in the verification and which were bugs in the code." The replay of the counterexample stays in step 5 as its method. It is not in the Outcome, because upstream replays only a failure on the rerun, and a step 2 failure that the update removes is judged under the Pass branch without a replay. |
| Where a verify skill exists, it records the code that each check covers, the commands, the bounds, the assumptions, and the sync commit as they stand at the commit that was checked, with the sync commit of a blocked check left where it was. | Step 6: "Update the code that each check covers, the commands, the bounds, the assumptions, and the sync commit. Set the sync commit to the commit that you checked. Do not move the sync commit for a blocked check". The condition "Where a verify skill exists" follows step 1's stop path: "If no verify skill exists, stop and point at `/create-formal-verification-skill`." |
| Where a verify skill exists, its steps run when it is followed once as the next agent would, apart from those of a check reported as blocked. | Step 6: "Then follow the verify skill once as the next agent would, so that you know its steps still run." The condition "Where a verify skill exists" follows step 1's stop path. The exception for a blocked check follows the outcome list: "blocked: the check could not be brought back in line or could not run". |

Headings whose text changed:

- "## Outcomes" became "### Outcome of each check (under ## Outputs)". Upstream's section lists the outcome that each check is given (in sync, updated, bug, blocked). It is not the Framework's Outcomes, and "## Outcomes" now holds the derived success conditions. The profile's example is "Run outcome". Here the outcome is given per check, not per run.

Order dependencies stated under Constraints, with the reason for each:

- dependency: Step 1 comes first. The later steps use what it collects for each check.; reason: Result use. Steps 2 to 6 work on what step 1 collects: "the property, the code it covers, the bounds and assumptions, the command that runs it, and the commit where it was last confirmed to describe the code".
- dependency: Step 2 runs each check before anything is changed, so it comes before the updates in steps 4 and 6.; reason: Order word and baseline. Step 2: "Run each check once before you change anything, and record the result."
- dependency: Step 3 comes before step 4, which updates the verification for what step 3 decides each change is.; reason: Result use. Step 4 changes the model or harness for a change that step 3 found, and "Change a property only for a promise that changed on purpose" uses the kind step 3 decides.
- dependency: In step 4 the update is written before the rerun in step 5.; reason: Order word. Step 4: "Write the update from the code before you rerun, and do not shape it by what makes the check pass."
- dependency: Whether a failure in step 2 is drift or a bug is not decided until step 5.; reason: Order word. Step 2: "A failure here can be drift or a bug. Do not decide which until step 5."
- dependency: Step 5 comes before step 6, which uses its results.; reason: Result use. Step 6: "Set the sync commit to the commit that you checked. Do not move the sync commit for a blocked check" needs the results of step 5.

State-changing or external effects the work can have, with the condition upstream states:

- Edits to the verification: models, harnesses, property files, and the verify skill itself (steps 4 and 6), including the recorded sync commit. Condition upstream states: "Edit only the verification". "Change a property only for a promise that changed on purpose." "Set the sync commit to the commit that you checked. Do not move the sync commit for a blocked check".
- Edits to product code. Condition upstream states: "Never edit product code during a run, unless the user asks you to."
- Temporary break of the new code in step 5 to show that a passing check can still fail. Condition upstream states: "Then drop the break."
- A cheap test or reproduction against the real code that shows a bug. Condition upstream states: "add it to the report as evidence. Do not commit it to the product code."
- "Put the verification updates in a change of their own, separate from any product fix." Condition upstream states: None stated. Upstream does not say whether the change is a commit, a branch, or a PR, and names no push or merge.

Also: 7 statements moved to the section their function calls for; 5 additions other than the Purpose and Outcomes (fixed sentences, pointers).
