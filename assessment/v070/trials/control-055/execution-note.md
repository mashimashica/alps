# Execution note

## Outputs

- `deliverables/skills/operational-intervention-decision/` is the reusable Skill. Its `SKILL.md` defines the decision workflow and its standard-library `scripts/analyze_packet.py` reproduces validation, cohort rates, planned-mix standardization, quality-cost scenarios, full-shift operations, and proportional labor projections.
- `deliverables/northbank-decision.md` is the packet-specific decision. It recommends a guarded four-week narrowing on East, with no West expansion, and includes the exact reproduction command.

## Supplied resources used

- `prompt.md`
- `input/brief.md`
- `input/sources/measurement_notes.md`
- `input/sources/decision_context.md`
- `input/sources/shipment_cohorts.csv`
- `input/sources/shift_operations.csv`
- `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/common/agent-skills-format.md`
- `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/frozen/skill-creator/SKILL.md`
- `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/frozen/skill-creator/scripts/quick_validate.py`

No external sources were used.

## Checks performed

### Analyzer help

Command:

```bash
python3 deliverables/skills/operational-intervention-decision/scripts/analyze_packet.py --help
```

Observed output: argparse printed usage and all required packet, comparison, planning-mix, volume, cap, and cost arguments. Exit code: `0`.

### Northbank reproduction

Command (run before and after the final analyzer validation refinement):

```bash
python3 deliverables/skills/operational-intervention-decision/scripts/analyze_packet.py \
  --shipments input/sources/shipment_cohorts.csv \
  --operations input/sources/shift_operations.csv \
  --baseline-label baseline \
  --pilot-label pilot \
  --treated-line East \
  --comparison-line West \
  --full-shift-dates 2026-06-01,2026-06-02,2026-06-03,2026-06-15,2026-06-16,2026-06-17 \
  --planned-mix standard=0.8,complex=0.2 \
  --planned-orders-per-shift 1200 \
  --planned-shifts 20 \
  --productive-hour-cap 84 \
  --hourly-cost 28 \
  --avoidable-event-cost 65
```

Observed output on the final run: 28 shipment rows and 14 operations rows passed nonnegative-count, maturity, subset, uniqueness, and join-grain checks. The output reported East planned-mix quality of 3.200% baseline and 2.000% pilot; West 3.000% and 2.452%; East pilot full-shift late dispatch of 1.967%; projected East all-order labor of 93.60 hours per 1,200-order shift against an 84-hour cap; projected full-period incremental labor cost of USD 6,048; and approximately 133 checks per shift within the proportional baseline headroom. Exit code on each run: `0`.

### Negative-input behavior

Command:

```bash
python3 deliverables/skills/operational-intervention-decision/scripts/analyze_packet.py \
  --shipments input/sources/shipment_cohorts.csv \
  --operations input/sources/shift_operations.csv \
  --baseline-label baseline \
  --pilot-label pilot \
  --treated-line East \
  --comparison-line West \
  --full-shift-dates 2026-06-01 \
  --planned-mix standard=0.8,complex=0.3 \
  --planned-orders-per-shift 1200 \
  --planned-shifts 20 \
  --productive-hour-cap 84 \
  --hourly-cost 28 \
  --avoidable-event-cost 65
```

Observed output: `error: Planned mix weights must sum to 1`. Exit code: `2`.

### Skill format

Command (run before and after the final analyzer validation refinement):

```bash
python3 /workspace/scratch/a75c3a6d9076/alps-v070-assessment/frozen/skill-creator/scripts/quick_validate.py \
  deliverables/skills/operational-intervention-decision
```

Observed output: `Skill is valid!`. Exit code on each run: `0`.

## Design choices and limits

- The Skill separates mature downstream outcomes, pre-dispatch catches, line-level labor, training, and immediate late dispatch according to the measurement notes.
- Quality is standardized to the planned 80/20 order mix. The report shows both an own-baseline scenario and a common-change scenario based on West; neither is presented as a causal estimate.
- Capacity uses ordinary full shifts and removes one-off training from routine hours. The 1,200-order projection assumes direct proportionality between labor and throughput.
- The recommended 100-order selective process is explicitly an unmeasured bounded follow-up. Its savings, throughput, and quality effect are not claimed as observed.
- The format validator checks the Skill's physical structure and frontmatter. The analyzer was exercised on this supplied packet and one invalid mix; it was not forward-tested on a second packet. No independent agent evaluation was performed because delegation was prohibited for this task.
- No statistical confidence interval was used to imply precision across only three mature pilot dates. The report instead exposes counts, confounders, and the limits on attribution.
- No production change, staffing change, expenditure, communication, record edit, external write, installation, commit, push, or publication was performed.
