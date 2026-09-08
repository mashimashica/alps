# Verification scope

Local verification used Python 3.12.13 and the supplied synthetic `ledger_api.py` CLI. Ten component/integration tests passed. The integration tests exercised the bundled runner as a subprocess and used separate disposable SQLite source states; only the test harness acted as operator to grant additional tranches.

| Condition examined | Observed result |
| --- | --- |
| Supplied 17-entry snapshot, 2026-02-01 through 2026-02-15 | Incomplete after 6 and 12 examined entries; complete after 17 entries across three tranches and six committed pages |
| Re-run without further approval | Remained incomplete; checkpoint unchanged; no extra successful calls |
| Completed-command replay | Same result; no extra page calls |
| Qualification, both interval boundaries, pending/void exclusion, nonchronological entries | Expected vendor cents and counts matched; late-page qualifying entries included |
| Zero and negative vendor nets | Cedar retained at 0 cents; dune retained at -800 cents |
| Invalid/reversed/noncanonical dates | Rejected before traversal or checkpoint creation; source allowance unchanged |
| Empty ledger | Complete empty result after one page call |
| No qualifying entries | Empty result only after all 17 records examined |
| Alternate snapshot, one-day leap-date interval, zero amount, large integer amounts | Three qualifying entries counted; exact arithmetic above 64-bit range |
| Lost successful page response | Quota decreased without checkpoint advancement; replay counted entries once and needed an additional tranche |
| Injected failure after page call, before checkpoint commit | Same cursor resumed; final coverage 17 entries, six committed pages |
| Output failure after checkpoint commit | Status regenerated complete output without additional source calls |
| Changed interval or replacement snapshot | Rejected without new page calls or checkpoint changes |
| Invalid cursor, snapshot mismatch, exhausted allowance | Source CLI returned 2, 4, and 75 as specified |
| Duplicate page response | Incorporation rejected duplicate/loop without altering committed records |

The frozen author's format validator passed after runtime requirements were placed in the body. This is a frontmatter/scaffold check, not proof of business correctness. Packaged Markdown links were also checked for local target existence.

Limits: these are deterministic local component and integration checks, not an independent agent's application or a live service evaluation. The test operator supplied grants; the runner cannot ensure that real approval ever arrives. Fault checks inject loss/failure at identified boundaries; they do not physically crash the OS or prove behavior under storage corruption, power failure, distributed filesystems, concurrent operators, or adversarial edits. Large-volume performance, Windows portability, live-service integration, and automatic Skill discovery were not tested. Test fixtures and the source simulator are not operational dependencies bundled into this Skill; future applications must supply the documented trusted CLI and state.
