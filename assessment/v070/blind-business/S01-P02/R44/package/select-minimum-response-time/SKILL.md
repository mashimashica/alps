---
name: select-minimum-response-time
description: Identify the smallest value in a supplied non-empty finite list of integer response times in milliseconds. Use when the task is to select the minimum listed measurement, without collecting measurements or judging service quality.
---

# Select the Minimum Response Time

Work only from the supplied list of response-time values. Treat each value as an integer number of milliseconds.

Identify the smallest listed value. Repeated occurrences of that value do not change the result.

Before responding, verify both required properties:

- the selected value occurs in the supplied list; and
- no value in the list is smaller than the selected value.

Return the selected value in milliseconds. Add a brief explanation only when it helps interpret the input or result.

If the list is empty, non-finite, or contains a value that is not an integer response time in milliseconds, ask the user to provide a valid list rather than inventing or converting data without instruction.

Do not assess whether the measurements indicate acceptable service quality, and do not collect or infer measurements outside the supplied list.
