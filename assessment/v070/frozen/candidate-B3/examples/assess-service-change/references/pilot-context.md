# Pilot conditions

[Japanese translation](locales/ja/pilot-context.md)

These conditions are illustrative Controls for the [Service Change Assessment](../SKILL.md). They are the source of the criteria for the supplied fixture pair.

The pilot concerns `GET /catalog` in an isolated staging environment, one concurrent client, a 60-second sampling window, and the same fixed request set and service dependencies. Both files below were constructed to represent that context. Their different latencies are the candidate's measured effect; all four requests completed without an application error.

- Baseline: [baseline.csv](../assets/baseline.csv).
- Candidate: [candidate.csv](../assets/candidate.csv).
- At least four requests in each file.
- Candidate nearest-rank p95 duration at most 200 ms.
- Candidate request error proportion at most 0.05.
- Candidate p95 increase over the baseline at most 50 ms.

All criteria must hold for a positive assessment in this pilot. The nearest-rank p95 is the sorted duration at rank `ceil(0.95 × count)`, with ranks starting at one. The error proportion is the number of rows with `status=error` divided by the number of rows. Durations include both successful and failed requests.

The small fixture size is intended to make every calculation inspectable. It does not establish statistical confidence or production representativeness. The script cannot determine whether the described measurement context is true; the agent must establish applicability from the supplied context and identify contradictions. A different load, endpoint, environment, or sampling window needs an applicable basis for comparison before these measurements can support that judgment.
