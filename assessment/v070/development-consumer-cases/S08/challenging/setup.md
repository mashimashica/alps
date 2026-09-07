# S08 challenging case: evaluator setup only

Do not give this file, `setup.json`, the setup observations, or the oracle to the consumer. In particular, do not expose the selected fault mode or the evaluator's lookup result. The consumer gets only the rendered `request.md`, its own existing state path, its own work directory, the unchanged local booking interface, and the target Skill/support materials being assessed.

This packet's `fixture.json` is original synthetic data. For every consumer, create a fresh disposable directory with `mktemp -d`, choose a new absolute `bookings.sqlite` filename in it, and allocate a separate existing work directory. Do not reuse any other consumer's database or caller-side recovery files. Persist no database binaries as inputs.

Bind `setup.json` to the available Python 3.12 executable, unchanged `main-cases/S08/booking.py`, this fixture, and that new state path. Execute its seven argv arrays in listed order, each as a separate process. Await the end of every command. The `original_uncertain_attempt` must exit 75, emit no stdout, and emit the common unavailable diagnostic on stderr. That nonzero exit is an intended setup event; capture it and continue. All other commands must exit 0. Compare each call's parsed JSON, exit code, and stderr with `setup-observations.json`, ignoring only disposable path bindings and JSON object-key order. Stop on a mismatch. Never construct or correct state by editing SQLite directly.

The fault flag is evaluator-only state construction, not evidence available to the business consumer. The raw interface states that either fault mode produces the same operational failure observation. The prompt records the actual observable exit, stdout, stderr, and availability history, but not the test control. Recovery calls must not use a fault flag.

The other coordinator's reservation is a bounded evaluator-authorized setup call, not authority for the consumer to touch that reservation. It occurs after the original uncertain invocation has ended. All setup processes have ended before handoff; do not leave a lock holder or an in-flight reservation running. This sequence represents a later independent booking, not a claim to test simultaneous-process scheduling.

Do not run the original request again during setup. Doing so would change the handoff condition. The final two lookup commands are read-only construction checks and are not included in the consumer's handoff text. Replace `{{STATE_DB}}`, `{{BOOKING_PY}}`, and `{{WORK_DIR}}` in `request.md` with the consumer's own absolute paths.

The fixture, ordered commands, and captured observations reproduce the committed logical state. Keep disposable generated databases and sidecars outside this packet. The durable inputs are these UTF-8 files, not a byte-for-byte SQLite snapshot.
