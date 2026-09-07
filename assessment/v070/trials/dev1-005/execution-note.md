# Execution note

Created `output/recoverable-local-workshop-bookings` as a self-contained Agent Skill. I used the supplied `brief.md`, `fixture.json`, `booking.py`, the common format orientation, the frozen `design-agent-work-system` Skill, its required process/design references, and the frozen skill-creator guidance.

The Skill bundles the supplied simulator unchanged and adds `scripts/book.py`. The wrapper durably records the request payload before calling the simulator, preserves the same key for retries, exposes reconciliation through lookup, and reports unresolved outcomes instead of inferring rejection. The ledger is recovery metadata; the simulator receipt remains authoritative. This keeps state effects limited to explicitly supplied local paths.

Checks performed:

- initialized a disposable SQLite state;
- completed the requested two-place `demo-cedar-01` reservation;
- replayed the same request and observed `replayed: true` without a second booking;
- reconciled the committed receipt after the caller process ended;
- compiled both Python scripts with `py_compile`.

Not performed: fault-injection recovery, concurrency stress, every syntax/business rejection, and end-to-end evaluation of an external agent interpreting the Skill. The bundled simulator's own behavior was not modified or independently revalidated beyond these wrapper checks.
