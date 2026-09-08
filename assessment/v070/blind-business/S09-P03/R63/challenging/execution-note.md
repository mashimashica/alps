# Public execution note — C-U106

## Files used

- `prompt.md`
- `skill/operational-intervention-decision/SKILL.md`
- `skill/operational-intervention-decision/scripts/analyze_packet.py`
- `input/request.md`
- `input/sources/decision_context.md`
- `input/sources/measurement_notes.md`
- `input/sources/shipment_cohorts.csv`
- `input/sources/shift_operations.csv`

No other trial, creator prompt, evaluation, audit, parent plan, or worktree was read. No web source was used.

## Commands and captured results

All commands ran with working directory `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U106` unless an absolute path is shown. Stderr was empty for every successful command below.

1. `cat /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U106/prompt.md`
   - Exit code: 0.
   - Relevant stdout: instructed use of the supplied skill and request, creation of `answer.md` with `apply_patch`, temporary work under `work/`, and a public `execution-note.md`.

2. `cat skill/operational-intervention-decision/SKILL.md`
   - Exit code: 0.
   - Relevant stdout: required validation, mature-cohort treatment, planned-mix adjustment, concurrent-control comparison, separate labor/service reporting, scenario labeling, and an actionable recommendation.

3. `cat input/request.md`
   - Exit code: 0.
   - Relevant stdout: requested a scoped next-20-shift decision and inspectable local reproduction based only on the synthetic sources.

4. `rg --files input`
   - Exit code: 0.
   - Stdout listed `input/request.md` and the four source files named above.

5. `cat input/sources/decision_context.md`
   - Exit code: 0.
   - Relevant stdout: 1,440 orders per line per shift for 20 shifts; 70%/30% planned mix; 102 productive-hour hard cap; 1% late-dispatch commitment; $55 per mispack and $34 per incremental productive hour; nonrandom allocation and concurrent changes; only all-order checking measured.

6. `cat input/sources/measurement_notes.md`
   - Exit code: 0.
   - Relevant stdout: seven-day maturity rule; August 28 immature; station-catch recording changed; line labor must be counted once; five Alder training hours on August 17 are one-off; August 3–5 and 17–19 are ordinary full shifts.

7. `cat input/sources/shipment_cohorts.csv`
   - Exit code: 0.
   - Relevant stdout: 28 data rows covering the two periods, lines, and bands.

8. `cat input/sources/shift_operations.csv`
   - Exit code: 0.
   - Relevant stdout: 14 line-date operation rows.

9. `rg --files skill/operational-intervention-decision`
   - Exit code: 0.
   - Stdout: `SKILL.md` and `scripts/analyze_packet.py`.

10. `python skill/operational-intervention-decision/scripts/analyze_packet.py --help`
    - Exit code: 0.
    - Relevant stdout: confirmed the two-CSV packet interface and required mix, intervention line, control line, and output arguments.

11. `mkdir -p work deliverables && python skill/operational-intervention-decision/scripts/analyze_packet.py input/sources --planned-mix standard=0.7,complex=0.3 --intervention-line Alder --control-line Birch --baseline-period baseline --trial-period pilot --ordinary-dates 2026-08-03,2026-08-04,2026-08-05,2026-08-17,2026-08-18,2026-08-19 --output work/measurement_basis.md`
    - Exit code: 0.
    - Stdout: `wrote work/measurement_basis.md`.

12. `cat work/measurement_basis.md`
    - Exit code: 0.
    - Exact relevant observations: adjusted rates were Alder 3.2% baseline and 3.7% pilot, Birch 2.6% baseline and 2.5% pilot; change-in-changes was +0.6 percentage points; Alder pilot ordinary shifts averaged 91.67 productive hours or 90.00 ongoing hours after training and 1.167% late dispatch; Birch pilot averaged 82.00 hours and 0.500% late dispatch.

13. `cat skill/operational-intervention-decision/scripts/analyze_packet.py`
    - Exit code: 0.
    - Relevant stdout: inspected its required-column, duplicate-key, nonnegative-value, count-relationship, subset-hour, and late-order checks, plus its aggregation logic.

14. `python deliverables/reproduce_decision.py | tee deliverables/reproduced_results.txt`
    - Exit code: 0.
    - Exact stdout:

```text
VALIDATION: PASS
rows: 28 cohort, 14 operations; unique keys and coverage pass
raw baseline Alder: 132/3600 = 3.667%
70/30 adjusted baseline Alder: 3.200%
raw baseline Birch: 102/3600 = 2.833%
70/30 adjusted baseline Birch: 2.600%
raw pilot Alder: 63/3600 = 1.750%
70/30 adjusted pilot Alder: 3.700%
raw pilot Birch: 51/3600 = 1.417%
70/30 adjusted pilot Birch: 2.500%
quality change-in-changes: 0.600%
labor change-in-changes per 1,200-order shift: 6.00 h
Alder continue projection: 108.0 h/shift vs 102 h cap
Alder stop projection (control-trend): 100.8 h/shift
Alder stop projection (baseline-only): 98.4 h/shift
Birch no-check projection: 98.4 h/shift
Alder continue late projection: 336/28800 = 1.167%
Alder stop late projection: 168/28800 = 0.583%
Birch no-check late projection: 144/28800 = 0.500%
continue expected mispacks: 1065.6; cost $58,608
stop expected mispacks (control-trend): 892.8; cost $49,104
continue-minus-stop expected mispack cost: $9,504
continue-minus-stop incremental labor: 144.0 h; cost $4,896
continue-minus-stop combined modeled cost: $14,400
```

15. `python -m py_compile deliverables/reproduce_decision.py`
    - Exit code: 0.
    - Stdout/stderr: empty.

16. `python deliverables/reproduce_decision.py`
    - Exit code: 0.
    - Stdout: exactly the validation and results block shown for command 14.

17. `rg -n "Recommendation|108.0|100.8|1.167|14,400|Unknown|Reproduce" answer.md`
    - Exit code: 0.
    - Relevant stdout: found the recommendation, constraint figures, modeled cost, unknowns, and reproduction section in `answer.md`.

`apply_patch` was used successfully to create `deliverables/reproduce_decision.py`, create and refine `answer.md`, and create this execution note. Tool responses contained no error text.

## Created outputs

- `answer.md` — user-facing decision memo.
- `deliverables/reproduce_decision.py` — standard-library validation and calculation script.
- `deliverables/reproduced_results.txt` — captured deterministic output.
- `work/measurement_basis.md` — output of the supplied skill analyzer.
- `execution-note.md` — this public record.

## Observation, interpretation, and unperformed checks

The numerical outputs above are exact captured observations from the supplied data and scripts. The recommendation, counterfactual attribution, and 1,440-order projections are interpretations or planning scenarios, labeled as such in `answer.md`.

No live operation was changed, no message was sent, no spending was committed, and no record or supplied input was modified. No randomized causal check, selective-check trial, band-level time study, or observed 1,440-order capacity check was performed because the packet contains none of those data and the task did not authorize live experimentation. Future shift dates were not supplied, so no calendar date for final outcome maturity was calculated.
