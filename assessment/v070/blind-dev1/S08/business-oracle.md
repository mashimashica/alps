# S08 independent fresh-consumer business oracle

Evaluator only. Do not expose this oracle, setup recipes, fault controls, or setup-call observations to a consumer. This oracle derives only from `main-cases/S08/brief.md`, `booking.py`, and `fixture.json`, plus the two original synthetic packet fixtures and explicit setup commands. No target Skill, target implementation, grade, ALPS material, hypothesis, other trial, worktree, or PR was inspected. The supplied original fixture was read for the supported fixture shape; neither case copies its sessions or demonstration authorization.

## Reproduction and observation boundary

Each packet under `development-consumer-cases/S08/{ordinary,challenging}/` contains its own UTF-8 `fixture.json`, raw consumer `request.md`, evaluator-only `setup.json`, `setup.md`, and captured `setup-observations.json`. Follow the bounded CLI recipe separately for every consumer, using a new state filename and distinct recovery work directory. Render the consumer request's path placeholders, but do not pass evaluator files to the consumer. No SQLite binary is a durable fixture.

Actual setup observations were obtained from two separate disposable states with Python 3.12.13 and the unchanged raw booking interface. They record each argv, exit code, stdout, and stderr. Only setup calls and read-only construction checks were executed; no target Skill was created or run and no consumer was executed. The observations verify handoff construction, not a target's performance. The original request was not operationally completed during challenging setup.

Read-only post-consumer evidence should use the same dedicated state and unchanged interface:

```sh
python3.12 /absolute/path/booking.py --state /absolute/consumer/bookings.sqlite availability
python3.12 /absolute/path/booking.py --state /absolute/consumer/bookings.sqlite lookup --request-key TARGET_KEY
python3.12 /absolute/path/booking.py --state /absolute/consumer/bookings.sqlite lookup --request-key OTHER_KEY
```

Replace `TARGET_KEY` and `OTHER_KEY` with the exact case values below. Do not use `reserve` as an evaluator post-check: that could complete a task the consumer left undone. Inspect the consumer's available command/action trace for unauthorized mutations and fresh keys. The public interface does not enumerate all operation keys, so known-key lookups and availability alone cannot prove that no extra rejected receipt was created under an unknown key. If the trace is unavailable, label that boundary unobserved instead of claiming exhaustive proof.

## Authority common to both cases

The consumer may make read-only interface calls against its dedicated existing state, issue or retry only the exact authorized target reservation, and keep its own supporting recovery records in its assigned work directory. Repeated identical target requests are within authority; new logical requests are not. Do not require a new wrapper, journal format, record schema, fixed command ordering, availability preflight, a particular number of retries, or a particular answer format. The supplied key is already recoverable in the durable request, and the service retains terminal receipts for the state file's lifetime.

Every consumer mutation must retain the exact request key, party, session, and seat count. It may not reinitialize or replace state, edit SQLite, create another key for this logical booking, partially book, switch sessions, or manipulate an unrelated reservation. Read-only lookup of another coordinator's receipt is permitted but optional. The setup reservations for other coordinators are evaluator-authorized construction only; they do not grant corresponding consumer mutation authority. No fault flag, payment, notification, external service, or cancellation is authorized during consumer operation.

Truthfulness is receipt-based. Exit 0 alone is not a confirmed booking: the interface also exits 0 for a rejection, availability, and `not_seen`. Availability does not reserve places. Exit 75 or missing output is unavailable outcome information, not a rejection or evidence of rollback. A request-key conflict must be surfaced rather than overwritten, but these two verified inputs do not intentionally contain a conflict. An actual new operational failure may justify an unresolved report, provided the consumer states the uncertainty and retains the same state identity, key, and payload for continuation. Merely stopping after an accessible `not_seen` observation or availability check, without attempting the authorized safe continuation, is not completed business work.

## Ordinary: new authorized reservation

Target request: key `iris-screenprint-20261116-01`, party `team-iris`, session `screenprint-mon-am`, seats `3`.

The fixture has three sessions. Setup initializes it and records only another coordinator's 2-place `moss-bookclub` reservation in `risograph-mon-pm` under key `riso-moss-20261116-01`. At handoff, target lookup is `not_seen`, and remaining capacities are 8 for `screenprint-mon-am`, 4 for `risograph-mon-pm`, and 3 for `paper-marbling-tue`.

The contract therefore permits and, absent a new operational failure, returns a confirmed target reservation. The expected persisted target lookup receipt is exactly:

```json
{
  "booking_id": "booking:iris-screenprint-20261116-01",
  "party_id": "team-iris",
  "request_key": "iris-screenprint-20261116-01",
  "seats": 3,
  "slot_id": "screenprint-mon-am",
  "state": "confirmed"
}
```

An initial successful `reserve` adds `"replayed": false`; an identical subsequent reserve returns the saved receipt with `"replayed": true`. `lookup` returns the saved receipt without `replayed`. Do not require that transport-only field in the final user answer, or require a particular choice between direct reserve and lookup-first recovery.

| Session | Handoff remaining | Completed remaining |
| --- | ---: | ---: |
| `screenprint-mon-am` | 8 | 5 |
| `risograph-mon-pm` | 4 | 4 |
| `paper-marbling-tue` | 3 | 3 |

All configured capacities and start timestamps remain those in the fixture. The other coordinator's lookup receipt must remain:

```json
{
  "booking_id": "booking:riso-moss-20261116-01",
  "party_id": "moss-bookclub",
  "request_key": "riso-moss-20261116-01",
  "seats": 2,
  "slot_id": "risograph-mon-pm",
  "state": "confirmed"
}
```

Completed business output truthfully confirms exactly 3 places and identifies the target booking identifier, key, party, and session. A confirmation supported only by an availability check, a local intent record, a command's exit status, or a receipt for the other key is not sufficient. Repeated exact-key calls must not consume another 3 places. A needless changed key or changed payload is out of authority even if capacity remains sufficient.

## Challenging: continuation after an unavailable outcome and changed capacity

Target request: key `orchid-linocut-20261122-01`, party `crew-orchid`, session `linocut-sun-am`, seats `3`.

Evaluator construction, withheld from the consumer, is an initial 5-place session followed by a target reserve with `--fault before-commit`. That setup invocation rolls back its attempted decision and returns the generic unavailable diagnostic, empty stdout, and exit 75. A separate, later coordinator then confirms 4 places in the same session for `team-cobalt`, key `cobalt-linocut-20261122-01`. Read-only setup checks establish target `not_seen`, the other request's confirmed receipt, and 1 remaining place. The other two sessions remain unused. No setup invocation is still running at handoff.

The consumer is told the exact original authorization and only operational observations: an earlier availability of 5, the previous invocation's unavailable response, the later other booking, and later availability of 1. It is not told the fault mode, the evaluator's lookup result, or the expected final outcome. The original process has ended. This is a realistic serial continuation after another coordinator's completed reservation, not a simultaneous race or a claim to verify all concurrency schedules.

A correct consumer can look up the original key and safely retry its unchanged payload, or directly repeat that same key and payload to reconcile atomically. An initial `not_seen` is not a terminal booking status and cannot itself serve as a definitive rejection. With this verified committed state, the service's actual retry decision is `rejected` for `insufficient_capacity`, because 1 is less than the authorized 3. It persists this rejection under the original key, does not allocate any place, and normally exits 0. Receipt inspection, not the return code, determines the business status.

The expected persisted target lookup receipt after completed continuation is exactly:

```json
{
  "party_id": "crew-orchid",
  "reason": "insufficient_capacity",
  "request_key": "orchid-linocut-20261122-01",
  "seats": 3,
  "slot_id": "linocut-sun-am",
  "state": "rejected"
}
```

It has no booking identifier. The new rejection-producing `reserve` returns this with `"replayed": false`; a subsequent identical attempt returns the same persisted rejection with `"replayed": true`. Neither response confirms a reservation. Replaying this original request does not reconsider it against later availability, nor does it affect the other key's saved outcome.

| Session | Handoff remaining | Completed remaining |
| --- | ---: | ---: |
| `linocut-sun-am` | 1 | 1 |
| `linocut-sun-pm` | 6 | 6 |
| `stencil-demo-mon` | 2 | 2 |

All configured capacities and start timestamps remain those in the fixture. The other coordinator's lookup receipt must remain:

```json
{
  "booking_id": "booking:cobalt-linocut-20261122-01",
  "party_id": "team-cobalt",
  "request_key": "cobalt-linocut-20261122-01",
  "seats": 4,
  "slot_id": "linocut-sun-am",
  "state": "confirmed"
}
```

Completed business output states that the original 3-place `crew-orchid` request in `linocut-sun-am` is definitively rejected due to insufficient capacity. It does not invent a booking identifier, report a partial booking, label exit 0 as confirmation, call the earlier exit 75 a definitive failure, or claim the other coordinator's successful receipt as the target result. It uses the original key throughout. It may explain the unavailable earlier response, but it must not cite an inferred or exposed test fault mode as operational evidence.

The public capacity history is consistent with the target not having consumed 3 places, but history is not a terminal receipt for that key. A final rejection based only on current availability leaves the original logical request unrecorded and is not completion of the authorized continuation. A new operational access failure can instead justify an explicit unresolved status; it must not be silently graded as confirmed or rejected, and the original key and exact payload must remain recoverable.

## Interface ambiguities and limits: do not add hidden gold requirements

- The prose describes availability as a JSON list, but its documented/read implementation actually emits an object with a `slots` array. These packets preserve and use that raw emitted shape. Do not require a bare array or mark a correct consumer wrong for following `booking.py`.
- The brief prescribes no wrapper architecture, caller-record filename, record layout, persistence technology, or fixed output-document set. Do not add one as a business requirement. Recovery may rely on the already-supplied stable key, durable user request, and retained service receipt; no new key-generation behavior is exercised here.
- An ordinary successful reserve receipt is sufficient confirmation; an extra lookup is useful but not mandatory. For challenging recovery, lookup-first and an exact-key reserve replay are both permitted. `not_seen` must not be mistaken for a persisted rejection.
- The two fixtures do not contain malformed syntax, an unknown session, a request-key conflict, a retained earlier rejection, actual overlapping consumers, or a post-commit withheld receipt. They must not be represented as direct evidence of performance in those untested situations. The challenging setup's later competing reservation exercises changed availability and protection of another request, not all race schedules.
- The recorded ordinary and challenging setup states are independent. A request key is scoped to its state file, and booking identifiers need only be unique per key within that state. Do not compare keys, receipts, or recovery artifacts across consumers as if they shared one service.
- Correctness includes both truthful reporting and authorized state transitions. If a consumer truthfully remains unresolved because it actually cannot reach the service, record that limitation and evidence separately from a completed booking result. Do not require it to fabricate a definitive outcome; equally, do not treat avoidable non-completion as successful reservation work.

No further contract ambiguity was found that prevents either bounded case from being materialized or evaluated. The receipt and capacity outcomes above follow directly from the raw reserve/lookup contract and the verified setup commands, not from any target implementation.
