---
name: correct
description: "Find the mistakes agents keep repeating in this repo and make each one impossible. Try architecture first, then types, then a lint whose error names the fix, then a test, and write docs last. Prove each check fails on a real past mistake. Repeat this each time the operator corrects you. Use for /correct."
disable-model-invocation: true
---

# Correct

## Purpose

Change this repo so the next agent can't make the same mistakes the operator keeps correcting agents for.

## Outcomes

- Each mistake class has evidence that it happened at least twice.
- Each fix is at the highest level that works for its class.
- The most frequent classes are fixed, one commit each.
- Each new check is shown to fail on a real past mistake.
- The same command runs locally and in CI.
- A table in the agent instruction file pairs each rule with what enforces it.
- The reply gives each class with its evidence, the level picked, and why a higher level didn't work.

## Activities & Tasks

The following Tasks are required whenever this skill runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

### Find the mistake classes

1. First, read recent commits, reverts, review comments, agent instruction files, and comments that explain workarounds.
2. Group the mistakes into classes. A class counts once it has happened twice.

### Fix each class at the highest level that works

1. **Eliminate it with architecture.** Give each piece of state one owner and each task one supported way. Hide internals so the wrong import fails. Replace hand-synced lists with one source of truth. Delete old ways and dead code an agent would copy.
2. **Enforce it with types so the bad state can't be written.** If bad code still compiles, add a lint or CI check whose error names the file, type, or function to use instead. If the pattern is already common, fail only when a change adds more.
3. **Test the behavior.** Fix or delete any test that still passes when the behavior it checks breaks, or that fails when only the internals change.
4. **Write docs or agent rules last, only for judgment calls.** Nothing fails when an agent skips them.

### Fix and prove

1. Then fix the most frequent classes now, one commit each.
2. Prove each new check fails on a real past mistake.
3. Run the same command locally and in CI.

### Keep the rule table

1. Last, keep a table in the agent instruction file that pairs each rule with what enforces it.
2. When the operator corrects you, fix the mistake and add the rule. If the rule was already there and nothing enforces it, that's a repeat, so fix it at the highest level in the same change.
3. Drop a rule once its mistake can't happen.

## Outputs

**Reply:** each class with its evidence, the level you picked, and why a higher level didn't work.

## Controls

Assume every contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Design the repo so a change that looks right from one file is right for the whole repo.

## Constraints

Repeat this work each time the operator corrects you.

Exceptions go on the offending line with a reason, an expiry date, and a human's approval.

Unless a Task states otherwise, work the Activities in the order listed. Within an Activity, Tasks may be worked in any order unless one states otherwise. These dependencies are required.

- "Find the mistake classes" comes first, "Fix and prove" comes after it, and "Keep the rule table" comes last.
- Each class is fixed at the highest level that works. The steps under "Fix each class at the highest level that works" are the levels, highest first. Try architecture first, then types, then a lint whose error names the fix, then a test, and write docs last.
- In "Fix and prove", step 2 comes after step 1, because it proves the new checks that the fixes of step 1 add.
