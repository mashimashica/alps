# Execution note — C-U118

All work was performed in `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U118`. No external state was changed, no messages were sent, and no network source was used. File edits were made with `apply_patch`; its returned result was `{}` on each successful edit.

## Files read

- `prompt.md`
- `skill/operational-intervention-decision/SKILL.md`
- `input/request.md`
- `input/sources/decision_context.md`
- `input/sources/measurement_notes.md`
- `input/sources/shift_operations.csv`
- `input/sources/shipment_cohorts.csv`
- Generated `deliverables/analysis_results.json`

The supplied Skill and all original inputs were left unchanged.

## Actual public commands and results

1. `cat prompt.md` — exit code 0. Exact captured observation: the prompt required applying the supplied Skill to `input/request.md`, writing `answer.md` via `apply_patch`, keeping work inside this consumer folder, preserving sources and Skill, and recording commands/results in this note.

2. `cat skill/operational-intervention-decision/SKILL.md` — exit code 0. Captured content supplied the required decision method, including native-grain validation, mature-outcome denominators, target-mix standardization, comparison adjustment, labor/service feasibility, economics, and review-plan requirements.

3. `cat input/request.md` — exit code 0. Exact captured observation: Nessa Vale needs a scoped recommendation for the next twenty shifts; local source files are authoritative; local analysis and deliverables are allowed; live operations and spending may not be changed.

4. `find input -maxdepth 2 -type f -print` — exit code 0. Exact stdout:

```text
input/sources/shift_operations.csv
input/sources/shipment_cohorts.csv
input/sources/measurement_notes.md
input/sources/decision_context.md
input/request.md
```

5. The following source reads each exited 0: `cat input/sources/decision_context.md`, `cat input/sources/measurement_notes.md`, `cat input/sources/shift_operations.csv`, and `cat input/sources/shipment_cohorts.csv`. Captured observations used in the answer: 1,440 orders per line per shift for twenty shifts at 70% standard / 30% complex; 102 productive-hour hard cap; 1% late-dispatch commitment; $55 per downstream mispack and $34 per additional labor hour; all-order checking is the only measured variant; August 28 outcomes are immature; August 28 is a short atypical shift; labor is whole-line grain; the August 17 five training hours are one-off; Alder volunteered and was not randomized; mix and the packing-list/recording process changed.

6. `python3 deliverables/reproduce_analysis.py` — run after initial script creation, exit code 0. Exact stdout:

```text
validation: PASS
wrote: /workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U118/deliverables/analysis_results.json
target-mix rates: {"baseline_alder": 0.032, "baseline_birch": 0.026, "pilot_alder": 0.037, "pilot_birch": 0.024999999999999998}
adjusted improvement from checking: -0.006000
checked hours at 1,440 orders: 108.0; supported volume at cap: 1360
Alder checked full-shift late rate: 0.011667
20-shift expected check disadvantage: $16032.00
```

7. `cat deliverables/analysis_results.json` — exit code 0. Exact captured output was the generated JSON. Relevant observations: 28 unique cohort rows, 14 unique operation rows, all shipment/operation keys reconciled, two band rows per shift, four immature cohort rows, twelve full-shift operation rows and two short-shift rows. It contained the source counts, raw and standardized rates, native-grain labor and dispatch aggregates, capacity scenarios, and economics reported in `answer.md`.

8. `python3 deliverables/reproduce_analysis.py` — rerun after adding stratum counts, mature workload shares, and break-even output; exit code 0. Stdout was exactly the same as command 6.

9. Final verification commands were launched independently and all exited 0:

   - `python3 deliverables/reproduce_analysis.py` produced the exact stdout shown for command 6 and regenerated the JSON.
   - `wc -l answer.md deliverables/reproduce_analysis.py deliverables/analysis_results.json` exact stdout:

```text
   68 answer.md
  215 deliverables/reproduce_analysis.py
  202 deliverables/analysis_results.json
  485 total
```

   - `rg -n "Stop Alder|108\\.0|1\\.17%|-0\\.6|16,032|0\\.412|review" answer.md` — exact captured observation: matches were found for the recommendation, 108-hour projection, 1.17% late rate, negative 0.6-point adjusted change, $16,032 scenario disadvantage, 0.412-point break-even, and both review sections.

No stderr was captured from these commands.

## Outputs created

- `answer.md` — user-facing decision and follow-up plan.
- `deliverables/reproduce_analysis.py` — standard-library, rerunnable calculation and validation script.
- `deliverables/analysis_results.json` — generated detailed aggregates and scenarios.
- `execution-note.md` — this record.

## Observation boundaries and unperformed checks

Exact source observations and script outputs are separated above from summaries. The arithmetic was rerun locally and source keys/reconciliation were checked by assertions. No causal significance test was performed; the packet has nonrandom allocation and too little pre-period evidence for a supported causal claim. No band-specific labor or selective-check estimate was performed because those data do not exist. No 1,440-order capacity test was performed because the packet contains only 1,200-order ordinary full shifts and one atypical 600-order shift. No live operational action or external verification was performed.
