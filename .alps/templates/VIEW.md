---
kind: process-view
id: example-view
name: Example Process View
version: 0.1.0
status: draft
binding: alps-markdown-agent-plugins/1.0
alps-requires: ">=0.4.0 <0.5.0"
authoritative-language: en
source-models: example-model
---

# Example Process View

## Purpose

State the cross-cutting Purpose or concern made visible by this Process View.

## Outcomes

- a) State one positive, observable result condition.
- b) State another result needed to satisfy the Purpose.

## Stakeholders and Concerns

| Stakeholder | Concern |
|---|---|
| Example stakeholder | State the matter of interest addressed by this Process View. |

## Source Models

| Model ID | Source | Version or Resolution |
|---|---|---|
| example-model | .alps/models/example-model/MODEL.md | compatible installed or repository version |

## Included Activities and Tasks

| View Element ID | Origin | Source Process | Source Element | Treatment | Guidance |
|---|---|---|---|---|---|
| view-01 | source-model | example-process | Activity: Example Activity | selected | Retain the source element and its normative meaning. |
| view-02 | source-model | example-process | Task: Example Task | adapted | Explain the adaptation; it does not change the source Process Description. |
| view-03 | view | — | View-specific coordination | new | Explain the Process View-only element and its application conditions. |

## Handoffs

| Provider Process | Output | Recipient Process | Input | Conditions |
|---|---|---|---|---|
| example-process | Example Output | another-process | Example Input | Identify whether selected from the Model or specific to this Process View. |

## Application Guidance

Explain how to select, combine, and assess the included elements without treating their display order as execution order.

## Compatibility and Conformance

State the supported ALPS and binding versions. Explain how selected, adapted, and new elements affect Conformance to the source Processes.
