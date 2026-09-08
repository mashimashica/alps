---
name: release-checkout-service
description: Qualify and release an exact checkout-service candidate in an authorized local simulation, validate the service owner's approval, reconcile uncertain promotion effects, and assess production revision, health, and checkout. Use for release requests or release assessments using the supplied release_tool.py interface.
compatibility: Requires Python 3, the application-provided release_tool.py, and an authorized local JSON state file. No external services are required.
---

# Checkout Service Release

## Purpose

Make the intended, approved revision available to users of the requested simulated environment with a ready service and functioning checkout. This work covers candidate assessment, authorized promotion, and production verification; creating approval, changing candidate content, repairing the service, and live deployment are outside its scope.

## Outcomes

- The intended revision, qualified and approved for that exact qualification, is present in the requested production environment.
- The production service for that revision reports ready.
- Checkout completes for that production revision.

## Inputs

Use the current release request for the exact candidate ID, desired environment, application-provided environment path and state file, and authorized simulation operations. Read candidate content identity, qualification, approval, service owner, production state, and request history through `inspect`.

## Controls

Qualification must pass for the exact candidate ID and digest. The service owner's approval must cover that candidate, digest, and exact qualification sequence, and must follow the qualification. The field comparisons in [the tool interface](references/tool-interface.md) implement this rule. Production acceptance requires matching revision identity, successful health, and successful checkout evidence from after promotion.

## Constraints

- Apply this Skill only to the supplied local simulation and operations authorized by the current user request. User authorization to operate the simulation and the recorded owner's candidate approval are distinct conditions.
- Qualification must precede its approval; matching approval must precede a new promotion; production acceptance checks must follow promotion or reconciliation of an already completed promotion.
- A changed candidate digest invalidates earlier qualification and approval. Every new qualification replaces the prior qualification, including a failed one; an old approval must not be reused against it.
- Missing approval prevents promotion, while authorized inspection, qualification, and assessment may continue. Missing paths, candidate identity, or environment mapping prevent dependent operations; do useful independent assessment and identify the missing input.
- Never invent approval, edit the state to bypass a condition, silently select another candidate, or send an approval request to another person without authorization. There is no approval or rollback command in this interface.
- Resolve uncertain promotion effects before another state-changing attempt. Do not replace a timed-out request's identifier with a new one.

## Activities & Tasks

The following Tasks are required within their applicable conditions. The Constraints specify necessary ordering; return to affected Tasks when evidence changes.

### Establishing the release basis

1. Bind the request to the intended candidate and environment using [the connection configuration](references/tool-interface.md#connection-configuration) and optional [context template](assets/release-context.json). Confirm the supplied state file represents that environment: the CLI has no environment selector or independent environment identity. Do not infer the mapping from a filename alone when the request does not establish it.
2. Read the interface reference before operations. Invoke `inspect` and retain the source paths, requested candidate, current candidate ID/digest, relevant qualification and approval records, and production identity in the assessment. Treat malformed or incomplete evidence as unconfirmed, not as default approval or success.
3. Compare the requested candidate ID with the current candidate ID. If they differ, stop candidate-dependent operations and report the mismatch; do not change the requested ID to make the command work. If an exact retry is already pending, retain its original ID/digest/request-id tuple and use `request-status` even if the current candidate has changed.

### Qualification and approval assessment

1. Examine the current qualification for this candidate and digest. Reuse an existing successful matching qualification when the request permits it; do not rerun a valid approved qualification unnecessarily. If qualification is missing, failed, stale, or the user explicitly requires a new run, perform authorized `qualify --candidate ID`. Capture the returned digest, `passed`, sequence, and exit code; inspect again if its write effect is uncertain.
2. Assess approval against the latest matching qualification using all comparisons in the reference. A prose instruction to release does not manufacture the recorded owner approval. A passed qualification alone does not authorize promotion. If a new qualification ran, even successfully, require approval covering its new sequence.
3. When qualification fails or approval is absent, stale, mismatched, or unconfirmed, prepare the release assessment and stop before promotion. Identify the exact candidate, digest, qualification sequence, and approval needed for continuation. The service owner supplies approval through the application's separate process; this Skill has no mechanism to grant it.
4. Immediately before any new promotion, inspect again and confirm candidate content, successful qualification, matching subsequent approval, intended environment, and operation authorization still apply. If any basis changed, re-evaluate it before proceeding.

### Promotion and uncertain effects

1. Establish one stable, unique request ID for the intended promotion in this state file. Reuse the known identifier when resuming the same request; otherwise use an identifier supplied by the request or generate one and record its association with candidate ID, digest, and environment before invoking promotion. Inspect request history to avoid a collision.
2. Call `promote --candidate ID --request-id ID` only when the applicable preconditions are confirmed. Preserve the result, exit code, and request tuple. Do not treat command completion as release success.
3. After timeout, transport interruption, or ambiguous output, call `request-status` with that same request ID and inspect current state. A matching result with `promoted: true` establishes the recorded effect; continue to production verification without promoting again. If the recorded request belongs to a different candidate or digest, stop and report the conflict.
4. A `null` request result means no record was found, not successful promotion. Confirm the previous command is no longer running and re-inspect before considering a retry. Only retry the exact same request tuple when the tool's supported idempotency applies, current candidate content is unchanged, and all current promotion conditions still hold. If the effect cannot be established, leave promotion unconfirmed and seek the missing evidence. Never loop blindly or start a replacement request to escape uncertainty.

### Production verification and assessment

1. After a confirmed promotion, invoke both `probe` and `checkout` in the same environment and state file. Perform checkout even when health fails if authorized and available, so its result is independently known. Collect both returned revision objects, `ok` fields, and exit codes.
2. Confirm both observations identify the intended candidate ID and digest. A successful observation for another revision does not establish this release's outcome. If the observations disagree or production changes during assessment, inspect and obtain fresh observations for the intended revision; do not combine evidence from different revisions into success.
3. Judge every Outcome separately against the evidence. Health success cannot substitute for checkout completion. Failed checkout leaves the intended release result unmet even if promotion and health succeeded. Missing observations leave the affected Outcomes unconfirmed.
4. Report the observed effects, Outcome judgments, mandatory requirement satisfaction, unconfirmed matters, and necessary follow-up using the Output requirements below. If an issue needs repair, rollback, new qualification, or new owner approval, identify it without inventing an unsupported command or performing an unauthorized action.

## Enablers

One applying agent interprets the request and evidence, checks authority and freshness, chooses permitted operations, manages request identity, and assesses the result. The existing Python CLI performs state inspection, qualification recording, guarded promotion, request lookup, health probing, and checkout observation. The local JSON state supplies the shared candidate, approval, qualification, production, and request records.

The [interface and configuration reference](references/tool-interface.md) defines dependencies, connections, effects, and known limits. Use the existing CLI directly: no wrapper, service connection, or additional agent is required. The optional JSON template is a record of application bindings, not an executable permission mechanism; the CLI does not consume it.

## Outputs

Produce a release assessment, in the response or an authorized artifact, containing:

- Requested environment and source mapping; candidate ID/digest; qualification sequence/result; approval owner and scope; promotion request ID and observed effect.
- Production revision, health observation, and checkout observation with their evidence sources and timing relative to promotion.
- One judgment per Outcome: achieved, unmet, or unconfirmed, with supporting observations.
- Separately, whether applicable mandatory conditions were satisfied, violated, or unconfirmed. State whether promotion was prevented by a gate. Correctly withholding promotion does not establish the production Outcomes.
- Missing evidence, unresolved effects, and the concrete next action and required authority or input. Do not imply a follow-up has happened merely because it is recommended.

## Entry and Exit Criteria

Assessment may begin with the available request information. Tool operations require the supplied connection information and applicable simulation authorization. Only promotion requires matching successful qualification and subsequent owner approval.

Declare the release successful only when all three Outcomes are evidenced and mandatory release conditions are satisfied. A blocked, failed, or incomplete application may end with an honest assessment, but must not be described as an achieved release.
