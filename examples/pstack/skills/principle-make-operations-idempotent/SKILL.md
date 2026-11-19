---
name: principle-make-operations-idempotent
description: "Apply when designing commands, lifecycle steps, or processing loops that run amid crashes, restarts, and retries. Converge to the same end state regardless of partial prior runs."
disable-model-invocation: true
---

# Make Operations Idempotent

## Purpose

Design every state-changing operation to converge to the correct state however many times it runs and wherever the previous run stopped.

## Outcomes

- Every state-changing operation converges to the correct state however many times it runs.
- Every state-changing operation converges to the correct state wherever the previous run stopped.
- Anything a run leaves behind is recognizable as stale by the next run, by evidence that holds wherever the previous run could have stopped.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. Derive each step from the state that exists, not from what the previous run meant to do. Read the current state, compare it to the goal, and apply only the difference.
2. Anything a run leaves behind (a lock, a temporary file, a half-written record, a claimed job) must be recognizable as stale by the next run, by evidence that holds wherever the previous run could have stopped. Write to a temporary path and rename it into place.

## Controls

The test: what happens if this runs twice? What if the previous run crashed at every possible point? If the answer depends on what was left behind, add a reconciliation step.

## Constraints

This principle applies when designing commands, lifecycle steps, or processing loops that run amid crashes, restarts, and retries. When another description cites this principle, that description's own limits on it hold.
