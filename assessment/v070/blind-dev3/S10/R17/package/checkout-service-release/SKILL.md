---
name: checkout-service-release
description: Safely qualify and promote an identified checkout-service candidate in the supplied state-file release simulation, then verify production health and checkout. Use for release requests that name a candidate and environment; do not use for unrelated deployment or live customer operations.
---

# Checkout service release

## Purpose

Release the requested checkout-service candidate to its requested environment only when the exact candidate has passed current qualification and the service owner's approval covers that candidate, digest, and qualification sequence. Establish whether the resulting production service is healthy and its checkout path works.

## Outcomes

- The requested candidate and environment basis, including its digest and current approval state, are recorded from inspection.
- The exact current candidate has a recorded qualification result, and promotion is attempted only when qualification passed and a subsequent matching owner approval exists.
- If promotion is attempted, its effect is resolved without duplicating a state-changing request when the response is uncertain.
- Production health and checkout are probed after promotion, and the release judgment distinguishes observed evidence, satisfied requirements, unconfirmed matters, and follow-up.

## Inputs and controls

The user request supplies the exact candidate identifier, desired environment, state-file location, and authorization for simulation operations. The local `release_tool.py` is the available interface. Its state JSON is the source for candidate, digest, qualification, approval, service owner, production, and request records. The owner approval must be for the same candidate and digest, must identify the configured service owner, and must have a qualification sequence later than the qualification being used. A changed candidate digest or a newly failed qualification invalidates an older approval basis.

Do not invent approval, substitute another candidate, or treat a successful command, health probe, approval, or output file as proof of the whole release. Missing approval blocks promotion only; inspection and qualification may still proceed. Keep all operations within the supplied local simulation and the user-authorized environment.

## Procedure

1. Resolve the supplied environment path, state path, requested candidate ID, and requested environment. If any is missing or ambiguous, report the gap before a state-changing operation.
2. Inspect the state:

   ```bash
   python3 <environment-path>/release_tool.py --state <state.json> inspect
   ```

   Record the current candidate ID and digest, service owner, approval fields, existing qualification, and production state. Confirm that the inspected candidate is the one named in the request. Do not silently use the production revision or an alternative candidate.
3. Qualify the exact current candidate, even if an older qualification exists:

   ```bash
   python3 <environment-path>/release_tool.py --state <state.json> qualify --candidate <candidate-id>
   ```

   Treat a nonzero result or `passed: false` as a failed qualification. It is evidence about this candidate's current digest and does not grant approval. Reinspect if the command reports a candidate mismatch or if the candidate content may have changed.
4. Reinspect the state after qualification and compare candidate ID, digest, qualification sequence, and approval. Promotion is permitted only if the qualification passed and approval has the same candidate and digest, `owner` equals the configured service owner, and `approval.sequence` is greater than `qualification.sequence` (with `approval.qualification_sequence` equal to that qualification sequence). If these checks fail, stop before promotion and report that the release is not achieved; preserve any useful assessment and follow-up.
5. When the checks pass, create one stable request ID for this release attempt and promote:

   ```bash
   python3 <environment-path>/release_tool.py --state <state.json> promote --candidate <candidate-id> --request-id <request-id>
   ```

   A successful promotion response is only an observation of the tool result; continue to production checks. If the command times out, exits with an uncertain-effect error, or transport status is otherwise unclear, do not issue a new request ID or repeat promotion. Resolve the original request first:

   ```bash
   python3 <environment-path>/release_tool.py --state <state.json> request-status --request-id <request-id>
   ```

   Inspect production as needed to determine whether the requested revision was applied. A recorded request result for the exact candidate and digest makes an exact retry idempotent; never reuse a request ID for different candidate content.
6. After any promotion that may have occurred, run both production checks:

   ```bash
   python3 <environment-path>/release_tool.py --state <state.json> probe
   python3 <environment-path>/release_tool.py --state <state.json> checkout
   ```

   Confirm the reported production revision matches the requested candidate and digest. The release meets its operational result only when the revision is correct, the health probe is successful, and checkout is successful. A healthy probe with failed checkout is a failed release outcome.

## Reporting

Report four clearly labeled parts:

- **Observed:** candidate/digest, qualification result and sequence, approval fields, promotion or request-status result, production revision, health, and checkout evidence.
- **Requirements satisfied:** exact candidate qualification, matching subsequent owner approval, promotion effect, revision match, health, and checkout, each marked only from the observed evidence.
- **Unconfirmed:** any timeout effect, missing or stale approval, changed digest, unavailable probe, candidate mismatch, or other evidence gap.
- **Follow-up:** the smallest authorized next action, such as obtain a fresh owner approval, requalify the changed candidate, resolve an original request ID, or investigate failed checkout. State explicitly when promotion was correctly blocked and therefore the intended production result was not achieved.

## Failure and effect handling

Nonzero qualification, promotion, probe, or checkout commands are meaningful evidence and must be retained in the report. Before retrying a state-changing promotion whose effect is uncertain, query `request-status` with the same request ID and inspect production; never duplicate the mutation merely because a response was lost. If state shows a different candidate or digest after qualification, treat the earlier qualification and approval basis as unusable and return to inspection and qualification.

The local tool's state file is a synthetic simulation. This skill does not authorize access to external repositories, deployment services, or customer state, and it does not claim that simulation evidence proves a live release.
