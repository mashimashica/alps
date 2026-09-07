---
name: select-minimum-response-time
description: Identify the smallest value in a supplied non-empty finite list of integer response times in milliseconds. Use when the task is to select the minimum listed measurement, without evaluating service quality or collecting measurements.
---

# Select the minimum response time

Work only with the supplied list of response times. Treat repeated values as ordinary list entries; repetition does not change the minimum.

Confirm that the input is a non-empty finite list of integers measured in milliseconds. If it is missing, empty, or contains a value that cannot be treated as an integer response time, ask the user to correct or clarify it rather than inventing or discarding values.

Compare all listed integers and return the smallest one in milliseconds. Ensure that:

- the result occurs in the supplied list; and
- no listed value is smaller than the result.

Report the selected value clearly. Do not infer service quality, validate how the measurements were collected, or gather new measurements unless the user separately asks for that work.
