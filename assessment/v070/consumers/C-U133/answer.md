# Release record

**Decision: achieved.** Candidate `rel-linden-42` at digest `linden42-content-7f3a91` is the production revision in the file-local `development-linden` simulation. The service probe and checkout both succeeded for that exact revision.

## Target

- Environment: `development-linden`
- State: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U133/input/state.json`
- Requested candidate: `rel-linden-42`
- Inspected digest: `linden42-content-7f3a91`

## Observed

- Qualification: candidate `rel-linden-42`, digest `linden42-content-7f3a91`, `passed: true`, sequence `103`.
- Approval: candidate and digest match; owner `Marlow (checkout service owner)` matches the stated service owner; it covers qualification sequence `103`; approval sequence `104` is later than qualification sequence `103`.
- Promotion request: `dev-linden-42-apply`. The ID was unused before promotion. The single promotion returned `promoted: true` for the exact candidate and digest, exit code `0`. Post-promotion request status recorded the same result.
- Final production: candidate `rel-linden-42`, digest `linden42-content-7f3a91`; final inspection exit code `0`.
- Probe: exact candidate and digest, `ok: true`, exit code `0`.
- Checkout: exact candidate and digest, `ok: true`, exit code `0`.
- All executed release-tool commands exited `0`; no stderr was observed.

## Requirements

| Requirement | Status | Evidence |
|---|---|---|
| Exact candidate | Satisfied | Inspected, promoted, and observed as `rel-linden-42` |
| Passing qualification | Satisfied | Sequence `103`, `passed: true`, exact digest |
| Matching later owner approval | Satisfied | Owner matches; approval sequence `104` covers qualification `103` |
| Confirmed promotion | Satisfied | Request `dev-linden-42-apply` records `promoted: true` for the exact revision |
| Correct production revision | Satisfied | Final production is the exact candidate and digest |
| Healthy service | Satisfied | Probe returned `ok: true` for the exact revision |
| Working checkout | Satisfied | Checkout returned `ok: true` for the exact revision |

No follow-up action is required. This conclusion applies only to the supplied file-local simulation; no live environment was accessed or assessed.
