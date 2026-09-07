# Checkout release rehearsal assessment

**Outcome:** `rel-onyx-27` was promoted in `development-onyx` and the service is healthy, but the requested release outcome was **not achieved** because the checkout exercise failed for that production revision.

## Observed

- Initial inspection (exit `0`) found exact candidate `rel-onyx-27`, digest `onyx27-content-c82d6e`, in environment `development-onyx`. Production was still `rel-onyx-26`.
- Existing qualification passed for the exact candidate and digest at sequence `207`. The matching approval was from the inspected service owner, `Rowan (checkout service owner)`, referred to qualification sequence `207`, and was later at sequence `208`. A new qualification was therefore not needed.
- The one promotion invocation used request ID `dev-onyx-27-rehearsal`. It returned exit `75` with `response timeout; operation effect unconfirmed by this response`.
- Before any retry, `request-status` (exit `0`) reported the original request as `promoted: true` for the exact candidate and digest. Re-inspection (exit `0`) confirmed production at `rel-onyx-27` / `onyx27-content-c82d6e` and `promotion_count: 1`. No retry was made.
- `probe` exited `0` and reported the requested production revision as healthy with `ok: true`.
- `checkout` exited `2` and reported `ok: false` for that same revision.

## Requirements satisfied

- Candidate, digest, and environment matched the request.
- Qualification and subsequent service-owner approval matched the exact candidate and digest.
- Promotion was confirmed without duplicating the uncertain request.
- Production revision/digest and service health were verified.

## Blocked or failed

- Working checkout is failed. Deployment and health alone do not establish the intended release outcome, so this rehearsal is not production-ready by the stated acceptance conditions.

## Unconfirmed

- None regarding the promotion effect: request status and post-promotion inspection resolved the timeout.

## Follow-up

Investigate and remediate the checkout failure for `rel-onyx-27`, then re-run qualification and obtain a new matching owner approval if candidate content or qualification evidence changes. A fresh authorized release request would then need promotion and both probe and checkout verification. No repair or rollback was attempted because neither was authorized.
