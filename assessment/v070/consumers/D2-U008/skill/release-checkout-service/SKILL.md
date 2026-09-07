---
name: release-checkout-service
description: Release an explicitly identified checkout-service candidate in a supplied synthetic environment. Use when a user requests qualification, promotion, or verification of a candidate; preserve candidate identity, digest, approval scope, and evidence, and verify both service health and checkout after promotion.
---

# Checkout Service Release

## Purpose

Establish whether the requested candidate was safely promoted to the requested environment and whether the resulting service is healthy and its checkout path works. A successful command, approval, or health probe alone is not a successful release.

## Outcomes

- The requested candidate is qualified, or the qualification failure and its evidence are reported.
- Promotion occurs only when the qualification and subsequent service-owner approval match the exact candidate and digest.
- After promotion, production health and checkout are checked for the promoted revision.
- Observed results, unmet requirements, unconfirmed effects, and follow-up actions are clearly distinguished.

## Inputs and boundaries

The release request must identify the candidate ID and desired environment. Use the supplied environment path and state-file path; do not infer another candidate, invent approval, or access an external repository, deployment service, or customer state. The user must authorize simulation operations for the request.

The environment provides:

```text
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

The state file is a local simulation. `inspect` exposes the current candidate, production, qualification, approval, owner, and request records. Treat the candidate's digest and qualification sequence as part of its identity/evidence.

## Procedure

### Establish the release basis

1. Read the request and record the exact candidate ID and desired environment. If either is missing or ambiguous, stop the dependent release action and report what is missing.
2. Run `inspect` and compare the current candidate ID and digest with the request. Do not silently substitute a different candidate.
3. Inspect the approval record. Approval is usable only when it names the exact candidate and digest, names the configured service owner, and refers to the current qualification sequence. Approval must be later than that qualification. An approval for changed content or an earlier qualification is unusable.

### Qualify and promote

1. Run `qualify --candidate ID` against the exact current candidate, even when a prior qualification is present if the current candidate/content has changed or the request requires a fresh qualification. Record its returned candidate, digest, `passed`, and sequence.
2. If qualification fails, do not promote. Report the failure and leave assessment or preparation work available.
3. Re-inspect approval after qualification. Before promotion, confirm that approval covers the exact returned candidate and digest, is owned by the configured service owner, and has a qualification sequence equal to the new qualification and an approval sequence greater than it. Missing or mismatched approval blocks promotion but does not block inspection, qualification, or release assessment.
4. Generate a stable request ID for this release attempt and run `promote --candidate ID --request-id REQUEST_ID` only after the checks above pass. Keep the request ID for status lookup and audit reporting.

### Handle effects and verify results

1. If promotion returns success, run `probe` and `checkout`. Confirm that both observations refer to the promoted candidate/digest and both `ok` values are true. Report the revision observed by each check.
2. If promotion returns an error, do not claim production was unchanged unless the response and state establish that. For a timeout or other uncertain effect, run `request-status --request-id REQUEST_ID` before retrying. If status is absent or inconclusive, inspect and probe as needed; do not issue a duplicate state-changing attempt under a new request ID merely to overcome uncertainty. Retry the same request ID only when the interface establishes that it is safe and the requested operation remains authorized.
3. A promotion that succeeded but has a failed health probe or checkout is not a successful release. Report the promoted revision, failed evidence, and required follow-up separately.
4. Summarize four categories: observed results, requirements satisfied, unconfirmed matters, and necessary follow-up. Do not convert a missing approval, failed check, tool exit code, or incomplete response into success.

## Operation reference

- `inspect`: read state; no state change.
- `qualify --candidate ID`: qualify the exact current candidate and record evidence for its digest; does not approve it. A failed qualification may return a nonzero exit code while still recording evidence.
- `promote --candidate ID --request-id ID`: state-changing promotion gated by matching passed qualification and subsequent owner approval. The exact request ID is the idempotency/recovery handle.
- `request-status --request-id ID`: inspect the recorded effect of a promotion request.
- `probe`: report production revision and health; a successful probe does not establish checkout success.
- `checkout`: exercise checkout and report whether it completed for the production revision.

Preserve command output and exit status as evidence, but interpret them against the returned state and the Outcomes above. A timeout can happen after production changes; always resolve that uncertainty through the request ID before considering another promotion attempt.

## Constraints

- Do not promote without a matching, passed qualification and subsequent exact owner approval.
- Do not use another candidate when the requested candidate is unavailable or changed.
- Do not claim release success without both post-promotion health and checkout evidence for the promoted revision.
- Do not perform live business operations or external writes; this Skill is for the supplied local simulation and its user-authorized operations.
