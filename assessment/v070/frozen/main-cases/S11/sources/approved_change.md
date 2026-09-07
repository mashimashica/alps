# Approved change CO-2026-17

Owner: Cora Elm, Meridian customer-care operations owner  
Approved: 2026-07-17  
Effective for open and newly received cases: 2026-07-20  
Document to amend: MFI-CARE-07, currently revision 6

Replace only the eligibility timing and date-source requirements in C1, Launch Assist:

- A qualifying symptom must first be reported from day 0 through day 21, inclusive, after the asset's accepted commissioning date.
- Use `accepted_on` from the latest authorized `accepted` record for the asset in the signed commissioning register MFI-COMM, interface version 2. This is a local calendar date at the installation site, not the export timestamp or carrier delivery date. The interface and ambiguity rules are supplied in `interfaces/commissioning_register.md`.
- A missing, disputed, or non-unique accepted commissioning date goes to the care operations lead to resolve the source evidence. Do not infer it from the delivery date, an installation appointment, a customer's recollection, or a pending commissioning record. Until resolved, retain the ordinary diagnostic booking path without claiming Launch Assist eligibility. The independent safety stop still takes priority.

All other C1 requirements and benefits remain unchanged. In particular, model and ownership exclusions remain; this is not a promise of replacement, a credit, or warranty coverage. Apply the new criterion when reviewing open cases from the effective date forward. Do not reopen closed cases or retroactively alter historical operational or quality results.

Update any related work description whose input, routing, or handoff is affected by that change. The intake-to-scheduling handoff must make the source basis of the routing decision available so scheduling can use the same decision rather than independently reconstructing a different date. Existing serial-number and delivery-date collection remains needed for other work.

No change is approved to C2 rental-charge relief, C3 warranty assessment, C4 safety escalation, or C5 the fixed early-failure quality series. The shared policy retains identifier MFI-CARE-07 and is to become revision 7 with this effective date. Keep it as the maintained source for the dependent descriptions; do not create competing eligibility policies.

The sales team's separately discussed suggestion to offer automatic replacement for Launch Assist cases was not approved and is outside this change.
