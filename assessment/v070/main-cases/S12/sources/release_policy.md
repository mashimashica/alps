# SW-RCV-04 — Inbound replacement-parts release review

Owner: Stonewake quality and receiving leads  
Revision: 4, effective 2026-08-03  
Status: unchanged by the tool upgrade

The review concerns replacement mechanical parts counted in individual pieces. It produces a recommendation and exceptions for a receiving lead; it never posts a stock movement or grants a quality clearance.

Review each combination of site, shipment, SKU, and lot. The four fields jointly identify the stock under review; a same-SKU total across shipments or lots is not a substitute. Stonewake treats these four identifiers as case-insensitive and ignores surrounding whitespace, but leading zeros are significant. Do not infer an omitted identifier or merge different lot identifiers.

A release recommendation requires all of the following evidence:

- A manifest and a posted physical-count record are both present for the same complete identity. Repeated manifest lines for that identity are additive. Count events are additive signed changes, not replacement snapshots; a signed correction reverses or adjusts earlier evidence.
- Net good pieces exactly match the manifested pieces, with no negative net total. Manifest lines and individual count events must use whole-piece quantities; fractional rows are invalid even if their totals happen to be whole. Do not round a discrepancy away. A missing side or a count represented only by pending events is unknown, not zero.
- Net damaged pieces are zero, and there are no unresolved pending count events. A correction awaiting posting cannot cancel a posted damaged quantity yet. Quantity agreement alone does not clear damage or a pending recount.
- The matching current quality-context record says supplier release is `cleared`, transport seal is `intact`, and traceability is `complete`. An absent, stale, unknown, or conflicting record needs the relevant quality evidence resolved, not an assumed clearance. The packet's `review_date` must match the date the lead requested for this review.
- A lot marked as a restricted part needs explicit quality-owner release approval in addition to the preceding conditions. An empty `quality_owner_approval_ref` is not approval. Ordinary, nonrestricted lots do not need this extra approval.

When evidence is inconsistent or incomplete, identify the particular lot, the unresolved condition, the available evidence, and the owner of the next check. The receiving counter resolves manifest/count discrepancies and fractional or negative count problems. The quality lead resolves damage, seals, supplier release, traceability, conflicting or stale quality context, and restricted-part approval. The receiving lead may only release once the required evidence is resolved; do not present a tool failure or missing input as an all-clear.

`demo/quality_context.csv` illustrates the quality-context interface: the four identity fields, `review_date`, `supplier_release`, `transport_seal`, `traceability`, `restricted_part`, `quality_owner_approval_ref`, and `context_ref`. Allowed state values are respectively `cleared|hold|unknown`, `intact|broken|unknown`, `complete|incomplete|unknown`, and `yes|no`. These facts and approvals are supplied by their owners; the quantity tool does not evaluate or refresh them. Preserve the context reference alongside the quantity source references in the review.

For the demonstration only, the receiving lead requested a review dated 2026-08-24. All records in the demonstration are fictional and local. For later work, establish the requested review date from that packet instead of reusing this example date.
