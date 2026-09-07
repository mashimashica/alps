# Checkout release rehearsal assessment

**Outcome:** Candidate `rel-onyx-27` was promoted once in the `development-onyx` simulation, but the release outcome was **not successful** because checkout verification failed. The service is ready/healthy, while working checkout remains unmet.

## Observed

- Initial inspection (exit 0) identified candidate `rel-onyx-27` at digest `onyx27-content-c82d6e`; production was still `rel-onyx-26` at digest `onyx26-content-58e1af`.
- Existing qualification covered the exact candidate and digest, reported `passed: true`, and had sequence 207.
- Existing approval covered the same candidate and digest, named the current service owner `Rowan (checkout service owner)`, referenced qualification sequence 207, and had later sequence 208.
- Promotion used the authorized stable request ID `dev-onyx-27-rehearsal`. The promotion command exited 75 with a response timeout and said its effect was unconfirmed by that response.
- Request-status for that same ID exited 0 and confirmed `promoted: true` for `rel-onyx-27` / `onyx27-content-c82d6e`. No promotion retry was issued.
- Post-promotion inspection (exit 0) showed production at the exact requested candidate and digest, with `promotion_count: 1`.
- Production probe exited 0 and reported `ok: true` for the requested revision.
- Production checkout exited 2 and reported `ok: false` for the requested revision.

## Requirements satisfied

- Candidate identity, digest, environment, service owner, qualification, and approval matched exactly before promotion.
- Approval sequence 208 was later than the covered qualification sequence 207.
- The single authorized logical promotion was resolved idempotently through its request status after the uncertain response.
- Production contains the requested candidate and digest, and the service health requirement passed.

## Unconfirmed or unmet

- Working checkout is unmet: the checkout check returned `ok: false` with exit 2.
- Therefore the complete release outcome—intended approved revision, ready service, and working checkout—has not been achieved, despite confirmed deployment and a passing health probe.

## Follow-up

Investigate and repair the checkout failure for `rel-onyx-27`, then obtain authorization for any further state-changing action. No repair, rollback, or additional promotion was performed because none was authorized. After an authorized remediation, re-establish the exact candidate/digest qualification and approval basis as needed and rerun both production checks.
