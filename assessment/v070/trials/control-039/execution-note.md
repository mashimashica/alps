# Execution note

## Outputs

- Skill: `deliverables/skills/reimbursement-ledger-rollup/`
- Instructions: `deliverables/skills/reimbursement-ledger-rollup/SKILL.md`
- Runner: `deliverables/skills/reimbursement-ledger-rollup/scripts/rollup.py`

The runner uses the supplied `ledger_api.py` only through its `describe` and
`page` commands. It stores an atomic JSON checkpoint after each successful
page, keeps all amounts as integer cents, deduplicates already incorporated
`entry_id` values on a repeated page, and leaves tranche grants to the
operator. Its output distinguishes `complete`, `incomplete`, and
`recovery_required`; partial rows are never labeled final.

## Supplied material used

I read `input/brief.md`, `input/ledger_api.py`, `input/fixture.json`, and
`/workspace/scratch/a75c3a6d9076/alps-v070-assessment/common/agent-skills-format.md`.
The frozen skill-creator copy was not needed.

## Checks performed

All commands below were run from the trial directory. The source states and
checkpoints were disposable files under `verification/`.

1. `python3.12 -m py_compile deliverables/skills/reimbursement-ledger-rollup/scripts/rollup.py`
   exited `0`.
2. `python3.12 deliverables/skills/reimbursement-ledger-rollup/scripts/rollup.py --help`
   exited `0` and displayed the five required options (`--state`, `--api`,
   `--from`, `--to`, and `--checkpoint`).
3. The supplied fixture was initialized into `verification/source.sqlite`.
   `ledger_api.py init` exited `0`, reporting snapshot
   `snap_a85a9511a684a5bb7e464198` and 17 records. `describe` exited `0` and
   reported page size 3 and two calls per tranche.
4. The demonstration interval `2026-02-01` through `2026-02-15` was run with
   `verification/rollup.json`. The first invocation exited `75` after two
   pages with `status: incomplete` and `final: false`. It retained a cursor
   and provisional rows for alder and birch. After an operator `grant-tranche`
   (exit `0`), the continuation again exited `75` after two pages. After a
   second grant (exit `0`), the continuation exited `0` with `status: complete`,
   six pages observed, and these rows (cents): alder `14000/1500/12500` (4),
   birch `7000/200/6800` (2), cedar `3250/3250/0` (2), dune `400/1200/-800`
   (2), and elm `2345/0/2345` (1), where each tuple is charge/credit/net and
   the parenthesized value is the qualifying count.
5. Re-running the completed checkpoint exited `0` and returned the same final
   result without fetching another page.
6. An invalid interval (`2026-02-16` through `2026-02-01`) exited `2` with
   `--from must be on or before --to`.
7. A second initialized source was run for a valid interval with no qualifying
   entries (`2025-01-01` through `2025-01-02`). Its first two invocations
   exited `75` at tranche boundaries; after the second operator grant, the
   final invocation exited `0` with `status: complete` and `result.rows: []`.
8. A structural check confirmed the required skill frontmatter, matching skill
   directory name, and runner file; it exited `0`.

## Limits of verification

The supplied simulator's normal budget exhaustion, multi-tranche continuation,
exact-cent aggregation, negative and zero net values, empty qualifying output,
invalid interval handling, and completed-checkpoint idempotence were exercised.
I did not inject a deliberately lost or malformed page response, corrupt a
checkpoint, or construct an empty source state; those paths are implemented but
remain unexercised here. The runner cannot determine whether a response was
lost after the API counted its call, so it reports `recovery_required` and
requires operator-directed continuation rather than claiming completion.
