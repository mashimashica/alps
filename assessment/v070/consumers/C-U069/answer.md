# June 2026 receiving review

The supplied scope contains **6 purchase-order lines**. Four lines have complete evidence and a final comparison; one complete line has a justified zero receipt position; and one line remains provisional because its June export coverage is partial. There are no invalid order rows, identity conflicts, or missing recipients.

| Purchase order | SKU | Ordered | Accepted June evidence | Observed net | Coverage | Supported position | Final remaining / excess |
| --- | --- | ---: | --- | ---: | --- | --- | --- |
| PO-R2606-410 | LABEL-60 | 120 | RCV-H1801 +75; RCV-H1802 +50; RCV-H1803 -5 | 120 | Complete | Received as ordered | — |
| PO-R2606-410 | CARTON-M | 80 | RCV-H1804 +50; RCV-H1805 -8 | 42 | Complete | Shortfall | **38 remaining** |
| PO-R2606-411 | GLOVE-N | 60 | RCV-H1806 +66; RCV-H1807 -2 | 64 | Complete | Excess | **4 excess** |
| PO-R2606-412 | FILM-300 | 24 | RCV-H1808 +24 | 24 | Complete | Received as ordered | — |
| PO-R2606-413 | SEAL-BLUE | 40 | RCV-H1809 +35; RCV-H1810 -5 | 30 subtotal | Partial | Not final | Not supported yet |
| PO-R2606-414 | TAPE-48 | 30 | No accepted June events | 0 | Complete | Shortfall | **30 remaining** |

## Evidence limits and exclusions

- **PO-R2606-413 / SEAL-BLUE cannot receive a final comparison.** Its accepted-event subtotal is 30, but coverage is explicitly partial. A full June event export and complete coverage declaration are required. The apparent difference from 40 ordered must not be treated as a final 10-unit shortfall.
- The repeated copy of event **RCV-H1801** at event record index 3 was identical and counted once.
- Event **RCV-H1720** for CARTON-M was excluded because it belongs to May 2026. Event **RCV-H1901** for FILM-300 was excluded because it belongs to July 2026.
- Event **RCV-H1811** was excluded because PO-R2606-499 is outside the supplied order scope.
- Complete coverage with no accepted June events supports the zero net for **PO-R2606-414 / TAPE-48**.

## Follow-up drafts

All four drafts have supplied recipients and are ready for Dana to address. These are drafts only; no messages have been sent.

### 1. CARTON-M supplier shortfall

**Owner:** Dana Ivers <dana.ivers@juniperworks.example>  
**Recipient:** Mara Quinn <mara.quinn@harborpack.example>  
**Next action:** Ask the supplier to confirm the status, expected receipt date, and next receiving action for the final 38-unit shortfall.

**To:** Mara Quinn <mara.quinn@harborpack.example>  
**Subject:** Receiving review 2026-06 — PO-R2606-410 CARTON-M

For June 2026, complete receiving evidence for PO-R2606-410, SKU CARTON-M, shows 42 net units received against 80 ordered, leaving 38 units outstanding. Please confirm the status and expected receipt date of the remaining 38 units and the next receiving action.

### 2. GLOVE-N warehouse excess

**Owner and recipient:** Noel Price <noel.price@juniperworks.example>  
**Next action:** Reconcile the 4-unit surplus and report its cause and proposed correction or disposition.

**To:** Noel Price <noel.price@juniperworks.example>  
**Subject:** Receiving review 2026-06 — PO-R2606-411 GLOVE-N

For June 2026, complete receiving evidence for PO-R2606-411, SKU GLOVE-N, shows 64 net units received against 60 ordered. Please reconcile the 4-unit surplus against the order and receiving evidence, then report the cause and proposed correction or disposition.

### 3. SEAL-BLUE incomplete export

**Owner and recipient:** Simone Bell <simone.bell@juniperworks.example>  
**Next action:** Provide or confirm the full June export and an explicit complete coverage declaration before any final comparison.

**To:** Simone Bell <simone.bell@juniperworks.example>  
**Subject:** Receiving review 2026-06 — PO-R2606-413 SEAL-BLUE

Please provide or confirm the full June 2026 receiving-event export and an explicit complete coverage declaration for PO-R2606-413, SKU SEAL-BLUE. Current coverage is partial, so the accepted-event net of 30 is only an observed subtotal and does not support a final comparison with the 40 units ordered.

### 4. TAPE-48 supplier shortfall

**Owner:** Dana Ivers <dana.ivers@juniperworks.example>  
**Recipient:** Owen Malik <owen.malik@bindwell.example>  
**Next action:** Ask the supplier to confirm the status, expected receipt date, and next receiving action for all 30 outstanding units.

**To:** Owen Malik <owen.malik@bindwell.example>  
**Subject:** Receiving review 2026-06 — PO-R2606-414 TAPE-48

For June 2026, complete receiving evidence for PO-R2606-414, SKU TAPE-48, shows 0 net units received against 30 ordered, leaving all 30 units outstanding. Please confirm the status and expected receipt date of the 30 units and the next receiving action.
