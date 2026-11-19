# Conversion record: Principles: core, part 1

[Conversion guide](../README.md)

## `skills/principle-laziness-protocol/SKILL.md`

Title: Laziness Protocol. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Solve the problem without building more than it needs.

| Outcome | Basis in the upstream text |
| --- | --- |
| Each choice the work makes or touches sits behind one source of truth instead of being repeated in several places. | Body bullet 1: "**Consolidate decisions.** Do not repeat the same choice in several places. Put it behind one source of truth and pass the result as a simple flag." Scoped to the choices the work makes or touches. "pass the result as a simple flag" stays in Task 1 only. |
| The change is the smallest that solves the problem. | Body bullet 2: "**Minimize the diff.** Make the smallest change that solves the problem." Description: "Bias toward deletion and the smallest change that solves the problem." |

Carried from the frontmatter description into the body:

- "Apply when refactoring, evaluating diff size, or tempted to add abstractions, layers, or signal threading." Carried as the first Constraints sentence in declarative form: "This principle applies when refactoring, evaluating diff size, or tempted to add abstractions, layers, or signal threading."
- "Bias toward deletion and the smallest change that solves the problem." Carried verbatim under Controls. The upstream body never mentions deletion.

Also: 3 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-foundational-thinking/SKILL.md`

Title: Foundational Thinking. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Get the foundations right before writing logic so downstream code becomes obvious.

| Outcome | Basis in the upstream text |
| --- | --- |
| The chosen data structures match the dominant access paths before logic is written. | Body paragraph 1: "Get the data shape right before writing logic. Define core types early, trace every access pattern, and choose structures that match the dominant paths." "Define core types early" stays in Task 1 only. |
| Actors share state only where nothing happens if another actor modifies it concurrently. Any other state that actors would share is isolated. | Body paragraph 2: "Before sharing state between actors, ask what happens if another actor modifies it concurrently. If the answer is not \"nothing\", isolate." |
| Whatever helps every later phase (CI, tests, shared types) is in place first, after dead code is removed. | Body paragraph 3, sentences 1 and 2: "Scaffold first. Whatever helps every later phase (CI, tests, shared types) goes first, after removing dead code." |
| Commits are small and single-purpose. | Body paragraph 3, sentence 3: "Keep commits small and single-purpose." |

Carried from the frontmatter description into the body:

- "Apply before writing logic: choosing core types and data structures, sequencing scaffold-vs-feature work, asking what concurrent actors share." Carried as the first Constraints sentence: "This principle applies before writing logic: choosing core types and data structures, sequencing scaffold-vs-feature work, asking what concurrent actors share."
- "Get the data structures right so downstream code becomes obvious." Carried verbatim as the last sentence of Task 1. The upstream body has the rule ("Get the data shape right before writing logic") but not the reason "so downstream code becomes obvious". The Purpose uses the same reason.

State-changing or external effects the work can have, with the condition upstream states:

- Creating commits (Task 3: "Keep commits small and single-purpose.") Condition upstream states: None stated in this file.

Also: 3 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-redesign-from-first-principles/SKILL.md`

Title: Redesign From First Principles. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Preserve option value when integrating changes into an existing design.

| Outcome | Basis in the upstream text |
| --- | --- |
| The design after the change is the one that would be built from scratch with the new requirement, not the existing design with the change bolted on. | Lead paragraph: "When integrating a change, don't bolt it onto the existing design. Redesign as if the requirement had been a foundational assumption from the start." Bullet 2: "Ask: \"if we were writing this from scratch with this new requirement, what would we build?\"" |
| Every reference reflects the change: types, docs, examples, rationale sections. | Bullet 3: "Propagate the change through every reference: types, docs, examples, rationale sections" |

Carried from the frontmatter description into the body:

- "Apply when integrating a new requirement into an existing design." Carried as the first Constraints sentence: "This principle applies when integrating a new requirement into an existing design." The description states no other rule.

State-changing or external effects the work can have, with the condition upstream states:

- Delivering the redesign (Task 5: "deliver it incrementally"). The file names no delivery mechanism. Condition upstream states: None stated in this file.

Also: 1 statements moved to the section their function calls for; 3 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-attack-the-premise/SKILL.md`

Title: Attack the Premise. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Ground the next fix in evidence about the premise that the failed fixes share.

| Outcome | Basis in the upstream text |
| --- | --- |
| The premise is written down, as the one sentence every failed fix assumed, before the next fix starts. | Bullet 1: "Write the premise down: the one sentence every failed fix assumed." Closing sentence: "Do not start the next fix before the premise is written down and tested." |
| The premise is tested before the next fix starts, by an observation that would come out differently if the premise were false. | Bullet 2: "Test it before the next fix. Find an observation that would come out differently if the premise were false, and make it." Closing sentence: "Do not start the next fix before the premise is written down and tested." |
| Where the evidence contradicts the premise and one part always lands on the losing side, the change is to what puts it there, not a mechanism that cleans up after it. | Bullet 3: "If the evidence contradicts the premise, look for what the failures share that it did not predict. If one part always lands on the losing side, change what puts it there instead of adding a mechanism that cleans up after it." |

Carried from the frontmatter description into the body:

- "Apply when two or more fixes that share one premise have failed the same gate." Carried as the first Constraints sentence: "This principle applies when two or more fixes that share one premise have failed the same gate." The body's lead sentence already states the same trigger and is kept as Task 1.

Order dependencies stated under Constraints, with the reason for each:

- dependency: "Do not start the next fix before the premise is written down and tested."; reason: Upstream's closing sentence states it with "before". It gates the next fix, which is not one of the listed Tasks, on the results of Tasks 2 and 3. Task 3 keeps its own "Test it before the next fix."
- dependency: Task 3 comes before Task 4, which acts on its evidence.; reason: Task 4 ("If the evidence contradicts the premise ...") uses a result only Task 3 produces (profile section 5). No order between the other Tasks is stated or added, and the order sentence does not make the listed order the default (amendment 15.2).

Also: 1 statements moved to the section their function calls for; 3 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-subtract-before-you-add/SKILL.md`

Title: Subtract Before You Add. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Make each addition, refactor, or rewrite build on a simpler base than it found.

| Outcome | Basis in the upstream text |
| --- | --- |
| Complexity is removed before construction, and construction builds on the simpler base. | Paragraph 1: "When evolving a system, remove complexity first, then build." Bullet 1: "Sequence removal before construction". Description: "then build on the simpler base". |
| The design is left slightly simpler and more capable, behind the same or smaller surface, than it was found. | Paragraph 2: "Leave the design slightly simpler and more capable behind the same or smaller surface than you found it." |
| What the work adds or changes serves observed usage, not speculative edge cases. | Bullet 3: "Design for observed usage, not speculative edge cases". Scoped to what the work adds or changes, since upstream states it as an action on the agent's design. Bullet 4 is carried by Constraints only. |

Carried from the frontmatter description into the body:

- "Apply when sequencing an addition, refactor, or rewrite." Carried as the first Constraints sentence: "This principle applies when sequencing an addition, refactor, or rewrite."
- "Remove dead code, redundant validators, and stub references first, then build on the simpler base." Carried verbatim as the third sentence of Task 1. The upstream body names neither dead code nor redundant validators, and refactoring.md step 4 cites this skill for them.

State-changing or external effects the work can have, with the condition upstream states:

- Deleting code and reference files in the repository (Task 1: "Remove dead code, redundant validators, and stub references first"; Task 7: "delete it rather than leaving a stub") Condition upstream states: None stated in this file.

Also: 1 statements moved to the section their function calls for; 3 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-minimize-reader-load/SKILL.md`

Title: Minimize Reader Load. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Minimize reader load. Reader load is the work a reader must do to understand code. It has two independent axes: layers to trace between the question and the answer, and hidden or mutable state to hold in their head.

| Outcome | Basis in the upstream text |
| --- | --- |
| A new reader can answer "where does X come from?" and "what can change X?" in under 30 seconds. | Closing paragraph: "The test: can a new reader answer \"where does X come from?\" and \"what can change X?\" in under 30 seconds? If not, cut layers or cut state." The two questions match the two axes of the lead paragraph. |

Carried from the frontmatter description into the body:

- "Apply when reviewing or shaping code that's hard to trace." Carried as the first Constraints sentence: "This principle applies when reviewing or shaping code that's hard to trace."
- "Count layers between question and answer, and hidden state in the reader's head" (first clause of the description's second sentence). Carried verbatim as the second sentence of Task 1. The upstream body never says to count. The second clause, "collapse one-caller wrappers and shrink mutable scope", is not repeated because the body states both rules (Tasks 2 and 3).

Also: 3 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).
