# Execution note — C-U116

Working directory for every command: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U116`.

## Files used

- `prompt.md`
- `skill/operational-intervention-decision/SKILL.md`
- `input/request.md`
- `input/sources/measurement_notes.md`
- `input/sources/decision_context.md`
- `input/sources/shipment_cohorts.csv`
- `input/sources/shift_operations.csv`

The supplied Skill and inputs were read only. No external sources or sibling/shared-workspace materials were consulted.

## Public commands and results

1. `cat prompt.md` — exit code 0. Exact observation: the prompt directs use of the supplied Skill and request, requires `answer.md` via `apply_patch`, permits local deliverables, forbids external state changes, and requires this execution note.
2. `cat skill/operational-intervention-decision/SKILL.md` — exit code 0. Exact observation: the Skill requires mature denominators, mix standardization, native-grain labor aggregation, capacity and dispatch checks, conservative and favorable economics, a scoped choice, and a reproducible numerical basis.
3. `cat input/request.md` — exit code 0. Exact observation: the requested horizon is the next 20 full shifts and Nessa Vale retains the actual operating decision.
4. `rg --files input skill/operational-intervention-decision` — exit code 0. Exact stdout:

   ```text
   skill/operational-intervention-decision/SKILL.md
   input/request.md
   input/sources/shipment_cohorts.csv
   input/sources/shift_operations.csv
   input/sources/measurement_notes.md
   input/sources/decision_context.md
   ```

5. `cat input/sources/measurement_notes.md`, `cat input/sources/decision_context.md`, `cat input/sources/shipment_cohorts.csv`, and `cat input/sources/shift_operations.csv` — each exit code 0. Summary of captured observations: 28 cohort rows and 14 whole-line operation rows were supplied; August 28 quality was immature; August 3–5 and 17–19 were comparable full shifts; five August 17 training hours were one-off; catch recording changed August 14; the plan is 1,440 orders/line/shift at 70/30, a 102-hour cap, and a 1% dispatch limit.
6. `apply_patch` added `deliverables/analysis.py` — completed successfully with result `{}`. The script reads the unchanged CSVs, validates row keys and counts, calculates mature quality, standardized comparisons, labor capacity, dispatch, and economics, then writes `deliverables/numerical_basis.md`.
7. `python3 deliverables/analysis.py` — exit code 0. Exact stdout:

   ```text
   Integrity: duplicate_keys=0 missing_rows=0 impossible_counts=0
   Quality next-mix: baseline Alder=3.2000% Birch=2.6000%; pilot Alder=3.7000% Birch=2.5000%; DiD=+0.6000%
   Capacity: checked_Alder=108.0h/shift cap_gap=-6.0h feasible_volume=1360; no_check_Alder=98.4h headroom=3.6h
   Dispatch full-shift pilot: Alder=1.1667% (42/3600); Birch=0.5000% (18/3600)
   Economics conservative_20_shift_net=-25536.00; favorable_20_shift_net=4560.00; break_even_rate=0.4121%
   Wrote deliverables/numerical_basis.md
   ```

8. `cat deliverables/numerical_basis.md` — exit code 0. Summary of captured result: the generated file exposes band counts and rates, actual cohort mix, 70/30 standardization, native-grain hours, feasible volumes, dispatch counts, scenario formulas, and projection boundaries.
9. `python3 -m py_compile deliverables/analysis.py` — exit code 0, no stdout or stderr.
10. `apply_patch` added `answer.md` — completed successfully with result `{}`.
11. Final rerun of `python3 deliverables/analysis.py` — exit code 0. Exact stdout matched item 7, including `duplicate_keys=0`, `missing_rows=0`, `impossible_counts=0`, the four standardized rates, the capacity and dispatch figures, both economic scenario totals, and successful regeneration of `deliverables/numerical_basis.md`.
12. A Python standard-library assertion command read `answer.md` and `deliverables/numerical_basis.md`, checked six required memo markers plus the basis integrity marker, and exited 0. Exact stdout:

    ```text
    answer_lines=65 basis_lines=69 required_markers=6 missing=0
    ```

## Verification and limitations

The executable basis completed successfully and its printed control totals agree with the memo. Python bytecode compilation succeeded. The script checks duplicate keys, expected source-row coverage, mature/shipped relationships, mispack/mature relationships, and nonnegative late counts. No inferential significance test, confidence interval, or causal identification check was performed; the memo treats difference-in-differences only as a sensitivity. No future capacity curve, selective-check timing, or future outcome was directly tested because those data are absent. No live operational change, message, spending action, or external interaction was performed.
