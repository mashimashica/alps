---
name: sharpen
description: "Make a task deeper, not bigger, then rewrite the prompt. Use for /sharpen."
disable-model-invocation: true
---

# Sharpen

## Purpose

Give the user a rewritten prompt that asks for a deeper version of their task, not a bigger one.

## Outcomes

- The reply states each of the four things in steps 1 to 4.
- The rewritten prompt asks for exactly the deeper version of the task that steps 1 to 4 describe, not a bigger one.
- The rewritten prompt asks the agent to prototype any choice an experiment can settle and to recommend an option based on what it observed.
- Product or preference choices that no experiment can settle are left for the user to make.

## Tasks

The following Tasks are required whenever this skill runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. Say what a top professional in this field would do here that the user is not asking for.
2. Name the rawest material they would start from instead of what has already been digested for the user.
3. Name the specific methods and tools they would use.
4. Say what, other than you or the user, would show the result is right.
5. Rewrite the user's prompt to ask for exactly that. Have the rewritten prompt ask the agent to prototype any choice an experiment can settle and recommend an option based on what it observed. Leave product or preference choices that no experiment can settle for the user to make.

## Constraints

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Steps 1 to 4 are the four things to do before rewriting. They come before step 5.
