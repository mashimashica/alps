---
name: select-minimum-response-time
description: Identify the smallest value in a supplied non-empty finite list of integer response times in milliseconds. Use for selecting the minimum listed response-time value, not for collecting measurements or judging service quality.
---

# Select the minimum response time

Accept a non-empty finite list of response times expressed as integers in milliseconds. If the input is empty, unbounded, contains a non-integer value, or does not clearly provide the list, ask the user to correct or clarify it before selecting a result.

Compare the integer values and return the smallest listed value in milliseconds. Repeated occurrences do not affect the result. Ensure the reported value appears in the supplied list and that no listed value is smaller.

Report the result concisely. Do not infer, collect, or validate measurements, and do not characterize the response time as good, bad, fast, slow, or representative of real service quality unless the user separately asks for analysis beyond this selection task.
