---
name: principle-foundational-thinking
description: "Apply before writing logic: choosing core types and data structures, sequencing scaffold-vs-feature work, asking what concurrent actors share. Get the data structures right so downstream code becomes obvious."
disable-model-invocation: true
---

# Foundational Thinking

## Purpose

Get the foundations right before writing logic so downstream code becomes obvious.

## Outcomes

- The chosen data structures match the dominant access paths before logic is written.
- Actors share state only where nothing happens if another actor modifies it concurrently. Any other state that actors would share is isolated.
- Whatever helps every later phase (CI, tests, shared types) is in place first, after dead code is removed.
- Commits are small and single-purpose.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. Get the data shape right before writing logic. Define core types early, trace every access pattern, and choose structures that match the dominant paths. DRY the structure, not every line. Get the data structures right so downstream code becomes obvious.
2. Before sharing state between actors, ask what happens if another actor modifies it concurrently. If the answer is not "nothing", isolate.
3. Scaffold first. Whatever helps every later phase (CI, tests, shared types) goes first, after removing dead code. Keep commits small and single-purpose.

## Constraints

This principle applies before writing logic: choosing core types and data structures, sequencing scaffold-vs-feature work, asking what concurrent actors share. When another description cites this principle, that description's own limits on it hold.
