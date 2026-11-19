---
name: principle-test-behavior-not-implementation
description: "Apply when you write, change, or keep a test. Assert what the code's users can observe, so that the test fails when that behavior breaks and keeps passing when only the internals change."
disable-model-invocation: true
---

# Test Behavior, Not Implementation

## Purpose

Make each test a claim about what the code's users can observe, so that the test fails when that behavior breaks and keeps passing when only the internals change.

## Outcomes

- Each test written, changed, or kept fails when the behavior it claims breaks.
- Each test written, changed, or kept still passes when the internals change and every observable result stays the same.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. Judge each test against two imagined edits:

   - **Break the behavior** (a wrong value, a skipped or doubled effect). If the test still passes, it proves nothing. The usual causes are a loose assertion, an expected value computed by the code under test, and an assertion on data the test built itself.
   - **Change the internals** and keep every observable result. If the test fails, it is pinned to the implementation.

   Keep a test that catches the first edit and survives the second. Rewrite or delete the rest.
2. Drive the code through its public interface with a concrete input, and derive the expected value from the requirement.
3. Pair "this never happens" with a case where it does happen.
4. Assert the error type that callers branch on, not the message.

## Controls

A test is a claim about what users of the code can observe through its interface: return values, errors, state they can read back, and effects on outside systems. Private helpers, internal call order, and intermediate data are implementation.

What an external service receives is behavior. A call to an internal helper is not.

## Constraints

This principle applies when you write, change, or keep a test. When another description cites this principle, that description's own limits on it hold.
