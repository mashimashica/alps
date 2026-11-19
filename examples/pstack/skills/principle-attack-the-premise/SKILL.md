---
name: principle-attack-the-premise
description: "Apply when two or more fixes that share one premise have failed the same gate. Write the premise down and test it directly before you write another fix that assumes it."
disable-model-invocation: true
---

# Attack the Premise

## Purpose

Ground the next fix in evidence about the premise that the failed fixes share.

## Outcomes

- The premise is written down, as the one sentence every failed fix assumed, before the next fix starts.
- The premise is tested before the next fix starts, by an observation that would come out differently if the premise were false.
- Where the evidence contradicts the premise and one part always lands on the losing side, the change is to what puts it there, not a mechanism that cleans up after it.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. When two or more fixes that share one premise have failed the same gate, suspect the premise, not the fixes.
2. Write the premise down: the one sentence every failed fix assumed.
3. Test it before the next fix. Find an observation that would come out differently if the premise were false, and make it. Look at how the failures are distributed, not only at how large they are.
4. If the evidence contradicts the premise, look for what the failures share that it did not predict. If one part always lands on the losing side, change what puts it there instead of adding a mechanism that cleans up after it.

## Constraints

This principle applies when two or more fixes that share one premise have failed the same gate. When another description cites this principle, that description's own limits on it hold.

Do not start the next fix before the premise is written down and tested.
