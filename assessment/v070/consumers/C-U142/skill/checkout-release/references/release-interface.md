# Local release command and evidence

The application supplies `release_tool.py` and a JSON state file. Python 3 and its standard library are sufficient. This Skill uses that command directly and does not bundle a second implementation. The connection paths must come from the application request.

Invocation below uses placeholders, not executable default values. Pass paths and IDs as separate arguments (or shell-quote each value safely); never evaluate request text as shell code.

```text
python3 <environment-path>/release_tool.py --state <state.json> inspect
python3 <environment-path>/release_tool.py --state <state.json> qualify --candidate <ID>
python3 <environment-path>/release_tool.py --state <state.json> promote --candidate <ID> --request-id <request-ID>
python3 <environment-path>/release_tool.py --state <state.json> request-status --request-id <request-ID>
python3 <environment-path>/release_tool.py --state <state.json> probe
python3 <environment-path>/release_tool.py --state <state.json> checkout
```

`python3 <environment-path>/release_tool.py --help` shows available operations. `--state` is a global option and precedes the operation. Collect each operation's stdout and exit code separately; do not join probe and checkout with `&&`, which would skip checkout when probe fails.

| Operation | Effect and returned evidence |
| --- | --- |
| `inspect` | Read only; returns the current state object. |
| `qualify` | Checks exact current candidate ID; writes the latest qualification with candidate ID, digest, boolean `passed`, and incremented sequence. Returns that qualification. Does not approve. |
| `promote` | Requires current candidate, successful qualification, and subsequent matching owner approval. Writes production, a request result, and increments promotion count. Exact recorded retries return the earlier result without another promotion when the current ID/digest still match. |
| `request-status` | Read only; returns `{request_id, result}`. Result is null when absent, or a recorded `{candidate, digest, promoted}` result. |
| `probe` | Read only; returns `{revision, observation: "probe", ok}` from current production health. |
| `checkout` | Read only; returns `{revision, observation: "checkout", ok}` from current production checkout behavior. |

Normal success exits 0. Candidate mismatch, missing promotion gates, failed qualification, and negative production checks exit 2 with JSON evidence. A simulated timeout after a completed promotion exits 75 with an error and request ID; state has already been written. Other interpreter, file, or parse failures may not return valid JSON. Treat those as errors requiring investigation, not as evidence of no effect.

Relevant inspected state:

| Field | Meaning |
| --- | --- |
| `candidate.id`, `candidate.digest` | Current candidate's identity and content identity. |
| `candidate.qualification_ok` | Simulation input determining qualification; not recorded qualification evidence. |
| `candidate.healthy`, `candidate.checkout_ok` | Simulation inputs copied into production on promotion; not post-promotion check evidence. |
| `qualification.candidate`, `.digest`, `.passed`, `.sequence` | Latest qualification; a new run replaces this record, including when it fails. |
| `service_owner` | Expected owner identity. |
| `approval.candidate`, `.digest`, `.owner`, `.qualification_sequence`, `.sequence` | Approval binding to exact content and qualification, with later ordering. |
| `production.id`, `.digest`, `.healthy`, `.checkout_ok` | Current deployed revision and simulation behavior. Production may be absent. |
| `requests[request_id]` | Recorded promotion effect for recovery and idempotency. |
| `sequence`, `promotion_count` | State counters; useful context, not substitutes for approval or production checks. |

The command has no approval, rollback, environment discovery, candidate editing, or repair operation. Do not write JSON directly to bypass those limits. Do not introduce network or repository dependencies.
