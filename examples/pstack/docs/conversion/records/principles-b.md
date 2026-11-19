# Conversion record: Principles: core, part 2, and architecture, part 1

[Conversion guide](../README.md)

## `skills/principle-outcome-oriented-execution/SKILL.md`

Title: Outcome-Oriented Execution. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Bring a planned rewrite or migration to its intended, verifiable end state without throwaway compatibility code that preserves smooth intermediate states, while keeping intermediate breakage planned, scoped, and reversible and actively touched areas checked.

| Outcome | Basis in the upstream text |
| --- | --- |
| No throwaway compatibility code preserves a smooth intermediate state. | Description: "don't preserve smooth intermediate states with throwaway compatibility code". Body lead: "Optimize for the intended, verifiable end state rather than preserving smooth intermediate states." Why line: "Keeping every intermediate step fully stable often creates temporary compatibility code that becomes long-lived debt." |
| Any intermediate breakage is planned, scoped, and reversible. | Core rule, bullet 2: "Intermediate breakage is acceptable when it is planned, scoped, and reversible", read as the criterion of acceptable breakage. |
| High-signal checks for actively touched areas are kept while migrating. | Guardrails, bullet 3: "Keep high-signal checks for actively touched areas while migrating". |
| At plan completion, full static and runtime verification establishes the correctness of the intended end state. | Guardrails, bullet 4: "Require full static and runtime verification at plan completion". Body lead: "the intended, verifiable end state". Why line: "prove correctness at explicit verification boundaries" (plan completion is the one boundary upstream names unambiguously). |

Carried from the frontmatter description into the body:

- "Apply during planned rewrites and migrations with explicit phase boundaries." Carried as the first Constraints sentence: "This principle applies during planned rewrites and migrations with explicit phase boundaries." The body's first guardrail states the same condition and is also kept.
- "don't preserve smooth intermediate states with throwaway compatibility code" (second clause of the description's second sentence). Carried under Constraints as "Don't preserve smooth intermediate states with throwaway compatibility code." The upstream body names compatibility code only as a rationale in the Why line and never states the prohibition.
- "Converge on the target architecture" (first clause of the same sentence) is not repeated. The body states it in the Why line, and it is Task 2.

Headings whose text changed:

- "**Why:**" became "> NOTE". Profile section 6. The label marks a rationale, which the Framework presents as a note. The token screen reports the label as absent.
- "**Guardrails:**" became "No label. Its three action bullets are Tasks 3 to 5 under '## Tasks' and its applicability bullet is under '## Constraints'.". The label only groups the list. Its bullets have two different functions, so the group could not stay whole under one element. No file cites the label. Every bullet keeps its text and force. The token screen reports the label as absent.

State-changing or external effects the work can have, with the condition upstream states:

- Leaving intermediate states of a rewrite or migration broken. Condition upstream states: "Intermediate breakage is acceptable when it is planned, scoped, and reversible", and "Declare where temporary breakage is acceptable". No approval by a person is stated.

Also: 5 statements moved to the section their function calls for; 6 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-experience-first/SKILL.md`

Title: Experience First. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Make the delight of whoever consumes the work, ahead of implementation convenience, the target of the work and the perspective from which its impact is explained.

| Outcome | Basis in the upstream text |
| --- | --- |
| Where implementation convenience conflicts with user delight, the choice made is delight, for whoever consumes the work. | Body lead: "When implementation convenience conflicts with user delight, choose delight." User paragraph: "The user is whoever consumes the work. ... Weigh their experience the same way". |
| Every feature, control, and option is justified. | Bullet 1: "Every feature, control, and option must be justified". |
| Fewer polished features ship rather than more rough ones. | Bullet 2: "Ship less, ship better (polished experience with three features beats rough one with ten)". Description: "ship fewer polished features over more rough ones". |
| The details are right (transitions, alignment, spacing, feedback, error states). | Bullet 4: "Get the details right (transitions, alignment, spacing, feedback, error states)". |
| Impact is explained from the user's perspective. | User paragraph, last sentence: "explain impact from their perspective". |

Carried from the frontmatter description into the body:

- "Apply when product, UX, or feature-scope tradeoffs come up." Carried as the first Constraints sentence: "This principle applies when product, UX, or feature-scope tradeoffs come up."
- "Choose user delight over implementation convenience; ship fewer polished features over more rough ones." Nothing was added to the Tasks for it. The upstream body states both rules in its own words (the lead sentence, now Task 1, and bullet 2, now Task 3). The description's words "fewer polished features ... more rough ones" are used in Outcome 3.

Also: 3 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-exhaust-the-design-space/SKILL.md`

Title: Exhaust the Design Space. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Base the commitment to a design on a side-by-side comparison of competing prototypes.

| Outcome | Basis in the upstream text |
| --- | --- |
| The commitment follows a side-by-side comparison of 2-3 competing prototypes. | Description: "Build 2-3 competing prototypes and compare side by side before committing." The upstream body states no result. |

Carried from the frontmatter description into the body:

- "Apply when facing a novel UI interaction or architectural decision with no precedent in the codebase." Carried as the first Constraints sentence: "This principle applies when facing a novel UI interaction or architectural decision with no precedent in the codebase."
- "Build 2-3 competing prototypes and compare side by side before committing." The upstream body does not state this rule. Carried verbatim as Task 1.

Also: 1 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-build-the-lever/SKILL.md`

Title: Build the Lever. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Have work that isn't trivial done or proven by a tool, the smallest that does the job, instead of by hand. The tool is the artifact a reviewer can rerun.

| Outcome | Basis in the upstream text |
| --- | --- |
| Work that isn't trivial is done or proven by a tool in the diff, not by hand. | Lead paragraph: "When the work isn't trivial, build the tool that does it (a codemod, script, generator, or rerunnable check) instead of doing it by hand." Bullet 3: "Applying this produces a file. No script, codemod, generator, or delegate skill in the diff means you didn't apply it." Bullet 4: "does or proves the job". |
| The tool is safe to rerun. | Bullet 1, second sentence: "Make it safe to rerun." |
| A rerun of the tool on the first unit, which was done by hand, proves the tool. | Bullet 1, first sentence: "Do the first unit by hand, then build the tool and prove it by rerunning it on that unit." |
| The tool is the smallest script that does or proves the job, not a framework. | Bullet 4: "Build the smallest script that does or proves the job, never a framework." |
| Where the work fans out, the recipe, the verification contract, and the fences are one skill that the delegates read and cannot edit. | Bullet 2, second sentence: "When you do fan out, write the recipe, the verification contract, and the fences as one skill the delegates read and cannot edit." |
| Where the work outlives the session, the tool is committed. | Bullet 3, third sentence: "Commit it when the work outlives the session." Description: "The tool is the artifact a reviewer can rerun." |

Carried from the frontmatter description into the body:

- "Apply to any non-trivial work, not just bulk work: edits, migrations, analyses, checks." Carried as the first Constraints sentence: "This principle applies to any non-trivial work, not just bulk work: edits, migrations, analyses, checks." The upstream body does not list the kinds of work.
- "The tool is the artifact a reviewer can rerun." The upstream body never names the reviewer. Carried verbatim as the second Purpose sentence, because it states what the tool is for.
- "Build the tool that does it or proves it (codemod, script, generator, or a skill your subagents follow) instead of working by hand." Nothing was added for it. The upstream body states the rule in its own words (lead paragraph, "does or proves the job" in bullet 4, "one skill the delegates read" in bullet 2).

State-changing or external effects the work can have, with the condition upstream states:

- Writing a new file (script, codemod, generator, or delegate skill) into the working tree. Condition upstream states: None stated. "Applying this produces a file."
- Committing that file. Condition upstream states: "Commit it when the work outlives the session." No approval is stated.
- Running and rerunning the tool on the work ("prove it by rerunning it on that unit"). Condition upstream states: "Make it safe to rerun." No approval is stated.

Also: 5 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-model-the-domain/SKILL.md`

Title: Model the Domain. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Have data structures, not scattered conditionals, carry the domain, without forcing a structure onto boring code.

| Outcome | Basis in the upstream text |
| --- | --- |
| Except where the shape is clear, local, and unlikely to grow, the domain is encoded in a data structure that removes branches or invalid states, not scattered across conditionals. | Paragraph 1: "Encode the domain in a data structure instead of scattering it across conditionals. The right structure makes invalid states unrepresentable and deletes branches." Paragraph 3: "distrust an abstraction that adds indirection without removing branches or invalid states", and the exception's condition "when the shape is clear, local, and unlikely to grow". |
| Boring code is kept where its shape is clear, local, and unlikely to grow. | Paragraph 3: "Do not force it. Keep boring code when the shape is clear, local, and unlikely to grow". |
| No feature in the work grows an if/else chain by one more branch. | Paragraph 4: "The sign that you skipped this: a feature that grows an if/else chain by one more branch". |
| The work adds no second boolean that must stay in sync with the first. | Paragraph 4: "... or a second boolean that must stay in sync with the first." |

Carried from the frontmatter description into the body:

- "Apply when writing stateful logic, or when code branches a lot or repeats a shape assumption across files." Carried as the first Constraints sentence: "This principle applies when writing stateful logic, or when code branches a lot or repeats a shape assumption across files." The description states no other rule.

Also: 3 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/principle-boundary-discipline/SKILL.md`

Title: Boundary Discipline. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Keep guards at system boundaries and framework dependencies in a thin shell, so that the code inside trusts its types and business logic is pure.

| Outcome | Basis in the upstream text |
| --- | --- |
| Validation, type narrowing, error handling, and the parse of raw data into domain types sit where data crosses a system boundary (CLI args, config files, external APIs, network). | Paragraph 1, sentence 1: "Validate, narrow types, and handle errors where data crosses a system boundary (CLI args, config files, external APIs, network)." Sentence 3, first clause: "Parse raw data into domain types at the boundary". Description: "Concentrate guards at system boundaries". |
| Inside, the types are trusted, with no re-validation and no redundant nil check. | Paragraph 1, sentence 2: "Inside, trust the types: no re-validation and no redundant nil checks." First test: "Is this data crossing a boundary right now? If not, the validation is redundant." |
| No transport or framework type is in the public surface. | Paragraph 1, sentence 3, second clause: "keep transport and framework types out of the public surface". |
| Business logic lives in pure functions with no framework dependencies. | Paragraph 1, sentence 4: "Business logic lives in pure functions with no framework dependencies." Second test: "Can this be a pure function the shell just calls? If yes, extract it." |
| The shell that calls the business logic is thin. | Paragraph 1, sentence 5: "The shell that calls them is thin." |

Carried from the frontmatter description into the body:

- "Apply when wiring validation, error handling, or framework adapters." Carried as the first Constraints sentence: "This principle applies when wiring validation, error handling, or framework adapters."
- "Concentrate guards at system boundaries (CLI, config, network, external APIs); trust internal types and keep business logic in pure functions." Nothing was added to the Tasks for it. The upstream body states all three rules in its own words. The description's word "guards" is used in the Purpose.

Also: 3 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).
