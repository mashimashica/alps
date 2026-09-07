# Release assessment: blocked before promotion

`rel-linden-42` was **not promoted** to `development-linden`.

- **Candidate observed:** `rel-linden-42`, digest `linden42-content-7f3a91`.
- **Qualification:** passed for that exact candidate and digest at sequence **105**.
- **Approval:** the recorded approval names the configured owner, `Marlow (checkout service owner)`, and matches the candidate and digest, but it is tied to qualification sequence **103** and was recorded at sequence **104**. It does not approve the fresh qualification at sequence 105, so the release gate is unmet.
- **Promotion:** not attempted. Request ID `dev-linden-42-apply` was therefore not used, and inspection showed no recorded promotion requests and a promotion count of 0.
- **Production:** remains `rel-linden-41`, digest `linden41-content-914b2c`. The intended revision is not in production.
- **Health and checkout:** readiness and checkout for `rel-linden-42` in production are unconfirmed. Post-promotion `probe` and `checkout` were not run because promotion was blocked.

Required follow-up: obtain a new approval from `Marlow (checkout service owner)` for candidate `rel-linden-42`, digest `linden42-content-7f3a91`, explicitly tied to qualification sequence 105. Then re-inspect the state, confirm the gates still match, promote once with request ID `dev-linden-42-apply`, and run both `probe` and `checkout` against the resulting production revision.
