---
name: checkout-service-release
description: Release an explicitly identified checkout-service candidate to a requested environment using the supplied local release tool. Use when qualification, service-owner approval, promotion, and production checkout evidence must all be checked; do not use for unrelated deployments or live external systems.
---

# Checkout Service Release

## Purpose

Establish that the requested candidate is safely promoted and that the production service is healthy and can complete checkout. A successful command, approval, or deployment alone is not the outcome.

## Outcomes

- The exact requested candidate is either promoted only when its current digest has passed qualification and has subsequent approval from the service owner for that same qualification, or promotion is correctly stopped with the unmet condition identified.
- After promotion, production evidence identifies the deployed revision and shows both a successful health probe and a successful checkout for that revision; otherwise the release is reported as incomplete or failed.
- Observed results, requirements satisfied, unconfirmed effects, and follow-up actions are clearly distinguished.

## Inputs and conditions

The request must identify the candidate ID and desired environment. Obtain the environment's state-file path and the supplied command path (`python3 <environment-path>/release_tool.py --state <state.json> <operation>`). Treat `inspect` as the source of current candidate, digest, production, qualification, approval, service-owner, and request state.

The candidate ID and digest are a coupled identity. Do not substitute another candidate, infer approval, or treat an older qualification or approval as current after the candidate digest changes. Approval must be from the configured service owner and must refer to the exact candidate and digest, the passed qualification sequence, and a later approval sequence.

## Activities & Tasks

### Establish the release basis

1. Read the request and inspect the state before changing it. Confirm the current candidate ID exactly matches the requested candidate and record its digest, desired environment, service owner, qualification, approval, and any existing request record.
2. If the candidate does not match, stop promotion and report the mismatch. You may still report inspection findings and perform qualification only when the requested candidate is the current candidate.

### Qualify the exact candidate

1. Run `qualify --candidate ID` for the exact current candidate when qualification evidence is missing, stale for the current digest, or otherwise needs to be established. Record the returned candidate, digest, passed flag, and qualification sequence.
2. If qualification fails, stop promotion. Do not invent approval or retry qualification as a substitute for a changed candidate; report the failed evidence and required follow-up.
3. Re-inspect when needed to ensure the candidate digest and qualification still match before relying on approval.

### Check approval and promote

1. Confirm approval covers the exact candidate and digest, names the configured service owner, refers to the passed qualification sequence, and has an approval sequence later than that qualification. Missing or mismatched approval prevents promotion but does not prevent inspection, qualification, or release assessment.
2. Construct a stable request ID for this exact release attempt and run `promote --candidate ID --request-id ID` only after the preceding conditions hold. Record the response and exit status.
3. If promotion returns an error saying approval/qualification is required, stop and report the unmet condition. If a response times out or otherwise leaves the effect uncertain, do not issue a new request ID or blindly repeat promotion. First run `request-status --request-id ID`; if that is inconclusive, inspect state and establish whether production changed before deciding whether an exact retry is safe.
4. An existing request record for the same request ID is evidence for that request only. A request ID tied to another candidate or digest must not be reused.

### Verify production outcomes

1. After a confirmed promotion (or when assessing an already-deployed requested revision), run `probe` and record the production revision and health observation.
2. Run `checkout` and record the production revision and checkout observation. Both checks must refer to the intended promoted revision; a health success does not establish checkout success.
3. Report the release as achieved only when the exact candidate/digest promotion is evidenced and both production checks succeed for that revision. Otherwise report the precise unmet outcome, including any unconfirmed effect, and the necessary follow-up.

## Tool interface and interpretation

Use the supplied command exactly as documented. `inspect` is read-only. `qualify` records qualification evidence and may update local simulation state; a zero exit status means the returned qualification passed, not that approval exists. `promote` changes production when all matching conditions hold; a nonzero timeout may occur after the effect has happened. `request-status` is the recovery lookup for a request ID. `probe` and `checkout` are read-only production observations and may return nonzero when their respective observation is false.

Preserve command output and exit status as evidence. Distinguish tool processing success from the intended release outcome. Never claim production success from a deployment response alone, from a passed qualification, or from an approval record.

## Constraints and reporting

Do not access or change external repositories, deployment services, real customer state, or any live business system. Use only the supplied local simulation and operations authorized by the request. Do not perform a future business instance beyond the requested assessment.

Report, in a compact release assessment:

- requested candidate, environment, and observed digest;
- qualification evidence and sequence;
- approval basis and any missing/mismatched condition;
- promotion response, request ID, and whether its effect is confirmed;
- production probe and checkout evidence, including deployed revision;
- achieved outcomes, unmet requirements, unconfirmed matters, and follow-up.

Do not label an unmet or unconfirmed outcome as successful merely because an intermediate command completed.
