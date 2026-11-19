---
name: principle-guard-the-context-window
description: "Apply when context is filling up: large outputs, long files, repeated reads, fan-out planning. Route bulk to subagents; keep summaries in the main thread, not raw payloads."
disable-model-invocation: true
---

# Guard the Context Window

## Purpose

Keep bulk and oversized phases from overflowing the context window.

> NOTE Context overflow degrades reasoning quality, creates compression artifacts, and halts progress.

## Outcomes

- The main thread holds summaries of the bulk, not raw payloads.
- Phases are sized and scope is capped, with files per phase limited, turn budgets set, and mechanism costs accounted for.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. Route bulk to subagents; keep summaries in the main thread, not raw payloads.
2. **Size phases and cap scope.** Limit files per phase, set turn budgets, account for mechanism costs.

## Constraints

This principle applies when context is filling up: large outputs, long files, repeated reads, fan-out planning. When another description cites this principle, that description's own limits on it hold.
