---
name: smallest-response-time
description: Identify the smallest listed integer response time in milliseconds from a supplied non-empty finite list. Use when asked for the minimum response time among supplied values.
---

Given a non-empty finite list of integer response times in milliseconds, return its smallest value.

1. Confirm that the supplied list is non-empty and contains only integers. If the list is missing, empty, or contains ambiguous or invalid entries, ask for a valid list rather than inventing values or silently discarding entries.
2. Start with the first listed value as the candidate. Compare each remaining value with the candidate, replacing the candidate whenever the next value is smaller. Equal values leave the candidate unchanged.
3. Check that the final candidate occurs in the supplied list and that no listed value is smaller.
4. State the selected value in milliseconds. A single concise answer is sufficient; repeated occurrences do not require repeated output.

Compare the supplied integers as given, including zero or negative values. Do not collect measurements or infer real service quality from this selection.
