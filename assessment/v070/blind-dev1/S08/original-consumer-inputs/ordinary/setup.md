# S08 ordinary case: evaluator setup only

Do not give this file, `setup.json`, the setup observations, or the oracle to the consumer. Give the consumer only the rendered `request.md`, its own existing state path, its own work directory, the unchanged local booking interface, and the target Skill/support materials being assessed.

This packet's `fixture.json` is original synthetic data. No database binary is a durable input. For every consumer, create a fresh disposable directory using `mktemp -d`, choose a new absolute `bookings.sqlite` filename inside it, and allocate a separate existing work directory. Do not share a state or a caller-side recovery directory between consumers.

Bind the four interface tokens in `setup.json` to the available Python 3.12 executable, the unchanged `main-cases/S08/booking.py`, this fixture, and the consumer's nonexistent state filename. Run the five argv arrays exactly in listed order. Invoke each command as a separate process; do not edit SQLite directly. All five calls must exit 0. Compare their parsed JSON and stderr to `setup-observations.json`, ignoring only the disposable absolute path bindings and JSON object-key order. Stop and report a setup mismatch rather than handing over the wrong state. The observations were captured from a separate disposable verification state, not a consumer state.

The sole setup reservation is evaluator-authorized construction of another coordinator's pre-existing booking. The consumer has no authority to change it. Do not make any additional reservations before consumer handoff. Replace `{{STATE_DB}}`, `{{BOOKING_PY}}`, and `{{WORK_DIR}}` in `request.md` with the consumer's own absolute paths.

State construction is entirely specified by the fixture and five bounded commands. The database's storage bytes and timestamps are not comparison criteria. Keep the generated database and sidecars outside the packet; preserve the UTF-8 recipe and observations instead.
