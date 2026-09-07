---
name: checkout-release
description: Qualify and release an exact checkout-service candidate with the supplied release_tool.py simulation, enforcing candidate-bound owner approval, idempotent promotion recovery, and post-promotion health and checkout verification. Use for release requests that provide an environment path, state file, candidate ID, and target environment.
---

# Checkout release

Use the environment and candidate named in the request. Treat paths, candidate IDs, digests, qualification sequences, approvals, and request IDs as exact values. The user's release authorization applies only to the specified local simulation operations; it does not authorize access to an external repository, deployment system, or customer state.

The command interface is:

```bash
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

Quote the environment path and state path when invoking it. Do not edit the state file directly. Use only `inspect`, `qualify`, `promote`, `request-status`, `probe`, and `checkout` through this interface.

## Establish the release basis

Confirm that the request supplies the target environment, environment path, state file, and exact candidate ID. Ask for any missing value that cannot be derived without ambiguity. Keep the requested target visible in the release assessment so that success in a different environment cannot satisfy the request.

Run `inspect` before any mutation. Compare the requested candidate ID with `candidate.id`, and record its digest. Stop promotion if it is not the current candidate. Never substitute another candidate.

Interpret qualification and approval together:

- Qualification is current only when `qualification.candidate` and `qualification.digest` match the inspected candidate, and `qualification.passed` is true.
- Approval is usable only when it matches that same candidate and digest, `approval.owner` equals `service_owner`, `approval.qualification_sequence` equals the current qualification's `sequence`, and the approval `sequence` is greater than the qualification sequence.
- Changed candidate content changes the digest and invalidates earlier evidence. Any newly recorded qualification replaces the previous qualification. A new failed qualification therefore makes an older approval unusable.

Do not run `qualify` merely to refresh already-valid evidence: doing so creates a new qualification sequence and invalidates its approval. If qualification is absent, stale, failed, or the user explicitly requires a fresh run, obtain authorization for this state-changing simulation operation if it is not already covered by the request, then run:

```bash
python3 "<environment-path>/release_tool.py" --state "<state.json>" qualify --candidate "<candidate-id>"
```

After qualification, inspect again. If it failed, stop. If it passed but lacks a subsequent matching service-owner approval, stop before promotion and report the candidate ID, digest, and qualification sequence that require approval. Do not invent approval, write it into the state file, or treat the requesting user's operational authorization as service-owner approval.

Read-only inspection, qualification, and assessment may continue when approval is missing. Missing approval means the intended production result remains unachieved.

## Promote exactly once

Promote only when the current inspection proves the complete basis above and the simulation promotion is authorized. Choose one unique request ID for this release attempt, preferably one supplied by the user; otherwise create a stable, collision-resistant ID and record it before invoking promotion. Use the same request ID for every status check or retry of this exact candidate and digest.

```bash
python3 "<environment-path>/release_tool.py" --state "<state.json>" promote --candidate "<candidate-id>" --request-id "<request-id>"
```

A successful command response is evidence of promotion, but it is not evidence that production works. If the command times out or its effect is uncertain, do not create a new request ID. Query:

```bash
python3 "<environment-path>/release_tool.py" --state "<state.json>" request-status --request-id "<request-id>"
```

If status records the candidate and digest as promoted, continue to production checks. If status has no result, an exact retry with the same request ID is idempotent, but retry only while the original promotion authorization remains applicable and the inspected candidate/digest have not changed. A request ID already bound to different content is an error; stop rather than working around it.

## Verify the user-visible result

After confirmed promotion, run both:

```bash
python3 "<environment-path>/release_tool.py" --state "<state.json>" probe
python3 "<environment-path>/release_tool.py" --state "<state.json>" checkout
```

Release success requires all of the following observed in the requested environment:

- promotion is confirmed for the requested candidate and its inspected digest;
- `probe` reports that same production revision and `ok: true`;
- `checkout` reports that same production revision and `ok: true`.

A healthy probe cannot compensate for failed checkout. A promotion response cannot compensate for either missing production check. Do not describe the release as successful unless all conditions hold.

## Report the assessment

Separate the report into:

- **Observed:** commands or operations performed, exit status, and returned candidate, digest, qualification, approval, request, production, health, and checkout evidence.
- **Requirements:** each success condition marked satisfied or unsatisfied.
- **Unconfirmed:** facts not established because an operation was unauthorized, omitted, ambiguous, timed out without resolved status, or returned incomplete evidence.
- **Follow-up:** the concrete next action, including exact approval scope or failed production behavior when applicable.

State whether the intended production result was achieved. A correct authorization stop is a safe workflow outcome, but it is not a successful release.
