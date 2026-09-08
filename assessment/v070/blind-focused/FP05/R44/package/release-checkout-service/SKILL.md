---
name: release-checkout-service
description: Qualify, promote, resume, or assess an exact checkout-service candidate in the supplied local release simulation, then verify production health and checkout. Use for synthetic release requests that provide an environment path, state file, candidate ID, and target environment; do not use for live deployments or other release tools.
---

# Checkout Service Release

## Purpose

Make the intended, approved checkout-service revision available in the requested simulated environment with both a ready service and a functioning checkout.

## Outcomes

- The exact candidate and digest covered by a passing qualification and the service owner's subsequent matching approval are the production revision.
- A post-promotion production probe reports that exact revision healthy.
- A post-promotion checkout exercise completes for that exact revision.
- The release result distinguishes observed evidence, satisfaction of requirements, unconfirmed matters, and necessary follow-up.

## Establish the release instance

Obtain the exact candidate ID, desired environment, environment path, state-file path, and requested extent of work. Treat these as application-specific inputs; do not substitute another candidate or environment. Confirm that the supplied paths are identified for the desired environment before changing state. Ask for missing identity or mapping information when it cannot be inferred reliably.

Operate only on the local simulation with:

```text
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

Read [the release-tool interface](references/release-tool.md) before invoking it. If the available `release_tool.py` differs from that interface or produces an unexpected result, inspect the supplied file and limit dependent actions until its behavior is understood. Quote paths and identifiers when forming shell commands.

Determine which operations the user's current request authorizes. `qualify` updates qualification state and `promote` updates simulated production state. Business approval recorded in the state does not grant tool-use authorization, and user authorization does not replace the service owner's recorded approval. A clear request to carry out the synthetic release may cover the necessary simulation operations; a request to inspect, assess, or prepare does not by itself authorize promotion.

## Inspect and establish the approval basis

1. Run `inspect` and preserve the observed candidate ID and digest, qualification record, approval record, service owner, production state, and prior request records needed for this release.
2. Require the current candidate ID to equal the requested candidate ID. A mismatch blocks qualification and promotion for the requested candidate; report it instead of switching candidates.
3. Reuse an existing qualification and approval only when all exact-match and ordering conditions in [Approval validity](references/release-tool.md#approval-validity) hold for the current candidate and digest. Do not rerun a valid qualification merely to refresh it, because a new qualification invalidates the prior approval basis.
4. When qualification is missing, failed, or stale and `qualify` is authorized, qualify the requested candidate. Treat a non-passing result as evidence that the candidate is not qualified even though the command recorded a qualification. Do not promote it.
5. After a passing qualification, inspect again. Confirm that the candidate ID and digest are unchanged and use the newly observed qualification record as the approval basis. If a matching subsequent owner approval is not present, stop before promotion and identify the exact candidate, digest, and qualification sequence that must be approved.

A changed candidate digest, a new qualification, or a new failed qualification requires the affected qualification and approval judgments to be made again. Never invent, infer, or edit approval state.

## Promote with recoverable request identity

Immediately before promotion, inspect again and recheck the candidate identity, digest, passing qualification, matching subsequent owner approval, target environment mapping, and authorization. If any basis changed, do not promote until the affected conditions are re-established.

Choose one unique request ID for this promotion attempt unless the user supplied the ID for a retry or resumption. Record it before invoking `promote`, and reuse that same ID for every status check and permitted retry of the exact candidate and digest. Never change the request ID merely because a response was lost or timed out.

Run `promote` only after all promotion conditions hold. A successful command is evidence of the promotion operation, but it does not establish production readiness or working checkout.

If the promotion response times out, is incomplete, or otherwise leaves its effect uncertain:

1. Run `request-status` with the same request ID before any retry.
2. Treat a recorded result with `promoted: true` and the expected candidate and digest as evidence that the request took effect. Do not promote again.
3. If the request is definitively unrecorded, inspect the current candidate, qualification, and approval again. Retry only if authorization still applies and the complete basis still holds, using the same request ID.
4. If request status or the applicable basis cannot be established, stop. Report the promotion effect as unconfirmed and do not create a second request ID.

## Verify production results

After promotion is established, run both `probe` and `checkout`. For each observation, require the returned production revision's ID and digest to match the promoted candidate and digest. Then judge the reported `ok` value.

Both observations are necessary and independently assessable. A healthy probe does not establish checkout success. A completed deployment or promotion does not establish either production outcome. Run both checks when they remain authorized and available even if one fails, so the report distinguishes the resulting conditions.

Report the overall release as achieved only when the exact approved revision is established in production, the matching production probe is healthy, the matching checkout completes, and the promotion requirements were satisfied. A blocked promotion can be the correct action while the intended production result remains unachieved. A mismatched revision, failed observation, missing evidence, or uncertain effect must remain failed or unconfirmed rather than being converted into success.

## Report the assessment

Provide a concise release assessment that identifies:

- the requested environment, candidate ID, observed digest, and promotion request ID if one was created;
- observed qualification and approval evidence, including their exact-match and ordering basis;
- the promotion or status observation and its effect;
- the production revision, health result, and checkout result;
- each Outcome and each mandatory promotion condition as achieved, unmet, blocked, or unconfirmed, with the supporting observation;
- follow-up needed for every unmet, blocked, or unconfirmed item.

Label facts returned by the tool as observations and keep them separate from the resulting judgments. Mention command failures that limit a judgment. Do not claim that a correct stop, a successful command, or the existence of a deployment record achieved the release Outcomes by itself.

## Constraints

- Work only in the user-authorized synthetic environment. This skill provides no permission for a live repository, deployment service, or customer state.
- Qualification must pass before the matching service-owner approval, and both must apply to the exact current candidate digest before promotion.
- Production checks must follow the established promotion and must concern the promoted revision.
- Missing permission blocks only the dependent operation; inspection, authorized qualification, status recovery, and release assessment may continue within their own conditions.

