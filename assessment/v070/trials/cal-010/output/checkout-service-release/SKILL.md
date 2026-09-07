---
name: checkout-service-release
description: Safely qualify and promote an exact checkout-service candidate in the supplied local release simulation, then verify production health and checkout. Use for release requests that name a candidate, environment, and approval context; do not use for live deployments or unrelated repository work.
---

# Checkout-service release

Operate only on the release environment and state file supplied by the user. The bundled command is:

```text
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

The state file is a local simulation. The user must authorize simulation operations for the current request; this skill does not grant permission for live systems.

## Required workflow

1. Parse the request's exact candidate ID, desired environment, state path/environment path, request ID (or obtain one if the caller permits), and approval basis. Do not substitute a candidate, environment, or approval.
2. Run `inspect` before mutating anything. Record candidate ID and digest, qualification, approval, service owner, production, and any relevant sequence/request data.
3. Confirm the request's candidate is the current candidate. If it is not, stop and report the mismatch.
4. Run `qualify --candidate ID` for that exact candidate. A nonzero result is a failed qualification: do not promote. Qualification evidence is tied to the candidate digest and sequence; never reuse evidence from a different digest.
5. Re-inspect if needed and verify the owner approval covers the exact candidate and digest, is for this qualification sequence, and is subsequent to qualification. Missing, stale, different-owner, or mismatched approval blocks promotion but does not block inspection or qualification reporting.
6. Only when those checks pass, run `promote --candidate ID --request-id ID`. Use a stable request ID for retries. Never retry with a new request ID merely because the command timed out.
7. If promotion returns a timeout or otherwise leaves its effect uncertain, run `request-status --request-id ID` and then `inspect`; do not duplicate promotion. Treat the request as promoted only when state evidence confirms it.
8. After confirmed promotion, run both `probe` and `checkout`. A successful deployment command, or a healthy probe alone, is insufficient. The release is successful only if production identifies the intended candidate/digest, the probe is healthy, and checkout succeeds for that production revision.

## Reporting

Separate:

- observed results (command outputs, exit status, candidate/digest, sequences, and production evidence);
- requirements satisfied or not satisfied;
- unconfirmed matters (including timeout effects, absent evidence, or unavailable state);
- required follow-up.

Never claim promotion or release success from intent, approval alone, a successful command, or a health probe alone. A correct stop for missing approval is not an achieved production release. Preserve command output and nonzero statuses for the caller; do not edit supplied environment files or invent approval.

## Operations reference

- `inspect`: read all state without changing it.
- `qualify --candidate ID`: qualify the current exact candidate and record digest-bound evidence; it does not approve.
- `promote --candidate ID --request-id ID`: promote only with matching passed qualification and subsequent service-owner approval.
- `request-status --request-id ID`: resolve an uncertain promotion request.
- `probe`: check production revision and health.
- `checkout`: exercise checkout for the production revision.
