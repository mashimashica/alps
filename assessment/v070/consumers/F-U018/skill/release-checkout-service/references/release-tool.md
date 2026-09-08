# Release-tool interface

Use the `release_tool.py` supplied with the business application's synthetic environment. It reads and, for qualification or promotion, updates the supplied JSON state file. It requires Python 3 and no documented third-party package.

Set these values from the release request; do not guess or substitute them:

```bash
environment_path='<supplied environment path>'
state_path='<supplied state-file path>'
candidate_id='<exact requested candidate ID>'
```

Quote every expansion. Capture stdout and the exit code for each call.

## Operations

```bash
python3 "$environment_path/release_tool.py" --state "$state_path" inspect
python3 "$environment_path/release_tool.py" --state "$state_path" qualify --candidate "$candidate_id"
python3 "$environment_path/release_tool.py" --state "$state_path" promote --candidate "$candidate_id" --request-id "$request_id"
python3 "$environment_path/release_tool.py" --state "$state_path" request-status --request-id "$request_id"
python3 "$environment_path/release_tool.py" --state "$state_path" probe
python3 "$environment_path/release_tool.py" --state "$state_path" checkout
```

| Operation | State effect | Interpret the result |
| --- | --- | --- |
| `inspect` | None | Returns current candidate, production, qualification, approval, owner, and request information. An observation does not qualify or approve a candidate. |
| `qualify` | Records a new qualification and sequence, including on a failed qualification | Exit `0` and `passed: true` support qualification of the returned candidate and digest. Exit `2` and `passed: false` record a failed qualification and block promotion. A new record supersedes the approval basis of an earlier qualification. |
| `promote` | May replace simulated production and record a request | Exit `0` with matching candidate, digest, and `promoted: true` establishes the operation. Exit `2` reports a rejected precondition. Exit `75` can mean production changed before the response timed out; resolve it with `request-status`. |
| `request-status` | None | Returns the result recorded for that request ID, or `null` if no result is recorded. Match the candidate and digest before relying on a recorded result. |
| `probe` | None | Returns the production revision and `ok`. Exit `0` means the reported revision is healthy; exit `2` means it is not. Always check revision identity. |
| `checkout` | None | Returns the production revision and `ok`. Exit `0` means checkout completed for the reported revision; exit `2` means it did not. Always check revision identity. |

An unexpected exit, unreadable state, malformed output, or interrupted call limits what the response establishes. For any uncertain promotion effect, use the original request ID with `request-status` before considering a retry.

## Approval validity

An approval is valid for promotion only when fresh `inspect` evidence establishes all of these conditions:

- the current candidate ID equals the exact requested candidate ID;
- the current candidate digest equals both the qualification digest and approval digest;
- the qualification candidate and approval candidate equal the requested candidate ID;
- the qualification has `passed: true`;
- the approval `owner` equals the state's `service_owner`;
- the approval `qualification_sequence` equals the current qualification `sequence`;
- the approval `sequence` is greater than the qualification `sequence`.

These comparisons establish both exact scope and order. A same-named candidate with changed content has a different digest and needs new qualification and subsequent approval. Running qualification again creates a new sequence and therefore requires a new approval for that qualification.

## Retry boundary

The request ID makes an exact retry idempotent. After an uncertain `promote` response:

- If status returns a matching recorded promotion, do not retry.
- If status definitively returns `null`, re-inspect the promotion basis before retrying with the same request ID.
- If status cannot be obtained or the basis changed, stop with the effect unconfirmed.
- Never use one request ID for another candidate or digest, and never use a new request ID to bypass uncertainty about the first.

