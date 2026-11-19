---
name: principle-build-the-lever
description: "Apply to any non-trivial work, not just bulk work: edits, migrations, analyses, checks. Build the tool that does it or proves it (codemod, script, generator, or a skill your subagents follow) instead of working by hand. The tool is the artifact a reviewer can rerun."
disable-model-invocation: true
---

# Build the Lever

## Purpose

Have work that isn't trivial done or proven by a tool instead of by hand. The tool is the artifact a reviewer can rerun.

## Outcomes

- Work that isn't trivial is done or proven by a tool in the diff, not by hand.
- The tool is safe to rerun, and a rerun on the first unit, which was done by hand, proves it.
- The tool is the smallest script that does or proves the job, not a framework.
- Where the work fans out, the recipe, the verification contract, and the fences are one skill that the delegates read and cannot edit.
- Where the work outlives the session, the tool is committed.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. When the work isn't trivial, build the tool that does it (a codemod, script, generator, or rerunnable check) instead of doing it by hand. The bar is triviality, not repetition. Skip the tool only for a couple of obvious edits.
2. Do the first unit by hand, then build the tool and prove it by rerunning it on that unit. Make it safe to rerun.
3. When you do fan out, write the recipe, the verification contract, and the fences as one skill the delegates read and cannot edit.
4. Build the smallest script that does or proves the job, never a framework.

## Outputs

Applying this produces a file. No script, codemod, generator, or delegate skill in the diff means you didn't apply it. Commit it when the work outlives the session.

## Controls

A deterministic tool beats fan-out.

## Constraints

This principle applies to any non-trivial work, not just bulk work: edits, migrations, analyses, checks. When another description cites this principle, that description's own limits on it hold.
