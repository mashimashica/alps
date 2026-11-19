---
name: principle-laziness-protocol
description: "Apply when refactoring, evaluating diff size, or tempted to add abstractions, layers, or signal threading. Bias toward deletion and the smallest change that solves the problem."
disable-model-invocation: true
---

# Laziness Protocol

## Purpose

Solve the problem without building more than it needs.

## Outcomes

- The same choice is not repeated in several places. It sits behind one source of truth, and its result is passed as a simple flag.
- The change is the smallest that solves the problem.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. **Consolidate decisions.** Do not repeat the same choice in several places. Put it behind one source of truth and pass the result as a simple flag.
2. **Minimize the diff.** Make the smallest change that solves the problem. Fewer lines beat "elegant" boilerplate.

## Controls

Bias toward deletion and the smallest change that solves the problem.

## Constraints

This principle applies when refactoring, evaluating diff size, or tempted to add abstractions, layers, or signal threading. When another description cites this principle, that description's own limits on it hold.
