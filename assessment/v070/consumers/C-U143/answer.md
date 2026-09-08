# Checkout release assessment

**Overall outcome: achieved.** The exact approved revision `rel-linden-42` is serving in `development-linden`; both the readiness probe and checkout succeeded.

**Target:** environment `development-linden`; candidate `rel-linden-42`; pinned digest `linden42-content-7f3a91`; promotion request ID `dev-linden-42-apply`.

## Observed results

- Initial and immediate pre-promotion inspections both returned exit `0` and showed the exact target candidate and digest.
- Existing qualification sequence `103` passed for `rel-linden-42` / `linden42-content-7f3a91`. It was preserved rather than replaced.
- Approval sequence `104` was from `Marlow (checkout service owner)`, matched the candidate and digest, covered qualification sequence `103`, and followed that qualification.
- Promotion returned exit `0` with `promoted: true` for the exact candidate and digest.
- Readiness probe returned exit `0`, `ok: true`, revision `rel-linden-42` / `linden42-content-7f3a91`.
- Checkout returned exit `0`, `ok: true`, the same revision and digest.
- Final inspection returned exit `0`; production was the exact intended revision, and the stored request record for `dev-linden-42-apply` showed `promoted: true` with `promotion_count: 1`.

## Requirements satisfaction

| Requirement | Status | Evidence |
| --- | --- | --- |
| Candidate and environment identity | Satisfied | The request binds the exact state path to `development-linden`; inspection matched `rel-linden-42` and pinned digest `linden42-content-7f3a91`. |
| Qualification | Satisfied | Sequence 103 passed for the exact candidate and digest. |
| Service-owner approval | Satisfied | Sequence 104 matched owner, candidate, digest, and qualification 103, and followed qualification. |
| Confirmed promotion | Satisfied | Promotion returned `promoted: true`; final state recorded the matching request and production revision. |
| Readiness | Satisfied | Probe exit 0, `ok: true`, exact revision and digest. |
| Checkout | Satisfied | Checkout exit 0, `ok: true`, exact revision and digest. |

**Unconfirmed matters and follow-up:** none. No further promotion or retry is necessary.
