---
name: recoverable-local-workshop-bookings
description: Reserve places in a supplied local workshop session with durable request-key recovery, idempotent retries, and truthful confirmed, rejected, or unresolved outcomes. Use for the local booking simulator only; never substitute sessions or perform cancellation, payment, notification, or external booking.
---

# Recoverable local workshop bookings

Use `scripts/book.py` as the coordinator. It records the request payload durably before any state-changing attempt, then delegates the atomic decision to the bundled simulator. Always provide an explicit state database and ledger path; separate scenarios need separate paths.

## Operations

Initialize once:

```sh
python3 scripts/book.py --state /absolute/state.sqlite --ledger /absolute/ledger.json init
```

Reserve the requested positive integer number of places:

```sh
python3 scripts/book.py --state /absolute/state.sqlite --ledger /absolute/ledger.json reserve --request-key demo-cedar-01 --party-id crew-cedar --slot-id paper-lab-am --seats 2
```

If no key is supplied, the coordinator creates one and persists it before attempting. A continuation or retry must reuse the same key, party, session, and count. A key conflict is surfaced; never overwrite it or create a fresh key to evade it.

Reconcile any nonzero, timeout, interrupted, empty, or otherwise untrusted attempt:

```sh
python3 scripts/book.py --state /absolute/state.sqlite --ledger /absolute/ledger.json reconcile --request-key demo-cedar-01
```

`confirmed` is valid only with the receipt's booking identifier and matching request details. `rejected` is definitive only when the simulator returns its persisted reason. `unresolved` means the outcome still needs reconciliation; do not claim that no booking occurred and do not retry under another key. Availability is advisory only and never a booking confirmation.

The wrapper's ledger is local recovery information, not booking truth; the simulator's committed receipt is authoritative. No operation changes any state except the explicitly named local SQLite database and ledger file. The bundled `booking.py` is the supplied simulator and must not be modified.
