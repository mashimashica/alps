# July 2026 receiving review

Rowan has 13 supplied lines to coordinate: 3 are received as ordered, 4 have confirmed shortfalls, 1 has a confirmed excess, and 5 remain unresolved because of conflicting, incomplete, or missing evidence. Quantities below use July events only, treat returns and reversals as signed quantities, and count exact duplicate event records once.

| Purchase order | SKU | Ordered | July evidence | Judgment | Required direction |
|---|---|---:|---:|---|---|
| PO-S2607-820 | BOLT-M8 | 100 | Net 90 (70 + 30 - 10) | **Complete shortfall: 10** | Supplier follow-up |
| PO-S2607-820 | WASHER-M8 | 200 | Net 200 | **Received as ordered** | None for this line |
| PO-S2607-821 | PACK-RACK | 48 | 20 from non-conflicting evidence; 38 if the disputed 18-unit `RCV-K7107` record belongs here | **Unresolved: conflicting event identity** | Rowan and Beck must reconcile `RCV-K7107`; no supplier shortage claim yet |
| PO-S2607-821 | STRAP-20 | 60 | Net 60 | **Received as ordered** | None |
| PO-S2607-822 | SHIELD-CLR | 40 | 28 from non-conflicting evidence; 40 if the disputed 12-unit `RCV-K7107` record belongs here | **Unresolved: conflicting event identity** | Rowan and Beck must reconcile `RCV-K7107`; no supplier shortage claim yet |
| PO-S2607-823 | POUCH-12 | 30 | Observed subtotal 34 (36 - 2); exact repeat of `RCV-K7110` counted once | **Unresolved: July export marked incomplete** | Beck to supply or confirm the full export before deciding whether there is an excess |
| PO-S2607-824 | TRAY-L | 18 | Observed subtotal 9 (12 - 3) | **Unresolved: July coverage missing** | Beck to provide July coverage/full export; the supplied coverage is for June |
| PO-S2607-825 | BINDER-B | 25 | Observed subtotal 0 | **Unresolved: July export marked incomplete** | Beck to supply or confirm the full export; zero is only an observed subtotal |
| PO-S2607-826 | INSERT-G | 70 | Net 75 (45 + 40 - 10); exact repeat of `RCV-K7114` counted once | **Complete excess: 5** | Warehouse reconciliation |
| PO-S2607-827 | WRAP-500 | 40 | Net 18 (20 + 6 - 8) | **Complete shortfall: 22** | Supplier follow-up |
| PO-S2607-828 | CLIP-R | 10 | Net 10 (6 + 4) | **Received as ordered** | None |
| PO-S2607-829 | PAD-FOAM | 12 | Net -4 (5 - 9) | **Complete shortfall: 16** | Supplier follow-up; call out the negative July net |
| PO-S2607-830 | CRATE-S | 16 | Net 0; no July events in a complete export | **Complete shortfall: 16** | Supplier follow-up |

## Evidence issues

- `RCV-K7107` is reused with different content: 18 units for `PO-S2607-821` / `PACK-RACK` and 12 units for `PO-S2607-822` / `SHIELD-CLR`. Both supplied lines remain unresolved until the source identity is reconciled.
- `RCV-K7105` names in-scope order `PO-S2607-820` but SKU `NUT-M8`, which is absent from that order's supplied lines. It contributes to neither `BOLT-M8` nor `WASHER-M8`; Rowan and Beck should reconcile it separately.
- Exact repeats of `RCV-K7110` and `RCV-K7114` were deduplicated.
- June events `RCV-K6990`, `RCV-K6991`, and `RCV-K6992` were excluded from July totals. The 500-unit July event for outside order `PO-S2607-899` was also excluded.

## Draft follow-ups

**To Tessa Holt <tessa.holt@ridgefast.example> — PO-S2607-820 / BOLT-M8**  
Subject: July receipt shortfall — PO-S2607-820 / BOLT-M8  
Our complete July receipt evidence nets to 90 units against 100 ordered, including a 10-unit return/reversal. Please confirm the status and expected delivery or resolution for the remaining 10 units.

**To Rowan Ames <rowan.ames@northquayassembly.example> and Beck Lin <beck.lin@northquayassembly.example> — conflicting `RCV-K7107`**  
Subject: Reconcile reused receipt ID RCV-K7107  
`RCV-K7107` appears with different order, SKU, and quantity content: 18 units for PO-S2607-821 / PACK-RACK and 12 units for PO-S2607-822 / SHIELD-CLR. Please determine the authoritative source record and correct identity before either line receives a final judgment. Non-conflicting July subtotals are 20 for PACK-RACK and 28 for SHIELD-CLR.

**To Rowan Ames <rowan.ames@northquayassembly.example> and Beck Lin <beck.lin@northquayassembly.example> — PO-S2607-820 / `NUT-M8` anomaly**  
Subject: Reconcile unmatched SKU on RCV-K7105  
July event `RCV-K7105` records 12 units against PO-S2607-820 under SKU `NUT-M8`, but that SKU is absent from the supplied order lines. Please identify the intended order line or correct the source record. The event was excluded from the BOLT-M8 and WASHER-M8 totals.

**To Beck Lin <beck.lin@northquayassembly.example> — incomplete or missing evidence**  
Subject: Complete July receipt evidence for three lines  
Please provide or confirm the full July export for PO-S2607-823 / POUCH-12 (observed subtotal 34; coverage marked incomplete), PO-S2607-824 / TRAY-L (observed subtotal 9; July coverage missing), and PO-S2607-825 / BINDER-B (observed subtotal 0; coverage marked incomplete). Final receipt positions should wait for that evidence.

**To Inez Cole <inez.cole@northquayassembly.example> — PO-S2607-826 / INSERT-G**  
Subject: Reconcile July receipt excess — PO-S2607-826 / INSERT-G  
The complete July evidence nets to 75 units against 70 ordered after deduplicating `RCV-K7114` and applying the 10-unit July reversal. Please reconcile the 5-unit excess against the order and receiving records.

**To Felix Arun <felix.arun@wrapline.example> — PO-S2607-827 / WRAP-500**  
Subject: July receipt shortfall — PO-S2607-827 / WRAP-500  
Our complete July evidence nets to 18 units against 40 ordered after the 8-unit return/reversal. Please confirm the status and expected delivery or resolution for the remaining 22 units.

**To Rafael Brooks <rafael.brooks@cushionstock.example> — PO-S2607-829 / PAD-FOAM**  
Subject: July receipt shortfall — PO-S2607-829 / PAD-FOAM  
Our complete July evidence nets to -4 units against 12 ordered: 5 received and 9 reversed in July. The June receipt was excluded from the requested month. Please confirm the status and expected delivery or resolution for the resulting 16-unit July shortfall.

**To Elena Duarte <elena.duarte@crateforge.example> — PO-S2607-830 / CRATE-S**  
Subject: No July receipt recorded — PO-S2607-830 / CRATE-S  
The complete July export contains no receipt events for the 16 units ordered. Please confirm the shipment status and expected delivery or resolution for all 16 units.

These are drafts only; no messages were sent and no receiving records were changed.
