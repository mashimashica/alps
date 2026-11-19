# Conversion record: Principles: verification, part 2, delegation, and meta

[Conversion guide](../README.md)

## `skills/principle-sequence-verifiable-units/SKILL.md`

Title: Sequence work into verifiable units. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Make multi-step work a sequence of small units that each end in a verifiable state, so that the work is checked as it advances and the delivered sequence proves itself to a reviewer.

| Outcome | Basis in the upstream text |
| --- | --- |
| The work is a sequence of small units, each ending in a state that is checked green before the next begins. | Body paragraph 1: 'Order work as small units that each end in a state you can check, and do not advance until the current one is green.' Body paragraph 2: 'each unit is a bracket: known-good state, one change, run the check, proceed. Run the per-unit check even when a tool does the edits.' Description: 'Break work into small units that each end in a verifiable state, check each before the next'. The division into small units is asserted in the Outcome (review round 1, W8), so one large unit checked once at the end fails it. |
| The work is delivered in the order that proves it to a reviewer. | Body paragraph 3: 'Deliver in the order that proves the work: the failing test first, then the fix. The subtraction before the reshape. The baseline before the treatment.' Description: 'order delivery so the sequence proves itself to a reviewer'. |

Carried from the frontmatter description into the body:

- "Apply to multi-step work (sweeps, migrations, runs of similar edits) and to how you stack commits and PRs." Carried as the first Constraints sentence. The body names commits only, so the scope 'and PRs' reaches the body through this sentence.
- "order delivery so the sequence proves itself to a reviewer" The body has the rule ('Deliver in the order that proves the work') but not its audience. The words 'to a reviewer' are carried in the Purpose and in the second Outcome.

State-changing or external effects the work can have, with the condition upstream states:

- Shapes how commits and PRs are ordered and delivered ('Deliver in the order that proves the work', 'Each commit lands on its own', description: 'how you stack commits and PRs'). Condition upstream states: This file states no approval or condition for committing, pushing, or opening PRs. The citing playbook or skill governs those actions.

Also: 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-test-behavior-not-implementation/SKILL.md`

Title: Test Behavior, Not Implementation. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Make each test a claim about what the code's users can observe, so that the test fails when that behavior breaks and keeps passing when only the internals change.

| Outcome | Basis in the upstream text |
| --- | --- |
| Each test written, changed, or kept fails when the behavior it claims breaks. | Bullet 'Break the behavior (a wrong value, a skipped or doubled effect). If the test still passes, it proves nothing.' Final paragraph: 'Keep a test that catches the first edit and survives the second. Rewrite or delete the rest.' Description: 'the test fails when that behavior breaks'. |
| Each test written, changed, or kept still passes when the internals change and every observable result stays the same. | Bullet 'Change the internals and keep every observable result. If the test fails, it is pinned to the implementation.' Final paragraph: 'Keep a test that catches the first edit and survives the second. Rewrite or delete the rest.' Description: 'keeps passing when only the internals change'. |

Carried from the frontmatter description into the body:

- "Apply when you write, change, or keep a test." Carried as the first Constraints sentence.
- "Assert what the code's users can observe, so that the test fails when that behavior breaks and keeps passing when only the internals change." The upstream body already states this rule in its own words (opening definition, the two imagined edits, 'Keep a test that catches the first edit and survives the second'). The description's wording is used for the Purpose and the two Outcomes. No new Task was added for it.

State-changing or external effects the work can have, with the condition upstream states:

- Rewrites or deletes tests in the repository ('Rewrite or delete the rest.'). Condition upstream states: Upstream states no approval. The only condition is the test's result against the two imagined edits.

Also: 4 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-explain-the-number/SKILL.md`

Title: Explain the Number. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Establish what limits a measured number, and that it measured the work you think and nothing else, before the number is trusted, reported, or acted on for the decision it was measured for.

| Outcome | Basis in the upstream text |
| --- | --- |
| The decision is written before the run, with the result that would change it and the noise floor named. | Bullet 1: 'Write the decision before you run. Name the result that would change it, and the noise floor.' |
| Where the run-to-run spread is not larger than the effect, the limiter named for the number is the resource or code path that bounds the result, taken from a profile or counters during a run. | Bullet 2: 'Name the resource or code path that bounds the result, from a profile or counters taken during a run. A guess from reading the code is not a limiter.' Description: 'Find what limits it'. Condition: Bullet 1 'Stop when the run-to-run spread is larger than the effect.' is upstream's ending for the noise case, so the Outcome is conditioned on the path where the work does not stop. |
| Where the run-to-run spread is not larger than the effect, each other thing the number could be measuring is ruled out with evidence. | Bullet 3: 'List what else the number could be measuring (errors, skipped or cached work, code that never ran, an untuned side, noise, a piece too small to matter) and rule out each one with evidence.' Description: 'rule out that it measured something other than the work you think'. For an eval result, the closing paragraph's three questions are instances of the same check. Condition: Bullet 1 'Stop when the run-to-run spread is larger than the effect.' is upstream's ending for the noise case, so the Outcome is conditioned on the path where the work does not stop. |
| Where the run-to-run spread is not larger than the effect, the run count, the spread, and the limiter are kept with the number. | Bullet 4: 'Keep the run count, the spread, and the limiter with the number.' Condition: Bullet 1 'Stop when the run-to-run spread is larger than the effect.' is upstream's ending for the noise case, so the Outcome is conditioned on the path where the work does not stop. |

Carried from the frontmatter description into the body:

- "Apply before you measure, and before you trust, report, or act on a number you measured: a speedup, a regression, a throughput, a latency, or an eval result." Carried as the first Constraints sentence.
- "Find what limits it, and rule out that it measured something other than the work you think." The upstream body already states both halves in its own words (bullets 2 and 3). Nothing was added to the Tasks for it.

Also: 2 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-guard-the-context-window/SKILL.md`

Title: Guard the Context Window. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Keep bulk and oversized phases from overflowing the context window.

| Outcome | Basis in the upstream text |
| --- | --- |
| The main thread holds summaries of the bulk, not raw payloads. | Description: 'Route bulk to subagents; keep summaries in the main thread, not raw payloads.' Citing playbooks rely on the same result ('keep the reduced finding in the main thread'). |
| Phases are sized and scope is capped, with files per phase limited, turn budgets set, and mechanism costs accounted for. | Body bullet: 'Size phases and cap scope. Limit files per phase, set turn budgets, account for mechanism costs.' |

Carried from the frontmatter description into the body:

- "Apply when context is filling up: large outputs, long files, repeated reads, fan-out planning." Carried as the first Constraints sentence.
- "Route bulk to subagents; keep summaries in the main thread, not raw payloads." The upstream body does not state this rule. Carried verbatim as Task 1.

Headings whose text changed:

- "**Why:**" became "> NOTE". Profile section 6. The label marks a rationale, which the Framework presents as a note. The token screen reports this label as moved.
- "**Pattern:**" became "## Tasks". The label only introduces the list of what to do. The Tasks heading and governing sentence take that role. No file cites the label. The token screen reports it as absent.

Also: 2 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-never-block-on-the-human/SKILL.md`

Title: Never Block on the Human. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Keep agents unblocked on reversible work and the system self-healing, with the human supervising asynchronously and course-correcting after the fact.

| Outcome | Basis in the upstream text |
| --- | --- |
| Reversible actions proceed without blocking on the human. | Opening paragraph: 'Agents must stay unblocked. Make reasonable decisions, proceed'. Bullet 1: 'Don't ask "should I do X?" Do X'. Bullet 4: 'Reversible actions (write code, edit notes, split tasks) should proceed without blocking.' Bullet 5: 'Execution should not block.' |
| The result of the work is shown to the human with the reason for what was done. | Bullet 1: 'Proceed, then present. Do the work, show the result. ... Do X, explain why.' Opening paragraph: 'let the human course-correct after the fact'. |
| Each problem noticed is logged and fixed in the next round. | Bullet 2: 'Make the system self-healing. When you notice a problem, log it and fix it in the next round.' The Purpose names 'self-healing' with upstream's word so that this Outcome is necessary for it (review round 1, W4). |

Carried from the frontmatter description into the body:

- "Apply when tempted to ask 'should I do X?' on reversible work." Carried as the first Constraints sentence, with the body's double quotation marks around the question.

State-changing or external effects the work can have, with the condition upstream states:

- Irreversible actions: force-push, delete production data, send external messages. Condition upstream states: 'still require confirmation' (kept verbatim under Constraints).
- Reversible actions: write code, edit notes, split tasks. Condition upstream states: 'should proceed without blocking'. No approval is required. The human course-corrects after the fact.

Also: 4 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-encode-lessons-in-structure/SKILL.md`

Title: Encode Lessons in Structure. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Carry a lesson that keeps recurring in structure wherever it can be encoded, not in one more repetition of the instruction.

| Outcome | Basis in the upstream text |
| --- | --- |
| Where the rule can be encoded, a lint, metadata flag, runtime check, or script carries it instead of more text. | Description: 'Encode the rule as a lint, metadata flag, runtime check, or script instead of more text.' Body: '**Corollary:** If the fix is structural, only use the structural fix.' The condition 'Where the rule can be encoded' is the complement of the body's 'If the lesson needs judgment and cannot be encoded'. |
| Where the lesson needs judgment and cannot be encoded, its instruction is more prominent and has an example of the failure mode. | Body sentence 1: 'If the lesson needs judgment and cannot be encoded, make the instruction more prominent and add an example of the failure mode.' |

Carried from the frontmatter description into the body:

- "Apply when you catch yourself writing the same instruction a second time, or notice a recurring correction." Carried as the first Constraints sentence.
- "Encode the rule as a lint, metadata flag, runtime check, or script instead of more text." The upstream body does not state this rule. Carried verbatim as Task 1.

State-changing or external effects the work can have, with the condition upstream states:

- Adds a lint, metadata flag, runtime check, or script to the repository, or edits an instruction to make it more prominent and add an example. Condition upstream states: Upstream states no approval. These are changes inside the repository.

Also: 2 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).
