---
name: checkout-release
description: Release an explicitly identified checkout-service candidate into its requested environment using the supplied local release tool, with exact qualification and owner-approval checks, idempotent recovery, and post-promotion health and checkout evidence. Use for synthetic or authorized checkout release requests; do not infer candidates, approvals, environments, or live production access.
---

# Checkout service release

Use this skill only when the requester supplies (or the authorized environment supplies) the release-tool path, state-file path, exact candidate ID, desired environment, and a request ID for promotion. Treat the state file as the source of truth. The tool is a local simulation unless the requester separately authorizes another environment; this skill never creates approval or substitutes a candidate.

## Release procedure

1. Establish the basis before changing state. Confirm the candidate ID and desired environment from the request, and confirm the supplied command and state path. If any of these are missing or ambiguous, inspect only if a path is available, then report the gap and stop before promotion.
2. Inspect the current state:

   `python3 <environment-path>/release_tool.py --state <state.json> inspect`

   Record the candidate ID and digest, service owner, existing qualification, approval (including owner, candidate, digest, qualification sequence, and approval sequence), and production state. Do not treat a deployment command's success or a probe alone as release success.
3. Qualify the exact current candidate before promotion:

   `python3 <environment-path>/release_tool.py --state <state.json> qualify --candidate <candidate-id>`

   A nonzero result or `passed: false` means promotion is blocked, though assessment and reporting may continue. Qualification is candidate-digest-specific; if inspection later shows the candidate or digest changed, qualify again and disregard the old qualification.
4. Re-inspect when needed and verify that the service owner's approval is for the exact candidate and digest, names the configured service owner, and has a later approval sequence than the qualification sequence. The approval must cover this qualification sequence. Missing, stale, mismatched, or invented approval blocks promotion but does not block inspection or qualification.
5. If those gates match, promote with the request's stable request ID:

   `python3 <environment-path>/release_tool.py --state <state.json> promote --candidate <candidate-id> --request-id <request-id>`

   Never retry a timed-out or otherwise uncertain state-changing call immediately. First query:

   `python3 <environment-path>/release_tool.py --state <state.json> request-status --request-id <request-id>`

   An existing matching result confirms the recorded promotion effect. If no result is recorded, inspect state and reconcile candidate, digest, and production before deciding whether a retry is safe. Reuse the same request ID for an exact retry; never reuse it for another candidate or digest. Stop and report if the identifier is unavailable or belongs to another candidate.
6. After confirmed promotion, run both production checks:

   `python3 <environment-path>/release_tool.py --state <state.json> probe`

   `python3 <environment-path>/release_tool.py --state <state.json> checkout`

   Confirm each result is for the promoted candidate and digest and has `ok: true`. A healthy probe does not establish checkout success. If either check fails, report that the release is not fully successful and include the failing evidence; do not claim success or perform unrelated remediation.

## Reporting

Separate observed evidence from interpretation. State the candidate and digest, qualification result and sequence, approval basis (or the exact missing/mismatched field), promotion result or its uncertainty, and each post-promotion check. Conclude distinctly as one of: promoted and verified (both checks pass), promotion blocked (with the gate), or promotion/production outcome unconfirmed or failed (with follow-up). Preserve nonzero tool results and timeout information; a blocked or failed release is not an achieved release.

## Boundaries

- Do not access external repositories, deployment services, customer data, or live production through this workflow.
- Do not modify the state file except through the supplied release-tool operations, and do not fabricate request IDs, approvals, qualification, or health evidence.
- Do not promote a newly changed candidate using an older approval or qualification.
- Qualification and assessment may proceed without approval; promotion may not.
- If the state changes between inspection and a gated operation, re-inspect and re-evaluate all exact-match conditions before any further state-changing call.
