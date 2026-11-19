---
name: principle-subtract-before-you-add
description: "Apply when sequencing an addition, refactor, or rewrite. Remove dead code, redundant validators, and stub references first, then build on the simpler base."
disable-model-invocation: true
---

# Subtract Before You Add

## Purpose

Make each addition, refactor, or rewrite build on a simpler base than it found.

## Outcomes

- Complexity is removed before construction, and construction builds on the simpler base.
- The design is left slightly simpler and more capable, behind the same or smaller surface, than it was found.
- The design serves observed usage, not speculative edge cases, with no speculative validator, parser, or guard beyond what the spec demands.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. When evolving a system, remove complexity first, then build. Default to subtraction. Remove dead code, redundant validators, and stub references first, then build on the simpler base.
2. Make simplification a continual investment. Leave the design slightly simpler and more capable behind the same or smaller surface than you found it.
3. Sequence removal before construction
4. Cut before you polish (get to the minimum before investing in quality)
5. Design for observed usage, not speculative edge cases
6. Simplify prompts (remove redundant instructions, excessive templates)
7. When a reference has no novel content, delete it rather than leaving a stub

## Constraints

This principle applies when sequencing an addition, refactor, or rewrite. When another description cites this principle, that description's own limits on it hold.

No speculative validators, parsers, or guards beyond what the spec demands.
