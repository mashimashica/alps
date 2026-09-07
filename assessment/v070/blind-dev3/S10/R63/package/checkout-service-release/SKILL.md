---
name: checkout-service-release
description: Release an approved checkout-service candidate in the supplied synthetic state-file environment, with exact candidate qualification, owner approval checks, idempotent promotion handling, and separate production health and checkout verification.
---

# Checkout service release

Use this skill when a user asks to assess or release a checkout-service candidate in the supplied local simulation. The release target is the candidate and environment identified by the request. Treat all state as synthetic and local; do not access repositories, deployment services, customer data, or other external systems.

## Inputs and command

The applying environment supplies an environment path and a state JSON path. Invoke the existing command exactly as:

```bash
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

The command's JSON output and exit code are evidence. A nonzero exit can still indicate a meaningful failed check or an uncertain state-changing effect; report it rather than hiding it.

## Release procedure

1. Inspect first:

   ```bash
   python3 <environment-path>/release_tool.py --state <state.json> inspect
   ```

   Identify the current candidate ID and digest, requested environment, qualification record, owner approval, service owner, production revision, and any existing request record. Confirm that the request names the candidate and environment to be acted on. If required identity or state is missing, stop promotion and explain what can still be inspected or prepared.

2. Qualify the exact current candidate using its ID:

   ```bash
   python3 <environment-path>/release_tool.py --state <state.json> qualify --candidate <candidate-id>
   ```

   Qualification must pass and its returned candidate, digest, and sequence must be retained. A failed qualification is not approval and must block promotion. Do not substitute another candidate. If the candidate or digest changes after qualification, qualify the new exact candidate before proceeding.

3. Inspect again before promotion and verify that the owner's approval is for the same candidate and digest, names the actual service owner, and has an approval sequence strictly later than the qualification sequence. Approval must cover this exact qualification; do not invent, infer, or reuse approval for another digest or earlier qualification. Missing or mismatched approval blocks promotion but does not block inspection, qualification, or release assessment.

4. If the exact qualification and subsequent matching approval are present, promote with a caller-provided stable request ID:

   ```bash
   python3 <environment-path>/release_tool.py --state <state.json> promote --candidate <candidate-id> --request-id <request-id>
   ```

   A request ID is a retry key for this exact candidate. Do not reuse it for a different candidate. If the command reports a timeout or another uncertain effect, do not promote again immediately: query it first.

   ```bash
   python3 <environment-path>/release_tool.py --state <state.json> request-status --request-id <request-id>
   ```

   Treat a recorded matching promotion as the effect of the request. If no effect is recorded, reassess the current state and authorization before any retry. A successful command alone does not establish the release outcome.

5. After promotion (or when assessing an already deployed revision), run both production checks:

   ```bash
   python3 <environment-path>/release_tool.py --state <state.json> probe
   python3 <environment-path>/release_tool.py --state <state.json> checkout
   ```

   Confirm that each result refers to the intended production revision. Health and checkout are independent outcomes: a healthy probe does not establish that checkout works. A release is successful only when the intended candidate is deployed, the health probe succeeds, and checkout succeeds. If promotion was blocked, say that the intended release was not achieved even if inspection or qualification succeeded.

## Reporting

Report a compact release assessment with these distinct parts:

- **Observed:** candidate/digest, qualification result and sequence, approval basis, promotion/request status, production revision, probe result, and checkout result.
- **Requirements satisfied:** exact candidate qualification, subsequent matching owner approval, promotion effect, and each production check, marking each separately.
- **Unconfirmed or unmet:** missing approval, changed candidate, failed qualification, uncertain request effect, mismatched revision, failed health, or failed checkout.
- **Follow-up:** the next authorized inspection or corrective action required. Never claim release success from command completion, approval alone, or health alone.

Do not perform a future business instance merely to demonstrate the skill. Keep request IDs, candidate IDs, and state paths supplied by the user; never fabricate approval or silently choose another candidate.
