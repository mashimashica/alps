---
name: release-checkout-service
description: Release an identified checkout-service candidate to its requested environment using local release tooling, with exact candidate qualification, subsequent owner approval, idempotent promotion handling, and production probe plus checkout evidence. Use for synthetic or authorized release requests; do not infer approval or treat deployment success alone as release success.
---

# Checkout-service release

Perform the requested release only in the supplied, authorized environment. The request must identify the candidate and desired environment; preserve that scope throughout. The release tool is a local simulation/CLI and is invoked as:

```bash
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

## Release procedure

1. Inspect state before acting. Record the current candidate `id` and `digest`, service owner, production revision, qualification, approval, and any relevant request records. If the requested candidate is absent or does not match the current candidate, stop and report the mismatch.
2. Qualify exactly the requested candidate:

   ```bash
   python3 <environment-path>/release_tool.py --state <state.json> qualify --candidate ID
   ```

   Require a successful result whose candidate and digest match the inspected candidate. A failed qualification blocks promotion but does not block reporting or further inspection.
3. Re-check approval basis from state. Promotion requires approval by the recorded service owner for the same candidate and digest, with `qualification_sequence` equal to the successful qualification sequence and approval sequence strictly later than it. Changed candidate content, a new failed qualification, or a missing/mismatched approval makes promotion unauthorized. Never invent approval or substitute another candidate.
4. If the basis matches, promote with a stable request identifier supplied by the caller (or generate one that is unique for this release attempt):

   ```bash
   python3 <environment-path>/release_tool.py --state <state.json> promote --candidate ID --request-id REQUEST_ID
   ```

   A successful response is evidence of the tool result, not yet of a healthy checkout service. If the command times out or otherwise leaves the effect uncertain, do not repeat `promote`; query the same request ID first:

   ```bash
   python3 <environment-path>/release_tool.py --state <state.json> request-status --request-id REQUEST_ID
   ```

   Retry only through the same request ID when the tool's recorded request state supports an exact idempotent retry. A request ID belonging to a different candidate is an error.
5. After confirmed promotion, run both production checks:

   ```bash
   python3 <environment-path>/release_tool.py --state <state.json> probe
   python3 <environment-path>/release_tool.py --state <state.json> checkout
   ```

   Confirm that probe and checkout report the promoted revision and both succeed. A healthy probe without a successful checkout is a failed release outcome.

## Reporting

Return a concise assessment that separates:

- observed results and exact evidence (candidate/digest, qualification sequence, approval basis, promotion/request status, probe, checkout);
- requirements satisfied;
- requirements not satisfied or blocked (including missing approval, failed qualification, revision mismatch, or failed checkout);
- unconfirmed matters and necessary follow-up.

Do not claim the intended production result from a successful command, a promotion record, or a health probe alone. If approval is missing, stop before promotion while still reporting inspection and qualification results. Keep local simulation state and caller-provided identifiers within the authorized environment; do not access external repositories, deployments, customer data, or live business systems.
