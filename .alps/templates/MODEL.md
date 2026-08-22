---
kind: process-model
id: example-model
name: Example Process Model
version: 0.1.0
status: draft
binding: alps-markdown-agent-plugins/1.0
alps-requires: ">=0.4.0 <0.5.0"
authoritative-language: en
default: false
---

# Example Process Model

## Purpose

State why this set of Processes and relationships exists for the intended domain.

## Scope

Describe the subjects, application contexts, exclusions, and intended users of the Model.

## Included Processes

| Process ID | Process Name | Skill ID | Skill Source | Version or Resolution | Status | Role |
|---|---|---|---|---|---|---|
| example-process | Example Process | example-skill | local:skills/example-skill | repository release | adopted | State the Process contribution without copying its Purpose or Outcomes. |

## Relationships

| Provider Process | Output | Recipient Process | Input | Conditions |
|---|---|---|---|---|
| example-process | Example Output | another-process | Example Input | Representative handoff; no sequence implied. |

## Selection and Application

Select Processes from the application context, target Outcomes, Controls, Constraints, risk, and managed Tailoring decisions. Resolve the Skills that provide their authoritative Process Descriptions. The order in this file does not prescribe execution order.

## Framework-Level Controls and Enablers

| Element | Classification | Scope | Exceptions | Tailoring |
|---|---|---|---|---|
| Example policy or shared capability | Control or Enabler | Declare affected Processes or Model scope. | Declare exceptions or `none`. | State whether Tailoring is permitted. |

## Process Views

| View ID | Source | Concern |
|---|---|---|
| example-view | .alps/views/example-view/VIEW.md | State the cross-cutting concern. |

## Compatibility

State the supported ALPS version range, binding identifier, external plugin prerequisites, and unresolved-source policy.

## Known Gaps

Record omitted or candidate Processes and the evidence needed to reconsider them.

## Management

State ownership, adoption status, change control, localization, reverification, deprecation, and retirement conditions.
