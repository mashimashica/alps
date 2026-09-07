# Public execution note

## Files used

- `prompt.md`
- `skill/operational-intervention-decision/SKILL.md`
- `skill/operational-intervention-decision/scripts/analyze_packet.py`
- `input/request.md`
- `input/sources/measurement_notes.md`
- `input/sources/decision_context.md`
- `input/sources/shift_operations.csv`
- `input/sources/shipment_cohorts.csv`

The supplied Skill and original inputs were read only and were not modified.

## Commands and captured results

All commands ran with working directory `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U107`.

1. `cat prompt.md` — exit code 0. Captured the task instructions.
2. `cat skill/operational-intervention-decision/SKILL.md` — exit code 0. Captured the supplied decision procedure.
3. `cat input/request.md` — exit code 0. Captured the user request.
4. `find input -maxdepth 2 -type f -print` — exit code 0. Captured exactly the request and four source files in the assigned input folder.
5. `cat input/sources/measurement_notes.md` — exit code 0. Captured definitions, maturity exclusions, table grain, and the July 31 short-shift note.
6. `cat input/sources/decision_context.md` — exit code 0. Captured the workload, authority, staffing, dispatch, and cost assumptions.
7. `cat input/sources/shift_operations.csv` — exit code 0. Captured 14 line/shift operation rows.
8. `cat input/sources/shipment_cohorts.csv` — exit code 0. Captured 28 mutually exclusive date/line/order-band cohort rows.
9. `find skill/operational-intervention-decision -maxdepth 3 -type f -print` — exit code 0. Captured the supplied Skill and analyzer paths.
10. `python skill/operational-intervention-decision/scripts/analyze_packet.py --help` — exit code 0, no stderr. Captured required arguments and options.
11. `mkdir -p deliverables work && python skill/operational-intervention-decision/scripts/analyze_packet.py input/sources/shipment_cohorts.csv input/sources/shift_operations.csv --intervention-line Harbor --control-line Ridge --baseline-period baseline --trial-period pilot --planned-mix standard=0.75,complex=0.25 --planned-orders-per-shift 800 --shifts 20 --hour-cap 68 --exclude-operations-date 2026-07-31 --avoidable-cost 48 --hour-cost 32 > deliverables/numerical-basis.md && cat deliverables/numerical-basis.md` — exit code 0, no stderr. Exact analyzer stdout is retained in `deliverables/numerical-basis.md`. It reports Harbor 2.62% baseline versus 1.25% pilot, Ridge 2.62% versus 2.50%, a -1.25 percentage-point descriptive difference-in-differences, Harbor 65.0 ongoing hours/full shift, Harbor 0.54% late dispatch, required throughput 11.76 orders/hour, and observed Harbor throughput 12.31 orders/hour.
12. `sed -n '1,260p' skill/operational-intervention-decision/scripts/analyze_packet.py` — exit code 0. Captured the supplied analyzer implementation to verify exclusions and formulas.

`apply_patch` created `answer.md`, `deliverables/reproduce.sh`, and this note. It did not alter the supplied Skill or inputs.

13. `chmod +x deliverables/reproduce.sh && cp answer.md deliverables/decision.md && ./deliverables/reproduce.sh > work/reproduced-numerical-basis.md && cmp -s deliverables/numerical-basis.md work/reproduced-numerical-basis.md && wc -l answer.md deliverables/decision.md deliverables/numerical-basis.md deliverables/reproduce.sh execution-note.md && sha256sum deliverables/numerical-basis.md work/reproduced-numerical-basis.md` — exit code 0, no stderr. The decision copy had 54 lines. The retained and regenerated analyzer outputs had identical SHA-256 `3703cc716e8f60930cb652b1f8bce83f539487a1618c4eed8d43e6653b8e22c2`.

## Summaries and checks not performed

The recommendation and Ridge cost scenario are reasoned summaries based on the exact captured observations. The Ridge quality effect and 65-hour staffing level were not observed; they are labeled planning assumptions. No causal effect was estimated, no statistical significance test was performed, no live roster or future cohort was available to verify, and no external action, message, spend, or operations change was performed.
