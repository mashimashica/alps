---
name: create-process-models
description: Create an ALPS process model as one self-contained Agent Plugin. Use when organizing related work into Processes and shared input/output definitions, or turning supplied Process Descriptions into a model package. Includes model design, canonical files, and verification within the request.
---

# Process Model Creation

## Purpose

Establish a usable model of related work whose Process responsibilities, success conditions, and shared information can be understood and maintained through one Plugin's source documents.

## Outcomes

- The selected Processes' coverage and boundaries are justified against the intended work and applicable conditions.
- Each Process has a coherent source description with observable success conditions.
- Shared information and artifact relationships have unambiguous definitions and references.
- The model is usable as a self-contained Plugin in the requested distribution.
- Assumptions, unresolved matters, and the limits of verification are explicit.

## Activities & Tasks

The following Tasks are required within the requested scope. Revisit earlier decisions when relationships or evidence expose gaps.

### Framing the model

1. Identify the model's purpose, applicable context, intended users, available source descriptions, and requested destination. Distinguish creating the model from performing the work it describes. Resolve material gaps from available sources; ask the requester where a gap would change scope or success conditions and cannot otherwise be resolved.
2. Select Process boundaries by coherent responsibilities and intended results. Use enough Processes to cover the requested work without inventing phases, creating a Process for every tool call, or splitting work only because its performer changes. Identify what is outside the model and why.
3. For each Process, establish a Name, Purpose, and one or more observable Outcomes. Each Outcome must be necessary for that Purpose, and together they must be sufficient within the stated scope. An Output's existence alone is not a success condition. Add Activities, Tasks, Controls, Constraints, Enablers, or Entry/Exit Criteria only where they affect understanding, application, or evaluation. Preserve applicable obligations and their sources.

### Defining relationships

1. Identify information items, products, and services used or produced by each Process. Use one shared definition when occurrences have the same meaning; similar names do not establish identity. State necessary scope, properties, conditions of use, and effects of changes in the definition or the affected Process.
2. Declare source material examined or transformed as inputs and what the work produces or updates as outputs. Describe governing criteria and policies as Controls, and execution limits as Constraints, preserving their sources and scope. Identify each role where the same resource serves more than one. A type may be both an input and an output. Distinguish type definitions from concrete files or instances.
3. Trace each handoff through the shared type identifier. Account for externally supplied inputs and externally consumed outputs. Preserve justified cycles and repeated use of shared information. I/O relationships and document order do not grant authority, establish readiness, or prescribe an execution sequence; necessary approvals and order must be explicit conditions of the work.

### Creating the Plugin

1. Read the [model format](references/model-format.md) and create one Plugin for one model. Use the declared sources and identifier rules; do not introduce a second model file, type registry, or I/O list.
2. Put work intended to be available as an Agent Skill in `skills/<name>/SKILL.md`. Use ordinary process Markdown for other work, including human work; do not invent an executable Skill merely to draw a node. List model members explicitly in `plugin.json`; helper Skills are not automatically model members.
3. Keep shared definitions under `references/artifacts/`. Include supporting references, scripts, or schemas only when the described work needs them. Keep reusable meaning in the Plugin and bind concrete artifact paths or execution settings in workspace configuration only when requested.
4. Preserve supplied source text that is not being changed. For an existing package, keep stable identifiers, inspect references before changing them, and make intended changes and their effects explicit. Migrate an old format explicitly when requested; do not retain compatibility readers or duplicate authorities.

### Verifying the model

1. Inspect the package as distributed: manifest membership, Skill frontmatter, process descriptions, string-encoded I/O arrays, shared definitions, identifier uniqueness, relative links, and resolved package boundaries. Every I/O reference must resolve to a definition; report a missing definition instead of inventing its meaning.
2. Review coverage and boundary choices against the original work. Trace representative input/output relationships, including any cycle or external input present. Review shared Controls and their applicability in the source descriptions. Check whether all stated Outcomes could hold while a Process's Purpose remains unmet, and whether an Output could exist while an Outcome remains unconfirmed.
3. When an applicable loader or validator is available, load the package and check that it preserves the intended members and relationships. Identify the tool and version used. Keep format validation, semantic review, and actual execution evidence distinct; a rendered graph does not demonstrate that the modeled work succeeds.
4. Deliver the package location, its scope and sources, verification evidence, and unresolved matters. Identify affected judgments that need revalidation after a source or shared definition changes.

## Inputs

The intended work, its context, and available source descriptions are examined to construct the model.

## Controls

Applicable requirements govern the model's meaning and scope. The [model format](references/model-format.md) governs its canonical representation. This Skill contains the guidance needed for model creation and does not require another installed Skill.

## Constraints

Changes must remain within the requested scope and authority. Creating a model does not authorize executing its Processes, installing it into a host, or publishing it. Unconfirmed information or an unread required source must limit dependent decisions and claims; independent work may continue within its applicable conditions. Preserve useful partial work and identify unmet Outcomes rather than presenting an incomplete model as complete. Keep execution choices open except where applicable requirements constrain them.

## Resources

This file is the English source for the [Japanese translation](references/locales/ja/SKILL.ja.md).
