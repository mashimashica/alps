---
name: select-smallest-response-time
description: Identify the smallest integer response time in a supplied non-empty finite list of milliseconds. Use when the requested result is the minimum listed value; repeated values do not affect it. Do not use this skill to collect measurements or judge service quality.
---

# Select the smallest response time

## Purpose

Return the minimum value from the supplied non-empty finite list of integer response times, in milliseconds. The work concerns only the supplied numbers; it does not assess whether the measurements represent good or poor service.

## Inputs

- A non-empty, finite list of integers, each representing a response time in milliseconds.

## Tasks

1. Confirm that the supplied collection is non-empty and finite and that every item is an integer. If any condition is not met, report that the input is invalid and do not invent a result.
2. Examine the listed values, treating repeated occurrences as having no additional effect.
3. Select the smallest listed value. Any sound minimum-selection method is acceptable; do not assume the list is sorted.
4. Return the selected integer value, clearly identified as the smallest listed response time in milliseconds.

## Success criteria

- The result is a value present in the supplied list.
- No value present in the supplied list is smaller than the result.
- Repeated occurrences do not change the result.

## Boundaries and constraints

- Input collection, measurement, validation of real-world service quality, and interpretation beyond the numeric minimum are outside this skill.
- Preserve the input unit (milliseconds); do not convert, average, or otherwise transform values.
- Do not report a result when the input validity conditions fail.
