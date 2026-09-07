---
name: select-min-response-time
description: Identify the smallest integer response-time value in a supplied non-empty finite list of milliseconds. Use when the requested result is the minimum listed measurement; repeated values do not affect the result. Do not use this skill to collect measurements or assess service quality.
---

# Select the minimum response time

Given a non-empty finite list of integer response times in milliseconds, return the smallest value in that list.

## Procedure

1. Confirm that the supplied collection is a finite, non-empty list and that every item is an integer response time in milliseconds. If the input is missing, empty, non-finite, or contains non-integers, explain the input problem instead of inventing or coercing values.
2. Inspect the listed values and retain the lowest value encountered. Repeated occurrences are immaterial.
3. Return the selected integer value, preserving its millisecond unit. The result must be one of the supplied values, and no supplied value may be smaller.

Do not collect new measurements, infer values, or evaluate whether the measurements indicate good or poor service quality. This skill only selects the minimum from the supplied numbers.
