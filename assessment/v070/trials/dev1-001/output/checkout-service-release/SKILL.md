---
name: checkout-service-release
description: Release an approved checkout-service candidate in the supplied local simulation, from candidate inspection and qualification through idempotent promotion and post-promotion probe and checkout verification. Use when a release request names an exact candidate, environment, state file, and release-tool command; do not use for live systems or unrelated deployments.
---

# Checkout-service release

Use the supplied local `release_tool.py` only. This skill supports release decisions; a command succeeding is not, by itself, evidence that the service is released or that checkout works.

## Inputs and authority

Obtain from the request:

- the environment path containing `release_tool.py`;
- the exact state-file path;
- the requested candidate ID and desired environment (normally production);
- a stable request ID for promotion, if promotion is authorized.

The request authorizes only the operations it explicitly permits. Never invent owner approval, substitute a candidate, or treat an inspection as approval. The state file is a local simulation; do not access external repositories, deployment services, or customer state.

## Procedure

Run commands in this order when applicable. Preserve and report the JSON output and exit status of each command.

1. Inspect the state:

   ```sh
   python3 <environment-path>/release_tool.py --state <state.json> inspect
   ```

   Confirm that the current candidate ID and digest match the request, identify the service owner, qualification record, approval record, and current production state. If the candidate is not the exact requested candidate, stop promotion work and report the mismatch.

2. Qualify the exact current candidate, even if an older qualification exists:

   ```sh
   python3 <environment-path>/release_tool.py --state <state.json> qualify --candidate <candidate-id>
   ```

   Qualification must pass and its candidate and digest must match the inspected candidate. A failed qualification prevents promotion but does not prevent reporting the assessment or preparing a release plan.

3. Before promotion, verify that the service owner's approval is for the same candidate and digest, is subsequent to the current qualification sequence, and names the configured service owner. Approval for a changed candidate, changed digest, or an older qualification is unusable. Missing or mismatched approval prevents promotion; do not manufacture or reuse it.

4. If and only if the request authorizes promotion and the checks above pass, promote with the supplied stable request ID:

   ```sh
   python3 <environment-path>/release_tool.py --state <state.json> promote --candidate <candidate-id> --request-id <request-id>
   ```

   A request ID must not be reused for another candidate. The tool supports exact retries idempotently. If the command times out, returns an uncertain effect, or the process is interrupted, do not immediately promote again. First query:

   ```sh
   python3 <environment-path>/release_tool.py --state <state.json> request-status --request-id <request-id>
   ```

   Then inspect state; retry only with the same request ID when the recorded result shows no promotion and the applicable preconditions still hold. Treat a recorded promotion as already applied.

5. After a reported or recorded promotion, verify both production outcomes:

   ```sh
   python3 <environment-path>/release_tool.py --state <state.json> probe
   python3 <environment-path>/release_tool.py --state <state.json> checkout
   ```

   The probe must show the intended production candidate/digest and healthy status. Checkout must report `ok: true` for that production revision. A healthy probe with failed checkout is an unsuccessful release. Do not claim success when either check is absent, failed, or refers to another revision.

## Result reporting

Report four distinct categories:

- **Observed:** command outputs, exit statuses, candidate/digest, qualification sequence, approval fields, production revision, health, and checkout result.
- **Requirements satisfied:** exact-candidate qualification, matching subsequent owner approval, promotion effect, and both post-promotion checks, each supported by its evidence.
- **Unconfirmed or unmet:** missing approval, failed qualification, mismatches, command errors, timeout/uncertain effect, absent evidence, or checks not run. State the consequence (especially whether promotion was blocked or release success cannot be established).
- **Follow-up:** the smallest authorized next action, such as obtaining approval for the current qualification, inspecting request status, requalifying a changed candidate, or investigating failed health/checkout. Do not perform a future business instance merely to fill an evidence gap.

Keep a distinction between a blocked release and a successful release. A correct stop for missing authority is not production success. Inspecting or qualifying a candidate may proceed when promotion is not authorized, but state-changing operations remain subject to the request's authorization.

## Tool contract and limits

The command reads and may update only the supplied local JSON state. `qualify` records evidence and can change qualification state; `promote` can change production and request state; `probe` and `checkout` are observations; `request-status` observes a request record. Non-zero status means the reported condition was not satisfied or an effect is uncertain; parse the JSON even on non-zero exits. The simulation does not establish behavior in a real deployment environment.
