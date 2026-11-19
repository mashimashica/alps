---
name: principle-redesign-from-first-principles
description: "Apply when integrating a new requirement into an existing design."
disable-model-invocation: true
---

# Redesign From First Principles

## Purpose

Preserve option value when integrating changes into an existing design.

## Outcomes

- The design after the change is the one that would be built from scratch with the new requirement, not the existing design with the change bolted on.
- Every reference reflects the change: types, docs, examples, rationale sections.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. Redesign as if the requirement had been a foundational assumption from the start.
2. Read all affected files and understand the current design
3. Ask: "if we were writing this from scratch with this new requirement, what would we build?"
4. Propagate the change through every reference: types, docs, examples, rationale sections
5. Think about the whole redesign, then deliver it incrementally

## Constraints

This principle applies when integrating a new requirement into an existing design. When another description cites this principle, that description's own limits on it hold.

When integrating a change, don't bolt it onto the existing design.
