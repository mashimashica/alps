---
name: principle-never-block-on-the-human
description: "Apply when tempted to ask 'should I do X?' on reversible work."
disable-model-invocation: true
---

# Never Block on the Human

## Purpose

Keep agents unblocked on reversible work and the system self-healing, with the human supervising asynchronously and course-correcting after the fact.

## Outcomes

- Reversible actions proceed without blocking on the human.
- The result of the work is shown to the human with the reason for what was done.
- Each problem noticed is logged and fixed in the next round.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. Make reasonable decisions, proceed, and let the human course-correct after the fact. Since code changes are reversible and reviewable, a wrong decision usually costs less than blocking.
2. Proceed, then present. Do the work, show the result. Don't ask "should I do X?" Do X, explain why.
3. Make the system self-healing. When you notice a problem, log it and fix it in the next round.

## Constraints

This principle applies when tempted to ask "should I do X?" on reversible work. When another description cites this principle, that description's own limits on it hold.

The human supervises asynchronously. Agents must stay unblocked.

- Irreversible actions (force-push, delete production data, send external messages) still require confirmation.
- Reversible actions (write code, edit notes, split tasks) should proceed without blocking.
- Product direction comes from the human. Execution should not block.
