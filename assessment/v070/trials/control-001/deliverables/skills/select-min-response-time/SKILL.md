---
name: select-min-response-time
description: Identify the smallest value in a supplied non-empty finite list of integer response times expressed in milliseconds. Use when the values are already collected and the task is only to select the minimum; repeated values do not affect the result.
---

# Select the minimum response time

Given a non-empty finite list of integer response times in milliseconds, return the smallest listed integer.

## Procedure

1. Confirm that the supplied collection is finite, non-empty, and contains integers. Input collection and measurement are outside this skill.
2. Compare the values, retaining the lowest value seen. Equal values require no change.
3. Return that value exactly as an integer in milliseconds.

The result must be one of the supplied values, and no supplied value may be smaller than it. Treat negative, zero, and positive integers as ordinary integers; do not reinterpret them as a service-quality judgment. Do not average, deduplicate for reporting, sort for presentation, or apply a threshold unless the caller separately requests such work.

If the input is empty, non-finite, or includes a non-integer, do not invent a result. State which input requirement failed and request a corrected list. If the list is valid, a single pass while tracking the current minimum is sufficient; any equivalent method is acceptable.

For example, `[18, 7, 7, 11]` produces `7 ms`, because `7` is present and no listed value is lower.
