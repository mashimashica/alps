# Conversion record: setup-pstack

[Conversion guide](../README.md)

## `skills/setup-pstack/SKILL.md`

Title: Setup pstack. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Configure which models pstack uses per role and at what reasoning budget, so that every role has a valid choice the user confirmed and the user is told which values of an existing rule were replaced or dropped and that the new rule applies to new sessions. It also lets the user have a project-local verification skill generated for a project with no way to drive the real app for proof, and a formal verification skill for a project without one.

| Outcome | Basis in the upstream text |
| --- | --- |
| `~/.cursor/rules/pstack-models.mdc` has the shape of step 5. | Step 5: "Write `~/.cursor/rules/pstack-models.mdc` with `alwaysApply: true`, the `# defaults: 3` line, a `# budget` line with the chosen label and the effort that label names, and one line per role, using the same labels poteto-mode uses. Overwrite the whole file so re-runs stay idempotent. Shape:" and the code block. Step 2: "A line whose role is not in step 5 ... is from a retired role. Drop it." |
| The rule's `# budget` line holds the budget label the user chose and the effort that label names. | Step 3(a): "Ask for a budget." Step 5: "a `# budget` line with the chosen label and the effort that label names", example `# budget: large (xhigh)`. Split from the shape Outcome in fix round 1 (framework W4). |
| Each role line holds the value the user confirmed for that role, which is the value step 3(b) builds from the chosen budget and the current choices step 2 loads unless the user chose another. | Step 2: "treat its `# budget` line and its role values as the current choices. Otherwise start from those defaults.", "Before step 3, replace these values", "Every other value is the user's choice and stays". Step 3(b): "Build the working table from the skill defaults, and on a re-run keep any role you changed by family, list, or alias", "Set the effort token of every real slug in the role, panel entries included, to the role's target." Step 3(c): "Show every role with its model ... Ask whether to accept as-is or change specific roles". Step 4: "stop and ask again". Added in fix round 1 (fidelity F2, framework W1). It refers to what step 3(b) builds and does not restate step 3(b)'s "you changed" test, so it adds no reading of that sentence. |
| Every real slug in the rule is in the detected set and at `xhigh` or below. | Step 4: "Every real slug written must be in the detected set and at `xhigh` or below. `inherit-parent` and `auto` always pass. If a chosen real slug is not available, stop and ask again." Step 1: "Never write a real slug you have not confirmed is available." |
| Where step 2 replaces a value or drops a line of an existing rule, the user is told which. | Step 2: "Tell the user which entries you replaced." and "Tell the user which values you replaced." Step 3(c): "Also list each line step 2 dropped." |
| The user is told that the rule was written and that it applies to new sessions. | Step 6: "Tell the user the rule was written and that it applies to new sessions." |
| An offer of a project-local verification skill is made at most once and only where the project has no way to drive the real app for proof, and `/create-verification-skill` is invoked exactly when the user accepts that offer. | Step 7 "(optional)": "Check whether the project has a way to drive the real app for proof (a `verify-*` skill, or an existing harness). If not, offer once: ... On yes, invoke `/create-verification-skill` ... On no, move on without pushing." Reworded in fix round 1 (fidelity F1) so that it holds under both readings of "(optional)": it does not require the offer to be made, and the step text keeps the instruction to offer. The offer condition and the invocation are kept in one item because the invocation is defined by the answer to that offer. |
| An offer of a formal verification skill is made at most once and only where the project has no formal verification skill, and `/create-formal-verification-skill` is invoked exactly when the user accepts that offer. | Step 8 "(optional)": "Check whether the project already has a formal verification skill (a project skill that runs a model checker, a proof, or another verifier against the code). If not, offer once: ... On yes, invoke `/create-formal-verification-skill` ... On no, move on without pushing." Same treatment as step 7. |

Carried from the frontmatter description into the body:

- "writes an always-applied rule that overrides the skill defaults" is carried under ## Outputs as "The rule overrides the skill defaults." The upstream body has these words only inside the rule template, as the rule file's own `description:` value.
- "Configure which models pstack uses per role and at what reasoning budget." supplies the wording of the first Purpose clause. The upstream body opens with "an always-applied rule that sets pstack's model per role" and never states the budget as part of the objective. The trigger sentence ("Use for /setup-pstack, ...") stays in the frontmatter only.

Headings whose text changed:

- "## Steps" became "## Tasks". Only element names are allowed as H2 headings. No file cites the heading "Steps" by name. The adapter's "Follow its steps" and every "step N" citation resolve through the governing sentence ("pstack text refers to them as steps", profile 15.1) and the unchanged headings "### 1. Detect available models" to "### 8. Offer a formal verification skill (optional)".

Order dependencies stated under Constraints, with the reason for each:

- Step 1 before steps 3 and 4. Reason: later steps use a result only step 1 produces. 3(b) "If the result is not a detected slug, use the same family's detected slug ..."; 3(c) "marking any real slug not in the detected set" and "offering the detected models"; step 4 "must be in the detected set".
- Step 2 before step 3. Reason: upstream order word, "Before step 3, replace these values" (kept verbatim in step 2), and use of step 2's result. 3(a) "name the current budget when the rule records one"; 3(b) "on a re-run keep any role you changed"; 3(c) "Also list each line step 2 dropped."
- Step 2 reads the existing rule before step 5 overwrites it. Reason: the earlier step captures state the later one changes. Step 2 "If `~/.cursor/rules/pstack-models.mdc` already exists, read it"; step 5 "Overwrite the whole file".
- Within step 3, (a) before (b) before (c). Reason: upstream letters the parts, (b) "Apply it" applies the budget (a) asks for, and (c) "Show every role with its model" shows the table (b) builds.
- Steps 3 and 4 before step 5. Reason: step 5 writes "the chosen label" and the role values step 3 settles, and step 4 is the gate for the write ("Every real slug written must be ...", "stop and ask again").
- Step 5 before step 6. Reason: step 6 reports the result of step 5 ("Tell the user the rule was written").
- Steps 7 and 8 have no stated dependency beyond the listed order. Step 4's "stop and ask again" is the one place a step sends the work back (to the question of 3(c)), which "Unless a Task states otherwise" allows.

State-changing or external effects the work can have, with the condition upstream states:

- Overwrites the whole of `~/.cursor/rules/pstack-models.mdc` in the user's home directory, outside the repository. The rule is always applied, so it changes the model every pstack role uses in new sessions. Anything in an existing file that is not carried into the new shape is lost. Condition upstream states: Upstream states no separate approval for the write. It follows the user's answer in step 3(c) ("Ask whether to accept as-is or change specific roles") and the gate of step 4 ("If a chosen real slug is not available, stop and ask again"). "Never write a real slug you have not confirmed is available." "Overwrite the whole file so re-runs stay idempotent."
- Drops retired role lines and replaces old default values of an existing rule (step 2). The loss becomes durable when step 5 overwrites the file. Condition upstream states: "Every other value is the user's choice and stays". The user is told: "Tell the user which entries you replaced.", "Tell the user which values you replaced.", and 3(c) "Also list each line step 2 dropped."
- Invokes `/create-verification-skill`, which generates a project-local verification skill in the user's project. Condition upstream states: Only where the project has no way to drive the real app for proof, after one offer, "On yes". "On no, move on without pushing."
- Invokes `/create-formal-verification-skill`, which generates a formal verification skill in the user's project. Condition upstream states: Only where the project has no formal verification skill, after one offer, "On yes". "On no, move on without pushing."

Also: 1 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).
