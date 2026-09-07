---
name: checkout-service-release
description: Release an explicitly identified checkout-service candidate through the supplied local release tool, using current qualification and exact subsequent service-owner approval, then verify production health and checkout. Use for controlled checkout-service release requests; do not use it to operate an unspecified or live external deployment.
---

# Checkout service release

Use this skill for the supplied file-local release environment. The environment is a simulation, but its release gates are meaningful: a successful deployment command alone does not establish that checkout works.

## Inputs and authority

The request must identify the exact candidate ID and desired environment. It must also provide the environment path and state-file path needed by the command:

```text
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

Use the command already supplied for that business application. Do not access a repository, deployment service, or customer state. Do not choose a different candidate or invent an approval. Treat the user's authorization as applying only to the simulation operations it covers. Read-only inspection can be used to prepare an assessment when promotion is not authorized; qualification records evidence in the state file and promotion changes production, so perform them only when authorized.

If the candidate, environment, paths, or authorization scope is missing or ambiguous, report what is missing before any mutating operation. Do not infer a candidate from production or substitute a nearby revision.

## Release procedure

1. Run `inspect` first and record the current candidate ID and digest, production revision, qualification record, approval record, service owner, and sequence values. Confirm that the requested candidate ID is the current candidate. If it is not, stop the release assessment as blocked and report the mismatch.

2. Establish a qualification for the exact candidate. An existing qualification may be reused only when its candidate and digest match the current candidate and it passed. Otherwise run:

   ```text
   qualify --candidate <exact-candidate-id>
   ```

   Record its output and exit code. A failed qualification blocks promotion. A newly recorded qualification has a new sequence and therefore requires a subsequent matching approval; do not treat an older approval as sufficient.

3. Inspect again after qualification (or after deciding that a current passing qualification can be reused). Approval is sufficient only when all of these are true:

   - approval candidate and digest equal the exact qualified candidate and digest;
   - approval owner equals the service owner;
   - approval `qualification_sequence` equals the qualification sequence; and
   - approval sequence is greater than the qualification sequence.

   The digest is part of the identity. If candidate content changed, the digest changed, qualification failed, or a new qualification superseded the approval, the older approval is unusable. Missing or non-matching approval blocks promotion but does not block inspection, qualification, or preparation of the assessment.

4. Before promotion, recheck the candidate and gate records if the environment could have changed since the last inspection. Promote only the exact candidate with one stable request ID:

   ```text
   promote --candidate <exact-candidate-id> --request-id <stable-request-id>
   ```

   Use a request ID supplied by the user or create one unique to this release attempt, then record it and never replace it during recovery. A successful promotion response is evidence of the command result, but production verification still determines whether the release succeeded.

5. If promotion returns a timeout or another response that leaves the effect uncertain, do not issue a new promotion request. First run:

   ```text
   request-status --request-id <same-request-id>
   ```

   Reconcile that result with `inspect`. If the status is unresolved and the interface supports exact request-ID idempotency, any retry must use the same candidate and same request ID; never retry with a new ID. Report the effect as unconfirmed until state or status resolves it.

6. Only after promotion is established, run both production checks:

   ```text
   probe
   checkout
   ```

   Record each JSON result and exit code. Confirm that the reported production revision has the requested candidate ID and digest, `probe` reports healthy, and `checkout` reports completion. A healthy probe without a successful checkout is a failed release outcome. If promotion was blocked or unresolved, do not present checks of an older production revision as evidence for this release.

## Reporting

Give the requester an evidence-based release assessment with four clearly labeled parts:

- **Observed:** operations actually run, relevant JSON fields, and exit codes; distinguish command output from your interpretation.
- **Requirements satisfied:** exact candidate identity, passing qualification, subsequent matching owner approval, established promotion, and both production checks.
- **Unconfirmed or blocked:** missing authorization, candidate/digest mismatch, failed or stale qualification, missing/non-matching approval, timeout, unresolved request status, unhealthy production, or failed checkout.
- **Follow-up:** the smallest authorized action needed to resolve each blocker, such as obtaining approval for the exact qualified digest or investigating a failed checkout.

Do not claim that the intended release was achieved merely because promotion returned code 0, because a health probe passed, or because an approval exists for a different digest or qualification sequence.
