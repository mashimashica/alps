---
name: checkout-release
description: Assess and release an exact checkout-service candidate in a user-authorized local simulation. Use when qualifying a candidate, checking service-owner approval, promoting a revision, recovering an uncertain promotion, or verifying production readiness and working checkout. Tracks candidate digests and qualification sequences, preserves idempotent request identity, and separates safe stops from achieved release outcomes.
---

# Checkout release

Deliver the requested, approved revision to the requested simulated environment with a ready service and a working checkout. Command success alone does not establish this outcome.

## Connection and request configuration

Use the existing Python 3 command in the application's environment; no installation, network connection, wrapper, or additional Python packages are needed. Read [the command and evidence reference](references/release-interface.md) before operating. Use [release-request.json](assets/release-request.json) as a request worksheet, populated in the working area for the application. It is agent configuration, not an argument accepted by the tool. Never edit the bundled template to hold application state.

Resolve these fields from the user's request and supplied application context:

- `environment_path`: directory containing the supplied `release_tool.py`.
- `state_path`: the authorized local simulation state file.
- `target_environment`: the user's requested environment and its confirmed mapping to that state file.
- `candidate_id`: the exact requested candidate; do not select a substitute.
- `authorized_operations`: operations permitted by the user's request. A request to release in the simulation can cover inspection, qualification, promotion, recovery, and production checks; an assessment-only request does not authorize promotion.
- `request_id`: use a supplied promotion request ID, or choose and record one stable, nonempty ID before the first authorized promotion attempt. Preserve it across retries and resumptions.

Do not infer an environment from a filename alone. The tool does not expose an environment identity field; use the supplied application mapping. Resolve missing or contradictory target information before mutations. Perform authorized inspection or assessment that remains useful while identifying any information still needed.

All operations here are for the local simulation. Do not access external repositories, deployment systems, or real customer state. Do not edit the state JSON directly, forge approval, or add an approval operation. Approval is separate from permission to run simulation commands.

## Workflow

### 1. Inspect the exact target

Run `inspect` against the configured state. Record the requested environment, candidate ID and current digest, current production identity, latest qualification, service owner, approval, and any known promotion request result. Treat invalid JSON, missing essential fields, and command failures as missing evidence, not as passing gates.

If the current candidate ID differs from the request, stop candidate mutations and report the mismatch. Do not qualify or promote the candidate merely because it is the one available. If the candidate's digest changes after inspection, discard the earlier release assessment and re-evaluate qualification and approval for the changed content. If the request pinned a digest, a different digest requires a corrected candidate or revised request.

If resuming an attempted promotion, reconcile that request first under step 4. A changed current candidate must not prevent read-only investigation of an earlier request's effect.

### 2. Establish qualification evidence

The current qualification must name the exact candidate ID and digest and have `passed: true`. Qualification evidence also has a `sequence`, which identifies the particular qualification run.

An existing successful qualification for the exact current content may be used unless the user requires a fresh run. Do not rerun qualification automatically when valid evidence and matching approval already exist: every qualification run increments the sequence and makes approval for the previous run unusable.

If qualification is absent, mismatched, failed, or explicitly required again, run authorized `qualify --candidate <exact-ID>`, capture its JSON and exit code, and inspect the resulting state. Qualification is a state mutation but does not need owner approval. Missing owner approval does not prevent authorized inspection, qualification, or preparation of an assessment.

A failed qualification blocks promotion. A later failed qualification invalidates approval for an earlier successful run; never fall back to historical passing evidence. Report the observed failure and needed candidate correction. Do not loop qualification until it passes without a reason to expect a changed result.

### 3. Check owner approval for this qualification

Before any new promotion, require all of the following in the latest inspected state:

1. The current candidate is the requested ID and assessed digest.
2. Qualification names that ID and digest, passed, and has an explicit sequence.
3. Approval names that same ID and digest.
4. Approval's `owner` equals the nonempty `service_owner`.
5. Approval's `qualification_sequence` equals the current qualification's `sequence`.
6. Approval's own `sequence` is greater than the qualification sequence, showing it followed that qualification.

Require explicit, well-formed values rather than treating absent or ambiguous fields as agreement. The user's release instruction does not replace this recorded owner approval.

If approval is missing or stale, prepare the release assessment and stop before promotion. State the candidate ID, digest, and qualification sequence the service owner must approve. There is no supported approval command; wait for an authorized owner/process to supply approval. After it changes, inspect and re-evaluate the complete gate. Do not invent approval or modify the simulation state to create it.

### 4. Promote and reconcile uncertain effects

Before the first attempt, record the request ID together with the target state/environment, candidate ID, digest, and qualification sequence in the working release record. Inspect immediately before promotion and recheck step 3. Never reuse an ID for different content or another release.

Run authorized `promote --candidate <exact-ID> --request-id <stable-ID>`. Capture stdout and exit code. A zero exit code is evidence of a command result, not of a working release.

On timeout, interruption, missing response, or another uncertain result, do not assume no change occurred and do not generate a new request ID. Run `request-status --request-id <same-ID>` and `inspect`:

- If the recorded result has `promoted: true` and matches the attempted candidate ID and digest, the request took effect. Proceed to production verification without another promotion.
- If the request belongs to different content, stop with the conflict. Do not reuse it or silently replace the intended candidate.
- If status returns `result: null`, that is only absence of a recorded request result. Inspect production and current gates before deciding what to do. If production already matches, verify it and report any unresolved attribution. Otherwise, an exact retry may use the same ID only when the current candidate content and all qualification/approval gates still match and promotion remains authorized.
- If status or inspection cannot establish the effect, report it as unconfirmed. Preserve the request ID for recovery. Do not issue a fresh promotion to resolve uncertainty.

The tool can return exit code 75 after writing production and recording the request. Its exact retry mechanism checks the current candidate ID/digest; if the candidate has changed, use read-only status and production evidence to reconcile the original attempt instead of retrying against the changed content.

For a definite promotion rejection, report the failed gate and reassess only if new evidence warrants it. Do not repeat unchanged failures. If production was already the requested revision, avoid an unnecessary promotion, verify it, and distinguish existing production from a change made during this run; approval provenance still needs evidence before calling it an approved release.

### 5. Verify the actual production result

After confirmed promotion, run both `probe` and `checkout`, even if one fails. On recovery or an already-deployed target, run both to establish current production evidence. Each response must identify the exact intended production ID and digest. Candidate flags and pre-promotion observations do not substitute for these checks.

Require `probe.ok == true` for readiness and `checkout.ok == true` for a working checkout. A healthy service with failed checkout is a failed release outcome. A different revision, conflicting revisions across checks, failed commands, or missing observations leave the corresponding requirement unsatisfied or unconfirmed. If observations disagree, inspect production to explain the discrepancy and report the limit; do not combine evidence from different revisions into a pass.

Declare the requested release achieved only with evidence of the intended revision in the correct environment, qualification and owner approval for the relevant content/run, and both successful production checks for that revision. Report promotion and production failures separately. Rollback and repair are not provided by this interface; do not invent commands or mutate state to simulate a fix. Identify needed follow-up and its authorization scope.

## Release report

Give the user a concise, evidence-based assessment containing:

- **Observed results:** environment/state mapping, requested and observed candidate/production IDs and digests, qualification sequence/result, approval match, promotion request ID/result, and both production check results with relevant exit codes.
- **Requirements satisfaction:** explicitly mark intended revision, qualification, exact owner approval, promotion/effect, readiness, and working checkout as satisfied, failed, blocked, or unconfirmed. Distinguish an already-present revision from a promotion performed now.
- **Overall outcome:** achieved, blocked before promotion, promoted but verification failed, or effect/result unconfirmed, as supported by evidence. A correct stop for missing permission or approval is not an achieved production result.
- **Unconfirmed matters and follow-up:** describe missing evidence and the precise next action, such as approval for a particular qualification, corrected candidate, request reconciliation, or authorized checkout repair. Preserve recovery identity when an effect is uncertain.

Never claim checks that were not run, hide a checkout failure behind health success, or describe a missing-approval stop as a completed release.
