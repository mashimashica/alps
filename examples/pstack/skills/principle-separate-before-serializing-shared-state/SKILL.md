---
name: principle-separate-before-serializing-shared-state
description: "Apply when concurrent actors might write to the same file, branch, key, or state object. Eliminate the sharing first; serialize structurally only when one shared writer is a real invariant."
disable-model-invocation: true
---

# Separate Before Serializing Shared State

## Purpose

Eliminate the sharing between concurrent actors first, and serialize access structurally only where one shared write target is a real invariant.

## Outcomes

- Where one shared write target is not a real invariant, each concurrent actor writes its own file, key, branch, or state directory, and the state is merged only where it is read.
- Where one shared write target is a real invariant, access to it is serialized structurally, not by instructions.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. When concurrent actors might write the same file, branch, key, or object, first ask whether they need one shared object or are publishing independent facts.
2. Default to giving each actor its own file, key, branch, or state directory, and merge only where the state is read. Two workers writing their own field into one `state.json` is still shared mutation.
3. Only when one shared write target is a real invariant, serialize access structurally (a lockfile, a single writer, sequential phases, compare-and-swap). Instructions are not concurrency control, and "we need a lock" is a smell to check first.

## Constraints

This principle applies when concurrent actors might write to the same file, branch, key, or state object. When another description cites this principle, that description's own limits on it hold.

Task 1 comes first.
