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

No external sources were used. No supplied Skill or input file was changed.

## Commands and observations

1. Command: `cat /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U108/prompt.md`
   - Exit code: 0
   - Exact captured observation: the prompt required applying the supplied Skill to `input/request.md`, writing `answer.md` with `apply_patch`, retaining a public execution note, and avoiding external state changes.

2. Commands run concurrently:
   - `cat skill/operational-intervention-decision/SKILL.md`
   - `cat input/request.md && find input -maxdepth 2 -type f -print`
   - Exit codes: 0, 0
   - Exact captured file listing: `input/sources/shift_operations.csv`, `input/sources/shipment_cohorts.csv`, `input/sources/measurement_notes.md`, `input/sources/decision_context.md`, `input/request.md`.
   - Relevant stdout summary: the Skill requires cohort maturity exclusions, planned-mix standardization, separate quality/labor/dispatch/cost analysis, explicit causal limits, and a scoped recommendation.

3. Commands run concurrently:
   - `cat input/sources/measurement_notes.md`
   - `cat input/sources/decision_context.md`
   - `cat input/sources/shift_operations.csv`
   - `cat input/sources/shipment_cohorts.csv`
   - `find skill/operational-intervention-decision -maxdepth 3 -type f -print`
   - Exit codes: all 0
   - Exact captured observations relevant to calculation: Aug 28 cohorts have `mature_orders=0`; Aug 28 was a short 600-order shift; Alder's Aug 17 training subset was 5 hours; the next period is 20 shifts at 1,440 orders per line per shift and 70%/30% mix; the hard cap is 102 productive hours per line per full shift; late dispatch must be no more than 1%; supplied values are $55 per downstream mispack and $34 per additional productive hour.
   - Exact captured Skill file listing: `skill/operational-intervention-decision/SKILL.md` and `skill/operational-intervention-decision/scripts/analyze_packet.py`.

4. Command: `python skill/operational-intervention-decision/scripts/analyze_packet.py --help`
   - Exit code: 0
   - Relevant stdout: usage requires shipment and operations CSVs, intervention/control lines, planned mix, planned orders per shift, shifts, and hour cap; optional flags include period names, operations-date exclusions, avoidable cost, and hour cost.

5. Command: `mkdir -p deliverables work && python skill/operational-intervention-decision/scripts/analyze_packet.py input/sources/shipment_cohorts.csv input/sources/shift_operations.csv --intervention-line Alder --control-line Birch --baseline-period baseline --trial-period pilot --planned-mix standard=0.7,complex=0.3 --planned-orders-per-shift 1440 --shifts 20 --hour-cap 102 --exclude-operations-date 2026-08-28 --avoidable-cost 55 --hour-cost 34 > deliverables/reproducible-analysis.md`
   - Exit code: 0
   - Stdout/stderr: none because stdout was redirected; no stderr was captured.
   - File created: `deliverables/reproducible-analysis.md`.

6. Command: `cat deliverables/reproducible-analysis.md`
   - Exit code: 0
   - Exact relevant stdout:
     - Standardized quality: Alder baseline 3.20%, Alder pilot 3.70%, Birch baseline 2.60%, Birch pilot 2.50%.
     - Difference-in-differences: +0.60 percentage points.
     - Comparable Alder pilot operations: 3,600 shipped, 275 productive hours, 5 training hours, 90 ongoing hours per shift, 42 late orders, 1.17% late rate.
     - Required throughput: 14.12 orders/hour; observed Alder pilot throughput: 13.33 orders/hour; proportional sensitivity: 108.0 hours per planned shift.
     - Script quality sensitivities: `-144.0 fewer errors and $-7,920` for Alder before/after and `-172.8 fewer and $-9,504` for difference-in-differences. These negative “fewer” values were presented in `answer.md` as 144.0 and 172.8 more errors, respectively.

7. Mutation: `apply_patch` created `answer.md` and this `execution-note.md`.
   - Result: patch applied successfully.

8. Command: local Python calculation reading `input/sources/shipment_cohorts.csv` and printing band aggregates and planning checks.
   - Exit code: 0
   - Exact relevant stdout: baseline/pilot band aggregates matched the supplied script; planned volume was 28,800 orders (20,160 standard and 8,640 complex); required throughput was 14.117647 orders/hour; pilot proportional hours were 108.0 per shift; before/after and difference-in-differences scenarios were 144.0 and 172.8 more errors; proportional incremental labor cost was $6,528.

9. Mutation: `apply_patch` added the difference-in-differences cost scenario to `answer.md` and recorded command 8 in this note.
   - Result: patch applied successfully.

10. Earlier mutation attempt: an `apply_patch` call intended to add the same cost scenario and command record failed its context check.
   - Tool result: `apply_patch verification failed` because an expected `execution-note.md` line was searched in `answer.md`.
   - Effect: no change from that failed patch; the corrected two-file patch is recorded in item 9.

11. Inspection commands:
   - `sed -n '75,135p' answer.md`
   - `tail -35 execution-note.md`
   - `rg -n -A10 -B2 'Planning cost' answer.md`
   - Exit codes: all 0.
   - Relevant stdout summary: the answer ending, execution-note command list, and cost table were present; the cost table initially had only the before/after scenario, which prompted the successful addition recorded in item 9.

12. Final verification commands run concurrently:
   - `cat answer.md`
   - `test -s execution-note.md && test -s deliverables/reproducible-analysis.md && printf '%s\\n' 'execution-note.md: present' 'deliverables/reproducible-analysis.md: present'`
   - Exit codes: 0, 0.
   - Exact relevant stdout: the complete answer rendered as Markdown and included the stop decision, quality/operations/cost tables, evidence boundary, review point, and reproduction command; the file check printed `execution-note.md: present` and `deliverables/reproducible-analysis.md: present`.

13. Mutation: this final `apply_patch` added items 10-12 to the execution note.
   - Result: patch applied successfully.

## Checks performed and not performed

- Performed: source schema/definition review, supplied-script help review, supplied-script calculation, manual directional interpretation of signed scenarios, and consistency checks against the hard hours and dispatch limits.
- Not performed: external browsing, causal estimation beyond the supplied descriptive comparison, live operations changes, staff/customer contact, record changes, spending, or validation of an unmeasured selective-check variant.
