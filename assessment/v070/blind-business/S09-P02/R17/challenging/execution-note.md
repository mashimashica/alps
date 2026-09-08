# Public execution note — C-U102

## Files used

- `prompt.md`
- `skill/operational-intervention-decision/SKILL.md`
- `input/request.md`
- `input/sources/measurement_notes.md`
- `input/sources/decision_context.md`
- `input/sources/shift_operations.csv`
- `input/sources/shipment_cohorts.csv`

No web source, other assessment trial, creator material, evaluation material, or external system was used. No live operation, record, message, staffing assignment, or spending commitment was changed.

## Commands and captured results

All commands used working directory `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U102` unless another directory is shown.

1. `cat /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U102/prompt.md`
   - Exit code: `0`
   - Exact relevant stdout: `Use the Skill at /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U102/skill/operational-intervention-decision/SKILL.md to complete the user's task in /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U102/input/request.md with any accompanying files in that input folder.`
   - Stderr: none captured.

2. `cat /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U102/skill/operational-intervention-decision/SKILL.md`
   - Exit code: `0`
   - Captured-summary label: the skill requires line/date reconciliation, mature-outcome denominators, planned-mix standardization, separate labor/training/overtime and dispatch checks, explicit evidence limits, and a continue/narrow/expand/stop decision.
   - Stderr: none captured.

3. `cat /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U102/input/request.md`
   - Exit code: `0`
   - Exact relevant stdout: `Manager Nessa Vale needs an actual scoped decision for the next twenty full shifts: continue, change the scope, propose expansion, or stop.`
   - Stderr: none captured.

4. `find /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U102/input -maxdepth 1 -type f -printf '%f\n'`
   - Exit code: `0`
   - Exact stdout: `request.md`
   - Stderr: none captured.

5. `find /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U102/input -maxdepth 3 -type f -print`
   - Exit code: `0`
   - Captured-summary label: stdout listed the five input files `request.md`, `sources/shift_operations.csv`, `sources/shipment_cohorts.csv`, `sources/measurement_notes.md`, and `sources/decision_context.md` under the assigned input directory.
   - Stderr: none captured.

6. The following four read-only commands were executed in `input/sources`:
   - `cat measurement_notes.md`
   - `cat decision_context.md`
   - `cat shift_operations.csv`
   - `cat shipment_cohorts.csv`
   - Exit code for each: `0`
   - Exact CSV values captured: every August 28 shipment row has `mature_orders` value `0`; the Alder August 17 operations row has `productive_labor_hours=95`, `training_hours=5`, and `late_dispatch_orders=14`; the Alder August 18 and 19 rows each have `productive_labor_hours=90` and `late_dispatch_orders=14`.
   - Calculated-observation label: shipment rows aggregate to 1,200 orders per ordinary line/date and 600 per August 28 line/date.
   - Captured-summary label: the notes identify August 3–5 and 17–19 as ordinary full shifts, August 28 as a short unusually simple shift, operations as one row per date/line, and catches as non-comparable across the August 14 recording change.
   - Stderr: none captured.

7. `python3 deliverables/reproduce_decision.py`
   - Exit code: `0` on both executions.
   - Exact relevant stdout:

```text
baseline Alder: total=132/3600=3.6667%; standard=42/2100=2.0000%; complex=90/1500=6.0000%; 70/30 standardized=3.2000%
baseline Birch: total=102/3600=2.8333%; standard=42/2100=2.0000%; complex=60/1500=4.0000%; 70/30 standardized=2.6000%
pilot Alder: total=63/3600=1.7500%; standard=33/3300=1.0000%; complex=30/300=10.0000%; 70/30 standardized=3.7000%
pilot Birch: total=51/3600=1.4167%; standard=33/3300=1.0000%; complex=18/300=6.0000%; 70/30 standardized=2.5000%
Alder standardized change=+0.5000%
Birch standardized change=-0.1000%
difference-in-differences adjustment=+0.6000%
adjusted no-check planning rate=3.1000%
orders per line=28800; standard=20160; complex=8640
all-check=90.0*1.2=108.0 h/shift; cap=102.0; over cap=6.0
baseline no-check=82.0*1.2=98.4 h/shift
added checking labor=9.6 h/shift; cost=$326.40/shift; 20-shift cost=$6,528.00
Alder pilot ordinary full shifts=42/3600=1.1667%; projected late=336; 1% ceiling=288
```

   - Stderr: none captured.

8. `python3 -m py_compile deliverables/reproduce_decision.py`
   - Exit code: `0`
   - Stdout/stderr: empty.

## Files created

- `deliverables/reproduce_decision.py` — standard-library reproduction script with join-key assertions and scenario arithmetic.
- `answer.md` — user-facing decision and bounded follow-up.
- `execution-note.md` — this public record.

The three files were created with `apply_patch`; each patch call completed successfully and returned no textual stdout or stderr. No check beyond the recorded script execution and Python compilation was performed.
