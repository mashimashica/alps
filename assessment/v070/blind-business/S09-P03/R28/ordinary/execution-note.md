# Public execution note

## Files used

- `prompt.md`
- `skill/intervention-decision/SKILL.md`
- `input/request.md`
- `input/sources/measurement_notes.md`
- `input/sources/decision_context.md`
- `input/sources/shipment_cohorts.csv`
- `input/sources/shift_operations.csv`

## Files created

- `answer.md` via `apply_patch`
- `deliverables/reproduce_decision.py` via `apply_patch`
- `deliverables/calculation-output.txt` by redirecting the reproduction script's stdout
- `execution-note.md` via `apply_patch`

No supplied Skill or original input file was edited.

## Commands and captured observations

All commands ran with working directory `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U103` unless the command contains an absolute path. No command emitted stderr.

1. `cat /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U103/prompt.md`
   - Exit code: `0`
   - Relevant stdout: exact assessment instructions, including the supplied Skill path, input request path, required `answer.md`, permitted `work` area, and execution-note requirement.

2. `cat skill/intervention-decision/SKILL.md`
   - Exit code: `0`
   - Relevant stdout: exact supplied Skill contents. The Skill requires mature-only outcome rates, line-level operations aggregated once, training separated from recurring hours, mix-aware comparison, authorized cost assumptions only, one actionable disposition, bounded follow-up, and a reproducible trace.

3. `cat input/request.md`
   - Exit code: `0`
   - Relevant stdout: exact user request for Cedar Quay's next-twenty-full-shift decision and a local reproducibility method.

4. `find input -maxdepth 2 -type f -print`
   - Exit code: `0`
   - Exact stdout:

```text
input/sources/shift_operations.csv
input/sources/shipment_cohorts.csv
input/sources/measurement_notes.md
input/sources/decision_context.md
input/request.md
```

5. `cat input/sources/measurement_notes.md`
   - Exit code: `0`
   - Relevant stdout summary: exact file contents established the seven-day maturity definition, July 31 immaturity and partial-shift status, catch definition, line-level operations grain, productive/overtime/training relationships, unchanged measurement rules, and absence of missing rows.

6. `cat input/sources/decision_context.md`
   - Exit code: `0`
   - Relevant stdout summary: exact file contents supplied the 20 shifts, 800 orders per line per shift, 75%/25% mix, 68-hour line ceiling, separate one-off training allowance, $48 error cost, $32 marginal labor cost, 1% late-dispatch promise, voluntary assignment, and authority limits.

7. `cat input/sources/shipment_cohorts.csv`
   - Exit code: `0`
   - Relevant stdout summary: exact CSV contents contained 28 mutually exclusive date/line/band cohort rows, including 24 mature full-shift rows and four immature July 31 rows.

8. `cat input/sources/shift_operations.csv`
   - Exit code: `0`
   - Relevant stdout summary: exact CSV contents contained 14 date/line operations rows, including twelve ordinary full-shift rows and two July 31 partial-shift rows.

9. `python3 deliverables/reproduce_decision.py`
   - Exit code: `0`
   - Exact relevant stdout:

```text
COHORT TABLE (rates use mature_orders only; pilot shipped includes July 31 immature orders)
period,line,band,shipped,mature,confirmed_mispack_7d,mature_rate,station_catches
baseline,Harbor,complex,600,600,36,6.000%,8
baseline,Harbor,standard,1800,1800,27,1.500%,5
baseline,Ridge,complex,600,600,36,6.000%,7
baseline,Ridge,standard,1800,1800,27,1.500%,5
pilot,Harbor,complex,680,600,18,3.000%,20
pilot,Harbor,standard,2040,1800,12,0.667%,23
pilot,Ridge,complex,680,600,33,5.500%,9
pilot,Ridge,standard,2040,1800,27,1.500%,7

FULL-SHIFT OPERATIONS (July 31 partial shift excluded)
period,line,shifts,shipped,productive_hours,training_hours,recurring_hours_per_shift,overtime_hours,late_dispatches,late_rate
baseline,Harbor,3,2400,186,0,62.000,6,14,0.583%
baseline,Ridge,3,2400,186,0,62.000,6,14,0.583%
pilot,Harbor,3,2400,198,3,65.000,15,13,0.542%
pilot,Ridge,3,2400,186,0,62.000,6,13,0.542%

PARTIAL-SHIFT CONTEXT (not a full-shift capacity test)
date,line,shipped,productive_hours,late_dispatches,late_rate
2026-07-31,Harbor,320,27,2,0.625%
2026-07-31,Ridge,320,26,1,0.312%

PROJECTION FOR HARBOR: 20 full shifts x 800 orders, 75% standard / 25% complex
standard DiD = (Harbor baseline 1.500% - Harbor pilot 0.667%) - (Ridge baseline 1.500% - Ridge pilot 1.500%) = 0.833 pp
complex DiD = (Harbor baseline 6.000% - Harbor pilot 3.000%) - (Ridge baseline 6.000% - Ridge pilot 5.500%) = 2.500 pp
Mix-weighted incremental reduction = 75%*0.833 pp + 25%*2.500 pp = 1.250 pp
Implied avoidable downstream mispacks = 16,000 * 0.01250 = 200.0
Expected gross avoided error cost = 200.0 * $48 = $9,600
Recurring labor baseline = 62.0 hours/shift; pilot = 65.0 hours/shift
Expected incremental labor cost = 20 * 3.0 hours * $32 = $1,920
Expected net cost reduction = $9,600 - $1,920 = $7,680
Labor-cost break-even incremental reduction = 0.250 pp
Capacity check = 65.0 recurring productive hours/shift <= 68.0-hour ceiling
One-off training = 3.0 observed hours on July 20; excluded from recurring projection
CAUTION: projection is an estimate, not a causal finding; Harbor volunteered and follow-up covers three mature pilot shifts.
```

10. `python3 deliverables/reproduce_decision.py > deliverables/calculation-output.txt`
    - Exit code: `0`
    - Stdout/stderr: none at the terminal; stdout was redirected to the named file.

11. `python3 deliverables/reproduce_decision.py | diff - deliverables/calculation-output.txt`
    - Exit code: `0`
    - Stdout/stderr: none. Exact match confirmed between a fresh script run and the saved calculation output.

12. `wc -l answer.md deliverables/reproduce_decision.py deliverables/calculation-output.txt`
    - Exit code: `0`
    - Exact stdout:

```text
   81 answer.md
  189 deliverables/reproduce_decision.py
   36 deliverables/calculation-output.txt
  306 total
```

## Checks performed

- The reproduction script ran successfully and validated presence of the two CSV files, required columns, numeric parseability, nonnegative numeric inputs, operations-to-cohort date/line coverage, and the existence of mature denominators.
- It aggregated cohort bands before assigning shipped volume to a line-level operations row, preventing labor duplication.
- It excluded July 31 from the full-shift capacity comparison while retaining its immediate dispatch observation.
- It removed the three one-off training hours from Harbor's recurring-hours projection and retained overtime within productive hours.
- A fresh script run exactly matched `deliverables/calculation-output.txt`.

## Unperformed checks and packet limitations

- No source-integrity hash comparison was performed; source files were read and only new output paths were patched or written.
- No external benchmark or substitute business assumption was used.
- No Ridge checked full shift or selective-check variant exists in the packet, so their capacity or savings were not projected.
- No exact calendar review date could be calculated because the next operating period's start date is not supplied; the answer uses a relative review point after shift 10 completes its seven-day maturity window.
- No production action, staffing change, spending commitment, external contact, browsing, or message sending was performed.
