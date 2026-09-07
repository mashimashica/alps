---
name: checkout-service-release
description: Release an exact checkout-service candidate through qualification, owner approval, promotion, and post-promotion health and checkout verification. Use when a user authorizes a simulated or local release with a candidate ID, target environment, state file, and release command; do not treat deployment success alone as release success.
---

# Checkout Service Release

## Purpose

Make the requested candidate available in the requested environment only when the candidate has current qualification evidence and subsequent service-owner approval for the same candidate and digest. Establish whether the resulting production service is healthy and its checkout path works, and report evidence and limits clearly.

## Outcomes

- The requested candidate is either promoted only under matching qualification and approval, or promotion is correctly withheld with the blocking condition identified.
- Production evidence identifies the deployed revision and whether the health probe succeeds.
- Production evidence identifies whether checkout completes for the deployed revision.
- The release result distinguishes observed facts, satisfied requirements, unconfirmed effects, and required follow-up.

## Inputs

- The exact candidate ID and desired environment from the release request.
- The environment path and state-file path supplied for that application.
- Service-owner approval information, including candidate, digest, owner, qualification sequence, and approval sequence, as present in the environment state.
- Authorization for the user-requested simulation operations.

## Enabler and interface

Use the supplied command directly; its form is:

```text
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

Operations are `inspect`; `qualify --candidate ID`; `promote --candidate ID --request-id ID`; `request-status --request-id ID`; `probe`; and `checkout`. Capture stdout, exit status, and (for state-changing operations) the resulting state. Nonzero status is evidence of a failed operation, not proof that no state changed.

## Activities & Tasks

### Establish the release basis

1. Read the supplied request and record the exact candidate ID, desired environment, environment path, state file, and any user-supplied request ID. Do not substitute another candidate or environment.
2. Run `inspect` before qualification or promotion. Confirm the current candidate ID and digest, service owner, prior qualification, approval, and production state. Treat a changed candidate ID or digest as a new basis.
3. If required information is absent or ambiguous, report the gap. Continue independent inspection or assessment, but do not perform a dependent promotion.

### Qualify and assess authority

1. Run `qualify --candidate ID` for the exact current candidate. Record its candidate, digest, pass/fail result, and qualification sequence.
2. Before promotion, verify that qualification passed for the current candidate and digest.
3. Verify that the approval is subsequent to that qualification, names the same candidate and digest, names the configured service owner, and matches the qualification sequence. Approval for another candidate, digest, or earlier qualification is unusable. Never invent, infer, or silently reuse approval.
4. Missing approval blocks promotion but does not block inspection, qualification, or preparation of a release assessment.

### Promote safely

1. If and only if the checks above pass, invoke `promote --candidate ID --request-id ID`. Use a stable request ID for a retry of the same intended promotion.
2. If the command returns an error, first determine whether its effect is uncertain. For a timeout or otherwise ambiguous response, run `request-status --request-id ID` and/or `inspect` before retrying. Do not duplicate a promotion or change the request ID while its effect is unresolved.
3. A request-status record is evidence about that request only. A successful command or request record does not by itself establish a healthy, working release.

### Verify production and report

1. After a confirmed promotion, run `probe` and `checkout`. Record the production revision returned by each and their `ok` observations and exit statuses.
2. Judge release success from the requested candidate being promoted plus successful production health and checkout evidence. A health probe without checkout success is incomplete; a working checkout on the wrong revision does not satisfy the request.
3. Report, separately: observed results and evidence; requirements satisfied; unmet or blocked requirements; unconfirmed matters (including uncertain effects); and necessary follow-up. State checks not performed and why. Do not report a correct stop for missing approval as an achieved production release.

## Controls and constraints

- The request's exact candidate and environment control scope. Candidate content is identified by its current digest.
- Qualification must precede the approval relied upon, and promotion must follow a matching owner approval. Any candidate-content change or new failed qualification invalidates an older approval for dependent promotion.
- Production checks occur after promotion. Do not infer production state from candidate metadata, a deployment command, or approval alone.
- Do not access or modify external repositories, deployment services, or real customer state. Do not manufacture approval or perform an unrequested business action.
- State-changing operations may have partial effects. Reconcile uncertain effects before retrying; an exact supported request ID makes a confirmed retry idempotent.

## Exit assessment

The release is complete only when the intended candidate is confirmed in production and both `probe` and `checkout` provide successful evidence for that production revision. Otherwise return the strongest supported partial result and the next safe action; keep unconfirmed conditions explicit.
