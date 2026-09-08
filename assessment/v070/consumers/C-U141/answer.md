# Checkout release result

**Overall outcome: achieved.** Candidate `rel-linden-42` at digest `linden42-content-7f3a91` was promoted to the file-local `development-linden` simulation and was verified as ready with a working checkout.

## Observed results

- Environment mapping: `development-linden` was represented by `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U141/input/state.json`, as specified in the request. Initial inspection returned the same environment name.
- Requested candidate: `rel-linden-42`; observed candidate: `rel-linden-42` with digest `linden42-content-7f3a91`.
- Initial production: `rel-linden-41` at digest `linden41-content-914b2c`.
- Qualification: candidate `rel-linden-42`, digest `linden42-content-7f3a91`, `passed: true`, sequence `103` (inspection exit 0). It was reused rather than rerun because it already matched the exact content and approval.
- Owner approval: owner `Marlow (checkout service owner)` matched the nonempty `service_owner`; it bound the same candidate and digest to qualification sequence `103`, and approval sequence `104` followed that qualification.
- Promotion: request ID `dev-linden-42-apply` returned `promoted: true` for the exact candidate and digest (exit 0). `request-status` independently returned the same recorded result (exit 0).
- Final production: `rel-linden-42` at digest `linden42-content-7f3a91`; final inspection showed `promotion_count: 1` (exit 0).
- Readiness: `probe` identified the intended production revision and returned `ok: true` (exit 0).
- Working checkout: `checkout` identified the intended production revision and returned `ok: true` (exit 0).

## Requirements satisfaction

| Requirement | Status | Evidence |
| --- | --- | --- |
| Intended revision | Satisfied | Candidate and final production both identify `rel-linden-42` / `linden42-content-7f3a91`. |
| Qualification | Satisfied | Exact candidate and digest passed at sequence 103. |
| Exact owner approval | Satisfied | Marlow's sequence-104 approval binds the exact content to qualification 103. |
| Promotion/effect | Satisfied | Promotion and request-status both record `promoted: true`; final production matches. |
| Readiness | Satisfied | Production `probe.ok` is true for the intended revision. |
| Working checkout | Satisfied | Production `checkout.ok` is true for the intended revision. |

There are no unconfirmed release requirements or required follow-up actions based on the observed simulator evidence.
