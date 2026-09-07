---
name: release-checkout-service
description: Assess, qualify, and promote an exact checkout-service candidate in the supplied local release simulation, then verify both service health and a completed checkout. Use for release or release-readiness requests that provide release_tool.py, a state file, a candidate, and a target environment; never use it to operate a live repository, deployment service, or customer system.
---

# Release Checkout Service

Use the supplied file-local command to make a release decision from evidence, not merely from a successful promotion command. The intended result is the exact approved revision running in the requested environment, with both the service probe and checkout path succeeding.

## Establish scope and authorization

Identify all of the following before changing the simulation:

- the exact requested candidate ID;
- the desired environment and the environment path/state file representing it;
- whether the request authorizes qualification, promotion, or assessment only;
- any promotion request ID supplied for a new attempt or a resumed attempt.

Do not guess a state file, environment, candidate, approval, or request ID from another release. A clear instruction to release or promote an exact candidate in an exact supplied simulation can authorize the normal qualification and promotion operations needed for that request. Readiness, inspection, or assessment language does not authorize a state-changing operation. If the scope is ambiguous, inspect and prepare the assessment, then ask before the first state change.

User authorization to operate the simulation and service-owner approval are separate requirements. Neither substitutes for the other. Never access a live repository, deployment service, or customer state through this skill.

## Use the local interface

Invoke:

```text
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

Supported operations are:

```text
inspect
qualify --candidate <candidate-id>
promote --candidate <candidate-id> --request-id <request-id>
request-status --request-id <request-id>
probe
checkout
```

Treat command output and exit status as evidence together. In particular, a failed `qualify` records new failed qualification evidence before returning nonzero. Preserve and interpret its JSON output rather than discarding it because of the exit status.

Quote filesystem paths and user-provided values safely when invoking the command. Do not add a wrapper unless the current environment genuinely needs an additional capability.

## Inspect the release basis

Run `inspect` first. Compare the requested candidate ID with `candidate.id` and record the current `candidate.digest`. Stop before qualification or promotion if the ID does not match; do not silently release the current candidate instead.

A qualification is current only when all of these hold:

- `qualification.candidate` equals the requested candidate;
- `qualification.digest` equals the current candidate digest;
- `qualification.passed` is true.

An approval is usable only when all of these hold:

- the qualification above is current and passing;
- `approval.candidate` and `approval.digest` match that exact qualification and current candidate;
- `approval.owner` equals `service_owner`;
- `approval.qualification_sequence` equals `qualification.sequence`;
- `approval.sequence` is later than `qualification.sequence`.

A matching candidate ID alone is insufficient. Changed content invalidates qualification and approval. A new qualification creates a new sequence, so even a successful re-qualification makes an older approval unusable. Do not re-run qualification when an existing current passing qualification and its subsequent matching approval are already valid unless the user specifically requested re-qualification and understands that a fresh approval will then be required.

## Qualify when needed

If no current passing qualification exists and qualification is authorized, run `qualify` against the exact requested candidate.

- On failure, stop promotion. Report the failed qualification, its candidate, digest, and sequence. Any older approval is unusable.
- On success, re-inspect state. Unless there is now a subsequent matching owner approval for that exact qualification sequence, stop and request that approval. The local tool does not create or infer approval.
- If qualification is not authorized, report it as a blocking requirement rather than performing it.

Missing approval does not block inspection, an authorized qualification, or preparation of a release assessment. It always blocks promotion.

## Promote idempotently

Immediately before promotion, re-inspect if the state may have changed. Recheck candidate ID and digest, passing qualification, matching subsequent owner approval, target state file, and promotion authorization.

Use one request ID for one environment/candidate/digest promotion intent. If the user supplied an ID, retain it. Otherwise create a unique, non-secret ID, record it in the response, and reuse it for every retry or status check for this intent. Never recycle it for changed candidate content or another environment.

When resuming an attempt or whenever the promotion response is missing, times out, cannot be parsed, or otherwise leaves its effect uncertain:

1. Do not issue a promotion with a new request ID.
2. Run `request-status` with the original request ID.
3. If it records the matching candidate and digest as promoted, treat the mutation as confirmed and continue to production checks.
4. If it records a conflicting candidate/digest or an error, stop and report the conflict.
5. If no effect is recorded and promotion remains authorized, an exact retry may use only the same request ID. Check status again after any further uncertainty.

A successful promotion response or confirmed request record proves promotion, not release success.

## Verify the production outcome

After a confirmed promotion, run both `probe` and `checkout`. For each result, verify that the reported production revision has the requested candidate ID and qualified digest; then require `ok: true`.

Call the intended release **achieved** only when all of the following are observed:

- promotion of the exact requested candidate and digest is confirmed;
- the production probe reports that exact revision and succeeds;
- checkout reports that exact revision and completes successfully.

A healthy probe with failed checkout is a failed production outcome, not a successful release. Likewise, successful checks against a different revision do not confirm this release. Do not attempt an unrequested rollback or other remediation; report the observed failure and the necessary follow-up.

## Report evidence and status

Keep these categories distinct:

- **Observed:** exact command evidence, including candidate/digest, qualification sequence/result, approval match, request ID and promotion status, production revision, probe, and checkout.
- **Requirements satisfied:** which candidate, approval, promotion, health, and checkout requirements are proven.
- **Unconfirmed or blocked:** missing authorization, missing or stale approval, candidate drift, uncertain promotion effect, missing check, or conflicting evidence.
- **Follow-up:** the precise approval, authorization, status check, remediation, or rerun needed.

Use an overall status that reflects the outcome:

- **Achieved** only for the fully verified production result above.
- **Not achieved** when promotion was not performed or a prerequisite failed.
- **Production failure** when the exact revision was promoted but health or checkout failed.
- **Unconfirmed** while the promotion effect or required production evidence remains unresolved.

A safe stop is a correct handling decision, but it does not make the intended production result achieved.
