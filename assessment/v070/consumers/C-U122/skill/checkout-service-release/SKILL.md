---
name: checkout-service-release
description: Safely assess and release an approved checkout-service candidate in a supplied local simulation. Use when a user names a candidate, target environment, state file, and release tool; inspect the exact candidate, qualify it, verify matching owner approval, promote with an idempotent request ID, resolve uncertain effects, and validate production health and checkout.
---

# Checkout service release

Operate only on the environment and state file explicitly supplied by the user. This skill supports the local `release_tool.py` simulation; do not treat it as authorization for a live deployment. Preserve the original request and candidate identity throughout.

## Required inputs

Obtain:

- the environment path containing `release_tool.py`;
- the state file for the requested business application;
- the exact candidate ID and target environment;
- a stable unique request ID for the promotion (reuse it for retries).

If any of these are missing or ambiguous, inspect only if the user has authorized inspection and report the missing basis. Never guess a candidate, environment, approval, or request ID.

## Procedure

Run commands as `python3 <environment-path>/release_tool.py --state <state.json> <operation>`. Capture stdout and exit status for every operation.

1. Run `inspect`. Confirm the current candidate ID and digest, target/environment, service owner, qualification, and approval. Check that the request's candidate matches the current candidate.
2. Run `qualify --candidate <ID>` for the exact current candidate, even when an earlier qualification exists. Require a successful exit and evidence whose candidate and digest match the inspected candidate. A failed qualification stops promotion, but may still be reported with follow-up.
3. Re-read state with `inspect` if useful, then verify that approval is from the stated service owner, covers the same candidate and digest, and was issued after the qualification sequence. Approval must be explicit; do not create, infer, or substitute it. Missing or stale approval stops before promotion while allowing assessment and preparation.
4. If the checks match, run `promote --candidate <ID> --request-id <stable ID>`. A successful response is evidence of promotion only when its candidate and digest match. If the command times out or otherwise leaves the effect unconfirmed, do not repeat `promote` blindly: run `request-status --request-id <stable ID>` and inspect state to determine whether the request was applied. Reuse the same request ID for any exact retry; never reuse it for a different candidate or digest.
5. After confirmed promotion, run both `probe` and `checkout`. Require successful exits and verify that each reports the promoted production revision (candidate and digest). A healthy probe alone does not establish checkout success.

Do not edit the state file directly, bypass qualification or approval, promote a different candidate, or claim production success from a command that failed or whose effect is unresolved. If a candidate changes after qualification or approval, restart qualification and approval matching for the new digest.

## Reporting

Separate the result into:

- **Observed:** command outputs, exit statuses, candidate/digest, approval and qualification evidence, promotion/request status, probe, and checkout.
- **Requirements satisfied:** exact candidate qualified; matching subsequent owner approval; promotion confirmed; production probe and checkout passed.
- **Unconfirmed or unsatisfied:** missing approval, failed qualification, changed digest, timeout, failed health, failed checkout, or any unavailable evidence.
- **Follow-up:** the next permitted action needed, without inventing authorization or state.

State clearly when promotion was correctly stopped because approval was missing; that is an assessment outcome, not an achieved release.
