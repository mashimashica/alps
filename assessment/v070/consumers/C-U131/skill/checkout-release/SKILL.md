---
name: checkout-release
description: Qualify and release an exact checkout-service candidate in the supplied synthetic release environment, including approval validation, idempotent promotion recovery, and production health and checkout verification. Use for assessing, preparing, executing, or confirming these simulated checkout releases.
---

# Checkout release

Use the supplied local command and state file:

```bash
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

Treat the state as the release record. Do not edit it directly. This skill does not authorize live deployments or access to external repositories, deployment systems, or customer state.

## Establish the release target

Extract the requested candidate ID, environment path, state path, desired environment, and whether the user has authorized state-changing simulation operations. Keep business approval recorded in the state distinct from the user's authorization to execute `qualify` or `promote`.

Run `inspect` first. Compare the requested candidate ID with the current candidate and record its digest. Stop promotion if the request is ambiguous, the desired environment does not correspond to the supplied simulation, or the current candidate ID differs. Never substitute a candidate or infer approval.

`inspect`, `request-status`, `probe`, and `checkout` are observations. `qualify` and `promote` change simulated state; execute each only when the user's request authorizes that change. If mutation is not authorized, inspect and prepare the assessment, then identify the specific authorization still needed.

## Qualify and validate approval

A usable qualification must name the current candidate ID and digest and have `passed: true`. Prefer an existing current passing qualification when present; rerunning qualification creates a new sequence and makes approval for the earlier sequence stale.

When qualification is needed and authorized, run:

```bash
python3 <environment-path>/release_tool.py --state <state.json> qualify --candidate <candidate-id>
```

A nonzero exit or `passed: false` blocks promotion. After qualification, inspect state again. Promotion requires all of the following in the latest state:

- candidate ID and digest still equal the requested, qualified candidate;
- qualification passed and refers to that exact ID and digest;
- approval refers to that exact ID and digest;
- approval owner equals `service_owner`;
- approval's `qualification_sequence` equals the current qualification sequence; and
- approval sequence is later than the qualification sequence.

Changed candidate content, a new qualification, a failed qualification, missing approval, or mismatched owner/scope makes older approval unusable. Report the mismatch and stop before promotion. Qualification success alone is not approval.

## Promote with an idempotency key

Choose one stable, unique request ID for this exact promotion attempt and record it before executing. Reuse it for every status check or retry of that attempt; never switch IDs to resolve uncertainty. Do not reuse an ID for different candidate content.

Immediately before promotion, ensure authorization is present and the latest inspected state still satisfies the candidate, qualification, and approval conditions. Then run:

```bash
python3 <environment-path>/release_tool.py --state <state.json> promote --candidate <candidate-id> --request-id <request-id>
```

Treat a timeout or missing response as an unknown effect, not a failure. Resolve it first with:

```bash
python3 <environment-path>/release_tool.py --state <state.json> request-status --request-id <request-id>
```

If status records `promoted: true` for the exact candidate and digest, do not promote again. If no effect is recorded and the candidate, qualification, approval, and authorization still apply, retry `promote` with the same request ID. Any conflicting status or request-ID ownership is a blocking inconsistency.

## Verify the production outcome

After promotion is confirmed, run both operations even if the first succeeds:

```bash
python3 <environment-path>/release_tool.py --state <state.json> probe
python3 <environment-path>/release_tool.py --state <state.json> checkout
```

Confirm each observation names the promoted candidate ID and digest. The release is achieved only when promotion is confirmed, the probe reports `ok: true`, and checkout reports `ok: true` for that same revision. A successful promote command or health probe alone is insufficient. If either check fails or reports another revision, state that the intended production result was not achieved and give the required investigation or recovery follow-up; do not claim success.

## Report

Separate the result into:

- **Observed:** commands run, candidate/digest, qualification and approval evidence, promotion request status, probe result, and checkout result, including failures or uncertainty.
- **Requirements satisfied:** each release condition supported by observed evidence.
- **Unconfirmed or blocked:** missing authorization, stale/missing approval, changed candidate, failed qualification, unresolved request effect, revision mismatch, or failed production behavior.
- **Follow-up:** the next concrete action needed and who must provide any missing approval or authorization.

Distinguish a correctly stopped workflow from a successful release. Never describe the intended production outcome as achieved unless all production evidence confirms it.
