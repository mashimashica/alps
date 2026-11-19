---
name: principle-sequence-verifiable-units
description: "Apply to multi-step work (sweeps, migrations, runs of similar edits) and to how you stack commits and PRs. Break work into small units that each end in a verifiable state, check each before the next, and order delivery so the sequence proves itself to a reviewer."
disable-model-invocation: true
---

# Sequence work into verifiable units

## Purpose

Make multi-step work a sequence of small units that each end in a verifiable state, so that the work is checked as it advances and the delivered sequence proves itself to a reviewer.

## Outcomes

- Each small unit of the work ends in a state that is checked green before the next unit begins.
- The work is delivered in the order that proves it to a reviewer.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. Order work as small units that each end in a state you can check, and do not advance until the current one is green.
2. In a sweep, migration, or run of similar edits, each unit is a bracket: known-good state, one change, run the check, proceed. Run the per-unit check even when a tool does the edits.
3. Deliver in the order that proves the work: the failing test first, then the fix. The subtraction before the reshape. The baseline before the treatment. Each commit lands on its own.

## Constraints

This principle applies to multi-step work (sweeps, migrations, runs of similar edits) and to how you stack commits and PRs. When another description cites this principle, that description's own limits on it hold.
