# Checkout release rehearsal assessment

## Observed

- The requested environment is `development-onyx` and the exact candidate is `rel-onyx-27` with digest `onyx27-content-c82d6e`.
- Fresh qualification passed for that exact candidate and digest at sequence 209.
- The service owner is `Rowan (checkout service owner)`. The available approval matches the candidate, digest, and owner, but it covers qualification sequence 207 and was recorded at sequence 208.
- Because that approval predates the fresh qualification at sequence 209, it does not approve the qualification used for this release decision.
- No promotion was attempted. Request ID `dev-onyx-27-rehearsal` therefore has no exercised or uncertain effect to resolve; inspection showed no request records and a promotion count of 0.
- Production remains `rel-onyx-26` with digest `onyx26-content-58e1af`. Its health probe passed and its checkout check passed.
- Inspection exposes `checkout_ok: false` on candidate `rel-onyx-27`, but this is candidate fixture data, not an observed production checkout result for that candidate.

## Requirements satisfied

| Requirement | Status | Basis |
|---|---|---|
| Exact candidate qualification | Satisfied | `rel-onyx-27` / `onyx27-content-c82d6e` passed at sequence 209. |
| Subsequent matching owner approval | Not satisfied | Matching approval sequence 208 covers qualification sequence 207, not the fresh qualification at 209. |
| Promotion effect | Not satisfied | Promotion was blocked and not attempted. |
| Intended revision health | Unconfirmed | The passing probe was for current production `rel-onyx-26`. |
| Intended revision checkout | Unconfirmed | The passing checkout was for current production `rel-onyx-26`. |

## Unconfirmed or unmet

The intended release was not achieved. Candidate `rel-onyx-27` is not deployed, and neither readiness nor working checkout has been observed for it in production. The uncertain-promotion recovery path was not exercised because no authorized promotion could begin.

## Follow-up

Obtain a new approval from `Rowan (checkout service owner)` for candidate `rel-onyx-27`, digest `onyx27-content-c82d6e`, explicitly covering qualification sequence 209, with an approval sequence later than 209. Then re-inspect to verify the candidate, digest, qualification, and approval are still aligned. If they are, promote once using request ID `dev-onyx-27-rehearsal`; if the response is uncertain, query that request ID before any retry. After a recorded promotion, run both the production probe and checkout check and confirm each reports `rel-onyx-27` / `onyx27-content-c82d6e`.
