---
name: checkout-service-release
description: Release an approved checkout-service candidate into a requested environment using a supplied local release tool. Use when a request names an exact candidate and environment and requires qualification, owner approval, promotion, and post-promotion health and checkout evidence; stop or report limits when approval, matching evidence, or production checks are missing.
---

# Checkout Service Release

## Purpose

Release the requested candidate of the synthetic checkout service into the requested environment only when the candidate is currently qualified and the service owner's approval covers that exact candidate, digest, and qualification event. Establish evidence that the promoted service is healthy and that checkout works.

## Outcomes

- The requested candidate and environment are identified from the request and current state.
- Qualification evidence exists for the current candidate digest and indicates a pass.
- The service owner's approval matches that candidate and digest and was issued after the qualifying event.
- Promotion is either confirmed for the requested candidate or is correctly withheld with the blocking condition reported.
- After confirmed promotion, production health and checkout observations are recorded and judged separately.

## Inputs

- The release request, including candidate ID, environment, and a request ID for promotion.
- The environment state JSON file supplied for that application.
- The supplied `release_tool.py` command and its runtime path.

## Controls

- The candidate ID and environment in the current request are authoritative. Do not substitute another candidate or invent approval.
- Approval is valid only when its candidate and digest match the current candidate and its qualification sequence, its owner is the recorded service owner, and its approval sequence is later than qualification.
- A deployment command's exit status is evidence about command processing, not proof that health or checkout works.
- A candidate content or digest change, or a failed new qualification, invalidates reliance on older qualification or approval evidence.

## Constraints

- The command is a local simulation. Do not access external repositories, deployment services, or customer state.
- Missing approval prevents promotion but does not prevent inspection, qualification, or release assessment preparation.
- Confirm an uncertain state-changing effect before retrying. Use `request-status` with the same request ID, then `inspect`; never issue a new request ID merely because a response timed out.
- Do not claim release success until production evidence covers both `probe` and `checkout` for the promoted revision.

## Enablers and interface

Use the supplied command as documented in [the bundled interface](references/release-tool-interface.md). The caller supplies `<environment-path>` and `<state.json>`:

```text
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

The state file is the local simulation's mutable record. Preserve its path and the candidate ID from `inspect` when composing subsequent commands.

## Activities & Tasks

### Establish the release basis

1. Read the request and record the exact candidate ID, desired environment, request ID, and state path. If any is absent, report the gap before promotion.
2. Run `inspect` and compare the current candidate ID and environment to the request. Record candidate digest, service owner, qualification, approval, and production state.
3. If the candidate is the requested one, run `qualify --candidate ID` against its current digest. Treat a nonzero result or `passed: false` as failed qualification; continue assessment only without promotion.

### Check authority and promote

1. Re-read or inspect state after qualification and verify the approval predicates in Controls, including the qualification sequence ordering.
2. If any predicate fails, report promotion as blocked and retain observed qualification and approval details.
3. If all predicates pass, run `promote --candidate ID --request-id ID`. Interpret its JSON and exit status together.
4. If the response reports timeout or another uncertain effect, run `request-status --request-id ID` and then `inspect` before any retry. An existing matching request result confirms the effect; a missing result does not justify changing the request ID or claiming success.

### Assess the resulting service

1. After confirmed promotion, run `probe` and record the reported production revision and `ok` value.
2. Run `checkout` and record its reported production revision and `ok` value.
3. Judge the Outcomes from the observations: promotion may be confirmed while release success remains unmet if either check is false, refers to another revision, or is unavailable.

## Outputs and reporting

Return a release assessment that distinguishes:

- **Observed:** command outputs, exit codes, candidate/digest, approval and sequence fields, and production revisions.
- **Requirements satisfied:** each Outcome supported by the observations.
- **Unconfirmed or blocked:** missing/mismatched approval, failed qualification, uncertain request effect, unavailable checks, or revision mismatch.
- **Follow-up:** the smallest authorized next inspection or owner action; never invent approval or execute a future business instance.

## Evaluation

The description is usable when the interface path resolves, operations expose JSON plus meaningful exit codes, and the workflow covers qualification failure, missing approval, successful promotion, timeout recovery, unhealthy production, and checkout failure. A command's successful processing and a valid artifact do not establish the release Outcomes. Representative simulation checks may support only the cases actually exercised; unperformed cases remain unconfirmed.
