# Conversion record: bro, in-your-own-words, sharpen, architect, tdd

[Conversion guide](../README.md)

## `skills/bro/SKILL.md`

Title: Bro. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Give the user your last message again in plain human language, with no jargon.

| Outcome | Basis in the upstream text |
| --- | --- |
| The reply restates your last message. | Body sentence 1: "Restate your last message." |
| The restatement uses no jargon. | Body sentence 2: "Stop using jargon". Description: "in plain human language, with no jargon". |
| The restatement is coherent. | Body sentence 2: "speak coherently". |
| The restatement states the last message more simply and concisely, like one human talking to another. | Body sentence 3: "State it more simply and concisely, like one human talking to another." |

Also: 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/in-your-own-words/SKILL.md`

Title: In your own words. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Show, in your own words, what you think the user's goals are and what problem they're trying to solve.

| Outcome | Basis in the upstream text |
| --- | --- |
| The restatement says what you think the user's goals are. | Body: "Restate ... what you think the user's goals are" |
| The restatement says what problem you think the user is trying to solve. | Body: "... and what problem they're trying to solve." |
| The restatement is in your own words. | Body: "Restate in your own words ..." |

Also: 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/sharpen/SKILL.md`

Title: Sharpen. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Make the user's task deeper, not bigger, and give the user their prompt rewritten to ask for that deeper version.

| Outcome | Basis in the upstream text |
| --- | --- |
| The reply states each of the four things in steps 1 to 4. | "Before rewriting it, do four things:" and steps 1 to 4 ("Say what ...", "Name the rawest material ...", "Name the specific methods and tools ...", "Say what ... would show the result is right.") |
| The rewritten prompt asks for exactly the deeper version of the task that steps 1 to 4 describe, not a bigger one. | "I want a deeper version of this task, not a bigger one." and "Then rewrite my prompt to ask for exactly that." |
| The rewritten prompt asks the agent to prototype any choice an experiment can settle and to recommend an option based on what it observed. | "Have the rewritten prompt ask the agent to prototype any choice an experiment can settle and recommend an option based on what it observed." |
| Product or preference choices that no experiment can settle are left for the user to make. | "Leave product or preference choices that no experiment can settle for me to make." |

Order dependencies stated under Constraints, with the reason for each:

- Steps 1 to 4 come before step 5. Reason: upstream says "Before rewriting it, do four things" and "Then rewrite my prompt to ask for exactly that", and step 5 asks for what steps 1 to 4 state. Stated as "Steps 1 to 4 are the four things to do before rewriting. They come before step 5, which asks for what they state."

Also: 4 statements moved to the section their function calls for; 5 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/architect/SKILL.md`

Title: Architect. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Settle the shape of a change before code is written, so that jumping to code does not lock in the wrong shape.

| Outcome | Basis in the upstream text |
| --- | --- |
| Every system the change touches is traced before code is written. | "Before writing code, trace every system the change touches" |
| Unless the design is large or contested, two different shapes for the change (types, signatures, module boundaries) are sketched before code is written. | "then sketch two different shapes for it (types, signatures, module boundaries)", with the condition from "For a large or contested design, run the **arena** skill instead of sketching alone." |
| For a large or contested design, the shape comes from the **arena** skill instead of from sketching alone. | "For a large or contested design, run the **arena** skill instead of sketching alone." |
| Where two shapes are sketched, the picked one is the shape where each piece of state has one owner, each task has one way to do it, and callers need to know least. | "and pick the one where each piece of state has one owner, each task has one way to do it, and callers need to know least." |
| Where workarounds repeat, a redesign replaces patching. | "Redesign instead of patching if workarounds repeat." |

Carried from the frontmatter description into the body:

- "then stay in the loop while implementation fills in" (carried as Task 4, "Stay in the loop while implementation fills in.", with its order word "then" stated under Constraints as "Staying in the loop while implementation fills in comes after the sketch.")
- "non-trivial work where jumping to code would lock in the wrong shape" (one of the "Use for" triggers; not carried as a rule. It is the basis of the Purpose clause "so that jumping to code does not lock in the wrong shape". See profile_issues.)

Order dependencies stated under Constraints, with the reason for each:

- Staying in the loop while implementation fills in (Task 4) comes after the sketch. Reason: the description says "Sketch ... before code, then stay in the loop while implementation fills in".
- Inside Task 1, kept in upstream's sentence and not restated under Constraints: "Before writing code", and "trace every system the change touches, then sketch ... and pick".

State-changing or external effects the work can have, with the condition upstream states:

- None of its own before code. Task 3 runs the **arena** skill, which spawns subagents and gives each candidate a git worktree or a `/tmp/arena-<slug>/candidate-<n>/` directory. Condition upstream states: "For a large or contested design". Upstream states no approval.
- Task 2, "Redesign instead of patching", can change the code the change touches. Condition upstream states: "if workarounds repeat". Upstream states no approval.

Also: 1 statements moved to the section their function calls for; 3 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/tdd/SKILL.md`

Title: TDD Bug Fix. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** When fixing a bug with a clear, cheap test path, make the broken behavior executable before changing production code. The goal is a focused regression test that fails before the fix and passes after it.

| Outcome | Basis in the upstream text |
| --- | --- |
| Where the bug has a clear, cheap test path, a focused regression test fails for the intended reason before production code changes. | Opening paragraph: "make the broken behavior executable before changing production code", "a focused regression test that fails before the fix". Workflow steps 3 and 4: "Write the failing test first.", "Confirm it fails for the intended reason." |
| Where the bug has a clear, cheap test path, the regression test that failed before the fix passes after it. | Opening paragraph: "When fixing a bug with a clear, cheap test path", "and passes after it". Workflow step 6: "Rerun the regression test. Confirm the test now passes." |
| Where a failing test is impractical, the bug is checked by the closest executable regression check instead of a new test. | Second paragraph: "skip adding a new test and use the closest useful verification instead". If a Failing Test Is Impractical: "Use the closest executable regression check instead", "Prefer no new test over a bad test." |
| The final response names the passing-after test run and any nearby validation performed. | Final Response: "Report the evidence, not just the outcome" and its second item, "Name the passing-after test run and any nearby validation performed." Unconditional upstream. |
| The final response names the failing-before test or executable check and the failure it produced, or, where failing-before evidence could not be demonstrated, states why and describes the closest regression check used instead. | Final Response, first and third items. The third replaces only the failing-before evidence. |

Carried from the frontmatter description into the body:

- "Use only when the user explicitly asks for TDD, a failing test, or a regression test, OR when the bug has an obvious cheap local test target. Skip when the test path is unclear, expensive, integration-heavy, or not requested." (carried as "## Entry Criteria", with "this skill" and "it" supplied as objects: "Use this skill only when ... Skip it when ...". Placed as conditions for beginning the work, its function in the description, so that it is not read as a mid-run rule beside the body's fallback. The body lacked "the user explicitly asks for TDD, a failing test, or a regression test" and "not requested".)

Order dependencies stated under Constraints, with the reason for each:

- Steps 3 and 4 come before step 5. Reason: "make the broken behavior executable before changing production code", "Write the failing test first.", "Run the new test before fixing.", "correct the test or reproduction before editing the implementation". Step 4 captures the failing state that step 5 changes.
- Step 6 comes after step 5. Reason: "Rerun the regression test. Confirm the test now passes." uses the fix.
- Kept inside its own bullet under Guardrails: "first land the focused regression path, then consider additional sibling coverage".

State-changing or external effects the work can have, with the condition upstream states:

- Adds a regression test and changes production code in the working tree (Workflow steps 3 and 5). Condition upstream states: Upstream states no approval. Limits: "Make the smallest production change ...", "Do not change tests merely to match a wrong implementation.", "Do not weaken existing assertions unless the expected behavior has genuinely changed and the reason is clear."
- "first land the focused regression path" (Guardrails). "land" is not defined and can mean a commit or a merge. Condition upstream states: "If the bug exposes a broader class of failures". Upstream states no approval.

Also: 7 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).
