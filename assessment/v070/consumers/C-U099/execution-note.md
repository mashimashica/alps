# Public execution note

All work was local. No external state was changed and no messages were sent.

## Commands and captured observations

1. Command:

   ```bash
   cat /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U099/prompt.md
   ```

   Exit code: `0`. Exact observation: the prompt directed use of the supplied skill and four source files, required `answer.md` via `apply_patch`, allowed local deliverables, prohibited modifying sources or external state, and required this execution note.

2. Commands run concurrently:

   ```bash
   cat skill/operational-intervention-decision/SKILL.md
   cat input/request.md && find input -maxdepth 2 -type f -print
   ```

   Exit codes: `0`, `0`. Exact observations: the skill requires maturity and grain validation, reviewable weighted arithmetic, forward workload and cost translation, a usable recommendation, uncertainties, boundaries, and a bounded follow-up when needed. The input inventory printed `request.md` and the four files under `input/sources/`.

3. Commands run concurrently:

   ```bash
   cat input/sources/measurement_notes.md
   cat input/sources/decision_context.md
   cat input/sources/shift_operations.csv
   cat input/sources/shipment_cohorts.csv
   ```

   Exit codes: all `0`; stderr was empty. Exact observations used in the answer include: July 31 is a 320-order immature short shift; all other listed dates are ordinary 800-order full shifts; operations rows are whole-line rows; training and overtime are subsets of productive hours; the next period is 20 shifts of 800 orders per line with a 75%/25% band mix; the hard limit is 68 productive hours per line; costs are $48 per downstream mispack and $32 per additional productive hour; and each line's late-dispatch commitment is at most 1%.

4. `apply_patch` created `deliverables/analyze.py`. No source or skill file was changed.

5. Command:

   ```bash
   python3 deliverables/analyze.py
   ```

   Exit code: `0`; stderr was empty. Captured stdout:

   ```text
   QUALITY — MATURE FULL SHIFTS
   period,line,mispack/mature,mispack_rate,catch/shipped,catch_rate
   baseline,Harbor,63/2400,2.625%,13/2400,0.542%
   baseline,Ridge,63/2400,2.625%,12/2400,0.500%
   pilot,Harbor,30/2400,1.250%,38/2400,1.583%
   pilot,Ridge,60/2400,2.500%,14/2400,0.583%

   QUALITY BY ORDER BAND — MATURE FULL SHIFTS
   period,line,band,mispack/mature,mispack_rate
   baseline,Harbor,complex,36/600,6.000%
   baseline,Harbor,standard,27/1800,1.500%
   baseline,Ridge,complex,36/600,6.000%
   baseline,Ridge,standard,27/1800,1.500%
   pilot,Harbor,complex,18/600,3.000%
   pilot,Harbor,standard,12/1800,0.667%
   pilot,Ridge,complex,33/600,5.500%
   pilot,Ridge,standard,27/1800,1.500%

   OPERATIONS — FULL SHIFTS
   period,line,shifts,hours,training,recurring_hours_per_shift,overtime_per_shift,late/shipped,late_rate
   baseline,Harbor,3,186,0,62.0,2.0,14/2400,0.583%
   baseline,Ridge,3,186,0,62.0,2.0,14/2400,0.583%
   pilot,Harbor,3,198,3,65.0,5.0,13/2400,0.542%
   pilot,Ridge,3,186,0,62.0,2.0,13/2400,0.542%

   FORWARD PLAN — PER CHECKED LINE, 20 FULL SHIFTS
   orders=16000 (standard=12000, complex=4000)
   difference_in_differences=-1.250 percentage points
   band effects: standard=-0.833 pp, complex=-2.500 pp
   estimated_avoided_mispacks=200 (standard=100, complex=100)
   estimated_avoidable_cost=9600 USD
   additional_recurring_hours=60; labor_cost=1920 USD
   estimated_net_before_one_off_training=7680 USD
   new_line_training=3 hours; at_given_rate=96 USD; separately funded
   estimated_net_after_new_line_training=7584 USD
   dispatch_at_Harbor_pilot_rate=86.7 late orders; commitment_limit=160
   ```

6. `apply_patch` wrote `answer.md` and this `execution-note.md`, then clarified the interim Ridge state while outcomes mature. The supplied skill and original inputs were preserved.

## Summary versus unperformed checks

The answer's forward totals are arithmetic extrapolations from the captured observations. No live operating change, external contact, spending action, randomized test, or seven-day follow-up was performed. Ridge's response to checking and persistence beyond the three mature Harbor pilot shifts remain unobserved.
