---
name: select-smallest-response-time
description: Identify the smallest listed value in a supplied non-empty finite list of integer response times in milliseconds. Use when asked to select the minimum response time from supplied numbers.
---

# Select the smallest response time

Use the supplied list of integer millisecond values. If the list is missing, empty, or contains ambiguous or non-integer entries, ask for a valid or clarified list before selecting a result. Do not collect or measure response times.

Compare the listed values numerically and select the smallest. One way is to start with the first value and replace it whenever a smaller value appears while scanning the rest of the list. Repeated occurrences do not change the result. Retain all supplied integers, including zero and negative values; do not adjust them based on measurement plausibility.

Before responding, confirm that the selected value occurs in the supplied list and that no listed value is smaller. For a one-value list, select that value.

State the selected value in milliseconds concisely. Make no inference about real service quality or the reliability of the measurements.
