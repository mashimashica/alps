---
name: principle-boundary-discipline
description: "Apply when wiring validation, error handling, or framework adapters. Concentrate guards at system boundaries (CLI, config, network, external APIs); trust internal types and keep business logic in pure functions."
disable-model-invocation: true
---

# Boundary Discipline

## Purpose

Keep guards at system boundaries and framework dependencies in a thin shell, so that the code inside trusts its types and business logic is pure.

## Outcomes

- Validation, type narrowing, error handling, and the parse of raw data into domain types sit where data crosses a system boundary (CLI args, config files, external APIs, network).
- Inside, the types are trusted, with no re-validation and no redundant nil check.
- No transport or framework type is in the public surface.
- Business logic lives in pure functions with no framework dependencies, and the shell that calls them is thin.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. Validate, narrow types, and handle errors where data crosses a system boundary (CLI args, config files, external APIs, network).
2. Inside, trust the types: no re-validation and no redundant nil checks.
3. Parse raw data into domain types at the boundary, and keep transport and framework types out of the public surface.

## Controls

Business logic lives in pure functions with no framework dependencies. The shell that calls them is thin.

Two tests. Is this data crossing a boundary right now? If not, the validation is redundant. Can this be a pure function the shell just calls? If yes, extract it.

## Constraints

This principle applies when wiring validation, error handling, or framework adapters. When another description cites this principle, that description's own limits on it hold.
