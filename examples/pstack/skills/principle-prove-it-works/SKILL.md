---
name: principle-prove-it-works
description: "Apply after completing a task, before declaring done. Verify against the real artifact (run the feature, read the actual value, inspect the diff), not a proxy, self-report, or 'it compiles.'"
disable-model-invocation: true
---

# Prove It Works

## Purpose

Prove that a completed task works before it is declared done, by evidence from the real artifact and not from a proxy.

## Outcomes

- Every output is verified by a direct check of the real thing, not by a proxy, before the task is declared done.
- Where the check can be scripted, it is scripted.
- The output of a scripted check is where the human can see it.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. Verify every output by checking the real thing directly: run the feature, read the actual value, inspect the diff. Proxies (file mtimes, self-reports, cached output, "it compiles") do not count.
2. When a check fails, suspect the observation method before the system.
3. Script the check when you can. A deterministic script that reruns the comparison beats a one-time look. Keep its output where the human can see it, and commit it only when the trail must be auditable later.

## Constraints

This principle applies after completing a task, before declaring done. When another description cites this principle, that description's own limits on it hold.
