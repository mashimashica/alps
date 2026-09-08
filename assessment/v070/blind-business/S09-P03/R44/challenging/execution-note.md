# Execution note

All commands below were run with working directory:

`/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U110`

## Files read

- `prompt.md`
- `skill/operational-intervention-decision/SKILL.md`
- `input/request.md`
- `input/sources/measurement_notes.md`
- `input/sources/decision_context.md`
- `input/sources/shift_operations.csv`
- `input/sources/shipment_cohorts.csv`
- The filename of the supplied analyzer was obtained with a `find` limited to `skill/operational-intervention-decision`.

The supplied Skill and original inputs were not modified. No external state was changed, and no message was sent.

## Actual public commands and results

1. `cat prompt.md`
   - Exit code: 0.
   - Exact captured observation: the prompt required use of the supplied Skill, local authoritative inputs, `answer.md` written with `apply_patch`, temporary/local outputs under this consumer folder, and an execution note.

2. `cat skill/operational-intervention-decision/SKILL.md`
   - Exit code: 0.
   - Exact captured observation: the Skill requires mature-only delayed outcomes, native-grain operations aggregation, planned-mix standardization, explicit counterfactuals, separate labor/service treatment, and a scoped continue/narrow/expand/stop recommendation.

3. `cat input/request.md && find input -maxdepth 2 -type f -print`
   - Exit code: 0.
   - Exact stdout file list: `input/sources/shift_operations.csv`, `input/sources/shipment_cohorts.csv`, `input/sources/measurement_notes.md`, `input/sources/decision_context.md`, and `input/request.md`.

4. The four source files were read with `cat`; the Skill directory was inspected with `find skill/operational-intervention-decision -maxdepth 3 -type f -print`.
   - Exit codes: 0 for all commands.
   - Exact stdout file list for the Skill: `skill/operational-intervention-decision/SKILL.md` and `skill/operational-intervention-decision/scripts/analyze_packet.py`.
   - Exact source observations used in the answer: August 28 cohorts have zero mature orders; only August 3–5 and 17–19 are ordinary full shifts; Alder's five August 17 training hours are one-off; planned workload is 20 shifts x 1,440 orders per line at 70% standard / 30% complex; the productive-hour cap is 102 per line-shift; the dispatch limit is 1%; costs are $55 per downstream mispack and $34 per additional productive hour.

5. `python skill/operational-intervention-decision/scripts/analyze_packet.py --help`
   - Exit code: 0.
   - Relevant exact stdout: the tool requires shipment and operations CSVs, baseline/pilot labels, treated/comparison lines, full-shift dates, planned mix, planned volume and shifts, productive-hour cap, hourly cost, and avoidable-event cost.
   - Stderr: none captured.

6. `mkdir -p deliverables work && python skill/operational-intervention-decision/scripts/analyze_packet.py --shipments input/sources/shipment_cohorts.csv --operations input/sources/shift_operations.csv --baseline-label baseline --pilot-label pilot --treated-line Alder --comparison-line Birch --full-shift-dates 2026-08-03,2026-08-04,2026-08-05,2026-08-17,2026-08-18,2026-08-19 --planned-mix standard=0.7,complex=0.3 --planned-orders-per-shift 1440 --planned-shifts 20 --productive-hour-cap 102 --hourly-cost 34 --avoidable-event-cost 55 > deliverables/analyzer-report.md`
   - Exit code: 0.
   - Stdout: redirected to `deliverables/analyzer-report.md`; terminal stdout was empty.
   - Stderr: none captured.
   - File created: `deliverables/analyzer-report.md`.

7. `cat deliverables/analyzer-report.md`
   - Exit code: 0.
   - Relevant exact captured results:
     - Validation passed for nonnegative counts, maturity, subsets, uniqueness, and join grain.
     - Planned-mix standardized Alder rates: baseline 3.200%, pilot 3.700%; Birch: baseline 2.600%, pilot 2.500%.
     - At 28,800 Alder orders, expected errors avoided were -144.0 against Alder's own baseline and -172.8 against the common-change scenario.
     - Ordinary full-shift Alder pilot operations: 90.00 routine hours per shift after excluding five training hours; 42 late orders among 3,600, or 1.167%.
     - Proportional projection: 108.00 pilot hours per 1,440-order shift, 6.00 hours over cap, and 192 incremental period hours costing $6,528.
     - Gross avoidable-error cost less incremental labor: -$14,448 against own baseline and -$16,032 under the common-change scenario.

8. `apply_patch` created `answer.md` and this `execution-note.md`; a subsequent `apply_patch` added this verification record.
   - Result: patches applied successfully.

9. `python skill/operational-intervention-decision/scripts/analyze_packet.py --shipments input/sources/shipment_cohorts.csv --operations input/sources/shift_operations.csv --baseline-label baseline --pilot-label pilot --treated-line Alder --comparison-line Birch --full-shift-dates 2026-08-03,2026-08-04,2026-08-05,2026-08-17,2026-08-18,2026-08-19 --planned-mix standard=0.7,complex=0.3 --planned-orders-per-shift 1440 --planned-shifts 20 --productive-hour-cap 102 --hourly-cost 34 --avoidable-event-cost 55 > work/verification-report.md && cmp -s deliverables/analyzer-report.md work/verification-report.md && test -s answer.md && test -s execution-note.md`
   - Exit code: 0.
   - Stdout/stderr: none captured.
   - Exact observation: rerunning the analyzer produced byte-identical output, and both required Markdown files were nonempty.

## Summaries and unperformed checks

The recommendation in `answer.md` is an interpretation of the exact packet observations and analyzer output listed above. No causal statistical test, confidence interval, selective-check simulation, external benchmark, live operational change, or customer/staff contact was performed. The labor and expected-event figures are planning projections under the explicit direct-scaling and rate-transfer assumptions, not observed next-period outcomes.
