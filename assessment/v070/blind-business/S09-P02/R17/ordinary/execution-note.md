# Public execution note — C-U101

## Files used

- `prompt.md`
- `skill/operational-intervention-decision/SKILL.md`
- `input/request.md`
- `input/sources/decision_context.md`
- `input/sources/measurement_notes.md`
- `input/sources/shift_operations.csv`
- `input/sources/shipment_cohorts.csv`

Created:

- `answer.md`
- `deliverables/reproduce_decision.py`
- `deliverables/derived_metrics.csv`
- `execution-note.md`

## Command and tool record

All shell commands ran with working directory `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U101` except the first, which ran from `/workspace/scratch/a75c3a6d9076`.

1. `cat /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U101/prompt.md`
   - Exit code: `0`
   - Exact relevant observation: the prompt required applying the supplied Skill, preserving sources and Skill, writing `answer.md` with `apply_patch`, using only the assigned scope, and recording this execution note.

2. The following three read-only commands were issued concurrently:
   - `cat skill/operational-intervention-decision/SKILL.md` — exit code `0`.
   - `cat input/request.md` — exit code `0`.
   - `find input -maxdepth 1 -type f -print | sort` — exit code `0`; exact stdout: `input/request.md`.
   - Captured observation (summary): the Skill required a decision among continue, narrow, expand, and stop, reviewable arithmetic, correct data grains, capacity and dispatch checks, explicit evidence limits, and a bounded follow-up when needed. The request identified four authoritative source files in `sources/` and prohibited external operational action.

3. `find sources -maxdepth 2 -type f -print | sort`
   - Exit code: `1`
   - Exact stderr: `find: ‘sources’: No such file or directory`
   - This established that `sources/` was not at the trial root; no files outside the assigned scope were searched.

4. `find input -maxdepth 3 -type f -print | sort`
   - Exit code: `0`
   - Exact stdout:

     ```text
     input/request.md
     input/sources/decision_context.md
     input/sources/measurement_notes.md
     input/sources/shift_operations.csv
     input/sources/shipment_cohorts.csv
     ```

5. The four commands below were issued concurrently and each exited `0`:
   - `cat input/sources/decision_context.md`
   - `cat input/sources/measurement_notes.md`
   - `cat input/sources/shift_operations.csv`
   - `cat input/sources/shipment_cohorts.csv`
   - Captured observations (summary): there were 14 line-date operations rows and 28 mutually exclusive shipment cohort rows; July 31 was short and immature for quality; the other six dates were ordinary full shifts, with three baseline and three pilot dates. The context supplied the 20-shift, 800-order, 75/25 plan, 68-hour cap, three-hour Ridge training allowance, $48 error cost, $32 hourly cost, and 1% line-level dispatch commitment.

6. `apply_patch` added `deliverables/reproduce_decision.py`.
   - This was a file-edit tool operation and did not expose a shell exit code. The tool returned success with no stderr.

7. `python3 deliverables/reproduce_decision.py`
   - Exit code: `0`
   - Exact stdout:

     ```text
     unit_quality=mature order; shipment_key=shipment_date+line+order_band
     unit_operations=line-date; join_key=shipment_date+line
     cohort_rows=28; operations_rows=14; key_reconciliation=passed
     Harbor baseline: 63/2400 = 2.6250%
     Harbor pilot: 30/2400 = 1.2500%
     Ridge baseline: 63/2400 = 2.6250%
     Ridge pilot: 60/2400 = 2.5000%
     difference_in_differences=-1.2500%
     planned_mix_adjusted_change=-1.2500%
     adjusted_avoided_mispacks_per_line=200
     avoidable_quality_cost_per_line=$9,600
     recurring_added_hours_per_line=60; cost=$1,920
     Harbor planning net=$7,680
     Ridge planning net after 3 training hours=$7,584
     wrote=deliverables/derived_metrics.csv
     ```
   - No stderr was emitted.

8. `cat deliverables/derived_metrics.csv`
   - Exit code: `0`
   - Exact relevant observations: the file contained 52 metric rows plus its header, including Harbor and Ridge counts and rates by period, band rates, the `-0.01250000` adjusted change, 200 avoided events per line, $9,600 avoidable quality cost, 60 added hours, $1,920 recurring labor cost, $96 Ridge training cost, the 68-hour cap, and full-shift dispatch and overtime metrics.

9. `apply_patch` added `answer.md`.
   - This was a file-edit tool operation and did not expose a shell exit code. The tool returned success with no stderr.

10. Two validation commands were issued concurrently:
    - `python3 -c 'from pathlib import Path; compile(Path("deliverables/reproduce_decision.py").read_text(), "deliverables/reproduce_decision.py", "exec"); print("syntax_ok")'`
      - Exit code: `0`; exact stdout: `syntax_ok`; no stderr.
    - `python3 -c 'from pathlib import Path; p=Path("answer.md"); s=p.read_text(); assert "controlled expansion" in s.lower(); assert "2.2375%" in s; assert "python3 deliverables/reproduce_decision.py" in s; print(f"answer_ok lines={len(s.splitlines())}")'`
      - Exit code: `0`; exact stdout: `answer_ok lines=79`; no stderr.

11. `apply_patch` added this `execution-note.md`.
    - This was a file-edit tool operation and did not expose a shell exit code. The tool returned success with no stderr.

12. A first inline-Python artifact-count command was attempted with an incorrectly escaped path inside an f-string.
    - Exit code: `1`.
    - Exact stderr began `SyntaxError: unexpected character after line continuation character` and pointed to the backslash-escaped `execution-note.md` expression.
    - It did not modify any file.

13. `python3 -c 'import csv; from pathlib import Path; rows=list(csv.DictReader(Path("deliverables/derived_metrics.csv").open())); print("derived_metrics_rows=%d" % len(rows)); print("execution_note_exists=%s" % Path("execution-note.md").is_file())'`
    - Exit code: `0`.
    - Exact stdout:

      ```text
      derived_metrics_rows=52
      execution_note_exists=True
      ```
    - No stderr was emitted.

14. `apply_patch` corrected the metric-row count in this note and added steps 12–14.
    - This was a file-edit tool operation and did not expose a shell exit code. The tool returned success with no stderr.

## Evidence limits and unperformed checks

- No web research, external messaging, live operational change, spending commitment, repository action, or state mutation was performed.
- No randomized or statistical significance test was performed. The difference-in-differences is used as a descriptive adjustment, not proof of causation.
- Ridge quality, labor, savings, and dispatch under checking remain planning scenarios until the bounded Ridge evidence stage is run. No selective checking variant was modeled as measured behavior.
- The local script validates source grains and key reconciliation, but it does not alter or replace any supplied source.
