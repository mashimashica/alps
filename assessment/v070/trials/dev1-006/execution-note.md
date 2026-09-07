# Execution note

Created `output/recoverable-local-workshop-bookings/` containing the target Skill, a bundled copy of the supplied `booking.py`, and `scripts/reconcile_booking.py`.

Resources used: the supplied brief, common Agent Skills format orientation, frozen `design-agent-work-system` Skill, its design examples and principles, frozen `design-process-description` Skill, and its process framework. The bundled simulator was copied without modification.

Checks performed:

- Initialized a fresh temporary SQLite state with the supplied fixture.
- Reserved the demonstration request (`demo-cedar-01`, `crew-cedar`, `paper-lab-am`, 2 seats) and observed a confirmed receipt.
- Repeated the same request and observed a replay without a second booking.
- Reconciled the request through `recover` and observed the terminal receipt.

The Skill documents recovery behavior for simulator exit 75, absent output, and interrupted calls, but fault-mode trials and concurrent stress tests were not completed in this handoff. No real or external booking was attempted.
