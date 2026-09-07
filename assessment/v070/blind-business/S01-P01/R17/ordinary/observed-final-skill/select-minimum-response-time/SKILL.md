---
name: select-minimum-response-time
description: Select the smallest value from a supplied non-empty finite list of integer response times in milliseconds. Use when the values are already provided and only the list minimum is requested; do not use this skill to collect or measure response times.
---

# Select the minimum response time

Given a non-empty finite list of integer response times in milliseconds, return the smallest listed integer.

Process the supplied values only:

1. Treat each supplied item as an integer number of milliseconds.
2. Compare all items and retain the least value.
3. Return that value exactly as a value from the input list.

Repeated values do not change the result. The result must be present in the supplied list, and no supplied value may be smaller than it. Do not infer, measure, validate, or interpret service quality; input collection and measurement are outside this skill.

If the list is empty, non-finite, or contains non-integer values, state that the input does not meet this skill's requirements instead of producing a result.
