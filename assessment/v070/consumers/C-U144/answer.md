# Checkout release rehearsal assessment

**Overall outcome: not achieved.** The approved candidate was promoted and is ready, but checkout failed on the exact production revision. This is a confirmed deployment with unsuccessful production behavior.

## Target

- Environment: `development-onyx`, explicitly bound by the request to the supplied file-local state
- Candidate: `rel-onyx-27`
- Pinned digest: `onyx27-content-c82d6e`
- Promotion request ID: `dev-onyx-27-rehearsal`

## Observed results

- Initial and immediate pre-promotion inspections both found the exact requested candidate and digest.
- The existing qualification passed for that exact content at sequence `207`. It was preserved rather than rerun because a fresh qualification would have made the existing approval stale.
- Approval was valid: sequence `208` matched the candidate and digest, named `Rowan (checkout service owner)`, referenced qualification sequence `207`, and followed the qualification.
- The promotion command returned exit `75` with a response timeout, so its response did not confirm the effect.
- `request-status` for the same request ID returned exit `0` and recorded `promoted: true` for `rel-onyx-27` / `onyx27-content-c82d6e`. No retry was issued. A subsequent inspection showed that exact revision in production and `promotion_count: 1`.
- Readiness probe: exit `0`, `ok: true`, exact requested revision and digest.
- Checkout: exit `2`, `ok: false`, exact requested revision and digest.

## Requirements satisfaction

| Requirement | Status | Evidence |
| --- | --- | --- |
| Candidate and environment identity | Satisfied | Request-bound environment and inspected candidate are `development-onyx` / `rel-onyx-27`; digest pinned as `onyx27-content-c82d6e`. |
| Qualification | Satisfied | Exact candidate and digest passed at sequence `207`. |
| Service-owner approval | Satisfied | Rowan's matching approval at sequence `208` covers qualification `207`. |
| Confirmed promotion | Satisfied | Same-ID request status recorded the exact candidate and digest as promoted; production inspection matched; promotion count was one. |
| Readiness | Satisfied | Post-promotion probe returned `ok: true` on the exact revision. |
| Checkout | Failed | Post-promotion checkout returned `ok: false` and exit `2` on the exact revision. |

## Follow-up and limits

The checkout failure must be diagnosed and remediated before this revision can meet the requested production outcome. No repair or rollback was attempted: neither is supported by the supplied interface, and repair was outside this request. Any corrected candidate would need its own matching passing qualification, subsequent service-owner approval, and separately authorized promotion. There are no unresolved questions about this rehearsal's promotion effect or the identity observed by either production check.
