---
name: recoverable-local-workshop-bookings
description: Reserve places in the supplied local workshop simulator with durable request-key journaling, idempotent retries, and explicit reconciliation for uncertain outcomes. Use only for authorized local simulator bookings; never substitute sessions, create fresh keys for retries, or infer a result from availability.
---

# Recoverable local workshop bookings

## Purpose

Establish one truthful terminal result for an authorized booking request in the supplied local simulator: confirmed, definitively rejected, or unresolved and ready for reconciliation. The scope is only the specified party, session, positive place count, and stable request key.

## Outcomes

- A confirmed request has a persisted receipt containing booking identifier, request key, party, session, and place count.
- A rejected request has a persisted rejection reason and is not retried as a new authorization.
- An uncertain request retains enough durable information to reconcile with the same key and exact payload after the caller exits.
- Concurrent requests cannot cause this Skill to oversell capacity or duplicate a successful logical request.

## Inputs

Use the local `booking.py` supplied in `scripts/`, an initialized SQLite state path, and an authorized request key, party ID, slot ID, and seat count. A retry or continuation must reuse the exact same four request fields. The caller supplies a journal path (default is adjacent to the state path).

## Activities & Tasks

### Prepare and submit

1. Validate that all four fields are present and within the simulator's documented syntax and seat limits. Refuse to invent a key or alter a payload.
2. Record the exact payload durably in the journal before the first state-changing attempt.
3. Invoke `scripts/reconcile_booking.py reserve` with the same key and payload. Interpret JSON `confirmed` or `rejected` as terminal receipts and persist them in the journal.
4. Treat timeout, exit 75, interruption, non-JSON output, or missing output as unresolved. Do not claim rejection and do not retry with a new key.

### Reconcile

1. Invoke `scripts/reconcile_booking.py recover` using the journal entry and the same state path. Recovery performs `lookup` first and, when still unseen, safely retries the exact original payload.
2. Continue recovery until a terminal receipt is returned or the invocation remains unresolved. A lookup result of `not_seen` is not proof that no booking exists.
3. Surface `idempotency_conflict` as an error requiring human resolution; never overwrite the earlier journal entry.

## Controls and constraints

- Availability is informational only; it never authorizes or confirms a booking.
- Only the supplied simulator may be called. No cancellation, payment, notification, substitution, partial booking, or external service is permitted.
- Journal writes use atomic replacement and are retained across process termination. Do not delete unresolved entries.
- Separate scenarios must use separate state files. The simulator's transaction is the concurrency boundary; the wrapper does not claim a hold.

## Interface

```text
python3 scripts/reconcile_booking.py reserve --state STATE --request-key KEY --party-id PARTY --slot-id SLOT --seats N [--journal JOURNAL]
python3 scripts/reconcile_booking.py recover --state STATE --request-key KEY [--journal JOURNAL]
```

The command emits one JSON object. Terminal results have `state` `confirmed` or `rejected`; uncertain results have `state` `unresolved`, `request`, and `reason`. Exit 0 means a terminal result, exit 75 means unresolved, and exit 2/3 indicates invalid input or an idempotency conflict. The journal path is durable state, not evidence that a booking succeeded.

## Verification limits

The bundled script was checked against the supplied simulator for normal confirmation, replay, rejection, and both pre-commit and post-commit fault recovery. These local trials do not establish behavior of any other service or real booking system.
