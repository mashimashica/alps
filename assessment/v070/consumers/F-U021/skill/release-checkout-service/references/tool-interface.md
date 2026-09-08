# Release tool interface and configuration

This reference describes the supplied synthetic `release_tool.py` contract. The work's meaning and success criteria remain in `SKILL.md`. At application time confirm the provided tool implements this interface; if it differs, read its source or help and resolve the affected assumptions before relying on it.

## Connection configuration

The applying agent requires Python 3 and filesystem access to the application-provided tool and state. No package installation, network, credentials, or external repository is required. Use `assets/release-context.json` from the Skill root as an optional binding record. Fill its null fields from the current application request and observed evidence, leaving unknown values null. `authorized_operations` must reflect actual authorization; populating the record does not grant it.

| Binding | Source and use |
| --- | --- |
| `environment_name` | User's desired environment. |
| `environment_path` | Supplied directory containing `release_tool.py`. |
| `state_path` | Supplied local JSON simulation for this environment. |
| `environment_mapping_source` | Request or other supplied authoritative information connecting the state file to the desired environment. |
| `candidate_id` | Exact candidate from the request; never inferred as a replacement from `inspect`. |
| `candidate_digest` | Observed content identity from `inspect`, retained for comparisons and retries. |
| `request_id` | Stable identifier for one promotion request; required before promotion or reconciliation. |
| `authorized_operations` | Operations covered by the user's current simulation request. |

The CLI has no `--environment` argument. Changing `--state` changes the simulation being operated on. Never silently substitute a different file. The state must be valid UTF-8 JSON with the expected object fields; do not create or repair it unless separately authorized.

## Invocation

Resolve each placeholder from the binding. Quote paths and IDs safely, or preferably pass arguments as an argument vector without a shell. Do not pass the literal angle-bracket placeholders or interpolate untrusted values as shell code.

```text
python3 <environment-path>/release_tool.py --help
python3 <environment-path>/release_tool.py --state <state.json> inspect
python3 <environment-path>/release_tool.py --state <state.json> qualify --candidate <candidate-id>
python3 <environment-path>/release_tool.py --state <state.json> promote --candidate <candidate-id> --request-id <request-id>
python3 <environment-path>/release_tool.py --state <state.json> request-status --request-id <request-id>
python3 <environment-path>/release_tool.py --state <state.json> probe
python3 <environment-path>/release_tool.py --state <state.json> checkout
```

Operations return JSON on stdout. Preserve stdout, stderr, and the process exit code; parse the output and inspect its fields. A missing file, malformed JSON, unexpected schema, or execution error may produce a traceback rather than the documented JSON. Do not infer absence of state changes from an unusable response.

| Operation | Effect and returned evidence | Interpretation |
| --- | --- | --- |
| `inspect` | Read-only; returns the state object, exit 0. | Supplies candidate, production, qualification, approval, owner, sequence, and recorded request evidence; missing fields are not affirmative evidence. |
| `qualify` | Replaces `qualification` and increments state `sequence`. Returns `{candidate, digest, passed, sequence}`. | Exit 0 means passed; exit 2 may be failed qualification or candidate mismatch. A failed qualification still writes the new qualification when the candidate matches. It never approves. |
| `promote` | On a new accepted request, writes production ID/digest/health/checkout fields, records a request result, and increments `promotion_count`. | Returns `{candidate, digest, promoted: true}` on confirmed acceptance or exact replay. Exit 2 means rejected by candidate/approval/request checks. A response does not establish production readiness or checkout. |
| `request-status` | Read-only; returns `{request_id, result}` with exit 0. | `result` is the recorded promotion result or null. Confirm its candidate and digest. Exit 0 alone does not establish a promotion. |
| `probe` | Read-only; returns `{revision, observation: "probe", ok}`. | `revision` is the production object; `ok` reflects its `healthy` field. Exit 0 for true, 2 for false. |
| `checkout` | Read-only synthetic observation; returns `{revision, observation: "checkout", ok}`. | `ok` reflects production `checkout_ok`. Exit 0 for true, 2 for false. This simulates checkout completion; it does not perform a real purchase. |

The synthetic timeout flag may cause `promote` to write its effect, return an error JSON saying its effect is unconfirmed by that response, and exit **75**. Reconcile it using the recorded request before proceeding. Other interrupted or ambiguous responses also need reconciliation.

## Approval comparisons

Let `c` be current candidate, `q` current qualification, `a` approval. A new promotion requires all of these, in addition to user operation authorization and confirmed environment mapping:

- Requested candidate ID equals `c.id`; the relevant identity fields must be present.
- `q.candidate == a.candidate == c.id`.
- `q.digest == a.digest == c.digest`.
- `q.passed` is true.
- `a.owner == state.service_owner`, with an identified service owner.
- `a.qualification_sequence == q.sequence`.
- `a.sequence > q.sequence`.

These comparisons express exact scope and subsequent approval. The latest qualification is the one stored in `qualification`; history is not preserved there. Every qualification rerun, including failure, replaces it and changes the sequence. The owner's separate process supplies the approval record; neither this configuration nor `qualify` can do so. Recheck affected judgments when candidate, qualification, owner, approval, or environment changes.

## Request identity and concurrency limits

The request ledger is scoped to the selected state file. Within it, an exact candidate ID/digest/request ID replay returns the recorded result without another promotion. A different candidate/digest under an existing request ID is rejected. The implementation checks current candidate identity before replay and consults an existing request before checking current approval; a replayed success therefore does not prove that current approval is valid or that production still contains that revision. Use `request-status` to discover historical effects and production observations to assess present results.

The implementation reads and rewrites a JSON file without locking or a compare-and-swap operation. Its idempotency assumes serial access to that file. Avoid overlapping state-changing commands; if another writer may be active, resolve that coordination before promotion or retry. A new request ID is a new mutation opportunity, even for the same revision.

The simulator supplies no independent environment identification, owner authentication service, approval command, rollback, real health network probe, or real checkout transaction. Its evidence is authoritative only within the supplied simulation and trusted state context. New runtime capabilities or changed field semantics require review of these bindings, approval comparisons, retry behavior, and result interpretation.
