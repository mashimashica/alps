---
name: why
description: "Use for 'why does X work this way', 'why we picked Y', design rationale, regressions, postmortems, or data-backed thresholds. Returns a cited read on decisions and tradeoffs. Use how for runtime behavior."
disable-model-invocation: true
---

# Why

## Purpose

Answer why the target is the way it is, with a cited read on decisions and tradeoffs. Use how for runtime behavior.

## Outcomes

- The answer comes from the record, not the code.
- The answer cites what the authors wrote.
- The answer marks its own inferences as inferences.
- The answer says what the record does not answer.

## Tasks

The following Tasks are required whenever this skill runs, each with the conditions it states. Numbers identify the Tasks and set no order.

1. Answer from the record, not the code: read the commits and PR discussions that introduced the target and each later change, and other sources if the trail is thin.
