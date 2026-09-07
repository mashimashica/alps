# Execution note

Created `deliverables/skills/reimbursement-ledger-rollup/` with `SKILL.md` and executable `scripts/rollup.py`.

## Checks run

- Initialized a disposable `verify/source.sqlite` from the supplied fixture. The API reported 17 records.
- Ran the helper over three operator tranches. The first two runs returned `complete: false`; the third returned `complete: true` and two sorted vendor rows. This exercised checkpoint continuation across six pages and entry-ID deduplication state.
- Ran an invalid interval. It returned `invalid interval: start is after end`, exited 2, and did not traverse pages.
- Ran the supplied frozen validator: `Skill is valid!` (exit 0).

## Design and limits

The helper calls `describe` and then at most two page calls per invocation, atomically saving the cursor and entries after each successful page. It retains only qualifying settled records in the final vendor view, uses integer cents, and emits incomplete output until the cursor is null. A page command failure is reported as incomplete and the checkpoint is preserved; entry IDs make replayed pages idempotent. I did not simulate a process crash between a counted source call and response receipt, nor test malformed source records or an empty fixture. The supplied inputs were not modified.
