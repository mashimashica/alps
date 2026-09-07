# Execution note

## Files used

- Assignment: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U012/prompt.md`
- Skill instructions: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U012/skill/recoverable-local-workshop-bookings/SKILL.md`
- Skill recovery wrapper: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U012/skill/recoverable-local-workshop-bookings/scripts/reconcile_booking.py`
- Skill-bundled simulator: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U012/skill/recoverable-local-workshop-bookings/scripts/booking.py`
- User request: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U012/input/request.md`
- User-specified simulator interface: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U012/input/booking.py`
- Existing simulator state: `/workspace/scratch/a75c3a6d9076/D1-U012-booking-state-0kvoufxa/bookings.sqlite`
- Durable recovery journal: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U012/work/booking-requests.json`

## Exact captured operational observations

### State and interface checks

Command:

```sh
test -f /workspace/scratch/a75c3a6d9076/D1-U012-booking-state-0kvoufxa/bookings.sqlite
state_status=$?
cmp -s /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U012/input/booking.py /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U012/skill/recoverable-local-workshop-bookings/scripts/booking.py
interface_cmp=$?
printf 'state_file_test_exit=%s\ninterface_cmp_exit=%s\n' "$state_status" "$interface_cmp"
```

Exit code: `0`

Stdout:

```text
state_file_test_exit=0
interface_cmp_exit=0
```

Stderr: empty.

This directly establishes that the existing state path was present and that the wrapper's bundled `booking.py` was byte-for-byte identical to the user-specified interface at the time of execution.

### Durable request reconstruction

Before recovery, `work/booking-requests.json` was created via `apply_patch` with the exact authorized request and state `unresolved`:

```json
{"orchid-linocut-20261122-01":{"request":{"party_id":"crew-orchid","request_key":"orchid-linocut-20261122-01","seats":3,"slot_id":"linocut-sun-am"},"state":"unresolved"}}
```

This was a supporting recovery record only; the SQLite simulator state was not edited directly.

### Recovery

Command:

```sh
python3 /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U012/skill/recoverable-local-workshop-bookings/scripts/reconcile_booking.py recover --state /workspace/scratch/a75c3a6d9076/D1-U012-booking-state-0kvoufxa/bookings.sqlite --request-key orchid-linocut-20261122-01 --journal /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U012/work/booking-requests.json
```

Exit code: `0`

Stdout:

```json
{"party_id": "crew-orchid", "reason": "insufficient_capacity", "replayed": false, "request_key": "orchid-linocut-20261122-01", "seats": 3, "slot_id": "linocut-sun-am", "state": "rejected"}
```

Stderr: empty.

The supplied wrapper defines exit `0` plus state `rejected` as terminal. In `recover` mode it performs a lookup first and retries the exact journaled payload only if lookup returns `not_seen`. The captured `replayed: false` terminal receipt is consistent with that exact retry creating the rejection receipt.

### Independent read-only receipt lookup

Command:

```sh
python3 /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U012/input/booking.py --state /workspace/scratch/a75c3a6d9076/D1-U012-booking-state-0kvoufxa/bookings.sqlite lookup --request-key orchid-linocut-20261122-01
```

Exit code: `0`

Stdout:

```json
{"party_id":"crew-orchid","reason":"insufficient_capacity","request_key":"orchid-linocut-20261122-01","seats":3,"slot_id":"linocut-sun-am","state":"rejected"}
```

Stderr: empty.

### Persisted journal check

Command:

```sh
sed -n '1,80p' /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/D1-U012/work/booking-requests.json
```

Exit code: `0`

Stdout:

```json
{"orchid-linocut-20261122-01": {"receipt": {"party_id": "crew-orchid", "reason": "insufficient_capacity", "replayed": false, "request_key": "orchid-linocut-20261122-01", "seats": 3, "slot_id": "linocut-sun-am", "state": "rejected"}, "request": {"party_id": "crew-orchid", "request_key": "orchid-linocut-20261122-01", "seats": 3, "slot_id": "linocut-sun-am"}, "state": "rejected"}}
```

Stderr: empty.

## Supplied observations and unperformed checks

The earlier exit `75`, its stderr, the earlier availability of 5, the other coordinator's 4-place confirmation, and the later availability of 1 were supplied in `input/request.md`; they were not independently reproduced. No availability command was run because availability cannot confirm or reject this request. No direct SQLite query, initialization, replacement, cancellation, altered-payload reservation, new request key, fault injection, notification, payment, external service, or change to another booking was performed.

## Result summary

The original request `orchid-linocut-20261122-01` for party `crew-orchid`, session `linocut-sun-am`, and exactly 3 places is terminally rejected with reason `insufficient_capacity`. A rejected request has no booking identifier.
