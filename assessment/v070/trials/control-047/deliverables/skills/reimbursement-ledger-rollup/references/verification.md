# Local verification

Verified using Python 3.12 against the supplied local ledger API and original 17-entry synthetic fixture. Ten standard-library unittest checks passed. No external services or business actions were used. Operator grants occurred only in the verification harness; the runtime has no grant operation.

The normal request for 2026-02-01 through 2026-02-15 paused after 6 and 12 examined entries, then completed with 17 examined entries and 6 committed pages across three tranches. The expected final amounts, in integer cents, were:

| Vendor | Settled charges | Settled credits | Net | Qualifying count |
| --- | ---: | ---: | ---: | ---: |
| alder | 14000 | 1500 | 12500 | 4 |
| birch | 7000 | 200 | 6800 | 2 |
| cedar | 3250 | 3250 | 0 | 2 |
| dune | 400 | 1200 | -800 | 2 |
| elm | 2345 | 0 | 2345 | 1 |

Checks also covered repeated paused/final invocations, invalid and reversed intervals without quota consumption, an empty ledger, a fully traversed interval with no matches, a single-day interval, amounts of 10^30 cents, mismatched interval binding, snapshot mismatch, a counted but lost page response, a failure after page writes but before commit, duplicated page IDs, and a quota error that remains incomplete. Recovery tests finished the same request without double counting. The fixture's out-of-range entry before later qualifying entries verifies that traversal does not stop based on dates.

Failure injection was at the Python function boundary. Actual power loss, OS kill timing, disk failure, timeout expiry, corrupted checkpoints, concurrent invocation/grant races and production-scale performance were not tested. SQLite supplies transaction rollback/durability; safe persistence still depends on the filesystem. Tests do not establish guarantees for an API that violates its immutable snapshot and quota contract. This Skill requires the caller's compatible source interface; it does not bundle or initialize a source database.
