---
name: principle-fix-root-causes
description: "Apply when debugging. Trace each symptom back to the first place the system went wrong and fix it there. A guard is a fix only when the state it handles is legitimate."
disable-model-invocation: true
---

# Fix Root Causes

## Purpose

Fix the fault, not the place where it surfaced. The root cause is the first place the system did something it should not do, or failed to handle a state it should handle.

## Outcomes

- The fix is at the root cause, not at the place where the fault surfaced.
- A guard is a fix only where the state it handles is legitimate.
- The fix covers every place with the same fault.
- Where the deciding fact took a deep dig, the cheap, always-on signal that would have shown it at first look is proposed.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. Reproduce first. Ask "why" until the answer is a wrong decision in the code. When stuck, instrument and read the actual state.
2. Ask whether the state that triggered the symptom is legitimate. If it is, handle it where the code broke. If it should never exist, a check there hides the bug, so find what produced it.

   > NOTE Guards, retries, swallowed errors, clamped values, and discarded state are the usual ways to hide a bug.

3. Fix the pattern, not the instance. Find every place with the same fault.
4. If the deciding fact took a deep dig, propose the cheap, always-on signal that would have shown it at first look.

## Constraints

This principle applies when debugging. When another description cites this principle, that description's own limits on it hold.

Tasks may be worked in any order unless one states otherwise. These dependencies are required.

- Reproduction comes first.
