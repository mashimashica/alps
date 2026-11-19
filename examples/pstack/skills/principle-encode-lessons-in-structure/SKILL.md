---
name: principle-encode-lessons-in-structure
description: "Apply when you catch yourself writing the same instruction a second time, or notice a recurring correction. Encode the rule as a lint, metadata flag, runtime check, or script instead of more text."
disable-model-invocation: true
---

# Encode Lessons in Structure

## Purpose

Carry a lesson that keeps recurring in structure wherever it can be encoded, not in one more repetition of the instruction.

## Outcomes

- Where the rule can be encoded, a lint, metadata flag, runtime check, or script carries it instead of more text.
- Where the lesson needs judgment and cannot be encoded, its instruction is more prominent and has an example of the failure mode.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. Encode the rule as a lint, metadata flag, runtime check, or script instead of more text.
2. If the lesson needs judgment and cannot be encoded, make the instruction more prominent and add an example of the failure mode.

## Constraints

This principle applies when you catch yourself writing the same instruction a second time, or notice a recurring correction. When another description cites this principle, that description's own limits on it hold.

**Corollary:** If the fix is structural, only use the structural fix. The instruction is the symptom.
