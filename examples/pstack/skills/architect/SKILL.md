---
name: architect
description: "Sketch types, signatures, and module structure before code, then stay in the loop while implementation fills in. Use for /architect, 'architect this', 'design this', or non-trivial work where jumping to code would lock in the wrong shape."
disable-model-invocation: true
---

# Architect

## Purpose

Settle the shape of a change before code is written, so that jumping to code does not lock in the wrong shape.

## Outcomes

- Every system the change touches is traced before code is written.
- Two different shapes for the change (types, signatures, module boundaries) are sketched before code is written, or, for a large or contested design, the **arena** skill ran instead of sketching alone.
- Of the two sketched shapes, the picked one is the shape where each piece of state has one owner, each task has one way to do it, and callers need to know least.
- Where workarounds repeat, a redesign replaces patching.

## Tasks

The following Tasks are required whenever this skill runs, each with the conditions it states. Numbers identify the Tasks and set no order.

1. Before writing code, trace every system the change touches, then sketch two different shapes for it (types, signatures, module boundaries) and pick the one where each piece of state has one owner, each task has one way to do it, and callers need to know least.
2. Redesign instead of patching if workarounds repeat.
3. For a large or contested design, run the **arena** skill instead of sketching alone.
4. Stay in the loop while implementation fills in.

## Constraints

Step 4 comes after the sketch.
