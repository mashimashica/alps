# Checkout release assessment

The requested release was **not completed**. Candidate `rel-linden-42` with digest `linden42-content-7f3a91` passed qualification at sequence 105, but the recorded owner approval is tied to the earlier qualification at sequence 103 and was issued at sequence 104. Because it does not cover the current qualification, promotion was blocked and request ID `dev-linden-42-apply` was not used.

## Observed

- Environment: `development-linden`.
- Intended candidate: `rel-linden-42`, digest `linden42-content-7f3a91`.
- Qualification: passed for the exact candidate and digest at sequence 105.
- Service owner: `Marlow (checkout service owner)`.
- Approval: exact candidate, digest, and owner match, but it covers qualification sequence 103 and has approval sequence 104; it predates the current qualification.
- Promotion/request status: no promotion attempted; no request record exists; promotion count remains 0.
- Production remains `rel-linden-41`, digest `linden41-content-914b2c`.
- Production health probe: passed for `rel-linden-41`.
- Production checkout: passed for `rel-linden-41`.

## Requirements satisfied

- Exact candidate qualification: **satisfied**.
- Subsequent matching owner approval for that qualification: **not satisfied**.
- Promotion effect for `rel-linden-42`: **not satisfied**.
- Health probe for the intended revision: **not satisfied**; the passing probe refers to `rel-linden-41`.
- Checkout verification for the intended revision: **not satisfied**; the passing checkout refers to `rel-linden-41`.

## Unconfirmed or unmet

The intended candidate is not deployed, and neither production check verifies it. The current production revision is ready and its checkout works, but those results do not establish success for `rel-linden-42`.

## Follow-up

The service owner must approve candidate `rel-linden-42` / digest `linden42-content-7f3a91` specifically against qualification sequence 105. After that approval is recorded with a sequence later than 105, inspect again, promote with request ID `dev-linden-42-apply`, confirm the request effect, and run both production checks against `rel-linden-42`.
