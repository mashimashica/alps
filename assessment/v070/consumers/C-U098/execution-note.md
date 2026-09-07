# Public execution note

All operations were local and read-only with respect to the supplied Skill and inputs. No external state was changed and no messages were sent.

## Files used

- `prompt.md`
- `skill/operational-intervention-decision/SKILL.md`
- `input/request.md`
- `input/sources/decision_context.md`
- `input/sources/measurement_notes.md`
- `input/sources/shipment_cohorts.csv`
- `input/sources/shift_operations.csv`

Created:

- `work/reproduce.py`
- `answer.md`
- `execution-note.md`

## Actual commands and observations

1. Command: `cat /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U098/prompt.md`
   - Exit code: `0`
   - Exact observation: stdout was the assigned assessment prompt. It directed use of the supplied Skill and inputs, creation of `answer.md` with `apply_patch`, and this execution note.

2. Commands, executed concurrently from the assigned task directory:
   - `cat skill/operational-intervention-decision/SKILL.md` — exit code `0`
   - `cat input/request.md` — exit code `0`
   - `rg --files input` — exit code `0`
   - Exact `rg` stdout:

     ```text
     input/request.md
     input/sources/decision_context.md
     input/sources/measurement_notes.md
     input/sources/shipment_cohorts.csv
     input/sources/shift_operations.csv
     ```

3. Commands, executed concurrently from the assigned task directory:
   - `cat input/sources/decision_context.md` — exit code `0`
   - `cat input/sources/measurement_notes.md` — exit code `0`
   - `cat input/sources/shipment_cohorts.csv` — exit code `0`
   - `cat input/sources/shift_operations.csv` — exit code `0`
   - Exact captured observations used: all four files were read in full. They establish the planning volume and mix, 102-hour cap, 1% dispatch promise, $55/$34 cost assumptions, maturity rule, recording change, cohort values, and line-level operations values. This sentence is a summary of the exact stdout rather than a verbatim copy.

4. `apply_patch` created `work/reproduce.py`. Tool result: `{}` (success).

5. Command: `python3 work/reproduce.py`
   - Exit code: `0`
   - Stderr: empty
   - Exact relevant stdout:

     ```text
     MATURE OUTCOMES BY PERIOD / LINE / BAND
     period,line,band,shipped,mature,mispack,mispack_rate
     baseline,Alder,complex,1500,1500,90,6.0000%
     baseline,Alder,standard,2100,2100,42,2.0000%
     baseline,Birch,complex,1500,1500,60,4.0000%
     baseline,Birch,standard,2100,2100,42,2.0000%
     pilot,Alder,complex,330,300,30,10.0000%
     pilot,Alder,standard,3870,3300,33,1.0000%
     pilot,Birch,complex,330,300,18,6.0000%
     pilot,Birch,standard,3870,3300,33,1.0000%

     FULL-SHIFT OPERATIONS (LINE-LEVEL ROWS COUNTED ONCE)
     period,line,orders,productive_hours,training_hours,ongoing_hours,late,late_rate
     baseline,Alder,3600,246,0,246,21,0.5833%
     baseline,Birch,3600,240,0,240,18,0.5000%
     pilot,Alder,3600,275,5,270,42,1.1667%
     pilot,Birch,3600,246,0,246,18,0.5000%

     TWENTY-SHIFT PLANNING SCENARIOS (NOT CAUSAL FORECASTS)
     planned_orders=28800; standard=20160; complex=8640
     no_check_mispacks_from_alder_baseline_band_rates=921.6
     checked_mispacks_from_alder_pilot_band_rates=1065.6
     no_check_error_cost_at_55=50688.00
     checked_error_cost_at_55=58608.00
     no_check_hours_constant_hours_per_order=1968.0
     checked_hours_constant_hours_per_order=2160.0
     twenty_shift_hours_cap=2040
     checked_hours_over_cap=120.0
     additional_checked_hours_vs_baseline=192.0
     additional_hour_cost_at_34=6528.00
     checked_full_shift_late_projection_at_observed_rate=336.0
     late_dispatch_limit_at_1_percent=288.0

     IMMATURE COHORTS
     rows=4; shipped=1200; mature=0
     Their zero confirmed outcomes are unavailable outcomes and are excluded above.
     ```

6. `apply_patch` created `answer.md`. Tool result: `{}` (success).

7. `apply_patch` created this `execution-note.md`. Tool result: `{}` (success).

8. Final checks, executed concurrently from the assigned task directory:
   - `python3 -m py_compile work/reproduce.py` — exit code `0`; stdout and stderr empty.
   - `test -s answer.md && test -s execution-note.md && test -s work/reproduce.py` — exit code `0`; stdout and stderr empty.
   - `rg -n "Recommendation:|102-hour|1\\.17%|planning scenarios|Follow-up and review point|python3 work/reproduce.py" answer.md` — exit code `0`.
   - Exact relevant stdout from the content check:

     ```text
     3:**Recommendation: stop Alder's all-order second-person check for the next 20 full shifts, and do not expand it to Birch.** Run both lines without a dedicated checker. This is an interim operating decision for the stated horizon; Nessa retains the actual decision.
     5:The quality records do not show that the measured check improves downstream mispacks, and its observed workload does not fit the hard 102-hour-per-line-per-shift cap at the planned volume. Narrowing to selective checking is not an implementable substitute because its time, quality, and dispatch effects have not been measured.
     26:Alder's late-dispatch rate on the three comparable full pilot shifts was **42 / 3,600 = 1.17%**, above the 1% commitment. At a constant rate, the next period would have 336 late orders against a maximum of 288. Including the unusually short, simple August 28 shift makes the full pilot record 42 / 4,200 = 1.00%, but that shift is not evidence of full-shift capacity. Alder's baseline full-shift rate was 21 / 3,600 = 0.58%.
     28:The following quality figures are **planning scenarios, not causal forecasts**. Applying Alder's own baseline band rates to 28,800 planned orders at the stated 70% standard / 30% complex mix yields 921.6 expected mispacks and **$50,688** in avoidable error cost at $55 each. Applying Alder's checked-pilot band rates yields 1,065.6 mispacks and **$58,608**. The latter is $7,920 higher before the $6,528 additional-hour cost. The periods differ in template, account mix, and allocation, so this comparison supports no claim that checking causes harm; it does show that the supplied evidence cannot justify paying for or operationally accommodating the check.
     30:## Follow-up and review point
     41:python3 work/reproduce.py
     44:The script uses only the supplied CSV files, aggregates outcomes by period, line, and band, counts each line-level operations row once, excludes immature outcomes, and prints the stated planning scenarios.
     ```

## Interpretation boundary

The recommendation and cost/workload figures in `answer.md` distinguish observed measurements from planning scenarios. No causal effect was estimated. Selective checking was not modeled as observed because the source packet says its time, quality, and dispatch effects are unmeasured.
