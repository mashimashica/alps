# S05 independent consumer oracle

## Basis and evaluation boundary

These two synthetic packets and this oracle were derived only from `cases/S05/brief.md`, the raw Monthly Receiving Review business contract. They do not rely on a generated Skill, a target execution, an earlier case, an earlier oracle, or an implementation-specific interface. The identities and business events are new and fictional.

Judge whether the review makes the supported receipt position and the necessary follow-up clear. Do not require a particular report layout, category name, file format, draft template, number of drafts, or implementation. Grouping several lines in a recipient-specific draft is acceptable if the affected lines, evidence problem or quantity, and concrete next actions remain clear. Quantities listed in the recipient obligations below may be established across a clearly linked review and draft; every quantity need not be repeated inside each message. A calculation without the necessary recipient-specific follow-up is insufficient. No message may be sent, no supplier contacted, and no source or real receiving record mutated.

All supplied order lines remain in scope for the requested month, including lines with no event rows or no applicable coverage declaration. Completeness must come from the applicable manifest, not row count. A complete declaration does not cure conflicting or unidentified receiving evidence. Exact event copies count once; signed quantities are algebraic; other-month events and events for an unsupplied order do not change in-scope month quantities.

The packets use well-formed JSON and contract-shaped fields. They do not require a novel malformed-input policy. Missing applicable coverage in the challenging packet is an evidence gap, not permission to omit the line or assume completeness.

## Ordinary packet: June 2026

Input: `development-consumer-cases/S05/ordinary/input/receiving.json`.

Scope: six order lines across five orders, requested month `2026-06`.

### Supported line judgments

| Order / SKU | Ordered | Applicable evidence and signed calculation | Supported receipt position | Necessary follow-up |
| --- | ---: | --- | --- | --- |
| PO-R2606-410 / LABEL-60 | 120 | Complete; RCV-H1801 +75, H1802 +50, H1803 -5; the repeated H1801 is counted once; net 120. | Received as ordered. | None needed. |
| PO-R2606-410 / CARTON-M | 80 | Complete; RCV-H1804 +50 and H1805 -8; net 42. | Shortfall of 38. | Dana Ivers follows up with Mara Quinn about the remaining 38 cartons. |
| PO-R2606-411 / GLOVE-N | 60 | Complete; RCV-H1806 +66 and H1807 -2; net 64. | Excess of 4. | Noel Price reconciles the 4-unit surplus against the order and receiving evidence. |
| PO-R2606-412 / FILM-300 | 24 | Complete; RCV-H1808 +24; net 24. | Received as ordered. | None needed. |
| PO-R2606-413 / SEAL-BLUE | 40 | Explicitly incomplete; RCV-H1809 +35 and H1810 -5; observed subtotal 30. | Final receipt position unresolved. The packet does not establish a final shortfall of 10. | Simone Bell provides or confirms the complete June export before final comparison. |
| PO-R2606-414 / TAPE-48 | 30 | Complete June coverage with no June events; signed received quantity 0. | Shortfall of 30. | Dana Ivers follows up with Owen Malik about the remaining 30 tape units. |

Event IDs shortened after their first occurrence in a calculation retain the `RCV-` prefix shown in the input. The table is an oracle, not a required output format.

### Exact recipient and action obligations

- Purchasing owner: Dana Ivers `<dana.ivers@juniperworks.example>`. Supplier draft to Mara Quinn `<mara.quinn@harborpack.example>` must identify PO-R2606-410 / CARTON-M, ordered 80, received 42, remaining 38, and request a concrete confirmation or plan for the outstanding receipt. Supplier draft to Owen Malik `<owen.malik@bindwell.example>` must identify PO-R2606-414 / TAPE-48, ordered 30, received 0, remaining 30, and request the outstanding receipt confirmation or plan. The contract does not supply a deadline to impose.
- Warehouse recipient: Noel Price `<noel.price@juniperworks.example>`. Draft must identify PO-R2606-411 / GLOVE-N, 64 received against 60 ordered, and ask to reconcile the surplus of 4 against the order and receiving records. Do not automatically turn this into supplier shortfall follow-up or authorize a return or record correction.
- Data recipient: Simone Bell `<simone.bell@juniperworks.example>`. Draft must identify PO-R2606-413 / SEAL-BLUE and June 2026, the incomplete export and observed 30, and ask for the full export or confirmation of completeness so the final comparison can be completed. Leni Perez is the supplied supplier contact, but supplier chasing is not the evidence-remediation action established for this line.

Named recipients may be represented using their supplied names and/or supplied addresses as long as identity is clear. Do not fabricate a different address, owner, or contact.

### Evidence boundaries

- `RCV-H1801` appears twice with identical content. It is not a conflict and contributes +75 only once.
- `RCV-H1720` is a May carton receipt of +20. It does not contribute to June CARTON-M.
- `RCV-H1901` is a July film reversal of -4. It does not reduce June FILM-300.
- `RCV-H1811` is a June +90 event for unsupplied PO-R2606-499. It is outside the review; it neither adds a review line nor contaminates the supplied orders.
- The absence of TAPE-48 event rows does not prevent its final zero-received judgment because June coverage is expressly complete. Conversely, the partial SEAL-BLUE rows cannot establish a final shortage despite containing usable numbers.

## Challenging packet: July 2026

Input: `development-consumer-cases/S05/challenging/input/receiving.json`.

Scope: thirteen order lines across eleven orders, requested month `2026-07`.

### Supported line judgments

| Order / SKU | Ordered | Evidence and quantities | Supported receipt position | Necessary follow-up |
| --- | ---: | --- | --- | --- |
| PO-S2607-820 / BOLT-M8 | 100 | July coverage says complete; known matching events +70 +30 -10 give 90, but current-month RCV-K7105 names NUT-M8, a SKU absent from this order. | Final comparison blocked by the order-level receiving identity gap. Do not report a confirmed shortfall of 10. | Rowan Ames and Beck Lin reconcile RCV-K7105 with the order and receiving source records before either line's final comparison. |
| PO-S2607-820 / WASHER-M8 | 200 | July coverage says complete; known matching event is +200; the same RCV-K7105 order-level gap applies. | Final comparison blocked; do not claim received as ordered. | Same order-level identity reconciliation as BOLT-M8. |
| PO-S2607-821 / PACK-RACK | 48 | July coverage says complete. Uncontested RCV-K7106 is +20. RCV-K7107 has one version for this line (+18) and another for PO-S2607-822 / SHIELD-CLR (+12). | Conflicting evidence; no final received quantity or final shortfall. | Rowan Ames and Beck Lin reconcile the two source versions of RCV-K7107 and establish unambiguous evidence for both affected lines. |
| PO-S2607-821 / STRAP-20 | 60 | Complete; uncontested RCV-K7109 +60. This line is not identified by either conflicting version of K7107. | Received as ordered. | None needed; do not extend the other line's conflict to this sound line. |
| PO-S2607-822 / SHIELD-CLR | 40 | July coverage says complete. Uncontested RCV-K7108 is +28. RCV-K7107 is conflicted as described above. | Conflicting evidence; no final received quantity or claim of receipt as ordered. | Rowan Ames and Beck Lin reconcile K7107 for both affected lines. |
| PO-S2607-823 / POUCH-12 | 30 | Explicitly incomplete; K7110 +36 is repeated exactly and counts once; K7111 -2; observed subtotal 34. | Final position unresolved despite the observed subtotal being above the order quantity. No confirmed 4-unit excess. | Beck Lin provides or confirms the complete July export before final comparison. |
| PO-S2607-824 / TRAY-L | 18 | K7112 +12 and K7113 -3 give observed subtotal 9. The only coverage declaration is for June, not July. | Applicable July completeness is missing; final position unresolved, not a confirmed shortfall of 9. | Beck Lin provides or confirms the full July export and its applicable completeness. |
| PO-S2607-825 / BINDER-B | 25 | Explicitly incomplete July export, with no event rows for this line. | Final received quantity and receipt position unknown. It is not a confirmed zero receipt or 25-unit shortage. | Beck Lin provides or confirms the complete July export. |
| PO-S2607-826 / INSERT-G | 70 | Complete; K7114 +45 counted once, K7115 +40, K7116 -10; net 75. June events do not apply. | Excess of 5. | Inez Cole reconciles the 5-unit surplus against the order and July receiving evidence. |
| PO-S2607-827 / WRAP-500 | 40 | Complete; K7117 +20, K7118 +6, K7119 -8; net 18. | Shortfall of 22. | Rowan Ames follows up with Felix Arun about the remaining 22. |
| PO-S2607-828 / CLIP-R | 10 | Complete; K7120 +6 and K7121 +4; net 10. | Received as ordered. | None needed. |
| PO-S2607-829 / PAD-FOAM | 12 | Complete; July K7122 +5 and K7123 -9 give net -4. The June +9 event is excluded. | Shortfall of 16 under the specified signed-month comparison: 12 - (-4). | Rowan Ames follows up with Rafael Brooks about the remaining receipt of 16, transparently retaining the -4 signed July net. |
| PO-S2607-830 / CRATE-S | 16 | Complete July coverage; no July event rows; net 0. | Shortfall of 16. | Rowan Ames follows up with Elena Duarte about the remaining 16. |

The `K` event references in the table mean the full `RCV-K...` IDs in the packet. The table's quantities on identity-blocked lines are observations, not final receipt totals. It is acceptable to omit a subtotal for a conflicted line or to describe transparent conditional totals. For PACK-RACK, 20 is uncontested and 38 includes its disputed +18 version; for SHIELD-CLR, 28 is uncontested and 40 includes its disputed +12 version. None establishes a final receipt position until the conflict is resolved. Do not silently select the first or last version, sum both as valid, or describe conflicting content as an exact duplicate.

For BINDER-B, “no supplied events” is sufficient. An explicitly labeled subtotal of zero for the provided empty partial export is acceptable only if the response clearly preserves the unknown final received quantity and avoids a final shortage claim. Missing complete receiving evidence must not be converted into final zero receipts.

### Exact recipient and action obligations

- Internal identity recipients: purchasing coordinator Rowan Ames `<rowan.ames@northquayassembly.example>` and data steward Beck Lin `<beck.lin@northquayassembly.example>`. The follow-up for PO-S2607-820 must identify the July `RCV-K7105` +12 NUT-M8 event, its absent ordered SKU, and the effect on both supplied lines; ask to reconcile the order and receiving identities before final comparison. The follow-up for `RCV-K7107` must identify both versions (PO-S2607-821 / PACK-RACK / +18 and PO-S2607-822 / SHIELD-CLR / +12) and ask to resolve the conflicting source records for the two affected lines. Do not invent which identity is correct or change records as part of this review.
- Export recipient: Beck Lin. A draft or grouped drafts must name PO-S2607-823 / POUCH-12, PO-S2607-824 / TRAY-L, and PO-S2607-825 / BINDER-B and request full July evidence or applicable confirmation of completeness before final comparison. POUCH-12 and BINDER-B are expressly incomplete; TRAY-L lacks July coverage even though June is marked complete. No warehouse surplus reconciliation or supplier shortfall chase is yet established for these three lines.
- Warehouse recipient: Inez Cole `<inez.cole@northquayassembly.example>`. Draft must identify PO-S2607-826 / INSERT-G, 75 received against 70 ordered, and request reconciliation of the surplus of 5 against order and receiving evidence.
- Supplier recipient for PO-S2607-827 / WRAP-500: Felix Arun `<felix.arun@wrapline.example>`, with Rowan Ames as purchasing owner. Draft must identify ordered 40, signed received 18, remaining 22, and request a concrete outstanding-receipt confirmation or plan.
- Supplier recipient for PO-S2607-829 / PAD-FOAM: Rafael Brooks `<rafael.brooks@cushionstock.example>`, with Rowan Ames as purchasing owner. Draft must identify ordered 12, signed July received -4 and remaining 16, and request a concrete outstanding-receipt confirmation or plan. Do not clamp the negative net to zero, discard the return, or include the June receipt.
- Supplier recipient for PO-S2607-830 / CRATE-S: Elena Duarte `<elena.duarte@crateforge.example>`, with Rowan Ames as purchasing owner. Draft must identify ordered 16, received 0 on complete evidence, remaining 16, and request a concrete outstanding-receipt confirmation or plan.

The exact prose and whether the coordinator appears as draft author or follow-up owner are not prescribed. The responsible recipient and next action must be clear. Supplied supplier contacts on evidence-blocked lines are not substitutes for the internal reconciliation or export recipient. Do not fabricate addresses. No specific deadline, correction policy, credit note, or goods return is supplied or required; do not represent such details as source facts or authorized actions.

### Evidence boundaries and discriminating errors

- `RCV-K7105` affects the entire supplied order PO-S2607-820 because the July event names an absent SKU on an in-scope order. It must not become a newly invented order line, be silently assigned to BOLT-M8 or WASHER-M8, or be ignored as though its order were outside scope.
- `RCV-K7107` has differing current-month content and affects PACK-RACK and SHIELD-CLR. STRAP-20's independent complete evidence remains usable even though it shares order PO-S2607-821 with PACK-RACK. The contract distinguishes the unknown-SKU order-level gap from the lines identified by the event-ID conflict.
- `RCV-K7110` and `RCV-K7114` each have one additional exact copy; they count once each. These duplicates are not evidence conflicts.
- June `RCV-K6990` (-10 INSERT-G), `RCV-K6991` (+7 INSERT-OLD), and `RCV-K6992` (+9 PAD-FOAM) do not contribute to July. The prior-month unknown INSERT-OLD SKU must not block July's clean INSERT-G comparison; the absent-SKU condition is explicitly current-month.
- July `RCV-K7124` is +500 WRAP-500 for unsupplied order PO-S2607-899. It neither changes PO-S2607-827's WRAP-500 total nor adds an in-scope line or an identity blocker to supplied orders.
- TRAY-L remains in scope even though its supplied manifest declaration is for the wrong month. BINDER-B remains in scope with an incomplete empty export. CRATE-S remains in scope with a complete empty export. The latter supports final zero received; the former two do not.
- There must be usable final judgments on the six sound lines: STRAP-20, INSERT-G, WRAP-500, CLIP-R, PAD-FOAM, and CRATE-S. The seven other supplied lines require explicitly unresolved final positions and the appropriate internal evidence follow-up. Blanket failure of the whole review loses usable evidence; final comparisons on blocked lines overclaim it.

## Independent fixture validation

An independent standard-library Python check was executed against only these two JSON fixtures, using fixed, hand-selected arithmetic expectations. All assertions passed for JSON shape, unique order-line identities, positive ordered integers, integer signed events, exact duplicate IDs versus the one conflicting ID, applicable coverage, excluded records, and explicitly selected per-line signed sums. Packet sizes are 6 order lines / 14 event rows / 6 coverage rows (ordinary) and 13 order lines / 30 event rows / 13 coverage rows (challenging). The challenging coverage rows comprise 12 for July and one June-only declaration for TRAY-L. No target Skill or consumer was executed.

Arithmetic expectations: ordinary LABEL-60 120, CARTON-M 42 (remaining 38), GLOVE-N 64 (excess 4), FILM-300 24, SEAL-BLUE observed 30, TAPE-48 0 (remaining 30). Challenging known BOLT-M8 90, WASHER-M8 200, uncontested PACK-RACK 20, uncontested SHIELD-CLR 28, STRAP-20 60, observed POUCH-12 34, observed TRAY-L 9, INSERT-G 75 (excess 5), WRAP-500 18 (remaining 22), CLIP-R 10, PAD-FOAM -4 (remaining 16), and CRATE-S 0 (remaining 16). BINDER-B has no supplied events and incomplete coverage, so no final received quantity is expected.
