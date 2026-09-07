# Simulator connection and evidence

Dependency: Python 3 and the application's existing `release_tool.py` plus a supplied JSON state file. No package installation, remote connection, credentials, wrapper or bundled simulator is required. Never replace the application tool or initialize, repair or rewrite its state as part of this workflow.

The context template is a per-request record. `authorized_operations` lists only operations covered by the cited user authorization; an empty list grants none. `request_id_origin` describes whether the ID was supplied, recovered or generated under the application's caller-chosen ID convention. `requested_digest` is optional; `observed_candidate_digest` is pinned from inspect. Record path-to-environment evidence in `environment_binding_evidence`, since this interface cannot independently prove an environment label.

Set shell variables from validated inputs, quote paths and values, and never use `eval`. In the examples, `RELEASE_ENV`, `RELEASE_STATE`, `RELEASE_CANDIDATE` and `RELEASE_REQUEST_ID` must be populated first. Use absolute paths where possible. Commands below are individual workflow steps, not a script to run unconditionally in order.

```bash
python3 "$RELEASE_ENV/release_tool.py" --state "$RELEASE_STATE" inspect
python3 "$RELEASE_ENV/release_tool.py" --state "$RELEASE_STATE" qualify --candidate "$RELEASE_CANDIDATE"
python3 "$RELEASE_ENV/release_tool.py" --state "$RELEASE_STATE" promote --candidate "$RELEASE_CANDIDATE" --request-id "$RELEASE_REQUEST_ID"
python3 "$RELEASE_ENV/release_tool.py" --state "$RELEASE_STATE" request-status --request-id "$RELEASE_REQUEST_ID"
python3 "$RELEASE_ENV/release_tool.py" --state "$RELEASE_STATE" probe
python3 "$RELEASE_ENV/release_tool.py" --state "$RELEASE_STATE" checkout
```

Capture each command's JSON output and process exit code separately. Do not join probe and checkout with `&&`, since a failing probe would suppress checkout. CLI syntax is discoverable with `python3 "$RELEASE_ENV/release_tool.py" --help`; operation help accepts `--state "$RELEASE_STATE" OPERATION --help` without running the operation.

| Operation | State effect | Result and interpretation |
| --- | --- | --- |
| `inspect` | None | Full state: candidate, production, qualification, approval, service_owner, requests and sequence when present. Exit 0 means read completed. |
| `qualify` | Replaces qualification and increments sequence, including on a failed check | `{candidate, digest, passed, sequence}`. Exit 0 for pass, 2 for failure or candidate mismatch. It never creates approval. |
| `promote` | On a new valid request, writes production, request record and promotion count | `{candidate, digest, promoted: true}` with exit 0 on success. Gate rejection returns error and exit 2. An injected response timeout returns error and exit 75 after persisting promotion. |
| `request-status` | None | `{request_id, result}` with exit 0. `result` is null for no recorded request, otherwise the stored promotion result; inspect nested identity and `promoted`. |
| `probe` | None | `{revision, observation: "probe", ok}`. Exit 0 for true, 2 for false. Revision is the production object, or null. |
| `checkout` | None | `{revision, observation: "checkout", ok}`. Exit 0 for true, 2 for false. This is separate from readiness. |

Candidate contains `id`, `digest`, `qualification_ok`, `healthy` and `checkout_ok`. The last three are simulation inputs; use qualification and production commands as evidence rather than reading the flags as completed checks. Production observations return `revision.id` and `revision.digest`, along with its health and checkout flags.

Qualification contains `candidate`, `digest`, `passed`, `sequence`. Approval contains `candidate`, `digest`, `owner`, `qualification_sequence`, `sequence`. Approval must match `service_owner`, the exact candidate content and the current passing qualification; its sequence must be later. The simulator stores only the current qualification, so stale evidence from earlier inspection is insufficient.

For promotion, the implementation first checks the candidate ID against current candidate. It then looks for an existing request ID. A recorded request matching the current candidate and digest returns the prior result without another promotion; a recorded request with differing candidate/digest errors. This retry path does not recheck approval, so a successful replay is historical effect evidence, not fresh proof of current approval. A new request must satisfy the full gate. `request-status` reads the stored record even if the current candidate changed.

The tool reads and rewrites one local JSON file and provides no concurrency lock. Avoid overlapping mutating commands. Fresh inspection reduces stale decisions but is not a transaction lock; contradictory or changing observations require reconciliation. A malformed state file, process interruption, non-JSON output or unexpected exit code is not proof of no effect. Preserve observed evidence, inspect state/status as applicable, and report unresolved matters before further mutation.
