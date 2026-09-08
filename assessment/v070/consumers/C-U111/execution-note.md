# Execution note

## Files used

- `prompt.md`
- `skill/operational-intervention-decision/SKILL.md`
- `skill/operational-intervention-decision/references/decision-method.md`
- `skill/operational-intervention-decision/scripts/analyze_packet.py`
- `input/request.md`
- `input/sources/measurement_notes.md`
- `input/sources/decision_context.md`
- `input/sources/shift_operations.csv`
- `input/sources/shipment_cohorts.csv`

The supplied Skill and input files were read only and were not modified.

## Public commands and results

All commands ran from `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U111`.

1. `cat prompt.md`
   - Exit code: 0.
   - Exact relevant observation: the prompt required use of the supplied Skill and request, creation of `answer.md` with `apply_patch`, preservation of inputs, no external actions, and an execution note.

2. `cat skill/operational-intervention-decision/SKILL.md`
   - Exit code: 0.
   - Exact relevant observation: the Skill required mature, mix-standardized outcome analysis; descriptive comparisons; labor, dispatch, capacity, cost, sensitivity, recommendation, follow-up gates, and a reproduction command.

3. `cat input/request.md`
   - Exit code: 0.
   - Exact relevant observation: the user requested a next-20-full-shift recommendation for Iona Bell, based only on the four source files, with an inspectable numerical basis and no live action.

4. `find input -maxdepth 2 -type f -print`
   - Exit code: 0.
   - Exact stdout:

```text
input/sources/shift_operations.csv
input/sources/shipment_cohorts.csv
input/sources/measurement_notes.md
input/sources/decision_context.md
input/request.md
```

5. `cat skill/operational-intervention-decision/references/decision-method.md`
   - Exit code: 0.
   - Exact relevant observation: the reference defined the rate, standardization, contemporaneous, difference-in-differences, approximate variance, proportional labor, dispatch, and economic calculations used.

6. `python3 skill/operational-intervention-decision/scripts/analyze_packet.py --help`
   - Exit code: 0.
   - Exact relevant stdout: usage listed required cohort and operations files, intervention/comparison lines, planned mix, ordinary dates, planned shifts, orders per shift, and optional labor cap, error cost, hour cost, and output path.

7. `cat input/sources/measurement_notes.md`, `cat input/sources/decision_context.md`, `cat input/sources/shift_operations.csv`, and `cat input/sources/shipment_cohorts.csv`
   - Exit codes: 0 for all four commands.
   - Exact captured observations used: July 31 outcomes were immature; the six July 6–8 and July 20–22 dates were ordinary full shifts; operations rows were whole-line rows; training was included in productive labor; Harbor's July 20 three training hours were one-off; the next-period plan was 20 × 800 orders per line at a 75% / 25% mix; the labor cap was 68 hours; authorized costs were $48 per mispack and $32 per added productive hour; the late-dispatch commitment was at most 1%; and assignment was non-random.

8. `mkdir -p deliverables work`
   - Exit code: 0.
   - Stdout/stderr: empty.

9. First analyzer attempt:

```bash
python3 skill/operational-intervention-decision/scripts/analyze_packet.py --cohorts input/sources/shipment_cohorts.csv --operations input/sources/shift_operations.csv --intervention-line Harbor --comparison-line Ridge --baseline-period baseline --intervention-period pilot --planned-mix standard=0.75,complex=0.25 --ordinary-dates 2026-07-20,2026-07-21,2026-07-22 --planned-shifts 20 --orders-per-shift 800 --labor-cap-hours 68 --error-cost 48 --hour-cost 32 --output deliverables/numerical_basis.json
```

   - Exit code: 1.
   - Exact relevant stderr: `ValueError: no ordinary operation rows for baseline/Harbor`.
   - Result: no usable output was produced. The rerun included all six dates that the notes explicitly identify as ordinary full shifts.

10. Successful analyzer invocation:

```bash
python3 skill/operational-intervention-decision/scripts/analyze_packet.py --cohorts input/sources/shipment_cohorts.csv --operations input/sources/shift_operations.csv --intervention-line Harbor --comparison-line Ridge --baseline-period baseline --intervention-period pilot --planned-mix standard=0.75,complex=0.25 --ordinary-dates 2026-07-06,2026-07-07,2026-07-08,2026-07-20,2026-07-21,2026-07-22 --planned-shifts 20 --orders-per-shift 800 --labor-cap-hours 68 --error-cost 48 --hour-cost 32 --output deliverables/numerical_basis.json
```

   - Exit code: 0.
   - Exact stdout: `wrote deliverables/numerical_basis.json`.
   - Output file: `deliverables/numerical_basis.json`.

11. `cat deliverables/numerical_basis.json`
   - Exit code: 0.
   - Exact captured observations used in the answer: Harbor pilot 30 / 2,400 at 1.25%; Ridge pilot 60 / 2,400 at 2.50%; both baselines 63 / 2,400 at 2.625%; contemporaneous and difference-in-differences benefits 0.0125; Harbor pilot recurring labor 65 hours; Harbor pilot late dispatch 13 / 2,400; 60 added hours and $1,920 labor cost over the plan; 200 avoided-outcome and $9,600 quality-value point estimates; and 640 open-window shipped orders excluded.

12. `python3 work/build_sensitivity.py`
   - Exit code: 0.
   - Exact stdout: `wrote deliverables/economic_sensitivity.csv`.
   - Output file: `deliverables/economic_sensitivity.csv`.

13. `cat deliverables/economic_sensitivity.csv`
   - Exit code: 0.
   - Exact captured observations used: at 3 added hours per shift, net values were −$1,366.26 at the lower difference-in-differences bound, +$1,824.49 at the lower contemporaneous bound, and +$7,680 at the point estimate; at 6 added hours they were −$3,286.26, −$95.51, and +$5,760 respectively.

14. Station-catch aggregation command:

```bash
python3 - <<'PY'
import csv
with open('input/sources/shipment_cohorts.csv', newline='') as f:
    rows = list(csv.DictReader(f))
for period in ('baseline','pilot'):
    for line in ('Harbor','Ridge'):
        selected = [r for r in rows if r['period']==period and r['line']==line and r['shipment_date']!='2026-07-31']
        print(period, line, 'station_catches', sum(int(r['station_catches']) for r in selected), 'shipped', sum(int(r['shipped_orders']) for r in selected))
PY
```

   - Exit code: 0.
   - Exact stdout:

```text
baseline Harbor station_catches 13 shipped 2400
baseline Ridge station_catches 12 shipped 2400
pilot Harbor station_catches 38 shipped 2400
pilot Ridge station_catches 14 shipped 2400
```

15. `apply_patch` created `work/build_sensitivity.py`, `answer.md`, and this `execution-note.md`. No shell exit code applies to `apply_patch`; the tool reported success.

16. `python3 -m py_compile work/build_sensitivity.py`
   - Exit code: 0.
   - Stdout/stderr: empty.

17. A local Python validation loaded `answer.md`, `execution-note.md`, `deliverables/numerical_basis.json`, and `deliverables/economic_sensitivity.csv` and checked the recommendation text, reproduction command, JSON effect, and CSV row count.
   - Exit code: 0.
   - Exact stdout: `{'answer_has_recommendation': True, 'answer_has_reproduction': True, 'execution_note_present': True, 'basis_effect': 0.0125, 'sensitivity_rows': 6}`.

18. `wc -l answer.md execution-note.md deliverables/numerical_basis.json deliverables/economic_sensitivity.csv work/build_sensitivity.py`
   - Exit code: 0.
   - Exact stdout at the time of the check:

```text
   95 answer.md
  124 execution-note.md
  295 deliverables/numerical_basis.json
    7 deliverables/economic_sensitivity.csv
   53 work/build_sensitivity.py
  574 total
```

## Summaries and unperformed checks

- Summary judgment: the arithmetic supports continuing Harbor's all-order check within explicit operating gates, while the non-random design prevents a causal claim and the packet does not establish a Ridge rollout or selective scope.
- No web research, live operating change, message, spending action, external write, commit, push, upload, or installation was performed.
- No calendar date was inferred for the shift-10 maturity review because future shift dates were not provided; the exact maturity rule is seven calendar days after shift 10's shipment date.
