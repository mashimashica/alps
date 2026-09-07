---
name: select-minimum-response-time
description: Identify the smallest value in a supplied non-empty finite list of integer response times in milliseconds. Use for selecting the minimum from given measurements, without assessing service quality or collecting data.
---

# Select the minimum response time

Work only with the supplied list. Confirm it is non-empty, finite, and contains integer response times in milliseconds; if any of these conditions is unclear or unmet, request corrected or clarified input rather than inventing values.

Return the smallest listed integer. Repeated occurrences do not affect the selected value. Before responding, verify both required properties:

- the result appears in the supplied list; and
- no supplied value is smaller than the result.

State the selected value with the `ms` unit. Do not infer whether it represents acceptable service quality, and do not collect or remeasure response times.
