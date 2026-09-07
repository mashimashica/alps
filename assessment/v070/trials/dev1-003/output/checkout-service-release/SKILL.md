---
name: checkout-service-release
description: Release an explicitly identified checkout-service candidate into a requested environment using the supplied local release CLI. Use when a user authorizes candidate inspection, qualification, promotion, and post-promotion health and checkout verification; do not use for unrelated deployments or live services.
---

# Checkout-service release

## Purpose

Make the requested candidate the production revision only when its qualification and the service owner's approval are exact and current, then establish production evidence for both service health and checkout. A successful command, approval, or health probe alone is not release success.

## Required inputs and authority

Obtain from the request: the exact candidate ID, desired environment, state-file path, environment path containing `release_tool.py`, and a stable request ID for promotion. Treat the request's authorization as applying only to the named simulation and operations. Do not invent a candidate, approval, owner, request ID, or environment; if any required input is absent, report the gap and stop before state-changing operations.

Run the supplied command as:

```sh
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

The state file is a local simulation. Preserve its output and exit status as evidence. Do not access external repositories, deployment systems, or customer state.

## Activities & Tasks

### Establish the release basis

1. Inspect the state before changing it:

   ```sh
   python3 <environment-path>/release_tool.py --state <state.json> inspect
   ```

2. Confirm that the current candidate ID is exactly the requested ID. Record its digest and the service owner. Treat a changed candidate or digest as a new basis.
3. Check existing qualification and approval evidence. Approval is usable only when it names the exact candidate and digest, names the current service owner, and its `qualification_sequence` is later than the qualification sequence it covers. Do not infer approval from a matching name, an old approval, or a successful inspection.

### Qualify and decide promotion

1. Qualify the exact current candidate, even if prior evidence exists, when the request requires current qualification or when candidate state has changed:

   ```sh
   python3 <environment-path>/release_tool.py --state <state.json> qualify --candidate <candidate-id>
   ```

2. Continue only if qualification reports the exact candidate and digest with `passed: true`. A failed qualification is a stop for promotion, but inspection and release assessment may continue.
3. Re-check that the owner's approval covers that exact qualification and candidate. Qualification does not approve the candidate. Missing, stale, mismatched, or unconfirmed approval prevents promotion.
4. If promotion is authorized and all conditions match, invoke it with the stable request ID:

   ```sh
   python3 <environment-path>/release_tool.py --state <state.json> promote --candidate <candidate-id> --request-id <request-id>
   ```

   Do not substitute another candidate or silently retry with a new request ID.

### Handle uncertain effects and verify the result

1. A nonzero result, timeout, interrupted connection, or message saying the effect is unconfirmed is not proof that no change occurred. Before retrying promotion, query the same request ID:

   ```sh
   python3 <environment-path>/release_tool.py --state <state.json> request-status --request-id <request-id>
   ```

   Inspect state as needed. Retry only with the same request ID and only if status and state establish that promotion did not take effect and the exact preconditions still hold. An existing recorded result for a different candidate or digest is a conflict and must stop.
2. After a confirmed promotion (or when assessing an already promoted requested revision), run both production checks:

   ```sh
   python3 <environment-path>/release_tool.py --state <state.json> probe
   python3 <environment-path>/release_tool.py --state <state.json> checkout
   ```

3. Judge release success only when production reports the requested candidate and digest, `probe` reports `ok: true`, and `checkout` reports `ok: true`. A healthy service with failed checkout is not successful; neither is checkout evidence for another revision.

## Reporting

Return a concise release assessment with separate sections or labels for:

- **Observed:** candidate/digest, qualification evidence, approval fields, promotion/request status, production revision, probe, and checkout outputs (including exit status).
- **Requirements satisfied:** only conditions directly supported by those observations.
- **Unconfirmed or unmet:** missing approval, failed qualification, mismatches, uncertain effects, stale evidence, or failed checks.
- **Follow-up:** the next authorized action, such as obtaining owner approval or requalifying a changed candidate.

Do not report a prepared assessment, successful qualification, approval, or command completion as production release success. State explicitly when promotion was correctly withheld because permission or evidence was missing.

## Controls and limits

- Candidate identity and digest are immutable release-basis fields for this run; any change invalidates earlier qualification and approval.
- Qualification must precede the approval that covers it; an approval sequence must be later than the qualification sequence.
- Promotion may change the local state file. Use the request ID to make exact retries idempotent and to resolve uncertain effects.
- Production checks are post-promotion evidence and must be interpreted against the requested revision.
- This skill does not grant authority. User authorization and the supplied simulation are prerequisites; no live production action is implied.
