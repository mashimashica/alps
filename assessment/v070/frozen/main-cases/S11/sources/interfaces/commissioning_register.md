# MFI-COMM signed commissioning register — interface version 2

The register is a read-only, owner-authorized CSV export provided with a future case packet. No live register connection or row-level case decision is needed to revise the work descriptions here. A valid export carries the register identifier, interface version, and export timestamp in its accompanying provenance note.

Fields:

| Field | Meaning |
| --- | --- |
| `record_id` | Stable identifier of one commissioning record. |
| `asset_serial` | Exact manufacturer serial number; leading zeros are significant. |
| `revision` | Positive integer revision number for that asset's commissioning record history. |
| `status` | `accepted`, `pending`, or `void`. Only `accepted` records establish an accepted commissioning date. |
| `accepted_on` | Installation-site local calendar date, `YYYY-MM-DD`; required for an accepted record. |
| `site_time_zone` | Named time zone used for the site date and the first-reported date. |
| `authorized_by` | Identity of the authorized commissioning approver; required for an accepted record. |
| `signed_record_ref` | Stable reference to the signed evidence; required for an accepted record. |
| `voids_record_id` | For a `void` record, the accepted record it explicitly voids; otherwise empty. |

Within one asset's record history, use the accepted record with the greatest revision number. A higher pending record does not itself supersede an accepted one. A void record is not evidence of acceptance. If a void record's `voids_record_id` names the selected acceptance, the care operations lead must resolve the asset's valid status before a date is used; do not fall back to an older acceptance on your own. A void record with a missing or unknown target also needs that lead's resolution. Conflicting records at the same highest accepted revision, a disputed signed record, invalid date or missing required accepted-record evidence must not be silently resolved by file order.

The first-reported date is the date of the earliest qualifying symptom report in the same site time zone. Day 0 is the accepted commissioning date; the elapsed calendar-day difference, not elapsed 24-hour periods, determines the window. A report before accepted commissioning does not qualify under this criterion. Retain the selected `record_id`, revision, date, site time zone, and signed evidence reference with the routing basis so another worker can inspect it without a new interpretation of the register.

The commissioning date is not an alternative start date for warranty, rental-charge relief, or the fixed historical quality cohort. Their source requirements remain in MFI-CARE-07.
