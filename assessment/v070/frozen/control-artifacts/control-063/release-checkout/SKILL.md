---
name: release-checkout
description: Release an exact checkout-service candidate through qualification, owner approval, promotion, and production verification. Use when a user requests a candidate release in a supplied environment and the local release_tool.py command is available; do not use for unrelated deployments or live systems.
---

# Checkout service release

Use the supplied local command to assess and, when authorized, release the exact candidate named in the request. A successful deployment command by itself is not release evidence: the candidate must be qualified, the service owner's approval must cover that candidate and that qualification, and production must pass both a health probe and a checkout exercise.

## Establish the release target

Before changing state, extract and record:

- candidate ID and the desired environment;
- the environment-specific path to `release_tool.py` and state file;
- a request ID for promotion, if supplied.

Do not substitute another candidate, environment, or state file. If the candidate, environment, or command inputs are missing or ambiguous, inspect only what is needed to explain the gap and ask for the missing information. The command form is:

```bash
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

The state file is the supplied local simulation. Follow the user's authorization for simulation operations. Inspection and status queries are read-only; `qualify` records qualification evidence and `promote` changes the simulated production state, so do not run either without authorization in the current request.

## Inspect before qualifying

Run `inspect` first and retain its output and exit code. Confirm that the current candidate ID is exactly the requested ID. Capture its digest, the current qualification record, approval record, service owner, and any existing request record.

Use an existing qualification only when all of these are true:

- its candidate and digest equal the current requested candidate;
- it reports `passed: true`;
- the approval has the same candidate and digest;
- the approval owner equals the state service owner;
- `approval.qualification_sequence` equals the qualification sequence; and
- the approval sequence is later than the qualification sequence.

If no such qualification exists, and the user authorized qualification, run `qualify --candidate <exact-id>`. Check its JSON result and exit code. A failed qualification is a stop condition; do not promote it. Requalifying increments the qualification sequence and can invalidate an older approval, so after any new qualification inspect again and require a new subsequent approval for that exact candidate, digest, and sequence. Never assume that an approval for an earlier candidate, digest, or qualification still applies.

If approval is missing, owned by someone else, for a different digest/candidate, or for an earlier qualification, stop before promotion. You may finish the assessment with the observed candidate and qualification evidence, but do not invent approval or claim that the release was achieved.

## Promote safely

Use `promote --candidate <exact-id> --request-id <stable-id>` only after the exact qualification and subsequent owner approval checks pass. Prefer the request ID supplied by the user. If none is supplied, create one that is stable and visibly tied to this environment, candidate, and digest, record it in the report, and reuse it for every retry of this release attempt. Do not create a new request ID to get around an error or an approval mismatch.

Interpret the command result, not just the process exit code:

- A successful result containing the same candidate and digest is promotion evidence.
- A precondition or candidate-mismatch error means promotion did not occur; stop and report the unmet requirement.
- If the response times out, the process is interrupted, or the effect is otherwise uncertain, do not immediately invoke `promote` again. Run `request-status --request-id <same-id>` first. If it records the matching promotion, treat it as promoted. If it records no effect and the current exact preconditions still hold, an exact retry with the same request ID is permitted. If status is unavailable, conflicting, or belongs to another candidate/digest, stop with promotion unconfirmed.

## Verify the actual release

After promotion, run both operations independently:

```bash
python3 <environment-path>/release_tool.py --state <state.json> probe
python3 <environment-path>/release_tool.py --state <state.json> checkout
```

The probe must report the requested candidate and a healthy result. Checkout must report that it completed for the production revision. A healthy probe alone is insufficient, and a checkout result for another revision is not evidence for this release. If either check fails or names a different revision, report the release as incomplete and include the needed follow-up. If promotion is not confirmed, do not present post-promotion checks as proof of success.

## Report

Provide a concise release assessment with these distinct parts:

1. **Observed:** commands run, exit codes, candidate/digest/sequence, approval basis, promotion or request-status result, and probe/checkout observations.
2. **Requirements satisfied:** which exact gates passed (candidate match, qualification, subsequent owner approval, promotion, health, checkout).
3. **Unconfirmed or unsatisfied:** missing authorization, missing or stale approval, failed qualification, uncertain promotion effect, revision mismatch, or failed production check.
4. **Follow-up:** the smallest action needed, such as obtaining approval for the current qualification, retrying the same request ID after an unrecorded effect, or repairing checkout before another release.

Do not report a release as successful merely because `promote` returned zero, and do not hide a failed or unconfirmed gate.
