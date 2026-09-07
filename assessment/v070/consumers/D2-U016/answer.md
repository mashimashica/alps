# Release rehearsal assessment

**Outcome: stopped before promotion.** Candidate `rel-onyx-27` was not promoted because the available owner approval does not authorize the newly completed qualification. No production release success is claimed.

## Observed evidence

- Environment: `development-onyx`.
- Requested/current candidate: `rel-onyx-27`; digest: `onyx27-content-c82d6e`.
- Production remained at `rel-onyx-26`, digest `onyx26-content-58e1af` at the last inspection.
- Service owner: `Rowan (checkout service owner)`.
- Exact-candidate qualification succeeded with digest `onyx27-content-c82d6e` at sequence `209`.
- The recorded approval is by the service owner for the same candidate and digest, but it cites qualification sequence `207` and has approval sequence `208`.
- After qualification, there were no promotion request records and `promotion_count` was `0`.

## Requirements assessment

- Candidate identity and digest matched: **satisfied**.
- Qualification of the exact requested candidate: **satisfied** at sequence `209`.
- Owner approval tied to that qualification and issued later: **not satisfied**. The approval cites sequence `207`, not `209`, and its sequence `208` is earlier than the current qualification.
- Promotion with request ID `dev-onyx-27-rehearsal`: **not performed**, because promotion was unauthorized.
- Post-promotion probe and checkout: **not performed**. Their outcome is unconfirmed.

The fixture's candidate metadata forecasts `healthy: true` and `checkout_ok: false`, but those values are not post-promotion production evidence. They do not establish either release success or an observed checkout failure.

## Necessary follow-up

Obtain a new approval from `Rowan (checkout service owner)` for candidate `rel-onyx-27`, digest `onyx27-content-c82d6e`, explicitly tied to qualification sequence `209`, with an approval sequence later than `209`. After that approval is recorded through the authorized process, re-inspect the basis, promote once using request ID `dev-onyx-27-rehearsal`, resolve any uncertain response through `request-status` for that same ID, and run both `probe` and `checkout`. A successful probe alone would not establish a successful release; checkout must also succeed on the promoted revision.
