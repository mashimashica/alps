---
name: create-formal-verification-skill
description: "Generate a project-local skill that formally verifies the code where a bug costs the most and tests reach the least, in any language, with whichever verification tool fits. Use for /create-formal-verification-skill, \"model-check this race\", \"prove this invariant\", or when concurrency, retries, state machines, parsers, or unsafe code need more than tests."
disable-model-invocation: true
---

# Create a formal verification skill

## Purpose

Verify one property of the part of the repo where formal verification matters most, and leave a project-local skill that lets the next agent check a change against that property. A test checks the cases that someone thought to write. Formal verification checks every case in a stated scope: every order of steps in a model, every input up to a bound, or every input.

## Outcomes

- The target is a promise the code makes, where a break harms users and tests rarely reach the case that breaks it, chosen for its strength and not for ease of verification.
- The check of the chosen property passes within its stated bounds and assumptions, or fails only on findings that are reported with the counterexample in the code's terms.
- Each property has been seen to fail on a broken variant of the code it guards.
- The generated skill, followed as the next agent would on a scratch change that breaks the property in the real code, runs every step and catches the break.
- The user can trust the result and act on it without learning the verification language.

## Activities & Tasks

The following Tasks are required whenever this skill runs, each with the conditions it states. Numbers identify the Tasks and set no order.

### Choose the target from the code

1. Answer from the codebase, and ask the user only what you cannot observe. If the user named an area or a bug, start there.
2. Choose the strongest good target in the repo, not the one that is easiest to verify. A good target is a promise the code makes, where a break harms users and tests rarely reach the case that breaks it.

### Let the question choose the tool

1. Pick the tool that answers the question at the lowest cost: a model checker, a proof assistant, an SMT-backed verifier, or another tool. Whether events can happen in a bad order usually suits a model checker over a small model of the design, and TLA+ is the default for that in any language. Whether the code itself behaves for every input, as with memory safety, overflow, or a data-structure invariant, usually suits a verifier that runs on the code. If no verifier runs on this language, say so, and test the real code with generated inputs, not a hand model of the function. A property that must hold at every size, where a bound is not enough, can need a proof. Prefer a tool that the repo's developers can install and run, and tell the user why you chose it.

### Verify one property

1. Verify one property of the target.

### Generate the verify skill

1. Write a project-local skill with frontmatter that names the area and says when to use it. Without frontmatter, the skill never registers. Write that skill for an agent who reads it cold, mid-change, and has never seen your work. From the skill alone, the next agent must be able to tell whether a change touches the verified code, run the check, tell a real bug from a modeling error, and update the verification when a change is intended. Put the coverage record and the sync commit in the skill, and tell the next agent to move the sync commit forward only after it confirms that the verification describes the code at the new commit. Use this repo's real commands, paths, and nouns, and leave no placeholders.
2. If the check is a TLA+ model, tell the next agent to read every result with the pstack [`/statechart`](../statechart/SKILL.md) skill. It shows each invariant violation the checker finds as its shortest path in plain words. When the check passes, `/statechart` draws a chart of how the system moves between states. Refer to `/statechart` by name. Its commands, options, and file paths change between releases and machines, so copy none of them into the generated skill or its scripts.

### Prove it before you hand off

1. Follow the generated skill once, as the next agent would, on a scratch change that breaks the property in the real code. It must catch the break. Then drop the scratch change and confirm that the check is back where it started: passing, or failing only on the findings you will report. A verify skill that was never run is a draft. If the skill misses the break or a step does not run, fix the skill or the verification, not the scratch change.

## Outputs

### Hand off

Tell the user what you verified, which tool you used and why, the bounds, what the check found in plain words, how to run it, and what it does not cover. Suggest a second target only if you found a close one. Point the user at `/maintain-formal-verification-skill` for bringing the verification back in line after changes that did not recheck it.

## Controls

### What makes it good

- **True to the code.** Every part of the model or proof points to code that a reviewer can open. What the verification treats as one indivisible step is one indivisible step in the code. Names come from this repo.
- **Able to fail.** A check that you have never seen fail proves nothing. Show each property failing on a broken variant of the code it guards, such as a removed check or a reordered step.
- **Findings stay findings.** When the current code breaks the property, report it with the counterexample in the code's terms. Do not weaken the property or the model until it passes, and do not change product code unless the user asks.
- **Honest about scope.** Say what is verified, under which bounds and assumptions, and what is left out. A pass covers the model or the bound, not the whole system.
- **Readable without the tool.** State the property and the harm in one plain sentence each. Tell a counterexample as a short sequence of steps in the code's words.
- **Cheap to rerun.** One command, a reproducible tool version, and a run short enough that the next agent will use it on every relevant change.
- **Kept in step with the code.** Record which files and functions each check covers, and the commit at which you last confirmed that the verification describes them. When the covered code changes after that commit, the next agent can see that the verification needs another look.

## Constraints

These dependencies are required.

- The target is chosen before the tool is picked, because the question that the tool answers comes from the target.
- The tool is picked before the property is verified with it.
- The property is verified before the verify skill is generated, because the skill holds the coverage record and the sync commit.
- The verify skill is generated before it is followed on the scratch change.
- The verify skill is followed on the scratch change before the hand off.
