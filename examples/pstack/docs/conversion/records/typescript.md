# Conversion record: typescript-best-practices

[Conversion guide](../README.md)

## `skills/typescript-best-practices/SKILL.md`

Title: TypeScript best practices. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Make the TypeScript in `.ts` or `.tsx` work follow TypeScript best practices.

| Outcome | Basis in the upstream text |
| --- | --- |
| The TypeScript in the `.ts` or `.tsx` work follows the **type-system-discipline** principle skill. | The sentence under the H1: "Apply the **type-system-discipline** principle skill first." The Outcome names the principle by reference and copies none of its content, so the principle file keeps governing what following it means. The scope words "in `.ts` or `.tsx` work" come from poteto-help's row for this skill ("Apply TypeScript rules to `.ts` or `.tsx` work") and stay as open as the description's "reading or editing any .ts or .tsx file": they do not limit the rules to code the work writes or edits. |
| Each rule in the table under Controls holds for the TypeScript in the `.ts` or `.tsx` work, at the force and with the exceptions its Summary states. | The table under the H1 with the columns "Rule" and "Summary" and its 16 rows (Discriminated unions, Branded types, Constructive modeling, Simplest total type, `unknown` over `any`, Schemas before guards, No `as` casts, Narrowing hierarchy, Type guards, Exhaustiveness, `satisfies` over `as`, Boundary validation, Schema-derived types, Object args, Real tests, Structured telemetry). Each Summary is an instruction in upstream's words. "at the force and with the exceptions its Summary states" keeps each rule at its own force and with its own exception: the preferences ("Prefer the framework's real test primitives", "Prefer structured logger diagnostics", "Reach for ... before declaring a new interface"), the conditions ("Cast only after validation.", "Strengthen to `NonEmpty<T>` only where ...", "Mock only what you can't run locally."), and the exception "Skip on hot paths (per-frame render, tokenizers, parsers)." A preference does not become a required result. "holds for" is used instead of "follows" because one rule clause is a check on the code and not a property of it ("verify UI in a running build"). The Outcome is judged per row of the table: it stands for 16 separately assessable conditions, each identified by its Rule name. |

Also: 3 statements moved to the section their function calls for; 1 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/typescript-best-practices/references/patterns.md`

Unchanged from upstream.
