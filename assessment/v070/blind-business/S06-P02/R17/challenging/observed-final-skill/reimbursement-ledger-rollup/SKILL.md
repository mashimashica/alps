---
name: reimbursement-ledger-rollup
description: Complete vendor reimbursement rollups from a paginated immutable ledger API, traversing every page across operator granted tranches and persisting safe continuation state.
---

# Reimbursement ledger rollup

Run `scripts/rollup.py --api API --source-state STATE --from YYYY-MM-DD --to YYYY-MM-DD --checkpoint CHECKPOINT`. It makes at most two page calls per invocation, emits JSON with `complete`, `paused`, or `invalid` status, and sorts completed rows by `vendor_id`. Reuse the checkpoint and arguments after the operator runs `grant-tranche`; this skill never grants a tranche. Only settled entries in the inclusive interval count. Amounts remain integer cents; zero and negative nets are retained. Invalid intervals stop before traversal.
