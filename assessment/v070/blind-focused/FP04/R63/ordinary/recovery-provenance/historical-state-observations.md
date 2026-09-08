# Historical state observations

Exact selected paragraphs from RECOVERY-ENVIRONMENT-OFFLINE.md at `75c0ea9bddf379c5e1803e4c0114ba5b47c871d8`. The original document's surrounding grades, configuration and progress material is not included. These outage-time observations are followed by the current availability limits in evidence-availability.md.

Actual final native API SQL was captured locally for C-U084–091 and C-U093. Captured ordinary SQL hashes match 0c59cdc1f01c69cb8dc8899d6565287e22fc0469988613be1a04c379594ca580; challenging hashes match 071ead7c2855dc57b35546ff0515c79039899eae12b921f60584232f858cb496. These observations do not substitute for original per-trial metadata, binary identity or call histories. C-U092 final API state was not captured; do not infer its hash.

A separate consumer-produced workflow checkpoint exists at consumers/C-U093/work/reimbursement-rollup-2026-04-03_2026-04-09.sqlite. It is not the API source database. The parent explicitly preserved it with observation label consumer-complete:

- Original SQLite SHA-256: 2b35f698076080a15b9df2148535a2955608c6f125c3a5c00504e4050e950359.
- Native SQL: sqlite-evidence/consumer-complete/consumers/C-U093/work/reimbursement-rollup-2026-04-03_2026-04-09.sqlite.sql.
- Native SQL SHA-256: 2f30def62fff9a87c9ebfa3d82235d7c627cb6df9d489a376f35396f4538c87c.
- The preservation completed locally; no subsequent full remote checkpoint succeeded.
