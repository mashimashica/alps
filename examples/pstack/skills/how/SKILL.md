---
name: how
description: "Use for \"how does X work\", code walkthroughs before changing something, and placement / ownership / layering questions (\"where should this live\", \"which package owns this\", \"is this the right layer\"). Explains subsystem architecture, runtime flow, onboarding mental models. Use why for motivation."
disable-model-invocation: true
---

# How

## Purpose

Answer "how does X work?" questions from an exploration of the codebase, with an explanation that gives a solid mental model of the area. Use why for motivation.

## Outcomes

- The user's question is answered with an architectural explanation that comes from exploring the codebase.
- The explanation is one that a senior engineer unfamiliar with the area could read and walk away with a solid mental model.
- Where the scope is ambiguous, the interpretation that was explored is stated.
- What is presented is the subagent's output, with no more than light edits for clarity or context from the conversation.

## Tasks

The following Tasks are required whenever this skill runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

### 1. Explain

Spawn one Task subagent with `subagent_type: generalPurpose` and `readonly: true` that explores and explains in one pass. Give it the user's question and this brief:

> You are writing an architectural explanation for a senior engineer. Explore the codebase and write an explanation that a senior engineer unfamiliar with this area could read and walk away with a solid mental model. They should understand the architecture well enough to start working in it confidently. You have read-only access to the codebase.

### 2. Present

Present the subagent's output. Light edits for clarity or context from the conversation are fine. Do not substantially rewrite it.

## Inputs

If the scope is ambiguous, state your interpretation and explore. The user can redirect.

## Constraints

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Step 2 presents the output of the subagent that step 1 spawns.
