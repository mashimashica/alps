---
name: checkout-service-release
description: Safely assess and release an approved checkout-service candidate in the supplied local release environment. Use when a user requests a checkout-service promotion, qualification, production verification, or release assessment; it enforces exact candidate and digest matching, owner approval after qualification, idempotent retries, and post-promotion health and checkout evidence.
---

# Checkout service release

Use this procedure for the synthetic checkout-service release tool. Treat the candidate ID and desired environment in the user's request as exact. Never substitute a candidate, invent approval, or claim success from a command exit alone.

## Required inputs

Obtain the per-application environment path, state file, exact candidate ID, desired environment, and a stable request ID for promotion. If any are missing, inspect what is available and report the missing information; do not guess. The command is:

```sh
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

The state file is a local simulation. The user must authorize simulation operations for this request.

## Procedure

1. Run `inspect` first and preserve its output. Confirm the current candidate ID and digest, target/environment, qualification, approval, service owner, and production state. Verify that the requested candidate is the current candidate before acting.
2. Run `qualify --candidate <exact-id>`. Qualification must pass for the current candidate digest. A failed qualification is a stop; report its evidence and do not promote.
3. Re-read or use inspection evidence to verify approval covers the exact candidate and digest, is from the service owner, and has a sequence later than this qualification sequence. Approval for another digest, candidate, owner, or an earlier qualification is unusable. Missing approval prevents promotion but does not prevent inspection, qualification, or preparing an assessment.
4. If the checks pass, run `promote --candidate <exact-id> --request-id <stable-id>`. Use the same request ID for retries. A successful result is evidence of the request effect, but production still requires verification.
5. If promotion returns a timeout or otherwise says its effect is unconfirmed, do not repeat with a new request ID. Run `request-status --request-id <stable-id>` and then inspect; determine whether the recorded request promoted the exact candidate. If status is absent or ambiguous, report promotion as unconfirmed and stop before another mutation.
6. After a confirmed promotion, run both `probe` and `checkout`. Both must report the promoted revision (matching candidate and digest), with health and checkout success. A healthy probe alone does not establish a working checkout.

## Reporting

Report separately:

- observed command outputs, exit codes, candidate/digest, approval basis, request ID, and production revision;
- requirements satisfied (qualification, owner approval, promotion confirmation, healthy probe, working checkout);
- unconfirmed or failed matters, including missing/invalid approval, stale qualification, timeout, revision mismatch, or failed checkout;
- the precise follow-up needed.

Distinguish a correct stop from an achieved release. Never conceal a nonzero exit, treat a timeout as success, or claim production success without both post-promotion checks. Preserve supplied inputs and state unless the requested `qualify` or `promote` operation is authorized.

## Interface reference

Supported operations are `inspect`, `qualify --candidate ID`, `promote --candidate ID --request-id ID`, `request-status --request-id ID`, `probe`, and `checkout`. Qualification and promotion can mutate the local simulation state. Promotion is guarded by exact candidate/digest qualification and subsequent matching service-owner approval; a supported request ID makes an exact retry idempotent.
