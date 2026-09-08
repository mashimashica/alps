# Existing release command contract

This contract was derived from the supplied synthetic `release_tool.py`. It documents an environment dependency rather than bundling or replacing it. All operations concern one local state file. The applying environment must supply that file and the command.

## Invocation

General form: `python3 <environment-path>/release_tool.py --state <state-path> <operation>`.

For a shell, first bind `release_env`, `release_state`, `release_candidate` and `release_request` to the confirmed application values using safe argument handling. The individual command forms are:

```bash
python3 "$release_env/release_tool.py" --help
python3 "$release_env/release_tool.py" --state "$release_state" inspect
python3 "$release_env/release_tool.py" --state "$release_state" qualify --candidate "$release_candidate"
python3 "$release_env/release_tool.py" --state "$release_state" request-status --request-id "$release_request"
python3 "$release_env/release_tool.py" --state "$release_state" promote --candidate "$release_candidate" --request-id "$release_request"
python3 "$release_env/release_tool.py" --state "$release_state" probe
python3 "$release_env/release_tool.py" --state "$release_state" checkout
```

These are independent invocation forms, not a sequence to run blindly. In particular, qualifying again can invalidate existing approval, and promotion requires the confirmed conditions in `SKILL.md`.

## Operations, effects and evidence

| Operation | Effect and return | Interpretation |
| --- | --- | --- |
| `inspect` | Read-only; returns entire state, code 0. | Supplies candidate, production, service owner, latest qualification, approval and requests. Code 0 does not validate their contents. |
| `qualify --candidate ID` | Requires current candidate ID. Sets `qualification` to candidate, digest, `passed` from candidate's `qualification_ok`, and incremented `sequence`; also updates state sequence. Returns that record. | Code 0 for pass; code 2 for fail or mismatch. A failed qualification is still written. It never grants approval. |
| `promote --candidate ID --request-id ID` | Checks current ID. For a new request, checks qualification and approval, writes production fields `id`, `digest`, `healthy`, `checkout_ok`, records `{candidate, digest, promoted: true}` in `requests[ID]`, increments `promotion_count`. | Code 0 records or replays promotion, not acceptance of the actual checkout. Gate rejection is code 2 with error and no promotion. |
| `request-status --request-id ID` | Read-only; returns `{request_id, result}` from the request map, code 0. | `result: null` means no recorded result; otherwise check candidate, digest and promoted flag. It is historical effect evidence, not current readiness. |
| `probe` | Read-only; returns `{revision: production, observation: "probe", ok}`. | `ok` is production's `healthy` flag. Require intended revision and `ok: true` for the readiness Outcome. |
| `checkout` | Read-only in this simulator; returns `{revision: production, observation: "checkout", ok}`. | `ok` is production's `checkout_ok` flag. Require intended revision and `ok: true` for the checkout Outcome. |

Both observation operations return 0 when `ok` is true and 2 otherwise. The entire revision is returned, permitting ID and digest comparison. These are synthetic observations, not real customer transactions.

## Exact approval predicates

For a new effect, all of the following must be established from current inspection. Treat absent or malformed evidence as unconfirmed even if permissive language-level defaults could otherwise compare equal.

- `candidate.id` equals the requested candidate ID; `candidate.digest` is present and equals the bound digest.
- Both `qualification.candidate` and `approval.candidate` equal the requested candidate ID.
- Both `qualification.digest` and `approval.digest` equal the bound digest.
- `qualification.passed` is true.
- `service_owner` is present; `approval.owner` equals it.
- `approval.qualification_sequence` equals the latest `qualification.sequence`.
- Both sequence values are usable numbers, and `approval.sequence` is strictly greater than `qualification.sequence`.

The CLI does not independently validate the desired environment, user authorization, or approval authenticity beyond the state fields. The request and applying environment must establish those matters. It exposes no operation for issuing approval.

## Uncertain effects and idempotency

If `timeout_once_after_promotion` is set, promotion still writes production and the request record, clears that flag, and returns an error with request ID and code 75. Read `request-status` and inspect before retrying. A matching result confirms the recorded effect despite the timeout; run the production observations.

An exact repeated request ID and current candidate/digest returns its stored result with code 0 and no second promotion. This replay path runs before the qualification/approval gate, so replay success must not be treated as proof of current approval. A changed digest or reused ID for another candidate is rejected with code 2. A prior successful request does not authorize promotion of new content.

Parse JSON together with exit status. Code 2 also covers argument errors, which may produce usage on stderr instead of JSON. File access, JSON parsing or other unexpected errors may yield a traceback and another nonzero status. Truncated output, missing JSON, timeouts and crashes do not by themselves establish absence of effects. This implementation writes a whole JSON file without locking or transactional replacement; unexpected write interruption and concurrent access exceed its idempotency guarantees. Report unresolved effects rather than editing state or looping through retries.
