# Authoring or modifying a skill

## Purpose

Author or modify a skill in a voice that keeps only prose that changes a decision, and deliver it validated for review.

## Outcomes

- The skill's frontmatter has `name` and `description`, every file it references exists, and every cross-skill link resolves.
- The skill keeps only prose that changes a decision.
- The change is open as a PR per **Opening a PR**.

## Tasks

The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. Use the **create-skill** skill (Cursor's built-in for authoring SKILL.md files).
2. Validate the skill: frontmatter has `name` and `description`, referenced files exist, cross-skill links resolve.
3. Test cases if structural. Skip if subjective.
4. Run **Opening a PR**.

## Outputs

**Reply:** summary of the skill, key design decisions, validation notes.

## Controls

When in doubt, delete. Keep only prose that changes a decision. Tell it to do the thing and skip the reason. Explain only when the rule is confusing without one. Match tone to scope. Point at structural sources (types, READMEs, config) per the **encode-lessons-in-structure** principle skill. Delegate to other skills by path. Don't restate. A workflow you keep hitting but isn't captured → propose a new skill.

## Constraints

**You own the skill's voice.**

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Steps 2, 3, and 4 follow step 1, because they act on the skill that step 1 authors or modifies.
