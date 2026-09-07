# S08 — Recoverable local workshop bookings

## Business work

The target Agent Skill helps a workshop coordinator reserve a specified number of places in one specified session for a supplied party identifier. Each user-authorized logical booking has a stable request key. A continuation or retry of that booking uses the same key and the same party, session, and place count; a genuinely new authorization uses a new key. If the key is missing, the supporting system must establish one and make it recoverable before the first attempt that could reserve places.

The coordinator needs one of three truthful outcomes: confirmed, definitively rejected with the reason, or unresolved and still requiring reconciliation. A confirmed outcome includes the booking identifier, request key, party, session, and place count. A nonzero command exit, timeout, interrupted invocation, or missing output does not by itself show that nothing was booked. Never report a confirmed booking based only on an earlier availability check, and never repeat a possibly completed booking under a fresh key just to get a clean response.

Independent coordinators may reserve the same remaining places at the same time. Two continuations of the same request may also overlap. A successful booking must not be duplicated, capacity must not be oversold, and one request's retry must not change another request's outcome. A request-key conflict is a problem to surface, not an invitation to overwrite the earlier request. No substitution of another session, partial booking, cancellation, payment, notification, or external booking service is authorized. The scope is only the supplied local simulator state.

The demonstration work is to reserve two places in `paper-lab-am` for `crew-cedar`, using request key `demo-cedar-01`. Other supplied sessions, parties, keys, and positive place counts within the interface's limits are in scope. Recovery must still work after the caller's process has ended; it must not depend on an in-memory observation that disappears between attempts.

## Available booking interface

Python 3.12 and its standard library, plus a local shell, are available. `booking.py` is a local stand-in for a booking service. `fixture.json` supplies original synthetic sessions. Use an existing disposable directory and a new state filename:

```sh
python3.12 booking.py --state /absolute/disposable/bookings.sqlite init --fixture fixture.json
python3.12 booking.py --state /absolute/disposable/bookings.sqlite availability
python3.12 booking.py --state /absolute/disposable/bookings.sqlite reserve --request-key demo-cedar-01 --party-id crew-cedar --slot-id paper-lab-am --seats 2
python3.12 booking.py --state /absolute/disposable/bookings.sqlite lookup --request-key demo-cedar-01
```

`init` refuses to overwrite an existing destination. Operational access is through these commands, not by changing the database directly. Separate test scenarios should use separate state files. The helper never contacts the network. Its only persistent effects are in the explicitly supplied state database; SQLite may use the corresponding `-journal` sidecar during a transaction. It does not manage any real bookings.

| Command | Information and effect contract |
| --- | --- |
| `availability` | Read-only JSON list of `slot_id`, `starts_at`, `capacity`, and `remaining`. This is a point-in-time observation, not a hold or a promise. |
| `reserve` | Takes `request_key`, `party_id`, `slot_id`, and integer `seats`. Atomically records a terminal receipt and, only if accepted, decrements that one session's remaining places. |
| `lookup` | Read-only lookup of a terminal receipt by request key. Returns the saved receipt or `{"state":"not_seen","request_key":"..."}`. |

Keys, party IDs, and slot IDs use 1–80 ASCII letters, digits, `.`, `_`, or `-`, beginning with a letter or digit. `seats` is an integer from 1 through 100. Invalid syntax exits 2 without changing the state. A syntactically valid request for an unknown session or too many remaining places is a definitive business rejection, not a syntax error.

For a new valid request key, the `reserve` response is a JSON receipt. Its `state` is `confirmed` or `rejected`, and it includes the request key, party ID, slot ID, and requested seats. Confirmation includes `booking_id`. Rejection includes `reason` (`unknown_slot` or `insufficient_capacity`). Both outcomes are persisted. Normal responses exit 0, including business rejections. The response additionally reports `replayed: false` for a newly created receipt and `replayed: true` for a replay.

Reusing the same key with the exact same payload returns the saved outcome and does not consume places again, even if another request has since changed availability. Reusing it with any changed party, session, or seat count exits 3 with `idempotency_conflict` and makes no changes. Receipt retention is unlimited for the lifetime of this state file, including rejections. A confirmed booking identifier is unique to its request key within that state. The same key in another state file is unrelated.

Reservation decisions, capacity changes, and receipt creation commit in one SQLite transaction. Concurrent requests are serialized at this boundary, so committed remaining capacity cannot go below zero. Concurrent attempts of the same key and payload converge on one terminal receipt. Lock contention can produce exit 75. The safe interpretation of exit 75, or absent trustworthy output, is “outcome unavailable; reconcile using the same key,” not “rejected.”

`lookup` sees committed state. `not_seen` is only an observation at that instant: another invocation may be in flight and later commit. It is not grounds for starting the same logical booking under a new key. Retrying with the original key and payload remains safe. If the service cannot be reached or the result cannot yet be established, retain an unresolved outcome and enough information to continue safely.

For local verification only, `reserve` accepts `--fault before-commit` or `--fault after-commit`. The first rolls back the attempted decision; the second commits it and then withholds its receipt. Both produce no stdout, the same stderr message, and exit 75. The fault setting is simulator control, not an operational signal on which the target work may rely. Faults apply only when creating a new receipt: replaying an already recorded identical request returns that receipt normally. Run recovery without a fault flag. These controls let you check both possibilities behind the same observed failure without external side effects.

## Assignment

Design, implement, and locally verify the supporting system needed by the target Agent Skill for this booking work. Decide what should be reused and what additional support is justified. Preserve the authorization, uncertainty, idempotency, and concurrency boundaries in the business work and interface. Make the operational inputs, outcomes, recovery information, limitations, and verification evidence clear enough for the target Skill to use the result. No particular wrapper, persistence layout for the caller, runtime architecture, or output-document set is prescribed.
