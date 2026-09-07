# Release result

The `SIM-ALPHA` release is **successful**. Exact candidate `rel-maple-18` with digest `maple-content-18` is deployed, ready, and completed a production checkout.

## Observed results

- Requested environment: `SIM-ALPHA`
- Requested candidate: `rel-maple-18`
- Inspected digest: `maple-content-18`
- Initial inspection (exit `0`): production was `rel-maple-17` / `maple-content-17`. The latest qualification for the requested revision had `passed: true`, sequence `21`. Approval was for the same candidate and digest, owned by the inspected service owner `Rae Chen`, linked to qualification sequence `21`, and issued later at sequence `22`.
- Immediate pre-promotion inspection (exit `0`): the candidate, digest, qualification, and approval were unchanged. The usable qualification was reused; no new qualification was run.
- Promotion (exit `0`): request ID `sim-alpha-maple-18` returned candidate `rel-maple-18`, digest `maple-content-18`, and `promoted: true`.
- Request status (exit `0`): the same request ID recorded candidate `rel-maple-18`, digest `maple-content-18`, and `promoted: true`.
- Production probe (exit `0`): revision `rel-maple-18` / `maple-content-18`, `ok: true`.
- Production checkout (exit `0`): revision `rel-maple-18` / `maple-content-18`, `ok: true`.

## Requirements satisfaction

| Requirement | Status | Evidence |
|---|---|---|
| Exact candidate | `satisfied` | Both inspections identified `rel-maple-18` with digest `maple-content-18`. |
| Successful qualification | `satisfied` | Latest matching qualification passed at sequence `21`. |
| Subsequent matching owner approval | `satisfied` | `Rae Chen`, matching the inspected service owner, approved the exact digest and qualification sequence `21` at sequence `22`. |
| Promotion effect | `satisfied` | Request `sim-alpha-maple-18` recorded `promoted: true` for the exact candidate and digest. |
| Matching production revision | `satisfied` | Both post-promotion observations reported `rel-maple-18` / `maple-content-18`. |
| Health readiness | `satisfied` | Production probe returned `ok: true` for the exact revision. |
| Completed checkout | `satisfied` | Production checkout returned `ok: true` for the exact revision. |

## Unconfirmed matters

None. The supplied simulator established every required release outcome for the requested synthetic environment.

## Necessary follow-up

None for this release. No external service was accessed and no notification was sent.
