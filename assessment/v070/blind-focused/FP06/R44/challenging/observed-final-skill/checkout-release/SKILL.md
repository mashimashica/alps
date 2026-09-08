---
name: checkout-release
description: Release an exact candidate of a fictional checkout service in an authorized local simulation. Qualify the candidate, verify subsequent owner approval, reconcile uncertain promotion effects, and assess revision, health, and checkout evidence. Use for release requests, blocked release assessments, and recovery of a timed-out promotion through an existing release_tool.py environment.
compatibility: Requires Python 3, an existing release_tool.py implementing the documented interface, a supplied local JSON state file, and a shell or argument-vector command runner. No network access is needed.
---

# Checkout Service Release

## Purpose

Make the intended, approved revision available to users in the requested simulated environment with a ready service and a working checkout. This work covers release qualification, promotion and result assessment; it does not create owner approval, repair candidate content, or perform live deployment.

## Outcomes

- The exact intended and approved candidate revision is present in the requested environment's production state.
- The production health probe reports ready for that revision.
- The production checkout exercise completes for that revision.

## Activities & Tasks

The following Tasks are required where their conditions apply. Use the [configuration](references/configuration.md) and [command contract](references/command-contract.md) when connecting to a supplied environment. The temporal dependencies are stated in Constraints.

### Establishing the release basis

1. Identify the user's exact candidate, desired environment, supplied environment path and state path, and authorized simulation operations. Bind the paths to the desired environment using the request; the tool has no environment selector or independent environment identity check. Resolve missing or conflicting bindings before dependent operations. Do not select another candidate or infer approval from a request to release.
2. Inspect the authorized state. Record the candidate ID and digest, current production revision, service owner, latest qualification, approval, and any relevant promotion request. If the candidate does not match the requested ID or the digest is absent, stop dependent promotion and explain the discrepancy. If the request supplies a digest, require that match too.
3. Retain the observed digest as part of the release identity. Reconsider qualification, approval and any pending promotion decision whenever the candidate content, qualification record, owner, approval, environment binding or production evidence changes. Missing approval must not prevent authorized inspection, qualification or preparation of the release assessment.

### Qualifying and establishing authority

1. Examine existing qualification evidence for the exact current candidate and digest. A successful existing qualification can be used if its basis is still applicable and the request does not require a fresh run. Otherwise run `qualify --candidate ID` if authorized and inspect the resulting state. Record its candidate, digest, `passed` and `sequence`. A failed or missing qualification prevents promotion.
2. Verify the approval against the latest qualification using every predicate in the command contract: exact ID and digest; successful qualification; owner equal to `service_owner`; approval's `qualification_sequence` equal to the qualification sequence; approval sequence strictly later than qualification sequence. Missing, malformed or mismatched fields leave approval unusable. A fresh qualification changes its sequence even when it passes; the earlier approval then no longer covers it.
3. When approval is missing or stale, prepare the release assessment identifying the candidate ID, digest, successful qualification sequence if available, and approval needed from the service owner. Do not edit the state to manufacture approval or contact anyone without authorization. Resume with inspection after owner approval is supplied through the applying environment.

### Promoting and reconciling effects

1. Before a new promotion, confirm authorized promotion scope, current candidate content, current successful qualification and applicable subsequent owner approval. Inspect again if intervening work or elapsed activity could have changed the basis. Do not run qualification again merely as a pre-promotion ritual when a matching approved qualification already exists.
2. Bind a request ID to this environment/state, candidate ID and digest. Reuse an ID already assigned to an uncertain attempt; otherwise select a unique ID and record this binding before sending the command. Check `request-status` to detect an existing effect or conflicting ID. Do not reuse an ID for different content or another logical promotion.
3. Run `promote --candidate ID --request-id ID` when the conditions are established. Record structured output and exit code. The tool enforces matching qualification and approval for new effects, but a command success does not establish production readiness or checkout success.
4. After a timeout, lost response or ambiguous error, run `request-status` with the original request ID and inspect state before any retry. A matching recorded `promoted: true` means the effect was recorded: proceed to production checks without promoting again. A conflicting record requires a stop and reconciliation. If status has `result: null`, inspect current production and prerequisites; absence of a record alone does not prove that no change happened after an unexpected interruption. If effects remain ambiguous, stop mutation and report the uncertainty. If no effect is established and the original identity, authorization and prerequisites still hold, an exact retry may use the same ID. Never use a new ID to bypass an uncertain attempt.

### Assessing production and handing off

1. After promotion or a reconciled recorded promotion, run both `probe` and `checkout` against the same bound state. Run checkout even when the probe is unsuccessful if it remains authorized and usable. Compare both returned revision IDs and digests to the intended revision. Candidate flags and qualification are not post-promotion evidence.
2. Assess each Outcome independently. A healthy different revision fails the intended-release condition. A healthy intended revision with a failed checkout leaves the checkout Outcome unmet. Missing, inconsistent, stale or unreadable observations leave affected judgments unconfirmed; inspect or repeat authorized read operations to resolve a concrete evidence gap.
3. Report the observed result, requirement satisfaction, unconfirmed matters and necessary follow-up in distinct fields or paragraphs. Include environment/path binding, intended ID/digest, qualification and approval basis, request ID/effect, and each production observation with its returned revision and exit code. Mark each Outcome as achieved, unmet or unconfirmed with evidence. Assess authorization, exact-candidate matching, qualification/approval order, and post-promotion checks separately from Outcome achievement.
4. On a blocked gate, report that promotion was withheld and the intended production result was not established by this attempt. On production failure, report the actual failure and follow-up needed; rollback, state repair and changing candidates require a separate authorized capability and must not be invented. Finish successfully only when all Outcomes have current supporting evidence and mandatory conditions were satisfied. A completed assessment can be handed off even when release success is unmet or unconfirmed.

## Controls

The request governs the target and authorized operation scope. Qualification must pass for the exact candidate content. Service-owner approval must cover that exact qualification and content. Readiness and completed checkout for the intended production revision are distinct acceptance conditions. The command contract documents how these requirements map to the supplied simulator; tool acceptance alone is not evidence of every requirement.

## Constraints

- Use only the authorized local simulation and documented operations. Do not modify the command implementation or directly edit state to qualify, approve, promote, repair or roll back.
- Qualification precedes the approval that covers it; that approval precedes a new promotion; production evidence follows promotion. A content change or a new qualification invalidates the old approval basis, including a new failed qualification.
- Missing or unconfirmed authority blocks only the dependent operation. The user authorizes simulation operations per application; owner approval is a separate promotion condition.
- Resolve uncertain effects before retrying mutation. Keep state-changing commands serial. The file simulator has no locking or transactional concurrency guarantee; if concurrent writers are present, coordinate their exclusion before promotion or mark the environment unsuitable for a reliable release.

## Inputs and Outputs

Inputs are the current release request and observed candidate, production, qualification, approval and request records. Outputs are any updated qualification, promotion request record and production revision produced by permitted commands, plus a release assessment. An assessment or deployment record alone does not establish the Outcomes.

## Enablers

One interpreting agent, the applying user's authorization, Python 3, the supplied local command and state file support this work. The service owner supplies approval through the environment's separate arrangement. [Configuration](references/configuration.md) allocates responsibilities and documents the connection; it refers to this description as the source of release meaning.
