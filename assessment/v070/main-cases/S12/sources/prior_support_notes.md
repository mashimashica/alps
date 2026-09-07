# Previous receiving-review support arrangement

Written when the only tool was the version 1 row viewer. These notes are raw operating history, not an Agent Skill and not a policy change authorization.

The old viewer displayed one count event at a time. It could not normalize identities, match manifest rows to count events, combine repeated manifest lines, total signed corrections, report unmatched identities, or export stable row references. Staff therefore used the following working arrangement:

1. Ask the operator to copy both files into a temporary grid, preserve leading zeros as text, and manually make a site/shipment/SKU/lot key. Trim whitespace and compare those four IDs without case distinctions. Never match just on SKU.
2. Sort both sides by the key, manually combine repeated manifest lines, and add signed posted good and damaged count changes separately. Mark pending events without including them in posted totals. Treat an absent side as missing evidence rather than a zero quantity.
3. Have a second pass re-key every quantity and recalculate every group. This blanket duplicate calculation compensated for the copy-and-sum workflow, not a policy requirement for two people to approve a lot. Hand-copy all manifest-line and count-event IDs into the review so the totals can be traced.
4. If the packet is too large for that grid, ask for a custom joining-and-summing script to be written and checked for this engagement. The old viewer was not considered a usable numeric source for the review. The local support configuration therefore described arithmetic as a user-performed prerequisite and omitted the viewer from the Skill's intended tools.
5. Check the quality-context record separately, including its review date, restricted-part approval, and all SW-RCV-04 release conditions. Do not release a lot because its numbers match, and do not use a spreadsheet flag as a quality-owner approval.

The restrictions on tool use above were compensations for version 1's missing capabilities, not security prohibitions on local commands. The receiving owner has authorized reassessing them for version 2. That permission does not change SW-RCV-04, authorize an inventory write, or mean all manual source checks are obsolete. There is no requirement to retain a hand-built grid, duplicate arithmetic on every valid run, or a newly authored matching script when the available capability makes them unnecessary.

Past pain points included accidentally discarding leading zeros, summing a pending correction as though it were posted, overlooking a manifest-only group, and losing the record IDs behind a total. The revised setup should make its treatment of those issues usable by a future operator, without relying on this particular demonstration's outcome.
