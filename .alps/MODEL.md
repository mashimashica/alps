---
kind: process-reference-model
id: alps-reference
name: ALPS Reference Model
version: 0.4.0
status: active
binding: alps-markdown-agent-plugins/1.0
alps-requires: ">=0.4.0 <0.5.0"
authoritative-language: en
default: true
---

# ALPS Reference Model

## Purpose

This Process Reference Model defines the Processes and relationships used to define, apply, and manage reusable Agent Skills and identifies the Skill Packages that provide their authoritative Process Descriptions.

## Scope

The Model covers the life cycle of Agent Skills and Skill Packages under ALPS. It applies to need identification, Skill Description design and verification, Process selection and execution, multi-Process orchestration, adoption, Tailoring, assessment, improvement, and retirement.

The Model does not prescribe a fixed phase order. Its Processes may be applied concurrently, iteratively, or recursively.

## Included Processes

| Process ID | Process Name | Skill ID | Skill Source | Version or Resolution | Status | Role |
|---|---|---|---|---|---|---|
| alps-definition | ALPS Definition Process | define-alps | local:skills/define-alps | repository release 0.4.0 | adopted | Defines and verifies Skill Descriptions, Process Models, and Process Views for an identified need. |
| alps-application | ALPS Application Process | apply-alps | local:skills/apply-alps | repository release 0.4.0 | adopted | Selects Processes, resolves their Skills, executes Process Instances, and composes their handoffs. |
| alps-management | ALPS Management Process | manage-alps | local:skills/manage-alps | repository release 0.4.0 | adopted | Governs adoption, compatibility, Tailoring, assessment, change, release, and retirement. |

## Relationships

| Provider Process | Output | Recipient Process | Input | Conditions |
|---|---|---|---|---|
| alps-definition | Verified Skill Description, Process Model, or Process View and verification results | alps-management | Verified asset and adoption evidence | Used before adoption or after semantic redefinition. |
| alps-management | Managed Skills and Skill Packages, Process Models, Process Views, compatibility decisions, Tailoring decisions, and application conditions | alps-application | Managed assets and application conditions | Used when selecting or applying a Process. |
| alps-application | Execution and decision records, lessons learned, and measurable results | alps-management | Assessment and improvement Inputs | Used throughout operation and at review points. |
| alps-management | Change, redefinition, or reverification request | alps-definition | Identified change need and affected scope | Used when an asset requires semantic change or renewed verification. |

## Selection and Application

Use `apply-alps` when existing managed Processes are to be selected or executed through their Skills. Use `define-alps` when a need is unmet or a Process Description, Process Model, or Process View requires definition or semantic redefinition. Use `manage-alps` for adoption, compatibility decisions, Tailoring, assessment, change control, release management, or retirement.

Selection and timing are determined from the application context, target Outcomes, Controls, Constraints, risk, and managed Tailoring decisions. Table order does not impose execution order.

## Framework-Level Controls and Enablers

| Element | Classification | Scope | Exceptions | Tailoring |
|---|---|---|---|---|
| Process Framework | Control | All Process Descriptions, Process Models, Process Reference Models, and Process Views governed by ALPS | None | Its requirements are not tailorable by this Model. |
| ALPS Specification | Control | Agent Skills and their application under ALPS | Process Framework takes precedence on conflict. | Tailoring follows the ALPS Management Process. |
| `alps-markdown-agent-plugins/1.0` | Control | Repository Process Models and Process Views using this binding | Assets using another declared binding | Binding selection may change only through a managed compatibility decision. |
| Managed repository and resolver | Enabler | Discovery, resolution, and application of bound assets | Manual resolution may be declared | The Enabler may be replaced when equivalent identity and compatibility evidence is retained. |

## Process Views

No default Process View is required. A repeatedly used cross-cutting composition may be represented under `.alps/views/<view-id>/VIEW.md`.

## Compatibility

This Model requires ALPS `>=0.4.0 <0.5.0` and binding `alps-markdown-agent-plugins/1.0`. Every included Skill is local to this package and must resolve to an authoritative root `SKILL.md`.

## Known Gaps

This Model covers the Agent Skill life cycle rather than domain-specific work. Domain plugins may provide Process Models and Process Views that depend on the Processes represented here.

## Management

`manage-alps` governs adoption, versioning, compatibility, Tailoring, assessment, improvement, deprecation, and retirement of this Model. Changes to included Processes, Skill mappings, relationships, compatibility, or Framework-level declarations require mechanical preflight and semantic reverification. English is authoritative; the Japanese file is a localization.
