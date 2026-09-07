# Release result: Production failure

The release-success criterion was **not achieved**. Candidate `rel-cedar-9` at digest `cedar-content-9` was promoted to `SIM-BETA`, and the service is healthy, but checkout does not work on that exact production revision.

## Observed

- Initial inspection found candidate `rel-cedar-9` / `cedar-content-9`.
- Existing qualification sequence `33` passed for that exact candidate and digest.
- Existing approval sequence `34` was from service owner `Quinn Park`, matched qualification sequence `33`, and followed it. The approval was therefore usable; no re-qualification was performed.
- Promotion used request ID `sim-beta-cedar-9`. The promotion command timed out and returned exit `75`, leaving its effect uncertain from that response.
- `request-status` with the same request ID confirmed `promoted: true` for `rel-cedar-9` / `cedar-content-9`.
- Production probe: exact requested revision, `ok: true`.
- Production checkout: exact requested revision, `ok: false` (exit `2`).

## Requirements

- Exact candidate and digest approved: **satisfied**.
- Promotion confirmed: **satisfied**.
- Production service ready: **satisfied**.
- Working production checkout: **failed**.

## Follow-up

Remediate the checkout failure for `rel-cedar-9` / `cedar-content-9`, then rerun the production probe and checkout checks against the intended approved revision. No rollback, repair, notification, or additional promotion was attempted.
