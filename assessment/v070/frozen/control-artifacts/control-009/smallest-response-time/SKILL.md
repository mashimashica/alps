---
name: smallest-response-time
description: Identify the smallest value in a supplied non-empty finite list of integer response times in milliseconds. Use when asked for the minimum listed response time; input collection, measurement and service-quality assessment are outside scope.
---

# Select the smallest response time

Use the supplied list of integers as given. If the list is missing, empty, or contains non-integer values, ask for a non-empty finite list of integer response times in milliseconds; do not invent values or silently discard or round entries.

Start with the first listed value as the current minimum. Compare each remaining value with it, replacing the current minimum whenever a smaller value appears. Equal values require no change. A one-element list returns that element. Do not reject negative integers merely because they may seem implausible as measurements: this task concerns the supplied numbers.

Before responding, confirm that the selected value occurs in the list and that no listed value is smaller. Return the value with its unit, for example, “The smallest listed response time is {value} ms.” Repeated occurrences do not change the answer. Do not infer service quality from the result.
