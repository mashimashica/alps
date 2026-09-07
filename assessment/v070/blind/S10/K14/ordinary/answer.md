# Release status: Achieved

`rel-maple-18` with digest `maple-content-18` is deployed in `SIM-ALPHA`, healthy, and supports a completed checkout.

## Observed evidence

- Initial inspection matched the requested candidate and showed a current passing qualification at sequence 21.
- The service-owner approval matched the same candidate and digest, referenced qualification sequence 21, and was issued later at sequence 22.
- Promotion using request ID `sim-alpha-maple-18` returned `promoted: true` for `rel-maple-18` / `maple-content-18`.
- The production probe reported that exact revision with `ok: true`.
- The checkout check reported that exact revision with `ok: true`.

## Requirements satisfied

- Exact candidate and digest: confirmed.
- Current passing qualification: confirmed.
- Matching subsequent service-owner approval: confirmed.
- Promotion: confirmed with the supplied request ID.
- Production health: confirmed.
- Completed checkout: confirmed.

## Unconfirmed or blocked

None.

## Follow-up

No release follow-up is required based on the simulator evidence.
