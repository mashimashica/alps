# Conversion record: Principles: architecture, part 2, and verification, part 1

[Conversion guide](../README.md)

## `skills/principle-type-system-discipline/SKILL.md`

Title: Type System Discipline. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Make the compiler reject impossible states, mismatched primitives, and unhandled variants.

| Outcome | Basis in the upstream text |
| --- | --- |
| The compiler rejects impossible states. | Body lead: 'Make the compiler reject impossible states, mismatched primitives, and unhandled variants.' Description: 'Make illegal states unrepresentable'. |
| Arguments that share a primitive type but mean different things each have their own type, so the compiler rejects a mismatch. | Body bullet 1: '**Brand semantic primitives.** If two arguments share a primitive type but mean different things, give each its own type.' Body lead: 'Make the compiler reject ... mismatched primitives'. |
| External data is typed only by a parse function at the boundary that returns the typed model. | Body bullet 2: '**External data is untyped until parsed.** JSON, RPC payloads, CLI args, config, environment variables, and database rows go through a parse function at the boundary that returns the typed model.' Description: 'parse external data at boundaries'. |
| The compiler rejects unhandled variants. | Body lead: 'Make the compiler reject ... unhandled variants.' Description: 'exhaust variants'. |
| Where a schema file owns a shape, the type is derived from it and no parallel type is hand-rolled. | Body bullet 3: '**Derive types from authoritative schemas.** When a schema file owns a shape, derive the type from it instead of hand-rolling a parallel one.' |

Carried from the frontmatter description into the body:

- "Apply when designing types, reviewing a function signature, or writing code in any statically-typed language." Carried as the first Constraints sentence in declarative form.
- "Make illegal states unrepresentable" Carried as Task 1. The upstream body has no instruction in these words. Its lead names only the result ('Make the compiler reject impossible states').
- "exhaust variants" Carried as Task 4 ('Exhaust variants.'). The upstream body has no instruction in these words. Its lead names only the result ('Make the compiler reject ... unhandled variants').

Also: 3 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-make-operations-idempotent/SKILL.md`

Title: Make Operations Idempotent. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Design every state-changing operation to converge to the correct state however many times it runs and wherever the previous run stopped.

| Outcome | Basis in the upstream text |
| --- | --- |
| Every state-changing operation converges to the correct state however many times it runs. | Body lead: 'Design every state-changing operation to converge to the correct state however many times it runs ...' Test paragraph: 'what happens if this runs twice?' |
| Every state-changing operation converges to the correct state wherever the previous run stopped. | Body lead: '... and wherever the previous run stopped.' Test paragraph: 'What if the previous run crashed at every possible point?' Description: 'Converge to the same end state regardless of partial prior runs.' |
| Anything a run leaves behind is recognizable as stale by the next run, by evidence that holds wherever the previous run could have stopped. | Body paragraph 3: 'Anything a run leaves behind (a lock, a temporary file, a half-written record, a claimed job) must be recognizable as stale by the next run, by evidence that holds wherever the previous run could have stopped.' |

Carried from the frontmatter description into the body:

- "Apply when designing commands, lifecycle steps, or processing loops that run amid crashes, restarts, and retries." Carried as the first Constraints sentence in declarative form.

Also: 4 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md`

Title: Migrate Callers Then Delete Legacy APIs. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Complete the move to a new internal API in one wave, leaving no old API or compatibility layer behind.

| Outcome | Basis in the upstream text |
| --- | --- |
| Callers are migrated to the new API. | Description: 'Migrate callers ...' Title: 'Migrate Callers Then Delete Legacy APIs'. |
| The old API is deleted in the same wave as the caller migration. | Description: '... and delete the old API in the same wave ...' Split from the caller migration because the two results can fail independently. |
| No compatibility layer is preserved. | Description: '... instead of preserving compatibility layers.' |
| The tests assert the new contract. | Body bullet: 'Update tests to assert the new contract ...' |
| No test remains that only protects pre-refactor implementation details. | Body bullet: '... and delete tests that only protect pre-refactor implementation details' |

Carried from the frontmatter description into the body:

- "Apply when introducing a new internal API while old callers still exist." Carried as the first Constraints sentence in declarative form.
- "Migrate callers and delete the old API in the same wave instead of preserving compatibility layers." The upstream body does not state this rule. Carried verbatim as Task 1.

State-changing or external effects the work can have, with the condition upstream states:

- Deletes the old API in the repository, in the same wave as the caller migration. Condition upstream states: The three conditions under '**When this applies:**' (no external users depend on backward compatibility, the project can absorb coordinated breaking changes, the new API is part of a simplification or refactor initiative). Upstream states no approval.
- Deletes tests that only protect pre-refactor implementation details. Condition upstream states: Only tests of that kind. Upstream states no approval.

Also: 2 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-separate-before-serializing-shared-state/SKILL.md`

Title: Separate Before Serializing Shared State. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Eliminate the sharing between concurrent actors first, and serialize access structurally only where one shared write target is a real invariant.

| Outcome | Basis in the upstream text |
| --- | --- |
| Where one shared write target is not a real invariant, each concurrent actor writes its own file, key, branch, or state directory. | Body paragraph 1: 'Default to giving each actor its own file, key, branch, or state directory ...' The condition comes from paragraph 2: 'Only when one shared write target is a real invariant, serialize ...'. Description: 'Eliminate the sharing first'. |
| Where one shared write target is not a real invariant, the state is merged only where it is read. | Body paragraph 1: '... and merge only where the state is read.' Same condition as Outcome 1. Split from Outcome 1 because separate write targets and merging only at the read site can fail independently. |
| Where one shared write target is a real invariant, access to it is serialized structurally, not by instructions. | Body paragraph 2: 'Only when one shared write target is a real invariant, serialize access structurally (a lockfile, a single writer, sequential phases, compare-and-swap). Instructions are not concurrency control ...' |

Carried from the frontmatter description into the body:

- "Apply when concurrent actors might write to the same file, branch, key, or state object." Carried as the first Constraints sentence in declarative form.
- "Eliminate the sharing first; serialize structurally only when one shared writer is a real invariant." The body states this rule in other words (default to separate targets, serialize only on a real invariant). The description's words 'Eliminate the sharing' and 'first' are carried in the Purpose, with the body's term 'one shared write target' in place of 'one shared writer'.

Order dependencies stated under Constraints, with the reason for each:

- Task 1 (the question) comes first. Reasons: upstream's order word 'first ask', and Task 3's condition ('Only when one shared write target is a real invariant') uses the answer.

State-changing or external effects the work can have, with the condition upstream states:

- Giving each actor its own file, key, branch, or state directory creates those write targets. Condition upstream states: Upstream states no approval or condition. The citing description (arena, figure-it-out, feature, visual-parity) governs where they are created.

Also: 4 statements moved to the section their function calls for; 5 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-prove-it-works/SKILL.md`

Title: Prove It Works. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Prove that a completed task works before it is declared done, by evidence from the real artifact and not from a proxy.

| Outcome | Basis in the upstream text |
| --- | --- |
| Before the task is declared done, a direct check of the real thing, not a proxy, shows that every output works. | Body paragraph 1: 'Verify every output by checking the real thing directly: run the feature, read the actual value, inspect the diff. Proxies (file mtimes, self-reports, cached output, "it compiles") do not count.' Description: 'Apply after completing a task, before declaring done. Verify against the real artifact ..., not a proxy, self-report, or 'it compiles.'' Title: 'Prove It Works'. The Outcome states what the check shows, not only that a check ran. |
| Where the check can be scripted, it is scripted. | Body paragraph 2: 'Script the check when you can.' |
| The output of a scripted check is where the human can see it. | Body paragraph 2: 'Keep its output where the human can see it ...' |

Carried from the frontmatter description into the body:

- "Apply after completing a task, before declaring done." Carried as the first Constraints sentence in declarative form. The body does not state when the principle applies.
- "Verify against the real artifact (run the feature, read the actual value, inspect the diff), not a proxy, self-report, or 'it compiles.'" The body states this rule in other words (Task 1). The description's term 'the real artifact', which the citing playbooks use, is carried in the Purpose.

State-changing or external effects the work can have, with the condition upstream states:

- Commits the check script or its output ('commit it'). Condition upstream states: 'only when the trail must be auditable later'. Upstream states no approval.
- Running the feature can change state in whatever the feature touches. Condition upstream states: Upstream states no condition. The citing description governs.

Also: 3 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-fix-root-causes/SKILL.md`

Title: Fix Root Causes. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Fix the fault, not the place where it surfaced. The root cause is the first place the system did something it should not do, or failed to handle a state it should handle.

| Outcome | Basis in the upstream text |
| --- | --- |
| The fix is at the root cause, not at the place where the fault surfaced. | Body lead: 'Fix the fault, not the place where it surfaced. The root cause is the first place ...' Description: 'Trace each symptom back to the first place the system went wrong and fix it there.' |
| A guard is a fix only where the state it handles is legitimate. | Description: 'A guard is a fix only when the state it handles is legitimate.' Body bullet 2: 'Ask whether the state that triggered the symptom is legitimate. If it is, handle it where the code broke. If it should never exist, a check there hides the bug, so find what produced it.' |
| The fix covers every place with the same fault. | Body bullet 3: 'Fix the pattern, not the instance. Find every place with the same fault.' |
| Where the deciding fact took a deep dig, the cheap, always-on signal that would have shown it at first look is proposed. | Body bullet 4: 'If the deciding fact took a deep dig, propose the cheap, always-on signal that would have shown it at first look.' |

Carried from the frontmatter description into the body:

- "Apply when debugging." Carried as the first Constraints sentence in declarative form. The body does not state when the principle applies.
- "A guard is a fix only when the state it handles is legitimate." The body states this rule in other words (bullet 2, with 'check' for 'guard'). The description's sentence is the wording of Outcome 2, with 'where' for 'when' to mark the condition and the article 'a' kept.

Order dependencies stated under Constraints, with the reason for each:

- Reproduction comes first. Reason: upstream's order word in 'Reproduce first.' The item names nothing that follows, as upstream names nothing. No other order among the Tasks is stated, and the Constraints permit any other order.

State-changing or external effects the work can have, with the condition upstream states:

- Edits code for the fix and for instrumentation ('instrument and read the actual state'). Condition upstream states: Upstream states no approval or condition. Nothing in this file acts outside the repository.

Also: 4 statements moved to the section their function calls for; 6 additions other than the Purpose and Outcomes (fixed sentences, pointers).
