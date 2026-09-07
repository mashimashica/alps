# Public execution note

This note records public tool activity for C-U105. It contains captured
observations and reproducible summaries, not private reasoning.

## Commands and results

1. `cat /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U105/prompt.md`
   - Exit code: `0`
   - Captured result: task instructions required the supplied Skill, the files
     under `input/`, `answer.md` via `apply_patch`, a local execution note, and
     no external state change.

2. `cat skill/operational-intervention-decision/SKILL.md`
   - Exit code: `0`
   - Captured result: the Skill required maturity-aware outcome handling,
     planned-mix and concurrent-control calculations, separate labor/service
     analysis, explicit causal limits, and a bounded recommendation.

3. `cat input/request.md`
   - Exit code: `0`
   - Captured result: Iona Bell needs a continue/change/expand/stop
     recommendation for 20 full shifts, with inspectable local arithmetic and
     no external action.

4. `find input -maxdepth 2 -type f -print`
   - Exit code: `0`
   - Exact stdout listed:
     `input/sources/shift_operations.csv`,
     `input/sources/shipment_cohorts.csv`,
     `input/sources/measurement_notes.md`,
     `input/sources/decision_context.md`, and `input/request.md`.

5. The following source reads all exited `0` and their complete stdout was
   inspected:
   - `cat input/sources/measurement_notes.md`
   - `cat input/sources/decision_context.md`
   - `cat input/sources/shift_operations.csv`
   - `cat input/sources/shipment_cohorts.csv`
   - Captured observations used: July 6–8 and July 20–22 are ordinary full
     shifts; July 31 is a short shift and its downstream cohorts are immature;
     future mix is 75% standard / 25% complex at 800 orders per line per shift;
     the labor ceiling is 68 hours; the dispatch commitment is at most 1%; and
     the supplied costs are $48 per avoidable downstream mispack and $32 per
     additional productive hour.

6. `find skill/operational-intervention-decision -maxdepth 3 -type f -print`
   - Exit code: `0`
   - Exact stdout identified `SKILL.md` and
     `scripts/analyze_packet.py` only.

7. `python skill/operational-intervention-decision/scripts/analyze_packet.py --help`
   - Exit code: `0`
   - Captured result: confirmed the two-CSV packet interface and flags for
     planned mix, intervention/control lines, periods, ordinary dates, and
     Markdown output.

8. `mkdir -p deliverables work && python skill/operational-intervention-decision/scripts/analyze_packet.py input/sources --planned-mix standard=0.75,complex=0.25 --intervention-line Harbor --control-line Ridge --baseline-period baseline --trial-period pilot --ordinary-dates 2026-07-06,2026-07-07,2026-07-08,2026-07-20,2026-07-21,2026-07-22 --output deliverables/numerical-basis.md`
   - Exit code: `0`
   - Exact stdout: `wrote deliverables/numerical-basis.md`

9. `cat deliverables/numerical-basis.md`
   - Exit code: `0`
   - Exact captured key figures: Harbor planned-mix rate 2.625% baseline and
     1.250% pilot; Ridge 2.625% and 2.500%; change-in-changes -1.250 percentage
     points. Harbor recurring pilot labor excluding training was 65 hours per
     full shift and its full-shift pilot late rate was 0.542%.

10. `apply_patch` created `work/validate_packet.py`.
    - Tool result: completed without error.
    - The script checks column sets, duplicate keys, matched line/date rows,
      nonnegative integer counts, numerator/denominator relationships, and
      labor subset relationships. It then calculates separate outcomes,
      catches, labor, overtime, dispatch, short-shift observations, and the
      planning scenario.

11. `python work/validate_packet.py`
    - Exit code: `0`
    - Exact stdout:

```text
VALIDATION PASS: 28 cohort rows; 14 operation rows; no duplicate keys; all date/line pairs matched; count relationships valid
baseline Harbor: shipped=2400, mature=2400, errors=63 (2.625%), catches=13 (0.542%), productive_h=186, training_h=0, ongoing_h_per_shift=62.00, overtime_h_per_shift=2.00, late=14 (0.583%)
pilot Harbor: shipped=2400, mature=2400, errors=30 (1.250%), catches=38 (1.583%), productive_h=198, training_h=3, ongoing_h_per_shift=65.00, overtime_h_per_shift=5.00, late=13 (0.542%)
baseline Ridge: shipped=2400, mature=2400, errors=63 (2.625%), catches=12 (0.500%), productive_h=186, training_h=0, ongoing_h_per_shift=62.00, overtime_h_per_shift=2.00, late=14 (0.583%)
pilot Ridge: shipped=2400, mature=2400, errors=60 (2.500%), catches=14 (0.583%), productive_h=186, training_h=0, ongoing_h_per_shift=62.00, overtime_h_per_shift=2.00, late=13 (0.542%)
short_shift Harbor: shipped=320, late=2 (0.625%), mature=0
short_shift Ridge: shipped=320, late=1 (0.312%), mature=0
planning: orders=16000, descriptive_effect=1.250%, fewer_mispacks=200, quality_value=$9,600, extra_hours=60, labor_cost=$1,920, net=$7,680
break_even: $96 incremental labor/shift / $48 per mispack = 2 mispacks/shift = 0.250% rate reduction
```

12. `apply_patch` created `answer.md` and `deliverables/README.md`.
    - Tool result: completed without error.

13. Final verification commands:
    - `python -m py_compile work/validate_packet.py` — exit code `0`, no stdout.
    - `wc -l answer.md deliverables/numerical-basis.md deliverables/README.md`
      — exit code `0`; exact stdout: `135 answer.md`, `40
      deliverables/numerical-basis.md`, `27 deliverables/README.md`, `202
      total`.
    - `rg -n "1\.250|7,680|68 productive|seven-calendar-day|numerical-basis" answer.md`
      — exit code `0`; matched the decision's core effect, planning net,
      staffing ceiling, maturity language, and deliverable link.

## Files used

- Supplied Skill: `skill/operational-intervention-decision/SKILL.md`
- Supplied analyzer: `skill/operational-intervention-decision/scripts/analyze_packet.py`
- Supplied inputs: `input/request.md` and all four files in `input/sources/`
- Temporary local validation: `work/validate_packet.py`
- Outputs: `answer.md`, `deliverables/numerical-basis.md`, and
  `deliverables/README.md`

## Summaries and unperformed checks

The decision memo summarizes the captured calculations and labels the
control-adjusted effect as quasi-experimental. No web research, external
messages, live operational changes, spending, commits, uploads, or source/Skill
edits were performed. No dollar value was assigned to dispatch because the
packet supplies none. No causal identification or statistical significance
test was claimed; the packet's nonrandom assignment and three mature pilot
shifts limit that inference. No exact future maturity calendar date was
calculated because the future shift schedule is absent.
