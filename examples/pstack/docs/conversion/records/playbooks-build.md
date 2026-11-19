# Conversion record: Playbooks: building and planning

[Conversion guide](../README.md)

## `skills/poteto-mode/playbooks/feature.md`

Title: Feature. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Build a feature under a design and a plan the lead owns, and deliver it for review.

| Outcome | Basis in the upstream text |
| --- | --- |
| The data shape and its organizing structure are chosen before the delegate writes logic. | Step 4: the delegate's scope holds the "named data shape and its organizing structure per **principle-model-the-domain**, a state machine over scattered booleans, a table/registry over branching, a typed model over repeated shape assumptions, chosen before the delegate writes logic". Step 2: "`architect` for the shape." Lead line: "You own the design." |
| The throughput checkpoint keeps an item for each of its four dimensions, and a dimension that does not apply reads `n/a: <reason>`. | Step 3: "Write the throughput checkpoint as four todo items. A dimension that genuinely does not apply (single file, no fan-out) keeps its item with `n/a: <reason>` rather than being dropped". The Reply must show "the throughput checkpoint". Lead line: "Plan, review, verify." |
| The feature passes verification on the matching surface, or an inconclusive or wrong-surface result is flagged and not counted as a pass. | Step 5: "Verify on the matching surface. \"Inconclusive\" or wrong-surface is not a pass. Flag it." The flagged ending is upstream's own alternative, so the Outcome can be met on it. |
| The change is delivered as small, ordered commits, each a verifiable unit. | Step 6: "Rebase into small, ordered commits." and "Use the **sequence-verifiable-units** principle skill, building, verifying, and committing each small unit before the next." The per-unit build, verify, commit discipline stays in Task 6; the Outcome states the observable state of the history. |
| The change is open as a PR per **Opening a PR**. | Step 8: "Run **Opening a PR**." |

Order dependencies stated under Constraints, with the reason for each:

- Step 2 before step 4. Reason: order word in step 4 ("chosen before the delegate writes logic"), and step 4's scope uses the shape only step 2 produces.
- Step 3 before step 4. Reason: step 4's delegation uses the decomposition only the checkpoint produces ("Gates run before fan-out"; "goes to a single owner with the checkpoint inline").
- Step 5 after step 4. Reason: verification uses the code only step 4 produces. Worded as a result dependency ("it verifies what step 4 built") so that it does not forbid step 6's per-unit build, verify, commit bracket.
- Step 7, when it applies, before shipping. Reason: order word in step 7 ("before shipping"); the interrogation is the gate for shipping a contested design.
- Step 8 after step 6. Reason: the PR carries the commits only step 6's rebase produces.
- Kept inside their statements, not turned into order between steps: "Gates run before fan-out." (step 3), "each small unit before the next" (step 6), "That owner fans out internally after the blocking phase." (Constraints paragraph).
- No dependency is listed for step 1 before step 2 or for step 6 after step 5. This file states no order word for them. The listed-order sentence still holds them in upstream's order.

State-changing or external effects the work can have, with the condition upstream states:

- Spawning subagents and, through the **arena** skill, runners and a cross-judge (step 4). No approval stated in this file. poteto-mode's Autonomy section lets reversible work proceed without asking.
- Commits on the work branch (step 4, "Commit liberally.") and a rebase that rewrites its history (step 6). No approval stated. poteto-mode's Autonomy section pauses only for a force-push to shared branches.
- Edits outside the feature's own files when porting shared-primitive improvements "to all consumers" (step 4). Condition stated: "verify each".
- Opening a PR, which publishes a branch and opens a PR ready for review (step 8, through **Opening a PR**). No approval stated. Condition stated: "If the design is contested, `interrogate` before shipping." (step 7).
- Stacking follow-ups as further branches or PRs (step 6). No approval stated.

Also: 3 statements moved to the section their function calls for; 8 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-mode/playbooks/refactoring.md`

Title: Refactoring. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Change the structure of the code while its behavior holds against a pinned contract, keep only a change that lowers reader load, and deliver what is kept for review.

| Outcome | Basis in the upstream text |
| --- | --- |
| A characterization test, snapshot, or equivalence harness pins the current behavior, captured before any structure moved. | Step 1: "write a characterization test, snapshot, or equivalence harness that captures current behavior before any structure moves. If the area has no coverage, write the pin before touching structure. Type check and lint are not a pin." Lead line: "You own the contract." Reply: "the pin you held it against". |
| The behavior is proven unchanged on the real artifact. | Step 6: "Prove behavior is unchanged on the real artifact, not \"it compiles\"". Reply: "the equivalence proof". |
| The pin is green after every small behavior-preserving move and at every behavior-preserving slice. | Step 5: "Move in small behavior-preserving steps, each keeping the pin green." Step 8: "so each behavior-preserving slice stays green before the next". Upstream's "steps" in step 5 are the small moves, so the Outcome says "move" to keep them apart from the playbook's steps; "slice" is step 8's word. |
| The shipped change carries no new behavior. | Lead line: "The structure changes. The behavior does not." Second paragraph: "If the cleanup reveals a missing feature or a real bug, split it out". Reply: "No new behavior." |
| The shipped diff lowers reader load somewhere, and a diff that does not is reverted. | Step 7: "The success measure is reduced reader load (**principle-minimize-reader-load**). If the diff does not lower reader load somewhere, revert it." Reply: "the reader-load delta, what shipped and what got reverted". The revert is upstream's own alternative ending. |
| The shipped history is small ordered commits, a subtraction commit, then the reshape, then any follow-on cleanup. | Step 8: "Rebase into small ordered commits. A subtraction commit, then the reshape, then any follow-on cleanup." |
| The shipped change is open as a PR per **Opening a PR**. | Step 8: "Run **Opening a PR**." |

Order dependencies stated under Constraints, with the reason for each:

- Step 1 before any structure moves. Reason: order words in step 1 ("first", "before any structure moves", "before touching structure"); the pin is a baseline.
- Step 3 before step 5. Reason: order word in step 3 ("before the move"); the move uses the target shape only step 3 names.
- Step 4 before step 5. Reason: order words in step 4 ("Subtract before you add", "before introducing the new shape").
- Step 6 after step 5. Reason: the proof uses the moved code only step 5 produces.
- Step 7 before step 8. Reason: step 7 is the gate for what step 8 ships.
- Kept inside their statements as order on a result: "A subtraction commit, then the reshape, then any follow-on cleanup." (commit order, step 8), "ship the structural change first against the pinned contract" (landing order, Constraints paragraph), "so each behavior-preserving slice stays green before the next" (step 8).
- No dependency is listed for step 2 before step 3. Upstream states no order word for it. The listed-order sentence still holds it.

State-changing or external effects the work can have, with the condition upstream states:

- Deleting code: dead code, one-caller wrappers, redundant validators, orphan references, and the old API (steps 4 and 5). No approval stated. Conditions stated: the pin stays green, and every caller is migrated in the same wave.
- Reverting work: a speculative cleanup (step 4) and a diff that does not lower reader load (step 7). No approval stated.
- Spawning a subagent for the mechanical edits (step 5). No approval stated.
- Commits and a rebase that rewrites the work branch's history (step 8). No approval stated.
- Opening a PR, which publishes a branch and opens a PR ready for review (step 8, through **Opening a PR**). No approval stated. Step 7 is stated as the keep-or-revert gate for what step 8 commits; step 8 follows step 6 only by the listed order, and upstream states no condition from step 6 on the PR.
- Splitting out a missing feature or a real bug as separate work, shipped after the structural change (second paragraph). No approval stated.

Also: 3 statements moved to the section their function calls for; 8 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-mode/playbooks/multi-phase-plan.md`

Title: Multi-phase or multi-PR plan. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Give multi-phase or multi-PR work a plan that an owner can run box by box and the operator can audit from the evidence, without implementing it.

| Outcome | Basis in the upstream text |
| --- | --- |
| The plan opens with what changes, the PR ids in landing order, and the dependency graph, and has one section of checkboxes per PR. Where the change is one or two files with an obvious approach, the plan is skipped instead and the skip is stated. | Step 3: "Open with what changes, the PR ids in landing order, and the dependency graph ... Then one section per PR. ... Each section has checkboxes for what it depends on, the files it edits, the one change it builds, the result you see, and its verification." Lead line: "The plan is a checklist an owner runs box by box". Step 1 gives the alternative ending: "When the change is one or two files with an obvious approach, skip the plan. Say so and stop." |
| Each PR in the plan is one change with its own evidence. | Step 3: "One PR is one change with its own evidence (the **sequence-verifiable-units** principle skill)." |
| Each PR's verification in the plan has unit, live, and perf boxes. | Step 4: "A PR is verified only when its unit, live, and perf boxes are all checked." Lead line: "the operator audits from the evidence". The rule "Tests alone are not sufficient verification." stays in Task 4 and is not restated in the Outcome. |
| The plan marks every PR that changes an interaction as waiting for the operator's review before merge. | Step 4: "A PR that changes an interaction waits for the operator's review before merge." Reply: "the review-gated set". The merge itself belongs to later execution ("Execution starts on the operator's explicit go."), so the Outcome states what this run establishes, the plan's mark. |
| The open questions that a run can settle are settled by prototype before the plan is written. | Step 2: "Settle open questions by prototype before you write, per `playbooks/prototype.md`. Ask the operator only about a product or preference call that no run can settle." |
| No part of the plan is implemented in this run. | Lead paragraph: "You own the plan, not the code.", "The plan is the deliverable. Do not implement." Step 5: "Hand back the plan path and stop. Execution starts on the operator's explicit go." The prohibition holds through the whole run, including the step 1 skip path. |

Order dependencies stated under Constraints, with the reason for each:

- Step 1 before every other step. Reason: step 1 decides whether the plan is written at all ("skip the plan. Say so and stop.").
- Step 2 before step 3. Reason: order word in step 2 ("before you write").
- Step 5 after step 3. Reason: it hands back the path of the file only step 3 writes.
- No dependency is listed between steps 3 and 4. Step 4 states criteria for what step 3 writes and orders no action of its own.
- Kept inside their statements: "the PR ids in landing order" (order on a result, step 3), "the trunk baseline measured first" (order the plan prescribes for its perf box, step 4), "waits for the operator's review before merge" (approval the plan carries, step 4), "Execution starts on the operator's explicit go." (approval for work outside this playbook, step 5).

State-changing or external effects the work can have, with the condition upstream states:

- Writing the plan file (step 3). Where it is written is not stated, so it can lie outside the repository. No approval stated.
- Building throwaway prototypes to settle open questions (step 2, per `playbooks/prototype.md`, which builds in an isolated scratch dir). No approval stated.
- Asking the operator a question (step 2). Condition stated: "only about a product or preference call that no run can settle".
- Implementation and execution of the plan are prohibited in this playbook ("Do not implement."). Condition stated for later execution: "Execution starts on the operator's explicit go."
- Merges that the plan describes. Condition stated: "A PR that changes an interaction waits for the operator's review before merge."

Also: 2 statements moved to the section their function calls for; 6 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-mode/playbooks/authoring-a-skill.md`

Title: Authoring or modifying a skill. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Author or modify a skill in a voice that keeps only prose that changes a decision, and deliver it validated for review.

| Outcome | Basis in the upstream text |
| --- | --- |
| The skill's frontmatter has `name` and `description`. | Step 2: "Validate the skill: frontmatter has `name` and `description`". Reply: "validation notes". |
| Every file the skill references exists. | Step 2: "referenced files exist". |
| Every cross-skill link in the skill resolves. | Step 2: "cross-skill links resolve". |
| In the parts of the skill this run authors or changes, only prose that changes a decision remains. | Paragraph after step 4: "When in doubt, delete. Keep only prose that changes a decision." Lead line: "You own the skill's voice." The subject is limited to what the run authors or changes, because upstream does not say whether the rule reaches untouched prose of a modified skill. |
| The change is open as a PR per **Opening a PR**. | Step 4: "Run **Opening a PR**." |

Order dependencies stated under Constraints, with the reason for each:

- Steps 2, 3, and 4 after step 1. Reason: each acts on the skill only step 1 authors or modifies.
- No dependency is listed among steps 2, 3, and 4. Upstream does not say that validation or test cases gate the PR. The listed-order sentence still holds them in upstream's order.

State-changing or external effects the work can have, with the condition upstream states:

- Creating or editing a skill's files through the **create-skill** skill (step 1). The target can be a skill folder outside the repository. No approval stated.
- Opening a PR, which publishes a branch and opens a PR ready for review (step 4, through **Opening a PR**). No approval stated.
- Proposing a new skill for an uncaptured workflow (Controls paragraph). A proposal only.

Also: 3 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).
