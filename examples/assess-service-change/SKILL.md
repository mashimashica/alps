---
name: assess-service-change
description: Assess whether a service change meets the criteria for a specified pilot using baseline and candidate request measurements. Use when measurement comparability, responsiveness, reliability, and the limits of a pilot decision need to be established.
---

# Service Change Assessment

## Purpose

Support a justified decision about a service change's suitability for the specified pilot conditions.

## Outcomes

- A judgment against each applicable pilot criterion is supported by comparable measurements and traceable calculations.
- The scope and limits of the judgment, including their effects on the pilot decision, are explicit.

## Activities

The following Tasks are required for this assessment. Their dependencies follow the evidence needed for each judgment.

### Establishing the assessment basis

- Identify the baseline and candidate measurements and confirm the source and applicability of the [pilot conditions](references/pilot-context.md). Check that the service operation, load, duration, and environment are comparable. Identify missing or contradictory information.
- Select the applicable criteria and parameters from those conditions. A changed pilot needs criteria and evidence that apply to that pilot.

### Producing and interpreting evidence

- Use the [measurement tool](scripts/compare_measurements.py) as described in the [tool instructions](references/tool-use.md) to validate the inputs, calculate metrics, and compare them with the selected limits. Check its diagnostics and the identity of the measurements used.
- Evaluate each criterion using the calculations and confirmed measurement conditions. Report a justified positive or negative assessment and its scope. If evidence is insufficient, report the gap and its effect; the affected Outcome remains unconfirmed.

## Inputs

Baseline and candidate request measurements and their measurement context.

## Controls

The applicable pilot criteria in [pilot conditions](references/pilot-context.md) govern the assessment. For this Process Description, apply the [Process Framework](../../spec/process-framework.md) and [ALPS Specification](../../spec/ALPS-SPEC.md).

## Constraints

This assessment concerns the specified pilot. Production suitability requires evidence for production conditions. Deployment and collection of new measurements are outside this example's scope. The supplied measurements are synthetic teaching data, not evidence about a real service.

## Enablers

An agent able to inspect the context, use a command tool, and interpret results; a local Python 3.11 or later environment; and the bundled measurement script. See [tool instructions](references/tool-use.md) for its interface and limits.

## Resources

This file is the source description for the [Japanese translation](references/locales/ja/SKILL.md). The [example guide](../README.md) explains its supporting configuration and evaluation cases.
