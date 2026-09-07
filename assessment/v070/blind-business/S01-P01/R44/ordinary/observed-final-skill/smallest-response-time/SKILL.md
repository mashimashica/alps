---
name: smallest-response-time
description: Identify the smallest value in a supplied non-empty finite list of integer response times in milliseconds. Use when asked for the minimum listed response time; input collection, measurement, and service-quality assessment are outside scope.
---

Given the supplied list, return its smallest integer value in milliseconds.

1. Confirm the list is non-empty, finite, and contains only integers. If it is missing, empty, or invalid, ask for a valid list instead of inventing a result or silently discarding entries. Do not round or convert values to make them integers.
2. Start with the first listed value as the candidate. Compare each remaining value with the candidate, replacing the candidate whenever a smaller value appears. Equal values require no change. Include every supplied integer, including zero or negative values.
3. Verify that the candidate occurs in the supplied list and that no listed value is smaller.
4. Report the candidate with the unit `ms`, concisely, unless the user requests a different presentation. Return the value, not its index or number of occurrences.

Use exact integer comparisons; avoid numeric conversions that could lose precision. A single-item list returns that item, and repetitions do not affect the result. Base the answer only on the supplied numbers without judging their measurements or inferring service quality.
