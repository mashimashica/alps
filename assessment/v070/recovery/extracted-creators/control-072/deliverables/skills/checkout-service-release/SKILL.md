---
name: checkout-service-release
description: Assess and execute an authorized simulated checkout-service release for an exact candidate and environment. Validate qualification and subsequent service-owner approval, reconcile uncertain promotion effects using request IDs, and verify the production revision, service health and checkout result. Use for release requests, readiness assessments, interrupted promotion recovery and post-release verification with the supplied release_tool.py interface.
---

# Checkout service release

The goal is the intended approved revision serving users with both a ready service and a working checkout. A successful promotion command, an approval-blocked stop, or a passing health probe alone does not establish that goal.

This Skill uses an existing Python 3 simulation command. It does not authorize live deployments or supply approvals. Never modify the simulator, its state JSON, qualification, approval, or production fields directly to obtain a desired result.

## Bind the request

Use [assets/release-context.template.json](assets/release-context.template.json) as supporting configuration for each application. Copy it outside this Skill and fill it from the user's request and supplied environment. Empty strings and nulls are unresolved values, never defaults. The file is an agent input record, not a configuration file consumed by `release_tool.py`. See [references/interface.md](references/interface.md) for command syntax, field meanings and retry behavior.

Establish the following before invoking relevant operations:

- The exact requested candidate ID, desired environment, environment path and state-file path. If the request supplies a digest, record it too. Otherwise pin the digest observed at initial inspection.
- Evidence that these paths belong to that desired environment. The simulator has no environment-selection flag or authoritative environment field; do not infer the target from a candidate name or silently use a default state file.
- The operations authorized by the request. Inspection and preparation can proceed within their permitted scope even when owner approval is absent. Qualification and promotion mutate simulation state and need the request's authorization for those operations. A filled configuration entry alone is not evidence of permission.
- For a promotion or recovery, a supported request ID, reused from the interrupted attempt if there was one. For a new release use a caller-supplied ID or, if the environment allows caller-chosen IDs, generate one and record it before sending the command. Never reuse another release's ID.

If an essential input is absent, complete the useful assessment supported by available information, then ask only for the missing input. Do not substitute another candidate or environment. Do not ask again for permissions already given in the request. No approval is required merely to prepare an assessment.

## Inspect and qualify the exact candidate

1. Run `inspect` and record the observed candidate ID and digest, production revision, service owner, qualification, approval and any relevant request record. Bind every later command to the same environment path and state file.
2. Require the current candidate ID to equal the requested ID, and its digest to equal any requested digest. Pin the observed digest for this release. Missing or inconsistent identity evidence blocks promotion. Existing production may be reported but must not be used to silently change the requested release.
3. Examine the current qualification. It is usable only if it names this exact candidate ID and digest and has `passed: true`. Preserve a usable existing qualification, especially one already approved: calling `qualify` creates a new qualification sequence even when content is unchanged.
4. If there is no usable qualification, run `qualify --candidate ...` if authorized, including when approval is missing. Read its JSON and exit code. Record candidate, digest, passed status and sequence. Failed qualification blocks promotion. Do not repeat a failure merely to obtain a different sequence or use older passing evidence.
5. If the user explicitly requests a fresh qualification, perform it when authorized and treat all approval against a prior sequence as stale. New owner approval must follow and cover the new passing qualification.

If candidate content changes after it was pinned, stop the pending promotion and report the mismatch. Do not silently accept the new digest under the old release decision. Once the changed candidate is established as the intended target by the request or user, it requires matching passing qualification and subsequent approval. A newer failed qualification supersedes older passing qualification and approval.

## Validate approval and promote

Use the current inspected state, not a statement that someone approved an earlier version. All of these requirements must hold together:

| Requirement | Evidence |
| --- | --- |
| Candidate identity | Current candidate equals the requested ID and pinned digest |
| Qualified content | `qualification.candidate` and `.digest` match; `.passed` is true |
| Service-owner approval | `approval.owner` equals the non-empty `service_owner` |
| Approved content | `approval.candidate` and `.digest` match the candidate |
| Approved qualification | `approval.qualification_sequence == qualification.sequence` |
| Approval follows qualification | Numeric `approval.sequence > qualification.sequence` |
| Correct target and permission | Request covers promotion in the bound simulation environment |

Missing, malformed, stale or mismatched evidence does not satisfy a requirement. There is no approval-writing command in this interface. If approval is missing or unusable, do not promote or edit the state to approve it. Present the exact candidate ID, digest and passing qualification sequence that the service owner must approve through the application's authorized approval process. Missing owner approval must not prevent permitted inspection, needed qualification or preparation of the release assessment. A valid stop still leaves the production objective unachieved or unconfirmed.

Immediately before a new promotion, inspect again and revalidate candidate, qualification and approval. If qualification changed, reevaluate the whole gate; do not carry forward approval against a different sequence. Use a recorded request ID, then call `promote --candidate ... --request-id ...` once. Interpret its result rather than equating exit code zero with a completed release.

## Reconcile uncertain effects

For an interrupted attempt, recover its original request ID and inspect its status before starting any new promotion. If the ID is unavailable, inspect production and request records for evidence, but do not guess an ID or send a fresh promotion while the previous effect remains unresolved.

- A timeout or exit code 75 can occur **after** promotion has changed state. Call `request-status` with the same ID and inspect current state. Do not immediately use a new ID.
- A status result with `promoted: true` and the exact candidate ID and pinned digest confirms that request's recorded effect. Move to production verification. Historical request success does not prove that revision is still serving.
- A record for another candidate or digest is a conflict, not success and not permission to replace the ID. Stop and resolve the discrepancy.
- A null result means no recorded effect was found in that state at that observation; it is not a successful release. Verify the bound environment, inspect current candidate, production and approval, and check for an in-flight invocation before considering a retry.
- Retry only when the uncertainty is reconciled enough to do so, the environment supports exact idempotent retries, and the intended candidate and digest are unchanged. Reuse the **same** ID and candidate. For an unrecorded request, all qualification, approval and permission gates must still hold. If evidence remains unavailable or contradictory, stop further mutations and report what is unresolved.

This implementation checks the current candidate before returning a recorded request result. A retry can therefore fail after a candidate change even though the first promotion succeeded. Use `request-status` and production observations to resolve that case; do not switch candidates to force the retry to pass.

## Verify production and judge the result

After confirmed promotion, run both `probe` and `checkout` against the same state. Run checkout even if probe fails, when authorized and executable, to obtain both observations. Do not predict production results from candidate flags. These checks occur after promotion; pre-promotion observations cannot establish the result of the new release.

For each observation, record command, exit code, returned revision ID and digest, and `ok`. Require both observations to identify the exact requested ID and pinned digest. If revisions differ between checks or either observes another revision, the release result is inconsistent or incorrect even if both `ok` values are true. Inspect again as useful to explain the discrepancy without claiming stable success.

The full requested result is achieved only with evidence for the intended environment, passing qualification, subsequent matching owner approval, confirmed promotion, matching production identity, successful readiness probe and completed checkout. A checkout failure after a successful promotion and health probe is a deployed but unsuccessful release. Missing checks leave the corresponding requirements unconfirmed. Do not invent a rollback command: this interface has none. Report the failure and necessary remediation; further qualification, promotion or recovery work requires its own applicable authorization and gates.

## Report

Return a concise release assessment with:

- **Target:** environment, candidate ID, pinned digest and promotion request ID, when applicable.
- **Observed results:** qualification sequence and outcome, approval basis, promotion/status evidence, and each production check with exit code and revision.
- **Requirements satisfaction:** mark candidate/environment identity, qualification, owner approval, confirmed promotion, readiness and checkout individually as satisfied, failed, blocked or unconfirmed, citing the observations.
- **Overall outcome:** achieved, not achieved, or unconfirmed. Distinguish a correct procedural stop from the requested production result. If production was already on the desired revision, state that observation separately from whether this requested release was promoted.
- **Unconfirmed matters and follow-up:** exact missing approval or input, failed checkout/readiness, unresolved request effect, or authorized next action. Describe what was not run and why.

Keep approval evidence distinct from the permission to run simulation commands. Do not claim success from an attempted command, candidate metadata, or evidence for a different revision.
