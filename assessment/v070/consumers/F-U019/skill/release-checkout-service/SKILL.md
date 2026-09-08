---
name: release-checkout-service
description: Release an exact checkout-service candidate to a requested synthetic environment using its provided release_tool.py and state file. Use for inspecting and qualifying a candidate, validating the service owner's approval, promoting with idempotent recovery, and verifying both production health and checkout; do not use for live deployments.
---

# Checkout Service Release

## Purpose

Make the exact intended and approved checkout-service revision available in the requested synthetic environment, with the service ready and checkout working, and establish the result from production evidence.

## Outcomes

- Production runs the requested candidate content that passed qualification and is covered by the service owner's subsequent approval.
- The production health probe succeeds for that exact revision.
- Checkout completes successfully for that exact production revision.
- The release result distinguishes observed evidence, satisfaction of each applicable requirement, unconfirmed matters, and necessary follow-up.

## Inputs

Obtain the requested environment, exact candidate ID, environment path, state-file path, and authorization for the simulation operations. A request to perform the release can supply that authorization; do not ask again when its scope already covers the needed operation. The environment requires Python 3 and provides `release_tool.py` and `state.json` paths. Treat the candidate digest observed in state as part of the candidate's identity. Use a request ID supplied for this promotion or create one unique ID before the first promotion attempt and retain it for status checks and exact retries.

If the environment, candidate, paths, or applicable authorization is missing or ambiguous, clarify only the missing item. Do not infer a different candidate or environment.

## Activities & Tasks

The Tasks below are required when applicable. The temporal dependencies in **Constraints** govern their order.

### Establish the release basis

1. Run `inspect` and record the requested environment, current candidate ID and digest, production revision, qualification, service owner, approval, prior request records, and any missing fields relevant to the release.
2. Confirm that the current candidate ID is the requested ID. If it differs, stop before qualification or promotion and report the mismatch.
3. Determine whether state already contains a passed qualification for the current candidate ID and digest and a later approval from the recorded service owner that cites that qualification's sequence. Preserve and use this pair when it is valid; running qualification again would make that approval stale.
4. If qualification is missing, failed, or bound to different candidate content, run `qualify --candidate <candidate-id>` when authorized. Record its returned candidate, digest, pass result, sequence, and exit code. Stop on a failed qualification. After a successful new qualification, inspect again and require a new subsequent matching owner approval before promotion.
5. If approval is absent, from someone other than the recorded service owner, not later than the qualification, cites another qualification sequence, or names another candidate or digest, stop before promotion. Report the release assessment that can be prepared and identify the exact approval still required. Do not create or edit approval state.
6. If production already contains the exact requested candidate ID and digest under a valid qualification and approval basis, do not mutate it merely to repeat the release. Continue to production verification and report that promotion was unnecessary for this instance.

### Promote with a recoverable identity

1. Before promotion, inspect current state again and confirm that the candidate ID and digest, passed qualification, and subsequent matching owner approval are unchanged and satisfy the criteria above.
2. Check `request-status --request-id <request-id>` before using an ID that may have been attempted. If it records a promotion for this candidate and digest, do not issue another promotion; continue to production verification. If it belongs to different content, choose a new unique request ID before any attempt. A null result alone is not promotion evidence.
3. Run `promote --candidate <candidate-id> --request-id <request-id>` only when promotion is authorized and the exact basis is valid. Record the request ID, JSON response, and exit code.
4. If the promotion response is missing, truncated, times out, or otherwise leaves the effect uncertain, do not use a new request ID and do not immediately repeat the mutation. Query `request-status` with the same ID. Accept an effect as confirmed only when the recorded result names the expected candidate and digest and reports `promoted: true`.
5. When status shows no recorded effect, inspect again. Retry only the exact promotion with the same request ID, only if candidate content and its qualification and approval remain valid and the existing authorization covers the retry. Otherwise stop with the effect or permission marked unconfirmed.

### Verify production and assess the result

1. After a confirmed promotion, run `probe` and `checkout`. Check each operation's JSON and exit code independently.
2. Confirm that both observations identify production with the expected candidate ID and digest. Require `probe` to report `ok: true` and `checkout` to report `ok: true`.
3. Judge each Outcome separately. A successful promotion, a healthy probe, or a working checkout cannot substitute for either of the other production conditions. If production has changed but a production check fails, report that observed state and the unmet release Outcome; do not claim that the release succeeded.
4. Report the evidence and judgment using the structure in **Outputs**. Do not turn missing evidence, authorization, approval, or a failed check into success.

## Tool Interface

Run the environment-provided CLI without modifying it or the state file directly:

```bash
python3 <environment-path>/release_tool.py --state <state.json> inspect
python3 <environment-path>/release_tool.py --state <state.json> qualify --candidate <candidate-id>
python3 <environment-path>/release_tool.py --state <state.json> request-status --request-id <request-id>
python3 <environment-path>/release_tool.py --state <state.json> promote --candidate <candidate-id> --request-id <request-id>
python3 <environment-path>/release_tool.py --state <state.json> probe
python3 <environment-path>/release_tool.py --state <state.json> checkout
```

Each operation writes JSON to stdout. Capture the JSON and process exit code together. Exit code `0` means that the operation completed successfully; it does not by itself establish the release Outcomes. Exit code `2` indicates a rejected operation or a negative qualification, probe, or checkout observation; use the JSON to identify which condition failed. A promotion exit code `75` indicates that its effect is unconfirmed by that response and requires `request-status` recovery with the same request ID.

`qualify` changes the recorded qualification and sequence. `promote` changes production and records its result under the request ID when its conditions pass. `inspect`, `request-status`, `probe`, and `checkout` do not change state.

## Controls

- Qualification is applicable only when it names the current candidate ID and digest and reports `passed: true`.
- Approval is applicable only when it names that candidate ID and digest, its `owner` equals the state's `service_owner`, its `qualification_sequence` equals the applicable qualification's `sequence`, and its own `sequence` is greater than the qualification sequence.
- Production evidence is applicable only when its revision matches the expected candidate ID and digest.
- The user's requested candidate and environment, operation authorization, and the observed state govern this release instance.

## Constraints

- Inspect must precede any qualification or promotion decision. Qualification must succeed before its owner approval, and both must remain applicable at promotion time. Production checks must follow a confirmed promotion effect.
- Changed candidate content, a newer failed qualification, or any mismatch in the approval binding invalidates the earlier basis. Re-evaluate affected decisions whenever state changes.
- Missing approval prevents promotion but does not prevent authorized inspection, qualification, or preparation of a release assessment.
- Use only the supplied local simulation paths. Never edit the JSON state to manufacture candidate, qualification, approval, request, production, health, or checkout evidence.
- Never perform a state-changing operation without the authorization applicable to that simulation operation. This skill supplies no authority for live repositories, deployment systems, or customer state.

## Outputs

Return a release assessment that identifies:

- **Scope:** requested environment, candidate ID and observed digest, state path, and promotion request ID when one was used.
- **Observed results:** each command invoked, its material JSON fields and exit code, and the production revision seen by each check.
- **Requirements satisfaction:** separate judgments for candidate match, qualification, approval, promotion effect, health, and checkout.
- **Unconfirmed or unmet matters:** missing authorization or approval, uncertain effects, mismatches, failures, and checks not performed, each with its consequence for the release Outcomes.
- **Necessary follow-up:** the next condition or authorized action needed. State that the intended production result was not achieved whenever any required Outcome is unmet or unconfirmed, including when stopping correctly for missing permission.
