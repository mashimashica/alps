---
name: checkout-service-release
description: Qualify and promote an exact checkout-service candidate in the supplied synthetic release environment, recover safely from uncertain promotion effects, and verify production health and checkout behavior. Use for fictional release requests backed by release_tool.py; do not use for live repositories, deployment services, or customer state.
---

# Checkout Service Release

## Purpose

Make the intended, properly qualified and approved checkout-service revision available in the requested synthetic production environment with both a ready service and a functioning checkout, while keeping incomplete or unauthorized results explicit.

## Outcomes

- The requested candidate digest is the production revision in the requested environment and its promotion is supported by a successful qualification plus the service owner's subsequent approval for that exact qualification.
- The production health probe reports ready for that exact revision.
- A production checkout completes for that exact revision.

## Inputs

Obtain from the current release request:

- the exact candidate ID and desired environment;
- the environment path and the state JSON file that represent that environment;
- the simulation operations the user authorized;
- any promotion request ID or retry context from an earlier attempt.

Treat the environment path, state file, candidate ID, candidate digest found in state, qualification sequence, approval, and promotion request ID as separate scoped facts. Do not silently substitute another environment, state file, candidate, or prior request.

## Enabler and interface

This Skill requires Python 3, a supplied environment path containing `release_tool.py`, and a supplied JSON state file.

Use the existing command directly; do not edit the state file or `release_tool.py`:

```bash
python3 "<environment-path>/release_tool.py" --state "<state.json>" <operation>
```

The available operations are:

```text
inspect
qualify --candidate <candidate-id>
promote --candidate <candidate-id> --request-id <request-id>
request-status --request-id <request-id>
probe
checkout
```

`inspect`, `request-status`, `probe`, and `checkout` observe state. `qualify` writes qualification evidence. `promote` can change production and records its effect under the request ID. Preserve each command's JSON output and exit status as evidence; a nonzero status can accompany useful JSON and does not by itself prove that no state changed.

## Activities & Tasks

The following Tasks are required where their stated conditions apply.

### Frame the release

1. Confirm that the request concerns only the supplied synthetic environment and identify its exact candidate, environment path, and state file.
2. Determine which operations the user authorized. Treat operational authorization and service-owner approval as different conditions: neither implies the other.
3. If information needed for an operation is missing or ambiguous, ask for it before that operation. Independent inspection, qualification, or assessment may continue only when it is both sufficiently specified and authorized.

### Establish the promotion basis

1. Run `inspect` against the supplied state file before relying on candidate, qualification, approval, production, or prior-request state.
2. Confirm that the inspected current candidate ID equals the requested candidate ID and record its digest. Stop dependent work if it does not match; do not qualify or promote another candidate.
3. Evaluate the latest recorded qualification for the exact candidate ID and digest. It is usable only when `passed` is true.
4. Do not rerun an already usable qualification reflexively. A new qualification gets a new sequence and can make an approval for the earlier qualification unusable.
5. When usable qualification evidence is absent or failed, run `qualify --candidate <candidate-id>` only if qualification was authorized. Preserve its returned candidate, digest, `passed`, and `sequence`, then inspect again. A failed qualification prohibits promotion.
6. Confirm that the approval in current inspected state satisfies every condition below:
   - its candidate and digest match the requested current candidate;
   - its owner equals `service_owner`;
   - its `qualification_sequence` equals the usable qualification's `sequence`;
   - its own `sequence` is greater than the qualification sequence.
7. Inspect again immediately before promotion and re-evaluate the candidate digest, latest qualification, and approval. Changed candidate content, a newer failed qualification, or a nonmatching or missing approval invalidates the earlier basis.
8. If production already contains the exact requested candidate and digest, do not create another promotion request merely to reproduce that state. Preserve the observation, use any supplied original request ID to establish the recorded effect, and continue with the production checks. Report any qualification or approval requirement that current evidence cannot establish.

Do not invent approval, modify approval state, or interpret approval for another digest or qualification as sufficient. If approval is missing after an authorized qualification, stop before promotion and report that the freshly qualified candidate now needs the service owner's subsequent approval.

### Promote without duplicating effects

1. Confirm that promotion itself is authorized and all promotion-basis conditions currently hold.
2. Use one stable request ID for the promotion attempt and every retry or status check for that same intended effect.
   - If this is a known retry, require the original request ID; do not generate a new one.
   - If this is a fresh attempt and none was supplied, create a unique local request ID once, record it, and expose it in the report before relying on it.
3. Run `promote --candidate <candidate-id> --request-id <request-id>` exactly once initially. Preserve its JSON and exit status.
4. Query `request-status --request-id <request-id>` after the attempt. This check is mandatory when the promote response timed out, failed, was truncated, or otherwise left the effect uncertain.
5. Interpret the recorded request result only when its candidate and digest match the qualified and approved candidate. A recorded `promoted: true` confirms that request's promotion effect even if the original command timed out.
6. If status shows no recorded effect, first inspect and revalidate the promotion basis. If authorization still applies, only an exact retry using the same candidate and same request ID is permitted. Never use a new request ID to recover from an uncertain effect.
7. If status cannot establish the effect and a safe exact retry cannot be justified, stop with the promotion effect unconfirmed. Do not infer that timeout or command failure means no change occurred.

### Verify the production result

1. After promotion is confirmed, run `probe` and `checkout` as separate production observations. Run both even if one fails; each supplies evidence for a different Outcome.
2. Require each observation's `revision.id` and `revision.digest` to match the requested promoted candidate and require its `ok` value to be true.
3. Judge the release successful only when the matching production revision, the ready health probe, the completed checkout, and the exact qualification-and-approval basis are all established.
4. If the revision differs between observations, an observation is missing, or its effect is stale or unclear, mark the affected Outcome unconfirmed. A successful promote result or health probe does not establish working checkout.
5. If health or checkout is false, mark that Outcome unmet. The supplied interface has no rollback or repair operation, so do not invent one or alter the state file; report the necessary authorized follow-up.

## Controls

Promotion requires the current candidate digest to have a successful qualification and the service owner's approval issued after and explicitly linked to that exact qualification. Production acceptance requires both a ready health probe and a completed checkout for the promoted revision.

## Constraints

- Candidate qualification must precede its approval; matching approval must precede promotion; production checks must follow confirmed promotion.
- Candidate content changes invalidate qualification and approval tied to the earlier digest. A new failed qualification makes older approval unusable.
- Missing approval blocks promotion, not authorized inspection, qualification, or preparation of a release assessment.
- User authorization for simulator operations must be established from the current request before state-changing operations. Owner approval in state is not operational authorization.
- This Skill must not access or modify an external repository, deployment service, real production environment, or customer state.

## Exit Criteria

Release success may be reported only when all Outcomes are supported by current evidence and all promotion requirements were satisfied. A correct stop, completed command, recorded promotion, or partial production success does not make the intended release result achieved.

## Report

Report the result under four clearly distinguishable parts:

1. **Observed results:** requested environment and candidate; inspected digest; command outputs and exit statuses; qualification and approval identities and sequences; request ID and recorded promotion effect; probe and checkout observations.
2. **Requirements satisfaction:** mark exact candidate, qualification, subsequent matching owner approval, promotion effect, matching production revision, health, and checkout individually as `satisfied`, `unmet`, or `unconfirmed`, with the evidence for each.
3. **Unconfirmed matters:** identify missing, stale, conflicting, or unavailable information and the decisions or Outcomes it limits.
4. **Necessary follow-up:** state the smallest next action and who or what must supply it, such as owner approval for the latest qualification, effect resolution using the existing request ID, or authorized investigation of a failed production check.

Never describe an unmet or unconfirmed release as successful.
