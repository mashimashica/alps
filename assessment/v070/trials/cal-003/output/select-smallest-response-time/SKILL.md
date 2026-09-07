---
name: select-smallest-response-time
description: Select the smallest value from a supplied non-empty finite list of integer response times in milliseconds. Use when the requested result is the numeric minimum of the supplied list, not an assessment of measurement validity or service quality.
---

# Select Smallest Response Time

## Purpose

Identify the least integer response-time value in the supplied list using only the listed numbers.

## Outcomes

- The selected value occurs in the supplied list.
- Every value in the supplied list is greater than or equal to the selected value.

## Input

- A non-empty finite list whose values are integer response times in milliseconds.

## Tasks

Perform these Tasks in order:

1. Confirm that the supplied input meets the stated Input conditions. If it does not, report the unmet condition instead of selecting a value.
2. Determine a listed value that is less than or equal to every listed value. Repeated occurrences of a value do not affect the selection.
3. Return the selected integer response time in milliseconds. Include supporting comparison detail only when it helps answer the request.

## Constraints

- Base the selection only on the values in the supplied list.
- Do not evaluate how the response times were collected or whether they indicate acceptable service quality.

## Exit Criteria

- Both Outcomes have been checked against the complete supplied list.
