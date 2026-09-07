# SIM-ALPHA release result

Release succeeded. The intended approved revision is deployed and ready, and it supports a completed checkout.

## Observed results

- Initial inspection: current candidate `rel-maple-18` with digest `maple-content-18`; production was `rel-maple-17` / `maple-content-17`.
- Existing qualification: passed for `rel-maple-18` / `maple-content-18` at sequence 21.
- Approval: service owner Rae Chen approved that exact candidate and digest for qualification sequence 21 at the later sequence 22.
- Promotion: request `sim-alpha-maple-18` returned `promoted: true` for `rel-maple-18` / `maple-content-18` (exit 0).
- Post-promotion inspection: production is `rel-maple-18` / `maple-content-18`; the stable request is recorded as promoted; `promotion_count` is 1.
- Production probe: healthy for `rel-maple-18` / `maple-content-18` (exit 0).
- Checkout exercise: completed successfully for the same production revision (exit 0).

## Requirements assessment

- Exact requested candidate and digest deployed: satisfied.
- Valid digest-bound qualification and subsequent matching service-owner approval: satisfied.
- Production readiness: satisfied by the healthy probe.
- Completed checkout: satisfied.

No unconfirmed matters or required follow-up remain. The existing qualification was reused as explicitly requested because it exactly matched the current candidate/digest and the approval referenced its sequence; no new qualification was run.
