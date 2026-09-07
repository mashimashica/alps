---
name: release-checkout
description: Qualify and release an exact checkout-service candidate in the supplied local simulation, verify service-owner approval, recover uncertain promotion effects, and assess production health and checkout. Use for checkout release requests or release-readiness assessments using release_tool.py.
---

# Release checkout

Deliver the requested revision to the requested environment with a ready service and a completed checkout. Qualification, approval, promotion, health, and checkout are distinct evidence requirements. A blocked release is not an achieved release.

## Connect the request

Use [assets/release-request.json](assets/release-request.json) as an optional per-request configuration template. Read its fields as agent inputs; the existing tool does not consume this configuration. Populate values from the user's request and supplied environment, never from guessed defaults. Require the exact candidate ID, desired environment, environment path, and state-file path before operating. Confirm that the supplied state file represents the requested environment: the tool has no environment-selection flag or independent environment attestation. If that mapping is unclear, inspect permitted information and resolve it before mutation.

The environment supplies Python 3 and `release_tool.py`; do not install a connector or copy a second implementation. All operations use this command shape, with quoted arguments:

```text
python3 "<environment-path>/release_tool.py" --state "<state.json>" inspect
python3 "<environment-path>/release_tool.py" --state "<state.json>" qualify --candidate "<candidate-id>"
python3 "<environment-path>/release_tool.py" --state "<state.json>" promote --candidate "<candidate-id>" --request-id "<request-id>"
python3 "<environment-path>/release_tool.py" --state "<state.json>" request-status --request-id "<request-id>"
python3 "<environment-path>/release_tool.py" --state "<state.json>" probe
python3 "<environment-path>/release_tool.py" --state "<state.json>" checkout
```

Substitute literal supplied values safely; do not execute these placeholders. Capture JSON output and exit status for each call. The supplied simulation's precise fields and retry semantics are described in [references/tool-contract.md](references/tool-contract.md); read it before deciding qualification or approval validity or recovering a promotion.

Respect the user's authorized simulation operations. Inspection, probe, checkout, and request-status are read-only in this interface; qualification and promotion write the local state. Existing session authorization is sufficient when it covers the operation. The configuration is not itself permission, and user permission to run the simulation is distinct from service-owner approval in its state. Never edit state directly, manufacture approval, access live services, or substitute another candidate.

## Establish release readiness

1. Inspect the state. Match the requested ID to `candidate.id` and bind this attempt to its exact `digest`. Record current production, qualification, service owner, and approval. If the ID differs, stop candidate mutation and report the mismatch; do not qualify the available candidate instead. Missing identity or evidence fields are unresolved, not successful matches.
2. Determine whether the current recorded qualification passed for this ID and digest. Reuse valid current qualification unless the user requested a fresh run or evidence requires one. Each qualification call creates a new sequence, even for unchanged content, and therefore invalidates approval tied to the previous sequence. If qualification is absent, mismatched, or failed, perform qualification when authorized. A failure blocks promotion. Do not repeatedly rerun a known failing qualification merely to obtain a pass.
3. Inspect again after qualification or any intervening change. Approval must be by the current service owner, name the exact candidate ID and digest, reference the current passed qualification's sequence, and occur later than that qualification. Apply the exact conditions in the tool contract. A changed digest, newer qualification, or latest failed qualification invalidates an older approval. General release permission, candidate-ID-only approval, or a successful historical qualification is insufficient.
4. If valid approval is missing, finish all authorized inspection, qualification, and assessment work. Then report the exact candidate/digest and qualification sequence needing owner approval. There is no approval operation in this interface: the owner or authorized environment provider must supply it. Do not invent a command or change approval fields. Missing owner approval blocks promotion, not the preparatory work.

## Promote and resolve the effect

Immediately before promotion, re-inspect and recheck candidate, qualification, approval, environment mapping, and user authorization. If content changed, reassess that content and require its valid qualification and approval; never silently treat an approval for an old digest as current.

Choose one unique request ID for this exact attempt, or use the request's supplied ID. Record it together with environment/state path, candidate ID, and digest before calling promotion so the same identity survives interruption. Query an existing supplied request ID before using it. If its recorded candidate/digest conflicts, stop and resolve the conflict. Never recycle an ID across candidates, content changes, environments, or unrelated attempts.

Call promotion only when all gates hold. Exit code 0 confirms a command result, not a working release. On timeout, interruption, malformed response, or any uncertain effect, query `request-status` with the same ID and inspect production before deciding whether to retry. Exit code 75 specifically can mean promotion already happened.

- A matching recorded result with `promoted: true` establishes the request's promotion effect; proceed to production checks without another promotion.
- A conflicting recorded result blocks reuse. A missing result does not by itself establish that production is unchanged; compare inspection with the initial state and resolve discrepancies.
- If no result exists, state is consistent with no completed promotion, and the exact candidate and approval gates still hold, an authorized retry may reuse the same ID and arguments. Limit automatic recovery to one exact retry, then inspect status again and report unresolved uncertainty if necessary. Do not use a fresh ID to escape a timeout or tool error.

If the candidate changed while resolving uncertainty, use request-status to recover the prior effect; do not retry against the new candidate. The tool checks the current candidate before recognizing a prior request.

## Verify and assess

After promotion is confirmed, run both `probe` and `checkout`, even if the first fails. Each must report `ok: true` and a production `revision` whose ID and digest match the intended candidate. Health success alone cannot satisfy checkout. Qualification flags and candidate expectations cannot substitute for these post-promotion observations. If the observations identify different revisions or disagree with final inspection, mark the intended release unconfirmed and investigate permitted read-only evidence.

Report the observed promotion effect separately from overall release success. If production is unhealthy or checkout fails, the release objective is unmet even though promotion succeeded. Do not claim automatic rollback, fix state flags, or promote an alternative: this interface supplies no rollback or repair operation. Identify the failed requirement and necessary authorized remediation, then require fresh evidence for any subsequent success claim.

Give a concise release assessment containing:

- Requested environment, candidate ID/digest, and simulation scope.
- Qualification result and sequence; approval owner and binding, or the specific missing gate.
- Request ID, promotion result, and any timeout/recovery evidence.
- Post-promotion health and checkout results with the observed revision for each, or explicitly “not run” and why.
- Requirement status for exact revision, valid qualification, exact owner approval, promotion, ready service, and working checkout; distinguish satisfied, failed, and unconfirmed.
- Overall outcome: achieved only when all requirements hold, otherwise blocked, failed, or unconfirmed, with the next necessary action and responsible party where known.

Support claims with actual outputs. Preserve uncertainty when a command or observation did not establish the result; do not describe a correct permission stop as release completion.
