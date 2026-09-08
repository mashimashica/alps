# Release assessment: achieved

The requested candidate `rel-linden-42` was released to the file-local `development-linden` simulation. The observed digest was `linden42-content-7f3a91`, and the promotion used request ID `dev-linden-42-apply`.

## Simulator observations

- Both the initial inspection and the immediate pre-promotion inspection reported environment `development-linden` and current candidate `rel-linden-42` with digest `linden42-content-7f3a91`.
- Qualification sequence `103` applied to that exact candidate and digest and had `passed: true`.
- Approval sequence `104` applied to that exact candidate and digest, named `Marlow (checkout service owner)` as owner, and referenced qualification sequence `103`. The state's `service_owner` was also `Marlow (checkout service owner)`.
- The promotion command exited `0` and returned `promoted: true` for `rel-linden-42` at digest `linden42-content-7f3a91`.
- The post-promotion probe exited `0`, observed that exact revision, and returned `ok: true` with `healthy: true`.
- The post-promotion checkout exited `0`, observed that exact revision, and returned `ok: true` with `checkout_ok: true`.

## Requirement judgments

| Requirement | Status | Basis |
| --- | --- | --- |
| Target mapping is the requested environment | Achieved | Inspection identified `development-linden` from the supplied state path. |
| Current candidate ID exactly matches the request | Achieved | Both inspections returned `rel-linden-42`. |
| Candidate, qualification, and approval digests exactly match | Achieved | All were `linden42-content-7f3a91`. |
| Qualification applies to the requested candidate and passed | Achieved | Qualification sequence `103` named `rel-linden-42` and returned `passed: true`. |
| Approval came from the recorded service owner | Achieved | Approval owner and `service_owner` both identified Marlow. |
| Approval covers the current qualification | Achieved | Approval referenced qualification sequence `103`. |
| Approval follows qualification | Achieved | Approval sequence `104` is greater than qualification sequence `103`. |
| Promotion used the authorized request identity | Achieved | Request ID `dev-linden-42-apply` was used once. |
| Exact approved revision is established in production | Achieved | Promotion returned the exact candidate and digest with `promoted: true`; both later production checks observed the same revision. |
| Production service is ready | Achieved | The matching post-promotion probe returned `ok: true`. |
| Checkout works | Achieved | The matching post-promotion checkout returned `ok: true`. |

No requirement is unmet, blocked, or unconfirmed, so no release follow-up is needed.
