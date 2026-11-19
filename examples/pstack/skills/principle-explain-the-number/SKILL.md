---
name: principle-explain-the-number
description: "Apply before you measure, and before you trust, report, or act on a number you measured: a speedup, a regression, a throughput, a latency, or an eval result. Find what limits it, and rule out that it measured something other than the work you think."
disable-model-invocation: true
---

# Explain the Number

## Purpose

Establish what limits a measured number, and that it measured the work you think and nothing else, before the number is trusted, reported, or acted on for the decision it was measured for.

## Outcomes

- The decision is written before the run, with the result that would change it and the noise floor named.
- Where the run-to-run spread is not larger than the effect, the limiter named for the number is the resource or code path that bounds the result, taken from a profile or counters during a run.
- Where the run-to-run spread is not larger than the effect, each other thing the number could be measuring is ruled out with evidence.
- Where the run-to-run spread is not larger than the effect, the run count, the spread, and the limiter are kept with the number.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. **Write the decision before you run.** Name the result that would change it, and the noise floor. Stop when the run-to-run spread is larger than the effect.
2. **Ask "why not double?"** Name the resource or code path that bounds the result, from a profile or counters taken during a run. A guess from reading the code is not a limiter.
3. **List what else the number could be measuring** (errors, skipped or cached work, code that never ran, an untuned side, noise, a piece too small to matter) and rule out each one with evidence.
4. **Keep the run count, the spread, and the limiter with the number.**
5. For a performance number, run the [benchmark-checklist](../benchmark-checklist/SKILL.md) skill.
6. For an eval result, ask whether every run did the task, whether the gap holds across trials and models, and whether the scenario matters.

## Constraints

This principle applies before you measure, and before you trust, report, or act on a number you measured: a speedup, a regression, a throughput, a latency, or an eval result. When another description cites this principle, that description's own limits on it hold.
