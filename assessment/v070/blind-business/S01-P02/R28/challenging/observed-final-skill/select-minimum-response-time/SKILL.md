---
name: select-minimum-response-time
description: Identify the smallest value in a supplied non-empty finite list of integer response times in milliseconds. Use when the task is to select the minimum listed measurement, without judging service quality or collecting measurements.
---

# Select the Minimum Response Time

Work only from the response-time values the user supplies. Treat repeated occurrences as the same candidate for the result.

Confirm that the input is a non-empty, finite list and that every supplied response time is an integer expressed in milliseconds. If a value or unit is ambiguous, ask for the missing clarification instead of guessing. Do not reject or alter a supplied integer based on whether it seems like a realistic measurement; measurement collection and quality are outside this task.

Select the numerically smallest listed integer. Before responding, verify both required properties:

- the selected value occurs in the supplied list;
- every listed value is greater than or equal to it.

Return the selected value in milliseconds. Keep the response concise unless the user asks for the comparison or other supporting detail.
