---
name: principle-model-the-domain
description: "Apply when writing stateful logic, or when code branches a lot or repeats a shape assumption across files."
disable-model-invocation: true
---

# Model the Domain

## Purpose

Have data structures, not scattered conditionals, carry the domain, without forcing a structure onto boring code.

## Outcomes

- Except where the shape is clear, local, and unlikely to grow, the domain is encoded in a data structure that removes branches or invalid states, not scattered across conditionals.
- Boring code is kept where its shape is clear, local, and unlikely to grow.
- No feature in the work grows an if/else chain by one more branch.
- The work adds no second boolean that must stay in sync with the first.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. Encode the domain in a data structure instead of scattering it across conditionals. The right structure makes invalid states unrepresentable and deletes branches.
2. Reach for a state machine instead of scattered booleans or phase checks, a typed model instead of loose parameters, a map, registry, or discriminated union instead of branching spread across files, a reducer instead of ad hoc mutations, and an index, queue, or normalized collection where the access pattern calls for it.

## Controls

The sign that you skipped this: a feature that grows an if/else chain by one more branch, or a second boolean that must stay in sync with the first.

## Constraints

This principle applies when writing stateful logic, or when code branches a lot or repeats a shape assumption across files. When another description cites this principle, that description's own limits on it hold.

Do not force it. Keep boring code when the shape is clear, local, and unlikely to grow, and distrust an abstraction that adds indirection without removing branches or invalid states.
