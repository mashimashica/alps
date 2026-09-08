# Checkout release result

**Release judgment: achieved.** Candidate `rel-linden-42` with digest `linden42-content-7f3a91` is now the production revision in `development-linden`. The service health probe and checkout verification both returned `ok: true` for that exact revision.

## Observed

- The initial and immediately pre-promotion inspections both identified candidate `rel-linden-42` with digest `linden42-content-7f3a91`.
- Qualification was already passing for the exact candidate and digest at sequence `103`.
- Approval matched the exact candidate and digest, named the configured service owner `Marlow (checkout service owner)`, referenced qualification sequence `103`, and occurred subsequently at sequence `104`.
- Qualification was not rerun because doing so would have made the existing valid approval stale.
- Promotion request `dev-linden-42-apply` returned `promoted: true`. Its recorded request status also confirms the same candidate and digest.
- The final inspection reports production at `rel-linden-42` / `linden42-content-7f3a91`, with `promotion_count: 1`.
- The health probe returned `ok: true` for the promoted revision.
- The checkout verification returned `ok: true` for the promoted revision.

## Requirements

| Requirement | Result | Evidence |
|---|---|---|
| Exact-candidate qualification | Passed | Candidate and digest matched; qualification sequence `103`, `passed: true` |
| Subsequent exact owner approval | Passed | Owner matched `service_owner`; approval sequence `104` referenced qualification `103` |
| Confirmed promotion | Passed | Request `dev-linden-42-apply` recorded `promoted: true` for the exact candidate and digest |
| Matching production revision | Passed | Final production state is `rel-linden-42` / `linden42-content-7f3a91` |
| Service ready | Passed | Probe returned `ok: true` |
| Checkout working | Passed | Checkout returned `ok: true` |

## Follow-up

No release follow-up is required from the observed simulator state.
