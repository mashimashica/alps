# Release rehearsal assessment

**Overall result: release outcome not achieved.** Candidate `rel-onyx-27` was validly promoted to simulated `development-onyx`, and its service is healthy, but checkout failed for that exact production revision.

## Observations

- Initial and immediate pre-promotion inspections both returned environment `development-onyx`, candidate `rel-onyx-27`, and digest `onyx27-content-c82d6e`.
- The existing qualification passed for that exact candidate and digest at sequence `207`.
- The approval applies to that exact candidate and digest, names the configured service owner `Rowan (checkout service owner)`, references qualification sequence `207`, and follows it at sequence `208`.
- Production initially ran `rel-onyx-26` / `onyx26-content-58e1af`. There were no prior promotion requests, and `promotion_count` was `0`.
- Promotion used the supplied request ID `dev-onyx-27-rehearsal`. The promotion command returned exit `75` with a response-timeout message, so that response alone did not establish the effect.
- `request-status` for the same request ID returned exit `0` and a recorded result with `promoted: true` for `rel-onyx-27` / `onyx27-content-c82d6e`. No promotion retry was performed.
- The post-promotion probe returned exit `0`, the exact promoted revision, and `ok: true`.
- The post-promotion checkout returned exit `2`, the exact promoted revision, and `ok: false`.

## Requirement assessment

| Requirement | Status | Basis |
| --- | --- | --- |
| Requested candidate and environment are exact | Achieved | Both inspections matched `rel-onyx-27` and `development-onyx`. |
| Passing qualification covers current digest | Achieved | Qualification sequence `207` passed for `rel-onyx-27` / `onyx27-content-c82d6e`. |
| Matching service-owner approval follows qualification | Achieved | Approval by the configured owner references qualification `207`, covers the same ID and digest, and has later sequence `208`. |
| Promotion was authorized and used the supplied recoverable request identity | Achieved | The request authorizes simulator promotion and supplied `dev-onyx-27-rehearsal`. |
| Exact approved revision is established in production | Achieved | Same-ID request status recorded `promoted: true`; both production checks reported the exact candidate and digest. |
| Production service is ready | Achieved | Matching probe returned `ok: true`. |
| Checkout works in production | Unmet | Matching checkout returned `ok: false` and exit `2`. |
| Complete release outcome | Unmet | Working checkout is a required independent outcome and failed. |

## Follow-up

Investigate and repair checkout behavior for `rel-onyx-27` / `onyx27-content-c82d6e`, then rerun the checkout observation against that exact production revision. No repair or rollback was attempted because neither operation was authorized or supported by this request.
