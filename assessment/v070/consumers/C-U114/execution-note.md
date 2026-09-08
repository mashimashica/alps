# Execution note

## Scope and files used

Work was confined to `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U114` and the fixed prompt path supplied by the parent. No browsing, external actions, messages, live operational changes, spending, or source/Skill edits were performed.

Files read:

- `prompt.md`
- `skill/operational-intervention-decision/SKILL.md`
- `input/request.md`
- `input/sources/decision_context.md`
- `input/sources/measurement_notes.md`
- `input/sources/shipment_cohorts.csv`
- `input/sources/shift_operations.csv`

Files created:

- `deliverables/reproduce_analysis.py`
- `deliverables/analysis_results.txt`
- `answer.md`
- `execution-note.md`

## Actual commands and results

1. Command: `cat prompt.md`
   - Working directory: consumer root.
   - Exit code: 0.
   - Relevant stdout: instructed use of the supplied Skill and request, creation of `answer.md` via `apply_patch`, permitted work paths, and recording of actual commands/results in this note.
   - Stderr: none captured.

2. Commands issued as independent reads:
   - `cat skill/operational-intervention-decision/SKILL.md`
   - `cat input/request.md`
   - `rg --files input skill/operational-intervention-decision`
   - Exit code: 0 for each.
   - Relevant stdout: the Skill required mature-cohort handling, mix standardization, contemporaneous comparison, native-grain labor aggregation, capacity/service/economic evaluation, and a scoped next-period action. The file inventory returned exactly the request, the Skill, and four source files under `input/sources/`.
   - Stderr: none captured.

3. Commands issued as independent source reads:
   - `cat input/sources/decision_context.md`
   - `cat input/sources/measurement_notes.md`
   - `cat input/sources/shipment_cohorts.csv`
   - `cat input/sources/shift_operations.csv`
   - Exit code: 0 for each.
   - Relevant exact observations: 20 planned full shifts per line; 1,440 orders/shift; 70% standard/30% complex; 102 productive-hours/line/shift cap; 1% late-dispatch limit per line; USD 55/mispack and USD 34/additional productive hour; 28 shipment rows and 14 operations rows were visible in the CSV content; August 28 outcome cohorts had zero mature orders; August 28 operations were 600-order short shifts; five Alder training hours appeared on August 17 and are included in productive hours.
   - Stderr: none captured.

4. `apply_patch` created `deliverables/reproduce_analysis.py`.
   - Tool result: `{}` (successful application; subsequent execution confirmed the file was present and runnable).

5. Command: `python3 deliverables/reproduce_analysis.py`
   - Exit code: 0.
   - Relevant stdout (exact):

```text
INPUTS
shipments=/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U114/input/sources/shipment_cohorts.csv
operations=/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U114/input/sources/shift_operations.csv
shipment_rows=28 operations_rows=14
checks=PASS unique keys, matched coverage, count ranges, labor subset ranges

MATURE OUTCOMES (errors/mature, rate)
baseline Alder: standard=42/2100 (2.000%), complex=90/1500 (6.000%), raw=132/3600 (3.667%), 70/30 standardized=3.200%
baseline Birch: standard=42/2100 (2.000%), complex=60/1500 (4.000%), raw=102/3600 (2.833%), 70/30 standardized=2.600%
pilot Alder: standard=33/3300 (1.000%), complex=30/300 (10.000%), raw=63/3600 (1.750%), 70/30 standardized=3.700%
pilot Birch: standard=33/3300 (1.000%), complex=18/300 (6.000%), raw=51/3600 (1.417%), 70/30 standardized=2.500%
standardized changes: Alder=0.500%; Birch=-0.100%; difference-in-changes=0.600%

FULL-SHIFT OPERATIONS (one operations row counted once; training removed from recurring hours)
baseline Alder: recurring_hours=246.0, orders=3600, hours/order=0.068333, minutes/order=4.10, late=21/3600 (0.583%)
baseline Birch: recurring_hours=240.0, orders=3600, hours/order=0.066667, minutes/order=4.00, late=18/3600 (0.500%)
pilot Alder: recurring_hours=270.0, orders=3600, hours/order=0.075000, minutes/order=4.50, late=42/3600 (1.167%)
pilot Birch: recurring_hours=246.0, orders=3600, hours/order=0.068333, minutes/order=4.10, late=18/3600 (0.500%)

NEXT-PERIOD PLANNING SCENARIOS
orders/line=28800; mix=70% standard/30% complex; shifts=20
Alder checker constant-rate projection: hours/shift=108.0 vs cap=102.0; errors=1065.6; late/full-shift sample projection=336.0 vs 1% maximum=288.0
Alder no-check comparator-adjusted projection: hours/shift=100.8; errors=892.8; late using Alder baseline plus Birch contemporaneous change=168.0

CHECKER ECONOMICS VS NO-CHECK COUNTERFACTUALS
own baseline: no-check quality=3.200%; errors_avoided=-144.0; gross_avoidable_error_value=$-7,920; incremental_hours=192.0; incremental_labor_cost=$6,528; net_value=$-14,448
current Birch comparator: no-check quality=2.500%; errors_avoided=-345.6; gross_avoidable_error_value=$-19,008; incremental_hours=192.0; incremental_labor_cost=$6,528; net_value=$-25,536
comparator-adjusted: no-check quality=3.100%; errors_avoided=-172.8; gross_avoidable_error_value=$-9,504; incremental_hours=144.0; incremental_labor_cost=$4,896; net_value=$-14,400
comparator-adjusted labor break-even requires at least 89.0 avoided errors (0.309 percentage points); observed standardized change vs that counterfactual was -0.600 percentage points.
capacity threshold=4.25 minutes/order
```

   - Stderr: none captured.

6. Command: `python3 deliverables/reproduce_analysis.py > deliverables/analysis_results.txt && wc -l deliverables/analysis_results.txt && sha256sum deliverables/reproduce_analysis.py deliverables/analysis_results.txt`
   - Exit code: 0.
   - Stdout (exact):

```text
30 deliverables/analysis_results.txt
043ba6f938a18622e614335b2b7d34c40a7db0f8f44ba75c5dfc5ca0cf288c88  deliverables/reproduce_analysis.py
8631bce9db1c32ce9819914f07d1ac38b7d30639e5fec883b13a0c87f44f3791  deliverables/analysis_results.txt
```

   - Stderr: none captured.

7. `apply_patch` created `answer.md` and `execution-note.md`.

8. Command: `python3 deliverables/reproduce_analysis.py > work/recheck.txt && diff -u deliverables/analysis_results.txt work/recheck.txt && rg -n "Recommendation to Nessa|3\\.7%|108\\.0 h/shift|−\\$14,400|reproduce_analysis" answer.md && wc -l answer.md execution-note.md`
   - Exit code: 1.
   - Stdout: none.
   - Stderr (exact): `/bin/bash: line 1: work/recheck.txt: No such file or directory`
   - Result: the permitted temporary `work/` directory did not yet exist; no deliverable was changed.

9. Command: `mkdir -p work && python3 deliverables/reproduce_analysis.py > work/recheck.txt && diff -u deliverables/analysis_results.txt work/recheck.txt && rg -n 'Recommendation to Nessa|3\\.7%|108\\.0 h/shift|−\\$14,400|reproduce_analysis' answer.md && wc -l answer.md execution-note.md`
   - Exit code: 0.
   - Relevant stdout: `diff` produced no output, confirming the new run exactly matched `deliverables/analysis_results.txt`; `rg` found the recommendation and the cited 3.7%, 108.0 h/shift, −$14,400, and reproduction-command text in `answer.md`; pre-update line counts were 60 for `answer.md` and 122 for `execution-note.md`.
   - Stderr: none captured.

## Formulas and cohort rules

- Mature mispack rate = summed `confirmed_mispack_7d` / summed `mature_orders`; zero-mature August 28 cohorts excluded.
- Planned-mix rate = 0.70 × standard stratum rate + 0.30 × complex stratum rate.
- Difference in changes = (Alder pilot standardized − Alder baseline standardized) − (Birch pilot standardized − Birch baseline standardized).
- Recurring hours/order = (`productive_labor_hours` − one-off `training_hours`) / shipped orders, using only 1,200-order full shifts and counting each line/date row once.
- Next-period orders/line = 20 × 1,440 = 28,800.
- Comparator-adjusted no-check case = Alder baseline + Birch contemporaneous change, separately for quality, labor, and dispatch.
- Errors avoided = next-period orders × (no-check rate − checker rate).
- Gross avoidable-error value = errors avoided × USD 55.
- Incremental labor cost = next-period orders × (checker hours/order − no-check hours/order) × USD 34.
- Net checker value = gross avoidable-error value − incremental labor cost.

## Checks actually performed and limits

The script asserted unique shipment and operations keys, exact date/line coverage between tables, nonnegative counts, mature orders no greater than shipped orders, mispacks no greater than mature orders, and overtime/training no greater than productive hours. It reconciled every reported outcome and operations total directly from source rows.

No statistical significance test, causal identification, mix-specific labor estimate, selective-check estimate, or validated nonlinear capacity model was performed because the packet does not support them. The short pilot, 300-order mature complex stratum per line, voluntary allocation, baseline imbalance, shared template change, catch-recording change, and forecast mix shift remain material limitations. Projections are transparent planning scenarios, not guaranteed future results.
