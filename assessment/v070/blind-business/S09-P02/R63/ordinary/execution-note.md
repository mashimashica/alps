# Public execution note — C-U097

## Scope and state

Only the task-local prompt, supplied Skill, the five files in `input/`, and created local deliverables were accessed. The supplied Skill and original input files were not modified. No web access, external communication, live operating change, spending, commit, upload, installation, or delegation occurred.

Before restoration, four shell submissions failed before process launch because the exec server returned `409 Conflict (environment_offline)`. They produced no process exit code, stdout, stderr, file read, or state change:

```text
cat prompt.md
cat prompt.md
pwd && cat ./prompt.md
cat /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U097/prompt.md
```

After the parent confirmed restoration, the same attempt resumed.

## Successful commands and observations

1. Command, run in the consumer folder:

   ```bash
   cat prompt.md
   ```

   Exit code: `0`. Exact observation: stdout contained the full task-local prompt; stderr was empty.

2. Command:

   ```bash
   cat skill/operational-intervention-decision/SKILL.md && find input -maxdepth 2 -type f -print
   ```

   Exit code: `0`. Exact observation: stdout contained the complete supplied Skill followed by these paths; stderr was empty:

   ```text
   input/sources/shift_operations.csv
   input/sources/shipment_cohorts.csv
   input/sources/measurement_notes.md
   input/sources/decision_context.md
   input/request.md
   ```

3. Command:

   ```bash
   cat input/request.md && cat input/sources/measurement_notes.md && cat input/sources/decision_context.md && cat input/sources/shipment_cohorts.csv && cat input/sources/shift_operations.csv
   ```

   Exit code: `0`. Exact observation: stdout contained the complete contents of all five supplied input files in the stated order; stderr was empty. Those supplied contents are not duplicated here.

4. `apply_patch` created `deliverables/reproduce.py`. Tool output was exactly `{}` and reported success. No source file was altered.

5. Command:

   ```bash
   python3 deliverables/reproduce.py
   ```

   Exit code: `0`; stderr was empty. This initial run verified the aggregation. The script was then updated with `apply_patch` to add full-shift process observations and dispatch/cost sensitivities; tool output was exactly `{}` and reported success.

6. Final numerical reproduction command:

   ```bash
   python3 deliverables/reproduce.py
   ```

   Exit code: `0`; stderr was empty. Exact stdout:

   ```text
   MATURE OUTCOMES BY PERIOD / LINE / BAND
   baseline Harbor complex  mispack=36/600 (6.000%), shipped=600, catches=8
   baseline Harbor standard mispack=27/1800 (1.500%), shipped=1800, catches=5
   baseline Ridge  complex  mispack=36/600 (6.000%), shipped=600, catches=7
   baseline Ridge  standard mispack=27/1800 (1.500%), shipped=1800, catches=5
   pilot    Harbor complex  mispack=18/600 (3.000%), shipped=680, catches=20
   pilot    Harbor standard mispack=12/1800 (0.667%), shipped=2040, catches=23
   pilot    Ridge  complex  mispack=33/600 (5.500%), shipped=680, catches=9
   pilot    Ridge  standard mispack=27/1800 (1.500%), shipped=2040, catches=7

   MATURE OUTCOMES BY PERIOD / LINE
   baseline Harbor mispack=63/2400 (2.625%), shipped=2400, catches=13
   baseline Ridge  mispack=63/2400 (2.625%), shipped=2400, catches=12
   pilot    Harbor mispack=30/2400 (1.250%), shipped=2720, catches=43
   pilot    Ridge  mispack=60/2400 (2.500%), shipped=2720, catches=16

   IMMATURE: 640 shipped orders across 4 cohorts; confirmed outcome unavailable

   FULL-SHIFT OPERATIONS BY PERIOD / LINE
   baseline Harbor shifts=3, productive=186 (62.000/shift), training=0, overtime=6 (2.000/shift), late=14/2400 (0.583%)
   baseline Ridge  shifts=3, productive=186 (62.000/shift), training=0, overtime=6 (2.000/shift), late=14/2400 (0.583%)
   pilot    Harbor shifts=3, productive=198 (66.000/shift), training=3, overtime=15 (5.000/shift), late=13/2400 (0.542%)
   pilot    Ridge  shifts=3, productive=186 (62.000/shift), training=0, overtime=6 (2.000/shift), late=13/2400 (0.542%)

   FULL-SHIFT PROCESS OBSERVATIONS (not downstream outcomes)
   baseline Harbor catches=13/2400 (0.542%)
   baseline Ridge  catches=12/2400 (0.500%)
   pilot    Harbor catches=38/2400 (1.583%)
   pilot    Ridge  catches=14/2400 (0.583%)

   SHORT-SHIFT DISPATCH (immediately observable)
   Harbor late=2/320 (0.625%)
   Ridge  late=1/320 (0.312%)

   PLANNING PROJECTION (assumptions, not realized results)
   Harbor raw change: -1.375 percentage points
   Ridge contemporaneous change: -0.125 percentage points
   Comparison-adjusted Harbor change: -1.250 percentage points
   Planned orders: 16,000 per line; 32,000 both lines
   Recurring check hours: 65.0/shift versus 62.0 baseline; +3.0, cap headroom=3.0
   Per line: projected avoided mispacks=200, avoidable error cost=$9,600, added hours=60, labor cost=$1,920, net=$7,680
   Per line, raw Harbor pre/post sensitivity: avoided mispacks=220, avoidable error cost=$10,560, net=$8,640
   Both lines: projected avoided mispacks=400, avoidable error cost=$19,200, added hours=120, labor cost=$3,840, net=$15,360
   Dispatch commitment: <= 160 late orders per line (1% of plan)
   At Harbor's pilot full-shift dispatch rate: projected late orders=86.7 per line (0.542%)
   ```

7. `apply_patch` created `answer.md`. Tool output was exactly `{}` and reported success.

8. Final validation command:

   ```bash
   python3 -m py_compile deliverables/reproduce.py && sed -n '1,260p' answer.md
   ```

   Exit code: `0`; stderr was empty. Exact observation: byte-code compilation succeeded and stdout displayed the complete final `answer.md` (1,717 output tokens as reported by the runner).

9. `apply_patch` created this `execution-note.md`. Tool output was exactly `{}` and reported success.

## Files used

- `prompt.md`
- `skill/operational-intervention-decision/SKILL.md`
- `input/request.md`
- `input/sources/measurement_notes.md`
- `input/sources/decision_context.md`
- `input/sources/shipment_cohorts.csv`
- `input/sources/shift_operations.csv`
- `deliverables/reproduce.py` (created)
- `answer.md` (created)
- `execution-note.md` (created)

The frozen skill-creator aid was available but not needed and was not read. No checks beyond those listed above were performed.
