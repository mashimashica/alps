# Execution evidence

## Exact captured observations

### 1. Read-only lookup of the original request key

Command:

```sh
python3 /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U010/input/booking.py --state /workspace/scratch/a75c3a6d9076/D1-U010-booking-state-3zc_fceb/bookings.sqlite lookup --request-key orchid-linocut-20261122-01
```

Exit code: `0`

Stdout:

```json
{"request_key":"orchid-linocut-20261122-01","state":"not_seen"}
```

Stderr: empty.

### 2. Authorized unchanged retry through the durable coordinator

Command:

```sh
python3 /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U010/skill/recoverable-local-workshop-bookings/scripts/book.py --state /workspace/scratch/a75c3a6d9076/D1-U010-booking-state-3zc_fceb/bookings.sqlite --ledger /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U010/work/orchid-booking-ledger.json reserve --request-key orchid-linocut-20261122-01 --party-id crew-orchid --slot-id linocut-sun-am --seats 3
```

Exit code: `0`

Stdout:

```json
{"party_id": "crew-orchid", "reason": "insufficient_capacity", "replayed": false, "request_key": "orchid-linocut-20261122-01", "seats": 3, "slot_id": "linocut-sun-am", "state": "rejected"}
```

Stderr: empty.

### 3. Same-key reconciliation of the persisted receipt

Command:

```sh
python3 /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U010/skill/recoverable-local-workshop-bookings/scripts/book.py --state /workspace/scratch/a75c3a6d9076/D1-U010-booking-state-3zc_fceb/bookings.sqlite --ledger /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U010/work/orchid-booking-ledger.json reconcile --request-key orchid-linocut-20261122-01
```

Exit code: `0`

Stdout:

```json
{"party_id": "crew-orchid", "reason": "insufficient_capacity", "request_key": "orchid-linocut-20261122-01", "seats": 3, "slot_id": "linocut-sun-am", "state": "rejected"}
```

Stderr: empty.

### 4. Recovery-ledger inspection

Command:

```sh
sed -n '1,240p' /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U010/work/orchid-booking-ledger.json
```

Exit code: `0`

Relevant stdout: the ledger contains the exact request payload and a `last_receipt` with `state` `rejected` and `reason` `insufficient_capacity` for request key `orchid-linocut-20261122-01`.

Stderr: empty.

## Files used

- Task request: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U010/input/request.md`
- Supplied skill: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U010/skill/recoverable-local-workshop-bookings/SKILL.md`
- Requested local booking interface: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U010/input/booking.py`
- Skill coordinator: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U010/skill/recoverable-local-workshop-bookings/scripts/book.py`
- Skill-bundled booking interface: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U010/skill/recoverable-local-workshop-bookings/scripts/booking.py`
- Existing state database: `/workspace/scratch/a75c3a6d9076/D1-U010-booking-state-3zc_fceb/bookings.sqlite`
- Recovery ledger created and updated by the coordinator: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U010/work/orchid-booking-ledger.json`

The requested input interface and the skill-bundled interface had the same captured SHA-256 hash: `49ac48ca1648f172c043a11fecf7fe0c049338755a6a26e4410a5c708cc39bc8`.

## Summary and unperformed checks

Summary: the authoritative simulator first reported the key as not seen; the exact-key retry then created a persisted rejection receipt for insufficient capacity; reconciliation returned that same rejection. The outcome is therefore definitively rejected, not unresolved.

No availability command was performed because the persisted receipt is authoritative and sufficient. No initialization, alternate request, fault injection, cancellation, payment, notification, external service, or modification of another booking was performed.
