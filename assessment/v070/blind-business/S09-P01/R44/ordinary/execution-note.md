# Execution note — C-U117

All commands below were run with working directory:

`/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U117`

No command produced stderr unless stated. No external action or state change was performed.

## Reads and discovery

1. `cat prompt.md`
   - Exit code: 0
   - Captured observation: instructed use of the supplied operational-intervention-decision Skill, the request and its source files; required `answer.md`, `execution-note.md`, local-only work, and no changes to original inputs or Skill.

2. `cat skill/operational-intervention-decision/SKILL.md`
   - Exit code: 0
   - Captured observation: the Skill requires source-grain validation, mature outcome denominators, common-mix standardization, a comparison-adjusted planning contrast, native-grain labor, capacity and economics, a bounded decision, and early and mature reviews.

3. `cat input/request.md`
   - Exit code: 0
   - Captured observation: Iona Bell needs a recommendation for the next 20 full shifts; the four files in `input/sources/` are authoritative; local calculations and deliverables are authorized, but no live or external action is.

4. `find input -maxdepth 2 -type f -print`
   - Exit code: 0
   - Exact stdout:

     ```text
     input/sources/shift_operations.csv
     input/sources/shipment_cohorts.csv
     input/sources/measurement_notes.md
     input/sources/decision_context.md
     input/request.md
     ```

5. `cat input/sources/decision_context.md`
   - Exit code: 0
   - Captured observation: planned workload is 20 shifts × 800 orders/line at 75% standard / 25% complex; the hard line cap is 68 productive hours/shift; no staff borrowing or extra station exists; dispatch commitment is at most 1%; avoidable error cost is $48 and incremental productive labor is $32/hour. Harbor volunteered and treatment was not randomized.

6. `cat input/sources/measurement_notes.md`
   - Exit code: 0
   - Captured observation: cohort outcomes require a completed seven-day window; July 31 is immature and a short 320-order shift; operations are at whole-line/date grain; productive labor already includes overtime and training; Harbor's July 20 training was a one-off three hours.

7. `cat input/sources/shift_operations.csv`
   - Exit code: 0
   - Relevant exact observations: 14 line/date rows; the six ordinary full-shift dates were July 6–8 and July 20–22; July 31 was also present for each line.

8. `cat input/sources/shipment_cohorts.csv`
   - Exit code: 0
   - Relevant exact observations: 28 date/line/band rows; the July 31 rows have 0 mature orders; every comparable full line-shift contains 600 standard and 200 complex orders.

## Mutations and calculations

9. `mkdir -p deliverables work`
   - Exit code: 0
   - Stdout: empty.

10. `apply_patch` created `deliverables/reproduce.py`.
    - Tool result: success.
    - The script reads only the two supplied CSVs and writes `deliverables/calculation_results.json`.

11. `python3 deliverables/reproduce.py`
    - Exit code: 0
    - Stderr: empty.
    - Relevant stdout: JSON reported `adjusted_reduction: 0.0125`, `forecast_recurring_hours: 1300.0`, `available_hours_at_cap: 1360`, `expected_avoided_errors_adjusted: 200.0`, `net_avoided_cost_usd: 7680.0`, 28 unique cohort keys, 14 unique operation keys, and the two July 31 line-shifts as short shifts.

12. `apply_patch` updated `deliverables/reproduce.py` to expose minimum and maximum recurring hours per shift.
    - Tool result: success.

13. `python3 deliverables/reproduce.py > work/reproduce.stdout`
    - Exit code: 0
    - Stdout/stderr: empty at the console; complete stdout was redirected to `work/reproduce.stdout`.

14. The following public Python check was run:

    ```bash
    python3 - <<'PY'
    import json
    from pathlib import Path
    p=Path('deliverables/calculation_results.json')
    d=json.loads(p.read_text())
    for k in ('Harbor_baseline','Harbor_pilot','Ridge_baseline','Ridge_pilot'):
        x=d['operations_full_shifts'][k]
        print(k, x['avg_recurring_hours_per_shift'], x['min_recurring_hours_per_shift'], x['max_recurring_hours_per_shift'], x['late_dispatch_rate'])
    print('adjusted_reduction', d['comparison']['adjusted_reduction'])
    print('net', d['harbor_20_shift_planning_scenario']['net_avoided_cost_usd'])
    PY
    ```

    - Exit code: 0
    - Exact stdout:

      ```text
      Harbor_baseline 62.0 61 63 0.005833333333333334
      Harbor_pilot 65.0 65 65 0.005416666666666667
      Ridge_baseline 62.0 61 63 0.005833333333333334
      Ridge_pilot 62.0 62 62 0.005416666666666667
      adjusted_reduction 0.0125
      net 7680.0
      ```

15. `apply_patch` created `answer.md`.
    - Tool result: success.

## Final rerun and checks

16. `python3 deliverables/reproduce.py > work/final-reproduce.stdout`
    - Exit code: 0
    - Stdout/stderr: empty at the console; complete final stdout was redirected to `work/final-reproduce.stdout` and matches the generated JSON.

17. The following public Python assertion command loaded `deliverables/calculation_results.json` and checked the decision-critical outputs and file existence:

    ```bash
    python3 - <<'PY'
    import json
    from pathlib import Path
    r=json.loads(Path('deliverables/calculation_results.json').read_text())
    assert r['comparison']['adjusted_reduction'] == 0.0125
    p=r['harbor_20_shift_planning_scenario']
    assert p['forecast_recurring_hours'] == 1300
    assert p['available_hours_at_cap'] == 1360
    assert p['expected_avoided_errors_adjusted'] == 200
    assert p['net_avoided_cost_usd'] == 7680
    assert r['operations_full_shifts']['Harbor_pilot']['max_recurring_hours_per_shift'] == 65
    assert Path('deliverables/reproduce.py').exists()
    assert Path('answer.md').exists()
    print('final assertions: PASS')
    print('adjusted_reduction=0.0125; forecast_hours=1300; cap_hours=1360; avoided_errors=200; net_usd=7680; max_recurring_hours=65')
    PY
    ```

    - Exit code: 0
    - Exact stdout:

      ```text
      final assertions: PASS
      adjusted_reduction=0.0125; forecast_hours=1300; cap_hours=1360; avoided_errors=200; net_usd=7680; max_recurring_hours=65
      ```

18. `sha256sum input/sources/shift_operations.csv input/sources/shipment_cohorts.csv input/sources/measurement_notes.md input/sources/decision_context.md deliverables/reproduce.py deliverables/calculation_results.json answer.md`
    - Exit code: 0
    - Exact stdout:

      ```text
      821cefcd24d45b7acebc6a30d1b9f3ab6f2f2cbb300a66aee359ef7cd2779c85  input/sources/shift_operations.csv
      280644532300832a9b74e2b3bc8daf7318f42124bf74f50f630dd22c15ea25b0  input/sources/shipment_cohorts.csv
      4f89f6c363b70e69e5acdabde1ba46f3ca96c4a65530ac524a47786830f4a91e  input/sources/measurement_notes.md
      db617bd327c581d41163649f373944101be1394c760359d77760b395ba42d267  input/sources/decision_context.md
      4b06749938113c15aa1f898bbd9adc5199d400dab60979f8e66403e8c0124425  deliverables/reproduce.py
      3113777432c6cb80e626d684673da709ee3da412ae68f19a24c3659c8be4b7a1  deliverables/calculation_results.json
      91b449737a4f1de948d712a9c5deb08b594a8ce86cdab36019fceb1f58b293ad  answer.md
      ```

## Files used and produced

- Read: `prompt.md`, `skill/operational-intervention-decision/SKILL.md`, `input/request.md`, and the four authoritative files in `input/sources/`.
- Produced: `answer.md`, `deliverables/reproduce.py`, `deliverables/calculation_results.json`, `work/reproduce.stdout`, `work/final-reproduce.stdout`, and this note.
- Unperformed checks: no statistical significance test was performed because the Skill directs against unsupported significance claims and the packet contains only three mature full shifts per period and line. No external business assumptions or web sources were used. No live operational action, message, spending, install, commit, upload, or source/Skill edit was performed.
