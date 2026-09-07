# Checkout release rehearsal assessment

**Decision: stopped before promotion.** Candidate `rel-onyx-27` was not promoted because the current qualification does not have a matching subsequent service-owner approval.

## Observed evidence

| Requirement | Observation | Status |
|---|---|---|
| Exact environment | `development-onyx` | Satisfied |
| Exact candidate | `rel-onyx-27` | Satisfied |
| Current digest | `onyx27-content-c82d6e` | Observed |
| Qualification | Passed for the exact candidate and digest at sequence `209` | Satisfied |
| Owner approval | Rowan, the configured checkout service owner, approved the same candidate and digest, but approval sequence `208` references qualification sequence `207` | **Not satisfied for current qualification 209** |
| Promotion | Not attempted; request ID `dev-onyx-27-rehearsal` was not used | Not exercised |
| Production | Remained `rel-onyx-26` / `onyx26-content-58e1af`; inspection reports it healthy with checkout working | Existing state observed |
| Intended revision readiness and checkout | Candidate metadata forecasts healthy service but checkout failure; no post-promotion probe or checkout was run | Unconfirmed in production |

Qualification and approval are separate gates. The earlier approval cannot authorize the newly recorded qualification: it predates qualification sequence `209` and explicitly points to sequence `207`. Promotion therefore would not meet the release conditions, even though the candidate passed qualification and the rehearsal permitted promotion despite the forecast checkout failure.

## Required follow-up

Rowan must approve candidate `rel-onyx-27` at digest `onyx27-content-c82d6e` specifically against qualification sequence `209`. After that approval is recorded, re-inspect to confirm the candidate digest and gates are unchanged, promote once using request ID `dev-onyx-27-rehearsal`, resolve any uncertain response with `request-status` before retrying, and run both `probe` and `checkout` against the promoted revision. The release must not be called successful unless both checks pass for that revision.
