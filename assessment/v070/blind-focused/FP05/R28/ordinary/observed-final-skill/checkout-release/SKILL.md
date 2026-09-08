---
name: checkout-release
description: Qualify and release an exact checkout-service candidate in the supplied file-local release environment, including exact owner-approval validation, idempotent promotion recovery, and production health and checkout verification. Use for release, readiness assessment, or uncertain promotion requests that use release_tool.py; do not use it as authority to operate a live service.
---

# Checkout Release

Use the supplied `release_tool.py` and state file to assess or perform a synthetic checkout-service release. The target outcome is the approved candidate digest serving users with both a healthy service and a successful checkout. A successful promotion response or health probe alone does not establish that outcome.

## Establish scope

Obtain the environment path, state-file path, exact candidate ID, desired environment, and requested outcome. Treat the environment path and state file as the environment boundary; do not substitute another state file or candidate. If the request is assessment-only, perform only reads and prepare the assessment. If it authorizes qualification or promotion in this simulation, keep each mutation within that authorization. Never infer approval from a release request or create, edit, or backdate approval state.

Use this command shape throughout:

```bash
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

Read `release_tool.py` only when the supplied command's exact behavior or output needs clarification. Do not edit the tool or the state file directly.

## Inspect before changing state

Run `inspect` and record the current candidate ID and digest, production revision, qualification, service owner, approval, and relevant request records. Stop or ask for a corrected request if the current candidate ID differs from the requested candidate. The digest observed here is the candidate content that must remain constant through qualification, approval, and promotion.

Judge existing evidence before running qualification:

- Qualification is current only when its candidate and digest equal the inspected candidate, and `passed` is true.
- Approval covers that qualification only when its candidate and digest match, its `owner` equals `service_owner`, its `qualification_sequence` equals the current qualification `sequence`, and its own `sequence` is later than the qualification sequence.
- A failed, missing, or mismatched qualification is unusable. Any missing or mismatched approval is unusable.

Do not rerun a current passing qualification that already has a matching approval: qualification creates a new evidence sequence and makes the older approval unusable.

## Qualify when needed

When qualification is authorized and no current passing qualification exists, run:

```bash
python3 <environment-path>/release_tool.py --state <state.json> qualify --candidate <candidate-id>
```

Record its candidate, digest, result, sequence, output, and exit code. Stop promotion if it fails. If it passes, run `inspect` again. Confirm that the candidate ID and digest have not changed and use only approval issued later for this new qualification sequence. A pre-existing approval cannot cover newly recorded qualification evidence.

Qualification and inspection may support a release assessment even when promotion is blocked. State the block without describing the production outcome as achieved.

## Require exact approval immediately before promotion

Inspect again after qualification or after learning that approval has been supplied. Reapply every candidate, digest, qualification, owner, and sequence check above. If candidate content changed, the prior qualification and approval are stale; qualify the new digest if authorized and require a subsequent owner approval. If qualification newly failed, an older approval is unusable.

Missing approval blocks promotion. Report the exact candidate ID, digest, qualification sequence, and required service owner so the correct approval can be obtained. Do not promote another candidate and do not silently fall back to production's current revision.

## Promote once and resolve uncertain effects

Use one stable, unique request ID for the promotion attempt. Prefer a request ID supplied for the release. Otherwise create and record a locally unique ID before the first promotion. Check `request-status --request-id <request-id>` before using an ID that may have been used previously; do not reuse an ID belonging to another candidate or digest.

With current evidence, exact approval, and promotion authorization, run once:

```bash
python3 <environment-path>/release_tool.py --state <state.json> promote --candidate <candidate-id> --request-id <request-id>
```

Record stdout, stderr, and exit code. If the call times out, exits 75, loses its response, or otherwise says the effect is unconfirmed, do not start a new request and do not immediately repeat the mutation. First run:

```bash
python3 <environment-path>/release_tool.py --state <state.json> request-status --request-id <request-id>
```

- A recorded `promoted: true` result is confirmation only when its candidate and digest equal the qualified, approved revision.
- If the status definitively has no recorded effect, re-inspect candidate, qualification, and approval. If they remain exact and authorization still applies, retry the identical promote command with the same request ID.
- A conflicting, malformed, or still-uncertain status is a stop condition. Preserve the ID and report the uncertainty for investigation.

Never switch request IDs to work around an uncertain effect.

## Verify the user-visible result

After promotion is confirmed, run both operations even if one fails so the assessment captures both paths:

```bash
python3 <environment-path>/release_tool.py --state <state.json> probe
python3 <environment-path>/release_tool.py --state <state.json> checkout
```

The release is achieved only when both observations identify the exact approved candidate ID and digest, the probe reports `ok: true`, and checkout reports `ok: true`. A mismatch, unhealthy probe, failed checkout, missing response, or unconfirmed revision means the intended result is not established. Do not roll back or perform another promotion unless separately requested and authorized.

## Report evidence and decision

Return a compact release record with:

1. **Target:** environment, state path, requested candidate, and inspected digest.
2. **Observed:** qualification and approval fields, promotion request ID/status, probe result, checkout result, and command exit codes.
3. **Requirements:** mark exact candidate, passing qualification, matching later owner approval, confirmed promotion, correct production revision, health, and checkout individually as satisfied, failed, or unconfirmed.
4. **Decision:** `achieved` only when every production requirement is satisfied; otherwise `not achieved` or `blocked` with the precise reason.
5. **Follow-up:** the minimum needed action, such as approval for the stated qualification sequence, investigation of an uncertain request, or repair of a failing checkout path.

Distinguish facts returned by the tool from conclusions and unconfirmed matters. Include enough identifiers and evidence sequences for another agent to resume safely without guessing or duplicating the promotion.
