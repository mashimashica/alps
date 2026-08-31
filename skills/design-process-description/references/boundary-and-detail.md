# Boundary and Detail

Use this reference to answer: **What belongs in the reusable Process, and what detail should remain with one application?**

## Process and Application

A Process Description holds knowledge intended to remain useful across repeated applications. One application supplies the concrete subject, requested result, values, people, tools, files, repository state, dates, and other local context.

Keep information in the Process Description only when changing it would change the recurring work itself. Leave information with the application when it selects one valid instance of that work.

Examples:

| Reusable Process knowledge | Application-specific information |
| --- | --- |
| The kind of success that must be observable | The requested target or acceptance value for this case |
| A safety check required in every relevant use | The current evidence and risk level |
| The meaning of a required Handoff | The actual file, message, or recipient used this time |
| A condition that determines whether work may start | Whether that condition is currently true |

## Set the Boundary

Include work needed to achieve one Purpose and its Outcomes. Exclude upstream preparation, downstream use, governance, and neighboring purposes unless the Process itself must establish their success conditions.

Use these tests:

- **Cohesion:** Every included element contributes to the same Purpose.
- **Completeness:** The Process does not depend on hidden recurring work inside its chosen boundary.
- **Reusability:** The description remains applicable across representative cases.
- **Ownership of success:** The Process claims only states it can reasonably establish or assess.

## Choose Granularity

Split a description when independent purposes can be selected, performed, changed, or assessed separately. Merge descriptions when their stated purposes are only fragments of one success condition and separating them would require persistent hidden context or meaningless Handoffs.

Do not split solely because the work has several Tasks. Do not merge solely because two Processes are frequently used together.

## Add Activities and Tasks Only When Needed

Start with Name, Purpose, and Outcomes. Add Activities or Tasks only when at least one of these is true:

- the work content is otherwise materially ambiguous;
- an omission would create a correctness or safety risk;
- a required responsibility or Handoff cannot be understood from Outcomes alone; or
- assessment needs a stable description of essential work.

Describe what work must occur, not a preferred implementation script. Avoid exhaustive checklists for uncommon cases.

## Avoid Unnecessary Implementation Commitments

Keep the reusable Process independent of a performer, role, agent, tool, method, metric, file format, repository layout, and execution sequence unless a particular commitment is necessary to the Process's meaning or safety.

When a commitment appears necessary, ask:

1. Would a different capable performer or tool make the Process invalid?
2. Does the order express a real dependency, or only one convenient workflow?
3. Does the metric define an Outcome or constraint, or merely report one implementation?
4. Can the detail be supplied by the application without changing the Process?

Prefer dependencies and conditions over a fixed total sequence. Preserve alternative valid methods.

## Entry and Exit Criteria

Add Entry Criteria only when work must not begin, or cannot be meaningful, before a testable condition holds. Add Exit Criteria only when Outcomes alone do not make permissible completion clear.

Do not restate every Input as an Entry Criterion or every Outcome as an Exit Criterion. Criteria should resolve a real start or completion ambiguity.

## Simplify an Existing Skill

Use evidence from actual use: failed results, repeated clarification, ignored instructions, duplicated guidance, excessive reading, brittle branches, and workarounds.

For each detail, ask whether removing it would reduce correctness, safety, meaning, composability, or assessability in a representative case. If not, remove it. If a rule repeatedly needs exceptions, replace it with the underlying condition or remove it. If multiple passages make the same decision, keep one authoritative statement.

Do not preserve complexity solely for compatibility with an obsolete internal structure. Record unresolved uncertainty instead of building a speculative extension point.

## Result

Produce one cohesive boundary with the minimum durable detail needed across repeated applications. State any boundary decision that remains uncertain and the evidence needed to resolve it.
