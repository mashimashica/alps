---
name: checkout-service-release
description: Release a specified checkout-service candidate through qualification, matching service-owner approval, promotion, and post-promotion health and checkout verification using the supplied local release command. Use for authorized synthetic or local release requests; do not infer approval or claim success from deployment alone.
---

# Checkout-service release

## Purpose

Make the exact requested candidate available in the requested environment only when its current content has passed qualification and the service owner's approval covers that same candidate and qualification. After promotion, establish the actual production result with both a health probe and a checkout exercise.

This skill operates only on the supplied local simulation. It must not access external repositories, deployment services, or real customer state.

## Required inputs and authority

Obtain from the request and local environment:

- the exact candidate ID and desired environment;
- the state-file path and the environment path containing `release_tool.py`;
- authorization for simulation operations; and
- a request ID for promotion (stable across retries).

Do not substitute a candidate, environment, request ID, or approval. The state inspection is the source for the current candidate digest, service owner, qualification record, approval record, production revision, and prior request effects. Approval must be attributable to the service owner and must identify the exact candidate and digest, refer to the qualification sequence, and be later than that qualification. A changed candidate or newly failed qualification invalidates an older approval.

## Interface

Invoke the supplied command (quote paths as needed):

```text
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

Operations and their roles:

- `inspect` reads candidate, production, qualification, and approval state; it does not change state.
- `qualify --candidate ID` evaluates the exact current candidate and records evidence keyed by its digest. A nonzero result means qualification did not pass; it is not approval.
- `promote --candidate ID --request-id ID` changes production only when candidate, digest, passed qualification, and subsequent matching owner approval all match. The request ID makes an exact retry idempotent.
- `request-status --request-id ID` reports the recorded effect for that promotion request.
- `probe` reports the production revision and health.
- `checkout` exercises checkout and reports whether it completed for the production revision.

Treat stdout JSON, exit status, and state evidence together. A nonzero status is a failed operation unless the output explicitly identifies an uncertain post-effect. Do not treat command completion, a healthy probe, or an artifact's existence as checkout success.

## Activities and tasks

### Establish the release basis

1. Inspect state before changing anything. Compare the requested candidate and environment with the inspected current candidate and record its ID and digest.
2. Confirm that the requested candidate is exact and that the desired environment is the one represented by the supplied state file. If either is missing or mismatched, stop promotion while reporting the gap.
3. Inspect approval and qualification records. Determine whether the current candidate has a passed qualification and whether the owner's approval covers the same candidate and digest, names the service owner, and has a sequence later than that qualification.

### Qualify and promote

1. Run `qualify --candidate ID` for the exact current candidate when qualification is absent, stale, or requested for this release. Record candidate, digest, sequence, pass/fail, exit status, and output.
2. Re-inspect when qualification changes the evidence or when candidate state may have changed. Never use an approval for a different digest or an approval preceding the qualification.
3. If the exact owner approval is absent, mismatched, stale, or otherwise unconfirmed, do not promote. You may inspect, qualify, and prepare the release assessment, but must report that the intended production result is not achieved.
4. If all promotion prerequisites match, invoke `promote` with the stable request ID. A successful response is evidence of a promotion attempt, not yet evidence that checkout works.
5. If promotion times out or its effect is otherwise uncertain, do not repeat `promote` blindly. First call `request-status --request-id ID` and inspect state. Retry only with the same request ID after the status/state shows no effect and the prerequisites still match. Treat a recorded result or matching production state as the effect of the original request.

### Verify the actual release

1. After a confirmed promotion, run `probe` and verify that the production revision has the requested candidate ID and digest and reports healthy.
2. Run `checkout` and verify that it reports success for that production revision.
3. Judge the release as achieved only when promotion is confirmed, revision and digest match, health is successful, and checkout is successful. Otherwise distinguish failed, blocked, and unconfirmed conditions and state the necessary follow-up.

## Reporting

Return a concise assessment with separate sections or labels for:

- **Observed:** commands, exit statuses, candidate/digest, qualification evidence, approval basis, request status, production revision, probe, and checkout.
- **Requirements satisfied:** exact conditions supported by evidence.
- **Blocked or failed:** missing authority, mismatches, failed qualification, failed promotion, unhealthy production, or failed checkout.
- **Unconfirmed:** timeout or incomplete evidence, including whether state was checked.
- **Follow-up:** the specific approval, requalification, retry/status check, remediation, or investigation required.

Do not invent approval, silently choose another candidate, claim success because promotion returned successfully, or perform any external/live operation. A stop for missing approval is a correct safety outcome but is not a successful release.

## Limits

This skill does not create approvals, alter candidate content, repair production, or contact an owner. It cannot establish results beyond the state file and command outputs it inspected. If the command, state path, candidate, environment, or approval provenance is unavailable, limit the judgment to the evidence available and say what remains unconfirmed.
