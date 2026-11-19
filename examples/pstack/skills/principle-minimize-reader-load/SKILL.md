---
name: principle-minimize-reader-load
description: "Apply when reviewing or shaping code that's hard to trace. Count layers between question and answer, and hidden state in the reader's head; collapse one-caller wrappers and shrink mutable scope."
disable-model-invocation: true
---

# Minimize Reader Load

## Purpose

Minimize reader load. Reader load is the work a reader must do to understand code. It has two independent axes: layers to trace between the question and the answer, and hidden or mutable state to hold in their head.

## Outcomes

- A new reader can answer "where does X come from?" and "what can change X?" in under 30 seconds.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. Guard both axes. Count layers between question and answer, and hidden state in the reader's head.
2. Collapse layers that only forward: wrappers with one caller, adapters with no second implementation, pass-through methods. Inline them.
3. Shrink state scope: returns over mutations, locals over fields, fields over module state, module state over globals. Derive instead of sync.
4. Name an invariant once at the boundary, not in every consumer.

## Controls

The test: can a new reader answer "where does X come from?" and "what can change X?" in under 30 seconds? If not, cut layers or cut state.

## Constraints

This principle applies when reviewing or shaping code that's hard to trace. When another description cites this principle, that description's own limits on it hold.
