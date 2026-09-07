---
name: select-smallest-response-time
description: Select the smallest value from a supplied non-empty finite list of integer response times in milliseconds. Use when the user needs the minimum listed response time; input collection and measurement are outside this skill.
---

# Select the smallest response time

Given the supplied list, return the minimum integer in that list.

## Procedure

1. Confirm that the input is a finite, non-empty list and that every item is an integer response time in milliseconds. If the list is missing, empty, non-finite, or contains a non-integer, request corrected input rather than inventing or measuring values.
2. Inspect the supplied values and keep the smallest value seen. A single pass is sufficient; sorting is optional.
3. Report the selected integer in milliseconds. Repeated occurrences do not change the result.

The result must be one of the supplied values, and no supplied value may be smaller than it. Judge only the numbers in the supplied list; do not infer real-world service quality or collect new measurements.
