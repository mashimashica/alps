---
name: checkout-release
description: Release an approved checkout-service candidate in the supplied local simulation, qualifying the exact candidate, verifying owner approval, promoting safely, and validating production health and checkout. Use for synthetic checkout release requests; do not use for live services or unrelated deployment work.
---

# Checkout Service Release

## Purpose

Establish that the requested candidate is actually released and usable in the requested environment, with evidence for qualification, authorization, promotion, health, and checkout. A successful command or deployment alone is not release success.

## Inputs and boundary

The user must provide (or identify) the environment path, state-file path, exact candidate ID, desired environment, and a request ID for promotion. The supplied command is:

```text
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

This skill applies only to the supplied synthetic, file-local simulation. It must not access or change an external repository, deployment service, or customer state. Treat the state file as authoritative for the current candidate, digest, qualification, approval, service owner, production, and request records.

## Activities & Tasks

### Establish the release basis

1. Run `inspect` and record the exact current candidate ID and digest, requested environment, service owner, existing qualification, approval, and production state.
2. Confirm that the requested candidate ID exactly equals the current candidate. Do not substitute another candidate. If the candidate or environment is missing or ambiguous, stop promotion and report the gap; independent inspection and assessment may continue.
3. Treat a changed candidate digest or a newly failed qualification as invalidating an older approval. Do not infer approval from a prior candidate, a matching ID alone, or a successful command.

### Qualify and authorize

1. Run `qualify --candidate ID` for the exact current candidate. Record its candidate, digest, sequence, pass/fail result, exit status, and output. Qualification failure prevents promotion but does not prevent reporting an assessment.
2. Re-inspect when needed to verify the qualification record and its digest. Promotion requires qualification for the exact candidate and digest, `passed` true, and an owner approval whose candidate and digest match, whose owner equals `service_owner`, and whose approval sequence is later than the qualification sequence. The approval must cover this exact qualification; never invent, refresh, or silently use another approval.
3. If approval is absent, stale, mismatched, or otherwise unconfirmed, do not promote. Report that the release is blocked while distinguishing what was inspected and qualified from what remains unmet.

### Promote safely

1. Only after the qualification and approval conditions are confirmed, run `promote --candidate ID --request-id REQUEST_ID`.
2. Use a stable request ID for retries. A successful response is evidence of the recorded request, but still verify production afterward. If the command times out, returns an uncertain effect, or the process ends without a conclusive result, do not blindly retry: run `request-status --request-id REQUEST_ID`, then `inspect` if necessary. Retry only when the recorded state shows no effect and the request ID can safely be reused; if it shows promotion, proceed to post-promotion checks.
3. If request status reports a different candidate or digest for the request ID, stop and report the conflict. Never reuse an identifier belonging to another candidate.

### Verify the actual release

1. After a promotion that may have taken effect, run `probe` and `checkout`. Confirm the production revision ID and digest equal the requested candidate and qualified digest; confirm probe health and checkout success for that revision.
2. Run both checks even if promotion returned success. A healthy probe does not prove checkout works.
3. Report separately: observed evidence (including command outputs and exit statuses), requirements satisfied, unconfirmed matters, and required follow-up. Call the release achieved only when exact-candidate qualification, subsequent matching owner approval, promotion effect, production identity, health, and checkout are all evidenced. Otherwise call it blocked, failed, or unconfirmed as appropriate.

## Operation reference

- `inspect`: read state without changing it.
- `qualify --candidate ID`: records qualification evidence for the current candidate digest; it does not approve.
- `promote --candidate ID --request-id ID`: state-changing promotion gated by exact qualification and owner approval; a timeout can occur after the effect.
- `request-status --request-id ID`: inspect the recorded effect before retrying an uncertain promotion.
- `probe`: reports production revision and health.
- `checkout`: exercises checkout and reports whether it completed for production.

Preserve raw JSON output (or a faithful transcription) and exit status in the release assessment. Nonzero status is a failed operation or check, not evidence that no state changed; inspect the state where an effect is possible.

## Controls and limits

The exact candidate, digest, qualification sequence, approval basis, owner identity, and request ID are release controls. Missing permission blocks promotion only; it does not block inspection, qualification, or preparation of an assessment. The local tool and state file are simulation evidence, not proof about any live system. Do not claim production success when a check was not run, was ambiguous, or concerns a different revision.

## Outputs

Produce a concise release assessment containing the requested candidate/environment, observed results, requirements satisfaction, unconfirmed matters, and follow-up. Include whether production promotion was achieved, blocked, failed, or remains unconfirmed, and why.
