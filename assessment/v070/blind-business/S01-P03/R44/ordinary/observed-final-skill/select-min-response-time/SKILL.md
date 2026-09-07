---
name: select-min-response-time
description: Selects the smallest integer response time from a supplied, non-empty finite list of response times in milliseconds. Use when the values are already provided and the required result is the minimum listed value; this skill does not collect or measure response times or assess service quality.
---

# Select the minimum response time

Given a supplied list of response times, return the smallest value in that list.

## Inputs

- A non-empty, finite list.
- Every list item must be an integer response time expressed in milliseconds.

Treat the supplied numbers as the complete input. Do not collect measurements, infer missing values, or judge whether the measurements indicate good or poor service quality. Preserve each integer's value; do not round, average, convert units, or otherwise transform it.

## Procedure

1. Confirm that a list was supplied and that it is non-empty and finite.
2. Confirm that every item is an integer. Reject ambiguous values such as decimals, numeric strings that have not been explicitly parsed by the caller, units other than milliseconds, or non-numeric entries.
3. Set the current smallest value to the first item.
4. Examine each remaining item. If it is smaller than the current smallest value, replace the current smallest value with it. Equal values require no change, so repeated occurrences do not affect the result.
5. Return the current smallest value exactly as an integer in milliseconds.

## Result requirements

The returned value must be one of the supplied list items, and no supplied item may be smaller than it. State the selected value clearly; a concise response such as `Minimum response time: <value> ms` is sufficient. Do not add conclusions about real-world service performance.

If the input is absent, empty, non-finite, or contains an invalid item, report that the supplied list does not meet the input requirements and identify the reason. Do not invent a result or silently discard invalid items.
