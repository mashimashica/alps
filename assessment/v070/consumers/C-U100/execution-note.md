# Public execution note

## Files used

- `prompt.md`
- `skill/operational-intervention-decision/SKILL.md`
- `input/request.md`
- `input/sources/measurement_notes.md`
- `input/sources/decision_context.md`
- `input/sources/shift_operations.csv`
- `input/sources/shipment_cohorts.csv`

Created locally:

- `work/analyze.py`
- `answer.md`
- `execution-note.md`

No external state was changed, no messages were sent, and no live operation was altered.

## Commands and captured results

1. Command: `cat /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U100/prompt.md`
   - Exit code: `0`
   - Exact observation: the prompt directed use of the supplied Skill and request, required `answer.md` via `apply_patch`, authorized `work/` for local processing, prohibited changes to sources and external state, and required this execution note.
   - Stderr: none.

2. Commands run as independent reads:
   - `cat skill/operational-intervention-decision/SKILL.md`
   - `cat input/request.md`
   - `find input -maxdepth 2 -type f -print`
   - Exit code for each: `0`
   - Exact file-list stdout:

     ```text
     input/sources/shift_operations.csv
     input/sources/shipment_cohorts.csv
     input/sources/measurement_notes.md
     input/sources/decision_context.md
     input/request.md
     ```

   - Stderr: none.

3. Commands run as independent reads:
   - `cat input/sources/measurement_notes.md`
   - `cat input/sources/decision_context.md`
   - `cat input/sources/shift_operations.csv`
   - `cat input/sources/shipment_cohorts.csv`
   - Exit code for each: `0`
   - Exact captured observations used: August 28 cohorts have `mature_orders=0`; ordinary full shifts are August 3–5 and August 17–19; August 28 is a short 600-order shift; Alder’s August 17 training is five hours; overtime and training are subsets of productive hours; next-period workload is 1,440 orders per line per shift for 20 shifts at a 70% / 30% mix; the hard cap is 102 productive hours per line per shift; the late-dispatch commitment is 1%; costs are $55 per downstream mispack and $34 per additional productive hour.
   - Stderr: none.

4. File creation through `apply_patch`: `work/analyze.py`
   - Tool result: success (`{}`).

5. Command: `python3 work/analyze.py input/sources`
   - Exit code: `0`
   - First-run relevant stdout included: mix-adjusted Alder baseline `3.200%`, Alder pilot `3.700%`, Birch baseline `2.600%`, Birch pilot `2.500%`; Alder pilot routine labor `90.000 h/shift`; Alder pilot late dispatch `42/3600 = 1.167%`; all-order-check projection `108.0 h/shift`; baseline no-check projection `98.4 h/shift`; initial raw labor-gap planning value `$6,528`.
   - Stderr: none.

6. File update through `apply_patch`: `work/analyze.py` was extended to show a control-adjusted labor scenario and line-level dispatch projections.
   - Tool result: success (`{}`).

7. Command: `python3 work/analyze.py input/sources`
   - Exit code: `0`
   - Exact final relevant stdout:

     ```text
     QUALITY STANDARDIZED TO PLANNED 70% STANDARD / 30% COMPLEX MIX
     baseline,Alder: 3.200%
     baseline,Birch: 2.600%
     pilot,Alder: 3.700%
     pilot,Birch: 2.500%
     mix-adjusted change Alder: +0.500 percentage points
     mix-adjusted change Birch: -0.100 percentage points
     difference in changes (Alder minus Birch): +0.600 percentage points

     FULL-SHIFT OPERATIONS
     baseline,Alder: productive=246 h; training=0 h; routine=246 h; routine_avg=82.000 h/shift; late=21/3600 = 0.583%
     baseline,Birch: productive=240 h; training=0 h; routine=240 h; routine_avg=80.000 h/shift; late=18/3600 = 0.500%
     pilot,Alder: productive=275 h; training=5 h; routine=270 h; routine_avg=90.000 h/shift; late=42/3600 = 1.167%
     pilot,Birch: productive=246 h; training=0 h; routine=246 h; routine_avg=82.000 h/shift; late=18/3600 = 0.500%

     NEXT-PERIOD PLANNING SCENARIOS (constant observed rates; not causal proof)
     Alder all-order check labor: 0.075000 h/order x 1,440 = 108.0 h/shift; cap=102 h
     Alder baseline no-check labor: 0.068333 h/order x 1,440 = 98.4 h/shift
     Alder no-check plus Birch's common +2 h/1,200 period change: 100.8 h/shift
     Birch pilot no-check labor: 98.4 h/shift
     Alder all-order check late dispatch: 42/3600 x 28800 = 336; commitment maximum=288
     Alder baseline no-check late dispatch: 21/3600 x 28800 = 168
     Birch pilot no-check late dispatch: 18/3600 x 28800 = 144
     Difference-in-changes labor scenario for check: 7.2 h/shift
     Planning value of that incremental labor over 20 shifts: $4,896
     ```

   - Stderr: none.

8. File creation through `apply_patch`: `answer.md` and `execution-note.md`.
   - Tool result: success (`{}`).

9. Commands run as independent verification checks:
   - `python3 -m py_compile work/analyze.py`
   - `cat answer.md`
   - `cat execution-note.md`
   - Exit code for each: `0`
   - Exact stdout: the compile check produced no stdout; the two `cat` commands returned the complete corresponding Markdown files.
   - Stderr: none.

10. File update through `apply_patch`: softened the opening capacity statement in `answer.md` to identify it as a planning scenario, and finalized entries 8–10 in this execution note.
    - Tool result: the note itself is part of this operation; the applied patch returned success (`{}`).

## Summaries and unperformed checks

- Summary: all arithmetic in the answer comes from the two supplied CSVs under the definitions and constraints in the two supplied Markdown sources.
- Unperformed: no statistical significance test or confidence interval was required or run; no browser or external data source was used; no live feasibility test at 1,440 orders was performed.
