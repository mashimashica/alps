---
name: checkout-release
description: Qualify and release an exact checkout-service candidate in the supplied local simulation, including owner-approval validation, idempotent promotion recovery, and production health and checkout verification. Use for release execution or readiness assessment when an environment path, state file, candidate ID, and desired environment are provided.
---

# Checkout Release

Release only the requested candidate in the requested local simulation. The goal is the intended revision available with both a ready service and a working checkout. A successful `promote` response or health probe alone does not establish that result.

This skill uses the environment's existing command:

```bash
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

Keep `<environment-path>` and `<state.json>` as separate, explicit values. Do not infer a different environment, candidate, or state file. Never apply this procedure to a live repository, deployment service, or customer environment.

## Establish scope and authority

Identify the desired environment and exact candidate ID from the request. Confirm that the supplied environment path and state file correspond to that environment when the request or surrounding context provides such a mapping. If a required value is missing or conflicting, inspect only when the available path is unambiguous; otherwise ask for the missing value.

`inspect`, `request-status`, `probe`, and `checkout` are observations. `qualify` and `promote` mutate the local simulation. A request to qualify or release a stated candidate in a stated simulation authorizes the mutations needed for that request unless the user narrows the scope. A readiness or assessment request does not authorize mutation. If mutation intent is unclear, prepare the assessment and ask before the first mutation. Service-owner approval is a separate release gate recorded in state; never invent it or treat the user's execution permission as owner approval.

## Inspect and evaluate evidence

Start with:

```bash
python3 <environment-path>/release_tool.py --state <state.json> inspect
```

Record the current candidate ID and digest, production revision, qualification, service owner, approval, and existing promotion requests. Stop rather than substituting a candidate if the current candidate ID differs from the requested ID.

Qualification is current only when it has `passed: true` and its candidate and digest match the current requested candidate. Owner approval is usable only when all of these hold:

- its candidate and digest match that same candidate and digest;
- its `owner` equals `service_owner`;
- its `qualification_sequence` equals the current qualification's `sequence`; and
- its own `sequence` is greater than the qualification sequence.

Do not rerun a passing current qualification that already has usable approval: qualification creates a new sequence and makes the older approval stale. If qualification is absent, failed, or for different content, and qualification is authorized, run:

```bash
python3 <environment-path>/release_tool.py --state <state.json> qualify --candidate <candidate-id>
```

Treat a nonzero exit or `passed: false` as failed qualification. Inspect again after qualification. A new successful qualification still requires a subsequent exact owner approval; because this tool has no approval operation, stop and report the qualification evidence the owner must approve. Missing or stale approval blocks promotion, while still allowing inspection, authorized qualification, and a release assessment.

## Promote exactly once

Immediately before promotion, inspect again and revalidate the candidate digest, passing qualification, and subsequent matching owner approval. Candidate drift, a new failed qualification, or an approval mismatch blocks promotion.

Use one request ID for one environment, candidate, and digest. Prefer a request ID supplied by the user or calling application. Otherwise generate a fresh opaque ID, state it in the record, and retain it for every status check or retry in this attempt. Never reuse it for different candidate content.

With mutation authorized and every gate valid, run:

```bash
python3 <environment-path>/release_tool.py --state <state.json> promote --candidate <candidate-id> --request-id <request-id>
```

If the response is successful and says `promoted: true`, continue to production checks. If the command times out, is interrupted, or otherwise leaves its effect uncertain, do not issue another promotion yet. Resolve the same request first:

```bash
python3 <environment-path>/release_tool.py --state <state.json> request-status --request-id <request-id>
```

A recorded result matching the candidate and digest confirms the promotion effect; continue to checks. A recorded result for other content is a conflict and requires a new assessment, not reuse. If no result is recorded, inspect production and gates. Retry `promote` with the same request ID only when the effect remains absent, candidate content and all gates are still exact, and the original promotion remains authorized. Do not create a new request ID merely because the response was uncertain.

## Verify the production outcome

After confirmed promotion, run both checks independently:

```bash
python3 <environment-path>/release_tool.py --state <state.json> probe
python3 <environment-path>/release_tool.py --state <state.json> checkout
```

The release is achieved only when both commands report `ok: true` and both production revisions match the promoted candidate ID and digest. A promotion with a failed probe, failed checkout, mismatched revision, or unperformed check is not a successful release. Report the observed failure or uncertainty and the follow-up needed; do not claim rollback because the supplied interface has none.

## Report

Separate the result into:

- **Observed:** command results, exit status when relevant, candidate ID and digest, qualification and approval sequences, request ID/status, and production check evidence.
- **Requirements:** whether exact-candidate qualification, exact subsequent owner approval, confirmed promotion, matching production revision, health, and checkout each passed, failed, or remain unconfirmed.
- **Release judgment:** `achieved`, `not achieved`, or `unconfirmed`, with the evidence that controls that judgment.
- **Follow-up:** the smallest concrete next action, such as obtaining approval for a named qualification sequence, fixing qualification or checkout, or resolving an unrecorded request effect.

A correct stop protects the process but does not make the requested production result achieved.
