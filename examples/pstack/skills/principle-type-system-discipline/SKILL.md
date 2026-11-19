---
name: principle-type-system-discipline
description: "Apply when designing types, reviewing a function signature, or writing code in any statically-typed language. Make illegal states unrepresentable, brand semantic primitives, parse external data at boundaries, exhaust variants, derive from authoritative schemas."
disable-model-invocation: true
---

# Type System Discipline

## Purpose

Make the compiler reject impossible states, mismatched primitives, and unhandled variants.

## Outcomes

- The compiler rejects impossible states.
- Arguments that share a primitive type but mean different things each have their own type, so the compiler rejects a mismatch.
- External data is typed only by a parse function at the boundary that returns the typed model.
- The compiler rejects unhandled variants.
- Where a schema file owns a shape, the type is derived from it and no parallel type is hand-rolled.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. Make illegal states unrepresentable.
2. **Brand semantic primitives.** If two arguments share a primitive type but mean different things, give each its own type. Validate once at creation.
3. **External data is untyped until parsed.** JSON, RPC payloads, CLI args, config, environment variables, and database rows go through a parse function at the boundary that returns the typed model.
4. Exhaust variants.
5. **Derive types from authoritative schemas.** When a schema file owns a shape, derive the type from it instead of hand-rolling a parallel one.

## Constraints

This principle applies when designing types, reviewing a function signature, or writing code in any statically-typed language. When another description cites this principle, that description's own limits on it hold.

## Resources

For TypeScript syntax, see the **typescript-best-practices** skill.
