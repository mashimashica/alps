---
name: design-process-description
description: Create or revise the Process Description that makes recurring agent work a reusable Process Skill. Use to clarify its purpose, observable outcomes, boundary, or minimum necessary detail, including simplification based on evidence from use. Do not use to execute, package, publish, version, or govern the target Skill.
---

# Design a Process Description

## Purpose

Design or redesign the authoritative Process Description for a Process Skill with the minimum detail needed to make its meaning, success conditions, and reusable boundary clear.

## Outcomes

- The recurring work is described as one coherent Process boundary.
- Its Name, Purpose, and observable Outcomes show success without depending on a particular performer, tool, method, or sequence.
- Reusable Process knowledge is distinguished from information that belongs to one application.
- Only details needed for correctness, safety, meaning, composability, or assessment remain.
- When revising an existing Skill, the description reflects evidence from use as well as unresolved assumptions and limitations.

## Work

1. Confirm the recurring work, its subject, its intended use situations, and any available evidence from prior use.
2. Choose a clear Name, state one Purpose, and define observable Outcomes sufficient to satisfy that Purpose.
3. Separate enduring Process knowledge from case-specific goals, values, people, tools, files, repositories, and execution context.
4. Do not add a detail unless its necessity can be explained in terms of correctness, safety, meaning, composability, or assessment.
5. Add Activities, Tasks, Inputs, Outputs, conditions, or Handoffs only when the Process would otherwise be ambiguous or unusable.
6. Remove unnecessary performers, tools, methods, metrics, file paths, repository details, fixed sequences, and special-case branches.
7. Check the description against representative cases or evidence from use. Revise unclear, duplicated, ineffective, or burdensome content.
8. Present the created or revised Process Description together with unresolved questions, explicit assumptions, and known limitations. Do not fill gaps by guessing.

Creation and revision are the same responsibility: designing the best current Process Description. Do not introduce separate lifecycle procedures for them.

## Boundary

- Do not execute the target Process Skill to achieve its normal Outcomes.
- Do not select Skills as a standing intermediary or orchestrate multiple Skills.
- Do not manage Git, repositories, branches, commits, releases, versions, publication, status, adoption, or retirement.
- Do not make formal conformance, capability, maturity, or certification claims.
- Do not create representation models, package identities, resolvers, dedicated records, schemas, parsers, validators, CLIs, generators, or host semantics.
- Do not read every reference by default.
- Do not require a complete template when a smaller description is sufficient.

When the user wants the target Process Outcomes, apply the target Skill directly. Use this Skill only to create, revise, or simplify that Skill's Process Description.

## Read References Only When Needed

- Read [Purpose and outcomes](references/purpose-and-outcomes.md) when the Purpose combines multiple independent intents, an Outcome is written as an artifact or procedure, success cannot be assessed, or a neighboring Skill has an overlapping Purpose.
- Read [Boundary and detail](references/boundary-and-detail.md) when the Skill is too case-specific, holds multiple purposes, reads like a procedure, raises a split-or-merge decision, fixes a role, tool, or sequence without clear need, or evidence from use suggests content should be removed.
- Read [Inputs, outputs, and conditions](references/inputs-outputs-and-conditions.md) when an agent or tool is labeled as an Input, Outcomes and Outputs are mixed, rules, limits, and resources are unclear, start or completion conditions are ambiguous, or meaning is lost at a Handoff between Skills.

Read only the reference whose stated condition applies. Each reference is usable on its own.
