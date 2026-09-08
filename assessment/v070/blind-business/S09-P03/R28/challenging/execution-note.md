# Public execution note

## Scope

Applied the supplied `intervention-decision` skill to the supplied Fenwick request and synthetic source packet. No external state was changed, no messages were sent, and the supplied Skill and inputs were not edited.

## Files read

- `prompt.md`
- `skill/intervention-decision/SKILL.md`
- `input/request.md`
- `input/sources/measurement_notes.md`
- `input/sources/decision_context.md`
- `input/sources/shipment_cohorts.csv`
- `input/sources/shift_operations.csv`

## Files created

- `answer.md`
- `deliverables/decision.md`
- `deliverables/reproduce_decision.py`
- `deliverables/calculation_output.txt`
- `execution-note.md`

## Commands and captured results

All commands used the task directory `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U104` or an explicitly stated parent work directory.

1. Read the task prompt.

   Command:

   ```bash
   cat /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U104/prompt.md
   ```

   Exit code: `0`. Relevant stdout: the prompt required application of the supplied Skill, use of the supplied input packet, creation of `answer.md` via `apply_patch`, and an execution note. Stderr: none.

2. Read the supplied Skill and request, and identify the input files.

   Commands:

   ```bash
   cat /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U104/skill/intervention-decision/SKILL.md
   cat /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U104/input/request.md
   find /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U104/input -maxdepth 2 -type f -print
   ```

   Each command exited `0`. The exact `find` stdout was:

   ```text
   /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U104/input/sources/shift_operations.csv
   /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U104/input/sources/shipment_cohorts.csv
   /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U104/input/sources/measurement_notes.md
   /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U104/input/sources/decision_context.md
   /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U104/input/request.md
   ```

   Stderr: none.

3. Read the four supplied source files.

   Commands:

   ```bash
   cat input/sources/measurement_notes.md
   cat input/sources/decision_context.md
   cat input/sources/shipment_cohorts.csv
   cat input/sources/shift_operations.csv
   ```

   Each command exited `0`; stderr was empty. Exact source contents remain in the files listed above. Captured observations used in the decision included: August 28 had zero mature orders; station-catch recording changed August 14; operations rows were whole-line date rows; August 3–5 and 17–19 were comparable full shifts; August 28 was a short 600-order shift; the next period was 20 shifts at 1,440 orders per line and a 70/30 mix; the hard cap was 102 productive hours per line per shift; and the dispatch promise was no more than 1%.

4. Created the reproducibility script with `apply_patch`. The tool returned `{}` and reported successful completion.

5. Ran the reproducibility script.

   Command:

   ```bash
   python3 deliverables/reproduce_decision.py
   ```

   Exit code: `0`. Stderr: none. Exact stdout:

   ```text
   QUALITY COHORTS — downstream rate uses mature orders only
   period,line,band,shipped,mature,errors,error_rate
   baseline,Alder,complex,1500,1500,90,6.000%
   baseline,Alder,standard,2100,2100,42,2.000%
   baseline,Birch,complex,1500,1500,60,4.000%
   baseline,Birch,standard,2100,2100,42,2.000%
   pilot,Alder,complex,330,300,30,10.000%
   pilot,Alder,standard,3870,3300,33,1.000%
   pilot,Birch,complex,330,300,18,6.000%
   pilot,Birch,standard,3870,3300,33,1.000%

   OPERATIONS — all recorded shifts; line rows counted once
   period,line,shipped,productive_hours,training_hours,late,late_rate
   baseline,Alder,3600,246.0,0.0,21,0.583%
   baseline,Birch,3600,240.0,0.0,18,0.500%
   pilot,Alder,4200,311.0,5.0,42,1.000%
   pilot,Birch,4200,280.0,0.0,18,0.429%

   COMPARABLE FULL-SHIFT OPERATIONS — excludes the 600-order August 28 shift
   period,line,shifts,shipped,productive_hours,training_hours,recurring_hours,late,late_rate
   baseline,Alder,3,3600,246.0,0.0,246.0,21,0.583%
   baseline,Birch,3,3600,240.0,0.0,240.0,18,0.500%
   pilot,Alder,3,3600,275.0,5.0,270.0,42,1.167%
   pilot,Birch,3,3600,246.0,0.0,246.0,18,0.500%

   QUALITY DIFFERENCE-IN-DIFFERENCES
   standard: (2.000% - 1.000%) - (2.000% - 1.000%) = 0.000% reduction
   complex: (6.000% - 10.000%) - (4.000% - 6.000%) = -2.000% reduction

   NEXT-PERIOD PLANNING SCENARIO
   workload = 20 shifts * 1440 orders = 28800 Alder orders
   mix = 70% standard / 30% complex
   weighted incremental reduction = 70%*0.000% + 30%*-2.000% = -0.600%
   modeled no-check quality rate = 3.100%; expected errors = 892.8
   observed-check mix-weighted quality rate = 3.700%; expected errors = 1065.6
   incremental checked errors = 172.8; error-cost difference = $9,504
   labor DiD at 1,200 orders = (90.0 - 82.0) - (82.0 - 80.0) = 6.0 hours
   modeled no-check hours at 1,440 = 100.8; checked hours = 108.0; cap = 102.0
   incremental checker hours = 7.2/shift * 20 shifts = 144.0; labor cost = $4,896
   modeled no-check error cost = $49,104
   modeled checked error cost = $58,608; plus incremental labor = $4,896
   modeled relevant-cost difference (check minus no check) = $14,400
   pilot full-shift late rate: Alder checked = 1.167%; Birch no-check = 0.500%; promise <= 1.000%

   INTERPRETATION LIMITS
   - Assignment was voluntary, not randomized; the template and catch-recording rules changed concurrently.
   - The complex pilot cells contain only 300 mature orders per line, and the future mix is 30% complex versus 8.3% in mature pilot orders.
   - Capacity uses constant hours per order; no time-by-band data or validated capacity curve exists.
   - August 28 has zero mature orders and is excluded from quality rates; its short shift is excluded from full-shift capacity and dispatch comparisons.
   - Station catches are not added to downstream errors because their recording rule changed.
   ```

6. Captured the same calculation output.

   Command:

   ```bash
   python3 deliverables/reproduce_decision.py > deliverables/calculation_output.txt
   ```

   Exit code: `0`. Stdout and stderr: empty because stdout was redirected to the file.

7. Created `answer.md` and `deliverables/decision.md` with `apply_patch`, then corrected their formula rendering and a rounded dispatch delta with `apply_patch`. Each tool call returned `{}` and reported successful completion.

8. Inspected and validated the deliverables.

   Commands:

   ```bash
   sed -n '1,260p' answer.md
   cmp -s answer.md deliverables/decision.md
   python3 -m py_compile deliverables/reproduce_decision.py
   ```

   Each command exited `0`; stderr was empty. The `sed` output showed the complete decision narrative. The `cmp` result confirmed the two decision files were byte-identical at that check. The Python compilation check produced no stdout.

9. Repeated final validation after the rendering correction.

   Commands:

   ```bash
   cmp -s answer.md deliverables/decision.md
   python3 -m py_compile deliverables/reproduce_decision.py
   rg -n 'Standard:|Complex:|Next-period mix|Check minus no check|Cost uses only' answer.md
   test -s answer.md -a -s execution-note.md -a -s deliverables/decision.md -a -s deliverables/reproduce_decision.py -a -s deliverables/calculation_output.txt
   ```

   Each command exited `0`; stderr was empty. The first, second, and fourth commands produced no stdout. Exact `rg` stdout was:

   ```text
   36:- Standard: `(2% - 1%) - (2% - 1%) = 0` percentage points of incremental reduction.
   37:- Complex: `(6% - 10%) - (4% - 6%) = -2` percentage points of incremental reduction.
   38:- Next-period mix: `70% × 0 + 30% × (-2%) = -0.6` percentage points.
   67:| Check minus no check | +0.600 pp | +172.8 | +7.2 | +0.583 pp | +$14,400 |
   71:Cost uses only the authorized assumptions. The no-check outcome cost is `892.8 × $55 = $49,104`. The checked outcome cost is `1,065.6 × $55 = $58,608`. Estimated incremental checker labor is `7.2 × 20 = 144` hours, costing `144 × $34 = $4,896`. Thus checked relevant cost is $63,504, or $14,400 more than modeled no-check. No dollar value is assigned to missed carrier cutoffs.
   ```

## Summaries and unperformed checks

The decision and numeric estimates are summaries derived from the exact source values and reproduced by the script. No causal significance test, confidence interval, or external benchmark was performed. No browser or external data source was used. No live operating change, staffing action, spending commitment, message, upload, install, commit, or push was performed. No calendar date was invented for the follow-up because the source packet supplies no next-period schedule; the decision uses the review point seven calendar days after shift 10.
